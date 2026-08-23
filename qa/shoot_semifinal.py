# -*- coding: utf-8 -*-
"""複賽說明文檔配圖：對公網站點截真實截圖。

用法:  python qa/shoot_semifinal.py [BASE_URL]
輸出:  docs/assets/semifinal/*.png
"""
import pathlib
import sys
import time

from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://47.79.228.128"
OUT = pathlib.Path(__file__).resolve().parents[1] / "docs" / "assets" / "semifinal"
OUT.mkdir(parents=True, exist_ok=True)

VIEWPORT = {"width": 1440, "height": 900}


def shot(page, name):
    path = OUT / name
    page.screenshot(path=str(path))
    print("saved", path.name)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport=VIEWPORT)

        # ---- 1) dashboard: KPI + proposal targets --------------------------
        page.goto(f"{BASE}/dashboard.html", wait_until="networkidle")
        page.wait_for_selector(".kpi", timeout=15_000)
        page.wait_for_timeout(600)
        shot(page, "01_dashboard_kpi.png")

        # targets table + usability
        page.locator("#targets").scroll_into_view_if_needed()
        page.wait_for_timeout(400)
        shot(page, "02_dashboard_targets.png")

        # heat + calibration charts
        page.locator("#heat").scroll_into_view_if_needed()
        page.wait_for_timeout(400)
        shot(page, "03_dashboard_heat.png")

        # merchant cards + redeem machine demo (issue → redeem on live API)
        page.locator("#merchants").scroll_into_view_if_needed()
        page.wait_for_timeout(400)
        page.click("#issueBtn")
        page.wait_for_selector("#issuedCode:not(.hidden)", timeout=10_000)
        code = page.locator("#issuedCode").inner_text().replace("🎟️", "").strip()
        page.fill("#redeemInput", code)
        page.click("#redeemBtn")
        page.wait_for_selector(".redeem-result.ok", timeout=10_000)
        page.locator("#redeemBox").scroll_into_view_if_needed()
        page.wait_for_timeout(300)
        shot(page, "04_dashboard_redeem.png")

        # ---- 2) main page: real plan on live Qwen --------------------------
        page.goto(f"{BASE}/", wait_until="networkidle")
        page.fill("#prompt", "帶爸媽半日遊，想睇歷史建築同食地道小食，唔想行斜路")
        page.click("#planBtn")
        page.wait_for_selector(".tl-stop", timeout=180_000)
        page.wait_for_timeout(1200)

        # claim a visit code inside the itinerary if available
        if page.locator(".code-btn").count():
            page.locator(".code-btn").first.scroll_into_view_if_needed()
            page.locator(".code-btn").first.click()
            try:
                page.wait_for_selector("#result .code-chip", timeout=10_000)
            except Exception:
                pass
            page.wait_for_timeout(400)
            shot(page, "05_itinerary_access_code.png")
        else:
            page.locator(".tl-stop").first.scroll_into_view_if_needed()
            page.wait_for_timeout(400)
            shot(page, "05_itinerary_access_code.png")

        # weather chip / header of result
        page.locator("#result").scroll_into_view_if_needed()
        page.wait_for_timeout(300)
        shot(page, "06_itinerary_header.png")

        browser.close()
    print("ALL_SHOTS_DONE")


if __name__ == "__main__":
    main()
