/* 街知巷聞 · EveryLane Macau — frontend app */
(() => {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const el = (tag, cls, html) => { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; };
  const esc = (s) => (s == null ? "" : String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c])));

  const TOOL_ICON = {
    get_weather: "🌤️", search_attractions: "🔎", check_opening: "🕒",
    predict_crowd: "👥", find_local_gem: "💎", compute_route: "🗺️", estimate_budget: "💰",
    submit_itinerary: "📦",
  };
  const CROWD_CLASS = { quiet: "crowd-quiet", moderate: "crowd-moderate", busy: "crowd-busy", packed: "crowd-packed" };

  const I18N = {
    "zh-HK": {
      htmlLang: "zh-Hant", title: "街知巷聞 · EveryLane Macau — 澳門深度遊 AI 智能體",
      navPlan: "規劃行程", navHow: "點樣運作", navValue: "商業價值", engineTitle: "當前推理引擎",
      connecting: "· 連接中 ·", offline: "● 離線示範引擎", offlineTitle: "未設定 DASHSCOPE_API_KEY：以離線引擎完整演示同樣的智能體流程；設定金鑰後自動改用真實 Qwen。", liveTitle: "正在使用阿里雲百煉 Qwen 模型驅動",
      eyebrow: "澳門文旅 × 舊區活化 · 千問 Qwen / QwenPaw 智能體",
      heroTitle: "唔止大三巴，<br><span class=\"hl\">阿濠帶你行勻澳門每一條老街</span>",
      lede: "一個識得「做任務」嘅 AI 智能體 —— 自動<b>查天氣、搜景點、核對開放時間、預測人流</b>，仲會將你由逼爆嘅熱點，<b>智能導流到舊區老街同本地小店</b>，輸出一份可驗證嘅深度遊行程。",
      ctaPlan: "開始規劃我的澳門深度遊 →", ctaHow: "睇下個 AI 點樣諗",
      statPoi: "個真實澳門景點", statOld: "個舊區景點", statLocal: "個本地商戶點", statTools: "項可調用工具",
      plannerTitle: "同阿濠講一句，佢就同你計掂成日行程", plannerSub: "用自然語言講低你嘅需求即可，例如日期、人數、興趣、預算、想唔想行多路。",
      placeholder: "例如：我下星期三想帶爸媽嚟澳門玩一日，鍾意歷史文化同地道美食，預算唔想太貴，又唔想行太多路…", inputLabel: "澳門行程需求",
      hint: "⌘/Ctrl + Enter 快速出發", planBtn: "出發 · 規劃行程", planning: "阿濠規劃緊…",
      traceTitle: "阿濠 · 智能體工作過程", traceToggle: "收合/展開", empty: "阿濠正在落手規劃，行程即將喺度生成…",
      howTitle: "點樣運作：一個真正識得「做任務」嘅智能體", howSub: "已接入 QwenPaw Skill + MCP —— 規劃、調用工具、多步執行、失敗自動恢復。",
      how1h: "理解 & 規劃", how1p: "解析自然語言需求，拆解成日期、人數、興趣、預算、步行偏好，並制定行動計劃。",
      how2h: "調用工具", how2p: "天氣、景點檢索、開放時間核實、人流預測、導流、路線計算、預算估算 —— 7 大工具。",
      how3h: "多步執行", how3p: "逐一核實每個景點，動態整合天氣、人流、地理片區，組裝出可步行嘅順路行程。",
      how4h: "失敗恢復", how4p: "遇到景點當日休息、預算超支、行得太遠，會自動改線、替換、縮減，唔會卡住。",
      valueTitle: "商業價值：一個導流引擎，三方共贏", tourist: "遊客", touristP: "避開人潮、慳錢慳腳骨力，體驗到真正地道、有故事嘅澳門，滿意度與停留時間提升。",
      shop: "舊區小店", shopP: "把集中在大三巴／威尼斯人的客流，導入十月初五街、福隆新街等老街與街坊老字號，<b>創造可轉化的新客流機會</b>。試點以一次性到店碼核銷，驗證實際轉化後按效果收費。",
      city: "城市 / 政府", cityP: "平衡旅遊承載、緩解過度集中、活化舊區與保育文化遺產，契合澳門「世界旅遊休閒中心」定位。",
      valueFoot: "變現路徑：到店碼核銷後的商戶精選訂閱／按效果付費 · 酒店與旅行社 API · 匿名化文旅儀表板。",
      footerSub: "「千模百煉」AI 開發者系列之學生競賽 · 參賽方向：澳門文旅 × 舊區活化", participant: "隊伍：愛拼才會贏 · 參賽者：施天益（SITINIEK，學號 dc227126）", tech: "技術：Qwen / QwenPaw · FastAPI · ReAct Agent", ethics: "AI 倫理：行程由 AI 生成，人流為估算值，請以現場為準；數據來源公開資料。",
      navDash: "成效儀表板", weatherLive: "實時天氣", accessOk: "無障礙友善", accessSteps: "有梯級/斜路",
      codeBtn: "領取一次性到店碼", codeHint: "到店出示，核銷一次即失效 · 商戶試點",
      judgeDemo: "90 秒評審快速演示",
      fastProgress: "評審快速模式 · 正在逐項調用並核驗 7 項工具", qwenProgress: "真實 Qwen ReAct 規劃中",
      runtimeQwen: "真實 Qwen 推理", runtimeVerified: "可重現工具鏈", runtimeFallback: "Qwen 超時保護 · 工具鏈接管",
      language: "語言", people: "人", interests: "興趣", budget: "預算 MOP", lowWalk: "少行路", daysTrip: "日行程",
      actionPlan: "行動計劃", recovery: "自動改線", noPrompt: "請先講低你想點玩",
      stops: "個站點", walkDistance: "估算步行", budgetPer: "全隊總預算", oldLanes: "舊區景點", localShops: "本地商戶點", localSpend: "本地消費估算", impactTitle: "舊區導流成效 · 由推薦走向可歸因", impactPilot: "目前為行程估算；商戶試點將以一次性到店碼 / 優惠碼核銷，量度實際到訪與轉化。",
      diversionTitle: "智能導流 · 由人潮熱點帶你去舊區老街", constraintsTitle: "任務完成核對 · 每項條件都已驗證", constraintsStatic: "場景核對 · 預設演示數據（天氣/人流為估算）", staticBanner: "策展演示模式：6 個預設場景，天氣與人流為模擬估算；點擊下方樣例後按「出發」開始。", staticEngine: "● 策展演示", staticEngineTitle: "GitHub Pages 靜態演示：6 個預設場景，非即時 Qwen 推理。", errorPlan: "連接失敗，未能取得行程。請檢查網絡後重試，或使用上方樣例進入演示模式。", retryPlan: "重試規劃", cancelPlan: "取消規劃", walkEstimate: "步行時間以舊城巷道錨點折算，並非 OSM 逐路口導航", via: "經", codeFail: "到店碼未能由伺服器發出，請重試。", mapOrderNote: "巷道錨點折線（非 OSM 逐路口導航）",
      daysOverview: "多日分區總覽 · 每日一個可步行主題", fullMap: "全程地圖 · 多日分區路線", routeMap: "路線地圖 · 順路而行",
      timeline: "行程時間軸", notes: "貼士", print: "列印 / 儲存成 PDF", replan: "再規劃一次",
      dayStops: "站", dayWalk: "步行", dayBudget: "預算", dayOld: "舊區", dayLocal: "小店", walk: "步行", minutes: "分鐘", crowd: "人流：", wait: "約等", minShort: "分", free: "免費", approx: "約 MOP ", ahouSays: "阿濠話：", story: "聽阿濠講古", storyListen: "聽阿濠講", storyStop: "停低", storyPlaying: "阿濠講緊…", storyLoading: "阿濠開聲緊…", storyVoice: "千問男聲 · 龍安魯風",
      tool: { get_weather: "查天氣", search_attractions: "搜尋景點", check_opening: "核實開放時間", predict_crowd: "預測人流", find_local_gem: "搵本地老街", compute_route: "規劃步行路線", estimate_budget: "估算預算", submit_itinerary: "提交行程" },
      samples: ["我下星期三想帶爸媽嚟澳門玩一日，鍾意歷史文化同地道美食，預算唔想太貴，又唔想行太多路", "幫我安排澳門三日兩夜，想玩半島世遺、氹仔美食同路環慢活", "情侶星期六想行下舊區老街、影靚相，順便試下街頭小食", "我想去鄭家大屋同附近嘅歷史老街，星期三去", "氹仔半日遊，主打地道美食", "First time in Macau this weekend, we love history, old streets and street food"],
    },
    zh: {
      htmlLang: "zh-Hans", title: "街知巷闻 · EveryLane Macau — 澳门深度游 AI 智能体",
      navPlan: "规划行程", navHow: "运作方式", navValue: "商业价值", engineTitle: "当前推理引擎", connecting: "· 连接中 ·", offline: "● 离线演示引擎", offlineTitle: "未设置 DASHSCOPE_API_KEY：使用离线引擎完整演示同样的智能体流程；设置密钥后自动改用真实 Qwen。", liveTitle: "正在使用阿里云百炼 Qwen 模型驱动",
      eyebrow: "澳门文旅 × 旧区活化 · 千问 Qwen / QwenPaw 智能体", heroTitle: "不止大三巴，<br><span class=\"hl\">阿濠带你走遍澳门每一条老街</span>",
      lede: "一个会“做任务”的 AI 智能体 —— 自动<b>查天气、搜景点、核对开放时间、预测人流</b>，还会把你从拥挤热点，<b>智能导流到旧区老街和本地小店</b>，输出一份可验证的深度游行程。",
      ctaPlan: "开始规划我的澳门深度游 →", ctaHow: "看看 AI 如何思考", statPoi: "个真实澳门景点", statOld: "个旧区景点", statLocal: "个本地商户点", statTools: "项可调用工具",
      plannerTitle: "跟阿濠说一句，就能规划整趟行程", plannerSub: "用自然语言写下需求即可，例如日期、人数、兴趣、预算、是否少走路。", placeholder: "例如：我下星期三想带爸妈来澳门玩一天，喜欢历史文化和地道美食，预算不想太贵，又不想走太多路…", inputLabel: "澳门行程需求", hint: "⌘/Ctrl + Enter 快速出发", planBtn: "出发 · 规划行程", planning: "阿濠正在规划…",
      traceTitle: "阿濠 · 智能体工作过程", traceToggle: "收合/展开", empty: "阿濠正在规划，行程马上在这里生成…", howTitle: "如何运作：一个真正会“做任务”的智能体", howSub: "已接入 QwenPaw Skill + MCP —— 规划、调用工具、多步执行、失败自动恢复。",
      how1h: "理解与规划", how1p: "解析自然语言需求，拆解成日期、人数、兴趣、预算、步行偏好，并制定行动计划。", how2h: "调用工具", how2p: "天气、景点检索、开放时间核实、人流预测、导流、路线计算、预算估算 —— 7 大工具。", how3h: "多步执行", how3p: "逐一核实每个景点，动态整合天气、人流、地理片区，组装出可步行的顺路行程。", how4h: "失败恢复", how4p: "遇到景点当天休息、预算超支、走得太远，会自动改线、替换、缩减，不会卡住。",
      valueTitle: "商业价值：一个导流引擎，三方共赢", tourist: "游客", touristP: "避开人潮、省钱省脚力，体验真正地道、有故事的澳门，提升满意度与停留时间。", shop: "旧区小店", shopP: "把集中在大三巴／威尼斯人的客流，导入十月初五街、福隆新街等老街与街坊老字号，<b>创造可转化的新客流机会</b>。试点使用一次性到店码核销，验证转化后按效果收费。", city: "城市 / 政府", cityP: "平衡旅游承载、缓解过度集中、活化旧区与保育文化遗产，契合澳门“世界旅游休闲中心”定位。", valueFoot: "变现路径：到店码核销后的商户精选订阅／按效果付费 · 酒店与旅行社 API · 匿名化文旅仪表板。",
      footerSub: "“千模百炼”AI 开发者系列之学生竞赛 · 参赛方向：澳门文旅 × 旧区活化", participant: "队伍：爱拼才会赢 · 参赛者：施天益（SITINIEK，学号 dc227126）", tech: "技术：Qwen / QwenPaw · FastAPI · ReAct Agent", ethics: "AI 伦理：行程由 AI 生成，人流为估算值，请以现场为准；数据来源公开资料。",
      navDash: "成效仪表板", weatherLive: "实时天气", accessOk: "无障碍友好", accessSteps: "有台阶/坡道", codeBtn: "领取一次性到店码", codeHint: "到店出示，核销一次即失效 · 商户试点",
      judgeDemo: "90 秒评审快速演示",
      fastProgress: "评审快速模式 · 正在逐项调用并核验 7 项工具", qwenProgress: "真实 Qwen ReAct 规划中",
      runtimeQwen: "真实 Qwen 推理", runtimeVerified: "可复现工具链", runtimeFallback: "Qwen 超时保护 · 工具链接管",
      language: "语言", people: "人", interests: "兴趣", budget: "预算 MOP", lowWalk: "少走路", daysTrip: "日行程", actionPlan: "行动计划", recovery: "自动改线", noPrompt: "请先写下你想怎么玩", stops: "个站点", walkDistance: "估算步行", budgetPer: "全队总预算", oldLanes: "旧区景点", localShops: "本地商户点", localSpend: "本地消费估算", impactTitle: "旧区导流成效 · 从推荐走向可归因", impactPilot: "目前为行程估算；商户试点将使用一次性到店码 / 优惠码核销，量度实际到访与转化。", diversionTitle: "智能导流 · 从人潮热点带你去旧区老街", constraintsTitle: "任务完成核对 · 每项条件都已验证", constraintsStatic: "场景核对 · 预设演示数据（天气/人流为估算）", staticBanner: "策展演示模式：6 个预设场景，天气与人流为模拟估算；点击样例后按「出发」开始。", staticEngine: "● 策展演示", staticEngineTitle: "GitHub Pages 静态演示：6 个预设场景，非实时 Qwen 推理。", errorPlan: "连接失败，未能取得行程。请检查网络后重试，或使用上方样例进入演示模式。", retryPlan: "重试规划", cancelPlan: "取消规划", walkEstimate: "步行时间以旧城巷道锚点折算，并非 OSM 逐路口导航", via: "经", codeFail: "到店码未能由服务器发出，请重试。", mapOrderNote: "巷道锚点折线（非 OSM 逐路口导航）", daysOverview: "多日分区总览 · 每日一个可步行主题", fullMap: "全程地图 · 多日分区路线", routeMap: "路线地图 · 顺路而行", timeline: "行程时间轴", notes: "贴士", print: "打印 / 保存为 PDF", replan: "再规划一次", dayStops: "站", dayWalk: "步行", dayBudget: "预算", dayOld: "旧区", dayLocal: "小店", walk: "步行", minutes: "分钟", crowd: "人流：", wait: "约等", minShort: "分", free: "免费", approx: "约 MOP ", ahouSays: "阿濠说：", story: "听阿濠讲故事", storyListen: "听阿濠讲", storyStop: "停下", storyPlaying: "阿濠正在讲…", storyLoading: "阿濠正在开口…", storyVoice: "千问男声 · 龙安鲁风",
      tool: { get_weather: "查天气", search_attractions: "搜索景点", check_opening: "核实开放时间", predict_crowd: "预测人流", find_local_gem: "找本地老街", compute_route: "规划步行路线", estimate_budget: "估算预算", submit_itinerary: "提交行程" },
      samples: ["我下星期三想带爸妈来澳门玩一天，喜欢历史文化和地道美食，预算不想太贵，又不想走太多路", "帮我安排澳门三天两夜，想玩半岛世遗、氹仔美食和路环慢生活", "情侣星期六想逛旧区老街、拍照，顺便吃街头小吃", "我想去郑家大屋和附近的历史老街，星期三去", "氹仔半日游，主打地道美食", "First time in Macau this weekend, we love history, old streets and street food"],
    },
    en: {
      htmlLang: "en", title: "EveryLane Macau — AI Deep-Travel Agent",
      navPlan: "Plan Trip", navHow: "How It Works", navValue: "Business Value", engineTitle: "Current reasoning engine", connecting: "· Connecting ·", offline: "● Offline Demo Engine", offlineTitle: "No DASHSCOPE_API_KEY set: the offline engine demonstrates the same agent flow; add a key to use real Qwen.", liveTitle: "Powered by Alibaba Cloud Bailian Qwen",
      eyebrow: "Macau Tourism × Old-District Revival · Qwen / QwenPaw Agent", heroTitle: "Beyond St. Paul’s,<br><span class=\"hl\">Ah-Hou walks you through every old lane in Macau</span>",
      lede: "An AI agent that actually gets tasks done: it <b>checks weather, searches POIs, verifies opening hours and predicts crowds</b>, then <b>diverts visitors into old streets and local shops</b> to produce a verifiable deep-travel itinerary.",
      ctaPlan: "Start My Macau Deep Trip →", ctaHow: "See How the AI Thinks", statPoi: "real Macau POIs", statOld: "old-district places", statLocal: "local shops", statTools: "callable tools",
      plannerTitle: "Tell Ah-Hou once, and he plans the whole trip", plannerSub: "Describe your date, group size, interests, budget and walking preference in natural language.", placeholder: "Example: Next Wednesday I’m bringing my parents to Macau for one day. We like history and local food, want a modest budget and less walking…", inputLabel: "Macau trip request", hint: "⌘/Ctrl + Enter to start", planBtn: "Go · Plan Trip", planning: "Ah-Hou is planning…",
      traceTitle: "Ah-Hou · Agent Work Trace", traceToggle: "Collapse/expand", empty: "Ah-Hou is planning. Your itinerary will appear here soon…", howTitle: "How It Works: an Agent That Really Does Tasks", howSub: "Integrated with QwenPaw Skill + MCP: planning, tool calling, multi-step execution and failure recovery.",
      how1h: "Understand & Plan", how1p: "Parse natural language into date, people, interests, budget and walking preference, then form an action plan.", how2h: "Call Tools", how2p: "Weather, POI search, opening checks, crowd prediction, diversion, routing and budgeting — 7 tools.", how3h: "Execute Steps", how3p: "Verify every stop and combine weather, crowd and geography into a walkable route.", how4h: "Recover Failures", how4p: "If a place is closed, over budget or too far away, the agent reroutes, replaces or trims automatically.",
      valueTitle: "Business Value: One Diversion Engine, Three Winners", tourist: "Visitors", touristP: "Avoid crowds, save money and walking effort, and experience a more authentic Macau with stories.", shop: "Old-District Shops", shopP: "Redirect traffic from St. Paul’s and Cotai into old lanes and family-run shops, <b>creating measurable conversion opportunities</b>. A pilot uses one-time visit codes before charging for outcomes.", city: "City / Government", cityP: "Balance visitor flows, reduce overcrowding, revitalise old districts and preserve cultural heritage.", valueFoot: "Monetisation after visit-code validation: featured merchants / pay per outcome · hotel and agency APIs · anonymised tourism dashboards.",
      footerSub: "Qianmo Bailian AI Developer Series Student Competition · Macau Tourism × Old-District Revival", participant: "Team: Ai Pin Cai Hui Ying · Shi Tianyi (SITINIEK, dc227126)", tech: "Tech: Qwen / QwenPaw · FastAPI · ReAct Agent", ethics: "AI Ethics: itineraries are AI-generated; crowd levels are estimates; please follow on-site conditions. Data comes from public sources.",
      navDash: "Impact Dashboard", weatherLive: "Live weather", accessOk: "Step-free friendly", accessSteps: "Steps / slopes", codeBtn: "Get one-time visit code", codeHint: "Show in store; one redemption only · merchant pilot",
      judgeDemo: "90-sec Judge Demo",
      fastProgress: "Judge mode · calling and verifying all 7 tools", qwenProgress: "Live Qwen ReAct planning",
      runtimeQwen: "Live Qwen reasoning", runtimeVerified: "Reproducible toolchain", runtimeFallback: "Qwen timeout guard · tools took over",
      language: "Language", people: "people", interests: "Interests", budget: "Budget MOP", lowWalk: "Less walking", daysTrip: "days", actionPlan: "Action Plan", recovery: "Auto Reroute", noPrompt: "Please describe how you want to travel", stops: "stops", walkDistance: "estimated walk", budgetPer: "total group budget", oldLanes: "old lanes", localShops: "local shops", localSpend: "estimated local spend", impactTitle: "Old-District Impact · From Recommendation to Attribution", impactPilot: "These are itinerary estimates. Merchant pilots will use one-time visit / offer codes to measure actual arrivals and conversion.", diversionTitle: "Smart Diversion · From Crowded Hotspots to Old Lanes", constraintsTitle: "Task Checks · Every Condition Verified", constraintsStatic: "Scenario Checks · Preset demo data (weather/crowd estimated)", staticBanner: "Curated demo mode: 6 preset scenarios with simulated weather and crowd estimates. Pick a sample, then press Go.", staticEngine: "● Curated Demo", staticEngineTitle: "GitHub Pages static demo: 6 preset scenarios, not live Qwen reasoning.", errorPlan: "Connection failed — itinerary not received. Check your network and retry, or use a sample above.", retryPlan: "Retry planning", cancelPlan: "Cancel planning", walkEstimate: "Walk times use old-town lane anchors, not OSM turn-by-turn routing", via: "via", codeFail: "The visit code could not be issued by the server. Please retry.", mapOrderNote: "Lane-anchor polyline (not OSM turn-by-turn)", daysOverview: "Multi-Day Overview · One Walkable Theme per Day", fullMap: "Full Map · Multi-Day District Routes", routeMap: "Route Map · Walkable Order", timeline: "Itinerary Timeline", notes: "Tips", print: "Print / Save Result as PDF", replan: "Plan Again", dayStops: "stops", dayWalk: "walk", dayBudget: "budget", dayOld: "old areas", dayLocal: "shops", walk: "Walk", minutes: "min", crowd: "Crowd: ", wait: "wait about ", minShort: "min", free: "Free", approx: "Approx. MOP ", ahouSays: "Ah-Hou says: ", story: "Hear Ah-Hou’s story", storyListen: "Listen", storyStop: "Stop", storyPlaying: "Ah-Hou is speaking…", storyLoading: "Ah-Hou is finding his voice…", storyVoice: "Qwen male voice · Longan Lufeng",
      tool: { get_weather: "Weather", search_attractions: "Search POIs", check_opening: "Check Opening", predict_crowd: "Predict Crowd", find_local_gem: "Find Local Gem", compute_route: "Plan Route", estimate_budget: "Estimate Budget", submit_itinerary: "Submit Itinerary" },
      samples: ["Next Wednesday I’m bringing my parents to Macau for one day. We like history and local food, want a modest budget and less walking.", "Plan a 3 days Macau trip with heritage, Taipa food and Coloane slow life", "A couple trip this Saturday: old lanes, photo spots and street food", "I want to visit Mandarin’s House and nearby historic lanes on Wednesday", "Taipa half-day food walk", "First time in Macau this weekend, we love history, old streets and street food"],
    },
    pt: {
      htmlLang: "pt", title: "EveryLane Macau — Agente IA de Turismo Profundo",
      navPlan: "Planear Roteiro", navHow: "Como Funciona", navValue: "Valor Comercial", engineTitle: "Motor de raciocínio atual", connecting: "· A ligar ·", offline: "● Motor de Demonstração Offline", offlineTitle: "Sem DASHSCOPE_API_KEY: o motor offline demonstra o mesmo fluxo do agente; com chave passa a usar Qwen real.", liveTitle: "Alimentado por Qwen no Alibaba Cloud Bailian",
      eyebrow: "Turismo de Macau × Revitalização dos bairros antigos · Agente Qwen / QwenPaw", heroTitle: "Para além das Ruínas de São Paulo,<br><span class=\"hl\">Ah-Hou leva-te por cada rua antiga de Macau</span>", lede: "Um agente de IA que executa tarefas: <b>consulta o tempo, pesquisa pontos, verifica horários e prevê multidões</b>, depois <b>encaminha visitantes para ruas antigas e lojas locais</b> para criar um roteiro verificável.",
      ctaPlan: "Começar o meu roteiro em Macau →", ctaHow: "Ver como a IA pensa", statPoi: "pontos reais de Macau", statOld: "locais de bairros antigos", statLocal: "lojas locais", statTools: "ferramentas disponíveis",
      plannerTitle: "Diz uma frase ao Ah-Hou e ele planeia tudo", plannerSub: "Descreve data, número de pessoas, interesses, orçamento e preferência de caminhada em linguagem natural.", placeholder: "Exemplo: Na próxima quarta quero levar os meus pais a Macau por um dia; gostamos de história e comida local, com orçamento moderado e pouca caminhada…", inputLabel: "Pedido de roteiro em Macau", hint: "⌘/Ctrl + Enter para começar", planBtn: "Ir · Planear Roteiro", planning: "Ah-Hou está a planear…",
      traceTitle: "Ah-Hou · Processo do Agente", traceToggle: "Recolher/expandir", empty: "Ah-Hou está a planear. O roteiro aparecerá aqui em breve…", howTitle: "Como Funciona: um Agente que Executa Tarefas", howSub: "Integrado com QwenPaw Skill + MCP: planeamento, ferramentas, execução multi-etapas e recuperação de falhas.",
      how1h: "Compreender & Planear", how1p: "Analisa a necessidade em data, pessoas, interesses, orçamento e caminhada, criando um plano de ação.", how2h: "Chamar Ferramentas", how2p: "Tempo, pesquisa de pontos, horários, multidões, alternativas locais, rotas e orçamento — 7 ferramentas.", how3h: "Executar Etapas", how3p: "Verifica cada paragem e combina tempo, multidões e geografia numa rota caminhável.", how4h: "Recuperar Falhas", how4p: "Se um local estiver fechado, caro ou longe, o agente altera, substitui ou reduz automaticamente.",
      valueTitle: "Valor Comercial: Um Motor de Distribuição, Três Beneficiários", tourist: "Visitantes", touristP: "Evita multidões, poupa dinheiro e esforço, e descobre uma Macau mais autêntica.", shop: "Lojas de Bairros Antigos", shopP: "Redireciona fluxo das Ruínas e de Cotai para ruas antigas e lojas familiares, <b>criando oportunidades mensuráveis de conversão</b>. O piloto usa códigos únicos antes da cobrança por resultado.", city: "Cidade / Governo", cityP: "Equilibra fluxos turísticos, reduz sobrelotação, revitaliza bairros antigos e preserva património.", valueFoot: "Monetização após validação: comerciantes destacados / pagamento por resultado · APIs para hotéis · painéis anónimos.",
      footerSub: "Concurso Estudantil Qianmo Bailian AI Developer Series · Turismo de Macau × Revitalização", participant: "Equipa: 愛拼才會贏 · Shi Tianyi / 施天益 (SITINIEK, dc227126)", tech: "Tecnologia: Qwen / QwenPaw · FastAPI · Agente ReAct", ethics: "Ética de IA: roteiros gerados por IA; multidões são estimativas; confirmar no local. Dados de fontes públicas.",
      navDash: "Painel de Impacto", weatherLive: "Tempo em direto", accessOk: "Acessível sem degraus", accessSteps: "Degraus / rampas", codeBtn: "Obter código de visita único", codeHint: "Mostre na loja; válido uma única vez · piloto de comerciantes",
      judgeDemo: "Demo para júri em 90 s",
      fastProgress: "Modo júri · a verificar as 7 ferramentas", qwenProgress: "Planeamento Qwen ReAct em direto",
      runtimeQwen: "Raciocínio Qwen em direto", runtimeVerified: "Ferramentas reproduzíveis", runtimeFallback: "Proteção de timeout · ferramentas assumiram",
      language: "Idioma", people: "pessoas", interests: "Interesses", budget: "Orçamento MOP", lowWalk: "Menos caminhada", daysTrip: "dias", actionPlan: "Plano de Ação", recovery: "Reencaminhamento", noPrompt: "Descreve como queres viajar", stops: "paragens", walkDistance: "caminhada estimada", budgetPer: "orçamento total do grupo", oldLanes: "ruas antigas", localShops: "lojas locais", localSpend: "consumo local estimado", impactTitle: "Impacto nos Bairros · Da Recomendação à Atribuição", impactPilot: "São estimativas do roteiro. O piloto usará códigos únicos de visita / oferta para medir chegadas e conversão reais.", diversionTitle: "Distribuição Inteligente · Dos Hotspots para Ruas Antigas", constraintsTitle: "Verificação da Tarefa · Condições Confirmadas", constraintsStatic: "Verificação de Cenário · Dados de demonstração (tempo/multidões estimados)", staticBanner: "Modo de demonstração: 6 cenários pré-definidos com tempo e multidões simulados. Escolha um exemplo e prima Ir.", staticEngine: "● Demo Curada", staticEngineTitle: "Demonstração estática GitHub Pages: 6 cenários, não é raciocínio Qwen em tempo real.", errorPlan: "Falha de ligação — roteiro não recebido. Verifique a rede ou use um exemplo acima.", retryPlan: "Tentar novamente", walkEstimate: "Tempos a pé por âncoras das ruelas, não navegação OSM", via: "via", cancelPlan: "Cancelar planeamento", codeFail: "O código de visita não pôde ser emitido pelo servidor. Tente novamente.", mapOrderNote: "Linha por âncoras das ruelas (não é OSM passo a passo)", daysOverview: "Visão Multi-Dia · Um Tema Caminhável por Dia", fullMap: "Mapa Completo · Rotas por Distrito", routeMap: "Mapa da Rota · Ordem Caminhável", timeline: "Linha do Tempo", notes: "Dicas", print: "Imprimir / Guardar Resultado em PDF", replan: "Planear Novamente", dayStops: "paragens", dayWalk: "a pé", dayBudget: "orçamento", dayOld: "bairros antigos", dayLocal: "lojas", walk: "A pé", minutes: "min", crowd: "Multidão: ", wait: "espera aprox. ", minShort: "min", free: "Grátis", approx: "Aprox. MOP ", ahouSays: "Ah-Hou diz: ", story: "Ouvir a história de Ah-Hou", storyListen: "Ouvir", storyStop: "Parar", storyPlaying: "Ah-Hou está a falar…", storyLoading: "Ah-Hou está a abrir a voz…", storyVoice: "Voz masculina Qwen · Longan Lufeng",
      tool: { get_weather: "Tempo", search_attractions: "Pesquisar Pontos", check_opening: "Verificar Horário", predict_crowd: "Prever Multidão", find_local_gem: "Alternativa Local", compute_route: "Planear Rota", estimate_budget: "Estimar Orçamento", submit_itinerary: "Submeter Roteiro" },
      samples: ["Na próxima quarta quero levar os meus pais a Macau por um dia, com história, comida local, orçamento moderado e pouca caminhada", "Planeia 3 dias em Macau com património, comida em Taipa e vida lenta em Coloane", "Viagem de casal no sábado: ruas antigas, fotos e comida de rua", "Quero visitar a Casa do Mandarim e ruas históricas próximas na quarta", "Meio dia em Taipa com foco em comida local", "First time in Macau this weekend, we love history, old streets and street food"],
    },
    ja: {
      htmlLang: "ja", title: "EveryLane Macau — マカオ深度旅行AIエージェント",
      navPlan: "旅程を作る", navHow: "仕組み", navValue: "商業価値", engineTitle: "現在の推論エンジン", connecting: "· 接続中 ·", offline: "● オフラインデモエンジン", offlineTitle: "DASHSCOPE_API_KEY 未設定：同じエージェント流れをオフラインで実演します。キー設定後は本物の Qwen を使用します。", liveTitle: "Alibaba Cloud Bailian の Qwen で動作中",
      eyebrow: "マカオ観光 × 旧市街活性化 · Qwen / QwenPaw エージェント", heroTitle: "聖ポール天主堂跡だけじゃない、<br><span class=\"hl\">阿濠がマカオの古い路地まで案内</span>", lede: "ただ答えるだけでなく、実際にタスクをこなすAIエージェント。<b>天気、スポット、営業時間、人流</b>を確認し、混雑スポットから<b>旧市街の路地と地元店</b>へスマートに誘導します。",
      ctaPlan: "マカオ深度旅行を作る →", ctaHow: "AIの考え方を見る", statPoi: "実在するマカオPOI", statOld: "旧市街スポット", statLocal: "地元店", statTools: "利用可能ツール",
      plannerTitle: "阿濠に一言伝えるだけで旅程を作成", plannerSub: "日付、人数、興味、予算、歩く量を自然な言葉で入力してください。", placeholder: "例：来週水曜に両親とマカオを1日観光。歴史とローカルグルメが好きで、予算は控えめ、歩きすぎたくない…", inputLabel: "マカオ旅行の希望", hint: "⌘/Ctrl + Enter で開始", planBtn: "出発 · 旅程を作成", planning: "阿濠が計画中…",
      traceTitle: "阿濠 · エージェント作業ログ", traceToggle: "折りたたみ/展開", empty: "阿濠が計画中です。旅程はここに表示されます…", howTitle: "仕組み：本当にタスクを実行するエージェント", howSub: "QwenPaw Skill + MCP を実装：計画、ツール呼び出し、多段実行、失敗回復。",
      how1h: "理解と計画", how1p: "自然言語を日付、人数、興味、予算、歩行希望に分解し、行動計画を立てます。", how2h: "ツール呼び出し", how2p: "天気、スポット検索、営業時間、人流予測、誘導、ルート、予算の7ツール。", how3h: "多段実行", how3p: "各スポットを検証し、天気・人流・地理を組み合わせて歩けるルートにします。", how4h: "失敗回復", how4p: "休業、予算超過、遠すぎる場合は自動で変更・代替・短縮します。",
      valueTitle: "商業価値：誘導エンジンで三方よし", tourist: "旅行者", touristP: "混雑を避け、費用と歩行負担を減らし、物語のある本当のマカオを体験できます。", shop: "旧市街の店", shopP: "聖ポールやコタイに集中する人流を古い路地と家族経営の店へ送り、<b>計測可能な来店機会</b>を作ります。実証では一回限りの来店コードを使います。", city: "都市 / 政府", cityP: "観光流量を分散し、過密を緩和し、旧市街活性化と文化保全に貢献します。", valueFoot: "来店コード検証後の収益化：おすすめ店舗／成果報酬 · ホテルAPI · 匿名観光ダッシュボード。",
      footerSub: "「千模百煉」AI開発者シリーズ学生コンペ · マカオ観光 × 旧市街活性化", participant: "チーム：愛拼才會贏 · 施天益（SITINIEK、dc227126）", tech: "技術：Qwen / QwenPaw · FastAPI · ReAct Agent", ethics: "AI倫理：旅程はAI生成、人流は推定値です。現地状況を優先してください。データは公開資料に基づきます。",
      navDash: "効果ダッシュボード", weatherLive: "リアルタイム天気", accessOk: "バリアフリー", accessSteps: "階段・坂あり", codeBtn: "ワンタイム来店コードを取得", codeHint: "店頭で提示、1回で失効 · 店舗実証中",
      judgeDemo: "90秒審査デモ",
      fastProgress: "審査モード · 7ツールを呼び出し検証中", qwenProgress: "Qwen ReActをリアルタイム実行中",
      runtimeQwen: "Qwenリアルタイム推論", runtimeVerified: "再現可能ツールチェーン", runtimeFallback: "Qwenタイムアウト保護 · ツールが継続",
      language: "言語", people: "人", interests: "興味", budget: "予算 MOP", lowWalk: "歩行少なめ", daysTrip: "日旅程", actionPlan: "行動計画", recovery: "自動変更", noPrompt: "旅行の希望を入力してください", stops: "スポット", walkDistance: "推定歩行", budgetPer: "グループ合計予算", oldLanes: "旧市街", localShops: "地元店", localSpend: "地元消費の推定", impactTitle: "旧市街への効果 · 推薦から計測へ", impactPilot: "現在は旅程上の推定です。店舗実証では一回限りの来店 / 特典コードで実来店と転換を測定します。", diversionTitle: "スマート誘導 · 混雑地から旧市街へ", constraintsTitle: "タスク確認 · 条件を検証済み", constraintsStatic: "シナリオ確認 · プリセットデモ（天気/人流は推定）", staticBanner: "キュレーション・デモ：6つのプリセットシナリオ。天気と人流はシミュレーション。サンプルを選び「出発」を押してください。", staticEngine: "● キュレーションデモ", staticEngineTitle: "GitHub Pages 静的デモ：6シナリオ。リアルタイム Qwen 推論ではありません。", errorPlan: "接続に失敗しました。ネットワークを確認して再試行するか、上のサンプルを使ってください。", retryPlan: "再試行", walkEstimate: "歩行時間は旧市街の巷道アンカーで換算（OSMの逐次ナビではない）", via: "経由", cancelPlan: "計画をキャンセル", codeFail: "来店コードをサーバーから発行できませんでした。再試行してください。", mapOrderNote: "巷道アンカーの折線（OSM逐次ナビではありません）", daysOverview: "複数日概要 · 1日1つの歩けるテーマ", fullMap: "全体地図 · 複数日エリア別ルート", routeMap: "ルート地図 · 歩きやすい順番", timeline: "旅程タイムライン", notes: "ヒント", print: "印刷 / 結果をPDF保存", replan: "もう一度計画", dayStops: "スポット", dayWalk: "歩行", dayBudget: "予算", dayOld: "旧市街", dayLocal: "地元店", walk: "徒歩", minutes: "分", crowd: "人流：", wait: "待ち約", minShort: "分", free: "無料", approx: "約 MOP ", ahouSays: "阿濠より：", story: "阿濠の話を聞く", storyListen: "聴く", storyStop: "止める", storyPlaying: "阿濠が話しています…", storyLoading: "阿濠が声を出しています…", storyVoice: "Qwen男性ボイス · 龍安魯風",
      tool: { get_weather: "天気確認", search_attractions: "スポット検索", check_opening: "営業時間確認", predict_crowd: "人流予測", find_local_gem: "地元スポット", compute_route: "徒歩ルート", estimate_budget: "予算見積", submit_itinerary: "旅程提出" },
      samples: ["来週水曜に両親とマカオを1日観光。歴史文化とローカルグルメが好きで、予算控えめ、歩きすぎたくない", "マカオ3日2泊：半島の世界遺産、タイパのグルメ、コロアンのスローライフ", "土曜のカップル旅：旧市街、写真スポット、ストリートフード", "水曜に鄭家大屋と近くの歴史路地へ行きたい", "タイパ半日グルメ散歩", "First time in Macau this weekend, we love history, old streets and street food"],
    },
  };

  window.__I18N = I18N; // exposed for automated QA checks

  let STORY_BANK = {};
  const storyReady = fetch("stories.json")
    .then((r) => (r.ok ? r.json() : {}))
    .then((d) => { STORY_BANK = d || {}; })
    .catch(() => {});
  let TTS_PACK = { model: "", voice: "", files: {} };
  const ttsPackReady = fetch("tts/manifest.json")
    .then((r) => (r.ok ? r.json() : null))
    .then((d) => { if (d && d.files) TTS_PACK = d; })
    .catch(() => {});

  const TTS_LANG = {
    "zh-HK": ["zh-HK", "zh-YUE", "yue-HK", "yue", "zh-TW"],
    // Simplified Chinese must never fall through to a Cantonese zh-HK voice.
    zh: ["zh-CN", "zh-SG", "cmn-CN", "cmn-Hans"],
    en: ["en-GB", "en-HK", "en-AU", "en-IE", "en-US", "en"],
    pt: ["pt-PT", "pt-BR", "pt"],
    ja: ["ja-JP", "ja"],
  };
  const MALE_VOICE = /male|nan-male|WanLung|Yunxi|Yunyang|Yunjian|Yunhao|Yunfeng|Yunze|Yunye|Kefu|Keita|Duarte|Daniel|George|Ryan|Guy|Brian|Andrew|Christopher|Steffan|Eric|Chaoxi|Kangkang/i;
  const FEMALE_VOICE = /female|Tracy|Huihui|Xiaoxiao|Xiaoyi|Xiaoshuang|Xiaochen|Xiaomo|HiuMaan|HiuGaai|Nanami|Haruka|Ayumi|Helena|Raquel|Sonia|Aria|Jenny|Emma|Zira|Susan|Hazel|Ana|Ines|Inês|Francisca|Ivy|Joanna|Kendra|Kimberly|Salli|Nicole|Samantha|Tingting|Yaoyao|MeiJia|Hui\b/i;
  let speakingPoi = "";
  let storyUtter = null;
  let storyAudio = null;
  let storyObjectUrl = "";
  let storyFetchCtl = null;

  function storyRecord(s) {
    if (s && s.story && typeof s.story === "object" && (s.story["zh-HK"] || s.story.zh || s.story.en)) {
      return s.story;
    }
    return (s && s.poi_id && STORY_BANK[s.poi_id]) || {};
  }

  function pickStory(s) {
    const rec = storyRecord(s);
    const lang = langNow();
    const order = {
      "zh-HK": ["zh-HK", "zh", "en"],
      zh: ["zh", "zh-HK", "en"],
      en: ["en", "zh-HK", "zh"],
      pt: ["pt", "en", "zh-HK"],
      ja: ["ja", "en", "zh-HK"],
    }[lang] || ["en"];
    for (const k of order) {
      const text = (rec[k] || "").trim();
      if (text) return { text, lang: k };
    }
    const fallback = (s && s.story_zh || "").trim();
    return fallback ? { text: fallback, lang: "zh-HK" } : null;
  }

  function loadVoices() {
    if (!("speechSynthesis" in window)) return [];
    return window.speechSynthesis.getVoices() || [];
  }
  if ("speechSynthesis" in window) {
    window.speechSynthesis.addEventListener("voiceschanged", loadVoices);
    loadVoices();
  }

  function pickVoice(storyLang) {
    const voices = loadVoices();
    const prefs = TTS_LANG[storyLang] || TTS_LANG.en;
    let best = null, bestScore = -1;
    for (const v of voices) {
      const name = v.name || "";
      if (FEMALE_VOICE.test(name) || FEMALE_VOICE.test(v.voiceURI || "")) continue;
      const loc = String(v.lang || "").replace("_", "-");
      const locLow = loc.toLowerCase();
      let score = 0;
      const hit = prefs.findIndex((p) => locLow === p.toLowerCase() || locLow.startsWith(p.toLowerCase() + "-") || locLow.startsWith(p.toLowerCase()));
      if (hit < 0) continue;
      score += 80 - hit * 6;
      if (MALE_VOICE.test(name) || /male/i.test(v.voiceURI || "")) score += 28;
      if (v.localService) score += 4;
      if (score > bestScore) { bestScore = score; best = v; }
    }
    if (best && (MALE_VOICE.test(best.name || "") || /male/i.test(best.voiceURI || ""))) return best;
    return null;
  }

  function markStoryBtn(btn, state) {
    document.querySelectorAll(".story-play").forEach((el) => {
      el.classList.remove("is-playing", "is-loading");
      el.setAttribute("aria-pressed", "false");
      const lab = el.querySelector(".story-play-label");
      if (lab) lab.textContent = tt("storyListen");
    });
    if (!btn || state === "idle") return;
    btn.classList.toggle("is-loading", state === "loading");
    btn.classList.toggle("is-playing", state === "playing" || state === "loading");
    btn.setAttribute("aria-pressed", state === "idle" ? "false" : "true");
    const lab = btn.querySelector(".story-play-label");
    if (lab) lab.textContent = tt(state === "loading" ? "storyLoading" : "storyPlaying");
  }

  function stopStoryVoice() {
    speakingPoi = "";
    storyUtter = null;
    if (storyFetchCtl) {
      try { storyFetchCtl.abort(); } catch (e) { /* ignore */ }
      storyFetchCtl = null;
    }
    if (storyAudio) {
      try { storyAudio.pause(); storyAudio.removeAttribute("src"); storyAudio.load(); } catch (e) { /* ignore */ }
      storyAudio = null;
    }
    if (storyObjectUrl) {
      try { URL.revokeObjectURL(storyObjectUrl); } catch (e) { /* ignore */ }
      storyObjectUrl = "";
    }
    if ("speechSynthesis" in window) {
      try { window.speechSynthesis.cancel(); } catch (e) { /* ignore */ }
    }
    markStoryBtn(null, "idle");
  }

  function isStoryPlaying(poiId) {
    if (speakingPoi !== poiId) return false;
    if (storyAudio && !storyAudio.paused && !storyAudio.ended) return true;
    if ("speechSynthesis" in window && window.speechSynthesis.speaking) return true;
    if (storyFetchCtl) return true;
    return false;
  }

  function playBrowserStory(picked, btn, poiId) {
    if (!picked || !("speechSynthesis" in window)) {
      stopStoryVoice();
      return;
    }
    const voice = pickVoice(picked.lang);
    if (!voice) {
      stopStoryVoice();
      return;
    }
    const u = new SpeechSynthesisUtterance(picked.text);
    u.voice = voice;
    u.lang = voice.lang || picked.lang;
    u.rate = 0.9;
    u.pitch = 0.92;
    u.volume = 1;
    u.onend = () => { if (storyUtter === u) stopStoryVoice(); };
    u.onerror = () => { if (storyUtter === u) stopStoryVoice(); };
    storyUtter = u;
    speakingPoi = poiId;
    markStoryBtn(btn, "playing");
    window.speechSynthesis.speak(u);
  }

  function packedStoryUrl(poiId, lang) {
    const rec = (TTS_PACK.files || {})[poiId] || {};
    // For Simplified Chinese, silence is safer than accidentally serving
    // the Cantonese recording. The live API/browser fallback also stays zh-CN.
    if (lang === "zh") return rec.zh ? ("tts/" + rec.zh) : "";
    const name = rec[lang] || rec["zh-HK"] || rec.zh || rec.en;
    return name ? ("tts/" + name) : "";
  }

  async function playPackedStory(url, btn, poiId) {
    const a = new Audio(url);
    storyAudio = a;
    speakingPoi = poiId;
    markStoryBtn(btn, "playing");
    a.onended = () => { if (storyAudio === a) stopStoryVoice(); };
    a.onerror = () => { if (storyAudio === a) stopStoryVoice(); };
    await a.play();
  }

  async function playQwenStory(picked, btn, poiId) {
    const ctl = storyFetchCtl || new AbortController();
    storyFetchCtl = ctl;
    const audioLang = langNow() === "zh" ? "zh" : picked.lang;
    const url = `/api/story/audio?poi_id=${encodeURIComponent(poiId)}&lang=${encodeURIComponent(audioLang)}`;
    const r = await fetch(url, { signal: ctl.signal });
    if (!r.ok) throw new Error("tts " + r.status);
    const blob = await r.blob();
    if (storyFetchCtl === ctl) storyFetchCtl = null;
    if (!blob || blob.size < 64) throw new Error("empty audio");
    const obj = URL.createObjectURL(blob);
    storyObjectUrl = obj;
    const a = new Audio(obj);
    storyAudio = a;
    speakingPoi = poiId;
    markStoryBtn(btn, "playing");
    a.onended = () => { if (storyAudio === a) stopStoryVoice(); };
    a.onerror = () => { if (storyAudio === a) playBrowserStory(picked, btn, poiId); };
    await a.play();
  }

  async function playStory(s, btn) {
    const picked = pickStory(s);
    if (!picked) return;
    const poiId = s.poi_id || "";
    if (isStoryPlaying(poiId)) {
      stopStoryVoice();
      return;
    }
    stopStoryVoice();
    speakingPoi = poiId;
    markStoryBtn(btn, "loading");
    const body = btn.closest(".story")?.querySelector(".story-body");
    if (body) body.hidden = false;
    const audioLang = langNow() === "zh" ? "zh" : picked.lang;
    const packed = packedStoryUrl(poiId, audioLang);
    if (packed) {
      try {
        await playPackedStory(packed, btn, poiId);
        return;
      } catch (e) {
        if (e && e.name === "AbortError") return;
      }
    }
    if (!staticMode && poiId) {
      storyFetchCtl = new AbortController();
      try {
        await playQwenStory(picked, btn, poiId);
        return;
      } catch (e) {
        if (e && e.name === "AbortError") return;
      }
    }
    playBrowserStory(picked, btn, poiId);
  }

  let map = null, today = macauToday(), es = null, running = false, healthState = null, lastItinerary = null, staticMode = false, staticTimers = [], gotResult = false;
  let planProgressTimer = null, planStartedAt = 0, planMode = "auto";
  const langNow = () => $("#lang")?.value || "zh-HK";
  const tt = (key) => (I18N[langNow()] || I18N["zh-HK"])[key] || I18N["zh-HK"][key] || key;
  const storyVoiceLabel = () => langNow() === "zh"
    ? "千问普通话男声 · 龙安鲁风"
    : tt("storyVoice");
  const toolLabel = (name) => ((I18N[langNow()] || I18N["zh-HK"]).tool || {})[name] || name;

  function macauToday() {
    return new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Macau", year: "numeric", month: "2-digit", day: "2-digit" }).format(new Date());
  }

  function clearStaticTimers() {
    staticTimers.forEach((id) => clearTimeout(id));
    staticTimers = [];
  }

  function setPlanningBusy(busy) {
    const ws = $("#workspace");
    if (ws) ws.setAttribute("aria-busy", busy ? "true" : "false");
  }

  function showLoadingEmpty() {
    const empty = $("#resultEmpty");
    const spinner = $("#resultSpinner");
    const text = $("#resultEmptyText");
    const retry = $("#retryBtn");
    if (!empty) return;
    empty.classList.remove("hidden", "is-error");
    if (spinner) spinner.classList.remove("hidden");
    if (text) text.textContent = tt("empty");
    if (retry) retry.classList.add("hidden");
  }

  function showPlanError(msg) {
    const empty = $("#resultEmpty");
    const spinner = $("#resultSpinner");
    const text = $("#resultEmptyText");
    const retry = $("#retryBtn");
    if (!empty) return;
    empty.classList.remove("hidden");
    empty.classList.add("is-error");
    empty.setAttribute("role", "alert");
    if (spinner) spinner.classList.add("hidden");
    if (text) text.textContent = msg || tt("errorPlan");
    if (retry) {
      retry.textContent = tt("retryPlan");
      retry.classList.remove("hidden");
    }
    $("#result").classList.add("hidden");
  }

  // ---------------- boot ----------------
  async function boot() {
    await storyReady;
    await ttsPackReady;
    applyStaticI18n();
    $("#lang").addEventListener("change", () => {
      stopStoryVoice();
      applyStaticI18n();
      if (lastItinerary) renderResult(lastItinerary);
    });
    if (isStaticHost()) {
      enableStaticMode();
      return;
    }
    // health
    try {
      healthState = await (await fetch("/api/health")).json();
      $("#hsPoi").textContent = healthState.poi_count;
      $("#hsOld").textContent = healthState.old_district;
      $("#hsLocal").textContent = healthState.local_business;
      updateEngineBadge();
    } catch (e) {
      enableStaticMode();
    }
  }

  function isStaticHost() {
    // Only GitHub Pages / local static QA use curated demos.
    // Any real server (IP / custom domain / localhost:8000) uses the live API.
    if (location.port === "8090") return true;
    if (location.hostname.endsWith("github.io")) return true;
    return false;
  }

  function enableStaticMode() {
    staticMode = true;
    today = macauToday();
    healthState = { ok: true, engine: "github-pages-static", real_llm: false, poi_count: 70, old_district: 25, local_business: 20 };
    $("#hsPoi").textContent = healthState.poi_count;
    $("#hsOld").textContent = healthState.old_district;
    $("#hsLocal").textContent = healthState.local_business;
    const banner = $("#staticBanner");
    if (banner) {
      banner.textContent = tt("staticBanner");
      banner.classList.remove("hidden");
    }
    updateEngineBadge();
  }

  function applyStaticI18n() {
    const L = I18N[langNow()] || I18N["zh-HK"];
    document.documentElement.lang = L.htmlLang;
    document.title = L.title;
    const set = (sel, key) => { const n = $(sel); if (n) n.innerHTML = tt(key); };
    set(".nav-links a[href='#planner']", "navPlan");
    set(".nav-links a[href='#how']", "navHow");
    set(".nav-links a[href='#value']", "navValue");
    set(".nav-links a[href='dashboard.html']", "navDash");
    set(".eyebrow", "eyebrow"); set(".hero h1", "heroTitle"); set(".lede", "lede");
    set(".hero-cta .btn-primary", "ctaPlan"); set(".hero-cta .btn-ghost", "ctaHow");
    set("#judgeDemoBtn", "judgeDemo");
    const statLabels = ["statPoi", "statOld", "statLocal", "statTools"];
    document.querySelectorAll(".hero-stats span").forEach((n, i) => n.textContent = tt(statLabels[i]));
    set("#planner .section-head h2", "plannerTitle"); set("#planner .section-head p", "plannerSub");
    $("#prompt").placeholder = tt("placeholder");
    $("#prompt").setAttribute("aria-label", tt("inputLabel"));
    set(".hint", "hint"); $("#planBtn").textContent = running ? tt("planning") : tt("planBtn");
    set(".trace-head h3", "traceTitle"); $("#traceToggle").title = tt("traceToggle");
    const emptyText = $("#resultEmptyText"); if (emptyText) emptyText.textContent = tt("empty");
    const retry = $("#retryBtn"); if (retry) retry.textContent = tt("retryPlan");
    const banner = $("#staticBanner");
    if (banner) {
      banner.textContent = tt("staticBanner");
      banner.classList.toggle("hidden", !staticMode);
    }
    set("#how .section-head h2", "howTitle"); set("#how .section-head p", "howSub");
    const howKeys = [["how1h", "how1p"], ["how2h", "how2p"], ["how3h", "how3p"], ["how4h", "how4p"]];
    document.querySelectorAll(".how-card").forEach((card, i) => {
      card.querySelector("h4").textContent = tt(howKeys[i][0]);
      card.querySelector("p").textContent = tt(howKeys[i][1]);
    });
    set("#value .section-head h2", "valueTitle");
    const v = document.querySelectorAll(".value-card");
    if (v[0]) { v[0].querySelector("h4").textContent = tt("tourist"); v[0].querySelector("p").innerHTML = tt("touristP"); }
    if (v[1]) { v[1].querySelector("h4").textContent = tt("shop"); v[1].querySelector("p").innerHTML = tt("shopP"); }
    if (v[2]) { v[2].querySelector("h4").textContent = tt("city"); v[2].querySelector("p").innerHTML = tt("cityP"); }
    set(".value-foot", "valueFoot"); set(".foot-in > div:first-child p", "footerSub");
    const meta = document.querySelectorAll(".foot-meta p");
    if (meta[0]) meta[0].textContent = tt("participant");
    if (meta[1]) meta[1].textContent = tt("tech");
    if (meta[2]) meta[2].textContent = tt("ethics");
    updateEngineBadge();
    renderSamples();
    renderTools();
  }

  function renderSamples() {
    const chips = $("#sampleChips"); chips.innerHTML = "";
    (I18N[langNow()] || I18N["zh-HK"]).samples.forEach(s => {
      const c = el("button", "chip", esc(s.length > 30 ? s.slice(0, 30) + "…" : s));
      c.title = s;
      c.addEventListener("click", () => { $("#prompt").value = s; $("#prompt").focus(); });
      chips.appendChild(c);
    });
  }

  function renderTools() {
    const ts = $("#toolsStrip"); ts.innerHTML = "";
    Object.keys(TOOL_ICON).filter(k => k !== "submit_itinerary").forEach(k => {
      ts.appendChild(el("span", "tool-pill", `<span class="tp-ic">${TOOL_ICON[k]}</span>${esc(toolLabel(k))}`));
    });
  }

  function updateEngineBadge() {
    const b = $("#engineBadge");
    b.title = tt("engineTitle");
    if (!healthState) { b.textContent = tt("connecting"); return; }
    if (staticMode) {
      b.textContent = tt("staticEngine");
      b.classList.add("offline"); b.classList.remove("live"); b.title = tt("staticEngineTitle");
      return;
    }
    if (healthState.real_llm) {
      b.textContent = "● Qwen " + healthState.engine.replace("qwen:", "");
      b.classList.add("live"); b.classList.remove("offline"); b.title = tt("liveTitle");
    } else {
      b.textContent = tt("offline");
      b.classList.add("offline"); b.classList.remove("live"); b.title = tt("offlineTitle");
    }
  }

  // ---------------- planning ----------------
  function updatePlanProgress() {
    const node = $("#planProgress");
    if (!node || !running) return;
    const elapsed = Math.max(0, Math.floor((Date.now() - planStartedAt) / 1000));
    node.textContent = `${tt(planMode === "fast" ? "fastProgress" : "qwenProgress")} · ${elapsed}s`;
  }

  async function startPlan(mode = "auto") {
    await storyReady;
    await ttsPackReady;
    stopStoryVoice();
    mode = mode === "fast" ? "fast" : "auto";
    if (running) {
      clearStaticTimers();
      es && es.close();
      clearInterval(planProgressTimer);
    }
    today = macauToday();
    const q = $("#prompt").value.trim();
    if (!q) { toast(tt("noPrompt")); $("#prompt").focus(); return; }
    const lang = $("#lang").value;
    running = true;
    planMode = mode;
    planStartedAt = Date.now();
    gotResult = false;
    $("#workspace").classList.remove("hidden");
    $("#result").classList.add("hidden");
    $("#result").innerHTML = "";
    showLoadingEmpty();
    $("#trace").innerHTML = "";
    $("#traceParams").textContent = "";
    $("#tracePulse").classList.add("run");
    $("#planBtn").disabled = true;
    $("#planBtn").textContent = tt("planning");
    const cancel = $("#cancelBtn");
    if (cancel) { cancel.classList.remove("hidden"); cancel.disabled = false; }
    setPlanningBusy(true);
    updatePlanProgress();
    planProgressTimer = setInterval(updatePlanProgress, 1000);
    $("#workspace").scrollIntoView({ behavior: "smooth", block: "start" });

    if (staticMode) {
      runStaticPlan(q, lang);
      return;
    }

    const url = `/api/plan?q=${encodeURIComponent(q)}&lang=${encodeURIComponent(lang)}&today=${today}&mode=${mode}`;
    es = new EventSource(url);
    es.onmessage = (m) => { try { handle(JSON.parse(m.data)); } catch (e) { console.error(e, m.data); } };
    es.onerror = () => {
      if (!running) return;
      if (!gotResult) showPlanError(tt("errorPlan"));
      finish();
    };
  }

  function finish() {
    running = false;
    clearInterval(planProgressTimer);
    planProgressTimer = null;
    clearStaticTimers();
    es && es.close();
    $("#tracePulse").classList.remove("run");
    $("#planBtn").disabled = false;
    $("#planBtn").textContent = tt("planBtn");
    const cancel = $("#cancelBtn");
    if (cancel) { cancel.classList.add("hidden"); cancel.disabled = true; }
    setPlanningBusy(false);
    const progress = $("#planProgress");
    if (progress) progress.textContent = "";
    if (gotResult) $("#resultEmpty").classList.add("hidden");
  }

  function handle(e) {
    switch (e.type) {
      case "params": {
        const p = e.params;
        $("#traceParams").textContent =
          `${tt("language")} ${p.language_name}・${p.date}・${p.people} ${tt("people")}・${tt("interests")}：${(p.interests || []).join("/")}`
          + (p.days && p.days > 1 ? `・${p.days} ${tt("daysTrip")}` : "")
          + (p.budget ? `・${tt("budget")}${p.budget}` : "") + (p.low_walk ? `・${tt("lowWalk")}` : "");
        break;
      }
      case "status": addTrace("status", "▶️", e.text); break;
      case "runtime": {
        const key = (e.engine || "").startsWith("qwen:") ? "runtimeQwen" :
          (e.engine === "fallback-tools" ? "runtimeFallback" : "runtimeVerified");
        addTrace("status", "⚙️",
          `<span class="tr-title">${esc(tt(key))}</span><span class="tr-sum">${esc(e.note || "")}</span>`, true);
        break;
      }
      case "plan": {
        const li = el("li", "tr plan");
        li.innerHTML = `<div class="tr-ic">📋</div><div class="tr-body"><div class="tr-title">${esc(tt("actionPlan"))}</div>` +
          `<ol class="plan-steps">${e.steps.map(s => `<li>${esc(s)}</li>`).join("")}</ol></div>`;
        $("#trace").appendChild(li); scrollTrace(); break;
      }
      case "thought": addTrace("thought", "💭", e.text); break;
      case "tool_call":
        addTrace("tool", TOOL_ICON[e.name] || "🛠️",
          `<span class="tr-title">${esc(toolLabel(e.name))}</span><div class="tr-args">${esc(argstr(e.args))}</div>`, true); break;
      case "tool_result":
        if (e.summary) addTrace("result", "✓", `<span class="tr-sum">${esc(e.summary)}</span>`, true); break;
      case "recovery":
        addTrace("recovery", "🔁",
          `<span class="tr-title">${esc(tt("recovery"))}</span><span class="tr-sum">${esc(e.reason)}</span>`, true); break;
      case "diversion":
        addTrace("diversion", "↪️", `<span class="tr-sum">${esc(e.reason)}</span>`, true); break;
      case "heartbeat": break;
      case "result": gotResult = true; renderResult(e.itinerary); break;
      case "done": finish(); break;
      case "error": showPlanError(e.text || tt("errorPlan")); addTrace("recovery", "⚠️", esc(e.text), true); finish(); break;
    }
  }

  function runStaticPlan(q, lang) {
    clearStaticTimers();
    const scenario = staticScenario(q);
    const L = staticTraceCopy(lang, scenario);
    const multi = scenario.days > 1;
    handle({ type: "params", params: { language: lang, language_name: LANG_LABEL[lang] || lang, date: today, people: scenario.people, interests: L.interests, days: scenario.days } });
    handle({ type: "status", text: L.status });
    handle({ type: "plan", steps: L.steps });
    const steps = [
      ["get_weather", { date: today }, L.weather],
      ["search_attractions", { prefer_local: true, limit: 12 }, L.search],
      ["check_opening", { poi_id: scenario.checkId, date: today }, L.open],
      ["predict_crowd", { poi_id: scenario.anchorId, datetime: today + " 13:00" }, L.crowd],
      ["find_local_gem", { near_poi_id: scenario.anchorId }, L.gem],
      ["compute_route", { optimize: true }, L.route],
      ["estimate_budget", { people: scenario.people }, L.budget],
    ];
    steps.forEach(([name, args, summary], i) => {
      staticTimers.push(setTimeout(() => {
        if (!running) return;
        handle({ type: "tool_call", name, args });
        handle({ type: "tool_result", name, summary });
      }, 250 + i * 180));
    });
    staticTimers.push(setTimeout(() => {
      if (!running) return;
      handle({ type: "recovery", reason: L.recovery });
      handle({ type: "diversion", reason: L.diversion });
      handle({ type: "result", itinerary: staticItineraryForScenario(lang, scenario, multi) });
      handle({ type: "done" });
    }, 1750));
  }

  function poi(id, order, zh, en, pt, category, lat, lng, image, unesco, old, local, arrive, depart, cost, crowd, why) {
    return { order, poi_id: id, name: { zh, en, pt }, category, district_name: "", zone: "", lat, lng, image, arrive, depart, visit_min: 30, why, blurb: { zh: why, en: why }, tags: [], unesco, old_district: old, local_business: local, cost_mop: cost, crowd: { level: 0.5, label: crowd, label_en: crowd, wait: crowd === "busy" ? 12 : 0 }, walk_to_next: null };
  }

  function makeDay(day_no, title, stops) {
    for (let i = 0; i < stops.length - 1; i++) stops[i].walk_to_next = { min: 8, km: 0.45, to: stops[i + 1].name.zh };
    return { day_no, day_title: title, date: today, summary: title, totals: summarize(stops), stops };
  }

  function summarize(stops) {
    return {
      stops: stops.length,
      cost_mop: stops.reduce((a, s) => a + (s.cost_mop || 0), 0),
      local_spend_mop: stops.filter(s => s.local_business).reduce((a, s) => a + (s.cost_mop || 0), 0),
      walk_min: Math.max(0, stops.length - 1) * 8,
      walk_km: +(Math.max(0, stops.length - 1) * 0.45).toFixed(2),
      old_district: stops.filter(s => s.old_district).length,
      local_business: stops.filter(s => s.local_business).length,
    };
  }

  function staticScenario(q) {
    const s = (q || "").toLowerCase();
    if (/鄭家|郑家|mandarin/.test(s)) return scenarioMandarin();
    if (/三日|三天|三日兩夜|三天两夜|[2-5]\s*(?:日|天|泊|days?|dias)|兩日|两日|multi/.test(s)) return scenarioMulti();
    if (/路環|路环|coloane|コロアン/.test(s)) return scenarioColoane();
    if (/氹仔|凼仔|taipa|タイパ/.test(s) && /半日|半天|half|meio\s*dia|美食|food|comida|グルメ/.test(s)) return scenarioTaipa();
    if (/情侶|情侣|拍拖|couple|casal|カップル|影|拍照|photo|写真/.test(s)) return scenarioCouple();
    if (/爸媽|爸妈|父母|parents|pais|両親/.test(s)) return scenarioFamily();
    if (/first time|weekend|第一次|首次/.test(s)) return scenarioFirstTime();
    return scenarioFirstTime();
  }

  const STATIC_UI = {
    "zh-HK": {
      status: "阿濠開始規劃：先理解你嘅日期、人數、興趣同片區，再逐步核實路線。",
      steps: ["理解需求：日期、人數、興趣、預算與步行偏好", "鎖定可步行片區，避免跨島亂跑", "核實開放時間、人流與導流替代點", "計算路線與預算，輸出可驗證行程"],
      interests: ["歷史", "老街", "美食"], weather: "晴朗舒適・適合步行", found: x => `找到 ${x} 候選景點`,
      open: x => `${x}：開放`, closed: "鄭家大屋：逢週三休息", crowd: (n, c) => `${n} 正午人流：${c}`,
      gem: x => `建議導流至 ${x}`, route: "已排好順路步行路線", budget: x => `預算合計 MOP ${x}`,
      weatherShort: "晴朗舒適", oneDay: "一日行程", multiDay: n => `${n} 日行程`,
      crowdLabels: { quiet: "寧靜", moderate: "適中", busy: "擁擠", packed: "極擁擠", closed: "當日休息" },
      constraints: [["路線分區合理", "每日集中一個可步行片區，避免跨島亂跑"], ["避開人潮熱點", "熱門點安排較早到達，並加入附近舊區導流"], ["帶旺舊區・本地小店", "行程包含舊區老街與本地老字號，不只停留在熱門景點"]],
      note: "建議熱門景點盡量早到；人流與天氣請以現場為準。",
      distanceNote: "步行距離為坐標加舊城巷道係數的規劃估算；實際道路、樓梯及無障礙安排請以現場導航為準。",
    },
    zh: {
      status: "阿濠开始规划：先理解日期、人数、兴趣和区域，再逐步核实路线。",
      steps: ["理解需求：日期、人数、兴趣、预算与步行偏好", "锁定可步行区域，避免跨岛乱跑", "核实开放时间、人流与导流替代点", "计算路线与预算，输出可验证行程"],
      interests: ["历史", "老街", "美食"], weather: "晴朗舒适・适合步行", found: x => `找到 ${x} 候选景点`,
      open: x => `${x}：开放`, closed: "郑家大屋：每逢周三休息", crowd: (n, c) => `${n} 中午人流：${c}`,
      gem: x => `建议导流至 ${x}`, route: "已排好顺路步行路线", budget: x => `预算合计 MOP ${x}`,
      weatherShort: "晴朗舒适", oneDay: "一日行程", multiDay: n => `${n} 日行程`,
      crowdLabels: { quiet: "宁静", moderate: "适中", busy: "拥挤", packed: "非常拥挤", closed: "当天休息" },
      constraints: [["路线分区合理", "每天集中一个可步行区域，避免跨岛乱跑"], ["避开人潮热点", "热门景点安排较早到达，并加入附近旧区导流"], ["带旺旧区・本地小店", "行程包含旧区老街与本地老字号，不只停留在热门景点"]],
      note: "建议热门景点尽量早到；人流与天气请以现场为准。",
      distanceNote: "步行距离为坐标加旧城巷道系数的规划估算；实际道路、楼梯与无障碍安排请以现场导航为准。",
    },
    en: {
      status: "Ah-Hou starts planning: understand your date, group, interests and district, then verify the route step by step.",
      steps: ["Understand date, group size, interests, budget and walking preference", "Keep the route within walkable districts", "Verify opening hours, crowds and diversion alternatives", "Compute route and budget, then output a verifiable itinerary"],
      interests: ["history", "old streets", "food"], weather: "Comfortable sunshine・good for walking", found: x => `Found candidate stops for ${x}`,
      open: x => `${x}: open`, closed: "Mandarin's House: closed on Wednesday", crowd: (n, c) => `${n} at noon: ${c}`,
      gem: x => `Suggest diverting to ${x}`, route: "Walkable route computed", budget: x => `Estimated total MOP ${x}`,
      weatherShort: "Comfortable", oneDay: "1-day trip", multiDay: n => `${n}-day trip`,
      crowdLabels: { quiet: "quiet", moderate: "moderate", busy: "busy", packed: "packed", closed: "closed" },
      constraints: [["Coherent district routing", "Each day focuses on one walkable district instead of crossing islands randomly"], ["Crowd-aware timing", "Popular stops are timed earlier, with nearby old-lane diversions"], ["Supports old districts and local shops", "The trip includes old lanes and local shops, not only famous hotspots"]],
      note: "Arrive early at popular stops; crowd and weather conditions should be checked on site.",
      distanceNote: "Walking distance is a planning estimate from coordinates plus an old-lane factor; follow on-site routing, stairs and accessibility guidance.",
    },
    pt: {
      status: "Ah-Hou começa a planear: compreende data, grupo, interesses e zona, e depois verifica a rota passo a passo.",
      steps: ["Compreender data, pessoas, interesses, orçamento e caminhada", "Manter cada dia numa zona caminhável", "Verificar horários, multidões e alternativas", "Calcular rota e orçamento e criar um roteiro verificável"],
      interests: ["história", "ruas antigas", "comida"], weather: "Sol agradável・bom para caminhar", found: x => `Encontrados pontos para ${x}`,
      open: x => `${x}: aberto`, closed: "Casa do Mandarim: encerrada à quarta-feira", crowd: (n, c) => `${n} ao meio-dia: ${c}`,
      gem: x => `Sugestão de desvio para ${x}`, route: "Rota caminhável calculada", budget: x => `Total estimado MOP ${x}`,
      weatherShort: "Agradável", oneDay: "1 dia", multiDay: n => `${n} dias`,
      crowdLabels: { quiet: "tranquilo", moderate: "moderado", busy: "movimentado", packed: "muito cheio", closed: "encerrado" },
      constraints: [["Rota coerente por zonas", "Cada dia fica numa zona caminhável, sem cruzar ilhas ao acaso"], ["Horários atentos às multidões", "Os pontos populares ficam mais cedo e incluem desvios para ruas antigas"], ["Apoio a bairros e lojas locais", "O roteiro inclui ruas antigas e lojas locais, não apenas atrações famosas"]],
      note: "Chegue cedo aos locais populares; confirme multidões e tempo no próprio dia.",
      distanceNote: "A distância a pé é uma estimativa por coordenadas e fator de ruas antigas; confirme vias, escadas e acessibilidade no local.",
    },
    ja: {
      status: "阿濠が計画を開始：日付、人数、興味、エリアを理解し、ルートを一段ずつ確認します。",
      steps: ["日付・人数・興味・予算・歩行希望を理解", "1日を徒歩圏の1エリアに限定", "営業時間・人流・代替スポットを確認", "ルートと予算を計算し検証可能な旅程を作成"],
      interests: ["歴史", "旧市街", "グルメ"], weather: "快適な晴れ・徒歩向き", found: x => `${x}の候補スポットを発見`,
      open: x => `${x}：開館`, closed: "鄭家屋敷：水曜日休館", crowd: (n, c) => `${n}の正午の人流：${c}`,
      gem: x => `${x}への分散を提案`, route: "徒歩ルートを計算済み", budget: x => `合計見積 MOP ${x}`,
      weatherShort: "快適", oneDay: "日帰り", multiDay: n => `${n}日間の旅`,
      crowdLabels: { quiet: "静か", moderate: "普通", busy: "混雑", packed: "非常に混雑", closed: "休館" },
      constraints: [["エリア別の合理的なルート", "1日1つの徒歩圏に集中し、無理な島間移動を避けます"], ["混雑を考慮した時間設定", "人気スポットを早めに訪れ、近くの旧市街へ分散します"], ["旧市街と地元店を応援", "有名観光地だけでなく、古い路地と地元店を含めます"]],
      note: "人気スポットは早めがおすすめです。人流と天気は当日の状況をご確認ください。",
      distanceNote: "歩行距離は座標と旧市街係数による計画上の推定です。道路・階段・バリアフリーは現地案内をご確認ください。",
    },
  };

  const SCENARIO_EXTRA = {
    family: {
      zh: ["爸妈轻松历史美食一日游", "行程集中在半岛历史城区，先到大三巴，再导流到草堆街、福隆新街与本地老字号，少跨区、少走冤枉路。", "澳门半岛历史城区", "大三巴牌坊", "大三巴牌坊", "草堆街与烂鬼楼", "已根据人流与距离调整停留顺序。", "大三巴中午人多，改以草堆街与烂鬼楼分流，距离近、人少又地道。"],
      pt: ["Dia tranquilo de património e gastronomia com os pais", "Uma rota compacta na península: Ruínas de São Paulo, ruas antigas e uma casa de noodles local, com pouca caminhada.", "património da Península de Macau", "Ruínas de São Paulo", "Ruínas de São Paulo", "Rua das Estalagens", "Ordem ajustada conforme multidões e distância.", "As Ruínas ficam cheias ao meio-dia; o percurso distribui visitantes pela próxima Rua das Estalagens."],
      ja: ["両親と巡るゆったり歴史・グルメ日帰り旅", "半島の歴史地区に集中し、聖ポール天主堂跡から古い路地と地元麺店へ。移動を少なくしたルートです。", "マカオ半島の歴史地区", "聖ポール天主堂跡", "聖ポール天主堂跡", "草堆街", "人流と距離に合わせて順番を調整しました。", "正午の混雑を避け、近くの草堆街へ人流を分散します。"],
    },
    multi: {
      zh: ["澳门三天两夜深度游", "三天分区：第一天半岛世遗与旧区，第二天氹仔美食与葡式建筑，第三天路环慢生活与本地小店。", "半岛、氹仔、路环", "大三巴牌坊", "大三巴牌坊", "草堆街与烂鬼楼", "已根据每天的人流与距离调整路线。", "把大三巴的人流分散到附近旧区老街与本地小店。"],
      pt: ["Viagem profunda de 3 dias e 2 noites em Macau", "Três dias por zonas: património e ruas antigas na península, gastronomia e arquitetura em Taipa, vida lenta e lojas locais em Coloane.", "Península, Taipa e Coloane", "Ruínas de São Paulo", "Ruínas de São Paulo", "Rua das Estalagens", "Rotas diárias ajustadas por multidões e distância.", "A multidão das Ruínas é distribuída pelas ruas antigas e lojas locais próximas."],
      ja: ["マカオ3日2泊ディープトリップ", "1日目は半島の世界遺産と旧市街、2日目はタイパのグルメとポルトガル建築、3日目はコロアンのスローライフです。", "半島・タイパ・コロアン", "聖ポール天主堂跡", "聖ポール天主堂跡", "草堆街", "日ごとに人流と距離を考慮して調整しました。", "聖ポールの混雑を近くの古い路地と地元店へ分散します。"],
    },
    coloane: {
      zh: ["路环渔村慢生活一日游", "路线集中在路环旧村，串联小教堂、海边老街、渔村信仰与葡挞老店，全程不跨岛。", "路环渔村与慢生活", "安德鲁饼店", "安德鲁饼店", "路环谭公庙", "已把热门葡挞店安排在非高峰时段。", "安德鲁饼店人多时，先到附近谭公庙与海边老街慢游，再错峰品尝葡挞。"],
      pt: ["Dia tranquilo na aldeia piscatória de Coloane", "Uma rota só pela antiga vila de Coloane: capela, ruas costeiras, templo de pescadores e a histórica pastelaria de ovos.", "aldeia e vida lenta de Coloane", "Lord Stow's Bakery", "Lord Stow's Bakery", "Templo de Tam Kong", "A pastelaria popular foi colocada fora da hora de ponta.", "Quando a Lord Stow's está cheia, visite primeiro o Templo de Tam Kong e as ruas costeiras."],
      ja: ["コロアン漁村のスロー日帰り旅", "コロアン旧村だけを歩き、礼拝堂、海辺の路地、漁村信仰、エッグタルトの老舗を巡ります。", "コロアン漁村とスローライフ", "ロード・ストウズ・ベーカリー", "ロード・ストウズ・ベーカリー", "譚公廟", "人気のベーカリーをピーク外に調整しました。", "ベーカリー混雑時は先に譚公廟と海辺の路地を巡り、時間をずらします。"],
    },
    couple: {
      zh: ["情侣旧区拍照小吃半日游", "路线围绕恋爱巷、议事亭前地与福隆新街，兼顾拍照、旧区氛围和甜品小吃。", "情侣拍照与街头小吃", "议事亭前地", "议事亭前地", "福隆新街", "已调整到较少人流的拍照时段。", "议事亭人流密集时，转入福隆新街拍照并带旺旧区小店。"],
      pt: ["Passeio de casal: fotos e petiscos no bairro antigo", "Uma rota compacta pela Travessa da Paixão, Largo do Senado e Rua da Felicidade, com fotos, ambiente antigo e sobremesa.", "fotos de casal e comida de rua", "Largo do Senado", "Largo do Senado", "Rua da Felicidade", "Ordem ajustada para fotografar com menos multidões.", "Quando o Senado enche, o percurso segue para a Rua da Felicidade e as lojas locais."],
      ja: ["カップル向け旧市街フォト＆食べ歩き", "恋愛巷、セナド広場、福隆新街を結ぶ徒歩ルート。写真、旧市街の雰囲気、スイーツを楽しめます。", "カップル向け写真スポットと食べ歩き", "セナド広場", "セナド広場", "福隆新街", "人の少ない撮影時間に合わせて調整しました。", "セナド広場の混雑時は福隆新街へ移動し、地元店にも立ち寄ります。"],
    },
    mandarin: {
      zh: ["郑家大屋附近历史老街替代路线", "由于郑家大屋星期三休息，行程自动改为恋爱巷、卢家大屋、草堆街与十月初五街，保持同区历史主题。", "郑家大屋附近历史老街", "郑家大屋", "郑家大屋", "恋爱巷", "郑家大屋星期三休息，已自动改为同区开放的历史景点。", "郑家大屋休息，路线改往同片区的恋爱巷与卢家大屋。"],
      pt: ["Rota histórica alternativa perto da Casa do Mandarim", "Como a Casa do Mandarim encerra à quarta-feira, a rota muda para Travessa da Paixão, Casa de Lou Kau e ruas históricas próximas.", "ruas históricas perto da Casa do Mandarim", "Casa do Mandarim", "Casa do Mandarim", "Travessa da Paixão", "A Casa do Mandarim fecha à quarta; foi substituída por locais históricos abertos na mesma zona.", "A Casa do Mandarim está fechada; a rota muda para a Travessa da Paixão e a Casa de Lou Kau."],
      ja: ["鄭家屋敷周辺の歴史路地・代替ルート", "水曜日は鄭家屋敷が休館のため、恋愛巷、盧家屋敷、草堆街、十月初五日街へ自動変更します。", "鄭家屋敷周辺の歴史路地", "鄭家屋敷", "鄭家屋敷", "恋愛巷", "水曜休館のため、同じエリアの開館中の歴史スポットへ変更しました。", "鄭家屋敷の休館に対応し、恋愛巷と盧家屋敷へ自動変更します。"],
    },
    taipa: {
      zh: ["氹仔半天地道美食路线", "半天集中在氹仔旧城区，官也街、龙环葡韵、猪扒包与大菜糕全部步行可达。", "氹仔半天地道美食", "官也街", "官也街", "龙环葡韵", "已根据人流与距离调整停留顺序。", "官也街人多时，先到龙环葡韵散步拍照，再回到小店品尝猪扒包。"],
      pt: ["Meio dia gastronómico autêntico em Taipa", "Meio dia concentrado na Taipa antiga: Rua do Cunha, Casas-Museu, sanduíche de costeleta e sobremesa, tudo a pé.", "gastronomia local de meio dia em Taipa", "Rua do Cunha", "Rua do Cunha", "Casas-Museu da Taipa", "Ordem ajustada conforme multidões e distância.", "Quando a Rua do Cunha fica cheia, visite primeiro as Casas-Museu e volte depois para a comida local."],
      ja: ["タイパ半日ローカルグルメ散歩", "官也街、タイパ・ハウス、ポークチョップバーガー、大菜糕を徒歩で巡る半日ルートです。", "タイパ半日ローカルグルメ", "官也街", "官也街", "タイパ・ハウス", "人流と距離に合わせて順番を調整しました。", "官也街が混雑する時は先にタイパ・ハウスを散策し、その後地元グルメへ戻ります。"],
    },
    first: {
      zh: ["第一次来澳门经典深度路线", "第一次来澳门先看大三巴与议事亭前地，再转入福隆新街与老字号食店，经典但不只停留在热点。", "澳门经典景点与旧区老街", "大三巴牌坊", "大三巴牌坊", "草堆街与烂鬼楼", "已根据人流与距离调整停留顺序。", "把大三巴的人流分散到草堆街与本地小店。"],
      pt: ["Primeira visita: património e ruas antigas de Macau", "Para a primeira visita: Ruínas e Senado, depois Rua da Felicidade e uma casa de noodles tradicional, indo além dos hotspots.", "clássicos e ruas antigas de Macau", "Ruínas de São Paulo", "Ruínas de São Paulo", "Rua das Estalagens", "Ordem ajustada conforme multidões e distância.", "A multidão das Ruínas é desviada para a Rua das Estalagens e lojas locais."],
      ja: ["初めてのマカオ：世界遺産と旧市街", "初訪問なら聖ポール天主堂跡とセナド広場から、福隆新街と老舗麺店へ。有名地だけに偏らないルートです。", "マカオの定番と古い路地", "聖ポール天主堂跡", "聖ポール天主堂跡", "草堆街", "人流と距離に合わせて順番を調整しました。", "聖ポールの混雑を草堆街と地元店へ分散します。"],
    },
  };

  function scenarioWords(scenario, lang) {
    if (lang === "zh" || lang === "pt" || lang === "ja") {
      const x = SCENARIO_EXTRA[scenario.key][lang];
      return { title: x[0], summary: x[1], search: x[2], anchor: x[3], from: x[4], to: x[5], recovery: x[6], diversion: x[7] };
    }
    const z = lang.startsWith("zh");
    return {
      title: z ? scenario.titleZh : scenario.titleEn,
      summary: z ? scenario.summaryZh : scenario.summaryEn,
      search: z ? scenario.searchLabelZh : scenario.searchLabelEn,
      anchor: z ? scenario.anchorNameZh : scenario.anchorNameEn,
      from: z ? scenario.diversionFromZh : scenario.diversionFromEn,
      to: z ? scenario.diversionToZh : scenario.diversionToEn,
      recovery: z ? scenario.recoveryZh : scenario.recoveryEn,
      diversion: z ? scenario.diversionZh : scenario.diversionEn,
    };
  }

  const DAY_TITLES = {
    family: { "zh-HK": ["Day 1 · 半島歷史城區"], zh: ["第 1 天 · 半岛历史城区"], en: ["Day 1 · Peninsula Heritage"], pt: ["Dia 1 · Património da Península"], ja: ["1日目 · 半島歴史地区"] },
    multi: { "zh-HK": ["Day 1 · 半島世遺與舊區", "Day 2 · 氹仔美食舊城", "Day 3 · 路環慢活"], zh: ["第 1 天 · 半岛世遗与旧区", "第 2 天 · 氹仔美食旧城", "第 3 天 · 路环慢生活"], en: ["Day 1 · Peninsula Heritage", "Day 2 · Taipa Food & Old Town", "Day 3 · Slow Coloane"], pt: ["Dia 1 · Património da Península", "Dia 2 · Gastronomia de Taipa", "Dia 3 · Coloane sem pressa"], ja: ["1日目 · 半島世界遺産", "2日目 · タイパのグルメ", "3日目 · コロアンでスロー旅"] },
    coloane: { "zh-HK": ["Day 1 · 路環漁村慢活"], zh: ["第 1 天 · 路环渔村慢生活"], en: ["Day 1 · Slow Coloane Village"], pt: ["Dia 1 · Vila de Coloane sem pressa"], ja: ["1日目 · コロアン漁村スロー旅"] },
    couple: { "zh-HK": ["Day 1 · 舊區拍照與甜品"], zh: ["第 1 天 · 旧区拍照与甜品"], en: ["Day 1 · Old-Town Photos & Dessert"], pt: ["Dia 1 · Fotos e sobremesa no bairro antigo"], ja: ["1日目 · 旧市街フォト＆スイーツ"] },
    mandarin: { "zh-HK": ["Day 1 · 歷史老街替代線"], zh: ["第 1 天 · 历史老街替代路线"], en: ["Day 1 · Historic-Lane Alternative"], pt: ["Dia 1 · Alternativa pelas ruas históricas"], ja: ["1日目 · 歴史路地の代替ルート"] },
    taipa: { "zh-HK": ["Day 1 · 氹仔半日美食"], zh: ["第 1 天 · 氹仔半天美食"], en: ["Day 1 · Taipa Half-Day Food Walk"], pt: ["Dia 1 · Gastronomia de Taipa"], ja: ["1日目 · タイパ半日グルメ"] },
    first: { "zh-HK": ["Day 1 · 初訪澳門"], zh: ["第 1 天 · 初访澳门"], en: ["Day 1 · First-Time Macau"], pt: ["Dia 1 · Primeira visita a Macau"], ja: ["1日目 · 初めてのマカオ"] },
  };

  function staticTraceCopy(lang, scenario) {
    const U = STATIC_UI[lang] || STATIC_UI.en;
    const S = scenarioWords(scenario, lang);
    const crowd = U.crowdLabels[scenario.crowdLabelEn] || scenario.crowdLabelEn;
    return {
      status: U.status, steps: U.steps, interests: U.interests, weather: U.weather,
      search: U.found(S.search),
      open: scenario.key === "mandarin" ? U.closed : U.open(S.anchor),
      crowd: U.crowd(S.anchor, crowd), gem: U.gem(S.to), route: U.route,
      budget: U.budget(scenario.budget), recovery: S.recovery, diversion: S.diversion,
    };
  }

  const LANG_LABEL = { "zh-HK": "粵語（澳門）", zh: "简体中文", en: "English", pt: "Português", ja: "日本語" };

  function addDays(iso, n) {
    const [y, m, d] = iso.split("-").map(Number);
    const dt = new Date(Date.UTC(y, m - 1, d + n));
    return dt.toISOString().slice(0, 10);
  }

  function staticItineraryForScenario(lang, scenario, multi) {
    const z = lang.startsWith("zh");
    const U = STATIC_UI[lang] || STATIC_UI.en;
    const S = scenarioWords(scenario, lang);
    const localize = (s) => {
      let w = (s.why && typeof s.why === "object") ? (z ? s.why.zh : (s.why.en || s.why.zh)) : s.why;
      if (lang === "pt") w = s.local_business ? "Uma paragem local autêntica que apoia o comércio do bairro." : "Uma paragem escolhida pela sua história, ambiente e rota caminhável.";
      if (lang === "ja") w = s.local_business ? "地元らしさを楽しみ、地域のお店も応援できるスポットです。" : "歴史・雰囲気・歩きやすさを考えて選んだスポットです。";
      const bz = (s.why && typeof s.why === "object") ? s.why.zh : w;
      const be = (lang === "pt" || lang === "ja") ? w :
        ((s.why && typeof s.why === "object") ? (s.why.en || w) : w);
      const crowd = { ...s.crowd, label: U.crowdLabels[s.crowd.label_en] || s.crowd.label_en };
      return { ...s, why: w, blurb: { zh: bz, en: be }, crowd };
    };
    const localizedDayTitles = (DAY_TITLES[scenario.key] || {})[lang] || (DAY_TITLES[scenario.key] || {}).en || [];
    const days = scenario.daysData.map((d, i) => {
      const dd = makeDay(i + 1, localizedDayTitles[i] || d.title, d.stops.map(localize));
      dd.date = addDays(today, i);
      return dd;
    });
    const all = days.flatMap(d => d.stops.map(s => ({ ...s, day_no: d.day_no, map_order: `${d.day_no}-${s.order}` })));
    return {
      title: S.title, summary: S.summary,
      language: lang, language_name: LANG_LABEL[lang] || lang,
      date: multi ? `${today} → ${addDays(today, scenario.days - 1)}` : today,
      weekday: multi ? U.multiDay(scenario.days) : U.oneDay,
      weather: { condition: U.weatherShort, temp_c: 28 },
      days: multi ? days : undefined,
      totals: summarize(all),
      constraints: U.constraints.map(x => ({ label: x[0], ok: true, detail: x[1] })),
      constraints_title: staticMode ? tt("constraintsStatic") : tt("constraintsTitle"),
      diversions: [{ from: S.from, to: S.to, reason: S.diversion }],
      notes: [U.note, U.distanceNote],
      stops: all,
    };
  }

  function scenarioBase(key, overrides) {
    return {
      key, days: 1, people: 2, checkId: "ruins_st_paul", anchorId: "ruins_st_paul",
      anchorNameZh: "大三巴牌坊", anchorNameEn: "Ruins of St. Paul's",
      crowdLabelZh: "極擁擠", crowdLabelEn: "packed",
      searchLabelZh: "半島歷史城區", searchLabelEn: "Macau Peninsula heritage",
      interests: ["歷史", "老街", "美食"], budget: 260,
      recoveryZh: "已根據人流與距離微調停留順序。", recoveryEn: "Stop order adjusted based on crowds and walking distance.",
      diversionFromZh: "大三巴牌坊", diversionFromEn: "Ruins of St. Paul's",
      diversionToZh: "草堆街與爛鬼樓", diversionToEn: "Rua das Estalagens",
      diversionZh: "大三巴正午人多，改以草堆街與爛鬼樓分流，步行近、人少又地道。",
      diversionEn: "St. Paul's gets crowded at noon, so the route diverts into Rua das Estalagens, nearby and more local.",
      ...overrides,
    };
  }

  function scenarioFamily() {
    const stops = [
      poi("ruins_st_paul", 1, "大三巴牌坊", "Ruins of St. Paul's", "Ruínas de São Paulo", "heritage", 22.19755, 113.54086, "assets/poi/ruins_st_paul.jpg", true, false, false, "10:00", "10:45", 0, "packed", { zh: "世界遺產地標，最適合早上避開人潮。", en: "The UNESCO landmark — best visited early to dodge crowds." }),
      poi("rua_estalagens", 2, "草堆街與爛鬼樓", "Rua das Estalagens", "Rua das Estalagens", "street", 22.19488, 113.53868, "assets/poi/rua_estalagens.jpg", false, true, true, "10:53", "11:18", 0, "quiet", { zh: "舊區老街，人少地道，適合帶爸媽慢慢行。", en: "A quiet old lane, authentic and easy to stroll with parents." }),
      poi("rua_felicidade", 3, "福隆新街", "Rua da Felicidade", "Rua da Felicidade", "street", 22.19283, 113.53894, "assets/poi/rua_felicidade.jpg", false, true, true, "11:26", "11:56", 0, "moderate", { zh: "紅窗門老街，既有故事亦有手信小店。", en: "The red-shutter street, full of stories and souvenir shops." }),
      poi("wong_chi_kei", 4, "黃枝記粥麵", "Wong Chi Kei Noodles", "Wong Chi Kei", "food", 22.19360, 113.53980, "assets/poi/wong_chi_kei.jpg", false, true, true, "12:05", "12:50", 210, "busy", { zh: "本地老字號，午餐兼支持街坊小店。", en: "A beloved local noodle house for lunch that supports the neighbourhood." }),
    ];
    return scenarioBase("family", { people: 3, budget: 210, titleZh: "爸媽輕鬆歷史美食一日遊", titleEn: "Easy Heritage & Local Food Day with Parents", summaryZh: "行程集中半島歷史城區，先到大三巴，再導流到草堆街、福隆新街與本地老字號，少跨區、少走冤枉路。", summaryEn: "A compact peninsula route: start at St. Paul's, then divert into old lanes and a local noodle shop, keeping walking light.", daysData: [{ title: "Day 1 · 半島歷史城區", stops }] });
  }

  function scenarioMulti() {
    const day1 = scenarioFamily().daysData[0].stops;
    const day2 = scenarioTaipa().daysData[0].stops;
    const day3 = [
      poi("st_francis_coloane", 1, "路環聖方濟各聖堂", "Chapel of St. Francis Xavier", "Capela de São Francisco Xavier", "temple", 22.11649, 113.55560, "assets/poi/st_francis_coloane.jpg", false, true, false, "10:30", "10:55", 0, "quiet", { zh: "路環海邊小教堂，節奏慢、拍照舒服。", en: "A seaside chapel in Coloane — slow-paced and photogenic." }),
      poi("lord_stow", 2, "安德魯餅店（路環總店）", "Lord Stow's Bakery", "Lord Stow's Bakery", "food", 22.11760, 113.55480, "assets/poi/lord_stow.jpg", false, true, true, "11:03", "11:28", 80, "busy", { zh: "葡撻創始店，路環慢活線的代表本地小店。", en: "Birthplace of the Macau egg tart and Coloane's iconic local shop." }),
      poi("coloane_village", 3, "路環市區", "Coloane Village", "Vila de Coloane", "street", 22.11680, 113.55540, "assets/poi/coloane_village.jpg", false, true, true, "11:35", "12:20", 0, "moderate", { zh: "海邊小村保留彩色平房與街坊節奏。", en: "A seaside village of pastel houses keeping its neighbourhood rhythm." }),
    ];
    return scenarioBase("multi", { days: 3, people: 2, budget: 380, endDate: "Day 3", searchLabelZh: "半島、氹仔、路環", searchLabelEn: "Peninsula, Taipa and Coloane", titleZh: "澳門三日兩夜深度遊", titleEn: "Three-Day Macau Deep Trip", summaryZh: "三日分區：第一日半島世遺與舊區，第二日氹仔美食與葡式建築，第三日路環慢活與本地小店。", summaryEn: "Three coherent days: peninsula heritage and old lanes, Taipa food and Portuguese houses, then Coloane slow living and local shops.", daysData: [{ title: "Day 1 · 半島世遺與舊區", stops: day1 }, { title: "Day 2 · 氹仔美食舊城", stops: day2 }, { title: "Day 3 · 路環慢活", stops: day3 }] });
  }

  function scenarioColoane() {
    const stops = [
      poi("st_francis_coloane", 1, "路環聖方濟各聖堂", "Chapel of St. Francis Xavier", "Capela de São Francisco Xavier", "temple", 22.11649, 113.55560, "assets/poi/st_francis_coloane.jpg", false, true, false, "10:00", "10:25", 0, "quiet", { zh: "海邊鵝黃小教堂，適合由寧靜廣場開始慢遊。", en: "A cream-yellow seaside chapel — a calm start to the village walk." }),
      poi("coloane_village", 2, "路環市區", "Coloane Village", "Vila de Coloane", "street", 22.11680, 113.55540, "assets/poi/coloane_village.jpg", false, true, true, "10:31", "11:16", 0, "moderate", { zh: "彩色平房、碼頭與小店保留路環漁村節奏。", en: "Pastel houses, piers and local shops preserve Coloane's fishing-village rhythm." }),
      poi("tam_kung_temple", 3, "路環譚公廟", "Tam Kung Temple, Coloane", "Templo de Tam Kong", "temple", 22.11640, 113.55495, "assets/poi/tam_kung_temple.jpg", false, true, false, "11:22", "11:42", 0, "quiet", { zh: "漁村信仰小廟，人少又有海邊老街味。", en: "A quiet fishing-village temple with sea breeze and old-lane character." }),
      poi("lord_stow", 4, "安德魯餅店（路環總店）", "Lord Stow's Bakery", "Lord Stow's Bakery", "food", 22.11760, 113.55480, "assets/poi/lord_stow.jpg", false, true, true, "11:50", "12:15", 40, "busy", { zh: "葡撻創始店，錯開正午高峰後幫襯路環老店。", en: "The birthplace of the Macau egg tart, timed before the lunch peak." }),
    ];
    return scenarioBase("coloane", {
      people: 1, budget: 40, anchorId: "lord_stow", checkId: "st_francis_coloane",
      anchorNameZh: "安德魯餅店", anchorNameEn: "Lord Stow's Bakery",
      crowdLabelZh: "擁擠", crowdLabelEn: "busy",
      searchLabelZh: "路環漁村與慢活", searchLabelEn: "Coloane village and slow living",
      diversionFromZh: "安德魯餅店", diversionFromEn: "Lord Stow's Bakery",
      diversionToZh: "路環譚公廟", diversionToEn: "Tam Kung Temple",
      recoveryZh: "已把熱門葡撻店安排喺非高峰時段。",
      recoveryEn: "The popular bakery is scheduled outside its busiest window.",
      diversionZh: "安德魯餅店人多時，先行附近譚公廟與海邊老街，再錯峰食葡撻。",
      diversionEn: "When the bakery is busy, visit Tam Kung Temple and the waterfront lanes first.",
      titleZh: "路環漁村慢活一日遊",
      titleEn: "Slow Coloane Fishing-Village Day",
      summaryZh: "行程集中路環舊村，串連小教堂、海邊老街、漁村信仰與葡撻老店，全日唔跨島。",
      summaryEn: "A coherent Coloane Village walk through its chapel, waterfront lanes, fishing faith and historic egg-tart bakery.",
      daysData: [{ title: "Day 1 · 路環漁村慢活", stops }],
    });
  }

  function scenarioCouple() {
    const stops = [
      poi("travessa_paixao", 1, "戀愛巷", "Travessa da Paixão", "Travessa da Paixão", "street", 22.19719, 113.54040, "assets/poi/travessa_paixao.jpg", false, true, false, "15:00", "15:20", 0, "busy", { zh: "粉色斜巷最適合情侶影相，鄰近大三巴但更有氛圍。", en: "The pink 'Love Lane' — a couple-photo classic beside St. Paul's." }),
      poi("senado_square", 2, "議事亭前地", "Senado Square", "Largo do Senado", "heritage", 22.19398, 113.53995, "assets/poi/senado_square.jpg", true, false, false, "15:30", "16:00", 0, "packed", { zh: "葡式波浪地與粉彩建築，是第一次來澳門必拍點。", en: "Portuguese wave pavement and pastel façades — an essential photo stop." }),
      poi("rua_felicidade", 3, "福隆新街", "Rua da Felicidade", "Rua da Felicidade", "street", 22.19283, 113.53894, "assets/poi/rua_felicidade.jpg", false, true, true, "16:08", "16:38", 0, "moderate", { zh: "紅窗門老街，兼具電影感與舊區小店。", en: "The cinematic red-shutter street lined with old-town shops." }),
      poi("yee_shun_milk", 4, "義順鮮奶", "Yee Shun Milk Company", "Leitaria I Son", "food", 22.19305, 113.53945, "assets/poi/yee_shun_milk.jpg", false, true, true, "16:46", "17:16", 90, "moderate", { zh: "雙皮燉奶老字號，適合拍照後食甜品。", en: "The double-skin milk pudding classic — perfect dessert after photos." }),
    ];
    return scenarioBase("couple", { people: 2, anchorId: "senado_square", checkId: "travessa_paixao", anchorNameZh: "議事亭前地", anchorNameEn: "Senado Square", diversionFromZh: "議事亭前地", diversionFromEn: "Senado Square", diversionToZh: "福隆新街", diversionToEn: "Rua da Felicidade", diversionZh: "議事亭人流密集，轉入福隆新街影相兼帶旺舊區小店。", diversionEn: "Senado gets crowded, so the route shifts into Rua da Felicidade for photos and local shops.", searchLabelZh: "情侶拍照與街頭小食", searchLabelEn: "couple photo spots and street food", titleZh: "情侶舊區拍照小食半日遊", titleEn: "Couple Photo Spots and Street Food Walk", summaryZh: "路線圍繞戀愛巷、議事亭與福隆新街，兼顧拍照、舊區氛圍與甜品小食。", summaryEn: "A compact route through romantic lanes, Senado and Rua da Felicidade, balancing photos, old-town atmosphere and dessert.", daysData: [{ title: "Day 1 · 舊區拍照與甜品", stops }] });
  }

  function scenarioMandarin() {
    const stops = [
      poi("travessa_paixao", 1, "戀愛巷", "Travessa da Paixão", "Travessa da Paixão", "street", 22.19719, 113.54040, "assets/poi/travessa_paixao.jpg", false, true, false, "10:00", "10:20", 0, "moderate", { zh: "鄭家大屋週三休息，改以同區歷史巷弄作替代。", en: "Mandarin's House rests on Wednesday, so nearby historic lanes step in." }),
      poi("lou_kau_mansion", 2, "盧家大屋", "Lou Kau Mansion", "Casa de Lou Kau", "heritage", 22.19460, 113.54020, "assets/poi/lou_kau_mansion.jpg", true, false, false, "10:30", "11:00", 0, "quiet", { zh: "同樣是中西合璧大宅，能補足歷史民居脈絡。", en: "Another East-meets-West mansion that keeps the heritage theme intact." }),
      poi("rua_estalagens", 3, "草堆街與爛鬼樓", "Rua das Estalagens", "Rua das Estalagens", "street", 22.19488, 113.53868, "assets/poi/rua_estalagens.jpg", false, true, true, "11:08", "11:33", 0, "quiet", { zh: "孫中山藥局舊址一帶，歷史味濃、人流少。", en: "Around Sun Yat-sen's old pharmacy — deep history, few tourists." }),
      poi("rua_cinco", 4, "十月初五街", "Rua de Cinco de Outubro", "Rua de Cinco de Outubro", "street", 22.19565, 113.53710, "assets/poi/rua_cinco.jpg", false, true, true, "11:43", "12:08", 0, "moderate", { zh: "內港老街與街坊小店，最能體驗澳門日常。", en: "The Inner Harbour's old street of everyday Macau life." }),
    ];
    return scenarioBase("mandarin", { people: 1, anchorId: "mandarin_house", checkId: "mandarin_house", anchorNameZh: "鄭家大屋", anchorNameEn: "Mandarin's House", crowdLabelZh: "當日休息", crowdLabelEn: "closed", diversionFromZh: "鄭家大屋", diversionFromEn: "Mandarin's House", diversionToZh: "戀愛巷", diversionToEn: "Travessa da Paixão", diversionZh: "鄭家大屋逢週三休息，改往同片區的戀愛巷與盧家大屋，保持歷史老街主題。", diversionEn: "Mandarin's House is closed on Wednesday, so the route switches to nearby Travessa da Paixão and Lou Kau Mansion.", recoveryZh: "鄭家大屋逢週三休息，已自動改為同區有開放的歷史巷弄。", recoveryEn: "Mandarin's House is closed on Wednesday, so the route switches to nearby open historic lanes.", searchLabelZh: "鄭家大屋附近歷史老街", searchLabelEn: "historic lanes near Mandarin's House", titleZh: "鄭家大屋附近歷史老街替代路線", titleEn: "Historic Lanes Near Mandarin's House", summaryZh: "針對星期三鄭家大屋休息，行程自動改為戀愛巷、盧家大屋、草堆街與十月初五街，保持同區歷史主題。", summaryEn: "Since Mandarin's House is closed on Wednesday, the route pivots to nearby historic lanes and mansions while keeping the same theme.", daysData: [{ title: "Day 1 · 歷史老街替代線", stops }] });
  }

  function scenarioTaipa() {
    const stops = [
      poi("rua_cunha", 1, "官也街", "Rua do Cunha", "Rua do Cunha", "street", 22.15408, 113.55695, "assets/poi/rua_cunha.jpg", false, true, true, "10:30", "11:10", 0, "busy", { zh: "氹仔美食手信街，半日遊最順路起點。", en: "Taipa's food-and-souvenir street — the natural half-day starting point." }),
      poi("taipa_houses", 2, "龍環葡韻", "Taipa Houses", "Casas-Museu da Taipa", "museum", 22.15389, 113.55944, "assets/poi/taipa_houses.jpg", false, false, false, "11:18", "11:58", 0, "moderate", { zh: "葡式建築與濕地景觀，行完官也街剛好散步。", en: "Portuguese houses and wetland views, a pleasant stroll after Rua do Cunha." }),
      poi("tai_lei_loi", 3, "大利來記豬扒包", "Tai Lei Loi Kei", "Tai Lei Loi Kei", "food", 22.15600, 113.55720, "assets/poi/tai_lei_loi.jpg", false, true, true, "12:08", "12:38", 90, "moderate", { zh: "氹仔豬扒包代表，半日美食重點。", en: "Taipa's signature pork-chop bun — the food highlight of the walk." }),
      poi("mok_yi_kei", 4, "莫義記大菜糕", "Mok Yi Kei", "Mok Yi Kei", "food", 22.15388, 113.55700, "assets/poi/mok_yi_kei.jpg", false, true, true, "12:46", "13:10", 80, "moderate", { zh: "官也街百年甜品老店，用大菜糕作結尾。", en: "A century-old dessert shop — finish with its famous agar jelly." }),
    ];
    return scenarioBase("taipa", { people: 1, anchorId: "rua_cunha", checkId: "rua_cunha", anchorNameZh: "官也街", anchorNameEn: "Rua do Cunha", crowdLabelZh: "擁擠", crowdLabelEn: "busy", diversionFromZh: "官也街", diversionFromEn: "Rua do Cunha", diversionToZh: "龍環葡韻", diversionToEn: "Taipa Houses", diversionZh: "官也街人多時，先轉到龍環葡韻散步拍照，再回到小店食豬扒包。", diversionEn: "When Rua do Cunha is busy, step over to Taipa Houses first, then return for local food.", searchLabelZh: "氹仔半日地道美食", searchLabelEn: "Taipa half-day local food", titleZh: "氹仔半日地道美食線", titleEn: "Taipa Half-Day Local Food Walk", summaryZh: "半日集中氹仔舊城區，官也街、龍環葡韻、豬扒包與大菜糕全部步行可達。", summaryEn: "A compact Taipa Village half-day route: Rua do Cunha, Taipa Houses, pork-chop bun and agar jelly all within walking distance.", daysData: [{ title: "Day 1 · 氹仔半日美食", stops }] });
  }

  function scenarioFirstTime() {
    const stops = [
      poi("ruins_st_paul", 1, "大三巴牌坊", "Ruins of St. Paul's", "Ruínas de São Paulo", "heritage", 22.19755, 113.54086, "assets/poi/ruins_st_paul.jpg", true, false, false, "09:45", "10:30", 0, "busy", { zh: "澳門必到世遺地標，安排最早到避開人潮。", en: "Macau's essential UNESCO landmark, placed early to avoid the heaviest crowds." }),
      poi("senado_square", 2, "議事亭前地", "Senado Square", "Largo do Senado", "heritage", 22.19398, 113.53995, "assets/poi/senado_square.jpg", true, false, false, "10:40", "11:10", 0, "busy", { zh: "葡式碎石廣場，第一次來澳門必看。", en: "The classic Portuguese pavement square, a must-see for first-time visitors." }),
      poi("rua_felicidade", 3, "福隆新街", "Rua da Felicidade", "Rua da Felicidade", "street", 22.19283, 113.53894, "assets/poi/rua_felicidade.jpg", false, true, true, "11:18", "11:48", 0, "moderate", { zh: "紅窗門老街，喺地標以外補一份地道質感。", en: "A red-shutter old lane that adds local texture beyond famous landmarks." }),
      poi("wong_chi_kei", 4, "黃枝記粥麵", "Wong Chi Kei Noodles", "Wong Chi Kei", "food", 22.19360, 113.53980, "assets/poi/wong_chi_kei.jpg", false, true, true, "12:00", "12:45", 140, "busy", { zh: "老字號粥麵，午餐食地道嘢最穩陣。", en: "A reliable old-name noodle stop for local food." }),
    ];
    return scenarioBase("first", { people: 1, titleZh: "第一次來澳門經典深度線", titleEn: "First-Time Macau Heritage and Old Streets", summaryZh: "第一次來澳門先看大三巴與議事亭，再轉入福隆新街與老字號食店，經典但不只停留在熱點。", summaryEn: "For a first visit: see St. Paul's and Senado, then move into Rua da Felicidade and an old-name noodle shop so the route goes beyond hotspots.", daysData: [{ title: "Day 1 · First-time Macau", stops }] });
  }

  function argstr(a) {
    if (!a) return "";
    return Object.entries(a).map(([k, v]) => `${k}=${Array.isArray(v) ? "[" + v.length + "]" : v}`).join("  ");
  }

  function addTrace(kind, icon, html, raw) {
    const li = el("li", "tr " + kind);
    li.innerHTML = `<div class="tr-ic">${icon}</div><div class="tr-body">${raw ? html : `<span class="tr-sum">${esc(html)}</span>`}</div>`;
    $("#trace").appendChild(li); scrollTrace();
  }
  function scrollTrace() { const t = $("#trace"); t.scrollTop = t.scrollHeight; }

  // ---------------- result ----------------
  function renderResult(it) {
    lastItinerary = it;
    $("#resultEmpty").classList.add("hidden");
    const r = $("#result"); r.classList.remove("hidden"); r.innerHTML = "";

    // banner
    const w = it.weather || {};
    const engineLabel = (it.engine || "").startsWith("qwen:")
      ? `${tt("runtimeQwen")} · ${it.engine.replace("qwen:", "")}`
      : (it.engine === "fallback-tools" ? tt("runtimeFallback") : tt("runtimeVerified"));
    const banner = el("div", "r-banner");
    banner.innerHTML =
      `<div class="r-title">${esc(it.title)}</div>` +
      `<p class="r-summary">${esc(it.summary)}</p>` +
      `<div class="r-meta">` +
      metachip("📅", `${it.date} ${it.weekday}`) +
      metachip(weatherIcon(w), `${esc(w.condition || "")} ${w.temp_c != null ? w.temp_c + "°C" : ""}`) +
      ((w.source || "").indexOf("live") >= 0 ? `<span class="metachip live-wx"><span class="mc-ic">📡</span>${esc(tt("weatherLive"))}</span>` : "") +
      metachip("🗣️", it.language_name) +
      metachip("⚙️", engineLabel) +
      `</div>`;
    r.appendChild(banner);

    // stats
    const t = it.totals || {};
    const localSpend = t.local_spend_mop != null ? t.local_spend_mop :
      (it.stops || []).filter(s => s.local_business).reduce((sum, s) => sum + (s.cost_mop || 0), 0);
    const stats = el("div", "stats");
    stats.innerHTML =
      stat(t.stops, tt("stops")) +
      stat(t.walk_km + " km", tt("walkDistance")) +
      stat("MOP " + t.cost_mop, tt("budgetPer"), true) +
      stat(t.old_district, tt("oldLanes")) +
      stat(t.local_business, tt("localShops")) +
      stat("MOP " + localSpend, tt("localSpend"));
    r.appendChild(stats);

    const impact = el("div", "panel impact-panel");
    impact.innerHTML =
      `<h3><span class="p-ic">📈</span>${esc(tt("impactTitle"))}</h3>` +
      `<div class="impact-flow"><span>🔥 Hotspot</span><b>→</b>` +
      `<span>🏘️ ${esc(t.old_district)} ${esc(tt("oldLanes"))}</span><b>→</b>` +
      `<span>🏪 ${esc(t.local_business)} ${esc(tt("localShops"))}</span><b>→</b>` +
      `<span class="impact-spend">MOP ${esc(localSpend)} ${esc(tt("localSpend"))}</span></div>` +
      `<p>${esc(tt("impactPilot"))}</p>`;
    r.appendChild(impact);

    // diversion (signature)
    if (it.diversions && it.diversions.length) {
      const d = el("div", "panel diversion");
      d.innerHTML = `<h3><span class="p-ic">↪️</span>${esc(tt("diversionTitle"))}</h3>`;
      it.diversions.forEach(dv => {
        const row = el("div", "divrow");
        row.innerHTML = `<span class="from">${esc(dv.from)}</span><span class="arrow">→</span>` +
          `<span class="to">${esc(dv.to)}</span><span class="why">${esc(dv.reason)}</span>`;
        d.appendChild(row);
      });
      r.appendChild(d);
    }

    // constraints
    if (it.constraints && it.constraints.length) {
      const c = el("div", "panel");
      c.innerHTML = `<h3><span class="p-ic">✅</span>${esc(it.constraints_title || tt("constraintsTitle"))}</h3>`;
      const list = el("div", "checks");
      it.constraints.forEach(ck => {
        const row = el("div", "check " + (ck.ok ? "ok" : "no"));
        row.innerHTML = `<span class="ck">${ck.ok ? "✓" : "!"}</span>` +
          `<span class="ck-txt"><b>${esc(ck.label)}</b><span>${esc(ck.detail)}</span></span>`;
        list.appendChild(row);
      });
      c.appendChild(list); r.appendChild(c);
    }

    const isMulti = Array.isArray(it.days) && it.days.length > 1;

    if (isMulti) {
      const overview = el("div", "panel days-overview");
      overview.innerHTML = `<h3><span class="p-ic">🗓️</span>${esc(tt("daysOverview"))}</h3>`;
      const grid = el("div", "day-grid");
      it.days.forEach(d => {
        const item = el("div", "day-chip");
        item.innerHTML = `<b>${esc(d.day_title || ("Day " + d.day_no))}</b>` +
          `<span>${esc(d.date)} · ${esc(d.totals.stops)} ${esc(tt("dayStops"))} · ${esc(d.totals.walk_km)} km · MOP ${esc(d.totals.cost_mop)}</span>`;
        grid.appendChild(item);
      });
      overview.appendChild(grid);
      r.appendChild(overview);
    }

    // map
    const mapPanel = el("div", "panel");
    mapPanel.innerHTML = `<h3><span class="p-ic">🗺️</span>${esc(isMulti ? tt("fullMap") : tt("routeMap"))}</h3>` +
      `<p class="map-note">${esc(tt("mapOrderNote"))}</p><div id="map"></div>`;
    r.appendChild(mapPanel);

    // timeline
    if (isMulti) {
      it.days.forEach(d => {
        const dayPanel = el("div", "panel day-panel");
        dayPanel.innerHTML = `<h3><span class="p-ic">📍</span>${esc(d.day_title || ("Day " + d.day_no))}</h3>` +
          `<p class="day-summary">${esc(d.summary)}</p>`;
        const dayStats = el("div", "day-stats");
        dayStats.innerHTML =
          stat(d.totals.stops, tt("dayStops")) +
          stat(d.totals.walk_km + " km", tt("dayWalk")) +
          stat("MOP " + d.totals.cost_mop, tt("dayBudget"), true) +
          stat(d.totals.old_district, tt("dayOld")) +
          stat(d.totals.local_business, tt("dayLocal"));
        dayPanel.appendChild(dayStats);
        const tl = el("div", "timeline");
        d.stops.forEach(s => {
          tl.appendChild(stopCard(s));
          if (s.walk_to_next) {
            const via = (s.walk_to_next.via || []).map(v => v.name).filter(Boolean);
            const viaTxt = via.length ? ` · ${esc(tt("via"))} ${via.map(esc).join("、")}` : "";
            tl.appendChild(el("div", "tl-walk", `🚶 ${esc(tt("walk"))} ${s.walk_to_next.min} ${esc(tt("minutes"))} · ${s.walk_to_next.km} km → ${esc(s.walk_to_next.to)}${viaTxt} · ${esc(tt("walkEstimate"))}`));
          }
        });
        dayPanel.appendChild(tl);
        r.appendChild(dayPanel);
      });
    } else {
      const tl = el("div", "timeline");
      it.stops.forEach(s => {
        tl.appendChild(stopCard(s));
        if (s.walk_to_next) {
          const via = (s.walk_to_next.via || []).map(v => v.name).filter(Boolean);
          const viaTxt = via.length ? ` · ${esc(tt("via"))} ${via.map(esc).join("、")}` : "";
          tl.appendChild(el("div", "tl-walk", `🚶 ${esc(tt("walk"))} ${s.walk_to_next.min} ${esc(tt("minutes"))} · ${s.walk_to_next.km} km → ${esc(s.walk_to_next.to)}${viaTxt} · ${esc(tt("walkEstimate"))}`));
        }
      });
      const tlPanel = el("div", "panel");
      tlPanel.innerHTML = `<h3><span class="p-ic">📍</span>${esc(tt("timeline"))}</h3>`;
      tlPanel.appendChild(tl);
      r.appendChild(tlPanel);
    }

    // notes + actions
    if (it.notes && it.notes.length) {
      const n = el("div", "panel notes");
      n.innerHTML = `<h3><span class="p-ic">📝</span>${esc(tt("notes"))}</h3><ul>${it.notes.map(x => `<li>${esc(x)}</li>`).join("")}</ul>`;
      r.appendChild(n);
    }
    const acts = el("div", "r-actions");
    const pBtn = el("button", "btn btn-ghost", `🖨️ ${esc(tt("print"))}`);
    pBtn.addEventListener("click", printResultOnly);
    const aBtn = el("button", "btn btn-primary", `↻ ${esc(tt("replan"))}`);
    aBtn.addEventListener("click", () => { $("#planner").scrollIntoView({ behavior: "smooth" }); $("#prompt").focus(); });
    acts.appendChild(pBtn); acts.appendChild(aBtn);
    r.appendChild(acts);

    drawMap(it.stops);
    r.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  function stopCard(s) {
    const card = el("div", "tl-stop");
    const lb = s.local_business ? " lb" : "";
    const cat = ["food", "street", "view"].includes(s.category) ? s.category : "";
    const img = s.image
      ? `<div class="tl-img"><img src="${esc(assetPath(s.image))}" alt="${esc(displayPoiName(s))}" loading="eager" decoding="sync" onerror="this.parentElement.classList.add('ph','${cat}');this.parentElement.innerHTML='<span class=&quot;ph-name&quot;>${esc(displayPoiName(s))}</span>'"></div>`
      : `<div class="tl-img ph ${cat}"><span class="ph-name">${esc(s.name.zh)}</span></div>`;
    const badges = [];
    if (s.unesco) badges.push(`<span class="tg unesco">UNESCO</span>`);
    if (s.old_district) badges.push(`<span class="tg old">${esc(tt("oldLanes"))}</span>`);
    if (s.local_business) badges.push(`<span class="tg local">${esc(tt("localShops"))}</span>`);
    const cl = CROWD_CLASS[s.crowd.label_en] || "crowd-moderate";
    badges.push(`<span class="tg ${cl}">${esc(tt("crowd"))}${esc(s.crowd.label)}${s.crowd.wait ? " · " + esc(tt("wait")) + s.crowd.wait + esc(tt("minShort")) : ""}</span>`);
    badges.push(`<span class="tg cost">${s.cost_mop ? esc(tt("approx")) + s.cost_mop : esc(tt("free"))}</span>`);
    if (s.accessibility && typeof s.accessibility.step_free === "boolean") {
      const a = s.accessibility;
      const note = langNow().startsWith("zh") ? (a.note_zh || "") : (a.note_en || a.note_zh || "");
      badges.push(`<span class="tg ${a.step_free ? "access-ok" : "access-warn"}" title="${esc(note)}">` +
        `${a.step_free ? "♿" : "⚠️"} ${esc(tt(a.step_free ? "accessOk" : "accessSteps"))}</span>`);
    }

    const why = `<div class="tl-why"><span class="qz">${esc(tt("ahouSays"))}</span>${esc(s.why)}</div>`;
    const name = displayPoiName(s);
    const secondary = langNow().startsWith("zh") ? (s.name.en || "") : "";
    const blurbText = s.blurb ? (langNow().startsWith("zh") ? (s.blurb.zh || s.blurb.en || "") : (s.blurb.en || s.blurb.zh || "")) : "";
    const blurb = blurbText ? `<div class="tl-blurb">${esc(blurbText)}</div>` : "";
    const picked = pickStory(s);
    const playBtn = picked
      ? `<button type="button" class="story-play" data-poi="${esc(s.poi_id || "")}" aria-pressed="false" aria-label="${esc(tt("story"))}"><span class="story-ic" aria-hidden="true">🔊</span><span class="story-play-label">${esc(tt("storyListen"))}</span></button>`
      : "";
    const voiceHint = picked && packedStoryUrl(s.poi_id || "", langNow() === "zh" ? "zh" : picked.lang)
      ? `<span class="story-voice">${esc(storyVoiceLabel())}</span>`
      : "";
    const story = picked
      ? `<div class="story" data-poi="${esc(s.poi_id || "")}"><div class="story-head">${playBtn}${voiceHint}<button type="button" class="story-more">${esc(tt("story"))}</button></div><p class="story-body" hidden>${esc(picked.text)}</p></div>`
      : "";
    const tip = s.tip ? `<div class="tl-tip">💡 ${esc(s.tip)}</div>` : "";
    const tags = (langNow().startsWith("zh") && s.tags && s.tags.length) ? `<div class="tl-tags">${s.tags.slice(0, 5).map(x => `<span class="mini">${esc(x)}</span>`).join("")}</div>` : "";
    const code = s.local_business
      ? `<div class="tl-code"><button type="button" class="code-btn" data-poi="${esc(s.poi_id || "")}">🎟️ ${esc(tt("codeBtn"))}</button></div>`
      : "";

    card.innerHTML =
      `<div class="tl-time"><span class="ord">${s.order}</span><span class="t">${s.arrive}<br>↓<br>${s.depart}</span></div>` +
      `<div class="tl-card${lb}"><div class="tl-media">${img}<div class="tl-info">` +
      `<div class="tl-name">${esc(name)}${secondary ? `<span class="en">${esc(secondary)}</span>` : ""}</div>` +
      `<div class="tl-badges">${badges.join("")}</div>${why}${blurb}${story}${tip}${tags}${code}` +
      `</div></div></div>`;
    return card;
  }

  function findStopByPoi(poiId) {
    const it = lastItinerary;
    if (!it || !poiId) return null;
    const lists = [];
    if (Array.isArray(it.stops)) lists.push(it.stops);
    (it.days || []).forEach((d) => { if (d && Array.isArray(d.stops)) lists.push(d.stops); });
    for (const list of lists) {
      const hit = list.find((s) => s.poi_id === poiId);
      if (hit) return hit;
    }
    return null;
  }

  function onStoryClick(e) {
    const more = e.target.closest(".story-more");
    if (more) {
      const wrap = more.closest(".story");
      const body = wrap?.querySelector(".story-body");
      if (body) {
        body.hidden = !body.hidden;
        more.classList.toggle("is-open", !body.hidden);
      }
      return;
    }
    const btn = e.target.closest(".story-play");
    if (!btn) return;
    const stop = findStopByPoi(btn.dataset.poi || "");
    if (stop) playStory(stop, btn);
  }

  // one-time visit code: real API on the live server, local mock on static demo
  async function onVisitCodeClick(e) {
    const btn = e.target.closest(".code-btn");
    if (!btn || btn.disabled) return;
    btn.disabled = true;
    const poiId = btn.dataset.poi || "";
    let code = "", offer = "";
    if (!staticMode && poiId) {
      try {
        const r = await fetch("/api/codes/issue", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ poi_id: poiId }),
        });
        if (r.ok) {
          const j = await r.json();
          code = j.code || "";
          offer = j.offer || "";
        }
      } catch (err) { /* live server must not fake a redeemable code */ }
    }
    if (!code) {
      if (!staticMode) {
        toast(tt("codeFail"));
        btn.disabled = false;
        return;
      }
      const ab = "23456789ABCDEFGHJKMNPQRSTUVWXYZ";
      const pick = (n) => Array.from({ length: n }, () => ab[Math.floor(Math.random() * ab.length)]).join("");
      code = `EL-${pick(4)}-${pick(2)}`;
    }
    const wrap = btn.closest(".tl-code");
    if (wrap) {
      wrap.innerHTML =
        `<span class="code-chip">🎟️ ${esc(code)}</span>` +
        (offer ? `<span class="code-offer">${esc(offer)}</span>` : "") +
        `<span class="code-hint">${esc(tt("codeHint"))}</span>`;
    }
  }

  function displayPoiName(s) {
    const l = langNow();
    if (l === "pt" && s.name.pt) return s.name.pt;
    if (!l.startsWith("zh") && s.name.en) return s.name.en;
    return s.name.zh || s.name.en || "";
  }

  function assetPath(path) {
    if (!path) return "";
    if (/^https?:\/\//.test(path)) return path;
    return path.replace(/^\/+/, "");
  }

  function metachip(ic, txt) { return `<span class="metachip"><span class="mc-ic">${ic}</span>${esc(txt)}</span>`; }
  function stat(v, label, hl) { return `<div class="stat${hl ? " hl" : ""}"><b>${esc(v)}</b><span>${esc(label)}</span></div>`; }
  function weatherIcon(w) {
    const c = w.condition || "";
    if (/雨/.test(c)) return "🌧️";
    if (/雷/.test(c)) return "⛈️";
    if (/晴/.test(c)) return "☀️";
    if (/霧/.test(c)) return "🌫️";
    return "⛅";
  }

  // ---------------- map ----------------
  function drawMap(stops) {
    if (map) { map.remove(); map = null; }
    const pts = stops.filter(s => s.lat && s.lng);
    if (!pts.length || !window.L) return;
    map = L.map("map", { scrollWheelZoom: false }).setView([pts[0].lat, pts[0].lng], 16);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19, attribution: "© OpenStreetMap"
    }).addTo(map);
    const latlngs = [];
    pts.forEach(s => {
      latlngs.push([s.lat, s.lng]);
      if (s.walk_to_next && Array.isArray(s.walk_to_next.via)) {
        s.walk_to_next.via.forEach(v => {
          if (v.lat && v.lng) latlngs.push([v.lat, v.lng]);
        });
      }
      const cat = ["food", "street", "view"].includes(s.category) ? s.category : "";
      const icon = L.divIcon({ className: "", html: `<div class="map-pin ${cat}"><span>${esc(s.map_order || s.order)}</span></div>`, iconSize: [34, 34], iconAnchor: [17, 30] });
      L.marker([s.lat, s.lng], { icon }).addTo(map)
        .bindPopup(`<b>${esc(displayPoiName(s))}</b><br>${esc(s.arrive)}–${esc(s.depart)} · ${esc(tt("crowd"))}${esc(s.crowd.label)}`);
    });
    if (latlngs.length > 1) {
      L.polyline(latlngs, { color: "#BE4A3A", weight: 3.5, opacity: .82, lineCap: "round" }).addTo(map);
      map.fitBounds(L.latLngBounds(latlngs).pad(0.18));
    }
    setTimeout(() => map && map.invalidateSize(), 200);
  }

  // ---------------- misc ----------------
  let toastTimer = null;
  function toast(msg) {
    let t = $(".toast");
    if (!t) { t = el("div", "toast"); t.setAttribute("role", "alert"); document.body.appendChild(t); }
    t.textContent = msg; t.classList.add("show");
    clearTimeout(toastTimer); toastTimer = setTimeout(() => t.classList.remove("show"), 2600);
  }

  function printResultOnly() {
    document.body.classList.add("print-result");
    const done = () => document.body.classList.remove("print-result");
    window.addEventListener("afterprint", done, { once: true });
    setTimeout(() => {
      window.print();
      setTimeout(done, 1200);
    }, 50);
  }

  function startJudgeDemo() {
    const samples = (I18N[langNow()] || I18N["zh-HK"]).samples || [];
    $("#prompt").value = samples[3] || samples[0] || "我想去鄭家大屋同附近嘅歷史老街，星期三去";
    $("#planner").scrollIntoView({ behavior: "smooth", block: "start" });
    setTimeout(() => startPlan("fast"), 280);
  }

  $("#planBtn").addEventListener("click", () => startPlan("auto"));
  $("#cancelBtn")?.addEventListener("click", () => {
    if (!running) return;
    es && es.close();
    finish();
    showPlanError(tt("cancelPlan"));
  });
  $("#judgeDemoBtn")?.addEventListener("click", startJudgeDemo);
  $("#result").addEventListener("click", onStoryClick);
  $("#result").addEventListener("click", onVisitCodeClick);
  $("#retryBtn")?.addEventListener("click", () => startPlan(planMode));
  $("#prompt").addEventListener("keydown", (e) => { if ((e.metaKey || e.ctrlKey) && e.key === "Enter") startPlan("auto"); });
  $("#traceToggle").addEventListener("click", () => {
    const trace = $("#trace");
    const hidden = trace.classList.toggle("hidden");
    $("#traceToggle").setAttribute("aria-expanded", hidden ? "false" : "true");
    $("#traceToggle").textContent = hidden ? "▾" : "▴";
  });
  boot();
})();
