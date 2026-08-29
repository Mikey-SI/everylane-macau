# -*- coding: utf-8 -*-
"""阿濠讲古：千问男声 TTS，按需合成并落盘缓存。

竞赛 Token Plan 只保证列出 qwen-audio-3.0-tts-plus。这里按顺序尝试：
  1) DashScope HTTP SpeechSynthesizer（plus + 男声 longanlufeng）
  2) Qwen3-TTS HTTP（粤语男声 Rocky / 多语男声 Ethan）
  3) Token Plan WebSocket SpeechSynthesizer

成功路由会记住，后续点击不再盲试。缓存命中不消耗额度。
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import ssl
import socket
import struct
import threading
import time
import uuid

import httpx

import config
import kb

logger = logging.getLogger("everylane.tts")

CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "tts_cache")
MAX_CHARS = 600
SYNTH_TIMEOUT = 40.0
HTTP_TIMEOUT = httpx.Timeout(40.0, connect=6.0)
LANGS = ("zh-HK", "zh", "en", "pt", "ja")

INSTRUCTIONS = {
    "zh-HK": "请用粤语、亲切的澳门街坊男向导口吻讲述。语速稍慢，温暖自然，不要播音腔，像邻里阿濠讲古。",
    "zh": "请用普通话、亲切的本地男向导口吻讲述。语速稍慢，温暖自然，像邻里阿濠讲故事。",
    "en": "Speak as a warm Macau neighbourhood male guide. Slightly slow, friendly, not announcer-like.",
    "pt": "Fala como um guia macaense simpático, voz masculina, ritmo calmo e caloroso.",
    "ja": "親しみやすい澳門の男性ガイドとして、ややゆっくり、温かく自然に話してください。",
}
LANG_HINTS = {
    "zh-HK": ["zh"],
    "zh": ["zh"],
    "en": ["en"],
    "pt": ["pt"],
    "ja": ["ja"],
}
QWEN3_VOICE = {
    "zh-HK": "Rocky",
    "zh": "Ethan",
    "en": "Ethan",
    "pt": "Ethan",
    "ja": "Ethan",
}
QWEN3_LANG = {
    "zh-HK": "Chinese",
    "zh": "Chinese",
    "en": "English",
    "pt": "Portuguese",
    "ja": "Japanese",
}

_lock = threading.Lock()
_inflight = {}
_route = None  # (kind, url, model, extra)


class NotFound(Exception):
    pass


class Unavailable(Exception):
    pass


class SynthError(Exception):
    pass


def available() -> bool:
    return bool(config.QWEN_API_KEY)


def story_text(poi_id: str, lang: str) -> str:
    rec = kb.STORIES.get(poi_id) or {}
    if lang in rec and str(rec[lang]).strip():
        return str(rec[lang]).strip()
    order = {
        "zh-HK": ("zh-HK", "zh", "en"),
        "zh": ("zh", "zh-HK", "en"),
        "en": ("en", "zh-HK", "zh"),
        "pt": ("pt", "en", "zh-HK"),
        "ja": ("ja", "en", "zh-HK"),
    }.get(lang, ("en",))
    for key in order:
        text = str(rec.get(key) or "").strip()
        if text:
            return text
    return ""


def cache_path(poi_id: str, lang: str, text: str) -> str:
    digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]
    safe = re.sub(r"[^a-zA-Z0-9_-]+", "_", f"{poi_id}_{lang}_{digest}")
    return os.path.join(CACHE_DIR, safe + ".bin")


def sniff_mime(data: bytes) -> str:
    if data[:3] == b"ID3" or data[:2] in (b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"):
        return "audio/mpeg"
    if data[:4] == b"RIFF":
        return "audio/wav"
    if data[:4] == b"OggS":
        return "audio/ogg"
    if data[4:8] == b"ftyp":
        return "audio/mp4"
    return "audio/mpeg"


def _redact(text: str) -> str:
    key = config.QWEN_API_KEY or ""
    if key and key in text:
        text = text.replace(key, "***")
    return text[:400]


def _gateway_roots():
    base = (config.QWEN_BASE_URL or "").rstrip("/")
    host = re.sub(r"/compatible-mode/v1/?$", "", base).rstrip("/")
    china = "cn-beijing" in (host + base)
    extra = "https://dashscope.aliyuncs.com" if china else "https://dashscope-intl.aliyuncs.com"
    roots = []
    for item in (host, extra):
        if item and item not in roots:
            roots.append(item)
    return roots


def _headers():
    return {
        "Authorization": "Bearer " + config.QWEN_API_KEY,
        "Content-Type": "application/json",
    }


def _plus_body(text: str, lang: str) -> dict:
    return {
        "model": os.getenv("EL_TTS_MODEL", "qwen-audio-3.0-tts-plus").strip()
        or "qwen-audio-3.0-tts-plus",
        "input": {
            "text": text,
            "voice": os.getenv("EL_TTS_VOICE", "longanlufeng").strip() or "longanlufeng",
            "format": "mp3",
            "sample_rate": 24000,
            "rate": 0.88,
            "pitch": 0.96,
            "volume": 62,
            "instruction": INSTRUCTIONS.get(lang, INSTRUCTIONS["zh"]),
            "language_hints": LANG_HINTS.get(lang, ["zh"]),
        },
    }


def _qwen3_body(text: str, lang: str, instruct: bool) -> dict:
    payload = {
        "text": text,
        "voice": QWEN3_VOICE.get(lang, "Ethan"),
    }
    if lang != "zh-HK":
        payload["language_type"] = QWEN3_LANG.get(lang, "Chinese")
    if instruct:
        payload["instructions"] = INSTRUCTIONS.get(lang, INSTRUCTIONS["en"])
        payload["optimize_instructions"] = True
        return {"model": "qwen3-tts-instruct-flash", "input": payload}
    return {"model": "qwen3-tts-flash", "input": payload}


def _audio_from_json(parsed: dict) -> str:
    output = parsed.get("output") or {}
    audio = output.get("audio") or {}
    url = audio.get("url") or ""
    if url:
        return url
    choices = output.get("choices") or parsed.get("choices") or []
    if choices:
        msg = (choices[0] or {}).get("message") or {}
        audio = msg.get("audio") or {}
        return audio.get("url") or audio.get("data") or ""
    return ""


def _download(url: str) -> bytes:
    with httpx.Client(timeout=httpx.Timeout(25.0, connect=6.0), follow_redirects=True) as client:
        resp = client.get(url)
        resp.raise_for_status()
        data = resp.content or b""
    if len(data) < 64:
        raise SynthError("audio too small")
    return data


def _post_speech(url: str, body: dict) -> bytes:
    with httpx.Client(timeout=HTTP_TIMEOUT, follow_redirects=True) as client:
        resp = client.post(url, headers=_headers(), json=body)
        raw = resp.content or b""
        ctype = (resp.headers.get("content-type") or "").lower()
        if resp.status_code >= 400:
            raise SynthError(f"HTTP {resp.status_code} {_redact(raw.decode('utf-8', 'replace'))}")
        if "audio/" in ctype or raw[:3] == b"ID3" or raw[:4] == b"RIFF":
            if len(raw) < 64:
                raise SynthError("audio too small")
            return raw
        try:
            parsed = json.loads(raw.decode("utf-8"))
        except Exception as exc:
            raise SynthError("non-json tts response") from exc
        if parsed.get("code") and str(parsed.get("code")) not in ("", "200", "null"):
            raise SynthError(_redact(str(parsed.get("message") or parsed.get("code"))))
        audio_ref = _audio_from_json(parsed)
        if audio_ref.startswith("http://") or audio_ref.startswith("https://"):
            return _download(audio_ref)
        if audio_ref and not audio_ref.startswith("http"):
            import base64
            data = base64.b64decode(audio_ref)
            if len(data) >= 64:
                return data
        raise SynthError("tts json had no audio")


def _ws_send(sock, payload: bytes, opcode: int = 0x1):
    header = bytearray([0x80 | opcode])
    n = len(payload)
    mask_bit = 0x80
    if n < 126:
        header.append(mask_bit | n)
    elif n < 65536:
        header.append(mask_bit | 126)
        header.extend(struct.pack("!H", n))
    else:
        header.append(mask_bit | 127)
        header.extend(struct.pack("!Q", n))
    mask = os.urandom(4)
    header.extend(mask)
    masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
    sock.sendall(header + masked)


def _ws_recv_frame(sock, buf: bytearray):
    def need(n):
        while len(buf) < n:
            chunk = sock.recv(4096)
            if not chunk:
                raise SynthError("ws closed")
            buf.extend(chunk)

    need(2)
    b0, b1 = buf[0], buf[1]
    opcode = b0 & 0x0F
    masked = b1 & 0x80
    length = b1 & 0x7F
    idx = 2
    if length == 126:
        need(4)
        length = struct.unpack("!H", bytes(buf[2:4]))[0]
        idx = 4
    elif length == 127:
        need(10)
        length = struct.unpack("!Q", bytes(buf[2:10]))[0]
        idx = 10
    if masked:
        need(idx + 4 + length)
        mask = bytes(buf[idx:idx + 4])
        idx += 4
        data = bytes(buf[idx:idx + length][i] ^ mask[i % 4] for i in range(length))
        idx += length
    else:
        need(idx + length)
        data = bytes(buf[idx:idx + length])
        idx += length
    del buf[:idx]
    return opcode, data


def _ws_handshake(host: str, path: str):
    raw = socket.create_connection((host, 443), timeout=SYNTH_TIMEOUT)
    ctx = ssl.create_default_context()
    sock = ctx.wrap_socket(raw, server_hostname=host)
    sock.settimeout(SYNTH_TIMEOUT)
    nonce = __import__("base64").b64encode(os.urandom(16)).decode()
    req = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"Upgrade: websocket\r\n"
        f"Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {nonce}\r\n"
        f"Sec-WebSocket-Version: 13\r\n"
        f"Authorization: Bearer {config.QWEN_API_KEY}\r\n"
        f"\r\n"
    )
    sock.sendall(req.encode())
    buf = b""
    while b"\r\n\r\n" not in buf:
        chunk = sock.recv(4096)
        if not chunk:
            raise SynthError("ws handshake closed")
        buf += chunk
    head = buf.split(b"\r\n\r\n", 1)[0]
    status = head.split(b"\r\n", 1)[0].decode("utf-8", "replace")
    if "101" not in status:
        sock.close()
        raise SynthError("ws " + status[:120])
    leftover = buf.split(b"\r\n\r\n", 1)[1]
    return sock, bytearray(leftover)


def _ws_synth(text: str, lang: str) -> bytes:
    host = "token-plan.ap-southeast-1.maas.aliyuncs.com"
    base = (config.QWEN_BASE_URL or "")
    if "cn-beijing" in base:
        host = "token-plan.cn-beijing.maas.aliyuncs.com"
    sock, buf = _ws_handshake(host, "/api-ws/v1/inference")
    chunks = []
    task_id = str(uuid.uuid4())
    model = os.getenv("EL_TTS_MODEL", "qwen-audio-3.0-tts-plus").strip() or "qwen-audio-3.0-tts-plus"
    voice = os.getenv("EL_TTS_VOICE", "longanlufeng").strip() or "longanlufeng"
    run_task = {
        "header": {"action": "run-task", "task_id": task_id, "streaming": "duplex"},
        "payload": {
            "task_group": "audio",
            "task": "tts",
            "function": "SpeechSynthesizer",
            "model": model,
            "parameters": {
                "text_type": "PlainText",
                "voice": voice,
                "format": "mp3",
                "sample_rate": 24000,
                "volume": 62,
                "rate": 0.88,
                "pitch": 0.96,
                "instruction": INSTRUCTIONS.get(lang, INSTRUCTIONS["zh"]),
                "language_hints": LANG_HINTS.get(lang, ["zh"]),
            },
            "input": {},
        },
    }
    try:
        _ws_send(sock, json.dumps(run_task).encode("utf-8"))
        sent = False
        deadline = time.time() + SYNTH_TIMEOUT
        while time.time() < deadline:
            opcode, data = _ws_recv_frame(sock, buf)
            if opcode in (0x8,):
                break
            if opcode == 0x9:
                _ws_send(sock, data, opcode=0xA)
                continue
            if opcode == 0x2:
                chunks.append(data)
                continue
            if opcode != 0x1:
                continue
            msg = json.loads(data.decode("utf-8", "replace") or "{}")
            event = ((msg.get("header") or {}).get("event") or "")
            if event == "task-started" and not sent:
                cont = {
                    "header": {"action": "continue-task", "task_id": task_id, "streaming": "duplex"},
                    "payload": {"input": {"text": text}},
                }
                _ws_send(sock, json.dumps(cont).encode("utf-8"))
                fin = {
                    "header": {"action": "finish-task", "task_id": task_id, "streaming": "duplex"},
                    "payload": {"input": {}},
                }
                time.sleep(0.2)
                _ws_send(sock, json.dumps(fin).encode("utf-8"))
                sent = True
            elif event == "task-failed":
                err = (msg.get("header") or {}).get("error_message") or msg
                raise SynthError(_redact(str(err)))
            elif event == "task-finished":
                break
        audio = b"".join(chunks)
        if len(audio) < 64:
            raise SynthError("ws produced no audio")
        return audio
    finally:
        try:
            sock.close()
        except Exception:
            pass


def _plans(text: str, lang: str):
    plus = _plus_body(text, lang)
    q3 = _qwen3_body(text, lang, False)
    q3i = _qwen3_body(text, lang, True)
    plans = []
    for root in _gateway_roots():
        plans.append(("speech", root + "/api/v1/services/audio/tts/SpeechSynthesizer", plus))
        plans.append(("qwen3", root + "/api/v1/services/aigc/multimodal-generation/generation", q3))
        plans.append(("qwen3i", root + "/api/v1/services/aigc/multimodal-generation/generation", q3i))
        plans.append((
            "openai",
            root + "/compatible-mode/v1/audio/speech",
            {"model": plus["model"], "input": text, "voice": plus["input"]["voice"]},
        ))
    plans.append(("ws", "wss://token-plan/api-ws/v1/inference", plus))
    return plans


def synthesize(text: str, lang: str) -> bytes:
    global _route
    text = (text or "").strip()
    if not text:
        raise NotFound()
    if len(text) > MAX_CHARS:
        text = text[: MAX_CHARS - 1] + "…"
    if not available():
        raise Unavailable()

    errors = []
    if _route:
        kind, url, body = _route
        try:
            if kind == "ws":
                return _ws_synth(text, lang)
            return _post_speech(url, _swap_text(body, text, lang, kind))
        except Exception as exc:
            logger.warning("cached tts route failed: %s", _redact(str(exc)))
            errors.append(str(exc))
            _route = None

    for kind, url, body in _plans(text, lang):
        try:
            if kind == "ws":
                data = _ws_synth(text, lang)
            else:
                data = _post_speech(url, body)
            _route = (kind, url, body)
            logger.info("tts route ok kind=%s", kind)
            return data
        except Exception as exc:
            errors.append(_redact(f"{kind}:{exc}"))
            continue
    raise SynthError("; ".join(errors[-6:]) or "no tts route")


def _swap_text(body: dict, text: str, lang: str, kind: str) -> dict:
    if kind == "speech":
        return _plus_body(text, lang)
    if kind == "qwen3":
        return _qwen3_body(text, lang, False)
    if kind == "qwen3i":
        return _qwen3_body(text, lang, True)
    if kind == "openai":
        voice = body.get("voice") or (body.get("input") or {}).get("voice") or "longanlufeng"
        return {"model": body.get("model"), "input": text, "voice": voice}
    return body


def ensure_audio(poi_id: str, lang: str):
    if lang not in LANGS:
        lang = "zh-HK"
    text = story_text(poi_id, lang)
    if not text:
        raise NotFound()
    path = cache_path(poi_id, lang, text)
    if os.path.isfile(path) and os.path.getsize(path) > 64:
        data = open(path, "rb").read()
        return data, sniff_mime(data)

    key = path
    with _lock:
        ev = _inflight.get(key)
        if ev is None:
            ev = threading.Event()
            _inflight[key] = ev
            owner = True
        else:
            owner = False
    if not owner:
        ev.wait(SYNTH_TIMEOUT + 5)
        if os.path.isfile(path) and os.path.getsize(path) > 64:
            data = open(path, "rb").read()
            return data, sniff_mime(data)
        raise SynthError("tts wait failed")

    try:
        data = synthesize(text, lang)
        os.makedirs(CACHE_DIR, exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "wb") as fh:
            fh.write(data)
        os.replace(tmp, path)
        return data, sniff_mime(data)
    finally:
        ev.set()
        with _lock:
            _inflight.pop(key, None)


def probe():
    """Short live check. Prints status only — never the key."""
    sample = "阿濠同你讲古，今日带你行澳门老街。"
    print("TTS probe key=", bool(config.QWEN_API_KEY), "base=", config.QWEN_BASE_URL)
    try:
        data = synthesize(sample, "zh-HK")
        print("OK bytes", len(data), "mime", sniff_mime(data), "route", None if not _route else _route[0])
        return True
    except Exception as exc:
        print("FAIL", _redact(str(exc)))
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    raise SystemExit(0 if probe() else 1)
