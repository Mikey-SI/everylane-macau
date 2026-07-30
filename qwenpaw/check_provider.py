"""Safe Token Plan / DashScope connection diagnostic.

Reads local environment variables but never prints the API key. Use --dry-run
to validate key/base-url/model compatibility without consuming credits.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "backend"))

import config  # noqa: E402

TOKEN_PLAN_MODELS = {
    "qwen3.7-max",
    "qwen3.7-plus",
    "qwen3.6-plus",
    "qwen3.6-flash",
}


def validate():
    key = config.QWEN_API_KEY
    url = config.QWEN_BASE_URL
    model = config.QWEN_MODEL
    errors = []
    if not key:
        errors.append("未设置 QWEN_API_KEY（请只写入本机 .env）")
    is_token_key = key.startswith("sk-sp-")
    is_token_url = "token-plan." in url
    if key and is_token_key != is_token_url:
        errors.append("Key 与 Base URL 套餐不匹配：sk-sp Key 必须配 Token Plan URL")
    if is_token_url and model not in TOKEN_PLAN_MODELS:
        errors.append(
            f"Token Plan 模型 {model!r} 不在本项目验证白名单；建议 qwen3.7-plus"
        )
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        errors.append("QWEN_BASE_URL 必须是有效 HTTPS 地址")
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    errors = validate()
    print("Provider:", urlparse(config.QWEN_BASE_URL).netloc or "(invalid)")
    print("Model:", config.QWEN_MODEL)
    print("Key loaded:", "yes (masked)" if config.QWEN_API_KEY else "no")
    if errors:
        for error in errors:
            print("ERROR:", error)
        return 2
    if args.dry_run:
        print("CONFIG PASS (network call skipped)")
        return 0

    from openai import OpenAI

    client = OpenAI(
        api_key=config.QWEN_API_KEY,
        base_url=config.QWEN_BASE_URL,
        timeout=30,
        max_retries=1,
    )
    started = time.perf_counter()
    try:
        response = client.chat.completions.create(
            model=config.QWEN_MODEL,
            messages=[{"role": "user", "content": "Reply with exactly: CONNECTED"}],
            temperature=0,
            max_tokens=16,
        )
    except Exception as exc:
        # SDK exceptions can contain endpoints/status but should not contain the
        # key. Still redact defensively before printing.
        message = str(exc).replace(config.QWEN_API_KEY, "***")
        print("CONNECTION FAIL:", message[:500])
        return 1
    elapsed = time.perf_counter() - started
    text = (response.choices[0].message.content or "").strip()
    print(f"CONNECTION PASS ({elapsed:.2f}s):", text[:80])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
