# -*- coding: utf-8 -*-
"""Generate polished screenshots for the Word/PDF deliverables.

The images are embedded by the document generators, so the Word files have
clean, consistent visuals instead of raw browser screenshots.
"""
import os
import time
from playwright.sync_api import sync_playwright


HERE = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(HERE, "assets")
os.makedirs(ASSET_DIR, exist_ok=True)

BASE = "http://127.0.0.1:8000/"
QUERY = "我想去鄭家大屋同附近嘅歷史老街，星期三去，順便食地道嘢"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": 1440, "height": 1040},
            device_scale_factor=2,
        )
        page.goto(BASE, wait_until="networkidle")
        time.sleep(1.0)

        # Clean product hero screenshot.
        page.locator(".hero").screenshot(
            path=os.path.join(ASSET_DIR, "product_hero.png")
        )

        # Run a scenario that demonstrates both opening-hour recovery and
        # crowd diversion, then capture the polished result area.
        page.fill("#prompt", QUERY)
        page.click("#planBtn")
        page.wait_for_selector("#result .r-banner", timeout=25000)
        time.sleep(3.0)
        page.locator("#workspace").screenshot(
            path=os.path.join(ASSET_DIR, "agent_result.png")
        )

        # A compact map/timeline crop works well in A4 pages.
        page.locator("#map").screenshot(
            path=os.path.join(ASSET_DIR, "route_map.png")
        )
        page.locator(".trace-col").screenshot(
            path=os.path.join(ASSET_DIR, "agent_trace.png")
        )
        browser.close()

    print("Document assets written to:", ASSET_DIR)


if __name__ == "__main__":
    main()
