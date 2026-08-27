# -*- coding: utf-8 -*-
"""
FastAPI application — mirrors QwenPaw's "Agent 運行時 = FastAPI app" layer.
Serves the static frontend and exposes the agent over a Server-Sent-Events
stream so the UI can render the live ReAct trace.
"""
import json
import logging
import os
import datetime as dt
import queue
import threading
import time
from collections import defaultdict, deque

from fastapi import FastAPI, Query, Request
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

import config
import kb
import agent
import impact

_BACKEND = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_BACKEND)
_FRONTEND = os.path.join(_ROOT, "frontend")

app = FastAPI(title=config.APP_TITLE)
logger = logging.getLogger("everylane")
_STARTED_MONO = time.monotonic()
_STARTED_AT = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
_METRICS_LOCK = threading.Lock()
_METRICS = {
    "plans_started": 0,
    "plans_completed": 0,
    "plans_failed": 0,
    "active_plans": 0,
    "fast_demo_runs": 0,
    "fallback_runs": 0,
}
_PLAN_DURATIONS_MS = deque(maxlen=100)
_QWEN_SEM = threading.Semaphore(config.QWEN_CONCURRENCY)
_PLAN_HITS = defaultdict(deque)


def _client_ip(request: Request) -> str:
    forwarded = (request.headers.get("x-forwarded-for") or "").split(",")[0].strip()
    return forwarded or (request.client.host if request.client else "unknown")


def _rate_limited(ip: str) -> bool:
    now = time.time()
    hits = _PLAN_HITS[ip]
    while hits and now - hits[0] > 60:
        hits.popleft()
    if len(hits) >= config.PLAN_RATE_PER_MIN:
        return True
    hits.append(now)
    return False


def _percentile(values, pct):
    if not values:
        return None
    ordered = sorted(values)
    idx = min(len(ordered) - 1, round((len(ordered) - 1) * pct))
    return ordered[idx]


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "img-src 'self' data: https://*.tile.openstreetmap.org; "
        "connect-src 'self'; font-src 'self' data: https://fonts.gstatic.com; "
        "object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
    )
    return response


@app.get("/api/health")
def health():
    return {
        "ok": True,
        "engine": ("qwen:" + config.QWEN_MODEL) if config.USE_REAL_LLM else "offline-demo",
        "real_llm": config.USE_REAL_LLM,
        "poi_count": len(kb.all_pois()),
        "old_district": sum(1 for p in kb.all_pois() if p["old_district"]),
        "local_business": sum(1 for p in kb.all_pois() if p["local_business"]),
        "planning_modes": ["qwen-react", "verified-tools-fast"],
    }


@app.get("/api/pois")
def pois():
    return kb.all_pois()


@app.get("/api/system/status")
def system_status():
    """Real runtime evidence, kept separate from the simulated pilot dataset."""
    with _METRICS_LOCK:
        metrics = dict(_METRICS)
        durations = list(_PLAN_DURATIONS_MS)
    completed = metrics["plans_completed"]
    failed = metrics["plans_failed"]
    finished = completed + failed
    return {
        "ok": True,
        "data_class": "live_runtime",
        "process_started_at": _STARTED_AT,
        "uptime_s": round(time.monotonic() - _STARTED_MONO),
        "engine": ("qwen:" + config.QWEN_MODEL) if config.USE_REAL_LLM else "verified-tools",
        "real_llm_configured": config.USE_REAL_LLM,
        "live_weather_enabled": os.getenv("EL_LIVE_WEATHER", "").strip() == "1",
        "metrics": {
            **metrics,
            "success_rate_pct": round(completed * 100.0 / finished, 1) if finished else None,
        },
        "latency_ms": {
            "sample_size": len(durations),
            "last": durations[-1] if durations else None,
            "p50": _percentile(durations, 0.50),
            "p95": _percentile(durations, 0.95),
        },
        "resilience": {
            "qwen_timeout_s": config.QWEN_TIMEOUT_S,
            "overall_deadline_s": config.AGENT_DEADLINE_S,
            "automatic_verified_tools_fallback": True,
        },
    }


@app.get("/api/plan")
def plan(
    request: Request,
    q: str = Query(default="", max_length=1000),
    lang: str = Query(default="", pattern=r"^(|zh-HK|zh|en|pt|ja)$"),
    today: str = Query(default="", max_length=32),
    mode: str = Query(default="auto", pattern=r"^(auto|fast)$"),
):
    """Stream the agent's planning as Server-Sent Events."""
    ip = _client_ip(request)
    crowded = _rate_limited(ip)
    overflow_fast = False
    run_mode = mode
    hold_qwen = False
    if mode != "fast":
        if crowded or not _QWEN_SEM.acquire(blocking=False):
            run_mode = "fast"
            overflow_fast = True
        else:
            hold_qwen = True

    def gen():
        started = time.monotonic()
        saw_result = False
        saw_fallback = False
        with _METRICS_LOCK:
            _METRICS["plans_started"] += 1
            _METRICS["active_plans"] += 1
            if run_mode == "fast":
                _METRICS["fast_demo_runs"] += 1
        box = queue.Queue()

        def produce():
            try:
                if overflow_fast:
                    box.put({
                        "type": "runtime",
                        "engine": "verified-tools",
                        "label": "可重現工具鏈",
                        "note": "評審高峰或 Qwen 忙碌時自動走 90 秒可核驗路徑，避免現場空等。",
                    })
                for event in agent.run(
                    q, language=(lang or None), today=(today or None), mode=run_mode
                ):
                    box.put(event)
                box.put(None)
            except Exception:
                logger.exception("Unhandled planning stream error")
                box.put({
                    "type": "error",
                    "text": "規劃暫時未能完成，請稍後再試。",
                })
                box.put(None)

        worker = threading.Thread(target=produce, daemon=True)
        worker.start()
        try:
            yield "retry: 3000\n\n"
            while True:
                try:
                    event = box.get(timeout=8)
                except queue.Empty:
                    yield "data: " + json.dumps({"type": "heartbeat"}, ensure_ascii=False) + "\n\n"
                    continue
                if event is None:
                    break
                if event.get("type") == "result":
                    saw_result = True
                if event.get("type") == "runtime" and event.get("engine") == "fallback-tools":
                    saw_fallback = True
                yield "data: " + json.dumps(event, ensure_ascii=False) + "\n\n"
        finally:
            if hold_qwen:
                _QWEN_SEM.release()
            duration_ms = round((time.monotonic() - started) * 1000)
            with _METRICS_LOCK:
                _METRICS["active_plans"] = max(0, _METRICS["active_plans"] - 1)
                if saw_result:
                    _METRICS["plans_completed"] += 1
                    _PLAN_DURATIONS_MS.append(duration_ms)
                else:
                    _METRICS["plans_failed"] += 1
                if saw_fallback:
                    _METRICS["fallback_runs"] += 1

    return StreamingResponse(gen(), media_type="text/event-stream", headers={
        "Cache-Control": "no-cache, no-transform",
        "X-Accel-Buffering": "no",
        "Connection": "keep-alive",
    })


# ---- 複賽 pilot: impact dashboard, visit codes, B2B API --------------------
app.include_router(impact.router)


# ---- static frontend -----------------------------------------------------
app.mount("/assets", StaticFiles(directory=os.path.join(_FRONTEND, "assets")), name="assets")


@app.get("/")
def index():
    return FileResponse(os.path.join(_FRONTEND, "index.html"))


@app.get("/{path:path}")
def static_files(path: str):
    full = os.path.normpath(os.path.join(_FRONTEND, path))
    try:
        inside_frontend = os.path.commonpath([_FRONTEND, full]) == _FRONTEND
    except ValueError:
        inside_frontend = False
    if inside_frontend and os.path.isfile(full):
        return FileResponse(full)
    return JSONResponse({"error": "not found"}, status_code=404)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)
