# -*- coding: utf-8 -*-
"""Generate the semifinal Practice Article.

The official rubric gives this article 20%, so it documents the implemented
system, evidence, limitations and AI ethics instead of repeating pitch copy.
"""
import os
from docstyle import (new_doc, para, runs, h1, h2, bullet, table,
                      image, page_break,
                      TERRA, AZUL, INK, GOLD, GREY, CENTER)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("PRACTICE_DOC_OUT", os.path.join(HERE, "實踐文章_街知巷聞_EveryLaneMacau.docx"))
ASSET_DIR = os.path.join(HERE, "assets")
doc = new_doc()

# title
para(doc, "「千模百煉」AI 開發者系列之學生競賽 · 複賽實踐文章", 11, GREY, align=CENTER, after=2)
para(doc, "街知巷聞 · EveryLane Macau", 24, TERRA, bold=True, align=CENTER, after=2)
para(doc, "把 AI 由「問答」做成「做任務」——一個會將遊客導流入舊區老街的澳門深度遊智能體",
     12, INK, bold=True, align=CENTER, after=2)
para(doc, "隊伍：愛拼才會贏　·　參賽者：施天益（SITINIEK，學號 dc227126）　·　2026-09-01",
     9.5, GREY, align=CENTER, after=10)

# abstract
h2(doc, "摘要")
para(doc, "本作品以 QwenPaw 2.0.0、qwen3.7-plus、專用 Skill 與 stdio MCP 實作可直接使用的"
     "「街知巷聞」澳門深度遊智能體。它以 ReAct 迴圈規劃、調用 7 種工具、多步執行並失敗恢復；"
     "核心創新是把遊客由熱門點導向舊區與本地商戶。複賽進一步把推薦做成可歸因閉環："
     "加入實時天氣、70/70 POI 無障礙資料、一次性到店碼、酒店/旅行社 API、成效儀表板、"
     "70 站五語講古男聲及可審計數據口徑。"
     "公網、工具軌跡、核銷流程與測試均可由評審親手驗證。")
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
h1(doc, "三、", "系統架構（實際部署 QwenPaw Skill + MCP）")
table(doc, [
    ["層", "本作品實作", "對應 QwenPaw"],
    ["接入層", "瀏覽器 SPA + Server-Sent Events 實時串流", "頻道接入層"],
    ["運行時", "QwenPaw 2.0 Console + FastAPI /api/plan SSE", "Agent 運行時"],
    ["智能體核心", "EveryLane Skill + Plan Mode + ReAct + 失敗恢復", "QwenPaw Agent / Skills"],
    ["能力層", "stdio MCP：7 種工具 + 1 個流程比較工具", "MCP 工具層"],
    ["模型層", "Token Plan qwen3.7-plus 真實 function calling + 逾時保護", "模型供應商 / 路由"],
    ["成效層", "到店碼、B 端 API、匿名化成效儀表板、證據 JSON", "可歸因產品閉環"],
], widths=[1.1, 3.4, 2.0], head_fill="2C5E86")
image(doc, os.path.join(ASSET_DIR, "qwenpaw", "03_everylane_mcp_connected.png"),
      "QwenPaw 中 EveryLane Macau Tools MCP 客戶端已實際連接", width=6.35, after=8)

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
h2(doc, "真實 Qwen + 可重現工具鏈（穩健且透明）")
para(doc, "正式單日自訂問題由 qwen3.7-plus function calling 驅動；每次運行在軌跡與結果徽章中標明"
     "「真實 Qwen」「可重現工具鏈」或「Qwen 逾時後工具鏈接管」，不把回退冒充模型推理。"
     "OpenAI SDK 的預設 600 秒等待已改為 45 秒單次逾時、110 秒整體時間預算及零隱式重試；"
     "供應商受限時自動使用同一知識庫與 7 項工具完整產出。另設「90 秒評審快速演示」，"
     "透明使用確定性工具鏈重現休息日改線與舊區導流。Key 只存於 Git 忽略的 .env。")

# 5
h1(doc, "五、", "數據與真實性")
bullet(doc, "Wikipedia / Wikimedia Commons 公開資料的坐標與相片；人手整理 70 個 POI 的開放、費用、舊區/商戶與無障礙資料。", "真實資料　")
bullet(doc, "Open-Meteo 實時預報（30 分鐘快取、2.5 秒逾時）；不可用或超出預報期時回退季節模型，結果以 source 欄位明示。", "實時資料　")
bullet(doc, "步行以坐標距離加舊城巷道係數估算；人流為時段模型，不宣稱為官方即時資料，介面提醒以現場為準。", "估算資料　")
bullet(doc, "複賽可用性、轉化累計、區域熱度與校正樣本為賽規允許的確定性示範數據；頁面、API 與文檔均標註，種子、公式與來源檔可由 /api/impact/evidence 下載。", "示範資料　")
image(doc, os.path.join(ASSET_DIR, "semifinal", "01_dashboard_kpi.png"),
      "複賽成效儀表板：指標呈現與「示範數據」標註同屏，避免誤導", width=6.35, after=8)

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
para(doc, "在不同興趣、人數、預算、日期與語言的回歸場景中，智能體能輸出開放時間已核驗、"
     "同區順路、預算可控的深度遊行程；遇休息日會換點，人潮擁擠會導向鄰近老街。"
     "真實 Qwen 延遲取決於供應商，因此不再宣稱「數秒」；現場快速模式以同一工具鏈在 90 秒內完成。"
     "每份行程附任務核對、引流歸因、無障礙徽章與到店碼入口。")
image(doc, os.path.join(ASSET_DIR, "route_map.png"),
      "結果頁路線：真實地圖、站點順序與步行導覽，讓評審可即時驗證", width=6.35, after=8)
image(doc, os.path.join(ASSET_DIR, "semifinal", "05_itinerary_access_code.png"),
      "公網實拍：工具軌跡、無障礙標註與一次性到店碼形成可操作閉環", width=6.35, after=8)

h1(doc, "八、", "複賽閉環與工程驗證")
bullet(doc, "行程頁領碼 → 商戶側核銷 → 第二次核銷被拒；流程真實、有狀態且不收集個人資料。", "到店碼　")
bullet(doc, "POST /api/v1/itinerary 以 X-API-Key 鑑權，返回時間軸、預算、無障礙與舊區歸因，供酒店/旅行社嵌入。", "B 端 API　")
bullet(doc, "成效頁把實時系統狀態與示範 KPI 分欄；/api/impact/evidence 匯出公式、數據類別、種子、來源與核驗端點。", "可審計　")
bullet(doc, "70 個景點均有粵語、普通話、英語、葡語、日語講古；簡體中文固定普通話男聲，不回退粵語。", "五語講古　")
bullet(doc, "後端 647 項、瀏覽器 127 項、API/安全 116 項、倉庫交付 109 項及 8 個 MCP 協議測試全部通過。", "測試　")
image(doc, os.path.join(ASSET_DIR, "semifinal", "04_dashboard_redeem.png"),
      "一次性到店碼：真實發碼與核銷；重複使用立即被拒", width=6.35, after=8)

# 9
h1(doc, "九、", "商業模式與可持續性")
bullet(doc, "商戶精選訂閱 / 引流分成（按帶客量計費）；", "B 端　")
bullet(doc, "酒店、旅行社、航空白標 API 授權；", "渠道　")
bullet(doc, "為文旅局提供客流分佈與舊區活化數據儀表板；", "政府　")
bullet(doc, "多語言（普通話 / 英 / 葡 / 日）擴展內地與國際客群。", "增長　")

# 10
h1(doc, "十、", "AI 倫理")
bullet(doc, "行程由 AI 生成、人流為估算值，介面明確標示，提醒以現場為準；", "透明　")
bullet(doc, "關鍵事實基於知識庫，模型不得杜撰、不超範圍亂答；", "準確　")
bullet(doc, "刻意把流量導向資源較弱的舊區小店，促進可持續而非加劇集中；", "公平　")
bullet(doc, "不收集個人身分資料、免登入；相片採公開授權並標註來源。", "私隱與版權　")

# 11
h1(doc, "十一、", "限制與下一步")
bullet(doc, "商戶、可用性與人流觀測目前按賽規使用示範數據；下一步需取得商戶書面同意並做真實小樣本 A/B 試點。", "實證限制　")
bullet(doc, "步行路線目前為坐標估算而非逐路口導航；下一步接入官方道路網/無障礙路徑 API。", "路線限制　")
bullet(doc, "到店碼是可操作原型，正式商用需商戶帳號、權限分層、限流、結算與審計日誌。", "商用限制　")
bullet(doc, "引入 QwenPaw 定時任務與經同意的偏好記憶，主動推送舊區活動；所有個人化採最小化與可撤回原則。", "產品下一步　")

para(doc, "結語：Qwen 與 QwenPaw 讓「諗到」就能「做到」——我們把對澳門舊區的關懷，"
     "變成一個真正幫到遊客同街坊的智能體。", bold=True, color=TERRA, before=8)
para(doc, "— 完 —", align=CENTER, color=GREY, before=10)

doc.save(OUT)
print("Saved:", OUT)
