# -*- coding: utf-8 -*-
"""Knowledge base access for Macau POIs."""
import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_POIS_PATH = os.path.join(_HERE, "data", "pois.json")

with open(_POIS_PATH, encoding="utf-8") as f:
    POIS = json.load(f)

_STORIES_PATH = os.path.join(_HERE, "data", "stories.json")
with open(_STORIES_PATH, encoding="utf-8") as f:
    STORIES = json.load(f)

for _p in POIS:
    _st = STORIES.get(_p["id"])
    if _st:
        _p["story"] = _st
        _p["story_zh"] = _st.get("zh-HK") or _p.get("story_zh")

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


# --------------------------------------------------------------------------
# Accessibility knowledge (計劃書晉級後第 1 階段：加入無障礙資料)
# Default: Macau old-town lanes and squares are broadly step-free; the map
# below overrides hillside forts, stair-heavy landmarks and beach paths.
# --------------------------------------------------------------------------
_ACCESS_OVERRIDES = {
    "ruins_st_paul": (False, "正面為 68 級石階，輪椅可經高園街斜道到牌坊平台", "68 stone steps at the front; wheelchair users can reach the platform via the ramp on Calçada de S. Paulo"),
    "monte_fort": (False, "上山斜路與梯級，可乘澳門博物館電梯再步行", "Uphill slopes and stairs; take the Macau Museum lift first"),
    "old_city_walls": (False, "遺址周邊有梯級與斜路", "Steps and slopes around the ruins"),
    "na_tcha_temple": (False, "位於大三巴側，需行少量石階", "A few stone steps beside the Ruins"),
    "guia_fortress": (False, "山上炮台，建議先乘松山纜車再沿斜道步行", "Hilltop fortress; take the Guia Cable Car, then a sloped path"),
    "penha_church": (False, "西望洋山長斜路，輪椅上山較吃力", "A long uphill slope to Penha Hill"),
    "mandarin_house": (False, "大宅內有門檻與梯級，部分展區輪椅未能到達", "Thresholds and internal stairs; some rooms are not wheelchair-reachable"),
    "moorish_barracks": (False, "沿萬里長城斜路而上", "Reached via a sloped street"),
    "st_lawrence": (False, "教堂正門有石階", "Stone steps at the main entrance"),
    "st_augustine": (False, "位於崗頂前地，需經斜巷上崗頂", "On Largo de Sto. Agostinho, up a sloped lane"),
    "dom_pedro_theatre": (False, "崗頂斜巷上落，門前有梯級", "Sloped lane and entrance steps"),
    "ho_tung_library": (False, "經崗頂斜巷前往，園內有梯級", "Sloped approach and garden steps"),
    "camoes_garden": (False, "園內有山丘斜路與梯級", "Hilly paths and steps inside the garden"),
    "a_ma_temple": (False, "廟內依山而建，殿與殿之間有石級", "Built on a hillside; stone steps between halls"),
    "carmel_church": (False, "位於氹仔小山丘，需行斜路", "On a small Taipa hill, sloped approach"),
    "pou_tai_temple": (False, "寺內有梯級平台", "Stepped terraces inside the temple"),
    "lai_chi_vun": (False, "船廠片區地面不平，部分為碎石路", "Uneven shipyard ground, some gravel paths"),
    "cheoc_van_beach": (False, "沙灘路段輪椅較難通行", "Sand sections are hard for wheelchairs"),
    "hac_sa_beach": (False, "沙灘路段輪椅較難通行", "Sand sections are hard for wheelchairs"),
    "macau_museum": (True, "設有電梯與無障礙通道", "Lifts and accessible routes available"),
    "science_center": (True, "全館電梯與無障礙通道", "Fully accessible with lifts"),
    "macau_tower": (True, "電梯直達觀光層，無障礙友善", "Lifts to the observation decks"),
    "red_market": (True, "街市已設升降機", "Market equipped with a lift"),
    "travessa_paixao": (True, "短斜巷，輪椅可在巷口平台拍照", "A short sloped lane; photo spot at the flat end"),
    "lilau_square": (True, "前地平緩，周邊為緩斜路", "Gentle square with mild slopes around"),
}
_ACCESS_DEFAULT = (True, "路面大致平坦，輪椅/嬰兒車可通行", "Mostly flat and stroller/wheelchair friendly")


def accessibility(poi_id):
    """Step-free flag + bilingual note for a POI (all 70 POIs annotated)."""
    step_free, note_zh, note_en = _ACCESS_OVERRIDES.get(poi_id, _ACCESS_DEFAULT)
    return {"step_free": step_free, "note_zh": note_zh, "note_en": note_en}


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
