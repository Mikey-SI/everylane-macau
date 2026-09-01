"""Browser QA for static GitHub Pages mode and live FastAPI mode."""
from __future__ import annotations

import os
import re
import subprocess
import sys
import time
import urllib.request

from playwright.sync_api import sync_playwright

STATIC = "http://127.0.0.1:8090/"
LIVE = "http://127.0.0.1:8000/"

passed = 0
failures: list[str] = []


def check(ok: bool, label: str, detail: str = ""):
    global passed
    if ok:
        passed += 1
    else:
        failures.append(f"{label}: {detail}")


def wait_result(page):
    page.wait_for_selector("#result:not(.hidden) .r-banner", timeout=15_000)
    page.wait_for_timeout(1900)


def url_ok(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            return response.status == 200
    except Exception:
        return False


def start_servers():
    """Make browser QA self-contained instead of relying on IDE terminals."""
    procs = []
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if not url_ok(STATIC):
        procs.append(subprocess.Popen(
            [sys.executable, "-m", "http.server", "8090"],
            cwd=os.path.join(root, "frontend"),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ))
    if not url_ok(LIVE + "api/health"):
        env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
        procs.append(subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", "8000"],
            cwd=os.path.join(root, "backend"),
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ))
    deadline = time.time() + 20
    while time.time() < deadline:
        if url_ok(STATIC) and url_ok(LIVE + "api/health"):
            return procs
        time.sleep(0.25)
    raise RuntimeError("QA servers did not start within 20 seconds")


def test_static(browser):
    errors: list[str] = []
    page = browser.new_page(viewport={"width": 1440, "height": 1050})
    page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.goto(STATIC, wait_until="domcontentloaded")

    # Translation dictionary structural parity.
    parity = page.evaluate(
        """() => {
          const d = window.__I18N;
          const base = Object.keys(d['zh-HK']).sort();
          return Object.fromEntries(Object.entries(d).map(([k,v]) => [
            k, {missing: base.filter(x => !(x in v)), extra: Object.keys(v).filter(x => !base.includes(x))}
          ]));
        }"""
    )
    for lang, diff in parity.items():
        check(not diff["missing"], f"i18n {lang} 无缺失 key", str(diff["missing"]))
        check(not diff["extra"], f"i18n {lang} 无多余 key", str(diff["extra"]))

    expected = {
        "zh-HK": ("zh-Hant", "規劃行程", "爸媽輕鬆歷史美食一日遊"),
        "zh": ("zh-Hans", "规划行程", "爸妈轻松历史美食一日游"),
        "en": ("en", "Plan Trip", "Easy Heritage & Local Food Day with Parents"),
        "pt": ("pt", "Planear Roteiro", "Dia tranquilo de património e gastronomia com os pais"),
        "ja": ("ja", "旅程を作る", "両親と巡るゆったり歴史・グルメ日帰り旅"),
    }
    check(page.locator("#lang option[value='zh']").inner_text() == "简体中文（普通话）",
          "简体中文选择器明确标注普通话")
    for lang, (html_lang, nav, title) in expected.items():
        page.select_option("#lang", lang)
        check(page.locator("html").get_attribute("lang") == html_lang, f"{lang} html lang")
        check(page.locator(".nav-links a").first.inner_text() == nav, f"{lang} 导航翻译")
        page.locator("#sampleChips .chip").first.click()
        page.click("#planBtn")
        wait_result(page)
        check(page.locator(".r-title").inner_text() == title, f"{lang} 动态标题翻译",
              page.locator(".r-title").inner_text())
        body = page.locator("#result").inner_text()
        check("undefined" not in body and "null" not in body, f"{lang} 无 undefined/null")
        check(not any(x in body for x in ("GitHub Pages", "FastAPI", "static demo", "靜態演示", "静态演示")),
              f"{lang} 用户结果不显示技术实现")
        if lang == "zh":
            check("千问普通话男声 · 龙安鲁风" in body,
                  "简体中文站点明确标注普通话男声")
            with page.expect_request(
                lambda req: req.url.endswith("ruins_st_paul.zh.mp3"),
                timeout=8_000,
            ) as audio_request:
                page.locator(".story-play").first.click()
            check(".zh-HK.mp3" not in audio_request.value.url,
                  "简体中文只请求普通话音频", audio_request.value.url)
            page.locator(".story-play").first.click()
        if lang == "pt":
            check("Rota coerente" in body and "Chegue cedo" in body, "葡语结果完整本地化")
            check("Coherent district" not in body and "Arrive early" not in body, "葡语无英文固定文案")
        if lang == "ja":
            check("エリア別" in body and "人気スポット" in body, "日语结果完整本地化")
            check("Coherent district" not in body and "Arrive early" not in body, "日语无英文固定文案")

    # Six sample scenarios must map to distinct, relevant results.
    page.select_option("#lang", "zh-HK")
    titles = [
        "爸媽輕鬆歷史美食一日遊",
        "澳門三日兩夜深度遊",
        "情侶舊區拍照小食半日遊",
        "鄭家大屋附近歷史老街替代路線",
        "氹仔半日地道美食線",
        "第一次來澳門經典深度線",
    ]
    seen = []
    for i, title in enumerate(titles):
        page.locator("#sampleChips .chip").nth(i).click()
        page.click("#planBtn")
        wait_result(page)
        got = page.locator(".r-title").inner_text()
        seen.append(got)
        check(got == title, f"示例 {i + 1} 场景匹配", got)
        imgs = page.locator("#result .tl-img img")
        for j in range(imgs.count()):
            imgs.nth(j).scroll_into_view_if_needed()
            page.wait_for_timeout(80)
            loaded = imgs.nth(j).evaluate("(img) => img.complete && img.naturalWidth > 0")
            check(loaded, f"示例 {i + 1} 图片 {j + 1} 加载")
    check(len(set(seen)) == 6, "六个示例输出各不相同", str(seen))
    check(page.locator(".tl-name").first.inner_text().startswith("大三巴"), "首次游首站为大三巴")

    # Free input outside the six chips must not silently fall back to parents.
    page.fill("#prompt", "路環自然漁村慢活一日遊")
    page.click("#planBtn")
    wait_result(page)
    check(page.locator(".r-title").inner_text() == "路環漁村慢活一日遊",
          "自由输入路环需求匹配路环路线", page.locator(".r-title").inner_text())
    names = " ".join(page.locator(".tl-name").all_inner_texts())
    check("路環" in names and "大三巴" not in names, "路环自由输入不回退半岛", names)

    page.fill("#prompt", "想隨便看看澳門建築")
    page.click("#planBtn")
    wait_result(page)
    check(page.locator(".r-title").inner_text() == "第一次來澳門經典深度線",
          "未知自由输入使用中性经典路线", page.locator(".r-title").inner_text())
    check("全隊總預算" in page.locator(".stats").inner_text(), "预算口径标为全队总额")
    check(page.locator(".impact-panel").count() == 1, "显示可归因导流成效面板")
    cards = page.locator(".tl-card").count()
    check(cards > 0 and page.locator(".story-play").count() == cards,
          "每个站点都有听阿濠讲古按钮",
          f"cards={cards} plays={page.locator('.story-play').count()}")
    check(page.locator(".story-more").count() == cards, "每个站点都有讲古全文")

    # Multi-day dates are consecutive and all three day headings localized.
    page.locator("#sampleChips .chip").nth(1).click()
    page.click("#planBtn")
    wait_result(page)
    check(page.locator(".day-chip").count() == 3, "三日两夜显示 3 天")
    day_text = " ".join(page.locator(".day-chip").all_inner_texts())
    check("半島世遺" in day_text and "氹仔美食" in day_text and "路環慢活" in day_text,
          "三日主题覆盖半岛/氹仔/路环", day_text)

    # Print mode: only result should remain visible.
    page.evaluate("document.body.classList.add('print-result')")
    page.emulate_media(media="print")
    check(page.locator("#result").evaluate("(e) => getComputedStyle(e).display !== 'none'"), "打印保留结果")
    check(page.locator(".hero").evaluate("(e) => getComputedStyle(e).display === 'none'"), "打印隐藏 Hero")
    check(page.locator("#planner").evaluate("(e) => getComputedStyle(e).display === 'none'"), "打印隐藏输入区")
    page.evaluate("document.body.classList.remove('print-result')")
    page.emulate_media(media="screen")

    check(page.locator("#staticBanner").count() == 1, "静态模式显示策展演示说明")
    check(not errors, "静态模式无控制台/Page Error", " | ".join(errors))
    page.close()


def test_mobile(browser):
    errors: list[str] = []
    page = browser.new_page(viewport={"width": 375, "height": 812}, device_scale_factor=2)
    page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.goto(STATIC, wait_until="domcontentloaded")
    overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    check(overflow <= 2, "手机首页无横向溢出", str(overflow))
    page.locator("#sampleChips .chip").nth(2).click()
    page.click("#planBtn")
    wait_result(page)
    overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    check(overflow <= 2, "手机结果无横向溢出", str(overflow))
    check(page.locator(".tl-card").first.bounding_box()["width"] > 250, "手机行程卡片宽度可读")
    check(page.locator("#map").bounding_box()["height"] >= 260, "手机地图高度足够")
    check(not errors, "手机模式无控制台/Page Error", " | ".join(errors))
    page.close()


def test_live(browser):
    errors: list[str] = []
    page = browser.new_page(viewport={"width": 1365, "height": 900})
    page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.goto(LIVE, wait_until="domcontentloaded")
    page.fill("#prompt", "我想去鄭家大屋同附近嘅歷史老街，星期三去")
    page.click("#planBtn")
    wait_result(page)
    body = page.locator("#result").inner_text()
    trace = page.locator("#trace").inner_text()
    check("你的澳門深度漫遊" in body, "后端模式生成真实结果")
    check("鄭家大屋" in trace and "自動改線" in trace, "后端模式展示休息日失败恢复")
    check(page.locator(".tl-stop").count() >= 3, "后端模式至少 3 站")
    check(page.locator("#map .leaflet-marker-icon").count() >= 3, "后端地图 Marker 正常")
    check(page.locator(".tg.access-ok, .tg.access-warn").count() >= 3,
          "行程站点带无障碍标注")
    # one-time visit code loop from the itinerary page
    if page.locator(".code-btn").count():
        page.locator(".code-btn").first.click()
        page.wait_for_selector("#result .code-chip", timeout=8_000)
        chip = page.locator("#result .code-chip").first.inner_text()
        check("EL-" in chip, "行程页可领取一次性到店码", chip)
    else:
        check(False, "行程页存在到店码按钮")
    check(not errors, "后端模式无控制台/Page Error", " | ".join(errors))
    page.close()


def test_dashboard(browser):
    """複賽成效儀表板 + 到店碼核銷閉環（真實 API）。"""
    errors: list[str] = []
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.goto(LIVE + "dashboard.html", wait_until="networkidle")
    page.wait_for_selector(".kpi", timeout=10_000)
    page.wait_for_selector("#runtimeBadge.ok", timeout=10_000)
    check("公網即時" in page.locator("#runtimeBadge").inner_text(),
          "仪表板区分真实运行数据")
    check(page.locator(".lineage-row.real").count() == 1
          and page.locator(".lineage-row.demo").count() == 1,
          "仪表板清晰区分真实与示范数据")
    check(page.locator("a[href='/api/impact/evidence']").count() == 1,
          "仪表板提供可审计证据 JSON")
    check(page.locator(".kpi").count() == 6, "仪表板 6 张 KPI 卡",
          page.locator(".kpi").count())
    check(page.locator("#targetTable tbody tr").count() == 9, "计划书指标对照 9 行")
    check(page.locator("#targetTable .t-ok").count() == 9, "计划书指标全部达标")
    check(page.locator(".merchant").count() == 5, "商户试点 5 间")
    check(page.locator("svg.chart-svg").count() >= 2, "SVG 走势图渲染")
    body = page.inner_text("body")
    check("86.4%" in body and "98.9%" in body and "41.8%" in body,
          "三大成效指标数值呈现")
    check("示範數據" in body or "示范数据" in body, "示范数据已明确标注")
    # full redeem loop: issue -> redeem -> duplicate rejected
    page.click("#issueBtn")
    page.wait_for_selector("#issuedCode:not(.hidden)", timeout=8_000)
    code = page.locator("#issuedCode").inner_text().replace("🎟️", "").strip()
    check(code.startswith("EL-"), "核销机领码成功", code)
    page.fill("#merchantPin", "2580")
    page.click("#redeemBtn")
    page.wait_for_selector(".redeem-result.ok", timeout=8_000)
    page.click("#redeemBtn")
    page.wait_for_selector(".redeem-result.warn", timeout=8_000)
    check("不可重用" in page.locator("#redeemResult").inner_text(), "一次性到店码不可重用")
    # index page exposes the dashboard entry
    page.goto(LIVE, wait_until="domcontentloaded")
    check(page.locator(".nav-links a[href='dashboard.html']").count() == 1,
          "主页导航含成效仪表板入口")
    check(page.locator(".proof-strip").count() == 0,
          "主页已移除复赛成果带")
    check(page.locator("#judgeDemoBtn").count() == 1,
          "主页保留 90 秒评审快速演示")
    page.click("#judgeDemoBtn")
    wait_result(page)
    check("可重現工具鏈" in page.locator("#result .r-meta").inner_text()
          or "可复现工具链" in page.locator("#result .r-meta").inner_text(),
          "90 秒评审模式透明标注运行引擎")
    check("qwen-audio-3.0-tts-plus" in page.locator("#trace").inner_text()
          and "longanlufeng" in page.locator("#trace").inner_text(),
          "90 秒评审轨迹标明预存千问男声")
    check(page.locator(".story-voice").count() >= 1, "90 秒评审站点标注龙安鲁风")
    check(page.locator("#trace .tr").count() >= 8,
          "90 秒评审模式完整展示工具轨迹")
    check(not errors, "仪表板无控制台/Page Error", " | ".join(errors))
    page.close()


def main():
    procs = start_servers()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            test_static(browser)
            test_mobile(browser)
            test_live(browser)
            test_dashboard(browser)
            browser.close()
    finally:
        for proc in procs:
            proc.terminate()
        for proc in procs:
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
    print(f"FRONTEND PASS {passed} FAIL {len(failures)}")
    for failure in failures:
        print("FAIL:", failure)
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
