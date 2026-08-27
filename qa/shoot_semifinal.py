# -*- coding: utf-8 -*-
"""複賽說明文檔配圖：對公網實拍，元件截圖 + 頁面實拍。

用法:  python qa/shoot_semifinal.py [BASE_URL]
輸出:  docs/assets/semifinal/*.png
"""
import io
import pathlib
import sys
import urllib.parse
import urllib.request

from PIL import Image, ImageDraw, ImageOps
from playwright.sync_api import sync_playwright

BASE = next((a for a in sys.argv[1:] if not a.startswith("-")), "http://127.0.0.1:8000").rstrip("/")
ITINERARY_ONLY = "--itinerary" in sys.argv or ":8090" in BASE
OUT = pathlib.Path(__file__).resolve().parents[1] / "docs" / "assets" / "semifinal"
OUT.mkdir(parents=True, exist_ok=True)

VIEWPORT = {"width": 1440, "height": 900}
CREAM = (248, 239, 221)
GOLD = (224, 203, 168)


def polish(path, max_w=1680):
    """Cream mat + gold hairline so screenshots sit cleanly on the PDF page."""
    im = Image.open(path).convert("RGB")
    if im.width > max_w:
        h = int(im.height * max_w / im.width)
        im = im.resize((max_w, h), Image.Resampling.LANCZOS)
    framed = ImageOps.expand(im, border=10, fill=CREAM)
    draw = ImageDraw.Draw(framed)
    draw.rectangle([0, 0, framed.width - 1, framed.height - 1], outline=GOLD, width=2)
    framed.save(path, "PNG", optimize=True)
    print("saved", path.name, path.stat().st_size, framed.size)


def shot(page, name):
    path = OUT / name
    page.screenshot(path=str(path))
    polish(path)


def shot_el(page, selector, name, timeout=15_000):
    loc = page.locator(selector).first
    loc.scroll_into_view_if_needed()
    page.wait_for_timeout(280)
    path = OUT / name
    loc.screenshot(path=str(path), timeout=timeout)
    polish(path)


def make_qr():
    dest = OUT / "site_qr.png"
    url = BASE + "/"
    try:
        import qrcode
        qr = qrcode.QRCode(border=1, box_size=10)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#2B2118", back_color="#F8EFDD").convert("RGB")
        img.save(dest)
        print("saved", dest.name, dest.stat().st_size)
        return
    except Exception as exc:
        print("qrcode lib fallback:", exc)
    api = "https://api.qrserver.com/v1/create-qr-code/?size=280x280&margin=8&data=" + urllib.parse.quote(url, safe="")
    urllib.request.urlretrieve(api, dest)
    print("saved", dest.name, dest.stat().st_size, "(api)")


def wait_stop_photos(page, timeout=25_000):
    """Force-eager every itinerary photo, then wait until they have pixels."""
    page.evaluate(
        """() => {
          document.querySelectorAll('#result img').forEach(img => {
            img.loading = 'eager';
            img.decoding = 'sync';
            if (!img.complete) img.src = img.src;
          });
        }"""
    )
    page.wait_for_function(
        """() => {
          const imgs = [...document.querySelectorAll('#result .tl-stop img')];
          if (!imgs.length) return false;
          return imgs.every(img => img.complete && img.naturalWidth > 0);
        }""",
        timeout=timeout,
    )


def reveal_stop(page, name, block="end"):
    card = page.locator(".tl-stop").filter(has_text=name)
    if not card.count():
        print("WARN missing stop:", name)
        return False
    page.evaluate(
        """([name, block]) => {
          const card = [...document.querySelectorAll('.tl-stop')]
            .find(c => (c.textContent || '').includes(name));
          if (card) card.scrollIntoView({ block, inline: 'nearest' });
        }""",
        [name, block],
    )
    page.wait_for_function(
        """(name) => {
          const cards = [...document.querySelectorAll('.tl-stop')];
          const card = cards.find(c => (c.textContent || '').includes(name));
          if (!card) return false;
          const img = card.querySelector('img');
          return !!(img && img.complete && img.naturalWidth > 0);
        }""",
        arg=name,
        timeout=20_000,
    )
    page.wait_for_timeout(400)
    return True


def assert_photo_detail(page, name):
    loc = page.locator(".tl-stop").filter(has_text=name).locator("img").first
    raw = loc.screenshot()
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    pixels = list(im.getdata())
    n = max(len(pixels), 1)
    avg = tuple(sum(p[i] for p in pixels) / n for i in range(3))
    var = sum(sum((p[i] - avg[i]) ** 2 for i in range(3)) for p in pixels) / n
    print(f"photo {name} size={im.size} var={var:.1f} avg={tuple(round(x) for x in avg)}")
    if var < 120:
        raise RuntimeError(f"{name} photo still looks blank/unloaded (var={var:.1f})")
    return True


def force_fast(route):
    url = route.request.url
    if "/api/plan" in url and "mode=auto" in url:
        url = url.replace("mode=auto", "mode=fast")
        print("rewrite plan -> fast")
    route.continue_(url=url)


def main():
    make_qr()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport=VIEWPORT)
        page.route("**/api/plan**", force_fast)

        # ---- 0) homepage hero + proof strip --------------------------------
        page.goto(f"{BASE}/", wait_until="networkidle")
        page.wait_for_selector("#judgeDemoBtn", timeout=15_000)
        page.wait_for_function("() => (document.querySelector('#hsPoi')||{}).textContent !== '—'", timeout=15_000)
        page.wait_for_timeout(400)
        shot(page, "00_home_proof.png")

        if not ITINERARY_ONLY:
            page.goto(f"{BASE}/dashboard.html", wait_until="networkidle")
            page.wait_for_selector(".kpi, .judge-path", timeout=15_000)
            page.wait_for_timeout(500)

            shot_el(page, ".judge-path", "00_dashboard_judgepath.png")

            page.locator("#evidence").scroll_into_view_if_needed()
            page.wait_for_timeout(400)
            shot_el(page, "#evidence", "00_dashboard_evidence.png")

            page.locator("#kpis").scroll_into_view_if_needed()
            page.wait_for_timeout(500)
            shot_el(page, "#kpis", "01_dashboard_kpi.png")

            page.locator("#targets").scroll_into_view_if_needed()
            page.wait_for_timeout(400)
            shot_el(page, "#targets", "02_dashboard_targets.png")

            page.locator("#heat").scroll_into_view_if_needed()
            page.wait_for_timeout(400)
            shot_el(page, "#heat", "03_dashboard_heat.png")

            page.locator("#redeemBox").scroll_into_view_if_needed()
            page.click("#issueBtn")
            page.wait_for_selector("#issuedCode:not(.hidden)", timeout=10_000)
            code = page.locator("#issuedCode").inner_text().replace("🎟️", "").strip()
            page.fill("#redeemInput", code)
            page.fill("#merchantPin", "2580")
            page.click("#redeemBtn")
            page.wait_for_selector(".redeem-result.ok", timeout=10_000)
            page.wait_for_timeout(250)
            shot_el(page, "#redeemBox", "04_dashboard_redeem.png")
            # keep a wider merchants+machine shot for the gallery
            page.locator("#merchants").scroll_into_view_if_needed()
            page.wait_for_timeout(200)
            shot_el(page, "#merchants", "04b_dashboard_merchants.png")

            page.goto(f"{BASE}/api.html", wait_until="networkidle")
            page.wait_for_selector(".dhero", timeout=15_000)
            page.wait_for_timeout(300)
            shot(page, "08_api.png")

        # ---- itinerary: 福隆新街 + 到店碼（fast 工具鏈，避免與真實 Qwen 搶時） ----
        page.set_viewport_size({"width": 1440, "height": 1050})
        page.goto(f"{BASE}/", wait_until="networkidle")
        page.fill("#prompt", "帶爸媽半日遊，想睇歷史建築同食地道小食，唔想行斜路，途經福隆新街")
        page.click("#planBtn")
        page.wait_for_selector(".tl-stop", timeout=90_000)
        wait_stop_photos(page)
        if page.locator(".code-btn").count():
            page.locator(".code-btn").first.click()
            try:
                page.wait_for_selector("#result .code-chip", timeout=10_000)
            except Exception:
                pass
        if not reveal_stop(page, "福隆新街"):
            raise RuntimeError("itinerary missing 福隆新街")
        wait_stop_photos(page)
        assert_photo_detail(page, "福隆新街")
        page.locator("#result").scroll_into_view_if_needed()
        page.wait_for_timeout(600)
        shot(page, "05_itinerary_access_code.png")

        if page.locator("#map").count():
            page.locator("#map").scroll_into_view_if_needed()
            page.wait_for_timeout(800)
            shot_el(page, "#map", "06_itinerary_map.png")

        page.locator(".tl-stop").filter(has_text="福隆新街").first.scroll_into_view_if_needed()
        page.wait_for_timeout(300)
        shot(page, "06_itinerary_header.png")

        # ---- 90-second judge mode ------------------------------------------
        page.goto(f"{BASE}/", wait_until="networkidle")
        page.click("#judgeDemoBtn")
        page.wait_for_selector(".tl-stop", timeout=90_000)
        wait_stop_photos(page)
        page.locator("#workspace").scroll_into_view_if_needed()
        page.wait_for_timeout(500)
        shot(page, "07_judge_fast_mode.png")

        browser.close()
    print("ALL_SHOTS_DONE")


if __name__ == "__main__":
    main()
