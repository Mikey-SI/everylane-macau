"""End-to-end MCP protocol test for the QwenPaw EveryLane bridge."""
from __future__ import annotations

import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVER = os.path.join(ROOT, "qwenpaw", "mcp_server.py")
EXPECTED = {
    "search_attractions",
    "get_weather",
    "check_opening",
    "predict_crowd",
    "find_local_gem",
    "compute_route",
    "estimate_budget",
    "plan_macau_trip",
}


def structured(result):
    if result.structuredContent is not None:
        return result.structuredContent
    if not result.content:
        return {}
    return json.loads(result.content[0].text)


async def main():
    params = StdioServerParameters(command=sys.executable, args=[SERVER])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            listing = await session.list_tools()
            names = {tool.name for tool in listing.tools}
            assert names == EXPECTED, f"tool mismatch: {names ^ EXPECTED}"

            opened = structured(
                await session.call_tool(
                    "check_opening",
                    {"poi_id": "mandarin_house", "date": "2026-07-15"},
                )
            )
            assert opened["open"] is False
            assert "週三" in opened["reason"]

            route = structured(
                await session.call_tool(
                    "compute_route",
                    {
                        "poi_ids": [
                            "ruins_st_paul",
                            "rua_estalagens",
                            "rua_felicidade",
                        ],
                        "optimize": True,
                    },
                )
            )
            assert len(route["ordered_ids"]) == 3
            assert route["total_km"] > 0

            planned = structured(
                await session.call_tool(
                    "plan_macau_trip",
                    {
                        "request": "我想去鄭家大屋同附近嘅歷史老街，星期三去",
                        "language": "zh-HK",
                        "today": "2026-07-11",
                    },
                )
            )
            assert planned["ok"] is True
            assert planned["poi_count"] == 70
            stops = planned["itinerary"]["stops"]
            assert all(stop["poi_id"] != "mandarin_house" for stop in stops)

    print("QwenPaw MCP PASS: 8 tools, protocol, failure recovery, route, planner")


if __name__ == "__main__":
    asyncio.run(main())
