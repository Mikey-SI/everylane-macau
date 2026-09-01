# -*- coding: utf-8 -*-
"""Regenerate selected prepacked Ah-Hou recordings.

Example on the production server:
  python backend/data/build_tts_pack.py --langs zh

The API key is read through backend/config.py and is never written to output.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
ROOT = BACKEND.parent
sys.path.insert(0, str(BACKEND))

import tts  # noqa: E402

DEFAULT_OUTPUT = ROOT / "frontend" / "tts"


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
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main():
    args = parse_args()
    output = args.output.resolve()
    manifest_path = output / "manifest.json"
    if not manifest_path.is_file():
        raise SystemExit(f"manifest not found: {manifest_path}")
    if not tts.available():
        raise SystemExit("QWEN_API_KEY is required")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = manifest.get("files") or {}
    pois = args.pois or list(files)
    unknown = [poi_id for poi_id in pois if poi_id not in files]
    if unknown:
        raise SystemExit(f"POIs absent from manifest: {', '.join(unknown)}")

    output.mkdir(parents=True, exist_ok=True)
    for poi_id in pois:
        for lang in args.langs:
            data, mime = tts.ensure_audio(poi_id, lang)
            if mime != "audio/mpeg":
                raise RuntimeError(f"{poi_id}/{lang}: expected MP3, got {mime}")
            name = f"{poi_id}.{lang}.mp3"
            tmp = output / (name + ".tmp")
            tmp.write_bytes(data)
            os.replace(tmp, output / name)
            files[poi_id][lang] = name
            print(f"{poi_id} {lang} {len(data)} bytes")

    manifest["model"] = "qwen-audio-3.0-tts-plus"
    manifest["voice"] = "longanlufeng"
    manifest["voice_name_zh"] = "龙安鲁风"
    manifest["profile_version"] = tts.TTS_PROFILE_VERSION
    manifest["language_modes"] = {
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
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"updated {len(pois)} POIs × {len(args.langs)} language(s)")


if __name__ == "__main__":
    main()
