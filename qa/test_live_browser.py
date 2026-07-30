# -*- coding: utf-8 -*-
"""Focused browser + API regression after nginx SSE fix."""
from __future__ import annotations

import json
import urllib.parse
import urllib.request

from playwright.sync_api import sync_playwright

BASE = "http://47.79.228.128"
passed = 0
failures = []


def check(ok, label, detail=""):
    global passed
    if ok:
        passed += 1
        print("PASS", label)
    else:
        failures.append(f"{label}: {detail}")
        print("FAIL", label, detail)


def main():
    # compressed image size
    with urllib.request.urlopen(BASE + "/assets/poi/ruins_st_paul.jpg", timeout=30) as r:
        n = len(r.read())
    check(n < 900_000, "ruins image compressed", f"{n} bytes")

    # quick SSE first event latency
    q = urllib.parse.quote("氹仔半日遊，主打地道美食")
    req = urllib.request.Request(BASE + f"/api/plan?q={q}&lang=zh-HK", headers={"Accept": "text/event-stream"})
    with urllib.request.urlopen(req, timeout=240) as resp:
        got_tool = got_result = False
        buf = b""
        while True:
            chunk = resp.read(256)
            if not chunk:
                break
            buf += chunk
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                s = line.decode("utf-8", "replace").strip()
                if not s.startswith("data:"):
                    continue
                ev = json.loads(s[5:].strip())
                if ev.get("type") == "tool_call":
                    got_tool = True
                if ev.get("type") == "result":
                    got_result = True
                    it = ev["itinerary"]
                    check(len(it.get("stops") or []) >= 3, "api plan stops")
                    print(" title", it.get("title"))
                if ev.get("type") in ("done", "error"):
                    check(ev.get("type") == "done", "api plan done", str(ev))
                    break
    check(got_tool and got_result, "api streamed tools+result")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        page.goto(BASE + "/", wait_until="networkidle", timeout=60000)
        badge = page.locator("#engineBadge").inner_text()
        check("Qwen" in badge, "live badge", badge)
        page.select_option("#lang", "zh-HK")
        page.fill("#prompt", "情侶星期六想行下舊區老街、影靚相，順便試下街頭小食")
        page.click("#planBtn")
        page.wait_for_selector("#result:not(.hidden) .r-banner", timeout=300000)
        check(page.locator(".tl-stop").count() >= 3, "desktop timeline")
        check(page.locator("#map").count() == 1, "desktop map")
        check(page.locator("#trace .tr").count() >= 3, "desktop trace")
        # print mode class
        page.evaluate("document.body.classList.add('print-result')")
        page.emulate_media(media="print")
        check(page.locator("#result").evaluate("(e)=>getComputedStyle(e).display!=='none'"), "print keeps result")
        check(page.locator(".hero").evaluate("(e)=>getComputedStyle(e).display==='none'"), "print hides hero")
        page.emulate_media(media="screen")
        page.evaluate("document.body.classList.remove('print-result')")

        mobile = browser.new_page(viewport={"width": 390, "height": 844})
        mobile.goto(BASE + "/", wait_until="domcontentloaded", timeout=60000)
        overflow = mobile.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")
        check(overflow <= 2, "mobile home overflow", str(overflow))
        mobile.fill("#prompt", "First time in Macau this weekend, history and street food")
        mobile.select_option("#lang", "en")
        mobile.click("#planBtn")
        mobile.wait_for_selector("#result:not(.hidden) .r-banner", timeout=300000)
        overflow2 = mobile.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")
        check(overflow2 <= 2, "mobile result overflow", str(overflow2))
        check(mobile.locator(".tl-stop").count() >= 3, "mobile stops")
        check(not errs, "no pageerrors", " | ".join(errs[:5]))
        browser.close()

    print("=" * 50)
    print(f"PASS {passed} FAIL {len(failures)}")
    for f in failures:
        print("FAIL:", f)
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
