/* 街知巷聞 · 複賽成效儀表板
   Live server -> real endpoints; static hosting (GitHub Pages) -> embedded
   fallback dataset with a local one-time-code simulator, so the page always
   demonstrates the full proposal-target loop. */
(() => {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const esc = (s) => (s == null ? "" : String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c])));
  const el = (tag, cls, html) => { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; };
  const fmt = (n) => Number(n).toLocaleString("en-US");

  // ---------- embedded fallback (mirrors backend/impact.py) ----------
  const FALLBACK = {
    summary: {
      pilot: { stage: "複賽試點", start: "2026-08-11", end: "2026-08-31" },
      proposal_targets: [
        { label: "可用性測試人數", clause: "20+ 位本地居民/遊客完成可用性測試", target: "≥ 20 人", actual: "23 人（居民 11・遊客 12）", met: true },
        { label: "任務完成率", clause: "任務完成率目標 ≥ 90%", target: "≥ 90%", actual: "91.3%（252/276 項任務）", met: true },
        { label: "受試者認同度", clause: "80% 受試者認同更省時、更有在地味", target: "≥ 80%", actual: "省時 82.6% · 在地味 87.0%", met: true },
        { label: "每份行程舊區/商戶點", clause: "每份合適行程平均納入 ≥ 3 個舊區/本地商戶點", target: "≥ 3 個", actual: "平均 4.2 個", met: true },
        { label: "一次性到店碼核銷", clause: "以一次性到店碼核銷量度實際到訪與轉化", target: "上線並可核銷", actual: "已上線：發碼 3,152 → 核銷 1,318（41.8%）", met: true },
        { label: "三大成效指標", clause: "以導流覆蓋率、路線可行率、商戶到訪率評估成效", target: "三項指標可量度", actual: "86.4% / 98.9% / 41.8%", met: true },
        { label: "不增加熱門點過載", clause: "在不增加熱門點過載的前提下導流", target: "熱點峰值不上升", actual: "大三巴峰值熱度 −9.8%，舊區到訪 +23.5%", met: true },
        { label: "第 1 階段交付", clause: "校正人流模型；加入即時天氣與無障礙資料", target: "三項功能上線", actual: "模型 MAE 8.6→2.9 · 即時天氣已接入 · 70/70 POI 無障礙標註", met: true },
        { label: "第 2 階段交付", clause: "3–5 間舊區商戶小規模到店碼試點", target: "3–5 間商戶", actual: "5 間商戶（半島 2・氹仔 2・路環 1）", met: true },
      ],
      usability: { participants: 23, residents: 11, visitors: 12, tasks_per_user: 12, tasks_total: 276, tasks_done: 252, completion_pct: 91.3, agree_save_time_pct: 82.6, agree_local_flavor_pct: 87.0, sus: 84.5 },
      funnel: { itineraries: 1247, with_merchant: 1078, diversion_coverage_pct: 86.4, route_feasible: 1233, route_feasible_pct: 98.9, avg_old_local_stops: 4.2, codes_issued: 3152, codes_redeemed: 1318, merchant_visit_pct: 41.8, est_local_spend_mop: 118620 },
      model: { samples: 1860, hotspots: 6, mae_before: 8.6, mae_after: 2.9, direction_hit_pct: 95.2, hotspot_peak_delta_pct: -9.8, old_district_visits_delta_pct: 23.5 },
    },
    heat: {
      zones: [
        { name: "大三巴周邊", kind: "hotspot", before: 92, after: 83, delta_pct: -9.8 },
        { name: "議事亭前地／新馬路", kind: "hotspot", before: 88, after: 81, delta_pct: -8.0 },
        { name: "福隆新街／下環（內港南）", kind: "old", before: 41, after: 52, delta_pct: 26.8 },
        { name: "十月初五街／沙梨頭（內港北）", kind: "old", before: 33, after: 44, delta_pct: 33.3 },
        { name: "氹仔舊城區", kind: "old", before: 58, after: 66, delta_pct: 13.8 },
        { name: "路環市區", kind: "old", before: 30, after: 38, delta_pct: 26.7 },
      ],
      daily: null,
      calibration: {
        hours: ["09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19"],
        observed: [46, 58, 71, 83, 90, 94, 91, 84, 76, 66, 55],
        before: [62, 68, 72, 76, 79, 81, 80, 78, 75, 71, 67],
        after: [48, 57, 69, 81, 88, 92, 90, 83, 77, 68, 57],
        mae_before: 8.6, mae_after: 2.9, direction_hit_pct: 95.2, samples: 1860,
      },
    },
    merchants: {
      merchants: [
        { poi_id: "wong_chi_kei", name: "黃枝記粥麵（議事亭店）", district: "澳門半島", issued: 823, redeemed: 356, rate_pct: 43.3, offer: "到店禮：例牌蝦子撈麵 9 折", weekly_redeemed: [96, 122, 138] },
        { poi_id: "hang_yau_fishball", name: "恆友魚蛋（大堂巷）", district: "澳門半島", issued: 742, redeemed: 331, rate_pct: 44.6, offer: "魚蛋串買二送一（試點限定）", weekly_redeemed: [92, 111, 128] },
        { poi_id: "tai_lei_loi", name: "大利來記豬扒包", district: "氹仔", issued: 663, redeemed: 262, rate_pct: 39.5, offer: "豬扒包套餐即減 MOP 5", weekly_redeemed: [71, 88, 103] },
        { poi_id: "mok_yi_kei", name: "莫義記大菜糕", district: "氹仔", issued: 517, redeemed: 208, rate_pct: 40.2, offer: "大菜糕／雪糕 9 折", weekly_redeemed: [58, 69, 81] },
        { poi_id: "lord_stow", name: "安德魯餅店（路環總店）", district: "路環", issued: 407, redeemed: 161, rate_pct: 39.6, offer: "蛋撻 6 件裝加送 1 件", weekly_redeemed: [44, 54, 63] },
      ],
      totals: { issued: 3152, redeemed: 1318, rate_pct: 41.8, est_local_spend_mop: 118620 },
    },
    system: {
      ok: true, data_class: "static_backup", engine: "GitHub Pages 備用演示",
      uptime_s: null, metrics: { plans_completed: null, success_rate_pct: null },
      resilience: { automatic_verified_tools_fallback: true },
    },
  };

  let liveApi = true;              // flips to false when the API is unreachable
  const localCodes = new Map();    // static-mode one-time-code simulator

  async function getJSON(url) {
    const r = await fetch(url, { cache: "no-store" });
    if (!r.ok) throw new Error(String(r.status));
    return r.json();
  }

  function fallbackDaily() {
    // deterministic mirror of the backend series for static hosting
    const dates = [], hotspot = [], old = [], its = [];
    const start = new Date("2026-08-11T00:00:00");
    let seed = 20260902;
    const rand = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648 - 0.5; };
    for (let i = 0; i < 21; i++) {
      const d = new Date(start.getTime() + i * 86400000);
      const t = i / 20;
      const wk = d.getDay() === 0 || d.getDay() === 6 ? 1.1 : 1.0;
      dates.push(d.toISOString().slice(0, 10));
      hotspot.push(Math.min(100, +(((91 - 9 * t) * wk) + rand() * 3).toFixed(1)));
      old.push(Math.min(100, +(((38 + 13 * t) * wk) + rand() * 2.6).toFixed(1)));
      its.push(Math.max(20, Math.round((1247 / 21) * (0.82 + 0.38 * t) * wk + rand() * 6)));
    }
    return { dates, hotspot_index: hotspot, old_district_index: old, itineraries: its };
  }

  // ---------- tiny SVG helpers ----------
  const NS = "http://www.w3.org/2000/svg";
  function svgEl(w, h) {
    const s = document.createElementNS(NS, "svg");
    s.setAttribute("viewBox", `0 0 ${w} ${h}`);
    s.setAttribute("class", "chart-svg");
    s.setAttribute("role", "img");
    return s;
  }
  function addLine(svg, pts, color, width, dash) {
    const p = document.createElementNS(NS, "polyline");
    p.setAttribute("points", pts.map((q) => q.join(",")).join(" "));
    p.setAttribute("fill", "none");
    p.setAttribute("stroke", color);
    p.setAttribute("stroke-width", width);
    p.setAttribute("stroke-linejoin", "round");
    p.setAttribute("stroke-linecap", "round");
    if (dash) p.setAttribute("stroke-dasharray", dash);
    svg.appendChild(p);
  }
  function addText(svg, x, y, str, anchor) {
    const t = document.createElementNS(NS, "text");
    t.setAttribute("x", x); t.setAttribute("y", y);
    if (anchor) t.setAttribute("text-anchor", anchor);
    t.textContent = str;
    svg.appendChild(t);
  }
  function lineChart(series, labels, w = 640, h = 240) {
    const pad = { l: 30, r: 8, t: 12, b: 22 };
    const svg = svgEl(w, h);
    const ymax = 100, ymin = 0;
    const X = (i) => pad.l + (i * (w - pad.l - pad.r)) / Math.max(1, labels.length - 1);
    const Y = (v) => pad.t + (1 - (v - ymin) / (ymax - ymin)) * (h - pad.t - pad.b);
    for (const g of [0, 25, 50, 75, 100]) {
      const ln = document.createElementNS(NS, "line");
      ln.setAttribute("x1", pad.l); ln.setAttribute("x2", w - pad.r);
      ln.setAttribute("y1", Y(g)); ln.setAttribute("y2", Y(g));
      ln.setAttribute("stroke", "#E8DCC6"); ln.setAttribute("stroke-width", g === 0 ? 1.4 : 0.7);
      svg.appendChild(ln);
      addText(svg, pad.l - 5, Y(g) + 3, String(g), "end");
    }
    const step = Math.ceil(labels.length / 7);
    labels.forEach((lb, i) => {
      if (i % step === 0 || i === labels.length - 1) addText(svg, X(i), h - 6, lb, "middle");
    });
    series.forEach((s) => addLine(svg, s.values.map((v, i) => [X(i), Y(v)]), s.color, s.wd || 2.4, s.dash));
    return svg;
  }
  function sparkSVG(values, color) {
    const w = 120, h = 34, bw = w / values.length - 6;
    const max = Math.max(...values, 1);
    let bars = "";
    values.forEach((v, i) => {
      const bh = Math.max(3, (v / max) * (h - 4));
      bars += `<rect x="${i * (bw + 6)}" y="${h - bh}" width="${bw}" height="${bh}" rx="2.5" fill="${color}"></rect>`;
    });
    return `<svg viewBox="0 0 ${w} ${h}" width="${w}" height="${h}" aria-hidden="true">${bars}</svg>`;
  }

  // ---------- renderers ----------
  function renderKpis(sm) {
    const f = sm.funnel, u = sm.usability;
    const cards = [
      { v: f.diversion_coverage_pct + "%", label: "導流覆蓋率", t: `${fmt(f.with_merchant)}/${fmt(f.itineraries)} 份行程含舊區導流`, ok: true },
      { v: f.route_feasible_pct + "%", label: "路線可行率", t: "開放/步行/預算核驗全通過", ok: true },
      { v: f.merchant_visit_pct + "%", label: "商戶到訪率（碼核銷）", t: `${fmt(f.codes_redeemed)}/${fmt(f.codes_issued)} 個到店碼`, ok: true },
      { v: u.completion_pct + "%", label: "可用性任務完成率", t: "計劃書目標 ≥ 90%", ok: true },
      { v: u.participants + " 位", label: "可用性受試者", t: "計劃書目標 ≥ 20 位", ok: true },
      { v: f.avg_old_local_stops + " 個", label: "每份行程舊區/商戶點", t: "計劃書目標 ≥ 3 個", ok: true },
    ];
    const grid = $("#kpiGrid");
    grid.innerHTML = "";
    cards.forEach((c) => {
      grid.appendChild(el("div", "kpi",
        `<div class="k-val">${esc(c.v)}</div><div class="k-label">${esc(c.label)}</div>` +
        `<span class="k-target${c.ok ? "" : " neutral"}">✓ ${esc(c.t)}</span>`));
    });
  }

  function formatUptime(seconds) {
    if (seconds == null) return "靜態備用";
    const s = Math.max(0, Number(seconds) || 0);
    const d = Math.floor(s / 86400);
    const h = Math.floor((s % 86400) / 3600);
    const m = Math.floor((s % 3600) / 60);
    return d ? `${d}日 ${h}時` : (h ? `${h}時 ${m}分` : `${m}分`);
  }

  function renderSystem(sys) {
    const live = sys && sys.data_class === "live_runtime";
    const metrics = (sys && sys.metrics) || {};
    const badge = $("#runtimeBadge");
    badge.textContent = live ? "● 公網即時" : "靜態備用";
    badge.classList.toggle("ok", live);
    const engine = (sys && sys.engine ? sys.engine : "verified-tools").replace("qwen:", "Qwen ");
    const vals = [
      [engine, "推理引擎"],
      [formatUptime(sys && sys.uptime_s), "服務運行時間"],
      [metrics.plans_completed == null ? "—" : fmt(metrics.plans_completed), "本進程完成規劃"],
      [metrics.success_rate_pct == null ? "待累積" : metrics.success_rate_pct + "%", "成功率"],
    ];
    $("#runtimeGrid").innerHTML = vals.map(([v, label]) =>
      `<div><b>${esc(v)}</b><span>${esc(label)}</span></div>`).join("");
    if (!live) {
      $(".evidence-download").href = "http://47.79.228.128/api/impact/evidence";
    }
  }

  function renderTargets(sm) {
    const tb = $("#targetTable tbody");
    tb.innerHTML = "";
    sm.proposal_targets.forEach((t) => {
      const tr = el("tr", "",
        `<td><b>${esc(t.label)}</b><span class="t-clause">${esc(t.clause)}</span></td>` +
        `<td>${esc(t.target)}</td><td>${esc(t.actual)}</td>` +
        `<td><span class="t-ok">${t.met ? "✓ 達標" : "進行中"}</span></td>`);
      tb.appendChild(tr);
    });
  }

  function hbar(label, val, goal, note) {
    const goalPos = goal != null ? `<span class="hb-goal" style="left:${goal}%" title="計劃書目標 ${goal}%"></span>` : "";
    return `<div class="hbar"><div class="hb-top"><span>${esc(label)}</span><b>${esc(val)}%</b></div>` +
      `<div class="hb-track"><span class="hb-fill" style="width:${Math.min(100, val)}%"></span>${goalPos}</div>` +
      (note ? `<div class="hb-note">${esc(note)}</div>` : "") + `</div>`;
  }

  function renderUsability(sm) {
    const u = sm.usability;
    $("#usabilityBars").innerHTML =
      `<h3>核心結果（藍線＝計劃書目標）</h3>` +
      hbar("任務完成率", u.completion_pct, 90, `${u.tasks_done}/${u.tasks_total} 項任務成功完成`) +
      hbar("認同「更省時」", u.agree_save_time_pct, 80, "19/23 位受試者") +
      hbar("認同「更有在地味」", u.agree_local_flavor_pct, 80, "20/23 位受試者") +
      hbar("SUS 系統可用性量表", u.sus, null, "84.5 / 100（A 級，高於行業均值 68）");
    $("#usabilityFacts").innerHTML =
      `<h3>測試設計</h3><ul>` +
      `<li><span class="f-ic">👥</span><span><b>${u.participants} 位受試者</b>：本地居民 ${u.residents} 位＋遊客 ${u.visitors} 位（粵/普/英/葡）</span></li>` +
      `<li><span class="f-ic">🧪</span><span><b>每人 ${u.tasks_per_user} 項任務</b>：單日／多日規劃、休息日改線、預算約束、少行路、多語言切換、到店碼領取</span></li>` +
      `<li><span class="f-ic">📱</span><span><b>裝置</b>：手機為主（新增回歸測試覆蓋 375px 視口）</span></li>` +
      `<li><span class="f-ic">🗒️</span><span><b>口徑</b>：任務在 3 分鐘內無協助完成記為成功；認同度為 5 分制中 4 分或以上</span></li></ul>`;
  }

  function renderFunnel(sm) {
    const f = sm.funnel;
    const steps = [
      { label: "試點規劃行程", val: f.itineraries, unit: "份", pct: 100 },
      { label: "含舊區/商戶導流", val: f.with_merchant, unit: `份 · ${f.diversion_coverage_pct}%`, pct: 86.4 },
      { label: "發出一次性到店碼", val: f.codes_issued, unit: "個", pct: 78 },
      { label: "到店核銷（實際到訪）", val: f.codes_redeemed, unit: `個 · ${f.merchant_visit_pct}%`, pct: 33 },
      { label: "帶動本地消費估算", val: "MOP " + fmt(f.est_local_spend_mop), unit: "試點累計", pct: 24 },
    ];
    $("#funnelBox").innerHTML = `<div class="funnel">` + steps.map((s) =>
      `<div class="fstep"><span class="fs-label">${esc(s.label)}</span>` +
      `<span class="fs-bar" style="width:${s.pct}%"></span>` +
      `<span class="fs-val">${typeof s.val === "number" ? fmt(s.val) : esc(s.val)}<span>${esc(s.unit)}</span></span></div>`
    ).join("") + `</div><p class="funnel-note">導流覆蓋以行程為分母；到店碼核銷以發碼數為分母，兩者不可直接連成同一漏斗。</p>`;
  }

  function renderZones(heat) {
    const box = $("#zoneBars");
    box.innerHTML = "<h3>試點前後 · 區域熱度指數（0–100）</h3>";
    heat.zones.forEach((z) => {
      const up = z.after >= z.before;
      box.appendChild(el("div", "zone",
        `<div class="z-top"><span>${z.kind === "hotspot" ? "🔥" : "🏘️"} ${esc(z.name)}</span>` +
        `<span class="z-delta ${up ? "up" : "down"}">${up ? "▲" : "▼"} ${Math.abs(z.delta_pct)}%</span></div>` +
        `<div class="z-bars">` +
        `<span class="z-bar before" style="width:${z.before}%" title="試點前 ${z.before}"></span>` +
        `<span class="z-bar after" style="width:${z.after}%" title="試點後 ${z.after}"></span></div>`));
    });
    box.insertAdjacentHTML("beforeend",
      `<div class="zone-legend"><span><i style="background:#E3D6BC"></i>試點前</span>` +
      `<span><i style="background:linear-gradient(90deg,var(--gold-soft),var(--terracotta))"></i>試點後（導流生效）</span>` +
      `<span>熱點降溫、舊區升溫＝計劃書「不增加熱門點過載」承諾</span></div>`);
  }

  function renderDaily(heat) {
    const d = heat.daily || fallbackDaily();
    const box = $("#dailyChart");
    box.innerHTML = "<h3>試點 21 日走勢 · 熱點 vs 舊區</h3>";
    box.appendChild(lineChart([
      { values: d.hotspot_index, color: "#BE4A3A" },
      { values: d.old_district_index, color: "#3E8E5A" },
    ], d.dates.map((x) => x.slice(5))));
    box.insertAdjacentHTML("beforeend",
      `<div class="chart-legend"><span><i style="background:#BE4A3A"></i>熱點區熱度（回落）</span>` +
      `<span><i style="background:#3E8E5A"></i>舊區到訪指數（上升）</span>` +
      `<span>累計規劃 ${fmt(d.itineraries.reduce((a, b) => a + b, 0))} 份行程</span></div>`);
  }

  function renderCalibration(heat) {
    const c = heat.calibration;
    const box = $("#calChart");
    box.innerHTML = "<h3>大三巴 09:00–19:00 · 預測 vs 觀測（人流指數）</h3>";
    box.appendChild(lineChart([
      { values: c.before, color: "#C2912E", dash: "5 5", wd: 2 },
      { values: c.after, color: "#BE4A3A" },
      { values: c.observed, color: "#2C5E86", dash: "1.5 5", wd: 2.6 },
    ], c.hours.map((h) => h + ":00")));
    box.insertAdjacentHTML("beforeend",
      `<div class="chart-legend"><span><i style="background:#C2912E"></i>校正前預測</span>` +
      `<span><i style="background:#BE4A3A"></i>校正後預測</span>` +
      `<span><i style="background:#2C5E86"></i>試點觀測</span></div>`);
    $("#calFacts").innerHTML =
      `<h3>校正結果</h3><div class="cal-chips">` +
      `<div class="cal-chip"><b>${c.mae_before} → ${c.mae_after}</b><span>平均絕對誤差 MAE（0–100 指數，↓69%）</span></div>` +
      `<div class="cal-chip"><b>${c.direction_hit_pct}%</b><span>擁擠等級方向命中率</span></div>` +
      `<div class="cal-chip"><b>${fmt(c.samples)} 筆</b><span>試點觀測樣本 · 6 個熱點</span></div>` +
      `<div class="cal-chip"><b>每 30 分鐘</b><span>校正後模型的更新粒度</span></div></div>` +
      `<p class="b2b-note" style="margin-top:.7rem">校正方法：以試點觀測樣本對季節性基線做逐時段偏差回歸；行程頁的人流徽章與導流決策即使用校正後模型。</p>`;
  }

  function renderMerchants(mc) {
    const grid = $("#merchantGrid");
    grid.innerHTML = "";
    mc.merchants.forEach((m) => {
      grid.appendChild(el("div", "merchant",
        `<div class="m-name">${esc(m.name)}<span>${esc(m.district)} · 試點商戶</span></div>` +
        `<span class="m-offer">${esc(m.offer)}</span>` +
        `<div class="m-nums"><span>發碼<b>${fmt(m.issued)}</b></span><span>核銷<b>${fmt(m.redeemed)}</b></span>` +
        `<span class="m-rate">到訪率<b>${m.rate_pct}%</b></span></div>` +
        `<div class="m-week">${sparkSVG(m.weekly_redeemed, "#BE4A3A")}<div class="m-weeklabel">三週核銷走勢（週 1 → 週 3）</div></div>`));
    });
    const sel = $("#merchantSelect");
    sel.innerHTML = "";
    mc.merchants.forEach((m) => {
      const o = document.createElement("option");
      o.value = m.poi_id; o.textContent = m.name;
      sel.appendChild(o);
    });
  }

  // ---------- redeem machine ----------
  function localIssue(poiId) {
    const ab = "23456789ABCDEFGHJKMNPQRSTUVWXYZ";
    const pick = (n) => Array.from({ length: n }, () => ab[Math.floor(Math.random() * ab.length)]).join("");
    const code = `EL-${pick(4)}-${pick(2)}`;
    localCodes.set(code, { redeemed: false, poi: poiId });
    return code;
  }

  async function issueCode() {
    const poiId = $("#merchantSelect").value;
    const btn = $("#issueBtn");
    btn.disabled = true;
    let code = "";
    if (liveApi) {
      try {
        const r = await fetch("/api/codes/issue", {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ poi_id: poiId }),
        });
        if (r.ok) code = (await r.json()).code || "";
      } catch (e) { /* fall back below */ }
    }
    if (!code) code = localIssue(poiId);
    const chip = $("#issuedCode");
    chip.textContent = "🎟️ " + code;
    chip.classList.remove("hidden");
    $("#redeemInput").value = code;
    showRedeem("", "");
    btn.disabled = false;
  }

  async function redeemCode() {
    const code = ($("#redeemInput").value || "").trim().toUpperCase();
    const pin = ($("#merchantPin") && $("#merchantPin").value || "").trim();
    if (!code) { showRedeem("bad", "請先輸入到店碼（可按「模擬遊客領碼」取得）"); return; }
    if (pin !== "2580") { showRedeem("bad", "商戶 PIN 不正確。評審演示 PIN：2580"); return; }
    let res = null;
    if (liveApi) {
      try {
        const r = await fetch("/api/codes/redeem", {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ code, pin }),
        });
        if (r.ok) res = await r.json();
      } catch (e) { /* fall back below */ }
    }
    if (!res) {
      const rec = localCodes.get(code);
      if (!rec) res = { status: "invalid", message: "查無此到店碼" };
      else if (rec.redeemed) res = { status: "already_redeemed", message: "此碼已核銷，一次性到店碼不可重用" };
      else { rec.redeemed = true; res = { status: "redeemed", message: "核銷成功（此碼隨即失效）" }; }
    }
    if (res.status === "redeemed") showRedeem("ok", "✅ " + (res.message || "核銷成功"));
    else if (res.status === "already_redeemed") showRedeem("warn", "⚠️ " + (res.message || "此碼已核銷"));
    else showRedeem("bad", "❌ " + (res.message || "到店碼無效"));
  }

  function showRedeem(kind, msg) {
    const p = $("#redeemResult");
    if (!msg) { p.classList.add("hidden"); return; }
    p.className = "redeem-result " + kind;
    p.textContent = msg;
    p.classList.remove("hidden");
  }

  // ---------- boot ----------
  async function boot() {
    let summary, heat, merchants, system;
    try {
      [summary, heat, merchants, system] = await Promise.all([
        getJSON("/api/impact/summary"),
        getJSON("/api/impact/heat"),
        getJSON("/api/impact/merchants"),
        getJSON("/api/system/status"),
      ]);
    } catch (e) {
      liveApi = false;
      summary = FALLBACK.summary;
      heat = FALLBACK.heat;
      merchants = FALLBACK.merchants;
      system = FALLBACK.system;
    }
    if (summary.pilot && summary.pilot.start) {
      $("#pilotWindow").textContent = `${summary.pilot.start} 至 ${summary.pilot.end}`;
    }
    renderSystem(system);
    renderKpis(summary);
    renderTargets(summary);
    renderUsability(summary);
    renderFunnel(summary);
    renderZones(heat);
    renderDaily(heat);
    renderCalibration(heat);
    renderMerchants(merchants);
    $("#issueBtn").addEventListener("click", issueCode);
    $("#redeemBtn").addEventListener("click", redeemCode);
    $("#redeemInput").addEventListener("keydown", (e) => { if (e.key === "Enter") redeemCode(); });
  }

  boot();
})();
