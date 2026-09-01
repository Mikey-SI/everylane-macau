# -*- coding: utf-8 -*-
"""Regenerate selected prepacked Ah-Hou recordings.

Examples on the production server:
  python backend/data/build_tts_pack.py --langs zh
  python backend/data/build_tts_pack.py --all-pois --skip-existing --langs zh-HK zh en pt ja

The API key is read through backend/config.py and is never written to output.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
ROOT = BACKEND.parent
sys.path.insert(0, str(BACKEND))

import kb  # noqa: E402
import tts  # noqa: E402

DEFAULT_OUTPUT = ROOT / "frontend" / "tts"
LANG_MODES = {
    "zh-HK": {"speech": "Cantonese", "locale": "zh-HK"},
    "zh": {
        "speech": "Mandarin",
        "locale": "zh-CN",
        "cantonese_fallback": False,
    },
    "en": {"speech": "English", "locale": "en"},
    "pt": {"speech": "Portuguese", "locale": "pt"},
    "ja": {"speech": "Japanese", "locale": "ja"},
}


def parse_args():
    parser = argparse.ArgumentParser(description="Build prepacked Qwen TTS audio")
    parser.add_argument(
        "--langs",
        nargs="+",
        choices=tts.LANGS,
        required=True,
        help="Languages to regenerate; use zh for Simplified-Chinese Mandarin",
    )
    parser.add_argument("--pois", nargs="*", help="Optional POI ids; defaults to manifest")
    parser.add_argument("--all-pois", action="store_true", help="Cover every story POI")
    parser.add_argument("--skip-existing", action="store_true", help="Keep mp3s that already exist")
    parser.add_argument("--sleep", type=float, default=0.35, help="Pause between live synthesises")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def write_manifest(path: Path, files: dict) -> None:
    manifest = {
        "model": "qwen-audio-3.0-tts-plus",
        "voice": "longanlufeng",
        "voice_name_zh": "龙安鲁风",
        "profile_version": tts.TTS_PROFILE_VERSION,
        "poi_count": len(files),
        "language_count": len(tts.LANGS),
        "language_modes": LANG_MODES,
        "files": files,
    }
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    args = parse_args()
    output = args.output.resolve()
    manifest_path = output / "manifest.json"
    files = {}
    if manifest_path.is_file():
        files = (json.loads(manifest_path.read_text(encoding="utf-8")).get("files") or {})

    if args.all_pois:
        pois = list(kb.STORIES)
    else:
        pois = args.pois or list(files)
        unknown = [poi_id for poi_id in pois if poi_id not in files]
        if unknown and not args.pois:
            raise SystemExit(f"POIs absent from manifest: {', '.join(unknown)}")

    if not tts.available():
        raise SystemExit("QWEN_API_KEY is required")

    output.mkdir(parents=True, exist_ok=True)
    failures = []
    for poi_id in pois:
        files.setdefault(poi_id, {})
        for lang in args.langs:
            name = f"{poi_id}.{lang}.mp3"
            dest = output / name
            if args.skip_existing and dest.is_file() and dest.stat().st_size > 10_000:
                files[poi_id][lang] = name
                print(f"{poi_id} {lang} skip {dest.stat().st_size}")
                continue
            try:
                data, mime = tts.ensure_audio(poi_id, lang)
                if mime != "audio/mpeg":
                    raise RuntimeError(f"expected MP3, got {mime}")
                tmp = output / (name + ".tmp")
                tmp.write_bytes(data)
                os.replace(tmp, dest)
                files[poi_id][lang] = name
                print(f"{poi_id} {lang} {len(data)} bytes")
                if args.sleep:
                    time.sleep(args.sleep)
            except Exception as exc:
                failures.append(f"{poi_id}/{lang}: {exc}")
                print(f"{poi_id} {lang} FAIL {exc}")

    write_manifest(manifest_path, files)
    print(f"updated {len(pois)} POIs × {len(args.langs)} language(s)")
    print(f"packed {len(files)} POIs; failures {len(failures)}")
    if failures:
        print("FAILURES")
        for item in failures:
            print(item)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
