"""Cycle 5 repository, deliverable and credential consistency checks."""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

import tools  # noqa: E402

passes = 0
fails: list[str] = []


def check(ok, label, detail=""):
    global passes
    if ok:
        passes += 1
    else:
        fails.append(f"{label}: {detail}")


def text_files():
    allowed = {".py", ".js", ".css", ".html", ".md", ".json", ".txt", ".bat", ".sh", ".example"}
    ignored = {".git", ".venv", "__pycache__", "node_modules", "logs"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in ignored for part in path.parts):
            continue
        if path.suffix.lower() in allowed or path.name == ".env.example":
            yield path


def main():
    pois = json.loads((ROOT / "backend/data/pois.json").read_text(encoding="utf-8"))
    check(len(pois) == 70, "POI count exactly 70")
    stories = json.loads((ROOT / "frontend" / "stories.json").read_text(encoding="utf-8"))
    check(len(stories) == 70, "frontend stories.json has 70 POIs")
    check(set(stories) == {p["id"] for p in pois}, "story ids match POI ids")
    check(all(all((stories[i].get(lang) or "").strip() for lang in ("zh-HK", "zh", "en", "pt", "ja")) for i in stories),
          "every story has five languages")
    check(len(tools.TOOLS) == 7, "granular tool count exactly 7")
    check(all(p["image"] for p in pois), "all POIs have image paths")
    check(all((ROOT / "frontend" / p["image"]).is_file() for p in pois),
          "all POI image files exist")

    pack = json.loads((ROOT / "frontend/tts/manifest.json").read_text(encoding="utf-8"))
    check(pack.get("model") == "qwen-audio-3.0-tts-plus", "packed TTS is qwen-audio-3.0-tts-plus")
    check(pack.get("voice") == "longanlufeng", "packed TTS voice is longanlufeng")
    check(pack.get("profile_version") == "20260901-mandarin-v2",
          "packed TTS profile version is current")
    mandarin = (pack.get("language_modes") or {}).get("zh") or {}
    check(mandarin.get("speech") == "Mandarin"
          and mandarin.get("locale") == "zh-CN"
          and mandarin.get("cantonese_fallback") is False,
          "Simplified Chinese audio contract is Mandarin-only", mandarin)
    for poi_id, rec in (pack.get("files") or {}).items():
        name = rec.get("zh")
        audio = ROOT / "frontend/tts" / name if name else None
        check(bool(name) and name.endswith(".zh.mp3")
              and audio.is_file() and audio.stat().st_size > 10_000,
              f"packed Mandarin audio {poi_id}")
    judge_pois = [
        "ruins_st_paul", "travessa_paixao", "rua_estalagens",
        "rua_cinco", "rua_felicidade", "lou_kau_mansion",
    ]
    langs = ("zh-HK", "zh", "en", "pt", "ja")
    for poi_id in judge_pois:
        for lang in langs:
            name = ((pack.get("files") or {}).get(poi_id) or {}).get(lang)
            audio = ROOT / "frontend/tts" / name if name else None
            check(bool(name) and audio.is_file() and audio.stat().st_size > 10_000,
                  f"packed judge audio {poi_id} {lang}")

    # No production credential (placeholder text is allowed).
    secret_re = re.compile(r"sk-sp-[A-Za-z0-9_./+=-]{20,}")
    secret_files = []
    stale_files = []
    stale = (
        "街知巷聞工作室",
        "參賽者：SITINIEK",
        "34 個景點",
        "34个景点",
        "對標 QwenPaw 的五層",
    )
    for path in text_files():
        if path.resolve() == Path(__file__).resolve():
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if secret_re.search(content):
            secret_files.append(str(path.relative_to(ROOT)))
        if any(term in content for term in stale):
            stale_files.append(str(path.relative_to(ROOT)))
    check(not secret_files, "repository has no Token Plan secret", secret_files)
    check(not stale_files, "repository has no stale identity/architecture claims", stale_files)
    check(not (ROOT / ".env").exists(), "local .env not present in repository workspace")

    required = [
        "docs/概念計劃書_街知巷聞_EveryLaneMacau.docx",
        "docs/概念計劃書_街知巷聞_EveryLaneMacau.pdf",
        "docs/實踐文章_街知巷聞_EveryLaneMacau.docx",
        "docs/實踐文章_街知巷聞_EveryLaneMacau.pdf",
        "docs/開發過程證明_QwenPaw_街知巷聞.docx",
        "docs/開發過程證明_QwenPaw_街知巷聞.pdf",
        "docs/團隊介紹視頻腳本_3分鐘.md",
        "docs/團隊介紹視頻_3分鐘.mp4",
        "qwenpaw/skill/everylane-macau/SKILL.md",
        "qwenpaw/mcp_server.py",
        "qwenpaw/README.md",
        # 複賽 deliverables
        "backend/impact.py",
        "frontend/dashboard.html",
        "frontend/dashboard.js",
        "frontend/dashboard.css",
        "frontend/api.html",
        "docs/複賽說明文檔_街知巷聞.docx",
        "docs/複賽說明文檔_街知巷聞.pdf",
        "docs/make_final_pitch.py",
        "docs/決賽路演_10分鐘_街知巷聞.pptx",
        "docs/決賽路演_10分鐘_街知巷聞.pdf",
        "docs/決賽路演_10分鐘講稿_街知巷聞.md",
        "docs/評審問答_冠軍版_街知巷聞.md",
        "docs/專業評委評分與冠軍改進報告_街知巷聞.md",
        "docs/assets/semifinal/00_home_proof.png",
    ]
    for rel in required:
        check((ROOT / rel).is_file(), f"deliverable exists: {rel}")

    video = ROOT / "docs/團隊介紹視頻_3分鐘.mp4"
    try:
        import imageio_ffmpeg

        frames = imageio_ffmpeg.read_frames(str(video), pix_fmt="rgb24")
        metadata = next(frames)
        frames.close()
        duration = float(metadata["duration"])
        check(120 <= duration < 180, "team video duration below 3 minutes", duration)
        check(metadata["size"] == (1920, 1080), "team video is 1080p", metadata["size"])
        check(video.stat().st_size > 2_000_000, "team video file has audio/video payload",
              video.stat().st_size)
    except Exception as exc:
        check(False, "team video metadata readable", str(exc))

    for i in range(1, 5):
        matches = list((ROOT / "docs/assets/qwenpaw").glob(f"0{i}_*.png"))
        check(len(matches) == 1 and matches[0].stat().st_size > 50_000,
              f"QwenPaw evidence image {i} valid",
              [str(m) for m in matches])

    # Extract PDFs to verify identity and QwenPaw evidence survived conversion.
    try:
        import fitz

        pdf_expect = {
            "docs/概念計劃書_街知巷聞_EveryLaneMacau.pdf": [
                "愛拼才會贏", "施天益", "QwenPaw 2.0.0", "EveryLane Macau MCP",
            ],
            "docs/實踐文章_街知巷聞_EveryLaneMacau.pdf": [
                "愛拼才會贏", "施天益", "QwenPaw 2.0.0", "qwen3.7-plus",
            ],
            "docs/開發過程證明_QwenPaw_街知巷聞.pdf": [
                "愛拼才會贏", "施天益", "QwenPaw 2.0.0", "641 PASS",
            ],
            "docs/複賽說明文檔_街知巷聞.pdf": [
                "愛拼才會贏", "施天益", "導流覆蓋率", "路線可行率", "商戶到訪率",
                "一次性到店碼", "el-demo-2026", "47.79.228.128",
            ],
            "docs/決賽路演_10分鐘_街知巷聞.pdf": [
                "愛拼才會贏", "街知巷聞", "QwenPaw", "到店碼", "641",
            ],
        }
        for rel, needles in pdf_expect.items():
            doc = fitz.open(ROOT / rel)
            text = "\n".join(page.get_text() for page in doc)
            check(all(needle in text for needle in needles),
                  f"PDF content verified: {rel}",
                  [n for n in needles if n not in text])
            check(3 <= len(doc) <= 12, f"PDF page count sane: {rel}", len(doc))
    except ImportError:
        check(False, "PyMuPDF available for PDF verification")

    temp = [p.name for p in (ROOT / "docs").glob("~$*")]
    check(not temp, "no Word lock/temp files", temp)

    print(f"REPOSITORY PASS {passes} FAIL {len(fails)}")
    for failure in fails:
        print("FAIL:", failure)
    raise SystemExit(1 if fails else 0)


if __name__ == "__main__":
    main()
