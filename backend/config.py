# -*- coding: utf-8 -*-
"""Central configuration. Reads .env if present."""
import os

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))
except Exception:
    pass

# --- Qwen / DashScope (Alibaba Cloud Bailian) -----------------------------
# DashScope exposes an OpenAI-compatible endpoint, so we use the openai SDK.
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "").strip()
DASHSCOPE_BASE_URL = os.getenv(
    "DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"
).strip()
# Planner model (strong reasoning + tool calling). qwen-plus is a good balance.
QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen-plus").strip()

# If no key is configured we run a fully-functional OFFLINE demo (mock LLM),
# so the website always runs and demonstrates the full agentic flow.
USE_REAL_LLM = bool(DASHSCOPE_API_KEY)

# Agent loop safety limits (mirrors QwenPaw's "Agent 迭代次数管理")
MAX_AGENT_STEPS = int(os.getenv("MAX_AGENT_STEPS", "12"))

APP_TITLE = "街知巷聞 · EveryLane Macau"
