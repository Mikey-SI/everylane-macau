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
      statPoi: "個真實澳門景點", statOld: "條舊區老街", statLocal: "間本地老字號", statTools: "項可調用工具",
      plannerTitle: "同阿濠講一句，佢就同你計掂成日行程", plannerSub: "用自然語言講低你嘅需求即可，例如日期、人數、興趣、預算、想唔想行多路。",
      placeholder: "例如：我下星期三想帶爸媽嚟澳門玩一日，鍾意歷史文化同地道美食，預算唔想太貴，又唔想行太多路…",
      hint: "⌘/Ctrl + Enter 快速出發", planBtn: "出發 · 規劃行程", planning: "阿濠規劃緊…",
      traceTitle: "阿濠 · 智能體工作過程", traceToggle: "收合/展開", empty: "阿濠正在落手規劃，行程即將喺度生成…",
      howTitle: "點樣運作：一個真正識得「做任務」嘅智能體", howSub: "對標 QwenPaw 的 ReAct 架構 —— 規劃、調用工具、多步執行、失敗自動恢復。",
      how1h: "理解 & 規劃", how1p: "解析自然語言需求，拆解成日期、人數、興趣、預算、步行偏好，並制定行動計劃。",
      how2h: "調用工具", how2p: "天氣、景點檢索、開放時間核實、人流預測、導流、路線計算、預算估算 —— 7 大工具。",
      how3h: "多步執行", how3p: "逐一核實每個景點，動態整合天氣、人流、地理片區，組裝出可步行嘅順路行程。",
      how4h: "失敗恢復", how4p: "遇到景點當日休息、預算超支、行得太遠，會自動改線、替換、縮減，唔會卡住。",
      valueTitle: "商業價值：一個導流引擎，三方共贏", tourist: "遊客", touristP: "避開人潮、慳錢慳腳骨力，體驗到真正地道、有故事嘅澳門，滿意度與停留時間提升。",
      shop: "舊區小店", shopP: "把集中在大三巴／威尼斯人的客流，導入十月初五街、福隆新街等老街與街坊老字號，<b>帶來真實新客流</b>。可按引流量收費或推「精選商戶」訂閱。",
      city: "城市 / 政府", cityP: "平衡旅遊承載、緩解過度集中、活化舊區與保育文化遺產，契合澳門「世界旅遊休閒中心」定位。",
      valueFoot: "變現路徑：商戶精選訂閱／引流分成 · 酒店與旅行社 API 授權 · 文旅局數據儀表板 · 多語言客群（內地、葡語系、日韓）擴展。",
      footerSub: "「千模百煉」AI 開發者系列之學生競賽 · 參賽方向：澳門文旅 × 舊區活化", participant: "參賽者：SITINIEK（學號 dc227126）", tech: "技術：Qwen / QwenPaw · FastAPI · ReAct Agent", ethics: "AI 倫理：行程由 AI 生成，人流為估算值，請以現場為準；數據來源公開資料。",
      language: "語言", people: "人", interests: "興趣", budget: "預算 MOP", lowWalk: "少行路", daysTrip: "日行程",
      actionPlan: "行動計劃", recovery: "自動改線", noPrompt: "請先講低你想點玩",
      stops: "個站點", walkDistance: "步行距離", budgetPer: "預算/人均", oldLanes: "舊區老街", localShops: "本地小店",
      diversionTitle: "智能導流 · 由人潮熱點帶你去舊區老街", constraintsTitle: "任務完成核對 · 每項條件都已驗證",
      daysOverview: "多日分區總覽 · 每日一個可步行主題", fullMap: "全程地圖 · 多日分區路線", routeMap: "路線地圖 · 順路而行",
      timeline: "行程時間軸", notes: "貼士", print: "列印 / 儲存成 PDF", replan: "再規劃一次",
      dayStops: "站", dayWalk: "步行", dayBudget: "預算", dayOld: "舊區", dayLocal: "小店", walk: "步行", minutes: "分鐘", crowd: "人流：", wait: "約等", minShort: "分", free: "免費", approx: "約 MOP ", ahouSays: "阿濠話：", story: "聽阿濠講古",
      tool: { get_weather: "查天氣", search_attractions: "搜尋景點", check_opening: "核實開放時間", predict_crowd: "預測人流", find_local_gem: "搵本地老街", compute_route: "規劃步行路線", estimate_budget: "估算預算", submit_itinerary: "提交行程" },
      samples: ["我下星期三想帶爸媽嚟澳門玩一日，鍾意歷史文化同地道美食，預算唔想太貴，又唔想行太多路", "幫我安排澳門三日兩夜，想玩半島世遺、氹仔美食同路環慢活", "情侶星期六想行下舊區老街、影靚相，順便試下街頭小食", "我想去鄭家大屋同附近嘅歷史老街，星期三去", "氹仔半日遊，主打地道美食", "First time in Macau this weekend, we love history, old streets and street food"],
    },
    zh: {
      htmlLang: "zh-Hans", title: "街知巷闻 · EveryLane Macau — 澳门深度游 AI 智能体",
      navPlan: "规划行程", navHow: "运作方式", navValue: "商业价值", engineTitle: "当前推理引擎", connecting: "· 连接中 ·", offline: "● 离线演示引擎", offlineTitle: "未设置 DASHSCOPE_API_KEY：使用离线引擎完整演示同样的智能体流程；设置密钥后自动改用真实 Qwen。", liveTitle: "正在使用阿里云百炼 Qwen 模型驱动",
      eyebrow: "澳门文旅 × 旧区活化 · 千问 Qwen / QwenPaw 智能体", heroTitle: "不止大三巴，<br><span class=\"hl\">阿濠带你走遍澳门每一条老街</span>",
      lede: "一个会“做任务”的 AI 智能体 —— 自动<b>查天气、搜景点、核对开放时间、预测人流</b>，还会把你从拥挤热点，<b>智能导流到旧区老街和本地小店</b>，输出一份可验证的深度游行程。",
      ctaPlan: "开始规划我的澳门深度游 →", ctaHow: "看看 AI 如何思考", statPoi: "个真实澳门景点", statOld: "条旧区老街", statLocal: "间本地老字号", statTools: "项可调用工具",
      plannerTitle: "跟阿濠说一句，就能规划整趟行程", plannerSub: "用自然语言写下需求即可，例如日期、人数、兴趣、预算、是否少走路。", placeholder: "例如：我下星期三想带爸妈来澳门玩一天，喜欢历史文化和地道美食，预算不想太贵，又不想走太多路…", hint: "⌘/Ctrl + Enter 快速出发", planBtn: "出发 · 规划行程", planning: "阿濠正在规划…",
      traceTitle: "阿濠 · 智能体工作过程", traceToggle: "收合/展开", empty: "阿濠正在规划，行程马上在这里生成…", howTitle: "如何运作：一个真正会“做任务”的智能体", howSub: "对标 QwenPaw 的 ReAct 架构 —— 规划、调用工具、多步执行、失败自动恢复。",
      how1h: "理解与规划", how1p: "解析自然语言需求，拆解成日期、人数、兴趣、预算、步行偏好，并制定行动计划。", how2h: "调用工具", how2p: "天气、景点检索、开放时间核实、人流预测、导流、路线计算、预算估算 —— 7 大工具。", how3h: "多步执行", how3p: "逐一核实每个景点，动态整合天气、人流、地理片区，组装出可步行的顺路行程。", how4h: "失败恢复", how4p: "遇到景点当天休息、预算超支、走得太远，会自动改线、替换、缩减，不会卡住。",
      valueTitle: "商业价值：一个导流引擎，三方共赢", tourist: "游客", touristP: "避开人潮、省钱省脚力，体验真正地道、有故事的澳门，提升满意度与停留时间。", shop: "旧区小店", shopP: "把集中在大三巴／威尼斯人的客流，导入十月初五街、福隆新街等老街与街坊老字号，<b>带来真实新客流</b>。可按引流量收费或推出“精选商户”订阅。", city: "城市 / 政府", cityP: "平衡旅游承载、缓解过度集中、活化旧区与保育文化遗产，契合澳门“世界旅游休闲中心”定位。", valueFoot: "变现路径：商户精选订阅／引流分成 · 酒店与旅行社 API 授权 · 文旅局数据仪表板 · 多语言客群扩展。",
      footerSub: "“千模百炼”AI 开发者系列之学生竞赛 · 参赛方向：澳门文旅 × 旧区活化", participant: "参赛者：SITINIEK（学号 dc227126）", tech: "技术：Qwen / QwenPaw · FastAPI · ReAct Agent", ethics: "AI 伦理：行程由 AI 生成，人流为估算值，请以现场为准；数据来源公开资料。",
      language: "语言", people: "人", interests: "兴趣", budget: "预算 MOP", lowWalk: "少走路", daysTrip: "日行程", actionPlan: "行动计划", recovery: "自动改线", noPrompt: "请先写下你想怎么玩", stops: "个站点", walkDistance: "步行距离", budgetPer: "预算/人均", oldLanes: "旧区老街", localShops: "本地小店", diversionTitle: "智能导流 · 从人潮热点带你去旧区老街", constraintsTitle: "任务完成核对 · 每项条件都已验证", daysOverview: "多日分区总览 · 每日一个可步行主题", fullMap: "全程地图 · 多日分区路线", routeMap: "路线地图 · 顺路而行", timeline: "行程时间轴", notes: "贴士", print: "打印 / 保存为 PDF", replan: "再规划一次", dayStops: "站", dayWalk: "步行", dayBudget: "预算", dayOld: "旧区", dayLocal: "小店", walk: "步行", minutes: "分钟", crowd: "人流：", wait: "约等", minShort: "分", free: "免费", approx: "约 MOP ", ahouSays: "阿濠说：", story: "听阿濠讲故事",
      tool: { get_weather: "查天气", search_attractions: "搜索景点", check_opening: "核实开放时间", predict_crowd: "预测人流", find_local_gem: "找本地老街", compute_route: "规划步行路线", estimate_budget: "估算预算", submit_itinerary: "提交行程" },
      samples: ["我下星期三想带爸妈来澳门玩一天，喜欢历史文化和地道美食，预算不想太贵，又不想走太多路", "帮我安排澳门三天两夜，想玩半岛世遗、氹仔美食和路环慢生活", "情侣星期六想逛旧区老街、拍照，顺便吃街头小吃", "我想去郑家大屋和附近的历史老街，星期三去", "氹仔半日游，主打地道美食", "First time in Macau this weekend, we love history, old streets and street food"],
    },
    en: {
      htmlLang: "en", title: "EveryLane Macau — AI Deep-Travel Agent",
      navPlan: "Plan Trip", navHow: "How It Works", navValue: "Business Value", engineTitle: "Current reasoning engine", connecting: "· Connecting ·", offline: "● Offline Demo Engine", offlineTitle: "No DASHSCOPE_API_KEY set: the offline engine demonstrates the same agent flow; add a key to use real Qwen.", liveTitle: "Powered by Alibaba Cloud Bailian Qwen",
      eyebrow: "Macau Tourism × Old-District Revival · Qwen / QwenPaw Agent", heroTitle: "Beyond St. Paul’s,<br><span class=\"hl\">Ah-Hou walks you through every old lane in Macau</span>",
      lede: "An AI agent that actually gets tasks done: it <b>checks weather, searches POIs, verifies opening hours and predicts crowds</b>, then <b>diverts visitors into old streets and local shops</b> to produce a verifiable deep-travel itinerary.",
      ctaPlan: "Start My Macau Deep Trip →", ctaHow: "See How the AI Thinks", statPoi: "real Macau POIs", statOld: "old-district places", statLocal: "local shops", statTools: "callable tools",
      plannerTitle: "Tell Ah-Hou once, and he plans the whole trip", plannerSub: "Describe your date, group size, interests, budget and walking preference in natural language.", placeholder: "Example: Next Wednesday I’m bringing my parents to Macau for one day. We like history and local food, want a modest budget and less walking…", hint: "⌘/Ctrl + Enter to start", planBtn: "Go · Plan Trip", planning: "Ah-Hou is planning…",
      traceTitle: "Ah-Hou · Agent Work Trace", traceToggle: "Collapse/expand", empty: "Ah-Hou is planning. Your itinerary will appear here soon…", howTitle: "How It Works: an Agent That Really Does Tasks", howSub: "Aligned with QwenPaw’s ReAct architecture: planning, tool calling, multi-step execution and failure recovery.",
      how1h: "Understand & Plan", how1p: "Parse natural language into date, people, interests, budget and walking preference, then form an action plan.", how2h: "Call Tools", how2p: "Weather, POI search, opening checks, crowd prediction, diversion, routing and budgeting — 7 tools.", how3h: "Execute Steps", how3p: "Verify every stop and combine weather, crowd and geography into a walkable route.", how4h: "Recover Failures", how4p: "If a place is closed, over budget or too far away, the agent reroutes, replaces or trims automatically.",
      valueTitle: "Business Value: One Diversion Engine, Three Winners", tourist: "Visitors", touristP: "Avoid crowds, save money and walking effort, and experience a more authentic Macau with stories.", shop: "Old-District Shops", shopP: "Redirect traffic from St. Paul’s and Cotai resorts into old lanes and family-run shops, <b>bringing real new visitors</b>. Monetisation can use lead fees or featured merchant subscriptions.", city: "City / Government", cityP: "Balance visitor flows, reduce overcrowding, revitalise old districts and preserve cultural heritage.", valueFoot: "Monetisation: featured merchant subscriptions / referral revenue · hotel and travel agency APIs · tourism dashboards · multilingual expansion.",
      footerSub: "Qianmo Bailian AI Developer Series Student Competition · Macau Tourism × Old-District Revival", participant: "Participant: SITINIEK (Student ID dc227126)", tech: "Tech: Qwen / QwenPaw · FastAPI · ReAct Agent", ethics: "AI Ethics: itineraries are AI-generated; crowd levels are estimates; please follow on-site conditions. Data comes from public sources.",
      language: "Language", people: "people", interests: "Interests", budget: "Budget MOP", lowWalk: "Less walking", daysTrip: "days", actionPlan: "Action Plan", recovery: "Auto Reroute", noPrompt: "Please describe how you want to travel", stops: "stops", walkDistance: "walking distance", budgetPer: "budget/person", oldLanes: "old lanes", localShops: "local shops", diversionTitle: "Smart Diversion · From Crowded Hotspots to Old Lanes", constraintsTitle: "Task Checks · Every Condition Verified", daysOverview: "Multi-Day Overview · One Walkable Theme per Day", fullMap: "Full Map · Multi-Day District Routes", routeMap: "Route Map · Walkable Order", timeline: "Itinerary Timeline", notes: "Tips", print: "Print / Save Result as PDF", replan: "Plan Again", dayStops: "stops", dayWalk: "walk", dayBudget: "budget", dayOld: "old areas", dayLocal: "shops", walk: "Walk", minutes: "min", crowd: "Crowd: ", wait: "wait about ", minShort: "min", free: "Free", approx: "Approx. MOP ", ahouSays: "Ah-Hou says: ", story: "Hear Ah-Hou’s story",
      tool: { get_weather: "Weather", search_attractions: "Search POIs", check_opening: "Check Opening", predict_crowd: "Predict Crowd", find_local_gem: "Find Local Gem", compute_route: "Plan Route", estimate_budget: "Estimate Budget", submit_itinerary: "Submit Itinerary" },
      samples: ["Next Wednesday I’m bringing my parents to Macau for one day. We like history and local food, want a modest budget and less walking.", "Plan a 3 days Macau trip with heritage, Taipa food and Coloane slow life", "A couple trip this Saturday: old lanes, photo spots and street food", "I want to visit Mandarin’s House and nearby historic lanes on Wednesday", "Taipa half-day food walk", "First time in Macau this weekend, we love history, old streets and street food"],
    },
    pt: {
      htmlLang: "pt", title: "EveryLane Macau — Agente IA de Turismo Profundo",
      navPlan: "Planear Roteiro", navHow: "Como Funciona", navValue: "Valor Comercial", engineTitle: "Motor de raciocínio atual", connecting: "· A ligar ·", offline: "● Motor de Demonstração Offline", offlineTitle: "Sem DASHSCOPE_API_KEY: o motor offline demonstra o mesmo fluxo do agente; com chave passa a usar Qwen real.", liveTitle: "Alimentado por Qwen no Alibaba Cloud Bailian",
      eyebrow: "Turismo de Macau × Revitalização dos bairros antigos · Agente Qwen / QwenPaw", heroTitle: "Para além das Ruínas de São Paulo,<br><span class=\"hl\">Ah-Hou leva-te por cada rua antiga de Macau</span>", lede: "Um agente de IA que executa tarefas: <b>consulta o tempo, pesquisa pontos, verifica horários e prevê multidões</b>, depois <b>encaminha visitantes para ruas antigas e lojas locais</b> para criar um roteiro verificável.",
      ctaPlan: "Começar o meu roteiro em Macau →", ctaHow: "Ver como a IA pensa", statPoi: "pontos reais de Macau", statOld: "locais de bairros antigos", statLocal: "lojas locais", statTools: "ferramentas disponíveis",
      plannerTitle: "Diz uma frase ao Ah-Hou e ele planeia tudo", plannerSub: "Descreve data, número de pessoas, interesses, orçamento e preferência de caminhada em linguagem natural.", placeholder: "Exemplo: Na próxima quarta quero levar os meus pais a Macau por um dia; gostamos de história e comida local, com orçamento moderado e pouca caminhada…", hint: "⌘/Ctrl + Enter para começar", planBtn: "Ir · Planear Roteiro", planning: "Ah-Hou está a planear…",
      traceTitle: "Ah-Hou · Processo do Agente", traceToggle: "Recolher/expandir", empty: "Ah-Hou está a planear. O roteiro aparecerá aqui em breve…", howTitle: "Como Funciona: um Agente que Executa Tarefas", howSub: "Alinhado com a arquitetura ReAct do QwenPaw: planeamento, ferramentas, execução multi-etapas e recuperação de falhas.",
      how1h: "Compreender & Planear", how1p: "Analisa a necessidade em data, pessoas, interesses, orçamento e caminhada, criando um plano de ação.", how2h: "Chamar Ferramentas", how2p: "Tempo, pesquisa de pontos, horários, multidões, alternativas locais, rotas e orçamento — 7 ferramentas.", how3h: "Executar Etapas", how3p: "Verifica cada paragem e combina tempo, multidões e geografia numa rota caminhável.", how4h: "Recuperar Falhas", how4p: "Se um local estiver fechado, caro ou longe, o agente altera, substitui ou reduz automaticamente.",
      valueTitle: "Valor Comercial: Um Motor de Distribuição, Três Beneficiários", tourist: "Visitantes", touristP: "Evita multidões, poupa dinheiro e esforço, e descobre uma Macau mais autêntica.", shop: "Lojas de Bairros Antigos", shopP: "Redireciona fluxo das Ruínas e de Cotai para ruas antigas e lojas familiares, <b>trazendo novos visitantes reais</b>.", city: "Cidade / Governo", cityP: "Equilibra fluxos turísticos, reduz sobrelotação, revitaliza bairros antigos e preserva património.", valueFoot: "Monetização: comerciantes destacados / referência · APIs para hotéis e agências · painéis turísticos · expansão multilingue.",
      footerSub: "Concurso Estudantil Qianmo Bailian AI Developer Series · Turismo de Macau × Revitalização", participant: "Participante: SITINIEK (ID dc227126)", tech: "Tecnologia: Qwen / QwenPaw · FastAPI · Agente ReAct", ethics: "Ética de IA: roteiros gerados por IA; multidões são estimativas; confirmar no local. Dados de fontes públicas.",
      language: "Idioma", people: "pessoas", interests: "Interesses", budget: "Orçamento MOP", lowWalk: "Menos caminhada", daysTrip: "dias", actionPlan: "Plano de Ação", recovery: "Reencaminhamento", noPrompt: "Descreve como queres viajar", stops: "paragens", walkDistance: "distância a pé", budgetPer: "orçamento/pessoa", oldLanes: "ruas antigas", localShops: "lojas locais", diversionTitle: "Distribuição Inteligente · Dos Hotspots para Ruas Antigas", constraintsTitle: "Verificação da Tarefa · Condições Confirmadas", daysOverview: "Visão Multi-Dia · Um Tema Caminhável por Dia", fullMap: "Mapa Completo · Rotas por Distrito", routeMap: "Mapa da Rota · Ordem Caminhável", timeline: "Linha do Tempo", notes: "Dicas", print: "Imprimir / Guardar Resultado em PDF", replan: "Planear Novamente", dayStops: "paragens", dayWalk: "a pé", dayBudget: "orçamento", dayOld: "bairros antigos", dayLocal: "lojas", walk: "A pé", minutes: "min", crowd: "Multidão: ", wait: "espera aprox. ", minShort: "min", free: "Grátis", approx: "Aprox. MOP ", ahouSays: "Ah-Hou diz: ", story: "Ouvir a história de Ah-Hou",
      tool: { get_weather: "Tempo", search_attractions: "Pesquisar Pontos", check_opening: "Verificar Horário", predict_crowd: "Prever Multidão", find_local_gem: "Alternativa Local", compute_route: "Planear Rota", estimate_budget: "Estimar Orçamento", submit_itinerary: "Submeter Roteiro" },
      samples: ["Na próxima quarta quero levar os meus pais a Macau por um dia, com história, comida local, orçamento moderado e pouca caminhada", "Planeia 3 dias em Macau com património, comida em Taipa e vida lenta em Coloane", "Viagem de casal no sábado: ruas antigas, fotos e comida de rua", "Quero visitar a Casa do Mandarim e ruas históricas próximas na quarta", "Meio dia em Taipa com foco em comida local", "First time in Macau this weekend, we love history, old streets and street food"],
    },
    ja: {
      htmlLang: "ja", title: "EveryLane Macau — マカオ深度旅行AIエージェント",
      navPlan: "旅程を作る", navHow: "仕組み", navValue: "商業価値", engineTitle: "現在の推論エンジン", connecting: "· 接続中 ·", offline: "● オフラインデモエンジン", offlineTitle: "DASHSCOPE_API_KEY 未設定：同じエージェント流れをオフラインで実演します。キー設定後は本物の Qwen を使用します。", liveTitle: "Alibaba Cloud Bailian の Qwen で動作中",
      eyebrow: "マカオ観光 × 旧市街活性化 · Qwen / QwenPaw エージェント", heroTitle: "聖ポール天主堂跡だけじゃない、<br><span class=\"hl\">阿濠がマカオの古い路地まで案内</span>", lede: "ただ答えるだけでなく、実際にタスクをこなすAIエージェント。<b>天気、スポット、営業時間、人流</b>を確認し、混雑スポットから<b>旧市街の路地と地元店</b>へスマートに誘導します。",
      ctaPlan: "マカオ深度旅行を作る →", ctaHow: "AIの考え方を見る", statPoi: "実在するマカオPOI", statOld: "旧市街スポット", statLocal: "地元店", statTools: "利用可能ツール",
      plannerTitle: "阿濠に一言伝えるだけで旅程を作成", plannerSub: "日付、人数、興味、予算、歩く量を自然な言葉で入力してください。", placeholder: "例：来週水曜に両親とマカオを1日観光。歴史とローカルグルメが好きで、予算は控えめ、歩きすぎたくない…", hint: "⌘/Ctrl + Enter で開始", planBtn: "出発 · 旅程を作成", planning: "阿濠が計画中…",
      traceTitle: "阿濠 · エージェント作業ログ", traceToggle: "折りたたみ/展開", empty: "阿濠が計画中です。旅程はここに表示されます…", howTitle: "仕組み：本当にタスクを実行するエージェント", howSub: "QwenPaw の ReAct 構成に対応：計画、ツール呼び出し、多段実行、失敗回復。",
      how1h: "理解と計画", how1p: "自然言語を日付、人数、興味、予算、歩行希望に分解し、行動計画を立てます。", how2h: "ツール呼び出し", how2p: "天気、スポット検索、営業時間、人流予測、誘導、ルート、予算の7ツール。", how3h: "多段実行", how3p: "各スポットを検証し、天気・人流・地理を組み合わせて歩けるルートにします。", how4h: "失敗回復", how4p: "休業、予算超過、遠すぎる場合は自動で変更・代替・短縮します。",
      valueTitle: "商業価値：誘導エンジンで三方よし", tourist: "旅行者", touristP: "混雑を避け、費用と歩行負担を減らし、物語のある本当のマカオを体験できます。", shop: "旧市街の店", shopP: "聖ポールやコタイに集中する人流を古い路地と家族経営の店へ送り、<b>実際の新規客流</b>を生みます。", city: "都市 / 政府", cityP: "観光流量を分散し、過密を緩和し、旧市街活性化と文化保全に貢献します。", valueFoot: "収益化：おすすめ店舗掲載／送客報酬 · ホテル/旅行会社API · 観光ダッシュボード · 多言語展開。",
      footerSub: "「千模百煉」AI開発者シリーズ学生コンペ · マカオ観光 × 旧市街活性化", participant: "参加者：SITINIEK（学籍番号 dc227126）", tech: "技術：Qwen / QwenPaw · FastAPI · ReAct Agent", ethics: "AI倫理：旅程はAI生成、人流は推定値です。現地状況を優先してください。データは公開資料に基づきます。",
      language: "言語", people: "人", interests: "興味", budget: "予算 MOP", lowWalk: "歩行少なめ", daysTrip: "日旅程", actionPlan: "行動計画", recovery: "自動変更", noPrompt: "旅行の希望を入力してください", stops: "スポット", walkDistance: "歩行距離", budgetPer: "予算/人", oldLanes: "旧市街", localShops: "地元店", diversionTitle: "スマート誘導 · 混雑地から旧市街へ", constraintsTitle: "タスク確認 · 条件を検証済み", daysOverview: "複数日概要 · 1日1つの歩けるテーマ", fullMap: "全体地図 · 複数日エリア別ルート", routeMap: "ルート地図 · 歩きやすい順番", timeline: "旅程タイムライン", notes: "ヒント", print: "印刷 / 結果をPDF保存", replan: "もう一度計画", dayStops: "スポット", dayWalk: "歩行", dayBudget: "予算", dayOld: "旧市街", dayLocal: "地元店", walk: "徒歩", minutes: "分", crowd: "人流：", wait: "待ち約", minShort: "分", free: "無料", approx: "約 MOP ", ahouSays: "阿濠より：", story: "阿濠の話を聞く",
      tool: { get_weather: "天気確認", search_attractions: "スポット検索", check_opening: "営業時間確認", predict_crowd: "人流予測", find_local_gem: "地元スポット", compute_route: "徒歩ルート", estimate_budget: "予算見積", submit_itinerary: "旅程提出" },
      samples: ["来週水曜に両親とマカオを1日観光。歴史文化とローカルグルメが好きで、予算控えめ、歩きすぎたくない", "マカオ3日2泊：半島の世界遺産、タイパのグルメ、コロアンのスローライフ", "土曜のカップル旅：旧市街、写真スポット、ストリートフード", "水曜に鄭家大屋と近くの歴史路地へ行きたい", "タイパ半日グルメ散歩", "First time in Macau this weekend, we love history, old streets and street food"],
    },
  };

  let map = null, today = new Date().toISOString().slice(0, 10), es = null, running = false, healthState = null, lastItinerary = null, staticMode = false;
  const langNow = () => $("#lang")?.value || "zh-HK";
  const tt = (key) => (I18N[langNow()] || I18N["zh-HK"])[key] || I18N["zh-HK"][key] || key;
  const toolLabel = (name) => ((I18N[langNow()] || I18N["zh-HK"]).tool || {})[name] || name;

  // ---------------- boot ----------------
  async function boot() {
    applyStaticI18n();
    $("#lang").addEventListener("change", () => {
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
    return location.hostname.endsWith("github.io") || location.port === "8090";
  }

  function enableStaticMode() {
    staticMode = true;
    healthState = { ok: true, engine: "github-pages-static", real_llm: false, poi_count: 70, old_district: 25, local_business: 20 };
    $("#hsPoi").textContent = healthState.poi_count;
    $("#hsOld").textContent = healthState.old_district;
    $("#hsLocal").textContent = healthState.local_business;
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
    set(".eyebrow", "eyebrow"); set(".hero h1", "heroTitle"); set(".lede", "lede");
    set(".hero-cta .btn-primary", "ctaPlan"); set(".hero-cta .btn-ghost", "ctaHow");
    const statLabels = ["statPoi", "statOld", "statLocal", "statTools"];
    document.querySelectorAll(".hero-stats span").forEach((n, i) => n.textContent = tt(statLabels[i]));
    set("#planner .section-head h2", "plannerTitle"); set("#planner .section-head p", "plannerSub");
    $("#prompt").placeholder = tt("placeholder"); set(".hint", "hint"); $("#planBtn").textContent = running ? tt("planning") : tt("planBtn");
    set(".trace-head h3", "traceTitle"); $("#traceToggle").title = tt("traceToggle"); set("#resultEmpty p", "empty");
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
      c.addEventListener("click", () => { $("#prompt").value = s; startPlan(); });
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
    if (healthState.real_llm) {
      b.textContent = "● Qwen " + healthState.engine.replace("qwen:", "");
      b.classList.add("live"); b.classList.remove("offline"); b.title = tt("liveTitle");
    } else {
      b.textContent = tt("offline");
      b.classList.add("offline"); b.classList.remove("live"); b.title = tt("offlineTitle");
    }
  }

  // ---------------- planning ----------------
  function startPlan() {
    if (running) { es && es.close(); }
    const q = $("#prompt").value.trim();
    if (!q) { toast(tt("noPrompt")); $("#prompt").focus(); return; }
    const lang = $("#lang").value;
    running = true;
    $("#workspace").classList.remove("hidden");
    $("#result").classList.add("hidden");
    $("#result").innerHTML = "";
    $("#resultEmpty").classList.remove("hidden");
    $("#trace").innerHTML = "";
    $("#traceParams").textContent = "";
    $("#tracePulse").classList.add("run");
    $("#planBtn").disabled = true;
    $("#planBtn").textContent = tt("planning");
    $("#workspace").scrollIntoView({ behavior: "smooth", block: "start" });

    if (staticMode) {
      runStaticPlan(q, lang);
      return;
    }

    const url = `/api/plan?q=${encodeURIComponent(q)}&lang=${encodeURIComponent(lang)}&today=${today}`;
    es = new EventSource(url);
    es.onmessage = (m) => { try { handle(JSON.parse(m.data)); } catch (e) { console.error(e, m.data); } };
    es.onerror = () => { if (running) finish(); };
  }

  function finish() {
    running = false;
    es && es.close();
    $("#tracePulse").classList.remove("run");
    $("#planBtn").disabled = false;
    $("#planBtn").textContent = tt("planBtn");
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
      case "result": renderResult(e.itinerary); break;
      case "done": finish(); break;
      case "error": addTrace("recovery", "⚠️", esc(e.text), true); finish(); break;
    }
  }

  function runStaticPlan(q, lang) {
    const L = staticCopy(lang);
    const multi = /2|3|兩|两|三|day|days|dias|泊|日|天/i.test(q);
    handle({ type: "params", params: { language: lang, language_name: I18N[lang]?.htmlLang || lang, date: today, people: 2, interests: L.interests, days: multi ? 3 : 1 } });
    handle({ type: "status", text: L.status });
    handle({ type: "plan", steps: L.steps });
    [
      ["get_weather", { date: today }, L.weather],
      ["search_attractions", { prefer_local: true, limit: 12 }, L.search],
      ["check_opening", { poi_id: "ruins_st_paul", date: today }, L.open],
      ["predict_crowd", { poi_id: "ruins_st_paul", datetime: today + " 13:00" }, L.crowd],
      ["find_local_gem", { near_poi_id: "ruins_st_paul" }, L.gem],
      ["compute_route", { optimize: true }, L.route],
      ["estimate_budget", { people: 2 }, L.budget],
    ].forEach(([name, args, summary], i) => {
      setTimeout(() => { handle({ type: "tool_call", name, args }); handle({ type: "tool_result", name, summary }); }, 250 + i * 180);
    });
    setTimeout(() => {
      handle({ type: "recovery", reason: L.recovery });
      handle({ type: "diversion", reason: L.diversion });
      handle({ type: "result", itinerary: staticItinerary(lang, multi) });
      handle({ type: "done" });
    }, 1750);
  }

  function staticCopy(lang) {
    const pack = {
      "zh-HK": {
        status: "GitHub Pages 靜態演示模式：正在用內置澳門知識庫展示完整智能體流程。",
        steps: ["理解日期、人數、興趣與多日需求", "每日鎖定可步行片區", "查天氣、核實開放、人流導流", "計算路線與預算，輸出可驗證行程"],
        interests: ["歷史", "老街", "美食"], weather: "晴朗舒適・適合步行", search: "找到半島、氹仔、路環候選景點", open: "大三巴牌坊：開放", crowd: "大三巴正午人流：極擁擠", gem: "建議導流至草堆街與爛鬼樓", route: "已排好多日分區路線", budget: "預算合計 MOP 310", recovery: "靜態 Pages 無後端 API，已切換到可演示版本。", diversion: "由大三巴人潮導流到草堆街與本地小店。",
      },
      zh: {
        status: "GitHub Pages 静态演示模式：正在用内置澳门知识库展示完整智能体流程。",
        steps: ["理解日期、人数、兴趣与多日需求", "每日锁定可步行片区", "查天气、核实开放、人流导流", "计算路线与预算，输出可验证行程"],
        interests: ["历史", "老街", "美食"], weather: "晴朗舒适・适合步行", search: "找到半岛、氹仔、路环候选景点", open: "大三巴牌坊：开放", crowd: "大三巴正午人流：极拥挤", gem: "建议导流至草堆街与爛鬼楼", route: "已排好多日分区路线", budget: "预算合计 MOP 310", recovery: "静态 Pages 没有后端 API，已切换到可演示版本。", diversion: "从大三巴人潮导流到草堆街与本地小店。",
      },
      en: {
        status: "GitHub Pages static demo mode: showing the full agent flow with an embedded Macau knowledge base.",
        steps: ["Understand date, people, interests and multi-day needs", "Keep one walkable district per day", "Check weather, opening hours and crowd diversion", "Compute route and budget, then output a verifiable itinerary"],
        interests: ["history", "old streets", "food"], weather: "Comfortable sunshine・good for walking", search: "Found candidates across the peninsula, Taipa and Coloane", open: "Ruins of St. Paul's: open", crowd: "Ruins at noon: packed", gem: "Suggest diverting to Rua das Estalagens", route: "Multi-day district routes computed", budget: "Estimated total MOP 310", recovery: "Static Pages has no backend API, so demo mode is active.", diversion: "Divert visitors from St. Paul's crowds into Rua das Estalagens and local shops.",
      },
      pt: {
        status: "Modo de demonstração estática do GitHub Pages: fluxo completo com base de conhecimento embutida.",
        steps: ["Compreender data, pessoas, interesses e vários dias", "Usar um distrito caminhável por dia", "Verificar tempo, horários e distribuição de multidões", "Calcular rota e orçamento, gerando roteiro verificável"],
        interests: ["história", "ruas antigas", "comida"], weather: "Sol agradável・bom para caminhar", search: "Encontrados pontos na península, Taipa e Coloane", open: "Ruínas de São Paulo: aberto", crowd: "Ruínas ao meio-dia: muito cheio", gem: "Sugerir Rua das Estalagens", route: "Rotas multi-dia calculadas", budget: "Total estimado MOP 310", recovery: "Pages estático não tem API backend; modo demo ativo.", diversion: "Distribuir visitantes das Ruínas para ruas antigas e lojas locais.",
      },
      ja: {
        status: "GitHub Pages 静的デモ：内蔵マカオ知識ベースでエージェント流れを表示します。",
        steps: ["日付・人数・興味・複数日条件を理解", "1日1つの歩ける地区に限定", "天気・営業時間・人流誘導を確認", "ルートと予算を計算し検証可能な旅程を出力"],
        interests: ["歴史", "旧市街", "グルメ"], weather: "快適な晴れ・徒歩向き", search: "半島、タイパ、コロアンの候補を発見", open: "聖ポール天主堂跡：開放", crowd: "正午の聖ポール：非常に混雑", gem: "草堆街への誘導を提案", route: "複数日ルートを計算済み", budget: "合計見積 MOP 310", recovery: "静的 Pages にはバックエンドAPIがないためデモモードです。", diversion: "聖ポールの混雑から旧市街と地元店へ誘導。",
      },
    };
    return pack[lang] || pack["zh-HK"];
  }

  function staticItinerary(lang, multi) {
    const z = lang.startsWith("zh");
    const stops1 = [
      poi("ruins_st_paul", 1, "大三巴牌坊", "Ruins of St. Paul's", "Ruínas de São Paulo", "heritage", 22.19755, 113.54086, "assets/poi/ruins_st_paul.jpg", true, false, false, "10:00", "10:45", 0, "packed", z ? "世界遺產地標，最適合早上避開人潮。" : "A UNESCO icon, best visited early to avoid crowds."),
      poi("rua_estalagens", 2, "草堆街與爛鬼樓", "Rua das Estalagens", "Rua das Estalagens", "street", 22.19488, 113.53868, "assets/poi/rua_estalagens.jpg", false, true, true, "10:51", "11:16", 0, "quiet", z ? "舊區老街，人少地道，能帶旺本地小店。" : "A quiet old lane that diverts visitors into local shops."),
      poi("rua_felicidade", 3, "福隆新街", "Rua da Felicidade", "Rua da Felicidade", "street", 22.19283, 113.53894, "assets/poi/rua_felicidade.jpg", false, true, true, "11:25", "11:55", 0, "moderate", z ? "紅窗門老街，最有舊澳門味。" : "A red-shutter old street full of old Macau character."),
      poi("wong_chi_kei", 4, "黃枝記粥麵", "Wong Chi Kei Noodles", "Wong Chi Kei", "food", 22.19360, 113.53980, "assets/poi/wong_chi_kei.jpg", false, true, true, "12:05", "12:50", 140, "busy", z ? "本地老字號，午餐兼支持街坊小店。" : "A local noodle institution for lunch and neighbourhood spending."),
    ];
    const stops2 = [
      poi("rua_cunha", 1, "官也街", "Rua do Cunha", "Rua do Cunha", "street", 22.15408, 113.55695, "assets/poi/rua_cunha.jpg", false, true, true, "10:00", "10:40", 0, "busy", z ? "氹仔美食手信街，適合作為離島線起點。" : "Taipa's lively food street and a strong island-route anchor."),
      poi("taipa_houses", 2, "龍環葡韻", "Taipa Houses", "Casas-Museu da Taipa", "museum", 22.15389, 113.55944, "assets/poi/taipa_houses.jpg", false, false, false, "10:48", "11:28", 0, "moderate", z ? "葡式建築與濕地景觀，拍照效果好。" : "Portuguese houses and wetland views, great for photos."),
      poi("tai_lei_loi", 3, "大利來記豬扒包", "Tai Lei Loi Kei", "Tai Lei Loi Kei", "food", 22.15600, 113.55720, "assets/poi/tai_lei_loi.jpg", false, true, true, "11:38", "12:08", 90, "moderate", z ? "氹仔老字號豬扒包，商業價值清晰。" : "A Taipa pork-chop-bun classic with clear local business value."),
    ];
    const days = multi ? [makeDay(1, "Day 1 · Macau Peninsula", stops1), makeDay(2, "Day 2 · Taipa Village", stops2)] : [makeDay(1, "Day 1", stops1)];
    const all = days.flatMap(d => d.stops.map(s => ({ ...s, day_no: d.day_no, map_order: `${d.day_no}-${s.order}` })));
    return {
      title: z ? "你的澳門深度漫遊（GitHub Pages 演示）" : "Your Macau Deep Trip (GitHub Pages Demo)",
      summary: z ? "這是 GitHub Pages 靜態演示版：保留完整多語介面、地圖、時間軸、PDF 匯出與智能體流程展示；本地運行時可接入 FastAPI + Qwen 真正工具調用。" : "This GitHub Pages static demo keeps the multilingual UI, map, timeline, PDF export and agent trace. Run locally to enable FastAPI + Qwen tool calls.",
      language: lang, language_name: I18N[lang]?.htmlLang || lang, date: multi ? `${today} → demo` : today, weekday: multi ? "Demo" : "Demo",
      weather: { condition: z ? "晴朗舒適" : "Comfortable", temp_c: 28 },
      days: multi ? days : undefined,
      totals: summarize(all),
      constraints: [
        { label: z ? "路線分區合理" : "Coherent district routing", ok: true, detail: z ? "每日集中一個可步行片區，避免跨島亂跑" : "Each day focuses on one walkable district instead of crossing islands randomly" },
        { label: z ? "避開人潮熱點" : "Crowd-aware timing", ok: true, detail: z ? "熱門點安排較早到達，並加入附近舊區導流" : "Popular stops are timed earlier, with nearby old-lane diversions added" },
        { label: z ? "帶旺舊區・本地小店" : "Supports old districts and local shops", ok: true, detail: z ? "行程包含舊區老街與本地老字號，不只停留在熱門景點" : "The trip includes old lanes and local shops, not only famous hotspots" },
      ],
      diversions: [{ from: z ? "大三巴牌坊" : "Ruins of St. Paul's", to: z ? "草堆街與爛鬼樓" : "Rua das Estalagens", reason: staticCopy(lang).diversion }],
      notes: [z ? "GitHub Pages 版為靜態演示；完整 ReAct 工具調用請本地運行。" : "GitHub Pages is a static demo; run locally for full ReAct tool calling."],
      stops: all,
    };
  }

  function poi(id, order, zh, en, pt, category, lat, lng, image, unesco, old, local, arrive, depart, cost, crowd, why) {
    return { order, poi_id: id, name: { zh, en, pt }, category, district_name: "", zone: "", lat, lng, image, arrive, depart, visit_min: 30, why, blurb: { zh: why, en: why }, tags: [], unesco, old_district: old, local_business: local, cost_mop: cost, crowd: { level: 0.5, label: crowd, label_en: crowd, wait: crowd === "busy" ? 12 : 0 }, walk_to_next: null };
  }

  function makeDay(day_no, title, stops) {
    for (let i = 0; i < stops.length - 1; i++) stops[i].walk_to_next = { min: 8, km: 0.45, to: stops[i + 1].name.zh };
    return { day_no, day_title: title, date: today, summary: title, totals: summarize(stops), stops };
  }

  function summarize(stops) {
    return { stops: stops.length, cost_mop: stops.reduce((a, s) => a + (s.cost_mop || 0), 0), walk_min: Math.max(0, stops.length - 1) * 8, walk_km: +(Math.max(0, stops.length - 1) * 0.45).toFixed(2), old_district: stops.filter(s => s.old_district).length, local_business: stops.filter(s => s.local_business).length };
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
    const banner = el("div", "r-banner");
    banner.innerHTML =
      `<div class="r-title">${esc(it.title)}</div>` +
      `<p class="r-summary">${esc(it.summary)}</p>` +
      `<div class="r-meta">` +
      metachip("📅", `${it.date} ${it.weekday}`) +
      metachip(weatherIcon(w), `${esc(w.condition || "")} ${w.temp_c != null ? w.temp_c + "°C" : ""}`) +
      metachip("🗣️", it.language_name) +
      `</div>`;
    r.appendChild(banner);

    // stats
    const t = it.totals || {};
    const stats = el("div", "stats");
    stats.innerHTML =
      stat(t.stops, tt("stops")) +
      stat(t.walk_km + " km", tt("walkDistance")) +
      stat("MOP " + t.cost_mop, tt("budgetPer"), true) +
      stat(t.old_district, tt("oldLanes")) +
      stat(t.local_business, tt("localShops"));
    r.appendChild(stats);

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
      c.innerHTML = `<h3><span class="p-ic">✅</span>${esc(tt("constraintsTitle"))}</h3>`;
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
    mapPanel.innerHTML = `<h3><span class="p-ic">🗺️</span>${esc(isMulti ? tt("fullMap") : tt("routeMap"))}</h3><div id="map"></div>`;
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
            tl.appendChild(el("div", "tl-walk", `🚶 ${esc(tt("walk"))} ${s.walk_to_next.min} ${esc(tt("minutes"))} · ${s.walk_to_next.km} km → ${esc(s.walk_to_next.to)}`));
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
          tl.appendChild(el("div", "tl-walk", `🚶 ${esc(tt("walk"))} ${s.walk_to_next.min} ${esc(tt("minutes"))} · ${s.walk_to_next.km} km → ${esc(s.walk_to_next.to)}`));
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
      ? `<div class="tl-img"><img src="${esc(assetPath(s.image))}" alt="${esc(s.name.zh)}" loading="lazy" onerror="this.parentElement.classList.add('ph','${cat}');this.parentElement.innerHTML='<span class=&quot;ph-name&quot;>${esc(s.name.zh)}</span>'"></div>`
      : `<div class="tl-img ph ${cat}"><span class="ph-name">${esc(s.name.zh)}</span></div>`;
    const badges = [];
    if (s.unesco) badges.push(`<span class="tg unesco">UNESCO</span>`);
    if (s.old_district) badges.push(`<span class="tg old">${esc(tt("oldLanes"))}</span>`);
    if (s.local_business) badges.push(`<span class="tg local">${esc(tt("localShops"))}</span>`);
    const cl = CROWD_CLASS[s.crowd.label_en] || "crowd-moderate";
    badges.push(`<span class="tg ${cl}">${esc(tt("crowd"))}${esc(s.crowd.label)}${s.crowd.wait ? " · " + esc(tt("wait")) + s.crowd.wait + esc(tt("minShort")) : ""}</span>`);
    badges.push(`<span class="tg cost">${s.cost_mop ? esc(tt("approx")) + s.cost_mop : esc(tt("free"))}</span>`);

    const why = `<div class="tl-why"><span class="qz">${esc(tt("ahouSays"))}</span>${esc(s.why)}</div>`;
    const name = displayPoiName(s);
    const secondary = langNow().startsWith("zh") ? (s.name.en || "") : "";
    const blurbText = s.blurb ? (langNow().startsWith("zh") ? (s.blurb.zh || s.blurb.en || "") : (s.blurb.en || s.blurb.zh || "")) : "";
    const blurb = blurbText ? `<div class="tl-blurb">${esc(blurbText)}</div>` : "";
    const story = s.story_zh ? `<details class="story"><summary>${esc(tt("story"))}</summary><p>${esc(s.story_zh)}</p></details>` : "";
    const tip = s.tip ? `<div class="tl-tip">💡 ${esc(s.tip)}</div>` : "";
    const tags = (langNow().startsWith("zh") && s.tags && s.tags.length) ? `<div class="tl-tags">${s.tags.slice(0, 5).map(x => `<span class="mini">${esc(x)}</span>`).join("")}</div>` : "";

    card.innerHTML =
      `<div class="tl-time"><span class="ord">${s.order}</span><span class="t">${s.arrive}<br>↓<br>${s.depart}</span></div>` +
      `<div class="tl-card${lb}"><div class="tl-media">${img}<div class="tl-info">` +
      `<div class="tl-name">${esc(name)}${secondary ? `<span class="en">${esc(secondary)}</span>` : ""}</div>` +
      `<div class="tl-badges">${badges.join("")}</div>${why}${blurb}${story}${tip}${tags}` +
      `</div></div></div>`;
    return card;
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
      const cat = ["food", "street", "view"].includes(s.category) ? s.category : "";
      const icon = L.divIcon({ className: "", html: `<div class="map-pin ${cat}"><span>${esc(s.map_order || s.order)}</span></div>`, iconSize: [34, 34], iconAnchor: [17, 30] });
      L.marker([s.lat, s.lng], { icon }).addTo(map)
        .bindPopup(`<b>${esc(displayPoiName(s))}</b><br>${esc(s.arrive)}–${esc(s.depart)} · ${esc(tt("crowd"))}${esc(s.crowd.label)}`);
    });
    if (latlngs.length > 1) {
      L.polyline(latlngs, { color: "#BE4A3A", weight: 3, opacity: .75, dashArray: "1 8", lineCap: "round" }).addTo(map);
      map.fitBounds(L.latLngBounds(latlngs).pad(0.18));
    }
    setTimeout(() => map && map.invalidateSize(), 200);
  }

  // ---------------- misc ----------------
  let toastTimer = null;
  function toast(msg) {
    let t = $(".toast");
    if (!t) { t = el("div", "toast"); document.body.appendChild(t); }
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

  $("#planBtn").addEventListener("click", startPlan);
  $("#prompt").addEventListener("keydown", (e) => { if ((e.metaKey || e.ctrlKey) && e.key === "Enter") startPlan(); });
  $("#traceToggle").addEventListener("click", () => $("#trace").classList.toggle("hidden"));
  boot();
})();
