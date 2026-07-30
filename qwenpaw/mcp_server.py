"""QwenPaw MCP bridge for EveryLane Macau.

Run this module as a stdio MCP server.  QwenPaw can then call the same seven
verified tools used by the website instead of relying on prompt-only claims.
No API key is read or transmitted by this bridge.
"""
from __future__ import annotations

import os
import sys
from typing import Any

from mcp.server.fastmcp import FastMCP

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND = os.path.join(ROOT, "backend")
if BACKEND not in sys.path:
    sys.path.insert(0, BACKEND)

import agent  # noqa: E402
import kb  # noqa: E402
import tools as travel_tools  # noqa: E402

mcp = FastMCP(
    "EveryLane Macau",
    instructions=(
        "Macau deep-travel tools backed by a curated 70-POI knowledge base. "
        "Use them to verify weather, opening hours, crowds, diversions, routes "
        "and budgets before presenting an itinerary."
    ),
)


@mcp.tool()
def search_attractions(
    interests: list[str] | None = None,
    district: str | None = None,
    prefer_local: bool = True,
    prefer_quiet: bool = False,
    limit: int = 12,
) -> dict[str, Any]:
    """Search verified Macau POIs by interests and district."""
    return travel_tools.search_attractions(
        interests=interests,
        district=district,
        prefer_local=prefer_local,
        prefer_quiet=prefer_quiet,
        limit=max(1, min(limit, 30)),
    )


@mcp.tool()
def get_weather(date: str) -> dict[str, Any]:
    """Get a deterministic Macau forecast for a YYYY-MM-DD date."""
    return travel_tools.get_weather(date=date)


@mcp.tool()
def check_opening(
    poi_id: str,
    date: str,
    time: str | None = None,
) -> dict[str, Any]:
    """Verify whether a POI is open on a date and optional HH:MM time."""
    return travel_tools.check_opening(poi_id=poi_id, date=date, time=time)


@mcp.tool()
def predict_crowd(poi_id: str, datetime: str) -> dict[str, Any]:
    """Predict crowd level for a POI at YYYY-MM-DD HH:MM."""
    return travel_tools.predict_crowd(poi_id=poi_id, datetime=datetime)


@mcp.tool()
def find_local_gem(near_poi_id: str) -> dict[str, Any]:
    """Find a quieter nearby old lane or local shop for crowd diversion."""
    return travel_tools.find_local_gem(near_poi_id=near_poi_id)


@mcp.tool()
def compute_route(
    poi_ids: list[str],
    optimize: bool = True,
    start_id: str | None = None,
) -> dict[str, Any]:
    """Compute a walkable order, legs, distance and walking time."""
    return travel_tools.compute_route(
        poi_ids=poi_ids,
        optimize=optimize,
        start_id=start_id,
    )


@mcp.tool()
def estimate_budget(
    poi_ids: list[str],
    people: int = 1,
) -> dict[str, Any]:
    """Estimate total entry and food cost in MOP for the party."""
    return travel_tools.estimate_budget(poi_ids=poi_ids, people=people)


@mcp.tool()
def plan_macau_trip(
    request: str,
    language: str = "zh-HK",
    today: str | None = None,
) -> dict[str, Any]:
    """Run the complete EveryLane agent and return its trace and itinerary.

    This orchestration tool is useful for comparison tests. For a visible
    QwenPaw ReAct demonstration, prefer calling the seven granular tools.
    """
    events = list(agent.run(request, language=language, today=today))
    itinerary = next(
        (event["itinerary"] for event in events if event["type"] == "result"),
        None,
    )
    trace = [
        {
            key: value
            for key, value in event.items()
            if key in {"type", "stage", "name", "args", "summary", "text", "reason"}
        }
        for event in events
        if event["type"] != "result"
    ]
    return {
        "ok": itinerary is not None,
        "engine": "EveryLane ReAct",
        "poi_count": len(kb.all_pois()),
        "trace": trace,
        "itinerary": itinerary,
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
