# -*- coding: utf-8 -*-
"""Geo helpers: great-circle distance and a nearest-neighbour route order."""
import math

WALK_SPEED_M_PER_MIN = 72.0  # ~4.3 km/h, realistic for sightseeing on foot in old town


def haversine_m(lat1, lng1, lat2, lng2):
    """Great-circle distance in metres."""
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def walk_minutes(dist_m):
    """Walking minutes for a great-circle distance (legacy helper).
    Prefer pedestrian_leg() when both endpoints are known so we can fold
    in old-town lane anchors instead of a flat 25% fudge factor."""
    eff = dist_m * 1.25
    return max(1, round(eff / WALK_SPEED_M_PER_MIN))


# Named pedestrian anchors on Macau's walkable spines. These are NOT an OSM
# router: they keep routes on historically walkable corridors (Senado, Rua da
# Felicidade, Taipa/Coloane village squares) instead of cutting through blocks.
_LANE_ANCHORS = (
    ("senado", "議事亭前地", 22.19354, 113.54021),
    ("stpaul", "大三巴前地", 22.19747, 113.54075),
    ("felicidade", "福隆新街", 22.19240, 113.53955),
    ("lilau", "亞婆井前地", 22.19095, 113.53685),
    ("ama", "媽閣廟前地", 22.18615, 113.53140),
    ("inner", "十月初五街", 22.19690, 113.53680),
    ("camoes", "白鴿巢前地", 22.20031, 113.53989),
    ("taipa", "氹仔官也街", 22.15420, 113.55980),
    ("coloane", "路環市區前地", 22.11655, 113.55095),
)


def _basin(lat):
    if lat < 22.135:
        return "coloane"
    if lat < 22.175:
        return "taipa"
    return "peninsula"


def pedestrian_leg(a, b):
    """Walk a→b via old-town lane anchors when they sit on the way.

    Honest about what it is: a corridor graph over a handful of named squares
    and streets, not turn-by-turn OSM. Distances stay in a 1.10–1.42× band
    around the great-circle so schedules remain comparable to the previous
    1.25× factor.
    """
    lat1, lng1 = float(a["lat"]), float(a["lng"])
    lat2, lng2 = float(b["lat"]), float(b["lng"])
    direct = haversine_m(lat1, lng1, lat2, lng2)
    if direct < 120:
        meters = direct * 1.12
        return {
            "meters": int(round(meters)),
            "walk_min": max(1, round(meters / WALK_SPEED_M_PER_MIN)),
            "via": [],
            "method": "short_lane",
        }

    basin_a, basin_b = _basin(lat1), _basin(lat2)
    via = []
    if basin_a != basin_b:
        meters = direct * 1.25
        method = "cross_island_factor"
    else:
        best = None
        for _id, name, alat, alng in _LANE_ANCHORS:
            if _basin(alat) != basin_a:
                continue
            d1 = haversine_m(lat1, lng1, alat, alng)
            d2 = haversine_m(alat, alng, lat2, lng2)
            extra = d1 + d2 - direct
            if d1 < 70 or d2 < 70:
                continue
            if extra < 40 or extra > direct * 0.42:
                continue
            if best is None or extra < best[0]:
                best = (extra, name, alat, alng, d1 + d2)
        if best:
            via = [{"name": best[1], "lat": best[2], "lng": best[3]}]
            meters = best[4]
            method = "old_town_lane_anchors"
        else:
            lat_m = 111320.0
            lng_m = 111320.0 * math.cos(math.radians((lat1 + lat2) / 2.0))
            l1 = abs(lng1 - lng2) * lng_m + abs(lat1 - lat2) * lat_m
            meters = 0.58 * l1 + 0.42 * direct
            method = "street_grid_blend"
        meters = min(max(meters, direct * 1.10), direct * 1.42)

    return {
        "meters": int(round(meters)),
        "walk_min": max(1, round(meters / WALK_SPEED_M_PER_MIN)),
        "via": via,
        "method": method,
    }


def order_by_nearest(points, start_index=0):
    """Greedy nearest-neighbour ordering to reduce backtracking.
    `points` = list of dicts with lat/lng. Returns ordered list of indices."""
    n = len(points)
    if n <= 2:
        return list(range(n))
    unvisited = set(range(n))
    order = [start_index]
    unvisited.discard(start_index)
    cur = start_index
    while unvisited:
        nxt = min(
            unvisited,
            key=lambda j: haversine_m(
                points[cur]["lat"], points[cur]["lng"], points[j]["lat"], points[j]["lng"]
            ),
        )
        order.append(nxt)
        unvisited.discard(nxt)
        cur = nxt
    return order
