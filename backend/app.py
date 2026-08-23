# -*- coding: utf-8 -*-
"""
FastAPI application — mirrors QwenPaw's "Agent 運行時 = FastAPI app" layer.
Serves the static frontend and exposes the agent over a Server-Sent-Events
stream so the UI can render the live ReAct trace.
"""
import json
import logging
import os

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
    }


@app.get("/api/pois")
def pois():
    return kb.all_pois()


@app.get("/api/plan")
def plan(
    q: str = Query(default="", max_length=1000),
    lang: str = Query(default="", pattern=r"^(|zh-HK|zh|en|pt|ja)$"),
    today: str = Query(default="", max_length=32),
):
    """Stream the agent's planning as Server-Sent Events."""
    def gen():
        # tell proxies not to buffer
        yield "retry: 3000\n\n"
        try:
            for event in agent.run(q, language=(lang or None), today=(today or None)):
                yield "data: " + json.dumps(event, ensure_ascii=False) + "\n\n"
        except Exception:
            logger.exception("Unhandled planning stream error")
            yield "data: " + json.dumps({
                "type": "error",
                "text": "規劃暫時未能完成，請稍後再試。",
            }, ensure_ascii=False) + "\n\n"
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
