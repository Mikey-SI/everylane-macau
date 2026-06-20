# -*- coding: utf-8 -*-
"""Fetch real photos for POIs lacking images (old streets, food shops) from
Wikimedia Commons search. Updates raw_scraped.json so build_kb picks them up."""
import json, os, urllib.parse, httpx, time

HERE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "frontend", "assets", "poi"))
os.makedirs(IMG_DIR, exist_ok=True)
HEADERS = {"User-Agent": "Mozilla/5.0 EveryLaneMacau/1.0 (academic; mailto:dc227126@um.edu.mo)"}
API = "https://commons.wikimedia.org/w/api.php"

# id -> Commons search term (chosen to land on the right place)
TERMS = {
    "travessa_paixao": "Travessa da Paixão Macau",
    "rua_felicidade": "Rua da Felicidade Macau",
    "rua_cinco": "Rua de Cinco de Outubro Macau",
    "rua_estalagens": "Rua das Estalagens Macau",
    "guan_qian": "Rua de Nossa Senhora do Amparo Macau",
    "penha_church": "Penha Church Macau",
    "st_augustine": "Church of St. Augustine Macau",
    "lilau_square": "Lilau Square Macau",
    "st_francis_coloane": "Chapel of St. Francis Xavier Coloane",
    "wong_chi_kei": "Wong Chi Kei Macau",
    "yee_shun_milk": "Yee Shun Milk Company Macau",
    "tai_lei_loi": "Tai Lei Loi Kei",
    "lord_stow": "Lord Stow's Bakery Coloane",
    "mok_yi_kei": "Mok Yi Kei Macau",
    "rua_cunha": "Rua do Cunha Taipa",
}

BAD = ("logo", "icon", "map", "flag", "coat", "diagram", "svg", ".pdf", "locator")


def search_image(term):
    params = {
        "action": "query", "format": "json", "generator": "search",
        "gsrnamespace": "6", "gsrlimit": "12", "gsrsearch": term,
        "prop": "imageinfo", "iiprop": "url|size|mime", "iiurlwidth": "1200",
    }
    r = httpx.get(API, params=params, headers=HEADERS, timeout=40)
    r.raise_for_status()
    pages = (r.json().get("query") or {}).get("pages") or {}
    cands = []
    for pg in pages.values():
        title = pg.get("title", "").lower()
        ii = (pg.get("imageinfo") or [{}])[0]
        mime = ii.get("mime", "")
        w = ii.get("width", 0)
        if mime not in ("image/jpeg", "image/png"):
            continue
        if any(b in title for b in BAD):
            continue
        if w < 600:
            continue
        url = ii.get("thumburl") or ii.get("url")
        if url:
            cands.append((pg.get("index", 99), url, pg.get("title")))
    cands.sort(key=lambda x: x[0])
    return cands[0] if cands else None


raw_path = os.path.join(HERE, "raw_scraped.json")
data = json.load(open(raw_path, encoding="utf-8"))

for pid, term in TERMS.items():
    # skip if already has a local image on disk from earlier scrape
    if data.get(pid, {}).get("local_image"):
        existing = os.path.join(HERE, "..", "..", "frontend", data[pid]["local_image"])
        if os.path.isfile(os.path.normpath(existing)):
            print(f"  {pid}: already has image, skip")
            continue
    try:
        hit = search_image(term)
        if not hit:
            print(f"  {pid}: no image found for '{term}'")
            continue
        _, url, title = hit
        ext = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower()
        if ext not in (".jpg", ".jpeg", ".png", ".webp"):
            ext = ".jpg"
        fn = f"{pid}{ext}"
        with httpx.stream("GET", url, headers=HEADERS, timeout=60, follow_redirects=True) as resp:
            resp.raise_for_status()
            with open(os.path.join(IMG_DIR, fn), "wb") as f:
                for chunk in resp.iter_bytes():
                    f.write(chunk)
        e = data.get(pid, {})
        e["image_url"] = url
        e["local_image"] = f"assets/poi/{fn}"
        e["commons_file"] = title
        data[pid] = e
        print(f"  {pid}: OK <- {title}")
    except Exception as ex:
        print(f"  {pid}: FAIL {ex}")
    time.sleep(0.4)

json.dump(data, open(raw_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("DONE")
