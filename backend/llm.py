# -*- coding: utf-8 -*-
"""
LLM access layer.

- get_client(): an OpenAI-compatible client pointed at Alibaba Cloud DashScope
  (Bailian), used to call Qwen models. This is exactly how QwenPaw / Bailian
  expose Qwen, so the same code works on the competition's 百炼 credits.
- parse_request(): lightweight NLU used to seed constraints (date, budget,
  party size, interests, mobility) — also powers the offline demo brain.
"""
import re
import datetime as dt

import config
import kb

_client = None


def _detect_requested_pois(text):
    """Detect explicitly named POIs in the request (zh / en), so users can ask
    for specific places (e.g. 鄭家大屋)."""
    low = (text or "").lower()
    hits = []
    for p in kb.all_pois():
        names = [p["name"]["zh"], p["name"]["en"], p["name"].get("pt", "")]
        # also a short zh alias = drop bracketed part
        short = re.split(r"[（(]", p["name"]["zh"])[0]
        names.append(short)
        for nm in names:
            nm = (nm or "").strip()
            if len(nm) >= 2 and nm.lower() in low:
                hits.append(p["id"])
                break
    return hits


def get_client():
    global _client
    if not config.USE_REAL_LLM:
        return None
    if _client is None:
        from openai import OpenAI
        _client = OpenAI(api_key=config.DASHSCOPE_API_KEY, base_url=config.DASHSCOPE_BASE_URL)
    return _client


# --------------------------------------------------------------------------
# request parsing (shared by real + offline brains)
# --------------------------------------------------------------------------
_LANG_PATTERNS = [
    ("zh-HK", ["粵語", "廣東話", "广东话", "粤语", "cantonese"]),
    ("en", ["english", "英文", "英語"]),
    ("pt", ["português", "portugues", "葡文", "葡萄牙文", "葡語"]),
    ("ja", ["日文", "日語", "japanese", "日本語"]),
    ("zh", ["普通話", "普通话", "國語", "国语", "mandarin", "簡體", "简体"]),
]

_INTEREST_KEYS = ["歷史", "历史", "文化", "美食", "小食", "甜品", "老街", "舊區", "旧区",
                  "懷舊", "怀旧", "拍照", "打卡", "文青", "文創", "文创", "藝術", "艺术",
                  "親子", "亲子", "教堂", "廟", "庙", "購物", "购物", "手信", "自然",
                  "風景", "风景", "本地", "history", "food", "photo", "local", "culture",
                  "nature", "shopping", "art", "family"]

_DISTRICT_KEYS = {
    "central": ["中區", "中区", "大三巴", "議事亭", "议事亭", "新馬路", "新马路"],
    "inner_harbour": ["內港", "内港", "西灣", "西湾", "媽閣", "妈阁", "下環", "下环"],
    "taipa": ["氹仔", "凼仔", "官也街", "taipa"],
    "coloane": ["路環", "路环", "coloane", "黑沙"],
}


def _coerce_today(today):
    if today is None:
        return dt.date.today()
    if isinstance(today, dt.date):
        return today
    try:
        return dt.date.fromisoformat(str(today)[:10])
    except Exception:
        return dt.date.today()


def _resolve_date(text, today=None):
    """Resolve a date expression to an ISO date. Defaults to the coming Saturday."""
    today = _coerce_today(today)
    t = text.lower()
    # explicit YYYY-MM-DD
    m = re.search(r"(20\d{2})[-/.年](\d{1,2})[-/.月](\d{1,2})", text)
    if m:
        try:
            return dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3))).isoformat()
        except Exception:
            pass
    # M月D日
    m = re.search(r"(\d{1,2})\s*月\s*(\d{1,2})", text)
    if m:
        try:
            y = today.year
            d = dt.date(y, int(m.group(1)), int(m.group(2)))
            if d < today:
                d = dt.date(y + 1, int(m.group(1)), int(m.group(2)))
            return d.isoformat()
        except Exception:
            pass
    if any(k in text for k in ["今日", "今天", "today"]):
        return today.isoformat()
    if any(k in text for k in ["聽日", "听日", "明日", "明天", "tomorrow"]):
        return (today + dt.timedelta(days=1)).isoformat()
    if any(k in text for k in ["後日", "后日", "後天", "后天"]):
        return (today + dt.timedelta(days=2)).isoformat()
    # weekday names
    wd_map = {0: ["週一", "周一", "星期一", "禮拜一", "monday"],
              1: ["週二", "周二", "星期二", "禮拜二", "tuesday"],
              2: ["週三", "周三", "星期三", "禮拜三", "wednesday"],
              3: ["週四", "周四", "星期四", "禮拜四", "thursday"],
              4: ["週五", "周五", "星期五", "禮拜五", "friday"],
              5: ["週六", "周六", "星期六", "禮拜六", "saturday", "weekend", "週末", "周末"],
              6: ["週日", "周日", "星期日", "禮拜日", "星期天", "sunday"]}
    next_week = any(k in text for k in ["下週", "下周", "下個", "下个", "next"])
    for wd, keys in wd_map.items():
        if any(k in t for k in keys):
            days = (wd - today.weekday()) % 7
            if days == 0 or next_week:
                days += 7 if (days == 0 or next_week) else 0
                if days == 0:
                    days = 7
            return (today + dt.timedelta(days=days)).isoformat()
    # default: the coming Saturday
    days = (5 - today.weekday()) % 7 or 7
    return (today + dt.timedelta(days=days)).isoformat()


def _parse_days(text):
    low = (text or "").lower()
    cn = {"一": 1, "兩": 2, "两": 2, "二": 2, "三": 3, "四": 4, "五": 5}
    m = re.search(r"(\d+)\s*(?:日|天|day|days|dia|dias|泊)", low)
    if m:
        return max(1, min(int(m.group(1)), 5))
    for k, v in cn.items():
        if re.search(k + r"\s*(?:日|天)", text):
            return max(1, min(v, 5))
    if any(k in low for k in ["多日", "幾日", "几日", "multi-day", "multiday"]):
        return 3
    if any(k in text for k in ["過夜", "过夜", "兩日一夜", "两日一夜", "一晚"]):
        return 2
    return 1


def parse_request(text, override_lang=None, today=None):
    text = text or ""
    low = text.lower()
    today = _coerce_today(today)

    lang = override_lang
    if not lang:
        for code, pats in _LANG_PATTERNS:
            if any(p in low for p in pats):
                lang = code
                break
        lang = lang or "zh-HK"

    interests = []
    for k in _INTEREST_KEYS:
        if k in low and k not in interests:
            interests.append(k)
    if not interests:
        interests = ["歷史", "美食", "老街"]

    district = None
    for d, keys in _DISTRICT_KEYS.items():
        if any(k.lower() in low for k in keys):
            district = d
            break

    # party size
    people = 1
    m = re.search(r"(\d+)\s*(?:個|个|位)?\s*人", text)
    if m:
        people = int(m.group(1))
    elif any(k in text for k in ["爸媽", "爸妈", "父母", "屋企人", "家人"]):
        people = 3
    elif any(k in text for k in ["一家", "全家", "家庭"]):
        people = 4
    elif any(k in text for k in ["情侶", "情侣", "拍拖", "另一半", "couple", "女朋友", "男朋友"]):
        people = 2
    people = max(1, min(people, 12))

    # budget (total MOP); None if unspecified
    budget = None
    m = re.search(r"(?:mop|澳門元|澳门元|蚊|元|塊|块|hkd|港幣|港币)\s*\$?\s*(\d{2,5})", low)
    if not m:
        m = re.search(r"(\d{2,5})\s*(?:mop|澳門元|澳门元|蚊|元|塊|块|港幣|港币)", low)
    if m:
        budget = int(m.group(1))
    cheap = any(k in low for k in ["唔想太貴", "不想太贵", "平", "便宜", "經濟", "经济", "budget", "cheap"])

    low_walk = any(k in low for k in ["唔想行太多", "不想走太多", "行得少", "少走路", "腳痛", "脚痛",
                                      "唔想行太遠", "輪椅", "轮椅", "老人家", "長者", "长者",
                                      "行動不便", "行动不便", "唔想行咁多", "less walk", "easy walk"])

    half_day = any(k in low for k in ["半日", "半天", "half day", "幾個鐘", "几个钟", "兩三個鐘", "两三个钟"])

    start_min = 10 * 60
    if any(k in low for k in ["朝早", "一早", "早上", "上午", "morning", "9點", "9点", "九點", "九点"]):
        start_min = 9 * 60 + 30
    if any(k in low for k in ["下午", "afternoon", "晏晝", "晏昼", "2點", "2点", "下晝", "下昼"]):
        start_min = 14 * 60
        half_day = True

    return {
        "raw": text,
        "language": lang,
        "interests": interests,
        "district": district,
        "people": people,
        "budget": budget,
        "cheap": cheap,
        "low_walk": low_walk,
        "half_day": half_day,
        "days": _parse_days(text),
        "date": _resolve_date(text, today),
        "start_min": start_min,
        "requested_ids": _detect_requested_pois(text),
    }


LANG_NAME = {"zh-HK": "粵語（澳門）", "zh": "簡體中文", "en": "English",
             "pt": "Português", "ja": "日本語"}
