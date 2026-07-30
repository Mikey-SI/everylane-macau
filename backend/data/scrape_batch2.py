# -*- coding: utf-8 -*-
"""Fetch Commons photos for the remaining POIs that still lack images.
Each POI gets a primary + fallback search term; skips files already used by
other POIs so the gallery stays visually distinct."""
import json
import os
import time
import urllib.parse

import httpx

HERE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "frontend", "assets", "poi"))
os.makedirs(IMG_DIR, exist_ok=True)
HEADERS = {"User-Agent": "Mozilla/5.0 EveryLaneMacau/1.0 (academic; mailto:dc227126@um.edu.mo)"}
API = "https://commons.wikimedia.org/w/api.php"

# poi_id -> [search terms in priority order]
TERMS = {
    "cathedral_macau": ["Cathedral of the Nativity of Our Lady Macau", "Se Cathedral Macau"],
    "hang_yau_fishball": ["Travessa da Se Macau", "Macau street food curry fishball"],
    "holy_house_mercy": ["Holy House of Mercy Macau", "Santa Casa da Misericordia Macau"],
    "lin_fong_temple": ["Lin Fong Temple Macau", "Lin Fung Temple Macau"],
    "lou_lim_ioc_garden": ["Lou Lim Ieoc Garden", "Lou Lim Ioc Garden Macau"],
    "macau_museum": ["Macao Museum building", "Museu de Macau"],
    "old_city_walls": ["Old City Walls Macau", "Troco das Antigas Muralhas de Defesa"],
    "red_market": ["Red Market Macau", "Mercado Vermelho Macau"],
    "st_anthony_church": ["St. Anthony's Church Macau", "Igreja de Santo Antonio Macau"],
    "tap_seac_gallery": ["Tap Seac Gallery", "Tap Seac Square buildings Macau"],
    "tap_seac_square": ["Tap Seac Square Macau", "Praca do Tap Seac"],
    "three_lamps": ["Rotunda de Carlos da Maia Macau", "Three Lamps district Macau"],
    "cheoc_van_beach": ["Cheoc Van Beach Coloane", "Praia de Cheoc Van"],
    "coloane_village": ["Coloane Village", "Coloane town Macau"],
    "fernando_restaurant": ["Restaurante Fernando Coloane", "Hac Sa Coloane"],
    "hac_sa_beach": ["Hac Sa Beach Coloane", "Praia de Hac Sa"],
    "hac_sa_park": ["Hac Sa Reservoir Coloane", "Hac Sa Coloane park"],
    "lai_chi_vun": ["Lai Chi Vun shipyards", "Coloane shipyard Macau"],
    "nga_tim_cafe": ["Eduardo Marques Square Coloane", "Coloane St Francis Xavier square"],
    "panda_pavilion": ["Macao Giant Panda Pavilion", "Giant panda Macau"],
    "seac_pai_van_park": ["Seac Pai Van Park", "Parque de Seac Pai Van"],
    "tam_kung_temple": ["Tam Kung Temple Coloane", "Tam Kung Miu Coloane"],
    "fishermans_wharf": ["Macau Fisherman's Wharf", "Fisherman's Wharf Macau"],
    "grand_prix_museum": ["Macau Grand Prix Museum", "Grande Premio Museum Macau"],
    "kun_iam_temple": ["Kun Iam Temple Macau", "Kun Iam Tong Macau"],
    "science_center": ["Macao Science Center", "Macau Science Center"],
    "kun_iam_statue": ["Kun Iam Statue Macau", "Kun Iam Ecumenical Centre Macau"],
    "broadway_food_street": ["Broadway Macau", "Broadway Food Street Macau"],
    "carmel_church": ["Our Lady of Carmel Church Taipa", "Igreja de Nossa Senhora do Carmo Taipa"],
    "mok_yi_kei": ["Rua do Cunha Taipa night", "Taipa food street Macau"],
    "old_taipa_market": ["Feira do Carmo Taipa", "Taipa old market Macau"],
    "pak_tai_temple_taipa": ["Pak Tai Temple Taipa", "Templo Pak Tai Taipa"],
    "parisian_macau": ["The Parisian Macao", "Parisian Macao Eiffel Tower"],
    "pou_tai_temple": ["Pou Tai Temple Taipa", "Pou Tai Un Temple Macau"],
    "seng_cheong": ["Rua do Cunha Taipa", "Taipa Village street food"],
    "taipa_museum": ["Museum of Taipa and Coloane History", "Taipa Houses Museum green"],
    "taipa_village": ["Taipa Village Macau", "Old Taipa Macau street"],
    "venetian_macau": ["The Venetian Macao exterior", "Venetian Macao"],
}

BAD = ("logo", "icon", "map", "flag", "coat", "diagram", "svg", ".pdf", "locator",
       "plan ", "chart", "seal", "emblem", "poster")


def search_images(term):
    params = {
        "action": "query", "format": "json", "generator": "search",
        "gsrnamespace": "6", "gsrlimit": "15", "gsrsearch": term,
        "prop": "imageinfo", "iiprop": "url|size|mime", "iiurlwidth": "1200",
    }
    r = httpx.get(API, params=params, headers=HEADERS, timeout=40)
    r.raise_for_status()
    pages = (r.json().get("query") or {}).get("pages") or {}
    cands = []
    for pg in pages.values():
        title = pg.get("title", "")
        ii = (pg.get("imageinfo") or [{}])[0]
        if ii.get("mime") not in ("image/jpeg", "image/png"):
            continue
        if any(b in title.lower() for b in BAD):
            continue
        if ii.get("width", 0) < 500:
            continue
        url = ii.get("thumburl") or ii.get("url")
        if url:
            cands.append((pg.get("index", 99), url, title))
    cands.sort(key=lambda x: x[0])
    return cands


def main():
    raw_path = os.path.join(HERE, "raw_scraped.json")
    data = json.load(open(raw_path, encoding="utf-8"))
    used_titles = {e.get("commons_file") for e in data.values() if e.get("commons_file")}

    ok = fail = 0
    for pid, terms in TERMS.items():
        e = data.get(pid, {})
        if e.get("local_image"):
            existing = os.path.normpath(os.path.join(HERE, "..", "..", "frontend", e["local_image"]))
            if os.path.isfile(existing):
                print(f"  {pid}: already has image, skip")
                continue
        got = None
        for term in terms:
            try:
                for _, url, title in search_images(term):
                    if title in used_titles:
                        continue
                    got = (url, title)
                    break
            except Exception as ex:
                print(f"  {pid}: search fail '{term}' {ex}")
            if got:
                break
            time.sleep(0.3)
        if not got:
            print(f"  {pid}: NO IMAGE FOUND")
            fail += 1
            continue
        url, title = got
        ext = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower()
        if ext not in (".jpg", ".jpeg", ".png", ".webp"):
            ext = ".jpg"
        fn = f"{pid}{ext}"
        try:
            with httpx.stream("GET", url, headers=HEADERS, timeout=60, follow_redirects=True) as resp:
                resp.raise_for_status()
                with open(os.path.join(IMG_DIR, fn), "wb") as f:
                    for chunk in resp.iter_bytes():
                        f.write(chunk)
        except Exception as ex:
            print(f"  {pid}: download fail {ex}")
            fail += 1
            continue
        e["image_url"] = url
        e["local_image"] = f"assets/poi/{fn}"
        e["commons_file"] = title
        data[pid] = e
        used_titles.add(title)
        ok += 1
        print(f"  {pid}: OK <- {title}")
        time.sleep(0.4)

    json.dump(data, open(raw_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"DONE ok={ok} fail={fail}")


if __name__ == "__main__":
    main()
