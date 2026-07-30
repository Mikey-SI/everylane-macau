# -*- coding: utf-8 -*-
"""Last two POIs — try broader Commons terms."""
import json
import os

from scrape_batch2 import search_images, IMG_DIR, HEADERS, HERE
import httpx
import urllib.parse

TERMS = {
    "hac_sa_park": ["Hac Sa Coloane", "黑沙 Coloane", "Hac Sa Macau"],
    "nga_tim_cafe": ["Largo Eduardo Marques Coloane", "Coloane square chapel", "路環 廣場"],
}

raw_path = os.path.join(HERE, "raw_scraped.json")
data = json.load(open(raw_path, encoding="utf-8"))
used_titles = {e.get("commons_file") for e in data.values() if e.get("commons_file")}

for pid, terms in TERMS.items():
    got = None
    for term in terms:
        try:
            for _, url, title in search_images(term):
                if title in used_titles:
                    continue
                got = (url, title)
                break
        except Exception as ex:
            print(pid, "search fail", term, ex)
        if got:
            break
    if not got:
        print(pid, "STILL NOTHING")
        continue
    url, title = got
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
    used_titles.add(title)
    print(pid, "OK <-", title)

json.dump(data, open(raw_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("DONE")
