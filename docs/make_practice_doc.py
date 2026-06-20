# -*- coding: utf-8 -*-
"""Generate the Practice Article (實踐文章) — design思路, 實作, 成效, AI 倫理."""
import os
from docstyle import (new_doc, para, runs, h1, h2, bullet, table,
                      image, page_break,
                      TERRA, AZUL, INK, GOLD, GREY, CENTER)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "實踐文章_街知巷聞_EveryLaneMacau.docx")
ASSET_DIR = os.path.join(HERE, "assets")
doc = new_doc()

# title
para(doc, "「千模百煉」AI 開發者系列之學生競賽 · 實踐文章", 11, GREY, align=CENTER, after=2)
para(doc, "街知巷聞 · EveryLane Macau", 24, TERRA, bold=True, align=CENTER, after=2)
para(doc, "把 AI 由「問答」做成「做任務」——一個會將遊客導流入舊區老街的澳門深度遊智能體",
     12, INK, bold=True, align=CENTER, after=2)
para(doc, "參賽者：SITINIEK（學號 dc227126）　·　方向：澳門文旅 × 舊區活化　·　2026 年",
     9.5, GREY, align=CENTER, after=10)

# abstract
h2(doc, "摘要")
para(doc, "本作品基於阿里雲 Qwen 千問大模型與 QwenPaw 智能體理念，實作了一個可直接運行的網站"
     "「街知巷聞」。它不是聊天機械人，而是一個會規劃、調用 7 種工具、多步執行並能失敗自動恢復的"
     "ReAct 智能體（人設「阿濠」）。其核心創新是「舊區導流引擎」：在為遊客生成個人化深度遊行程時，"
     "主動把人流由大三巴、議事亭等熱點，分流到福隆新街、十月初五街等舊區老街與本地老字號，"
     "形成遊客、小店、城市三方共贏的商業模式。全程於網頁實時可視化，結果可逐項驗證。")
image(doc, os.path.join(ASSET_DIR, "product_hero.png"),
      "產品首頁：以澳門舊城色系建立文旅與舊區活化的視覺記憶", width=6.35, after=10)

# 1
h1(doc, "一、", "背景與問題")
para(doc, "澳門是世界級旅遊城市，但客流高度集中於少數熱點，舊區老街與街坊小店卻日漸凋零。"
     "這同時造成遊客體驗下降、社區文化流失、旅遊承載失衡三重問題。我們認為，AI 智能體最適合"
     "解決這種「資訊整合 + 動態決策 + 流量再分配」的任務。")

# 2
h1(doc, "二、", "設計思路")
h2(doc, "為何選「導流」定位？")
para(doc, "賽事評分重「應用創新性」與「實際價值」。市面上的行程規劃多以熱門景點為中心，"
     "我們反其道而行，以「把遊客帶入舊區」為核心目標，既差異化，又同時命中文旅與舊區活化兩條賽道，"
     "且具清晰商業價值（為小店帶客流）。")
h2(doc, "為何要做成「智能體」而非問答？")
para(doc, "賽事評分中「任務完成度（30%）」與「智能體能力（20%）」合佔一半，明確要求規劃、工具調用、"
     "多步執行與失敗恢復。因此我們把規劃做成真正的 ReAct 迴圈，並讓每一個結論都由工具計算得出、可驗證，"
     "而非由模型空泛生成。")

# 3
h1(doc, "三、", "系統架構（對標 QwenPaw 五層）")
table(doc, [
    ["層", "本作品實作", "對應 QwenPaw"],
    ["接入層", "瀏覽器 SPA + Server-Sent Events 實時串流", "頻道接入層"],
    ["運行時", "FastAPI 應用，/api/plan 串流端點", "Agent 運行時 / FastAPI app"],
    ["智能體核心", "ReAct 迴圈（思考-行動-觀察）+ 失敗恢復", "QwenPawAgent / ReAct 核心"],
    ["能力層", "7 種工具，統一 function-calling schema", "工具 / Toolkit / MCP"],
    ["模型層", "Qwen（百煉 OpenAI 相容）/ 離線雙腦", "雲端模型供應商 / 模型路由"],
], widths=[1.1, 3.4, 2.0], head_fill="2C5E86")

# 4
page_break(doc)
h1(doc, "四、", "智能體實作")
h2(doc, "ReAct 迴圈與工具")
para(doc, "智能體以 Qwen 的 function calling 驅動「思考 → 調用工具 → 觀察結果 → 再決策」迴圈，"
     "直至呼叫 submit_itinerary 提交結構化行程。七種工具：")
table(doc, [
    ["工具", "作用"],
    ["search_attractions", "按興趣 / 地區 / 偏好檢索景點知識庫（可優先舊區小店）"],
    ["get_weather", "查當日天氣，決定室內 / 室外比重"],
    ["check_opening", "核實景點當日是否開放（休息日 → 觸發失敗恢復）"],
    ["predict_crowd", "預測指定時段人流，過於擁擠時建議替代點"],
    ["find_local_gem", "給定熱點，返回鄰近寧靜的舊區老街 / 本地小店（導流核心）"],
    ["compute_route", "最近鄰排序計算步行路線與總距離 / 時間"],
    ["estimate_budget", "按人數估算門票 + 餐飲總開支"],
], widths=[1.9, 4.4], head_fill="BE4A3A")
h2(doc, "失敗恢復（Failure Recovery）")
para(doc, "智能體會主動處理三類「失敗 / 衝突」，而非卡住：")
bullet(doc, "景點當日休息 → 於同片區自動改揀有開、同類的替代點；", "休息日　")
bullet(doc, "熱點正午極擁擠 → 透過 find_local_gem 加插鄰近寧靜老街分流；", "人潮衝突　")
bullet(doc, "預算超支 / 步行太遠 → 自動剔除最貴的非必要收費點、縮減最遠站點。", "預算與距離　")
image(doc, os.path.join(ASSET_DIR, "agent_trace.png"),
      "智能體實時軌跡：核實開放時間後發現鄭家大屋休息，並自動改線", width=3.55, after=8)
h2(doc, "在線 / 離線雙腦（穩健性設計）")
para(doc, "設定百煉 API Key 時由真實 Qwen 驅動；未設定時切換到「離線示範引擎」——它調用同一套真實工具、"
     "用同一份真實數據完成規劃與失敗恢復，確保網站任何環境都能完整演示，亦避免路演時受網絡影響。"
     "二者共用同一個確定性「行程組裝器」，保證輸出穩定可驗證。")

# 5
h1(doc, "五、", "數據與真實性")
bullet(doc, "以程式抓取 Wikipedia / Wikimedia Commons 的真實坐標與相片（公開授權），坐標用於真實步行距離計算；", "來源　")
bullet(doc, "人手整理 70 個景點的開放時間、休息日、費用、人流特徵、舊區 / 本地小店標記；", "校正　")
bullet(doc, "天氣與人流以季節 / 時段模型估算並於介面明確標示，預留接入真實 API 的接口。", "估算　")

# 6
h1(doc, "六、", "關鍵難點與解法")
table(doc, [
    ["難點", "解法"],
    ["跨島亂跑、步行路線不合理", "鎖定單一可步行片區（半島歷史城區 / 氹仔 / 路環），最近鄰排序 + 以地標為起點"],
    ["熱點永遠被推薦，導流無從談起", "明確建模 hotspot 與 crowd_base，並以 find_local_gem 提供鄰近替代，主動寫入 diversions"],
    ["模型輸出不穩定、難驗證", "工具負責計算事實，模型只負責決策；最終由確定性組裝器產出時間軸與『任務完成核對』面板"],
], widths=[2.2, 4.1], head_fill="2C5E86")

# 7
h1(doc, "七、", "應用效果")
para(doc, "在多種情境（不同興趣 / 人數 / 預算 / 日期 / 語言）測試下，智能體均能於數秒內輸出"
     "開放時間正確、路線順路（半島行程全程多在 1–3 公里）、預算可控的深度遊行程，"
     "每次平均納入 3 個以上舊區老街 / 本地小店，並穩定觸發人潮導流；遇休息日能自動改線。"
     "每份行程附「任務完成核對」面板，逐項標示是否達成（預算、步行、開放、避開人潮、帶旺舊區）。")
image(doc, os.path.join(ASSET_DIR, "route_map.png"),
      "結果頁路線：真實地圖、站點順序與步行導覽，讓評審可即時驗證", width=6.35, after=8)

# 8
h1(doc, "八、", "商業模式與可持續性")
bullet(doc, "商戶精選訂閱 / 引流分成（按帶客量計費）；", "B 端　")
bullet(doc, "酒店、旅行社、航空白標 API 授權；", "渠道　")
bullet(doc, "為文旅局提供客流分佈與舊區活化數據儀表板；", "政府　")
bullet(doc, "多語言（普通話 / 英 / 葡 / 日）擴展內地與國際客群。", "增長　")

# 9
h1(doc, "九、", "AI 倫理")
bullet(doc, "行程由 AI 生成、人流為估算值，介面明確標示，提醒以現場為準；", "透明　")
bullet(doc, "關鍵事實基於知識庫，模型不得杜撰、不超範圍亂答；", "準確　")
bullet(doc, "刻意把流量導向資源較弱的舊區小店，促進可持續而非加劇集中；", "公平　")
bullet(doc, "不收集個人身分資料、免登入；相片採公開授權並標註來源。", "私隱與版權　")

# 10
h1(doc, "十、", "未來工作")
para(doc, "現已擴充至 70 個景點並支援 2–5 日多日行程；下一步可接入真實天氣 / 人流 API 與地圖步行導航；"
     "上線商戶端（精選商戶、引流統計、優惠券核銷）；引入 QwenPaw 的定時任務與記憶能力，"
     "做到「主動推送舊區活動 / 限定美食」與「越用越懂你」的個人化。")

para(doc, "結語：Qwen 與 QwenPaw 讓「諗到」就能「做到」——我們把對澳門舊區的關懷，"
     "變成一個真正幫到遊客同街坊的智能體。", bold=True, color=TERRA, before=8)
para(doc, "— 完 —", align=CENTER, color=GREY, before=10)

doc.save(OUT)
print("Saved:", OUT)
