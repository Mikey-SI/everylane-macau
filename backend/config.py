# -*- coding: utf-8 -*-
"""Central configuration. Reads .env if present."""
import os

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))
except Exception:
    pass

# --- Qwen / QwenPaw / OpenAI-compatible providers -------------------------
# Competition Token Plan keys (sk-sp-...) are NOT interchangeable with normal
# DashScope keys.  Generic QWEN_* names support either provider while the old
# DASHSCOPE_* names remain backwards-compatible.
QWEN_API_KEY = os.getenv(
    "QWEN_API_KEY", os.getenv("DASHSCOPE_API_KEY", "")
).strip()
QWEN_BASE_URL = os.getenv(
    "QWEN_BASE_URL",
    os.getenv(
        "DASHSCOPE_BASE_URL",
        "https://dashscope.aliyuncs.com/compatible-mode/v1",
    ),
).strip()
# Token Plan: qwen3.7-plus has strong reasoning + function calling.
# Pay-as-you-go DashScope users can override this with qwen-plus, etc.
QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen3.7-plus").strip()

# Backwards-compatible aliases used by earlier code and external scripts.
DASHSCOPE_API_KEY = QWEN_API_KEY
DASHSCOPE_BASE_URL = QWEN_BASE_URL

# If no key is configured we run a fully-functional OFFLINE demo (mock LLM),
# so the website always runs and demonstrates the full agentic flow.
USE_REAL_LLM = bool(QWEN_API_KEY)

# Agent loop safety limits (mirrors QwenPaw's "Agent 迭代次数管理")
MAX_AGENT_STEPS = int(os.getenv("MAX_AGENT_STEPS", "12"))

APP_TITLE = "街知巷聞 · EveryLane Macau"
