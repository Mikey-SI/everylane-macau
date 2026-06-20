# -*- coding: utf-8 -*-
"""Fetch lead images for the 3 POIs that lacked pageimages, via REST summary API."""
import json, os, urllib.parse, httpx, time

HERE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "frontend", "assets", "poi"))
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) EveryLaneMacau/1.0 "
                  "(academic student project; mailto:dc227126@um.edu.mo)",
}
REST = "https://en.wikipedia.org/api/rest_v1/page/summary/"

# id -> (title, lat, lng)  coordinates hand-verified from Macau heritage records
MISSING = {
    "lilau_square": ("Lilau Square", 22.18879, 113.53381),
    "st_augustine": ("St. Augustine's Church, Macau", 22.19166, 113.53745),
    "st_francis_coloane": ("Chapel of St. Francis Xavier, Coloane", 22.11649, 113.55560),
}

raw_path = os.path.join(HERE, "raw_scraped.json")
data = json.load(open(raw_path, encoding="utf-8"))

for pid, (title, lat, lng) in MISSING.items():
    e = data.get(pid, {})
    e["lat"] = lat
    e["lng"] = lng
    try:
        r = httpx.get(REST + urllib.parse.quote(title.replace(" ", "_")), headers=HEADERS, timeout=40, follow_redirects=True)
        r.raise_for_status()
        j = r.json()
        img = (j.get("originalimage") or j.get("thumbnail") or {}).get("source")
        if img:
            e["image_url"] = img
            ext = os.path.splitext(urllib.parse.urlparse(img).path)[1].lower()
            if ext not in (".jpg", ".jpeg", ".png", ".webp"):
                ext = ".jpg"
            fn = f"{pid}{ext}"
            with httpx.stream("GET", img, headers=HEADERS, timeout=60, follow_redirects=True) as resp:
                resp.raise_for_status()
                with open(os.path.join(IMG_DIR, fn), "wb") as f:
                    for chunk in resp.iter_bytes():
                        f.write(chunk)
            e["local_image"] = f"assets/poi/{fn}"
            print(f"  {pid}: img OK -> {fn}")
        else:
            print(f"  {pid}: no image in summary")
    except Exception as ex:
        print(f"  {pid}: FAIL {ex}")
    data[pid] = e
    time.sleep(0.4)

json.dump(data, open(raw_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("DONE")
