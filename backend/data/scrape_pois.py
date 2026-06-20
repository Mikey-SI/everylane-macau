# -*- coding: utf-8 -*-
"""
Scrape real coordinates + lead images for Macau POIs from Wikipedia/Wikimedia.
Output: raw_scraped.json  (coords + image url + local image path)
Images are downloaded into ../../frontend/assets/poi/
This satisfies the "use real data / scrape images" requirement and guarantees
that coordinates used for routing are real.
"""
import json
import os
import time
import urllib.parse
import httpx

HERE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "frontend", "assets", "poi"))
os.makedirs(IMG_DIR, exist_ok=True)

# id -> English Wikipedia title (best source for coordinates & images)
TITLES = {
    "ruins_st_paul": "Ruins of St. Paul's",
    "monte_fort": "Mount Fortress",
    "senado_square": "Senado Square",
    "leal_senado": "Leal Senado",
    "st_dominic": "St. Dominic's Church, Macau",
    "a_ma_temple": "A-Ma Temple",
    "mandarin_house": "Mandarin's House",
    "lilau_square": "Lilau Square",
    "st_augustine": "St. Augustine's Church, Macau",
    "st_lawrence": "St. Lawrence's Church, Macau",
    "moorish_barracks": "Moorish Barracks",
    "guia_fortress": "Guia Fortress",
    "taipa_houses": "Taipa Houses-Museum",
    "rua_cunha": "Rua do Cunha",
    "st_francis_coloane": "Chapel of St. Francis Xavier, Coloane",
    "macau_tower": "Macau Tower",
    "ho_tung_library": "Sir Robert Ho Tung Library",
    "dom_pedro_theatre": "Dom Pedro V Theatre",
    "sam_kai_vui_kun": "Sam Kai Vui Kun",
    "na_tcha_temple": "Na Tcha Temple",
    "camoes_garden": "Casa Garden",
    "lou_kau_mansion": "Lou Kau Mansion",
}

API = "https://en.wikipedia.org/w/api.php"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) EveryLaneMacau/1.0 "
                  "(academic student project; https://github.com/everylane-macau; mailto:dc227126@um.edu.mo)",
    "Accept": "application/json",
    "Accept-Language": "en,zh;q=0.8",
}


def fetch_batch(titles):
    params = {
        "action": "query",
        "format": "json",
        "prop": "coordinates|pageimages|info",
        "piprop": "original|thumbnail",
        "pithumbsize": "1200",
        "inprop": "url",
        "coprimary": "primary",
        "titles": "|".join(titles),
        "redirects": "1",
    }
    r = httpx.get(API, params=params, headers=HEADERS, timeout=40)
    r.raise_for_status()
    return r.json()


def main():
    title_to_id = {v: k for k, v in TITLES.items()}
    all_titles = list(TITLES.values())
    result = {}

    # query in batches of 10
    norm_map = {}
    pages = {}
    for i in range(0, len(all_titles), 10):
        batch = all_titles[i:i + 10]
        data = fetch_batch(batch)
        q = data.get("query", {})
        for n in q.get("normalized", []):
            norm_map[n["to"]] = n["from"]
        for r in q.get("redirects", []):
            norm_map[r["to"]] = r["from"]
        for pid, page in q.get("pages", {}).items():
            pages[page.get("title")] = page
        time.sleep(0.4)

    def resolve_origin(title):
        seen = 0
        t = title
        while t in norm_map and seen < 5:
            t = norm_map[t]
            seen += 1
        return t

    for title, page in pages.items():
        origin = resolve_origin(title)
        pid = title_to_id.get(origin) or title_to_id.get(title)
        if not pid:
            # try fuzzy
            for k, v in TITLES.items():
                if v.lower() == title.lower():
                    pid = k
                    break
        if not pid:
            print("  ?? could not map:", title)
            continue
        entry = {"wiki_title": title, "wiki_url": page.get("fullurl")}
        coords = page.get("coordinates")
        if coords:
            entry["lat"] = coords[0]["lat"]
            entry["lng"] = coords[0]["lon"]
        img = page.get("original") or page.get("thumbnail")
        if img:
            entry["image_url"] = img["source"]
        result[pid] = entry
        print(f"  OK {pid}: lat={entry.get('lat')}, img={'Y' if entry.get('image_url') else 'N'}")

    # download images
    for pid, e in result.items():
        url = e.get("image_url")
        if not url:
            continue
        ext = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower()
        if ext not in (".jpg", ".jpeg", ".png", ".webp"):
            ext = ".jpg"
        fn = f"{pid}{ext}"
        fp = os.path.join(IMG_DIR, fn)
        try:
            with httpx.stream("GET", url, headers=HEADERS, timeout=60, follow_redirects=True) as resp:
                resp.raise_for_status()
                with open(fp, "wb") as f:
                    for chunk in resp.iter_bytes():
                        f.write(chunk)
            e["local_image"] = f"assets/poi/{fn}"
            print(f"  IMG {pid} -> {fn} ({os.path.getsize(fp)//1024} KB)")
        except Exception as ex:
            print(f"  IMG FAIL {pid}: {ex}")
        time.sleep(0.3)

    out = os.path.join(HERE, "raw_scraped.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("Saved", out, "with", len(result), "entries")
    print("DONE")


if __name__ == "__main__":
    main()
