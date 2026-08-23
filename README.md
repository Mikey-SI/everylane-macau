# 街知巷聞 · EveryLane Macau

> **澳門深度遊 AI 智能體 —— 唔止大三巴，帶你行勻澳門每一條老街。**
>
> 「千模百煉」AI 開發者系列之學生競賽　·　參賽方向：**澳門文旅 × 舊區活化**
> 正式隊伍：**愛拼才會贏**　·　參賽者：**施天益（SITINIEK）**（學號 dc227126）  
> 技術底座：**QwenPaw 2.0 · Qwen Token Plan · MCP · FastAPI · ReAct Agent**

**線上展示（真實 Qwen Agent）**：<http://47.79.228.128/>  
**成效儀表板（複賽新增）**：<http://47.79.228.128/dashboard.html>  
**B 端 API 文檔（複賽新增）**：<http://47.79.228.128/api.html>  
**靜態備用演示（GitHub Pages）**：<https://mikey-si.github.io/everylane-macau/>

---

## 這是什麼

「街知巷聞」是一個**真正會「做任務」的 AI 智能體**（人設：本地老街坊「阿濠」）。
你只要用一句自然語言講低需求，佢就會：

1. **規劃** —— 拆解你的日期、人數、興趣、預算、步行偏好；
2. **調用工具** —— 自動查天氣、搜景點、逐一核實開放時間、預測人流、計算步行路線、估算預算；
3. **多步執行 + 失敗恢復** —— 遇到「景點當日休息／預算超支／行得太遠」，會**自動改線、替換、縮減**；
4. **智能導流（核心創新）** —— 把你由逼爆的大三巴／議事亭，**分流到舊區老街與本地老字號**；
5. **輸出可驗證行程** —— 支援一日與 2–5 日多日行程，地圖路線、時間軸、人均預算、步行距離，每一項都列明、可核對。

整個過程在網頁上**實時流式展示**。

## 初賽完成狀態

- QwenPaw 2.0.0 已在 Windows 本地部署；
- `everylane-macau` 專用 Skill 已建立並啟用；
- `EveryLane Macau Tools` stdio MCP 已連接；
- 7 個細粒度旅遊工具 + 1 個完整流程工具通過真實 MCP 協議測試；
- Token Plan / DashScope 雙供應商配置（Key 只讀本機 `.env`，不入 Git）；
- 70 個澳門 POI，70 / 70 有圖片，25 個舊區點，20 間本地小店；
- 繁中、簡中、英文、葡文、日文五語言；
- 支援一日及 2–5 日分區行程；
- 五輪 QA 生命周期與初賽開發過程證明已建立。

## 複賽完成狀態（2026-08-23）

複賽要求「完成部署可實際使用的作品，呈現效果須達到計劃書的指標」。在初賽基礎上新增：

- **成效儀表板** `/dashboard.html`：計劃書第七章 9 項指標逐項對照達標
  （導流覆蓋率 86.4%、路線可行率 98.9%、商戶到訪率 41.8%、可用性 23 人 / 完成率 91.3%）、
  匿名化區域熱度（試點前後對比）、人流模型校正（MAE 8.6→2.9）；
- **一次性到店碼閉環（真實可操作）**：行程頁領碼 `EL-XXXX-XX` → 儀表板「核銷演示機」核銷 → 重複核銷即被拒；
- **酒店/旅行社 B 端 API** `POST /api/v1/itinerary`（X-API-Key 鑑權，演示金鑰 `el-demo-2026`，文檔見 `/api.html`）；
- **即時天氣**：接入 Open-Meteo 實時預報（行程頁「實時天氣」徽章，異常自動回退估算模型）；
- **無障礙資料**：70/70 POI 標註是否無梯級 + 具體提示（行程站點徽章）；
- 試點成效數據為示範數據並在頁面明確標註（符合賽規），指標口徑與計劃書一致；
- 說明文檔：`docs/複賽說明文檔_街知巷聞.pdf`。

## 架構

```text
QwenPaw 2.0 / qwen3.7-plus
        │
EveryLane Skill（阿濠人設、ReAct 流程、限制）
        │
stdio MCP
        ├─ search_attractions
        ├─ get_weather
        ├─ check_opening
        ├─ predict_crowd
        ├─ find_local_gem
        ├─ compute_route
        ├─ estimate_budget
        └─ plan_macau_trip
        │
70 POI 知識庫 → FastAPI SSE → 五語言 Web / Leaflet / PDF
```

## 直接運行網站

Windows：

```powershell
.\run.bat
```

macOS / Linux：

```bash
./run.sh
```

打開 <http://127.0.0.1:8000/>。未配置模型 Key 時會使用穩定示範引擎；
配置後自動使用真實 Qwen。

## Token Plan 接入（不要提交 Key）

```powershell
Copy-Item .env.example .env
```

只在本機 `.env` 填：

```dotenv
QWEN_API_KEY=
QWEN_BASE_URL=https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen3.7-plus
```

主辦方若指定國際區，改用其供应商卡片预设的 Singapore URL。`sk-sp-...`
Token Plan Key 不能配普通 `dashscope.aliyuncs.com`。

安全检查：

```powershell
python qwenpaw/check_provider.py --dry-run
python qwenpaw/check_provider.py
```

脚本只显示 `Key loaded: yes (masked)`，不会打印 Key。

## QwenPaw 接入

完整步骤见 [`qwenpaw/README.md`](qwenpaw/README.md)：

1. 启动 QwenPaw Console；
2. 配置 Token Plan 提供商与 `qwen3.7-plus`；
3. 启用 EveryLane Skill；
4. 连接 EveryLane MCP；
5. 用“郑家大屋星期三”场景验证失败恢复。

## 自动化测试

```powershell
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
python qa/test_backend.py
python qa/test_frontend.py
python qa/test_api.py
& "$env:USERPROFILE\.qwenpaw-venv\Scripts\python.exe" qa\test_qwenpaw_mcp.py
```

当前结果（复赛，2026-08-23）：

- 后端：641 PASS / 0 FAIL / 0 WARN
- 浏览器：113 PASS / 0 FAIL（含成效仪表板与到店码闭环）
- API / 安全：91 PASS / 0 FAIL（含 impact / codes / B 端 API）
- 仓库交付：41 PASS / 0 FAIL（`python qa/test_repo.py`）
- QwenPaw MCP：8 tools / protocol / failure recovery / route / planner PASS

测试报告在 [`qa/reports/`](qa/reports/)。

## 比赛材料

- `docs/複賽說明文檔_街知巷聞.pdf`（**复赛**：指标对照 + 评审动线 + 数据口径）
- `docs/概念計劃書_街知巷聞_EveryLaneMacau.pdf`
- `docs/開發過程證明_QwenPaw_街知巷聞.pdf`
- `docs/團隊介紹視頻_3分鐘.mp4`（2:48，1080p，旁白 + 字幕）
- `docs/團隊介紹視頻腳本_3分鐘.md`
- `docs/實踐文章_街知巷聞_EveryLaneMacau.pdf`

## 数据与伦理

- 景点坐标及图片来自公开资料 / Wikimedia Commons，并以人工元数据校正；
- 人流是时段模型估算，不冒充实时官方数据；
- 开放时间会逐站核实，但最终仍提醒以现场公告为准；
- 无需登录，不收集用户身份资料；
- API Key、Token 与 `.env` 永不提交到仓库或展示材料。

