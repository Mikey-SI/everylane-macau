# -*- coding: utf-8 -*-
"""
The 阿濠 travel agent.

It runs a ReAct-style loop (plan -> call tools -> observe -> adapt -> finalise),
streaming every step so the UI can show real "agent capability": planning,
tool calling, multi-step execution and failure recovery.

Two interchangeable "brains" share the SAME real tools and the SAME deterministic
assembler:
  * Qwen brain  (when DASHSCOPE_API_KEY is set) — Qwen drives the loop via
    OpenAI-compatible function calling.
  * Offline brain (no key) — a scripted planner so the demo always runs and
    still shows the full agentic behaviour with real tool execution + real data.
"""
import json
import datetime as dt
import logging
import time

import config
import kb
import tools as T
from llm import get_client, parse_request, LANG_NAME
from geo import walk_minutes, haversine_m, pedestrian_leg

logger = logging.getLogger("everylane.agent")


def _hm(m):
    m = int(round(m))
    return f"{(m // 60) % 24:02d}:{m % 60:02d}"


def _hm_min(value):
    hour, minute = map(int, value.split(":"))
    return hour * 60 + minute


def ev(t, **kw):
    d = {"type": t}
    d.update(kw)
    return d


# --------------------------------------------------------------------------
# short human summaries of tool results (for the live trace)
# --------------------------------------------------------------------------
def _summ(name, res):
    try:
        if name == "get_weather":
            return f"{res['weekday']}・{res['condition']}・{res['temp_c']}°C・{res['advice']}"
        if name == "search_attractions":
            return "找到 " + str(res["count"]) + " 個候選：" + "、".join(r["name"] for r in res["results"][:5]) + ("…" if res["count"] > 5 else "")
        if name == "check_opening":
            return f"{res.get('name','')}：{'開放' if res.get('open') else '✗ ' + res.get('reason','')}（{res.get('hours','')}）"
        if name == "predict_crowd":
            s = f"{res['name']} {res['time'][-5:]} 人流：{res['label']}（{res['crowd_level']}）"
            if res.get("est_wait_min"):
                s += f"，約等 {res['est_wait_min']} 分鐘"
            return s
        if name == "find_local_gem":
            return (f"建議改往 {res['name']}（步行 {res['walk_min']} 分）" if res.get("found")
                    else "附近暫無合適替代點")
        if name == "compute_route":
            return f"已排線：{len(res.get('legs', []))} 段，全程步行約 {res.get('total_km')} 公里 / {res.get('total_walk_min')} 分鐘"
        if name == "estimate_budget":
            return f"預算合計 MOP {res.get('total_mop')}（{res.get('people')} 人）"
    except Exception:
        pass
    return ""


# --------------------------------------------------------------------------
# deterministic assembler — builds the final, verifiable itinerary
# --------------------------------------------------------------------------
_GENERIC_TAGS = {"世界遺產", "免費", "必去", "必看", "必食", "地標"}


def _nice_tag(p):
    for t in p["tags"]:
        if t not in _GENERIC_TAGS:
            return t
    return p["tags"][0] if p["tags"] else ""


def _why_template(p, lang):
    z = lang.startswith("zh")
    tag = _nice_tag(p)
    if p["category"] == "food":
        return (f"本地老字號・{ '・'.join(p['tags'][:2]) }，醫肚兼幫襯街坊小店" if z
                else "A beloved local eatery — taste authentic Macau & support a neighbourhood shop")
    if p["old_district"]:
        return (f"舊區老街・{tag}，遊客少、夠地道，行起上嚟最有澳門味" if z
                else "An authentic old lane — far fewer tourists, the real Macau to wander")
    if p["unesco"]:
        return (f"世界遺產・{tag}，嚟澳門必到" if z
                else "A UNESCO World Heritage site — a must-see in Macau")
    if p["category"] in ("view", "garden"):
        return (f"影相靚位・{tag}，景觀開揚，唞下腳唞下氣" if z
                else "A scenic spot to slow down, breathe and take photos")
    return (f"{tag}，有韻味又唔多人，值得一行" if z else "Characterful and uncrowded — worth a stop")


def _simulate_packed(ids, date, start_min):
    """Simulate the day's schedule and count stops landing in packed windows."""
    packed, cursor = [], start_min
    for i, pid in enumerate(ids):
        p = kb.get(pid)
        if not p:
            continue
        cr = T.predict_crowd(poi_id=pid, datetime=f"{date} {_hm(cursor)}")
        if cr.get("label_en") == "packed":
            packed.append(p["name"]["zh"])
        cursor += p["visit_min"]
        if i < len(ids) - 1:
            nxt = kb.get(ids[i + 1])
            cursor += pedestrian_leg(p, nxt)["walk_min"]
    return packed


def _tune_crowd_timing(ids, date, start_min):
    """Try a few visit orders and keep the one with least packed exposure.
    Crowds peak ~13:30, so shifting hotspots to the schedule edges helps."""
    if len(ids) < 3:
        return ids, _simulate_packed(ids, date, start_min), False
    hot = [i for i in ids if kb.get(i) and kb.get(i)["hotspot"]]
    cool = [i for i in ids if i not in hot]
    candidates = [list(ids), hot + cool, cool + hot, list(reversed(ids))]
    best, best_packed = None, None
    for cand in candidates:
        pk = _simulate_packed(cand, date, start_min)
        km = T.compute_route(poi_ids=cand, optimize=False)["total_km"]
        key = (len(pk), km)
        if best is None or key < best_packed:
            best, best_packed = (cand, pk), key
    ids2, pk2 = best
    return ids2, pk2, ids2 != list(ids)


def _cluster_districts(params):
    """Pick a coherent, *walkable* zone for a one-day trip. The Macau peninsula
    historic centre (central + inner_harbour) is a compact UNESCO walking trail;
    Taipa and Coloane are separate islands needing transport, so we keep a day
    within one zone to keep walking realistic."""
    d = params.get("district")
    if not d:
        # if the user named an island POI explicitly, anchor the day there
        for pid in params.get("requested_ids", []):
            p = kb.get(pid)
            if p and p["district"] in ("taipa", "coloane"):
                d = p["district"]
                break
    if d in ("taipa", "coloane"):
        return [d]
    if d == "guia":
        return ["guia", "central"]
    return ["central", "inner_harbour", "guia"]


def _make_open_schedule(ids, date, start_min, max_wait=30):
    """Build a time-aware schedule and reject stops outside visit-time hours."""
    schedule, changes = [], []
    cursor, previous = start_min, None
    for pid in ids:
        p = kb.get(pid)
        if not p:
            continue
        if previous:
            a = kb.get(previous)
            cursor += pedestrian_leg(a, p)["walk_min"]
        arrive = cursor
        if arrive < p["open_min"]:
            wait = p["open_min"] - arrive
            if wait > max_wait:
                changes.append(f"{p['name']['zh']} 要等 {wait} 分鐘先開，已移除")
                continue
            arrive = p["open_min"]
            changes.append(f"{p['name']['zh']} 開門前等候 {wait} 分鐘")
        depart = arrive + p["visit_min"]
        if arrive >= p["close_min"] or depart > p["close_min"]:
            changes.append(f"{p['name']['zh']} 到達時已關門或停留時間不足，已移除")
            continue
        schedule.append({"poi_id": pid, "arrive": arrive, "depart": depart})
        cursor, previous = depart, pid
    return schedule, changes


def _best_open_schedule(ids, date, start_min):
    """Choose a walkable order that maximises stops valid at arrival time."""
    candidates = [
        list(ids),
        sorted(ids, key=lambda pid: (kb.get(pid)["open_min"], kb.get(pid)["crowd_base"])),
        sorted(ids, key=lambda pid: (kb.get(pid)["category"] == "food", kb.get(pid)["open_min"])),
        list(reversed(ids)),
    ]
    best = None
    for candidate in candidates:
        schedule, changes = _make_open_schedule(candidate, date, start_min)
        valid_ids = [slot["poi_id"] for slot in schedule]
        route_km = T.compute_route(poi_ids=valid_ids, optimize=False).get("total_km", 99)
        wait_count = sum("等候" in change for change in changes)
        key = (-len(valid_ids), wait_count, route_km)
        if best is None or key < best[0]:
            best = (key, candidate, schedule, changes)
    _, chosen, schedule, changes = best
    if chosen != list(ids):
        changes.insert(0, "已按實際開放時段重排到訪次序")
    return schedule, changes


def assemble(params, ordered_ids, diversions, lang, why_map=None, notes=None):
    diversions = diversions or []
    why_map = why_map or {}
    notes = list(notes or [])
    date = params["date"]
    d = dt.date.fromisoformat(date)
    weekday_zh = T.WEEKDAY_ZH[d.weekday()]
    weather = T.get_weather(date=date)
    people = params["people"]

    # Keep only unique, valid and open POIs. The Qwen brain is instructed to
    # verify every stop, but deterministic enforcement prevents a hallucinated
    # or closed id from ever reaching the final itinerary.
    ids, seen, removed = [], set(), []
    for pid in ordered_ids:
        if pid in seen:
            continue
        seen.add(pid)
        p = kb.get(pid)
        if not p:
            removed.append(str(pid))
            continue
        if not T.check_opening(poi_id=pid, date=date)["open"]:
            removed.append(p["name"]["zh"])
            continue
        ids.append(pid)
    if removed:
        notes.append("安全核對已移除無效、重複或當日休息的站點：" + "、".join(removed))
    schedule, time_changes = _best_open_schedule(ids, date, params["start_min"])
    ids = [slot["poi_id"] for slot in schedule]
    if time_changes:
        notes.extend(time_changes)
    route = T.compute_route(poi_ids=ids, optimize=False)
    legs = {(l["from"], l["to"]): l for l in route["legs"]}

    stops = []
    total_cost = total_local_spend = total_walk = 0
    packed = busy = 0
    name_seq = [kb.get(i)["name"]["zh"] for i in ids]
    for idx, (pid, slot) in enumerate(zip(ids, schedule)):
        p = kb.get(pid)
        arrive = slot["arrive"]
        depart = slot["depart"]
        crowd = T.predict_crowd(poi_id=pid, datetime=f"{date} {_hm(arrive)}")
        if crowd.get("label_en") == "packed":
            packed += 1
            if not any(dv.get("from") in (p["name"]["zh"], p["name"]["en"]) for dv in diversions):
                alt = T.find_local_gem(near_poi_id=pid)
                if alt.get("found"):
                    ap = kb.get(alt["id"])
                    if lang.startswith("zh"):
                        frm, to = p["name"]["zh"], ap["name"]["zh"]
                        reason = f"{frm} 到訪時段極擁擠，建議先分流到步行約 {alt['walk_min']} 分鐘的 {to}"
                    else:
                        frm, to = p["name"]["en"], ap["name"]["en"]
                        reason = f"{frm} is packed at this time; divert first to {to}, about {alt['walk_min']} minutes away"
                    diversions.append({"from": frm, "to": to, "reason": reason})
        elif crowd.get("label_en") == "busy":
            busy += 1
        walk_next = None
        if idx < len(ids) - 1:
            key = (name_seq[idx], name_seq[idx + 1])
            leg = legs.get(key)
            if leg:
                walk_next = {"min": leg["walk_min"], "km": round(leg["distance_m"] / 1000, 2),
                             "to": name_seq[idx + 1],
                             "via": leg.get("via") or []}
                total_walk += leg["walk_min"]
        cost = p["cost_mop"] * people
        total_cost += cost
        if p["local_business"]:
            total_local_spend += cost
        stops.append({
            "order": idx + 1, "poi_id": pid,
            "name": p["name"], "category": p["category"],
            "district_name": p["district_name"], "zone": p["zone"],
            "lat": p["lat"], "lng": p["lng"], "image": p["image"],
            "arrive": _hm(arrive), "depart": _hm(depart), "visit_min": p["visit_min"],
            "why": why_map.get(pid) or _why_template(p, lang),
            "blurb": p["blurb"], "tip": p.get("tip", {}).get("zh"),
            "story": p.get("story") or {},
            "story_zh": (p.get("story") or {}).get("zh-HK") or p.get("story_zh"),
            "tags": p["tags"], "unesco": p["unesco"],
            "old_district": p["old_district"], "local_business": p["local_business"],
            "cost_mop": cost,
            "crowd": {"level": crowd["crowd_level"], "label": crowd["label"],
                      "label_en": crowd["label_en"], "wait": crowd.get("est_wait_min", 0)},
            "accessibility": kb.accessibility(pid),
            "walk_to_next": walk_next, "wiki_url": p.get("wiki_url"),
        })
    old_cnt = sum(1 for s in stops if s["old_district"])
    local_cnt = sum(1 for s in stops if s["local_business"])
    end_min = params["start_min"] if not schedule else schedule[-1]["depart"]

    # ---- constraint verification (drives the "任務完成度" panel) ----
    checks = []
    all_open = True
    for stop in stops:
        p = kb.get(stop["poi_id"])
        op = T.check_opening(poi_id=stop["poi_id"], date=date, time=stop["arrive"])
        if not op["open"] or _hm_min(stop["depart"]) > p["close_min"]:
            all_open = False
    checks.append({"label": "全部景點當日開放", "ok": all_open,
                   "detail": "已逐一核實開放時間與休息日" if all_open else "仍有景點當日休息"})
    if params.get("budget"):
        ok = total_cost <= params["budget"]
        checks.append({"label": f"預算 ≤ MOP {params['budget']}", "ok": ok,
                       "detail": f"實際約 MOP {total_cost}（{people} 人）"})
    walk_km = round(route["total_km"], 2)
    if params.get("low_walk"):
        ok = walk_km <= 3.6
        checks.append({"label": "步行輕鬆（≤ 3.6 公里）", "ok": ok,
                       "detail": f"全程約 {walk_km} 公里"})
    # A packed stop still counts as "handled" when we explicitly divert its
    # crowd to a quieter nearby lane — that is the product's signature move.
    crowd_ok = packed == 0 or (packed <= 1 and len(diversions) > 0)
    checks.append({"label": "避開人潮熱點", "ok": crowd_ok,
                   "detail": ("無景點處於『極擁擠』時段" if packed == 0 else
                              (f"{packed} 個熱點已配對舊區導流替代點" if crowd_ok else f"仍有 {packed} 個站點極擁擠"))
                             + (f"（{busy} 個適度繁忙，已盡量提早）" if busy else "")})
    checks.append({"label": "帶旺舊區・本地小店", "ok": (old_cnt + local_cnt) >= 2,
                   "detail": f"納入 {old_cnt} 個舊區老街、{local_cnt} 間本地小店"})

    title = {"zh-HK": "你的澳門深度漫遊", "zh": "你的澳门深度漫游", "en": "Your Macau Deep-Travel Day",
             "pt": "O Teu Dia em Macau", "ja": "あなたのマカオ深度さんぽ"}.get(lang, "你的澳門深度漫遊")

    summary = (f"為你（{people}人）規劃咗 {date}（{weekday_zh}）嘅澳門深度遊："
               f"共 {len(stops)} 站，當中 {old_cnt} 條舊區老街、{local_cnt} 間本地小店；"
               f"特登避開正午人潮，全程步行約 {walk_km} 公里，"
               f"預算約 MOP {total_cost}。") if lang.startswith("zh") else (
        f"A {len(stops)}-stop deep-travel day for {people} in Macau on {date} ({weekday_zh}): "
        f"{old_cnt} old-district lanes and {local_cnt} local shops, timed to dodge midday crowds — "
        f"about {walk_km} km on foot, roughly MOP {total_cost}.")

    distance_note = (
        "步行距離以舊城巷道錨點（議事亭、福隆新街、官也街等）折算，"
        "不是 OSM 逐路口導航；實際樓梯與無障礙繞行請以現場為準。"
    )
    if distance_note not in notes:
        notes.append(distance_note)

    return {
        "title": title, "summary": summary, "language": lang,
        "language_name": LANG_NAME.get(lang, lang),
        "date": date, "weekday": weekday_zh, "weather": weather,
        "totals": {"stops": len(stops), "cost_mop": total_cost,
                   "local_spend_mop": total_local_spend,
                   "walk_min": total_walk, "walk_km": walk_km,
                   "old_district": old_cnt, "local_business": local_cnt,
                   "start": _hm(params["start_min"]), "end": _hm(end_min)},
        "constraints": checks,
        "diversions": diversions or [],
        "notes": notes,
        "stops": stops,
    }


def _combine_days(params, day_its, lang):
    """Combine several single-day itineraries into one multi-day result.

    Each day is still produced by the same ReAct/tool pipeline, so multi-day
    mode stays verifiable instead of becoming a static template.
    """
    people = params["people"]
    all_stops = []
    totals = {"stops": 0, "cost_mop": 0, "local_spend_mop": 0,
              "walk_min": 0, "walk_km": 0,
              "old_district": 0, "local_business": 0}
    all_open = True
    packed = 0
    diversions, notes = [], []

    for di, day in enumerate(day_its, 1):
        day["day_no"] = di
        day["label"] = f"Day {di}"
        totals["stops"] += day["totals"]["stops"]
        totals["cost_mop"] += day["totals"]["cost_mop"]
        totals["local_spend_mop"] += day["totals"].get("local_spend_mop", 0)
        totals["walk_min"] += day["totals"]["walk_min"]
        totals["walk_km"] += day["totals"]["walk_km"]
        totals["old_district"] += day["totals"]["old_district"]
        totals["local_business"] += day["totals"]["local_business"]
        diversions.extend(day.get("diversions") or [])
        notes.extend(day.get("notes") or [])
        for ck in day.get("constraints") or []:
            if "開放" in ck["label"] and not ck["ok"]:
                all_open = False
            if "避開人潮" in ck["label"] and not ck["ok"]:
                packed += 1
        for s in day.get("stops") or []:
            cp = dict(s)
            cp["day_no"] = di
            cp["map_order"] = f"{di}-{s['order']}"
            all_stops.append(cp)

    totals["walk_km"] = round(totals["walk_km"], 2)
    days = len(day_its)
    first = day_its[0]["date"]
    last = day_its[-1]["date"]
    date_range = first if first == last else f"{first} → {last}"
    old_cnt = totals["old_district"]
    local_cnt = totals["local_business"]
    z = lang.startswith("zh")

    title = ("你的澳門多日深度漫遊" if z else "Your Multi-Day Macau Deep Trip")
    summary = (f"為你規劃咗 {days} 日澳門深度遊：每日鎖定一個可步行片區，"
               f"由半島世遺老城、氹仔舊村到路環慢活分日完成；"
               f"合共 {totals['stops']} 站，{old_cnt} 個舊區/老街點、{local_cnt} 間本地小店，"
               f"總步行約 {totals['walk_km']} 公里，總預算約 MOP {totals['cost_mop']}。") if z else (
        f"A {days}-day Macau deep trip: one coherent walkable zone per day, "
        f"covering the peninsula, Taipa and Coloane where possible. "
        f"{totals['stops']} stops, {old_cnt} old-district places and {local_cnt} local shops, "
        f"about {totals['walk_km']} km total on foot and roughly MOP {totals['cost_mop']}.")

    checks = [
        {"label": "多日路線分區合理", "ok": True,
         "detail": f"{days} 日分別規劃，避免同一天跨島亂跑"},
        {"label": "全部景點當日開放", "ok": all_open,
         "detail": "每一日均逐站核實開放時間與休息日"},
        {"label": "避開人潮熱點", "ok": packed == 0,
         "detail": "每日均檢查熱門點時段，必要時加入舊區導流"},
        {"label": "帶旺舊區・本地小店", "ok": (old_cnt + local_cnt) >= days * 2,
         "detail": f"全程納入 {old_cnt} 個舊區/老街點、{local_cnt} 間本地小店"},
    ]
    if params.get("budget"):
        checks.insert(2, {"label": f"總預算 ≤ MOP {params['budget']}", "ok": totals["cost_mop"] <= params["budget"],
                          "detail": f"全程估算 MOP {totals['cost_mop']}（{people} 人）"})

    seen_notes = []
    for n in notes:
        if n and n not in seen_notes:
            seen_notes.append(n)

    return {
        "title": title, "summary": summary, "language": lang,
        "language_name": LANG_NAME.get(lang, lang),
        "date": date_range, "weekday": f"{days} 日行程",
        "weather": day_its[0].get("weather", {}),
        "days": day_its,
        "totals": totals,
        "constraints": checks,
        "diversions": diversions,
        "notes": seen_notes[:5],
        "stops": all_stops,
    }


# --------------------------------------------------------------------------
# OFFLINE BRAIN — scripted planner using the real tools
# --------------------------------------------------------------------------
def _offline(params, lang, engine="verified-tools", runtime_note=None,
             emit_runtime=True):
    date = params["date"]
    interests = params["interests"]
    people = params["people"]
    cluster = _cluster_districts(params)
    excl = set(params.get("exclude_ids") or [])  # POIs already used on other days

    def in_cluster(p):
        return kb.get(p["id"])["district"] in cluster and p["id"] not in excl

    if emit_runtime:
        yield ev(
            "runtime",
            engine=engine,
            label="可重現工具鏈",
            note=runtime_note or "使用同一知識庫、7 項真實工具與確定性安全核對；結果可重現。",
        )
    yield ev("status", stage="start", text=f"阿濠開始規劃（{LANG_NAME.get(lang, lang)}）…")
    yield ev("plan", steps=[
        "理解需求：日期、人數、興趣、預算、步行偏好",
        "查當日天氣，決定室內/室外比重",
        "鎖定一個可步行嘅地理片區，避免跨島亂跑",
        "搜尋景點：1 個地標 + 多個舊區老街 + 本地美食",
        "逐一核實開放時間（休息日自動改線）",
        "預測人流，將遊客從擠爆熱點導流到寧靜老街",
        "規劃步行路線、核算預算，輸出可驗證行程",
    ])

    # 1) weather
    yield ev("tool_call", name="get_weather", args={"date": date})
    w = T.get_weather(date=date)
    yield ev("tool_result", name="get_weather", summary=_summ("get_weather", w), data=w)
    rainy = w["rain"]
    if rainy:
        yield ev("thought", text="當日有雨，會多安排室內景點（教堂、大屋、博物館），減少戶外暴曬與淋雨。")

    zone_label = {"taipa": "氹仔舊城區", "coloane": "路環"}.get(params.get("district"),
                 "澳門半島歷史城區（中區＋內港）")
    yield ev("thought", text=f"一日步行團鎖定【{zone_label}】，景點集中、唔使搭車跨島，行起上嚟先順。")

    # 2) search within the walkable cluster
    yield ev("thought", text=f"用戶興趣：{ '、'.join(interests) }。策略：揀 1 個必到地標做錨點，其餘盡量係舊區老街同本地小店。")
    yield ev("tool_call", name="search_attractions", args={"interests": interests, "district": params.get("district"), "prefer_local": True, "limit": 14})
    sr = T.search_attractions(interests=interests, district=params.get("district"), prefer_local=True, limit=14)
    yield ev("tool_result", name="search_attractions", summary=_summ("search_attractions", sr), data=sr)

    cand = [r for r in sr["results"] if in_cluster(r)]
    # widen if interest filter left too few in this zone
    if len(cand) < 6:
        extra = T.search_attractions(prefer_local=True, limit=40)
        for r in extra["results"]:
            if in_cluster(r) and r["id"] not in {c["id"] for c in cand}:
                cand.append(r)

    famous = [r for r in cand if r["hotspot"] and r["unesco"]]
    if not famous:  # guarantee an iconic anchor for the zone
        for pref in ("ruins_st_paul", "senado_square", "rua_cunha", "a_ma_temple"):
            p = kb.get(pref)
            if p and p["district"] in cluster and pref not in excl:
                famous = [{"id": p["id"], "name": p["name"]["zh"], "category": p["category"],
                           "hotspot": True, "unesco": p["unesco"], "old_district": p["old_district"],
                           "local_business": p["local_business"]}]
                break
    food = [r for r in cand if r["category"] == "food"]
    oldstreet = [r for r in cand if r["old_district"] and r["category"] != "food"]
    quiet = [r for r in cand if not r["hotspot"] and r["category"] in ("heritage", "temple", "view", "garden", "museum")]

    target = 4 if (params["half_day"] or params["low_walk"]) else 6
    chosen, seen = [], set()

    def add(r):
        if r and r["id"] not in seen and len(chosen) < target:
            chosen.append(r); seen.add(r["id"]); return True
        return False

    def as_card(p):
        return {"id": p["id"], "name": p["name"]["zh"], "category": p["category"],
                "hotspot": p["hotspot"], "unesco": p["unesco"],
                "old_district": p["old_district"], "local_business": p["local_business"]}

    anchor_id = None
    # explicitly-requested POIs first (respect what the user asked for)
    req_in_zone = [pid for pid in params.get("requested_ids", [])
                   if kb.get(pid) and kb.get(pid)["district"] in cluster and pid not in excl]
    if req_in_zone:
        yield ev("thought", text="用戶指名要去：" + "、".join(kb.get(i)["name"]["zh"] for i in req_in_zone) + "，優先納入行程。")
        for pid in req_in_zone:
            add(as_card(kb.get(pid)))
    if famous and not any(c["id"] in {f["id"] for f in famous} for c in chosen):
        add(famous[0])
    anchor_id = (famous[0]["id"] if famous else (chosen[0]["id"] if chosen else None))
    # a premium cultural house for history/culture lovers (often has a weekly closure)
    if any(i in ("歷史", "历史", "文化", "history", "culture") for i in interests):
        for pid in ("mandarin_house", "lou_kau_mansion"):
            p = kb.get(pid)
            if p and p["district"] in cluster and pid not in seen and pid not in excl:
                add(as_card(p)); break
    for r in oldstreet:
        add(r)
    for r in quiet:
        if len(chosen) >= target - 1:
            break
        add(r)
    if food and not any(c["category"] == "food" for c in chosen):
        if len(chosen) >= target and len(chosen) > 2:
            chosen.pop(); seen = {c["id"] for c in chosen}
        add(food[0])
    for r in cand:
        add(r)

    yield ev("thought", text="初步揀咗：" + "、".join(c["name"] for c in chosen) + "。下一步逐個核實當日開放。")

    # 3) opening checks + FAILURE RECOVERY
    final, used = [], set(c["id"] for c in chosen)
    for c in chosen:
        yield ev("tool_call", name="check_opening", args={"poi_id": c["id"], "date": date})
        op = T.check_opening(poi_id=c["id"], date=date)
        yield ev("tool_result", name="check_opening", summary=_summ("check_opening", op), data=op)
        if op["open"]:
            final.append(c); continue
        yield ev("thought", text=f"⚠️ {c['name']} 當日休息，要改線。喺同片區搵一個有開、同樣有韻味嘅替代點。")
        replaced = None
        for r in cand:
            if r["id"] in used:
                continue
            ro = T.check_opening(poi_id=r["id"], date=date)
            if ro["open"]:
                replaced = kb.get(r["id"]); break
        if replaced:
            used.add(replaced["id"])
            final.append({"id": replaced["id"], "name": replaced["name"]["zh"], "category": replaced["category"],
                          "hotspot": replaced["hotspot"], "unesco": replaced["unesco"],
                          "old_district": replaced["old_district"], "local_business": replaced["local_business"]})
            yield ev("recovery", frm=c["name"], to=replaced["name"]["zh"],
                     reason=f"{c['name']} 當日休息，自動改為同區嘅 {replaced['name']['zh']}")
            yield ev("thought", text=f"✅ 已將 {c['name']} 換成 {replaced['name']['zh']}，行程照樣順暢。")
            if c["id"] == anchor_id:
                anchor_id = replaced["id"]
    chosen = final or chosen
    seen = {c["id"] for c in chosen}

    # 4) crowd-aware diversion (signature feature): anchor packed -> add nearby gem
    diversions = []
    if anchor_id:
        yield ev("tool_call", name="predict_crowd", args={"poi_id": anchor_id, "datetime": f"{date} 13:00"})
        cr = T.predict_crowd(poi_id=anchor_id, datetime=f"{date} 13:00")
        yield ev("tool_result", name="predict_crowd", summary=_summ("predict_crowd", cr), data=cr)
        aname = kb.get(anchor_id)["name"]["zh"]
        if cr["label_en"] in ("busy", "packed"):
            yield ev("thought", text=f"{aname} 正午{cr['label']}。對策：① 安排最早去，避開人潮；② 用 find_local_gem 搵附近寧靜老街，順手帶旺本地。")
            yield ev("tool_call", name="find_local_gem", args={"near_poi_id": anchor_id})
            gem = T.find_local_gem(near_poi_id=anchor_id)
            yield ev("tool_result", name="find_local_gem", summary=_summ("find_local_gem", gem), data=gem)
            if gem.get("found") and gem["id"] in excl:
                gem = {"found": False}
            if gem.get("found"):
                g = kb.get(gem["id"])
                go = T.check_opening(poi_id=g["id"], date=date)
                if go["open"]:
                    if gem["id"] in seen:
                        diversions.append({"from": aname, "to": g["name"]["zh"],
                                           "reason": f"{aname}正午{cr['label']}，已將人流分流到行程內嘅{g['name']['zh']}（步行{gem['walk_min']}分），人少又地道"})
                    else:
                        if len(chosen) >= target + 1:
                            chosen = chosen[:target]
                        chosen.append({"id": g["id"], "name": g["name"]["zh"], "category": g["category"],
                                       "hotspot": g["hotspot"], "unesco": g["unesco"],
                                       "old_district": g["old_district"], "local_business": g["local_business"]})
                        seen.add(g["id"])
                        diversions.append({"from": aname, "to": g["name"]["zh"],
                                           "reason": f"{aname}正午{cr['label']}，加插附近嘅{g['name']['zh']}（步行{gem['walk_min']}分）分流，人少又帶旺本地"})

    # 5) route optimisation (start at the anchor so we hit it earliest)
    ids = [c["id"] for c in chosen]
    yield ev("tool_call", name="compute_route", args={"poi_ids": ids, "optimize": True, "start_id": anchor_id})
    route = T.compute_route(poi_ids=ids, optimize=True, start_id=anchor_id)
    yield ev("tool_result", name="compute_route", summary=_summ("compute_route", route), data=route)
    ids = route["ordered_ids"]

    # 5b) low-walk trimming: drop farthest tail stops until within cap
    if params["low_walk"]:
        while len(ids) > 3:
            r2 = T.compute_route(poi_ids=ids, optimize=False)
            if r2["total_km"] <= 3.6:
                break
            drop = kb.get(ids[-1])["name"]["zh"]
            ids = ids[:-1]
            yield ev("recovery", frm=drop, to="（縮短行程）",
                     reason=f"用戶想行少啲，移除最遠嘅 {drop}，將全程步行控制喺 3.6 公里內")

    # 5c) crowd-timing pass: if any stop still lands in a "packed" window,
    #     re-order so hotspots sit at the schedule edges (off-peak)
    packed_now = _simulate_packed(ids, date, params["start_min"])
    if packed_now:
        yield ev("thought", text=f"按目前次序，{ '、'.join(packed_now) } 會撞正人潮高峰。試緊調動次序，令熱點避開 13:30 前後嘅高峰時段…")
        ids2, packed_after, changed = _tune_crowd_timing(ids, date, params["start_min"])
        if changed and len(packed_after) < len(packed_now):
            ids = ids2
            yield ev("recovery", frm="原路線次序", to="錯峰次序",
                     reason=f"重排訪問次序避開人潮高峰：極擁擠站點由 {len(packed_now)} 個減至 {len(packed_after)} 個")
        elif packed_after:
            yield ev("thought", text=f"高峰難以完全避開（{ '、'.join(packed_after) }），已盡量提早／延後到訪並保留導流建議。")

    # 6) budget + recovery if over
    yield ev("tool_call", name="estimate_budget", args={"poi_ids": ids, "people": people})
    bud = T.estimate_budget(poi_ids=ids, people=people)
    yield ev("tool_result", name="estimate_budget", summary=_summ("estimate_budget", bud), data=bud)
    if params.get("budget") and bud["total_mop"] > params["budget"]:
        yield ev("thought", text=f"預算超咗（MOP {bud['total_mop']} > {params['budget']}）。對策：剔走最貴而非必要嘅收費點，再核算。")
        for p in sorted([kb.get(i) for i in ids], key=lambda x: -x["cost_mop"]):
            if p["cost_mop"] > 0 and len(ids) > 3:
                ids.remove(p["id"])
                yield ev("recovery", frm=p["name"]["zh"], to="（移除收費項）",
                         reason=f"為控制預算，移除收費較高的 {p['name']['zh']}（MOP {p['cost_mop']}/人）")
                if T.estimate_budget(poi_ids=ids, people=people)["total_mop"] <= params["budget"]:
                    break

    notes = []
    if rainy:
        notes.append("當日有雨：行程已偏重室內景點，記得帶遮。")
    notes.append("世遺景點多數免費入場，費用主要落喺餐飲，啱晒幫襯本地老字號。")
    notes.append("人流預測以星期與時段估算，實際以現場為準；熱點愈早去愈舒服。")

    yield ev("status", stage="assemble", text="整合行程、核對所有限制條件…")
    itinerary = assemble(params, ids, diversions, lang, notes=notes)
    itinerary["engine"] = engine
    yield ev("result", itinerary=itinerary)
    yield ev("done")


def _multi_day_districts(params):
    raw = (params.get("raw") or "").lower()
    fixed_one_zone = any(k in raw for k in ["只玩", "只去", "淨係", "净係", "only"])
    if params.get("district") and fixed_one_zone:
        return [params["district"]] * params.get("days", 1)
    # A competition-friendly Macau story arc: UNESCO peninsula -> Taipa village
    # -> Coloane slow living -> Guia/New Port museums -> peninsula deep dive.
    return [None, "taipa", "coloane", "guia", "inner_harbour"][:params.get("days", 1)]


def _offline_multi(params, lang, engine="verified-tools", runtime_note=None):
    days = max(2, min(int(params.get("days", 2)), 5))
    base_date = dt.date.fromisoformat(params["date"])
    districts = _multi_day_districts(params)
    yield ev(
        "runtime",
        engine=engine,
        label="多日可重現工具鏈",
        note=runtime_note or "逐日使用同一知識庫與 7 項工具核驗，確保分區合理、結果可重現。",
    )
    yield ev("status", stage="multi_day", text=f"偵測到 {days} 日行程，阿濠會每日鎖定一個片區，避免跨島亂跑。")
    yield ev("plan", steps=[
        "將多日需求拆成每日一個可步行片區",
        "Day 1 優先半島世遺與舊區導流",
        "Day 2 優先氹仔舊城區與地道美食",
        "Day 3 起加入路環慢活、自然海岸或松山博物館線",
        "每日各自查天氣、核實開放、人流導流、路線與預算",
        "最後合併成多日總覽、每日地圖與每日時間軸",
    ])

    day_its = []
    used_ids = set()
    for i in range(days):
        d = base_date + dt.timedelta(days=i)
        dp = dict(params)
        dp["days"] = 1
        dp["date"] = d.isoformat()
        dp["district"] = districts[i] if i < len(districts) else None
        dp["exclude_ids"] = sorted(used_ids)  # never repeat a stop across days
        if params.get("budget"):
            dp["budget"] = max(1, int(params["budget"] / days))
        # Keep full days useful; half-day only if user explicitly asked for <=1 day.
        dp["half_day"] = False if days > 1 else params["half_day"]

        day_name = {None: "澳門半島歷史城區", "taipa": "氹仔舊城區",
                    "coloane": "路環慢活", "guia": "松山/新口岸",
                    "inner_harbour": "內港/媽閣"}.get(dp["district"], dp["district"])
        yield ev("status", stage=f"day_{i + 1}", text=f"Day {i + 1}：規劃 {day_name}（{dp['date']}）")
        for e in _offline(dp, lang, engine=engine, emit_runtime=False):
            if e["type"] == "result":
                it = e["itinerary"]
                it["day_no"] = i + 1
                it["day_title"] = f"Day {i + 1} · {day_name}"
                day_its.append(it)
                used_ids.update(s["poi_id"] for s in it["stops"])
            elif e["type"] == "done":
                continue
            else:
                yield e

    yield ev("status", stage="assemble", text="合併多日行程，計算總步行、總預算與總導流成效…")
    itinerary = _combine_days(params, day_its, lang)
    itinerary["engine"] = engine
    yield ev("result", itinerary=itinerary)
    yield ev("done")


# --------------------------------------------------------------------------
# QWEN BRAIN — real ReAct loop via DashScope function calling
# --------------------------------------------------------------------------
_SUBMIT_SCHEMA = {"type": "function", "function": {
    "name": "submit_itinerary",
    "description": "在完成天氣查詢、景點搜尋、逐一開放核實、人流預測與導流、路線與預算計算後，提交最終行程。",
    "parameters": {"type": "object", "properties": {
        "title": {"type": "string"},
        "summary": {"type": "string", "description": "用所選語言寫的一段總結"},
        "ordered_poi_ids": {"type": "array", "items": {"type": "string"}, "description": "已排好順序的景點 id 列表"},
        "stop_reasons": {"type": "array", "items": {"type": "object", "properties": {
            "poi_id": {"type": "string"}, "reason": {"type": "string"}}},
            "description": "每個景點一句推薦理由（所選語言）"},
        "diversions": {"type": "array", "items": {"type": "object", "properties": {
            "from": {"type": "string"}, "to": {"type": "string"}, "reason": {"type": "string"}}}},
        "notes": {"type": "array", "items": {"type": "string"}},
    }, "required": ["ordered_poi_ids"]}}}


def _system_prompt(params, lang):
    poi_lines = []
    for p in kb.all_pois():
        flags = []
        if p["unesco"]:
            flags.append("世遺")
        if p["hotspot"]:
            flags.append("熱門")
        if p["old_district"]:
            flags.append("舊區老街")
        if p["local_business"]:
            flags.append("本地小店")
        closed = ("，逢" + "、".join(T.WEEKDAY_ZH[d] for d in p["closed_days"]) + "休") if p["closed_days"] else ""
        poi_lines.append(f'{p["id"]}｜{p["name"]["zh"]}（{p["category"]}/{p["district_name"]}）'
                         f'[{",".join(flags) or "一般"}] 停留{p["visit_min"]}分 費用{p["cost_mop"]}{closed}')
    catalog = "\n".join(poi_lines)
    return f"""你係「街知巷聞」嘅澳門資深本地導遊智能體，花名【阿濠】，講嘢親切、有澳門老街坊味道。
你嘅使命：唔單止帶遊客去大三巴、議事亭呢啲逼爆嘅熱點，仲要將佢哋【導流到舊區老街同本地小店】，
做到「避開人潮、深度體驗、帶旺社區」三贏。

【今次需求】語言={LANG_NAME.get(lang, lang)}；日期={params['date']}；人數={params['people']}；
興趣={'、'.join(params['interests'])}；預算={params['budget'] or '未指定'}；
少行路={params['low_walk']}；半日={params['half_day']}；開始時間={_hm(params['start_min'])}。

【你必須遵守嘅工作流程（ReAct）】
1. 先 get_weather 查天氣，落雨就多安排室內點。
2. search_attractions 搜候選（記得用 prefer_local 帶出舊區老街/本地小店）。
3. 揀 4-6 個景點，做到「1 個地標 + 多個舊區老街/本地小店 + 至少 1 個美食」嘅平衡。
   一日只可集中同一個可步行片區；半島、氹仔、路環不可混成全程步行路線。
4. 對【每一個】揀中嘅景點呼叫 check_opening 核實當日係咪開放；若果休息，要改揀第二個（失敗恢復）。
5. 對熱門地標呼叫 predict_crowd；若擁擠/極擁擠，用 find_local_gem 搵附近寧靜老街導流，並寫入 diversions。
6. compute_route 排好步行路線；estimate_budget 核算預算，若超支就移除最貴而非必要嘅收費點。
7. 全部完成後，呼叫 submit_itinerary 提交（ordered_poi_ids 必須係知識庫真實 id；stop_reasons 用所選語言）。

【景點知識庫（只可使用以下 id）】
{catalog}

務必逐步呼叫工具，唔好自己亂作開放時間或人流；所有結論要基於工具返回嘅真實數據。"""


def _sanitize_qwen_ids(params, proposed_ids):
    """Deterministically enforce location, opening, walking and budget rules."""
    allowed_districts = set(_cluster_districts(params))
    date = params["date"]
    ids, seen, changes = [], set(), []
    for pid in proposed_ids or []:
        p = kb.get(pid)
        if not p or pid in seen:
            continue
        seen.add(pid)
        if p["district"] not in allowed_districts:
            changes.append(f"移除跨區站點 {p['name']['zh']}")
            continue
        if not T.check_opening(poi_id=pid, date=date)["open"]:
            changes.append(f"移除當日休息站點 {p['name']['zh']}")
            continue
        ids.append(pid)

    if params.get("low_walk"):
        while len(ids) > 3 and T.compute_route(poi_ids=ids, optimize=False)["total_km"] > 3.6:
            p = kb.get(ids.pop())
            changes.append(f"為少行路移除 {p['name']['zh']}")

    if params.get("budget"):
        while len(ids) > 3:
            total = T.estimate_budget(poi_ids=ids, people=params["people"])["total_mop"]
            if total <= params["budget"]:
                break
            costly = max(ids, key=lambda pid: kb.get(pid)["cost_mop"])
            if kb.get(costly)["cost_mop"] <= 0:
                break
            ids.remove(costly)
            changes.append(f"為控制預算移除 {kb.get(costly)['name']['zh']}")
    return ids, changes


def _qwen(params, lang):
    client = get_client()
    started = time.monotonic()
    yield ev(
        "runtime",
        engine="qwen:" + config.QWEN_MODEL,
        label=f"Qwen {config.QWEN_MODEL}",
        note="真實 Qwen function calling；所有事實仍由工具返回並經確定性安全核對。",
    )
    yield ev("status", stage="start", text=f"阿濠（Qwen {config.QWEN_MODEL}）開始規劃…")
    messages = [
        {"role": "system", "content": _system_prompt(params, lang)},
        {"role": "user", "content": params["raw"] or "幫我計劃一日澳門深度遊"},
    ]
    all_tools = T.TOOL_SCHEMAS + [_SUBMIT_SCHEMA]
    diversions, why_map, notes, final_ids = [], {}, [], None
    title = summary = None
    called_tools, checked_ids = set(), set()
    required_tools = {
        "get_weather", "search_attractions", "check_opening",
        "predict_crowd", "compute_route", "estimate_budget",
    }

    for step in range(config.MAX_AGENT_STEPS):
        remaining = config.AGENT_DEADLINE_S - (time.monotonic() - started)
        if remaining <= 3:
            yield ev("thought", text="Qwen 已完成部分決策，但現場時間預算已到；由可重現工具鏈接手完成，避免路演等待。")
            yield from _offline(
                params,
                lang,
                engine="fallback-tools",
                runtime_note="Qwen 時間預算到達後自動接管；沿用同一知識庫、工具與安全核對。",
            )
            return
        try:
            resp = client.chat.completions.create(
                model=config.QWEN_MODEL, messages=messages,
                tools=all_tools, tool_choice="auto", temperature=0.2,
                max_tokens=1200,
                timeout=min(config.QWEN_TIMEOUT_S, remaining),
            )
        except Exception as e:
            logger.warning("Qwen call failed; using verified tools: %s", type(e).__name__)
            yield ev("thought", text="Qwen 服務回應逾時或受限；已由可重現工具鏈接手，行程仍會完整產出。")
            yield from _offline(
                params,
                lang,
                engine="fallback-tools",
                runtime_note="Qwen 暫時不可用後自動接管；不使用模型杜撰，全部結論仍由工具核驗。",
            )
            return
        msg = resp.choices[0].message
        if msg.content:
            yield ev("thought", text=msg.content.strip())
        if not msg.tool_calls:
            messages.append({"role": "assistant", "content": msg.content or ""})
            messages.append({"role": "user", "content": "請繼續：依工作流程呼叫工具，或在完成後呼叫 submit_itinerary。"})
            continue
        messages.append({"role": "assistant", "content": msg.content or "",
                         "tool_calls": [{"id": tc.id, "type": "function",
                                         "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                                        for tc in msg.tool_calls]})
        for tc in msg.tool_calls:
            name = tc.function.name
            try:
                args = json.loads(tc.function.arguments or "{}")
            except Exception:
                args = {}
            if name == "submit_itinerary":
                proposed = [i for i in (args.get("ordered_poi_ids") or []) if kb.get(i)]
                missing = sorted(required_tools - called_tools)
                unchecked = [pid for pid in proposed if pid not in checked_ids]
                if missing or unchecked:
                    detail = {
                        "ok": False,
                        "reason": "required_verification_incomplete",
                        "missing_tools": missing,
                        "unchecked_poi_ids": unchecked,
                    }
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(detail, ensure_ascii=False),
                    })
                    yield ev(
                        "thought",
                        text="提交前核對未完成，會先補齊必要工具與每站開放驗證。",
                    )
                    continue
                final_ids = proposed
                title = args.get("title")
                summary = args.get("summary")
                for sr in args.get("stop_reasons") or []:
                    if sr.get("poi_id"):
                        why_map[sr["poi_id"]] = sr.get("reason")
                diversions = args.get("diversions") or []
                notes = args.get("notes") or []
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": "OK"})
                break
            yield ev("tool_call", name=name, args=args)
            res = T.run_tool(name, args)
            called_tools.add(name)
            if name == "check_opening" and args.get("poi_id"):
                checked_ids.add(args["poi_id"])
            yield ev("tool_result", name=name, summary=_summ(name, res), data=res)
            if name == "find_local_gem" and res.get("found"):
                yield ev("thought", text=f"發現寧靜替代點：{res['name']}，考慮導流。")
            messages.append({"role": "tool", "tool_call_id": tc.id,
                             "content": json.dumps(res, ensure_ascii=False)})
        if final_ids is not None:
            break

    if not final_ids:
        yield ev("thought", text="未取得最終結構化行程，改用離線規劃引擎完成。")
        yield from _offline(
            params, lang, engine="fallback-tools",
            runtime_note="Qwen 未在步數上限內提交結構化結果；由可重現工具鏈安全完成。",
        )
        return

    final_ids, safety_changes = _sanitize_qwen_ids(params, final_ids)
    if len(final_ids) < 3:
        yield ev("thought", text="模型行程經安全核對後不足 3 站，改用穩定規劃引擎重建。")
        yield from _offline(
            params, lang, engine="fallback-tools",
            runtime_note="Qwen 初稿未通過最少站點核對；由可重現工具鏈重建。",
        )
        return
    if safety_changes:
        notes.extend(safety_changes)
        yield ev("recovery", frm="模型初稿", to="安全核對後行程",
                 reason="；".join(safety_changes))

    yield ev("status", stage="assemble", text="整合行程、核對所有限制條件…")
    itinerary = assemble(params, final_ids, diversions, lang, why_map=why_map, notes=notes)
    itinerary["engine"] = "qwen:" + config.QWEN_MODEL
    if title:
        itinerary["title"] = title
    if summary:
        itinerary["summary"] = summary
    yield ev("result", itinerary=itinerary)
    yield ev("done")


# --------------------------------------------------------------------------
# public entry
# --------------------------------------------------------------------------
def run(text, language=None, today=None, mode="auto"):
    params = parse_request(text, override_lang=language, today=today)
    lang = params["language"]
    if mode == "fast":
        run_engine = "verified-tools"
    elif params.get("days", 1) > 1:
        run_engine = "verified-tools"
    elif config.USE_REAL_LLM:
        run_engine = "qwen:" + config.QWEN_MODEL
    else:
        run_engine = "verified-tools"
    yield ev("params", params={
        "language": lang, "language_name": LANG_NAME.get(lang, lang),
        "date": params["date"], "people": params["people"],
        "interests": params["interests"], "budget": params["budget"],
        "low_walk": params["low_walk"], "half_day": params["half_day"],
        "days": params.get("days", 1),
        "engine": run_engine,
    })
    try:
        if mode == "fast":
            voice_mode = {
                "zh-HK": "粵語（Cantonese）",
                "zh": "普通话（Mandarin）",
                "en": "English",
                "pt": "Português",
                "ja": "日本語",
            }.get(lang, lang)
            yield ev(
                "thought",
                text=(
                    "評審快速演示：使用與正式模式相同的知識庫、天氣、開放、人流、導流、"
                    "路線與預算工具，確保 90 秒內可完整核驗。阿濠講古為預存千問男聲："
                    f"qwen-audio-3.0-tts-plus / longanlufeng（龍安魯風）· {voice_mode}。"
                ),
            )
            yield from _offline(
                params,
                lang,
                engine="verified-tools",
                runtime_note=(
                    "評審快速演示；講古預存 qwen-audio-3.0-tts-plus · "
                    f"longanlufeng · {voice_mode}。Qwen 規劃保持在線，"
                    "自訂問題可切回真實推理。"
                ),
            )
            return
        if params.get("days", 1) > 1:
            yield ev(
                "thought",
                text=(
                    "多日模式：每日鎖定片區後，由同一套已核實工具（天氣/開放/人流/導流/路線/預算）"
                    "組裝可步行行程；避免跨日重複景點，並在最終合併總覽。"
                ),
            )
            yield from _offline_multi(params, lang, engine="verified-tools")
            return
        if config.USE_REAL_LLM:
            yield from _qwen(params, lang)
        else:
            yield from _offline(params, lang, engine="verified-tools")
    except Exception as e:
        yield ev("error", text=f"規劃過程發生錯誤：{type(e).__name__}: {e}")
