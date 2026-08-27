# -*- coding: utf-8 -*-
"""QA cycle harness — backend correctness tests.

Runs the agent end-to-end (offline brain) over many scenarios and verifies
invariants: event protocol, itinerary structure, times, routes, opening
checks, budgets, multi-day coherence. Also validates the POI knowledge base.

Usage:  python qa/test_backend.py
Exit code 0 = all pass; prints a report with FAIL/WARN lines otherwise.
"""
import datetime as dt
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "backend"))

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import agent  # noqa: E402
import kb  # noqa: E402
import tools as T  # noqa: E402
from llm import parse_request  # noqa: E402

FAILS, WARNS, PASSES = [], [], []


def check(ok, label, detail=""):
    if ok:
        PASSES.append(label)
    else:
        FAILS.append(f"{label} — {detail}")


def warn(label, detail=""):
    WARNS.append(f"{label} — {detail}")


def hm_to_min(s):
    h, m = s.split(":")
    return int(h) * 60 + int(m)


# --------------------------------------------------------------------------
# 1. Knowledge base integrity
# --------------------------------------------------------------------------
def test_kb():
    pois = kb.all_pois()
    check(len(pois) >= 70, "KB: 至少 70 個 POI", f"實際 {len(pois)}")
    ids = [p["id"] for p in pois]
    check(len(ids) == len(set(ids)), "KB: id 唯一", "有重複 id")

    required = ["id", "name", "category", "district", "district_name", "zone",
                "lat", "lng", "open_min", "close_min", "closed_days", "visit_min",
                "cost_mop", "crowd_base", "hotspot", "unesco", "old_district",
                "local_business", "tags", "image", "blurb"]
    img_dir = os.path.join(ROOT, "frontend", "assets", "poi")
    missing_imgs = []
    for p in pois:
        for f in required:
            if f not in p:
                check(False, f"KB[{p.get('id','?')}]: 缺字段 {f}")
        for langk in ("zh", "en", "pt"):
            if not p["name"].get(langk):
                check(False, f"KB[{p['id']}]: name.{langk} 為空")
        # Macau bbox
        if not (22.06 <= p["lat"] <= 22.23 and 113.51 <= p["lng"] <= 113.61):
            check(False, f"KB[{p['id']}]: 坐標超出澳門範圍", f"{p['lat']},{p['lng']}")
        # district-coordinate coherence
        if p["district"] in ("central", "inner_harbour", "guia") and p["lat"] < 22.17:
            check(False, f"KB[{p['id']}]: 半島 POI 坐標落在離島", f"lat={p['lat']}")
        if p["district"] == "taipa" and not (22.13 <= p["lat"] <= 22.175):
            check(False, f"KB[{p['id']}]: 氹仔 POI 坐標異常", f"lat={p['lat']}")
        if p["district"] == "coloane" and p["lat"] > 22.145:
            check(False, f"KB[{p['id']}]: 路環 POI 坐標異常", f"lat={p['lat']}")
        if not (0 <= p["open_min"] < 1440 and 0 < p["close_min"] <= 1440 and p["open_min"] < p["close_min"]):
            check(False, f"KB[{p['id']}]: 開放時間異常", f"{p['open_min']}-{p['close_min']}")
        if any(d < 0 or d > 6 for d in p["closed_days"]):
            check(False, f"KB[{p['id']}]: closed_days 非法", str(p["closed_days"]))
        if p["visit_min"] < 10 or p["visit_min"] > 240:
            warn(f"KB[{p['id']}]: visit_min 可疑", str(p["visit_min"]))
        if not (0.0 <= p["crowd_base"] <= 1.0):
            check(False, f"KB[{p['id']}]: crowd_base 越界", str(p["crowd_base"]))
        img = p.get("image") or ""
        if img.startswith("assets/"):
            fp = os.path.join(ROOT, "frontend", img.replace("/", os.sep))
            if not os.path.isfile(fp):
                missing_imgs.append(f"{p['id']} -> {img}")
        elif not img:
            missing_imgs.append(f"{p['id']} -> (無圖)")
        if not p["blurb"].get("zh"):
            check(False, f"KB[{p['id']}]: blurb.zh 為空")
    check(not missing_imgs, "KB: 所有 POI 圖片存在", "; ".join(missing_imgs[:8]) + (f" 等共{len(missing_imgs)}個" if len(missing_imgs) > 8 else ""))
    old_cnt = sum(1 for p in pois if p["old_district"])
    loc_cnt = sum(1 for p in pois if p["local_business"])
    check(old_cnt >= 20, "KB: 舊區 POI ≥ 20", f"實際 {old_cnt}")
    check(loc_cnt >= 15, "KB: 本地小店 POI ≥ 15", f"實際 {loc_cnt}")


# --------------------------------------------------------------------------
# 2. parse_request
# --------------------------------------------------------------------------
def test_parse():
    base = dt.date(2026, 7, 6)  # Monday
    p = parse_request("我下星期三想帶爸媽嚟澳門玩一日", today=base)
    check(p["date"] == "2026-07-15", "解析：下星期三 → 下週三", p["date"])
    check(p["people"] == 3, "解析：帶爸媽 → 3 人", str(p["people"]))
    check(p["days"] == 1, "解析：玩一日 → 1 天", str(p["days"]))

    p = parse_request("幫我安排澳門三日兩夜，想玩半島世遺、氹仔美食同路環慢活", today=base)
    check(p["days"] == 3, "解析：三日兩夜 → 3 天", str(p["days"]))

    p = parse_request("兩日一夜輕鬆遊", today=base)
    check(p["days"] == 2, "解析：兩日一夜 → 2 天", str(p["days"]))

    p = parse_request("First time in Macau this weekend, 2 people, we love history", today=base)
    check(p["people"] == 2, "解析：2 people → 2 人", str(p["people"]))
    d = dt.date.fromisoformat(p["date"])
    check(d.weekday() == 5, "解析：weekend → 週六", p["date"])

    p = parse_request("預算300，少行路，途經福隆新街", today=base)
    check(p["budget"] == 300, "解析：預算300 無貨幣單位", str(p["budget"]))
    check(p["low_walk"], "解析：少行路 → low_walk", str(p["low_walk"]))
    check("rua_felicidade" in p["requested_ids"], "解析：途經福隆新街", str(p["requested_ids"]))

    p = parse_request("我想去鄭家大屋同附近嘅歷史老街，星期三去", today=base)
    check("mandarin_house" in p["requested_ids"], "解析：指名鄭家大屋", str(p["requested_ids"]))
    check(dt.date.fromisoformat(p["date"]).weekday() == 2, "解析：星期三", p["date"])

    p = parse_request("氹仔半日遊，主打地道美食", today=base)
    check(p["district"] == "taipa", "解析：氹仔 → taipa", str(p["district"]))
    check(p["half_day"], "解析：半日", str(p["half_day"]))

    p = parse_request("4日遊", today=base)
    check(p["days"] == 4, "解析：4日遊 → 4 天", str(p["days"]))

    p = parse_request("十日環遊澳門", today=base)
    check(p["days"] <= 5, "解析：天數上限 5", str(p["days"]))


# --------------------------------------------------------------------------
# 3. agent runs — invariants per scenario
# --------------------------------------------------------------------------
SCENARIOS = [
    ("我下星期三想帶爸媽嚟澳門玩一日，鍾意歷史文化同地道美食，預算唔想太貴，又唔想行太多路", None),
    ("幫我安排澳門三日兩夜，想玩半島世遺、氹仔美食同路環慢活", None),
    ("情侶星期六想行下舊區老街、影靚相，順便試下街頭小食", None),
    ("我想去鄭家大屋同附近嘅歷史老街，星期三去", None),
    ("氹仔半日遊，主打地道美食", None),
    ("First time in Macau this weekend, we love history, old streets and street food", "en"),
    ("週日一家四口親子遊，想去公園同博物館", None),
    ("路環一日慢活遊", None),
    ("兩日一夜，鍾意教堂同攝影", None),
    ("澳門五日深度遊", None),
    ("預算 300 蚊二人下午半日遊", None),
    ("退休長者遊澳門，行動不便，想輕鬆啲", None),
]


def run_agent(q, lang=None, today="2026-07-06"):
    events = []
    for e in agent.run(q, language=lang, today=today):
        events.append(e)
    return events


def verify_events(q, events):
    types = [e["type"] for e in events]
    check(types[0] == "params", f"[{q[:12]}…] 事件流以 params 開始", str(types[:2]))
    check("result" in types, f"[{q[:12]}…] 有 result 事件", str(set(types)))
    check(types[-1] == "done", f"[{q[:12]}…] 以 done 結束", str(types[-3:]))
    check("error" not in types, f"[{q[:12]}…] 無 error 事件",
          next((e.get("text", "") for e in events if e["type"] == "error"), ""))
    for e in events:
        try:
            json.dumps(e, ensure_ascii=False)
        except Exception as ex:
            check(False, f"[{q[:12]}…] 事件不可 JSON 序列化", f"{e.get('type')}: {ex}")
    return next((e["itinerary"] for e in events if e["type"] == "result"), None)


def verify_day(q, day, params_date=None):
    stops = day["stops"]
    check(len(stops) >= 3, f"[{q[:12]}…] 每日至少 3 站", f"實際 {len(stops)}")
    ids = [s["poi_id"] for s in stops]
    check(len(ids) == len(set(ids)), f"[{q[:12]}…] 單日無重複景點", str(ids))
    date = day["date"]
    # every stop open that day
    for s in stops:
        op = T.check_opening(poi_id=s["poi_id"], date=date, time=s["arrive"])
        p = kb.get(s["poi_id"])
        check(op["open"], f"[{q[:12]}…] {s['name']['zh']} 到達時開放", op.get("reason", ""))
        check(hm_to_min(s["depart"]) <= p["close_min"],
              f"[{q[:12]}…] {s['name']['zh']} 離開前未關門",
              f"{s['depart']} vs close {p['close_min']}")
    # times strictly sequential
    last_depart = None
    for s in stops:
        a, d = hm_to_min(s["arrive"]), hm_to_min(s["depart"])
        check(d > a, f"[{q[:12]}…] {s['name']['zh']} 離開晚於到達", f"{s['arrive']}→{s['depart']}")
        if last_depart is not None:
            check(a >= last_depart, f"[{q[:12]}…] {s['name']['zh']} 到達時間順序正確",
                  f"上一站離開 {last_depart} vs 到達 {a}")
        last_depart = d
    # single walkable district-cluster per day
    districts = {kb.get(s["poi_id"])["district"] for s in stops}
    island = {"taipa", "coloane"}
    if districts & island and districts - island:
        check(False, f"[{q[:12]}…] 單日跨島", str(districts))
    check(not (("taipa" in districts) and ("coloane" in districts)), f"[{q[:12]}…] 氹仔路環不同日", str(districts))
    # end time sane (finish before midnight)
    end = hm_to_min(stops[-1]["depart"])
    check(end <= 23 * 60, f"[{q[:12]}…] 行程在 23:00 前完結", stops[-1]["depart"])


def test_agent_scenarios():
    for q, lang in SCENARIOS:
        events = run_agent(q, lang)
        it = verify_events(q, events)
        if not it:
            continue
        params = next(e["params"] for e in events if e["type"] == "params")
        if it.get("days"):
            check(len(it["days"]) == params["days"],
                  f"[{q[:12]}…] 天數符合解析（{params['days']}）", f"實際 {len(it['days'])}")
            dates = [d["date"] for d in it["days"]]
            expect = [(dt.date.fromisoformat(it["days"][0]["date"]) + dt.timedelta(days=i)).isoformat()
                      for i in range(len(dates))]
            check(dates == expect, f"[{q[:12]}…] 多日日期連續", str(dates))
            all_ids = [s["poi_id"] for d in it["days"] for s in d["stops"]]
            dup = [i for i in set(all_ids) if all_ids.count(i) > 1]
            check(not dup, f"[{q[:12]}…] 多日之間無重複景點", str(dup))
            for d in it["days"]:
                verify_day(q, d)
        else:
            verify_day(q, it)
        # constraints panel exists and all verifiable
        check(len(it.get("constraints", [])) >= 3, f"[{q[:12]}…] 核對面板 ≥ 3 項", str(len(it.get("constraints", []))))
        bad = [c["label"] for c in it["constraints"] if not c["ok"]]
        if bad:
            warn(f"[{q[:12]}…] 有未通過的核對項", str(bad))
        # totals consistency
        tot = it["totals"]
        stops_all = it["stops"]
        check(tot["stops"] == len(stops_all), f"[{q[:12]}…] totals.stops 一致", f"{tot['stops']} vs {len(stops_all)}")
        cost = sum(s["cost_mop"] for s in stops_all)
        check(tot["cost_mop"] == cost, f"[{q[:12]}…] totals.cost 一致", f"{tot['cost_mop']} vs {cost}")
        local_spend = sum(s["cost_mop"] for s in stops_all if s["local_business"])
        check(tot["local_spend_mop"] == local_spend,
              f"[{q[:12]}…] totals.local_spend 一致",
              f"{tot.get('local_spend_mop')} vs {local_spend}")


# --------------------------------------------------------------------------
# 4. targeted behaviours
# --------------------------------------------------------------------------
def test_behaviours():
    # 4.1 failure recovery: mandarin_house closed on Wednesday
    events = run_agent("我想去鄭家大屋同附近嘅歷史老街，星期三去", today="2026-07-06")
    recov = [e for e in events if e["type"] == "recovery"]
    check(any("鄭家大屋" in (e.get("frm") or "") for e in recov),
          "行為：週三鄭家大屋觸發失敗恢復", str([(e.get('frm'), e.get('to')) for e in recov]))
    it = next(e["itinerary"] for e in events if e["type"] == "result")
    check(all(s["poi_id"] != "mandarin_house" for s in it["stops"]),
          "行為：休息景點不入行程", "")

    # 4.2 non-Wednesday keeps mandarin house when requested
    events = run_agent("我想去鄭家大屋同附近嘅歷史老街，星期四去", today="2026-07-06")
    it = next(e["itinerary"] for e in events if e["type"] == "result")
    check(any(s["poi_id"] == "mandarin_house" for s in it["stops"]),
          "行為：週四鄭家大屋正常納入", str([s["poi_id"] for s in it["stops"]]))

    # 4.3 budget recovery
    events = run_agent("兩個人去澳門玩一日，預算 100 蚊，想去博物館同埋大三巴", today="2026-07-06")
    it = next(e["itinerary"] for e in events if e["type"] == "result")
    bc = [c for c in it["constraints"] if "預算" in c["label"]]
    if bc:
        check(bc[0]["ok"], "行為：預算約束最終滿足", bc[0]["detail"])

    # 4.4 diversion fires for crowded anchor
    events = run_agent("週六想去大三巴", today="2026-07-06")
    it = next(e["itinerary"] for e in events if e["type"] == "result")
    check(len(it.get("diversions", [])) >= 1, "行為：熱點導流有觸發", str(it.get("diversions")))

    # 4.5 low-walk cap
    events = run_agent("老人家想輕鬆行下舊區", today="2026-07-06")
    it = next(e["itinerary"] for e in events if e["type"] == "result")
    check(it["totals"]["walk_km"] <= 3.6, "行為：低步行 ≤ 3.6km", str(it["totals"]["walk_km"]))

    # 4.6 empty / weird input does not crash
    for weird in ["", "asdfghjkl", "🦀🦀🦀", "     ", "我要去香港迪士尼", "'; DROP TABLE pois;--",
                  "<script>alert(1)</script> 帶我玩", "一百人一齊去", "0 蚊預算"]:
        events = run_agent(weird)
        types = [e["type"] for e in events]
        check("error" not in types and "result" in types,
              f"健壯：異常輸入不崩潰 [{weird[:10]!r}]", str(types[-2:]))

    # 4.7 tools defensive
    check(not T.check_opening(poi_id="nope")["open"], "工具：check_opening 未知 id 安全", "")
    r = T.compute_route(poi_ids=[])
    check(r.get("legs") == [], "工具：compute_route 空列表安全", str(r))
    from geo import pedestrian_leg, haversine_m
    a, b = kb.get("senado_square"), kb.get("ruins_st_paul")
    check(bool(a and b), "KB：議事亭與大三巴存在", "")
    if a and b:
        leg = pedestrian_leg(a, b)
        check(leg["walk_min"] >= 1, "geo：巷道步行分鐘", str(leg))
        check(leg["meters"] >= haversine_m(a["lat"], a["lng"], b["lat"], b["lng"]) * 0.99,
              "geo：巷道距離不短於直線", str(leg))
    r2 = T.compute_route(poi_ids=["senado_square", "rua_felicidade", "ruins_st_paul"], optimize=False)
    method = r2.get("method") or ""
    check("lane" in method or "anchor" in method or "osm" in method,
          "工具：compute_route 巷道方法", method)
    check(all("via" in lg for lg in r2.get("legs") or []), "工具：legs 含 via", str(r2.get("legs")))
    b = T.estimate_budget(poi_ids=["ruins_st_paul"], people=0)
    check(b["people"] == 1, "工具：estimate_budget 人數下限 1", str(b["people"]))
    c = T.predict_crowd(poi_id="ruins_st_paul", datetime="garbage")
    check("crowd_level" in c, "工具：predict_crowd 垃圾時間安全", "")


def main():
    test_kb()
    test_parse()
    test_agent_scenarios()
    test_behaviours()
    print("=" * 60)
    print(f"PASS {len(PASSES)}  FAIL {len(FAILS)}  WARN {len(WARNS)}")
    for f in FAILS:
        print("FAIL:", f)
    for w in WARNS:
        print("WARN:", w)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
