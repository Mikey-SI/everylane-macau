# -*- coding: utf-8 -*-
"""複賽（Semi-final）pilot endpoints.

Implements the semifinal targets promised in《項目策劃書》第七章:

* 可用性測試（20+ 人、完成率 ≥90%、80% 認同）
* 每份合適行程 ≥3 個舊區/本地商戶點 + 一次性到店碼核銷
* 導流覆蓋率 / 路線可行率 / 商戶到訪率 三大成效指標
* 人流模型校正 · 匿名化文旅熱度儀表板 · 酒店/旅行社 B 端 API

Per the semifinal rules the pilot dataset may be simulated ("數據可以不用真實，
但呈現效果須達到計劃書的指標"); every number below is generated deterministically
so the dashboard, the API and the accompanying document always agree, and the
dashboard clearly labels the pilot window as demonstration data.
The visit-code issue/redeem loop itself is real and stateful.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import random
import re
import threading

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

import agent
import kb
from llm import parse_request

router = APIRouter()

_BACKEND = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_BACKEND)
_CODE_STORE = os.path.join(_ROOT, "logs", "visit_codes.json")

# --------------------------------------------------------------------------
# Pilot constants — single source of truth for dashboard + 複賽說明文檔.
# --------------------------------------------------------------------------
PILOT = {
    "stage": "複賽試點",
    "start": "2026-08-11",
    "end": "2026-08-31",
    "data_note": (
        "本頁為複賽示範數據（賽規：數據可以不用真實，但呈現效果須達到計劃書的指標）；"
        "指標口徑與《項目策劃書》第七章一致，一次性到店碼的發碼/核銷流程為真實可操作功能。"
    ),
}

USABILITY = {
    "participants": 23,
    "residents": 11,
    "visitors": 12,
    "tasks_per_user": 12,
    "tasks_total": 276,
    "tasks_done": 252,
    "completion_pct": 91.3,
    "agree_save_time_pct": 82.6,   # 19 / 23
    "agree_local_flavor_pct": 87.0,  # 20 / 23
    "sus": 84.5,
}

FUNNEL = {
    "itineraries": 1247,
    "with_merchant": 1078,
    "diversion_coverage_pct": 86.4,   # 1078 / 1247
    "route_feasible": 1233,
    "route_feasible_pct": 98.9,       # 1233 / 1247
    "avg_old_local_stops": 4.2,       # target ≥ 3
    "codes_issued": 3152,
    "codes_redeemed": 1318,
    "merchant_visit_pct": 41.8,       # 1318 / 3152
    "est_local_spend_mop": 118620,
}

MODEL_CAL = {
    "samples": 1860,
    "hotspots": 6,
    "mae_before": 8.6,   # crowd index points (0-100)
    "mae_after": 2.9,
    "direction_hit_pct": 95.2,
    "hotspot_peak_delta_pct": -9.8,
    "old_district_visits_delta_pct": 23.5,
}

# 計劃書第七章「晉級後驗證目標」 → 試點呈現值
PROPOSAL_TARGETS = [
    {"id": "testers", "label": "可用性測試人數", "clause": "20+ 位本地居民/遊客完成可用性測試",
     "target": "≥ 20 人", "actual": "23 人（居民 11・遊客 12）", "met": True},
    {"id": "completion", "label": "任務完成率", "clause": "任務完成率目標 ≥ 90%",
     "target": "≥ 90%", "actual": "91.3%（252/276 項任務）", "met": True},
    {"id": "agree", "label": "受試者認同度", "clause": "80% 受試者認同更省時、更有在地味",
     "target": "≥ 80%", "actual": "省時 82.6% · 在地味 87.0%", "met": True},
    {"id": "old_stops", "label": "每份行程舊區/商戶點", "clause": "每份合適行程平均納入 ≥ 3 個舊區/本地商戶點",
     "target": "≥ 3 個", "actual": "平均 4.2 個", "met": True},
    {"id": "visit_code", "label": "一次性到店碼核銷", "clause": "以一次性到店碼核銷量度實際到訪與轉化",
     "target": "上線並可核銷", "actual": "已上線：發碼 3,152 → 核銷 1,318（41.8%）", "met": True},
    {"id": "three_metrics", "label": "三大成效指標", "clause": "以導流覆蓋率、路線可行率、商戶到訪率評估成效",
     "target": "三項指標可量度", "actual": "86.4% / 98.9% / 41.8%", "met": True},
    {"id": "no_overload", "label": "不增加熱門點過載", "clause": "在不增加熱門點過載的前提下導流",
     "target": "熱點峰值不上升", "actual": "大三巴峰值熱度 −9.8%，舊區到訪 +23.5%", "met": True},
    {"id": "stage1", "label": "第 1 階段交付", "clause": "校正人流模型；加入即時天氣與無障礙資料",
     "target": "三項功能上線", "actual": "模型 MAE 8.6→2.9 · 即時天氣已接入 · 70/70 POI 無障礙標註", "met": True},
    {"id": "stage2", "label": "第 2 階段交付", "clause": "3–5 間舊區商戶小規模到店碼試點",
     "target": "3–5 間商戶", "actual": "5 間商戶（半島 2・氹仔 2・路環 1）", "met": True},
]

# 5 pilot merchants (all real KB local businesses across three districts)
MERCHANTS = [
    {"poi_id": "wong_chi_kei", "issued": 823, "redeemed": 356,
     "offer": "到店禮：例牌蝦子撈麵 9 折", "weekly": [96, 122, 138]},
    {"poi_id": "hang_yau_fishball", "issued": 742, "redeemed": 331,
     "offer": "魚蛋串買二送一（試點限定）", "weekly": [92, 111, 128]},
    {"poi_id": "tai_lei_loi", "issued": 663, "redeemed": 262,
     "offer": "豬扒包套餐即減 MOP 5", "weekly": [71, 88, 103]},
    {"poi_id": "mok_yi_kei", "issued": 517, "redeemed": 208,
     "offer": "大菜糕／雪糕 9 折", "weekly": [58, 69, 81]},
    {"poi_id": "lord_stow", "issued": 407, "redeemed": 161,
     "offer": "蛋撻 6 件裝加送 1 件", "weekly": [44, 54, 63]},
]

HEAT_ZONES = [
    {"id": "ruins", "name": "大三巴周邊", "kind": "hotspot", "before": 92, "after": 83},
    {"id": "senado", "name": "議事亭前地／新馬路", "kind": "hotspot", "before": 88, "after": 81},
    {"id": "inner_south", "name": "福隆新街／下環（內港南）", "kind": "old", "before": 41, "after": 52},
    {"id": "inner_north", "name": "十月初五街／沙梨頭（內港北）", "kind": "old", "before": 33, "after": 44},
    {"id": "taipa_old", "name": "氹仔舊城區", "kind": "old", "before": 58, "after": 66},
    {"id": "coloane", "name": "路環市區", "kind": "old", "before": 30, "after": 38},
]

# Crowd-model calibration curve for 大三巴 (crowd index 0-100, 09:00-19:00)
CAL_HOURS = ["09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19"]
CAL_OBSERVED = [46, 58, 71, 83, 90, 94, 91, 84, 76, 66, 55]
CAL_BEFORE = [62, 68, 72, 76, 79, 81, 80, 78, 75, 71, 67]
CAL_AFTER = [48, 57, 69, 81, 88, 92, 90, 83, 77, 68, 57]


def _daily_series():
    """Deterministic 21-day pilot series (hotspot cooling, old district rising)."""
    rng = random.Random(20260902)
    start = dt.date.fromisoformat(PILOT["start"])
    dates, hotspot, old_district, itineraries = [], [], [], []
    n = (dt.date.fromisoformat(PILOT["end"]) - start).days + 1
    for i in range(n):
        d = start + dt.timedelta(days=i)
        t = i / (n - 1)
        weekend = 1.10 if d.weekday() >= 5 else 1.0
        hs = (91 - 9.0 * t) * weekend + rng.uniform(-1.6, 1.6)
        od = (38 + 13.0 * t) * weekend + rng.uniform(-1.4, 1.4)
        it = int((FUNNEL["itineraries"] / n) * (0.82 + 0.38 * t) * weekend + rng.uniform(-3, 3))
        dates.append(d.isoformat())
        hotspot.append(round(min(100, hs), 1))
        old_district.append(round(min(100, od), 1))
        itineraries.append(max(20, it))
    drift = FUNNEL["itineraries"] - sum(itineraries)
    itineraries[-1] = max(20, itineraries[-1] + drift)
    return {"dates": dates, "hotspot_index": hotspot,
            "old_district_index": old_district, "itineraries": itineraries}


_DAILY = _daily_series()


def _merchant_rows():
    rows = []
    for m in MERCHANTS:
        p = kb.get(m["poi_id"])
        rows.append({
            "poi_id": m["poi_id"],
            "name": p["name"]["zh"],
            "name_en": p["name"]["en"],
            "district": p["district_name"],
            "image": p["image"],
            "issued": m["issued"],
            "redeemed": m["redeemed"],
            "rate_pct": round(m["redeemed"] * 100.0 / m["issued"], 1),
            "offer": m["offer"],
            "weekly_redeemed": m["weekly"],
        })
    return rows


# --------------------------------------------------------------------------
# read-only dashboard endpoints
# --------------------------------------------------------------------------
@router.get("/api/impact/summary")
def impact_summary():
    return {
        "pilot": PILOT,
        "proposal_targets": PROPOSAL_TARGETS,
        "usability": USABILITY,
        "funnel": FUNNEL,
        "model": MODEL_CAL,
        "targets_met": all(t["met"] for t in PROPOSAL_TARGETS),
    }


@router.get("/api/impact/heat")
def impact_heat():
    zones = []
    for z in HEAT_ZONES:
        delta = round((z["after"] - z["before"]) * 100.0 / z["before"], 1)
        zones.append({**z, "delta_pct": delta})
    return {"pilot": PILOT, "zones": zones, "daily": _DAILY,
            "calibration": {"hours": CAL_HOURS, "observed": CAL_OBSERVED,
                            "before": CAL_BEFORE, "after": CAL_AFTER,
                            **MODEL_CAL}}


@router.get("/api/impact/merchants")
def impact_merchants():
    return {
        "pilot": PILOT,
        "merchants": _merchant_rows(),
        "totals": {
            "issued": FUNNEL["codes_issued"],
            "redeemed": FUNNEL["codes_redeemed"],
            "rate_pct": FUNNEL["merchant_visit_pct"],
            "est_local_spend_mop": FUNNEL["est_local_spend_mop"],
        },
    }


# --------------------------------------------------------------------------
# one-time visit codes (real, stateful loop: issue -> redeem once)
# --------------------------------------------------------------------------
_CODES: dict[str, dict] = {}
_CODES_LOCK = threading.Lock()
_CODE_ALPHABET = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"
_CODE_RE = re.compile(r"^EL-[A-Z0-9]{4}-[A-Z0-9]{2}$")
_CODE_LIMIT = 20000


def _load_codes():
    try:
        with open(_CODE_STORE, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            _CODES.update(data)
    except Exception:
        pass


def _save_codes():
    try:
        os.makedirs(os.path.dirname(_CODE_STORE), exist_ok=True)
        tmp = _CODE_STORE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(_CODES, f, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, _CODE_STORE)
    except Exception:
        pass  # persistence is best-effort; the in-memory loop still works


_load_codes()


class IssueBody(BaseModel):
    poi_id: str = Field(max_length=64)


DEMO_MERCHANT_PIN = "2580"


class RedeemBody(BaseModel):
    code: str = Field(max_length=16)
    pin: str = Field(default="", max_length=8)


@router.post("/api/codes/issue")
def issue_code(body: IssueBody):
    p = kb.get(body.poi_id)
    if not p:
        raise HTTPException(status_code=404, detail="POI 不存在")
    if not (p["local_business"] or p["old_district"]):
        raise HTTPException(status_code=400, detail="到店碼只適用於舊區/本地商戶點")
    rng = random.SystemRandom()
    with _CODES_LOCK:
        if len(_CODES) >= _CODE_LIMIT:  # keep the demo store bounded
            for key in list(_CODES)[: _CODE_LIMIT // 2]:
                _CODES.pop(key, None)
        while True:
            code = "EL-" + "".join(rng.choice(_CODE_ALPHABET) for _ in range(4)) \
                   + "-" + "".join(rng.choice(_CODE_ALPHABET) for _ in range(2))
            if code not in _CODES:
                break
        _CODES[code] = {
            "poi_id": body.poi_id,
            "issued_at": dt.datetime.now().isoformat(timespec="seconds"),
            "redeemed": False,
        }
        _save_codes()
    offer = next((m["offer"] for m in MERCHANTS if m["poi_id"] == body.poi_id),
                 "出示此碼享試點到店禮遇")
    return {"code": code, "poi_id": body.poi_id, "name": p["name"]["zh"],
            "name_en": p["name"]["en"], "offer": offer,
            "hint": "一次性到店碼：到店出示，核銷一次即失效（試點演示）"}


@router.post("/api/codes/redeem")
def redeem_code(body: RedeemBody):
    code = body.code.strip().upper()
    if not _CODE_RE.match(code):
        return {"status": "invalid", "code": code,
                "message": "格式不正確：到店碼形如 EL-XXXX-XX"}
    if (body.pin or "").strip() != DEMO_MERCHANT_PIN:
        return {"status": "denied", "code": code,
                "message": "商戶 PIN 不正確。評審演示 PIN：2580"}
    with _CODES_LOCK:
        rec = _CODES.get(code)
        if not rec:
            return {"status": "invalid", "code": code, "message": "查無此到店碼"}
        p = kb.get(rec["poi_id"])
        name = p["name"]["zh"] if p else rec["poi_id"]
        if rec["redeemed"]:
            return {"status": "already_redeemed", "code": code, "poi_id": rec["poi_id"],
                    "name": name, "redeemed_at": rec.get("redeemed_at"),
                    "message": f"此碼已於 {rec.get('redeemed_at', '早前')} 核銷，一次性到店碼不可重用"}
        rec["redeemed"] = True
        rec["redeemed_at"] = dt.datetime.now().isoformat(timespec="seconds")
        _save_codes()
    return {"status": "redeemed", "code": code, "poi_id": rec["poi_id"], "name": name,
            "redeemed_at": rec["redeemed_at"],
            "message": f"核銷成功：{name}（此碼隨即失效）"}


# --------------------------------------------------------------------------
# evidence / data-lineage export — lets judges audit every claim
# --------------------------------------------------------------------------
@router.get("/api/impact/evidence")
def impact_evidence():
    with _CODES_LOCK:
        live_codes = len(_CODES)
        live_redeemed = sum(1 for rec in _CODES.values() if rec.get("redeemed"))
    return {
        "schema_version": "semifinal-evidence-v1",
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "competition_rule": "數據可以不用真實，但呈現效果須達到計劃書的指標",
        "data_classes": [
            {
                "id": "live_runtime",
                "label": "真實・即時可操作",
                "items": [
                    "Qwen / 可重現工具鏈行程規劃",
                    "Open-Meteo 天氣（不可用時明確回退季節模型）",
                    "一次性到店碼發碼與不可重複核銷",
                    "B 端 API、70 POI 知識庫、無障礙標註、自動化測試",
                ],
                "verify": ["/api/health", "/api/system/status", "/api/codes/issue",
                           "/api/codes/redeem", "/api/v1/itinerary"],
            },
            {
                "id": "simulated_pilot",
                "label": "示範・確定性生成",
                "items": [
                    "23 人可用性測試呈現值",
                    "1,247 份行程的轉化漏斗",
                    "21 日區域熱度、1,860 筆模型校正樣本、5 間商戶累計值",
                ],
                "verify": ["/api/impact/summary", "/api/impact/heat",
                           "/api/impact/merchants"],
                "seed": 20260902,
                "note": "只用於按賽規呈現計劃書指標，不宣稱為真實田野研究。",
            },
        ],
        "formulas": {
            "diversion_coverage_pct": "含舊區/商戶行程數 ÷ 全部行程數 × 100",
            "route_feasible_pct": "通過開放/步行/預算核驗的行程數 ÷ 全部行程數 × 100",
            "merchant_visit_pct": "已核銷一次性到店碼 ÷ 已發出到店碼 × 100",
            "mae": "mean(abs(predicted_crowd_index - observed_crowd_index))",
        },
        "live_code_store_since_last_reset": {
            "issued": live_codes,
            "redeemed": live_redeemed,
            "contains_personal_data": False,
        },
        "proposal_targets": PROPOSAL_TARGETS,
        "source_code": {
            "pilot_single_source_of_truth": "backend/impact.py",
            "dashboard_renderer": "frontend/dashboard.js",
            "automated_checks": ["qa/test_backend.py", "qa/test_api.py",
                                 "qa/test_frontend.py", "qa/test_repo.py"],
        },
    }


# --------------------------------------------------------------------------
# B2B itinerary API (hotels / travel agencies) — proposal's B-end path
# --------------------------------------------------------------------------
_B2B_KEYS = {
    k.strip() for k in os.getenv("EL_B2B_KEYS", "el-demo-2026").split(",") if k.strip()
}


class ItineraryBody(BaseModel):
    query: str = Field(max_length=1000)
    lang: str = Field(default="zh-HK", pattern=r"^(zh-HK|zh|en|pt|ja)$")
    today: str = Field(default="", max_length=32)


@router.post("/api/v1/itinerary")
def b2b_itinerary(body: ItineraryBody, x_api_key: str = Header(default="")):
    if x_api_key not in _B2B_KEYS:
        raise HTTPException(status_code=401,
                            detail="缺少或無效的 X-API-Key（演示金鑰：el-demo-2026）")
    params = parse_request(body.query, override_lang=body.lang,
                           today=(body.today or None))
    lang = params["language"]
    gen = (agent._offline_multi(params, lang) if params.get("days", 1) > 1
           else agent._offline(params, lang))
    itinerary = None
    for event in gen:
        if event.get("type") == "result":
            itinerary = event["itinerary"]
    if itinerary is None:
        raise HTTPException(status_code=500, detail="規劃失敗，請稍後再試")
    t = itinerary.get("totals", {})
    return {
        "api_version": "v1",
        "engine": "deterministic-tools",
        "note": "B 端 API 使用與網站相同的知識庫與 7 項工具；確定性引擎保證低延遲與可重現。",
        "attribution": {
            "old_district_stops": t.get("old_district", 0),
            "local_business_stops": t.get("local_business", 0),
            "est_local_spend_mop": t.get("local_spend_mop", 0),
        },
        "itinerary": itinerary,
    }
