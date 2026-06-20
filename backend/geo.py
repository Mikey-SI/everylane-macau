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
    """Walking minutes for a distance, with a small intersection/buffer factor.
    Old-town lanes are winding, so we add a 25% detour factor over straight line."""
    eff = dist_m * 1.25
    return max(1, round(eff / WALK_SPEED_M_PER_MIN))


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
