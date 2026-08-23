# -*- coding: utf-8 -*-
"""Generate the 複賽說明文檔 (semifinal explanation document).

Maps every semifinal requirement and every proposal target to where the judge
can verify it on the deployed product, and documents which data is real vs
simulated (the semifinal rules explicitly allow simulated data as long as the
presented effect meets the proposal targets)."""
import os

from docstyle import (AZUL, CENTER, GOLD, GREY, INK, TERRA, bullet, h1, h2,
                      image, new_doc, page_break, para, runs, table)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "複賽說明文檔_街知巷聞.docx")
ASSETS = os.path.join(HERE, "assets", "semifinal")

SITE = "http://47.79.228.128/"
DASH = "http://47.79.228.128/dashboard.html"
APIDOC = "http://47.79.228.128/api.html"
REPO = "https://github.com/Mikey-SI/everylane-macau"
PAGES = "https://mikey-si.github.io/everylane-macau/"

doc = new_doc()

# ---------------------------------------------------------------- cover
para(doc, "「千模百煉」AI 開發者系列學生競賽 · 複賽", size=13, color=AZUL, bold=True, align=CENTER, before=6)
para(doc, "複賽說明文檔", size=26, color=TERRA, bold=True, align=CENTER, after=2)
para(doc, "街知巷聞 EveryLane Macau — 澳門深度遊 AI 智能體", size=13, bold=True, align=CENTER, after=2)
para(doc, "已部署、可實際使用；計劃書指標逐項呈現，可線上核驗", size=10.5, color=GREY, align=CENTER, after=10)

table(doc, [
    ["項目", "內容"],
    ["比賽階段", "複賽（提交截止 2026-09-02 23:59）"],
    ["公網作品（真實 Qwen）", SITE],
    ["成效儀表板（複賽新增）", DASH],
    ["B 端 API 文檔（複賽新增）", APIDOC],
    ["代碼倉庫（GitHub）", REPO],
    ["靜態備用演示", PAGES],
    ["團隊 / 成員", "愛拼才會贏 · 施天益（SI TIN IEK，學號 dc227126）"],
    ["文檔日期", "2026 年 8 月 23 日"],
], widths=[1.75, 5.05], header=False)

para(doc, "", after=2)

# ------------------------------------------------- 1. semifinal requirement
h1(doc, "一、", "複賽要求逐項對照")
table(doc, [
    ["複賽官方要求", "本作品對應", "核驗方式"],
    ["完成部署可實際使用的作品",
     "公網 24 小時運行：真實 qwen3.7-plus 推理、五語言、單日/多日規劃、地圖時間軸、PDF 匯出",
     f"直接使用 {SITE}（無需登入）"],
    ["呈現效果須達到計劃書的指標",
     "計劃書第七章「晉級後驗證目標」與時間表第 1/2 階段全部落地為可操作功能與儀表板",
     "本文檔第二、三章 + 成效儀表板逐項對照"],
    ["數據可以不用真實",
     "試點成效數據為示範數據並在頁面明確標註；功能本身（到店碼、API、即時天氣、無障礙）真實可操作",
     "本文檔第四章「數據口徑」"],
    ["可附帶說明文檔", "即本文檔（指標對照 + 評審動線 + 技術說明）", "—"],
], widths=[1.7, 3.05, 2.05])

# ------------------------------------------------- 2. proposal targets
h1(doc, "二、", "計劃書指標 → 呈現位置逐項對照")
para(doc, "《項目策劃書》第七章承諾的每一項晉級後目標，均已在公網作品呈現並達標：", after=4)
table(doc, [
    ["計劃書條文", "目標值", "複賽呈現值", "核驗位置"],
    ["20+ 位本地居民/遊客完成可用性測試", "≥ 20 人", "23 人（居民 11・遊客 12）", "儀表板「可用性測試」"],
    ["任務完成率", "≥ 90%", "91.3%（252/276 項）", "儀表板「可用性測試」"],
    ["受試者認同更省時、更有在地味", "≥ 80%", "省時 82.6%・在地味 87.0%", "儀表板「可用性測試」"],
    ["每份合適行程平均舊區/商戶點", "≥ 3 個", "平均 4.2 個", "儀表板 KPI + 任意行程結果"],
    ["一次性到店碼核銷量度到訪與轉化", "上線可核銷", "發碼 3,152 → 核銷 1,318（41.8%）；行程頁可領碼、儀表板可核銷", "行程結果頁 + 儀表板「核銷演示機」"],
    ["導流覆蓋率", "可量度", "86.4%（1,078/1,247 份行程）", "儀表板 KPI"],
    ["路線可行率", "可量度", "98.9%（開放/步行/預算核驗）", "儀表板 KPI + 行程「任務完成核對」面板"],
    ["商戶到訪率", "可量度", "41.8%（碼核銷率）", "儀表板 KPI + 商戶卡片"],
    ["不增加熱門點過載", "熱點峰值不升", "大三巴峰值 −9.8%、舊區到訪 +23.5%", "儀表板「匿名化區域熱度」"],
    ["第 1 階段：校正人流模型", "完成", "MAE 8.6 → 2.9（0–100 指數）、方向命中 95.2%", "儀表板「人流模型校正」"],
    ["第 1 階段：加入即時天氣", "完成", "接入 Open-Meteo 實時預報（行程頁「實時天氣」徽章），異常自動回退估算模型", "任意行程結果頁"],
    ["第 1 階段：加入無障礙資料", "完成", "70/70 POI 無障礙標註（行程站點徽章 + 提示）", "任意行程結果頁"],
    ["第 2 階段：3–5 間商戶到店碼試點", "3–5 間", "5 間老字號（半島 2・氹仔 2・路環 1）", "儀表板「商戶試點」"],
], widths=[2.25, 0.95, 2.2, 1.4])

img1 = os.path.join(ASSETS, "01_dashboard_kpi.png")
image(doc, img1, "成效儀表板：三大成效指標與計劃書目標逐項達標", width=6.3)

# ------------------------------------------------- 3. what's new
h1(doc, "三、", "複賽新增功能總覽（相對初賽）")
h2(doc, "成效儀表板（/dashboard.html）")
bullet(doc, "計劃書 9 項指標對照表、三大成效指標 KPI、可用性測試結果、到店碼轉化漏斗。")
bullet(doc, "匿名化區域熱度（6 區試點前後對比 + 21 日走勢）——即計劃書 B 端「文旅數據儀表板」雛形。")
bullet(doc, "人流模型校正（預測 vs 觀測曲線、MAE 8.6→2.9、方向命中 95.2%）。")
h2(doc, "一次性到店碼閉環（真實可操作）")
bullet(doc, "行程頁每個本地商戶站點可「領取一次性到店碼」（EL-XXXX-XX）。")
bullet(doc, "儀表板「核銷演示機」完成商戶側核銷；重複核銷即被拒——完整演示「領碼 → 到訪 → 核銷 → 不可重用」。")
bullet(doc, "對應計劃書變現路徑：核銷數據是商戶按效果付費的結算依據。")
h2(doc, "酒店與旅行社 B 端 API（/api/v1/itinerary）")
bullet(doc, "一個 POST 請求返回完整行程 JSON（站點、時間軸、預算、無障礙、舊區歸因），供酒店/旅行社系統嵌入。")
bullet(doc, "X-API-Key 鑑權；評審演示金鑰 el-demo-2026；文檔見 /api.html。")
h2(doc, "即時天氣 + 無障礙資料（計劃書第 1 階段）")
bullet(doc, "公網已接入 Open-Meteo 實時預報（30 分鐘快取、2.5 秒超時自動回退估算模型，演示永不中斷）。")
bullet(doc, "70 個 POI 全部標註無障礙資訊（是否無梯級 + 具體提示，如大三巴石階可經斜道繞行）。")
h2(doc, "工程質量")
bullet(doc, "回歸測試由初賽 531/99/64/32 擴充至 641 後端、113 瀏覽器、91 API/安全、41 倉庫交付，全部 PASS；8 個 MCP 工具協議測試通過。")

image(doc, os.path.join(ASSETS, "05_itinerary_access_code.png"),
      "公網實拍：行程站點同屏呈現無障礙徽章與已領取的一次性到店碼（EL-XXXX-XX）", width=6.3)
image(doc, os.path.join(ASSETS, "04_dashboard_redeem.png"),
      "公網實拍：商戶試點卡片與核銷演示機——核銷成功、重複核銷即被拒", width=6.3)

# ------------------------------------------------- 4. data disclosure
h1(doc, "四、", "數據口徑（透明聲明）")
para(doc, "依複賽規則「數據可以不用真實，但呈現效果須達到計劃書的指標」，本作品如實區分兩類數據：", after=4)
table(doc, [
    ["類別", "內容", "口徑"],
    ["真實・可操作",
     "70 POI 知識庫（Wikipedia/Commons 座標與相片）、真實 Qwen 推理、路線/預算/開放核驗、"
     "即時天氣（Open-Meteo）、到店碼發碼/核銷、B 端 API、全部自動化測試結果",
     "線上即時發生"],
    ["示範・模擬",
     "試點窗口（8/11–8/31）的可用性測試結果、發碼/核銷累計量、區域熱度指數、模型校正觀測樣本",
     "確定性生成、口徑與計劃書一致，儀表板與本文檔已明確標註"],
], widths=[1.25, 4.0, 1.55])
para(doc, "與計劃書倫理承諾一致：介面標明 AI 生成與估算值；區域熱度僅到區域粒度、無個人資料；不收集身份信息即可使用。", size=9.8, color=GREY)

# ------------------------------------------------- 5. judge walkthrough
h1(doc, "五、", "評審 5 分鐘動線建議")
table(doc, [
    ["步驟", "操作", "看點"],
    ["1", f"打開 {SITE}，輸入「我下星期三想帶爸媽嚟玩一日」",
     "真實 Qwen ReAct：工具調用、休息日自動改線、實時天氣徽章"],
    ["2", "在行程結果任一本地商戶站點按「領取一次性到店碼」", "到店碼 EL-XXXX-XX 即時發出（無障礙徽章同屏可見）"],
    ["3", f"打開 {DASH}，於「核銷演示機」貼上該碼並核銷兩次",
     "第一次成功、第二次被拒——一次性核銷閉環"],
    ["4", "瀏覽儀表板其餘板塊", "計劃書 9 項指標逐項達標、區域熱度、模型校正"],
    ["5", f"（可選）用 {APIDOC} 的 curl 調用 B 端 API", "401 → 帶演示金鑰 200，返回含舊區歸因的行程 JSON"],
], widths=[0.55, 3.1, 3.15])

# ------------------------------------------------- 6. tech notes
h1(doc, "六、", "技術與部署摘要")
bullet(doc, "架構不變：QwenPaw 2.0.0 Skill + stdio MCP（7+1 工具）＋ FastAPI/SSE ＋ 五語言前端；複賽新增 impact 模組（成效/熱度/商戶/到店碼/B 端 API）。", head="架構：")
bullet(doc, "阿里雲新加坡實例 + Nginx + systemd；本次僅更新 /opt/everylane-macau 應用檔案並重啟 everylane 服務。", head="部署：")
bullet(doc, "到店碼僅存於服務端（無個人資料）；B 端 API 金鑰經環境變數配置；倉庫無任何憑證。", head="安全：")
bullet(doc, "641 後端、113 瀏覽器、91 API/安全、41 倉庫交付、8 MCP 協議測試全部 PASS（qa/ 目錄可重現）。", head="質量：")

para(doc, "", after=2)
runs(doc, [("我們相信複賽要求的不只是「部署完成」，而是把計劃書的每一個承諾變成評審可以親手驗證的功能。", {"size": 10.5}),
           ("街知巷聞已準備好接受核驗。", {"bold": True, "size": 10.5, "color": TERRA})], after=6)
para(doc, "— 完 —", align=CENTER, color=GREY, size=10)

doc.save(OUT)
print("SAVED", OUT)
