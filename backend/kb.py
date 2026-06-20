# -*- coding: utf-8 -*-
"""Knowledge base access for Macau POIs."""
import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_POIS_PATH = os.path.join(_HERE, "data", "pois.json")

with open(_POIS_PATH, encoding="utf-8") as f:
    POIS = json.load(f)

BY_ID = {p["id"]: p for p in POIS}

# Map free-text interests (zh/en) to POI categories/tags for searching.
INTEREST_MAP = {
    "歷史": ["heritage", "temple"], "文化": ["heritage", "temple", "museum"],
    "history": ["heritage", "temple"], "culture": ["heritage", "temple", "museum"],
    "建築": ["heritage"], "教堂": ["temple"], "廟": ["temple"], "宗教": ["temple"],
    "美食": ["food"], "食": ["food"], "小食": ["food"], "food": ["food"], "eat": ["food"],
    "甜品": ["food"], "dessert": ["food"],
    "老街": ["street"], "舊區": ["street"], "懷舊": ["street"], "本地": ["street", "food"],
    "street": ["street"], "local": ["street", "food"], "authentic": ["street"],
    "拍照": ["view", "street", "heritage"], "打卡": ["view", "street"],
    "photo": ["view", "street"], "風景": ["view", "garden"], "view": ["view"], "景觀": ["view"],
    "文青": ["street", "museum"], "文創": ["street"], "藝術": ["museum", "street"],
    "親子": ["garden", "view", "museum"], "family": ["garden", "view", "museum"],
    "公園": ["garden"], "自然": ["garden", "view"], "nature": ["garden", "view"],
    "購物": ["street"], "手信": ["street", "food"], "shopping": ["street"],
}


def all_pois():
    return POIS


def get(poi_id):
    return BY_ID.get(poi_id)


def search(interests=None, district=None, prefer_local=False, prefer_quiet=False,
           categories=None, limit=12):
    """Search the POI knowledge base by interests / district / preferences.
    Returns a scored, ranked list of POIs."""
    cats = set(categories or [])
    if interests:
        for it in interests:
            it = (it or "").strip().lower()
            for key, mapped in INTEREST_MAP.items():
                if key.lower() in it or it in key.lower():
                    cats.update(mapped)
    results = []
    for p in POIS:
        if district and p["district"] != district:
            continue
        score = 0.0
        if cats:
            if p["category"] in cats:
                score += 3.0
            else:
                continue  # when categories specified, restrict to them
        else:
            score += 1.0
        # tag overlap with interests
        if interests:
            for it in interests:
                for tag in p["tags"]:
                    if it and (it in tag or tag in it):
                        score += 1.0
        if p["unesco"]:
            score += 0.6
        if prefer_local and (p["old_district"] or p["local_business"]):
            score += 2.0
        if prefer_quiet:
            score += (1.0 - p["crowd_base"]) * 1.5
        results.append((score, p))
    results.sort(key=lambda x: (-x[0], x[1]["crowd_base"]))
    return [p for _, p in results[:limit]]


def find_local_alternative(crowded_poi_id):
    """Given a crowded hotspot, suggest a nearby quieter old-district / local gem.
    This is the core 'divert tourists to old districts' capability."""
    src = BY_ID.get(crowded_poi_id)
    if not src:
        return None
    from geo import haversine_m
    cands = []
    for p in POIS:
        if p["id"] == crowded_poi_id:
            continue
        if not (p["old_district"] or p["local_business"] or p["crowd_base"] < 0.45):
            continue
        d = haversine_m(src["lat"], src["lng"], p["lat"], p["lng"])
        if d > 1200:  # within ~1.2km walking
            continue
        # prefer closer + quieter + local
        score = (1.0 - p["crowd_base"]) * 2 + (2 if p["old_district"] else 0) - d / 1000.0
        cands.append((score, d, p))
    if not cands:
        return None
    cands.sort(key=lambda x: -x[0])
    score, dist, p = cands[0]
    return {"poi": p, "distance_m": round(dist)}
