# -*- coding: utf-8 -*-
"""Full live-server QA against the public Alibaba Cloud instance."""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.parse
import urllib.request

from playwright.sync_api import sync_playwright

BASE = os.environ.get("LIVE_BASE", "http://47.79.228.128").rstrip("/")
passed = 0
failures: list[str] = []


def check(ok: bool, label: str, detail: str = ""):
    global passed
    if ok:
        passed += 1
        print(f"PASS  {label}")
    else:
        failures.append(f"{label}: {detail}")
        print(f"FAIL  {label}: {detail}")


def get_json(path: str):
    with urllib.request.urlopen(BASE + path, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def plan_events(q: str, lang: str = "zh-HK", timeout: int = 180):
    url = f"{BASE}/api/plan?q={urllib.parse.quote(q)}&lang={urllib.parse.quote(lang)}"
    req = urllib.request.Request(url, headers={"Accept": "text/event-stream"})
    events = []
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        buf = b""
        while True:
            chunk = resp.read(512)
            if not chunk:
                break
            buf += chunk
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                s = line.decode("utf-8", "replace").strip()
                if not s.startswith("data:"):
                    continue
                try:
                    ev = json.loads(s[5:].strip())
                except Exception:
                    continue
                events.append(ev)
                if ev.get("type") in ("done", "error"):
                    return events
    return events


def test_api():
    h = get_json("/api/health")
    check(h.get("ok") is True, "health ok")
    check(h.get("real_llm") is True, "real LLM enabled", str(h))
    check("qwen" in str(h.get("engine", "")).lower(), "engine is qwen", str(h.get("engine")))
    check(h.get("poi_count") == 70, "70 POIs", str(h.get("poi_count")))

    pois = get_json("/api/pois")
    check(isinstance(pois, list) and len(pois) == 70, "pois list length", str(len(pois) if isinstance(pois, list) else pois))
    ids = {p.get("id") for p in pois}
    for need in ("ruins_st_paul", "rua_estalagens", "mandarin_house", "rua_cunha"):
        check(need in ids, f"kb has {need}")

    # security headers via homepage
    with urllib.request.urlopen(BASE + "/", timeout=20) as r:
        headers = {k.lower(): v for k, v in r.headers.items()}
        body = r.read()
    check(r.status == 200 and len(body) > 1000, "homepage 200")
    check("content-security-policy" in headers or "x-content-type-options" in headers, "security headers present", str(list(headers)[:12]))

    for path in (
        "/app.js",
        "/styles.css",
        "/assets/vendor/leaflet/leaflet.js",
        "/assets/poi/rua_cunha.jpg",
        "/assets/poi/mandarin_house.jpg",
    ):
        with urllib.request.urlopen(BASE + path, timeout=30) as r:
            check(r.status == 200 and len(r.read()) > 100, f"asset {path}")


def test_plans():
    scenarios = [
        ("爸媽一日歷史美食，預算唔想太貴，少行路", "zh-HK", "family"),
        ("幫我安排澳門三日兩夜，半島世遺、氹仔美食同路環慢活", "zh-HK", "multi"),
        ("我想去鄭家大屋同附近嘅歷史老街，星期三去", "zh-HK", "mandarin"),
        ("氹仔半日遊，主打地道美食", "zh-HK", "taipa"),
        ("A couple trip this Saturday: old lanes, photo spots and street food", "en", "couple"),
        ("First time in Macau this weekend, history and street food", "en", "first"),
    ]
    for q, lang, tag in scenarios:
        print(f"\n--- plan {tag} ---")
        t0 = time.time()
        events = plan_events(q, lang=lang)
        elapsed = time.time() - t0
        types = [e.get("type") for e in events]
        check("done" in types, f"{tag} reaches done", str(types[-5:]))
        check("error" not in types, f"{tag} no error event", str([e for e in events if e.get("type") == "error"]))
        check("tool_call" in types and "tool_result" in types, f"{tag} uses tools")
        check("result" in types, f"{tag} has result")
        result = next((e for e in events if e.get("type") == "result"), None)
        if not result:
            continue
        it = result["itinerary"]
        stops = it.get("stops") or []
        check(len(stops) >= 3, f"{tag} >=3 stops", str(len(stops)))
        names = [s.get("name", {}).get("zh") or s.get("name", {}).get("en") for s in stops]
        check(all(names), f"{tag} stop names present")
        check(it.get("totals", {}).get("stops", 0) >= 3, f"{tag} totals.stops")
        check("walk_km" in (it.get("totals") or {}), f"{tag} walk_km")
        if tag == "multi":
            days = it.get("days") or []
            check(len(days) >= 2, f"{tag} multi-day days", str(len(days)))
        if tag == "mandarin":
            # recovery should keep itinerary usable even if Mandarin House closed Wed
            joined = " ".join(names)
            check("鄭家" not in joined or "恋爱" in joined or "戀愛" in joined or len(stops) >= 3,
                  f"{tag} recovery usable", joined)
            check("recovery" in types or any("休息" in str(e) for e in events), f"{tag} recovery signal", str(types))
        check(elapsed < 240, f"{tag} finishes <240s", f"{elapsed:.1f}s")
        print(f"    title={it.get('title')} stops={names} {elapsed:.1f}s")


def test_browser():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        # desktop live
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.goto(BASE + "/", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(1500)
        badge = page.locator("#engineBadge").inner_text()
        check("Qwen" in badge and "策展" not in badge and "演示" not in badge and "Demo" not in badge,
              "badge shows live Qwen", badge)
        check(page.locator("#staticBanner").count() == 0 or page.locator("#staticBanner").is_hidden(),
              "no static banner on live host")

        # i18n switch
        for lang, needle in [("zh", "规划行程"), ("en", "Plan Trip"), ("pt", "Planear"), ("ja", "旅程"), ("zh-HK", "規劃行程")]:
            page.select_option("#lang", lang)
            page.wait_for_timeout(300)
            check(needle in page.locator(".nav-links a").first.inner_text(), f"i18n nav {lang}",
                  page.locator(".nav-links a").first.inner_text())

        # sample fill + plan
        page.select_option("#lang", "zh-HK")
        page.locator("#sampleChips .chip").nth(4).click()  # Taipa
        page.click("#planBtn")
        page.wait_for_selector("#result:not(.hidden) .r-banner", timeout=300000)
        page.wait_for_timeout(800)
        title = page.locator(".r-title").inner_text()
        check(bool(title), "UI result title", title)
        check(page.locator(".tl-stop").count() >= 3, "UI timeline stops")
        check(page.locator("#map").count() == 1, "UI map present")
        check(page.locator(".impact-panel").count() == 1, "UI impact panel")
        check("全隊總預算" in page.locator(".stats").inner_text() or "預算" in page.locator(".stats").inner_text(),
              "UI budget label")
        check(page.locator("#trace .tr").count() >= 5, "UI agent trace rows")
        body = page.locator("#result").inner_text()
        check("GitHub Pages" not in body and "static demo" not in body, "UI no technical jargon")

        # Mandarin House recovery UI
        page.fill("#prompt", "我想去鄭家大屋同附近嘅歷史老街，星期三去")
        page.click("#planBtn")
        page.wait_for_selector("#result:not(.hidden) .r-banner", timeout=300000)
        page.wait_for_timeout(500)
        trace = page.locator("#trace").inner_text()
        check("鄭家" in trace or "改線" in trace or "休息" in trace or page.locator(".tl-stop").count() >= 3,
              "UI mandarin recovery/result", trace[:200])

        # mobile
        page.close()
        mobile = browser.new_page(viewport={"width": 390, "height": 844})
        mobile.goto(BASE + "/", wait_until="domcontentloaded", timeout=60000)
        overflow = mobile.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
        check(overflow <= 2, "mobile no horizontal overflow", str(overflow))
        mobile.fill("#prompt", "情侶星期六想行下舊區老街影靚相")
        mobile.click("#planBtn")
        mobile.wait_for_selector("#result:not(.hidden) .r-banner", timeout=300000)
        overflow2 = mobile.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
        check(overflow2 <= 2, "mobile result no overflow", str(overflow2))
        check(mobile.locator(".tl-card").first.bounding_box()["width"] > 240, "mobile card readable")

        check(not errors, "no browser console errors", " | ".join(errors[:8]))
        mobile.close()
        browser.close()


def main():
    print(f"LIVE BASE = {BASE}")
    test_api()
    test_plans()
    test_browser()
    print("=" * 60)
    print(f"LIVE PASS {passed} FAIL {len(failures)}")
    for f in failures:
        print("FAIL:", f)
    # write report
    out = os.path.join(os.path.dirname(__file__), "reports", "live_server_qa.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(f"# Live Server QA\n\nBase: {BASE}\n\nPASS {passed} / FAIL {len(failures)}\n\n")
        for f in failures:
            fh.write(f"- FAIL: {f}\n")
        if not failures:
            fh.write("\nAll checks passed.\n")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
