(function () {
  "use strict";

  const D = window.RETAIL_DATA;
  if (!D) {
    document.body.innerHTML = '<p style="padding:32px">数据快照加载失败，请刷新页面。</p>';
    return;
  }

  const PAGE_CONFIG = {
    overview: { title: "零售业务数据洞察与分析", eyebrow: "Executive overview", productScope: true },
    alerts: { title: "预警与行动", eyebrow: "Signals & actions", productScope: false },
    channels: { title: "渠道经营", eyebrow: "Channel operations", productScope: true },
    customers: { title: "客户与留存", eyebrow: "Customer retention", productScope: false },
    products: { title: "产品与竞品", eyebrow: "Product intelligence", productScope: true, productOnly: true },
    marketing: { title: "营销复盘", eyebrow: "Campaign review", productScope: false },
    report: { title: "经营月报", eyebrow: "Management report", productScope: true },
  };

  const TARGET_PAGE = {
    P2: "channels",
    P3: "products",
    P4: "marketing",
    P5: "customers",
    P6: "products",
    P7: "customers",
  };

  const COLORS = ["#24523f", "#a5822f", "#2563a8", "#6952a8", "#a86405", "#22714f"];
  const CHANNEL_STYLES = {
    "银行": { color: "#24523f", shape: "circle" },
    "互联网": { color: "#2563a8", shape: "square" },
    "直销": { color: "#a86405", shape: "diamond" },
    "混合": { color: "#6952a8", shape: "triangle" },
  };
  const productMap = new Map(D.products.map((row) => [row.fund_code, row]));
  const channelMap = new Map(D.channels.map((row) => [row.channel_code, {
    name: row.channel_name,
    type: row.channel_type_cn,
  }]));
  const validPages = Object.keys(PAGE_CONFIG);
  const initialHash = location.hash.replace("#", "");
  const latestMonth = D.months[D.months.length - 1];
  const defaultProduct = productMap.has("017560.OF") ? "017560.OF" : D.products[0].fund_code;
  const migrationMonths = [...new Set(D.migration.map((row) => row.month))].sort();
  const cohortOptions = [...new Set(D.cohort.map((row) => row.cohort))].sort();
  const precursorCustomers = [...new Set(D.precursor.map((row) => row.customer_id))].sort();
  const campaignProducts = [...new Set(D.campaigns.map((row) => row.promote_fund_code).filter(Boolean))].sort();

  const state = {
    page: validPages.includes(initialHash) ? initialHash : "overview",
    month: latestMonth,
    product: "ALL",
    drill: null,
    selectedChannel: "ANT",
    alertScope: "month",
    alertLevels: ["红", "黄"],
    alertEntityType: "全部对象",
    alertProduct: "ALL",
    selectedAlert: null,
    alertDraft: {},
    customerTab: "migration",
    migrationMonth: migrationMonths.includes(latestMonth) ? latestMonth : migrationMonths[migrationMonths.length - 1],
    migrationMetric: "人数",
    migrationPrev: "T3",
    migrationCurr: "T1",
    showFullCustomerId: false,
    cohortPicks: ["2026-01 × ANT", "2026-01 × CMB"].filter((x) => cohortOptions.includes(x)),
    precursorCustomer: precursorCustomers.includes("U102733") ? "U102733" : precursorCustomers[0],
    productTab: "operations",
    includeSimulated: false,
    amacPeriod: null,
    marketingProduct: "ALL",
    campaignMode: "原始",
    selectedCampaign: D.campaigns.some((row) => row.campaign_id === "CP_C") ? "CP_C" : D.campaigns[0].campaign_id,
    reportTab: "preview",
  };

  let savedAlertOverlay = loadAlertOverlay();
  const root = document.getElementById("page-root");
  const titleEl = document.getElementById("page-title");
  const eyebrowEl = document.getElementById("page-kicker");
  const monthSelect = document.getElementById("month-select");
  const productSelect = document.getElementById("product-select");
  const productControl = document.querySelector(".product-control");
  const contextText = document.getElementById("context-text");
  const snapshotBadge = document.getElementById("snapshot-badge");

  function esc(value) {
    return String(value == null ? "" : value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function num(value) {
    const n = Number(value);
    return Number.isFinite(n) ? n : 0;
  }

  function money(value, signed = false) {
    if (value == null || !Number.isFinite(Number(value))) return "—";
    const n = Number(value);
    const sign = n < 0 ? "−" : signed && n > 0 ? "+" : "";
    const v = Math.abs(n);
    if (v >= 1e8) return `${sign}¥${(v / 1e8).toFixed(2)}亿`;
    if (v >= 1e4) return `${sign}¥${(v / 1e4).toFixed(v >= 1e6 ? 1 : 0)}万`;
    return `${sign}¥${Math.round(v).toLocaleString("zh-CN")}`;
  }

  function pct(value, digits = 1, signed = false) {
    if (value == null || !Number.isFinite(Number(value))) return "—";
    const n = Number(value);
    const sign = signed && n > 0 ? "+" : n < 0 ? "−" : "";
    return `${sign}${Math.abs(n * 100).toFixed(digits)}%`;
  }

  function integer(value) {
    return Math.round(num(value)).toLocaleString("zh-CN");
  }

  function shortNumber(value) {
    const n = num(value), v = Math.abs(n), sign = n < 0 ? "−" : "";
    if (v >= 1e8) return `${sign}${(v / 1e8).toFixed(1)}亿`;
    if (v >= 1e4) return `${sign}${(v / 1e4).toFixed(v >= 1e6 ? 0 : 1)}万`;
    return `${sign}${Math.round(v).toLocaleString("zh-CN")}`;
  }

  function monthOf(value) {
    return String(value || "").slice(0, 7);
  }

  function productLabel(code) {
    if (code === "ALL") return "全部产品";
    const product = productMap.get(code);
    return product ? `${product.fund_name} · ${code}` : code;
  }

  function channelStyle(type) {
    return CHANNEL_STYLES[type] || CHANNEL_STYLES["混合"];
  }

  function channelInfo(code) {
    return channelMap.get(code) || { name: code, type: "混合" };
  }

  function campaignChannelType(row) {
    const types = [...new Set(String(row.channel_code || "").split("+").filter(Boolean).map((code) => channelInfo(code).type))];
    return types.length === 1 ? types[0] : "混合";
  }

  function channelBadge(type) {
    const style = channelStyle(type);
    return `<span class="channel-badge"><i class="legend-symbol ${esc(style.shape)}" style="--legend-color:${esc(style.color)}"></i>${esc(type)}</span>`;
  }

  function channelLegend(types = ["银行", "互联网", "直销"], includeSelected = false) {
    const unique = [...new Set(types)].filter(Boolean);
    return `<div class="chart-legend channel-type-legend" role="list" aria-label="渠道类型图例">
      <span class="legend-title" role="listitem">渠道类型：</span>
      ${unique.map((type) => {
        const style = channelStyle(type);
        return `<span role="listitem"><i class="legend-symbol ${esc(style.shape)}" style="--legend-color:${esc(style.color)}" aria-hidden="true"></i>${esc(type)}</span>`;
      }).join("")}
      ${includeSelected ? '<span role="listitem"><i class="legend-symbol selected-ring" aria-hidden="true"></i>金色描边＝当前重点</span><span role="listitem"><i class="legend-symbol bubble-size" aria-hidden="true"></i>点大小＝月末保有</span><span role="listitem"><i class="legend-symbol median-line" aria-hidden="true"></i>虚线＝样本中位数</span>' : ""}
    </div>`;
  }

  function chartLegend(items, label = "图例", extraClass = "") {
    return `<div class="chart-legend ${esc(extraClass)}" role="list" aria-label="${esc(label)}">${items.map((item) => `<span role="listitem"><i class="legend-symbol ${esc(item.kind || "swatch")}" style="--legend-color:${esc(item.color || "#24523f")}" aria-hidden="true"></i>${esc(item.label)}</span>`).join("")}</div>`;
  }

  function cohortLabel(value) {
    const [month, code] = String(value || "").split(" × ");
    const info = channelInfo(code);
    return `${month} · ${info.name}（${info.type}）`;
  }

  function kpi(scope = currentScope(), month = state.month) {
    return D.kpis.find((row) => row.month === month && row.scope === scope) || {
      month, scope, aum: 0, aum_mom: null, holding_customers: 0, new_customers: 0,
      high_value_customers: 0, subscribe: 0, redeem: 0, net: 0, nav: 0,
      fee_annual: 0, product_churn: null, red_alert_records: 0, red_alert_entities: 0,
      snapshot: D.snapshots[month],
    };
  }

  function currentScope() {
    const config = PAGE_CONFIG[state.page];
    if (!config.productScope) return "ALL";
    if (config.productOnly && state.product === "ALL") return defaultProduct;
    return state.product;
  }

  function channelRows(scope = currentScope(), month = state.month) {
    return D.channels.filter((row) => row.month === month && row.scope === scope);
  }

  function allAlerts() {
    return D.alerts.map((row) => ({
      ...row,
      ...(savedAlertOverlay[row.alert_id] || {}),
      ...(state.alertDraft[row.alert_id] || {}),
    }));
  }

  function loadAlertOverlay() {
    try {
      return JSON.parse(localStorage.getItem("wenbo-retail-alert-overlay-v1") || "{}") || {};
    } catch (_) {
      return {};
    }
  }

  function saveAlertOverlay() {
    savedAlertOverlay = { ...savedAlertOverlay, ...state.alertDraft };
    localStorage.setItem("wenbo-retail-alert-overlay-v1", JSON.stringify(savedAlertOverlay));
    state.alertDraft = {};
    toast("处置状态已保存到当前浏览器");
  }

  function metricGrid(items) {
    return `<section class="metric-strip">${items.map((item) => `
      <article class="metric-card${item.tone ? ` tone-${esc(item.tone)}` : ""}"${item.help ? ` title="${esc(item.help)}"` : ""}>
        <span class="metric-label">${esc(item.label)}</span>
        <strong>${esc(item.value)}</strong>
        ${item.delta ? `<span class="metric-delta${item.deltaTone ? ` ${esc(item.deltaTone)}` : ""}">${esc(item.delta)}</span>` : ""}
      </article>`).join("")}</section>`;
  }

  function sectionHead(kicker, title, copy = "", action = "") {
    return `<header class="section-head">
      <div><span class="section-kicker">${esc(kicker)}</span><h2>${esc(title)}</h2>${copy ? `<p>${esc(copy)}</p>` : ""}</div>
      ${action || ""}
    </header>`;
  }

  function panel(kicker, title, copy, body, extraClass = "") {
    return `<section class="panel ${extraClass}">${sectionHead(kicker, title, copy)}${body}</section>`;
  }

  function insight(html, tone = "normal") {
    return `<div class="insight ${esc(tone)}"><span class="insight-mark">${tone === "risk" ? "!" : tone === "warn" ? "↗" : "i"}</span><p>${html}</p></div>`;
  }

  function dataNote(text) {
    return `<details class="data-note"><summary>口径与数据边界</summary><p>${esc(text)}</p></details>`;
  }

  function empty(text) {
    return `<div class="empty-state">${esc(text)}</div>`;
  }

  function table(rows, columns, className = "") {
    if (!rows.length) return empty("当前筛选没有可展示的数据。");
    return `<div class="table-wrap ${esc(className)}" tabindex="0" role="region" aria-label="数据表，可横向滚动"><table><thead><tr>${columns.map((col) => `<th>${esc(col.label)}</th>`).join("")}</tr></thead>
      <tbody>${rows.map((row) => `<tr>${columns.map((col) => {
        const value = typeof col.value === "function" ? col.value(row) : row[col.key];
        const rendered = col.html ? col.html(value, row) : esc(col.format ? col.format(value, row) : value == null ? "—" : value);
        return `<td data-label="${esc(col.label)}"${col.className ? ` class="${esc(col.className)}"` : ""}>${rendered}</td>`;
      }).join("")}</tr>`).join("")}</tbody></table></div>`;
  }

  function chip(text, tone = "") {
    return `<span class="context-chip ${esc(tone)}">${esc(text)}</span>`;
  }

  function tabs(active, items, action) {
    return `<div class="tabs" role="tablist">${items.map((item) => `<button type="button" role="tab" aria-selected="${active === item.id ? "true" : "false"}" class="tab-button${active === item.id ? " active" : ""}" data-action="${esc(action)}" data-value="${esc(item.id)}">${esc(item.label)}</button>`).join("")}</div>`;
  }

  function segmented(active, items, action) {
    return `<div class="segmented" role="group">${items.map((item) => `<button type="button" aria-pressed="${active === item.id ? "true" : "false"}" class="${active === item.id ? "active" : ""}" data-action="${esc(action)}" data-value="${esc(item.id)}">${esc(item.label)}</button>`).join("")}</div>`;
  }

  function isCompactViewport() {
    const width = Number(window.innerWidth);
    return Number.isFinite(width) && width > 0 && width <= 620;
  }

  function svgFrame(width, height, content, label) {
    return `<div class="chart-wrap"><svg class="chart-svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="${esc(label)}" preserveAspectRatio="xMidYMid meet">${content}</svg></div>`;
  }

  function lineChart(rows, series, labelKey, options = {}) {
    if (!rows.length) return empty("暂无趋势数据。");
    const compact = isCompactViewport();
    const W = compact ? 420 : 820, H = options.height || (compact ? 260 : 300), L = compact ? 48 : 58, R = compact ? 12 : 18, T = compact ? 20 : 24, B = compact ? 40 : 44;
    const pw = W - L - R, ph = H - T - B;
    const values = rows.flatMap((row) => series.map((s) => Number(row[s.key])).filter(Number.isFinite));
    let min = options.zeroBase ? Math.min(0, ...values) : Math.min(...values);
    let max = options.zeroBase ? Math.max(0, ...values) : Math.max(...values);
    if (min === max) { min -= 1; max += 1; }
    const pad = (max - min) * 0.1;
    min -= pad; max += pad;
    const x = (index) => L + (rows.length === 1 ? pw / 2 : index * pw / (rows.length - 1));
    const y = (value) => T + (max - value) * ph / (max - min);
    let out = "";
    for (let i = 0; i <= 4; i += 1) {
      const value = min + (max - min) * i / 4;
      const py = y(value);
      out += `<line class="chart-grid" x1="${L}" y1="${py}" x2="${W - R}" y2="${py}"/><text class="chart-axis" x="${L - 8}" y="${py + 4}" text-anchor="end">${esc(options.axisFormat ? options.axisFormat(value) : shortNumber(value))}</text>`;
    }
    const labelStep = Math.max(1, Math.ceil(rows.length / (compact ? 4 : 6)));
    rows.forEach((row, index) => {
      if (index % labelStep === 0 || index === rows.length - 1) out += `<text class="chart-axis" x="${x(index)}" y="${H - 14}" text-anchor="middle">${esc(String(row[labelKey]).slice(2))}</text>`;
    });
    series.forEach((s, si) => {
      const color = s.color || COLORS[si % COLORS.length];
      const points = rows.map((row, index) => `${x(index).toFixed(1)},${y(num(row[s.key])).toFixed(1)}`).join(" ");
      out += `<polyline class="chart-line" points="${points}" fill="none" stroke="${color}"/>`;
      rows.forEach((row, index) => {
        const raw = num(row[s.key]);
        const tip = `${row[labelKey]} · ${s.label} ${s.format ? s.format(raw) : raw}`;
        out += `<circle class="chart-point" cx="${x(index)}" cy="${y(raw)}" r="3.2" fill="${color}"><title>${esc(tip)}</title></circle>`;
      });
    });
    const legend = series.map((s, i) => ({ label: s.label, color: s.color || COLORS[i % COLORS.length], kind: "line" }));
    return svgFrame(W, H, out, options.label || "趋势图") + chartLegend(legend, `${options.label || "趋势图"}图例`);
  }

  function barChart(rows, valueKey, labelKey, options = {}) {
    if (!rows.length) return empty("暂无分布数据。");
    const compact = isCompactViewport();
    const W = compact ? 420 : 820, H = options.height || (compact ? 260 : 300), L = compact ? 46 : 54, R = compact ? 12 : 16, T = 20, B = compact ? 50 : 56;
    const pw = W - L - R, ph = H - T - B;
    const values = rows.map((row) => num(row[valueKey]));
    const min = Math.min(0, ...values), max = Math.max(0, ...values, 1);
    const y = (v) => T + (max - v) * ph / (max - min || 1);
    const zeroY = y(0), band = pw / rows.length, bw = Math.max(6, band * 0.62);
    let out = `<line class="chart-zero" x1="${L}" y1="${zeroY}" x2="${W - R}" y2="${zeroY}"/>`;
    rows.forEach((row, index) => {
      const value = num(row[valueKey]), py = y(value), top = Math.min(py, zeroY), height = Math.max(1, Math.abs(zeroY - py));
      const color = options.color ? options.color(row, value) : value < 0 ? "#b42318" : "#22714f";
      out += `<rect class="chart-bar" x="${L + index * band + (band - bw) / 2}" y="${top}" width="${bw}" height="${height}" rx="2" fill="${color}"><title>${esc(`${row[labelKey]} · ${options.valueFormat ? options.valueFormat(value) : value}`)}</title></rect>`;
      const labelEvery = Math.max(1, Math.ceil(rows.length / (compact ? 4 : 7)));
      if ((!compact && rows.length <= 14) || index % labelEvery === 0 || index === rows.length - 1) out += `<text class="chart-axis" x="${L + (index + 0.5) * band}" y="${H - 16}" text-anchor="middle">${esc(String(row[labelKey]).slice(options.trimLabel ? options.trimLabel : 0))}</text>`;
    });
    const legend = options.legend?.length ? chartLegend(options.legend, `${options.label || "柱状图"}图例`) : "";
    return svgFrame(W, H, out, options.label || "柱状图") + legend;
  }

  function horizontalBars(rows, valueKey, labelKey, options = {}) {
    if (!rows.length) return empty("暂无分布数据。");
    const max = Math.max(...rows.map((row) => Math.abs(num(row[valueKey]))), 1);
    return `<div class="hbars">${rows.map((row, index) => {
      const value = num(row[valueKey]);
      const width = Math.max(1, Math.abs(value) / max * 100);
      const color = options.color ? options.color(row, index) : COLORS[index % COLORS.length];
      return `<div class="hbar-row"><span>${esc(row[labelKey])}</span><div class="hbar-track"><i style="width:${width}%;background:${color}"></i></div><strong>${esc(options.format ? options.format(value, row) : integer(value))}</strong></div>`;
    }).join("")}</div>`;
  }

  function scatterMark(shape, cx, cy, radius, className, color) {
    const common = `class="${esc(className)}" fill="${esc(color)}" aria-hidden="true"`;
    if (shape === "square") {
      const side = radius * 1.68;
      return `<rect ${common} x="${cx - side / 2}" y="${cy - side / 2}" width="${side}" height="${side}" rx="2"/>`;
    }
    if (shape === "diamond") {
      const rr = radius * 1.2;
      return `<path ${common} d="M ${cx} ${cy - rr} L ${cx + rr} ${cy} L ${cx} ${cy + rr} L ${cx - rr} ${cy} Z"/>`;
    }
    if (shape === "triangle") {
      const rr = radius * 1.3;
      return `<path ${common} d="M ${cx} ${cy - rr} L ${cx + rr} ${cy + rr * 0.78} L ${cx - rr} ${cy + rr * 0.78} Z"/>`;
    }
    return `<circle ${common} cx="${cx}" cy="${cy}" r="${radius}"/>`;
  }

  function scatterChart(rows, config) {
    if (!rows.length) return empty("暂无可比较样本。");
    const compact = isCompactViewport();
    const W = compact ? 420 : 820, H = config.height || (compact ? 290 : 330), L = compact ? 52 : 64, R = compact ? 14 : 24, T = 24, B = compact ? 46 : 50;
    const pw = W - L - R, ph = H - T - B;
    const xs = rows.map((row) => num(row[config.xKey])), ys = rows.map((row) => num(row[config.yKey]));
    let xmin = Math.min(...xs), xmax = Math.max(...xs), ymin = Math.min(...ys), ymax = Math.max(...ys);
    if (xmin === xmax) { xmin -= 1; xmax += 1; }
    if (ymin === ymax) { ymin -= 1; ymax += 1; }
    const xpad = (xmax - xmin) * 0.12, ypad = (ymax - ymin) * 0.14;
    xmin -= xpad; xmax += xpad; ymin -= ypad; ymax += ypad;
    const x = (v) => L + (v - xmin) * pw / (xmax - xmin);
    const y = (v) => T + (ymax - v) * ph / (ymax - ymin);
    const rvals = config.rKey ? rows.map((row) => Math.max(0, num(row[config.rKey]))) : [];
    const rmax = Math.max(...rvals, 1);
    let out = "";
    for (let i = 0; i <= 4; i += 1) {
      const xv = xmin + (xmax - xmin) * i / 4, yv = ymin + (ymax - ymin) * i / 4;
      out += `<line class="chart-grid" x1="${x(xv)}" y1="${T}" x2="${x(xv)}" y2="${H - B}"/><line class="chart-grid" x1="${L}" y1="${y(yv)}" x2="${W - R}" y2="${y(yv)}"/>`;
      out += `<text class="chart-axis" x="${x(xv)}" y="${H - 20}" text-anchor="middle">${esc(config.xFormat ? config.xFormat(xv) : xv.toFixed(1))}</text><text class="chart-axis" x="${L - 8}" y="${y(yv) + 4}" text-anchor="end">${esc(config.yFormat ? config.yFormat(yv) : yv.toFixed(1))}</text>`;
    }
    if (config.xMid != null) out += `<line class="chart-reference" x1="${x(config.xMid)}" y1="${T}" x2="${x(config.xMid)}" y2="${H - B}"/>`;
    if (config.yMid != null) out += `<line class="chart-reference" x1="${L}" y1="${y(config.yMid)}" x2="${W - R}" y2="${y(config.yMid)}"/>`;
    rows.forEach((row, index) => {
      const radius = config.rKey ? 6 + Math.sqrt(num(row[config.rKey]) / rmax) * 17 : 8;
      const color = config.color ? config.color(row, index) : COLORS[index % COLORS.length];
      const selected = config.selected && config.selected(row);
      const tip = config.tip ? config.tip(row) : row[config.labelKey];
      const shape = config.shape ? config.shape(row, index) : "circle";
      const cx = x(num(row[config.xKey])), cy = y(num(row[config.yKey]));
      out += `<g class="chart-symbol" tabindex="0" role="img" aria-label="${esc(tip)}"><title>${esc(tip)}</title>${scatterMark(shape, cx, cy, radius, `chart-bubble${selected ? " selected" : ""}`, color)}</g>`;
      if (selected || config.labelAll) {
        const placeLeft = cx > W - R - 92;
        out += `<text class="chart-label${selected ? " selected" : ""}" x="${placeLeft ? cx - radius - 5 : cx + radius + 5}" y="${cy + 4}" text-anchor="${placeLeft ? "end" : "start"}">${esc(row[config.labelKey])}</text>`;
      }
    });
    out += `<text class="chart-axis-title" x="${L + pw / 2}" y="${H - 3}" text-anchor="middle">${esc(config.xLabel)}</text><text class="chart-axis-title" x="14" y="${T + ph / 2}" transform="rotate(-90 14 ${T + ph / 2})" text-anchor="middle">${esc(config.yLabel)}</text>`;
    return svgFrame(W, H, out, config.label || "散点图");
  }

  function waterfallChart(values) {
    const opening = num(values.aum) - num(values.net) - num(values.nav);
    const subscribe = num(values.subscribe), redeem = num(values.redeem), nav = num(values.nav), closing = num(values.aum);
    const points = [
      { label: "期初", start: 0, end: opening, value: opening, color: "#24523f" },
      { label: "申购", start: opening, end: opening + subscribe, value: subscribe, color: "#22714f" },
      { label: "赎回", start: opening + subscribe, end: opening + subscribe - redeem, value: -redeem, color: "#b42318" },
      { label: "净值变动", start: opening + num(values.net), end: closing, value: nav, color: nav >= 0 ? "#22714f" : "#a86405" },
      { label: "期末", start: 0, end: closing, value: closing, color: "#a5822f" },
    ];
    const compact = isCompactViewport();
    const W = compact ? 420 : 820, H = compact ? 280 : 330, L = compact ? 28 : 42, R = compact ? 10 : 16, T = compact ? 24 : 28, B = compact ? 52 : 62, pw = W - L - R, ph = H - T - B;
    const max = Math.max(...points.flatMap((p) => [p.start, p.end]), 1) * 1.08;
    const y = (v) => T + (max - v) * ph / max;
    const band = pw / points.length, bw = band * 0.55;
    let out = "";
    points.forEach((p, index) => {
      const top = y(Math.max(p.start, p.end)), height = Math.max(2, Math.abs(y(p.start) - y(p.end)));
      const x = L + index * band + (band - bw) / 2;
      out += `<rect class="chart-bar" x="${x}" y="${top}" width="${bw}" height="${height}" rx="3" fill="${p.color}"><title>${esc(`${p.label} · ${money(p.value, index > 0 && index < 4)}`)}</title></rect>`;
      out += `<text class="chart-value" x="${x + bw / 2}" y="${Math.max(14, top - 7)}" text-anchor="middle">${esc(money(p.value, index > 0 && index < 4).replace("¥", ""))}</text><text class="chart-axis" x="${x + bw / 2}" y="${H - 22}" text-anchor="middle">${esc(p.label)}</text>`;
      if (index < points.length - 1) out += `<line class="chart-connector" x1="${x + bw}" y1="${y(p.end)}" x2="${L + (index + 1) * band + (band - bw) / 2}" y2="${y(p.end)}"/>`;
    });
    return svgFrame(W, H, out, "AUM经营归因瀑布");
  }

  function toast(message) {
    let el = document.getElementById("toast");
    if (!el) {
      el = document.createElement("div");
      el.id = "toast";
      el.className = "toast";
      document.body.appendChild(el);
    }
    el.textContent = message;
    el.classList.add("show");
    clearTimeout(toast.timer);
    toast.timer = setTimeout(() => el.classList.remove("show"), 2400);
  }

  function drillBanner(expectedType) {
    if (!state.drill || (expectedType && state.drill.entity_type !== expectedType)) return "";
    return `<div class="drill-banner"><div><strong>来自 ${esc(state.drill.rule_id)} 的下钻</strong><span>${esc(state.drill.entity_name)} · ${esc(state.drill.start)} 至 ${esc(state.drill.end)}</span></div><button type="button" class="button ghost small" data-action="clear-drill">清除下钻</button></div>`;
  }

  function filteredAlerts() {
    return allAlerts().filter((row) => {
      if (state.alertScope === "month" && monthOf(row.window_end) !== state.month) return false;
      if (!state.alertLevels.includes(row.level)) return false;
      if (state.alertEntityType !== "全部对象" && row.entity_type !== state.alertEntityType) return false;
      if (state.alertEntityType === "产品" && state.alertProduct !== "ALL" && row.entity_id !== state.alertProduct) return false;
      return true;
    });
  }

  function capabilityHero() {
    const channelCount = new Set(D.channels.map((row) => row.channel_code)).size;
    return `<section class="capability-hero" aria-labelledby="capability-title">
      <header class="capability-intro">
        <span class="section-kicker">Retail data analytics portfolio</span>
        <h2 id="capability-title">从多源零售数据到经营增量机会</h2>
        <p>整合渠道代销、线上直销、客户持仓交易、净值规模、营销活动与外部排名数据，完成清洗映射、跨表整合与指标建模，统一产品、渠道、客户与时间口径；围绕渠道效能、客户分层与流失、产品销售与竞品、营销效果，形成“监控—诊断—名单—行动—复盘”的经营分析闭环。</p>
        <div class="capability-tags" aria-label="岗位能力覆盖">
          <span>多源数据治理</span><span>零售经营监控</span><span>专题诊断</span><span>竞品对标</span><span>客户留存</span><span>决策报告</span>
        </div>
      </header>
      <div class="capability-flow" aria-label="分析能力链">
        <article>
          <span>01 · Data foundation</span>
          <strong>${integer(D.months.length)}个月 × ${integer(D.products.length)}只产品 × ${integer(channelCount)}个渠道</strong>
          <p>只读整合 DuckDB 与 PBI 快照，处理主数据映射、跨表粒度、缺失值和口径核验，并保留事实来源与边界。</p>
        </article>
        <article>
          <span>02 · Business diagnosis</span>
          <strong>六类零售经营场景</strong>
          <p>从总量监控下钻到渠道、客户、产品、竞品、活动与留存，区分经营变化和市场影响。</p>
        </article>
        <article>
          <span>03 · Decision delivery</span>
          <strong>${integer(D.alert_rules.length)}条规则 × 预警工作台 × 管理月报</strong>
          <p>把异常聚合为对象级事件，连接责任人、处置备注、客户名单、验证指标和可下载事实表。</p>
        </article>
      </div>
    </section>`;
  }

  function leadershipBrief(values, channels, judgment) {
    const weakest = [...channels].sort((a, b) => num(a.net_inflow) - num(b.net_inflow))[0];
    const impactBase = Math.abs(num(values.net)) + Math.abs(num(values.nav));
    const businessShare = impactBase ? Math.abs(num(values.net)) / impactBase : 0;
    const what = `${currentScope() === "ALL" ? "月末" : "产品"} AUM ${money(values.aum)}，环比 ${pct(values.aum_mom, 1, true)}；经营净申购 ${money(values.net, true)}。`;
    const why = values.net < 0 && values.nav < 0
      ? `经营净流出与净值下跌共同拖累，按绝对影响估算，经营因素约占 ${pct(businessShare, 0)}。`
      : judgment.replace(/<[^>]+>/g, "");
    const where = weakest
      ? `${weakest.channel_name}当月净申购最低（${money(weakest.net_inflow, true)}），月流失率 ${pct(weakest["月流失率"])}。`
      : "当前筛选没有渠道层结果，先检查映射与快照完整性。";
    const act = weakest
      ? `先拆解${weakest.channel_name}的产品贡献，再按客户层级生成跟进名单。`
      : "补齐渠道映射后再开展产品与客户归因。";
    return `<section class="management-brief" aria-labelledby="management-brief-title">
      <header>
        <div><span class="section-kicker">Executive brief · ${esc(state.month)}</span><h2 id="management-brief-title">领导摘要：结论、归因、对象与动作</h2></div>
        <p>首屏固定回答四个管理问题；下方各工作区保留趋势、对比、名单与口径证据。</p>
      </header>
      <div class="brief-grid">
        <article><span>What · 发生什么</span><strong>${esc(what)}</strong><small>验证：AUM、净申购、环比</small></article>
        <article><span>Why · 为什么</span><strong>${esc(why)}</strong><small>方法：申赎与净值影响拆分</small></article>
        <article><span>Where · 影响哪里</span><strong>${esc(where)}</strong><small>定位：渠道 → 产品 → 客户层级</small></article>
        <article class="action"><span>Act · 下一步</span><strong>${esc(act)}</strong><small>协同：渠道经营 × 产品 × 客户运营；复盘：次月净保有、流失率、90日留存</small></article>
      </div>
    </section>`;
  }

  function scenarioCapabilityMap() {
    const scenarios = [
      { page: "channels", title: "渠道效能", data: "AUM、净申购、户均、流失、尾随成本", insight: "识别规模质量、渠道依赖与资源效率", output: "渠道拓展与维护优先级" },
      { page: "customers", view: "migration", title: "客户分层画像", data: "价值层级、迁移路径、主渠道、交易产品", insight: "识别升级机会与降级原因", output: "分层经营与客户名单" },
      { page: "products", view: "operations", title: "产品销售复盘", data: "净值、周度净申购、规模、风险收益", insight: "区分行情驱动与真实销售动能", output: "产品推广与货架动作" },
      { page: "products", view: "benchmark", title: "竞品对标", data: "同类规模、风险收益、AMAC销售机构排名", insight: "判断产品位置与渠道覆盖差距", output: "竞品专题与渠道策略" },
      { page: "marketing", title: "营销活动效果", data: "曝光链路、转化、基线、30日赎回、90日留存", insight: "识别补贴依赖与增长可持续性", output: "活动复盘与预算建议" },
      { page: "customers", view: "retention", title: "客户留存流失", data: "Cohort、层级迁移、行为前兆、历史流失样本", insight: "定位流失窗口与主要赎回产品", output: "挽留名单与触达时点" },
    ];
    return panel("Capability map", "零售全业务场景分析体系", "每个工作区都从关键数据出发，形成可解释洞察并落到经营输出。", `<div class="scenario-grid">${scenarios.map((item) => `<button type="button" class="scenario-card" data-action="navigate" data-value="${esc(item.page)}"${item.view ? ` data-view="${esc(item.view)}"` : ""} aria-label="打开${esc(item.title)}分析">
      <span>${esc(item.title)}</span><strong>${esc(item.data)}</strong><p>${esc(item.insight)}</p><small>${esc(item.output)} <b aria-hidden="true">→</b></small>
    </button>`).join("")}</div>`);
  }

  function productionDataGaps() {
    return `<details class="panel details-panel production-gaps"><summary>生产化补数与验证计划</summary><div class="gap-grid">
      <article><strong>渠道目标与成本</strong><p>补充目标值、资源投入、获客成本和净收入，评估达成率与净贡献。</p></article>
      <article><strong>客户完整画像</strong><p>补充风险偏好、服务触点和授权行为数据，再扩展偏好、LTV与流失概率。</p></article>
      <article><strong>竞品货架信息</strong><p>补充上架覆盖、费率、曝光与同类产品明细，定位渠道覆盖和转化差距。</p></article>
      <article><strong>活动增量评估</strong><p>补充完整成本、对照组与留存后AUM，计算增量净AUM和留存客户成本。</p></article>
    </div></details>`;
  }

  function renderOverview() {
    const scope = currentScope(), scoped = scope !== "ALL", values = kpi(scope);
    const productName = scoped ? productMap.get(scope)?.fund_name : null;
    const metrics = [
      { label: scoped ? "产品 AUM" : "月末 AUM", value: money(values.aum), delta: `环比 ${pct(values.aum_mom, 1, true)}`, help: "月末最后交易日持仓市值；环比基于上一月末快照。" },
      { label: "经营净申购", value: money(values.net, true), delta: `净值影响 ${money(values.nav, true)}` },
      { label: scoped ? "产品持有人" : "持仓客户", value: `${integer(values.holding_customers)} 人` },
      { label: scoped ? "产品首购客户" : "新增首购客户", value: `${integer(values.new_customers)} 人` },
      { label: scoped ? "高价值持有人" : "高价值客户", value: `${integer(values.high_value_customers)} 人`, delta: "客户总AUM ≥50万" },
      scoped
        ? { label: "产品持有流失率", value: pct(values.product_churn), delta: `红色日志 ${integer(values.red_alert_records)} 条` }
        : { label: "本月红色命中", value: `${integer(values.red_alert_records)} 条`, delta: `涉及 ${integer(values.red_alert_entities)} 个对象` },
    ];
    const alerts = allAlerts().filter((row) => monthOf(row.window_end) === state.month && row.level === "红" && (!scoped || (row.entity_type === "产品" && row.entity_id === scope)));
    const cases = aggregateAlerts(alerts).slice(0, 4);
    const totalChange = num(values.net) + num(values.nav);
    let judgment = "经营净流入与市场收益同向贡献，下一步重点验证增长是否来自可持续客户与产品。";
    let tone = "normal";
    if (values.net < 0 && values.nav < 0 && totalChange < 0) {
      const share = Math.abs(values.net) / Math.abs(totalChange || 1);
      judgment = `本月 AUM 变动中，经营净流出贡献约 <strong>${pct(share, 0)}</strong>，市场净值影响约 <strong>${pct(1 - share, 0)}</strong>。两类原因需要分开处置。`;
      tone = "risk";
    } else if (values.net >= 0 && values.nav < 0) {
      judgment = "经营净流入抵消了部分市场下跌，建议继续观察净流入质量与90日留存。";
      tone = "warn";
    } else if (values.net < 0 && values.nav >= 0) {
      judgment = "市场上涨掩盖了经营净流出；只看期末 AUM 会高估真实经营表现。";
      tone = "warn";
    }
    const trend = D.kpis.filter((row) => row.scope === scope && row.month <= state.month).sort((a, b) => a.month.localeCompare(b.month)).slice(-13);
    const channels = channelRows(scope).sort((a, b) => num(b.aum_end) - num(a.aum_end));
    const worst = [...channels].sort((a, b) => num(a.net_inflow) - num(b.net_inflow))[0];
    return `
      ${capabilityHero()}
      ${leadershipBrief(values, channels, judgment)}
      ${metricGrid(metrics)}
      <div class="content-grid split-main">
        ${panel("Why", `${productName ? `${productName} · ` : ""}AUM经营归因瀑布`, "首尾是绝对总量，中间仅累计申购、赎回和净值变动。", waterfallChart(values))}
        ${panel("So what", "本月判断", "先把异动归因成经营问题或市场问题，再决定下钻方向。", `${insight(judgment, tone)}
          <div class="priority-list">${cases.length ? `<h3>优先关注对象</h3>${cases.map((row) => `<div class="priority-item"><i class="level-dot red"></i><div><strong>${esc(row.rule_id)} · ${esc(row.entity_name)}</strong><span>${integer(row.records)} 条命中记录 · 最近 ${esc(String(row.latest).slice(5, 10))}</span></div></div>`).join("")}<button class="button primary wide" data-action="navigate" data-value="alerts">进入预警工作台</button>` : `<div class="success-box">所选月没有红色命中记录。</div>`}</div>`)}
      </div>
      ${panel("Trend", "AUM 与净申购的同轴时间对照", "上下两个面板共享月份：上看结果，下看经营流量。", `<div class="chart-stack">${lineChart(trend, [{ key: "aum", label: "月末AUM", color: "#24523f", format: money }], "month", { axisFormat: shortNumber, label: "AUM趋势" })}${barChart(trend, "net", "month", { valueFormat: (v) => money(v, true), trimLabel: 2, label: "净申购趋势" })}</div>`)}
      ${channels.length ? `${panel("Where", scoped ? "产品渠道分布与当月贡献" : "渠道结构与当月贡献", scoped ? "所选产品在各渠道的保有、净申购和持有流失率。" : "按所选月末 AUM 排序，同时保留净申购、户均和流失率。", table(channels, [
        { key: "channel_name", label: "渠道" }, { key: "channel_type_cn", label: "类型", html: (v) => channelBadge(v) },
        { key: "aum_share", label: scoped ? "产品份额" : "AUM份额", format: pct },
        { key: "net_inflow", label: "当月净申购", format: (v) => money(v, true), className: "numeric" },
        { key: "客户数", label: "持仓客户", format: integer, className: "numeric" },
        { key: "户均_aum", label: "户均AUM", format: money, className: "numeric" },
        { key: "月流失率", label: scoped ? "产品持有流失率" : "月流失率", format: pct, className: "numeric" },
      ]))}
      <div class="action-grid">
        <article class="action-card"><span>渠道动作</span><strong>复盘 ${esc(worst?.channel_name || "—")}</strong><p>当月净申购 ${esc(money(worst?.net_inflow, true))}，优先拆解产品贡献。</p></article>
        <article class="action-card"><span>客户动作</span><strong>${values.new_customers ? "验证新增质量" : "先核查数据完整性"}</strong><p>${values.new_customers ? "继续观察次月复购和90日持有，避免只看首购。" : "新增首购为 0，再决定是否启动拉新专项。"}</p></article>
        <article class="action-card"><span>风险动作</span><strong>按对象合并事件</strong><p>红色日志涉及 ${integer(values.red_alert_entities)} 个对象，避免逐日命中造成工单膨胀。</p></article>
      </div>` : ""}
      ${scenarioCapabilityMap()}
      ${productionDataGaps()}
      ${dataNote(`数据源：持仓快照、日度AUM归因、交易与预警日志。自有产品年化管理费粗估为 ${money(values.fee_annual)}，仅用于经营估算，不等同财务确认收入。`)}`;
  }

  function aggregateAlerts(rows) {
    const groups = new Map();
    rows.forEach((row) => {
      const key = [row.rule_id, row.level, row.entity_type, row.entity_id, row.entity_name].join("|");
      const current = groups.get(key) || { ...row, records: 0, latest: row.window_end, earliest: row.window_start, maxMetric: -Infinity };
      current.records += 1;
      if (String(row.window_end) > String(current.latest)) current.latest = row.window_end;
      if (String(row.window_start) < String(current.earliest)) current.earliest = row.window_start;
      current.maxMetric = Math.max(current.maxMetric, num(row.metric_value));
      groups.set(key, current);
    });
    return [...groups.values()].sort((a, b) => (a.level === b.level ? b.records - a.records : a.level === "红" ? -1 : 1));
  }

  function renderAlerts() {
    const rows = filteredAlerts();
    const redCount = rows.filter((row) => row.level === "红").length;
    const yellowCount = rows.filter((row) => row.level === "黄").length;
    const objects = new Set(rows.map((row) => `${row.entity_type}|${row.entity_id}`)).size;
    const openCount = rows.filter((row) => row.status !== "已闭环").length;
    const entityTypes = ["全部对象", ...new Set(D.alerts.map((row) => row.entity_type))];
    const alertProducts = [...new Map(D.alerts.filter((row) => row.entity_type === "产品").map((row) => [row.entity_id, row.entity_name])).entries()];
    const distribution = [...new Set(D.alert_rules.map((row) => row.rule_id))].map((rule) => ({ rule, count: rows.filter((row) => row.rule_id === rule).length }));
    const cases = aggregateAlerts(rows);
    const selected = rows.find((row) => row.alert_id === state.selectedAlert) || rows[0];
    if (selected && state.selectedAlert !== selected.alert_id) state.selectedAlert = selected.alert_id;
    const filters = `<div class="filter-panel">
      <label class="control"><span>时间范围</span><select data-control="alert-scope"><option value="month"${state.alertScope === "month" ? " selected" : ""}>${esc(state.month)}</option><option value="all"${state.alertScope === "all" ? " selected" : ""}>全部历史</option></select></label>
      <fieldset class="control check-control"><legend>级别</legend><label><input type="checkbox" data-control="alert-level" value="红"${state.alertLevels.includes("红") ? " checked" : ""}><i class="level-dot red"></i>红</label><label><input type="checkbox" data-control="alert-level" value="黄"${state.alertLevels.includes("黄") ? " checked" : ""}><i class="level-dot yellow"></i>黄</label></fieldset>
      <label class="control"><span>对象类型</span><select data-control="alert-entity">${entityTypes.map((value) => `<option${state.alertEntityType === value ? " selected" : ""}>${esc(value)}</option>`).join("")}</select></label>
      ${state.alertEntityType === "产品" ? `<label class="control"><span>预警产品</span><select data-control="alert-product"><option value="ALL">全部预警产品</option>${alertProducts.map(([code, name]) => `<option value="${esc(code)}"${state.alertProduct === code ? " selected" : ""}>${esc(name)} · ${esc(code)}</option>`).join("")}</select></label>` : ""}
    </div>`;
    const caseTable = table(cases, [
      { key: "rule_id", label: "规则" }, { key: "level", label: "级别", html: (v) => `<span class="level-badge ${v === "红" ? "red" : "yellow"}">${esc(v)}</span>` },
      { key: "entity_name", label: "对象" }, { key: "records", label: "命中记录", format: integer },
      { key: "earliest", label: "开始", format: (v) => String(v).slice(0, 10) }, { key: "latest", label: "最近", format: (v) => String(v).slice(0, 10) },
    ]);
    const editor = rows.length ? `<div class="table-wrap alert-editor" tabindex="0" role="region" aria-label="预警处置工作台"><table><thead><tr><th>ID / 规则</th><th>对象与事实</th><th>状态</th><th>Owner</th><th>处置备注</th></tr></thead><tbody>${rows.map((row) => `<tr>
      <td data-label="ID / 规则"><strong>${esc(row.alert_id)}</strong><span>${esc(row.rule_id)} · ${esc(row.level)} · ${esc(String(row.window_end).slice(0, 10))}</span></td>
      <td data-label="对象与事实"><strong>${esc(row.entity_name)}</strong><span>${esc(row.summary_text)}</span></td>
      <td data-label="状态"><select aria-label="${esc(`${row.alert_id}处置状态`)}" data-alert-id="${esc(row.alert_id)}" data-alert-field="status"><option${row.status === "未处理" ? " selected" : ""}>未处理</option><option${row.status === "跟进中" ? " selected" : ""}>跟进中</option><option${row.status === "已闭环" ? " selected" : ""}>已闭环</option></select></td>
      <td data-label="Owner"><input aria-label="${esc(`${row.alert_id}负责人`)}" data-alert-id="${esc(row.alert_id)}" data-alert-field="owner" value="${esc(row.owner)}" placeholder="负责人"></td>
      <td data-label="处置备注"><input aria-label="${esc(`${row.alert_id}处置备注`)}" data-alert-id="${esc(row.alert_id)}" data-alert-field="note" value="${esc(row.note)}" placeholder="处置备注"></td>
    </tr>`).join("")}</tbody></table></div><div class="panel-actions"><button type="button" class="button primary" data-action="save-alerts">保存处置状态</button><span>演示状态仅保存在当前浏览器，不修改原始日志。</span></div>` : empty("当前筛选没有命中记录。");
    const drill = selected ? `<div class="drill-card"><div><span class="level-badge ${selected.level === "红" ? "red" : "yellow"}">${esc(selected.level)}</span><strong>${esc(selected.rule_id)} · ${esc(selected.entity_name)}</strong><p>${esc(selected.summary_text)}</p><small>阈值：${esc(selected.threshold_desc)} · 窗口：${esc(String(selected.window_start).slice(0, 10))} 至 ${esc(String(selected.window_end).slice(0, 10))}</small></div>${TARGET_PAGE[selected.target_page] ? `<button type="button" class="button primary" data-action="drill-alert" data-value="${esc(selected.alert_id)}">下钻到「${esc(PAGE_CONFIG[TARGET_PAGE[selected.target_page]].title)}」</button>` : ""}</div>` : empty("暂无可下钻记录。");
    return `${filters}${metricGrid([
      { label: "红色命中记录", value: `${integer(redCount)} 条` }, { label: "黄色命中记录", value: `${integer(yellowCount)} 条` },
      { label: "涉及对象", value: `${integer(objects)} 个` }, { label: "未闭环记录", value: `${integer(openCount)} 条` },
    ])}
    <div class="content-grid two-col">
      ${panel("Signal", "规则命中分布", "记录数用于观察噪声与集中度，不能直接等同工单数。", horizontalBars(distribution, "count", "rule", { color: (_, i) => COLORS[i % COLORS.length] }))}
      ${panel("Cases", "对象级事件", "把同一规则、同一对象的多日记录先聚合，再决定是否创建处置任务。", caseTable)}
    </div>
    ${panel("Act", "处置工作台", "状态、Owner、备注形成独立的浏览器 overlay，原始 alert_log 不被覆盖。", editor)}
    ${panel("Drill", "选一条记录下钻", "下钻会把对象和窗口带到目标页，并可在目标页清除。", `<label class="control inline-control"><span>命中记录</span><select data-control="selected-alert">${rows.map((row) => `<option value="${esc(row.alert_id)}"${selected?.alert_id === row.alert_id ? " selected" : ""}>${esc(row.alert_id)}｜${esc(row.level)}｜${esc(row.entity_name)}｜${esc(String(row.window_end).slice(0, 10))}</option>`).join("")}</select></label>${drill}`)}
    <details class="panel details-panel"><summary>查看 7 条规则定义与可运行边界</summary>${table(D.alert_rules, [
      { key: "rule_id", label: "规则" }, { key: "rule_name", label: "名称" }, { key: "threshold_desc", label: "阈值" }, { key: "level", label: "级别" }, { key: "status", label: "状态" },
    ])}<p class="caption">R5、R7可计算但当前数据无命中；R6存在近端确认盲区。</p></details>
    ${dataNote("当前 alert_log 为精选演示案例，并非完整七规则全历史扫描。处置状态使用浏览器本地 overlay；生产多用户环境应迁移至带并发控制和审计日志的数据库。")}`;
  }

  function renderChannels() {
    const scope = currentScope(), scoped = scope !== "ALL", rows = channelRows(scope);
    if (!rows.length) return empty("所选月份没有渠道结果表数据。");
    const codes = rows.sort((a, b) => num(b.aum_end) - num(a.aum_end)).map((row) => row.channel_code);
    if (state.drill?.entity_type === "渠道" && codes.includes(state.drill.entity_id)) state.selectedChannel = state.drill.entity_id;
    if (!codes.includes(state.selectedChannel)) state.selectedChannel = codes.includes("ANT") ? "ANT" : codes[0];
    const selected = rows.find((row) => row.channel_code === state.selectedChannel);
    const annualTrail = num(selected.aum_end) * num(selected["尾随佣金_bps"]) / 10000;
    const history = D.channels.filter((row) => row.scope === scope && row.channel_code === state.selectedChannel && row.month <= state.month).sort((a, b) => a.month.localeCompare(b.month)).slice(-13);
    const mixRows = D.tier_mix.filter((row) => row.month === state.month && row.scope === scope);
    const medChurn = median(rows.map((row) => num(row["月流失率"]))), medAvg = median(rows.map((row) => num(row["户均_aum"])));
    const messages = [];
    if (num(selected["月流失率"]) > medChurn) messages.push("流失率高于渠道中位数，先做客户名单级归因");
    if (num(selected["户均_aum"]) > medAvg) messages.push("户均高于中位数，适合高价值客人工维护");
    if (selected.channel_code === "DIRECT_APP" && !scoped) messages.push(`直销90日留存约 ${pct(D.direct_app_retention)} 且无尾随，适合作为长期承接阵地`);
    if (num(selected.net_3m) < 0) messages.push("近3月净流出，资源考核应从销量切换到净保有与留存");
    if (!messages.length) messages.push("当前规模与质量没有明显异常，维持监控并用客户留存验证增长质量");
    const contribution = state.drill?.entity_type === "渠道" && state.drill.entity_id === state.selectedChannel ? D.channel_alert_flows[state.drill.alert_id] || [] : [];
    const contributionRanked = [...contribution].sort((a, b) => num(a.net_inflow) - num(b.net_inflow));
    const controls = `<div class="filter-panel compact"><label class="control"><span>重点渠道</span><select data-control="selected-channel">${rows.map((row) => `<option value="${esc(row.channel_code)}"${row.channel_code === state.selectedChannel ? " selected" : ""}>${esc(row.channel_name)} · ${esc(row.channel_code)}</option>`).join("")}</select></label></div>`;
    return `${drillBanner("渠道")}${controls}${metricGrid([
      { label: scoped ? "渠道产品 AUM" : "渠道 AUM", value: money(selected.aum_end), delta: `份额 ${pct(selected.aum_share)}` },
      { label: "当月净申购", value: money(selected.net_inflow, true) }, { label: "近3月净申购", value: money(selected.net_3m, true) },
      { label: scoped ? "户均产品保有" : "户均 AUM", value: money(selected["户均_aum"]) },
      { label: scoped ? "产品持有流失率" : "月流失率", value: pct(selected["月流失率"]) },
      { label: "年化尾随成本粗估", value: money(annualTrail), delta: `费率 ${integer(selected["尾随佣金_bps"])} bps` },
    ])}
    ${contributionRanked.length ? panel("Drill", "预警窗口的产品贡献", "这里真正应用了预警中的渠道与日期筛选，按产品拆解净申购。", `${barChart(contributionRanked, "net_inflow", "product_code", { valueFormat: (v) => money(v, true), label: "预警窗口产品贡献", legend: [{ label: "净流入", color: "#22714f", kind: "bar" }, { label: "净流出", color: "#b42318", kind: "bar" }] })}${insight(`窗口内流出贡献最大的产品是 <strong>${esc(contributionRanked[0].fund_name)}（${esc(contributionRanked[0].product_code)}）</strong>，净申购 ${esc(money(contributionRanked[0].net_inflow, true))}。`, num(contributionRanked[0].net_inflow) < 0 ? "risk" : "normal")}`) : ""}
    ${panel("Portfolio", `${scoped ? `${productMap.get(scope)?.fund_name} · ` : ""}渠道价值地图`, "颜色与形状区分渠道类型；金色描边为当前重点，点大小为渠道保有，虚线仅用于分区导航。", `${channelLegend(rows.map((row) => row.channel_type_cn), true)}${scatterChart(rows, {
      xKey: "net_3m", yKey: "户均_aum", rKey: "aum_end", labelKey: "channel_name", xLabel: "近3月净申购", yLabel: scoped ? "户均产品保有" : "户均AUM",
      xFormat: (v) => shortNumber(v), yFormat: (v) => shortNumber(v), xMid: median(rows.map((r) => num(r.net_3m))), yMid: medAvg,
      selected: (row) => row.channel_code === state.selectedChannel,
      color: (row) => channelStyle(row.channel_type_cn).color,
      shape: (row) => channelStyle(row.channel_type_cn).shape,
      labelAll: true,
      tip: (row) => `${row.channel_name} · ${row.channel_type_cn} · AUM ${money(row.aum_end)} · 近3月 ${money(row.net_3m, true)} · 流失 ${pct(row["月流失率"])}`,
      label: "渠道价值地图：横轴近3月净申购，纵轴户均AUM，点大小为渠道保有，颜色与形状为渠道类型",
    })}`)}
    <div class="content-grid two-col">
      ${panel("Trend", `${selected.channel_name}：AUM与净申购`, "共享月份的上下分面，比双轴叠图更容易判断先后关系。", `<div class="chart-stack">${lineChart(history, [{ key: "aum_end", label: "AUM", color: "#24523f", format: money }], "month", { axisFormat: shortNumber, label: "渠道AUM趋势" })}${barChart(history, "net_inflow", "month", { valueFormat: (v) => money(v, true), trimLabel: 2, label: "渠道净申购趋势", legend: [{ label: "净流入", color: "#22714f", kind: "bar" }, { label: "净流出", color: "#b42318", kind: "bar" }] })}</div>`)}
      ${panel("Mix", scoped ? "产品持有人公司层级" : "渠道客户层级结构", "层级按客户总AUM计算；同一客户可在多个渠道分别计数。", tierStackedBars(mixRows))}
    </div>
    ${insight(`<strong>建议：</strong>${messages.map(esc).join("；")}。`, num(selected["月流失率"]) > medChurn ? "warn" : "normal")}
    <details class="panel details-panel"><summary>查看全渠道明细</summary>${table(rows.sort((a, b) => num(b.aum_end) - num(a.aum_end)), [
      { key: "channel_name", label: "渠道" }, { key: "channel_type_cn", label: "类型", html: (v) => channelBadge(v) }, { key: "aum_share", label: "AUM份额", format: pct },
      { key: "net_inflow", label: "净申购", format: (v) => money(v, true) }, { key: "户均_aum", label: "户均AUM", format: money },
      { key: "月流失率", label: "流失率", format: pct }, { key: "尾随佣金_bps", label: "尾随bps", format: integer },
    ])}</details>
    ${dataNote(scoped ? "产品切片指标直接查询持仓与日度AUM归因；层级仍按客户公司总AUM识别。" : "渠道指标来自 channel_monthly.csv 与持仓快照；预警窗口产品贡献直接查询日度AUM归因。")}`;
  }

  function median(values) {
    const sorted = values.filter(Number.isFinite).sort((a, b) => a - b);
    if (!sorted.length) return 0;
    const mid = Math.floor(sorted.length / 2);
    return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
  }

  function tierStackedBars(rows) {
    if (!rows.length) return empty("暂无客户层级数据。");
    const byChannel = new Map();
    rows.forEach((row) => {
      if (!byChannel.has(row.channel_code)) byChannel.set(row.channel_code, []);
      byChannel.get(row.channel_code).push(row);
    });
    return `<div class="stacked-bars">${[...byChannel.entries()].map(([channel, values]) => {
      const total = values.reduce((sum, row) => sum + num(row.customers), 0);
      const name = D.channels.find((row) => row.channel_code === channel)?.channel_name || channel;
      const segments = D.tier_order.slice(1).map((tier, index) => {
        const count = num(values.find((row) => row.tier === tier)?.customers);
        return `<i style="width:${total ? count / total * 100 : 0}%;background:${COLORS[index % COLORS.length]}" title="${esc(`${D.tier_labels[tier]} · ${integer(count)}人`)}" aria-hidden="true"></i>`;
      }).join("");
      const summary = D.tier_order.slice(1).map((tier) => `${D.tier_labels[tier]}${integer(num(values.find((row) => row.tier === tier)?.customers))}人`).join("，");
      return `<div class="stacked-row" role="img" aria-label="${esc(`${name}：${summary}`)}"><span>${esc(name)}</span><div>${segments}</div><strong>${integer(total)}</strong></div>`;
    }).join("")}</div>${chartLegend(D.tier_order.slice(1).map((tier, index) => ({ label: D.tier_labels[tier], color: COLORS[index % COLORS.length], kind: "swatch" })), "客户层级图例")}`;
  }

  function maskCustomer(value) {
    const text = String(value || "");
    return text.length <= 4 ? "***" : `${text.slice(0, 2)}***${text.slice(-2)}`;
  }

  function migrationGrid(month) {
    const rows = D.migration.filter((row) => row.month === month);
    return D.tier_order.flatMap((prev) => D.tier_order.map((curr) => rows.find((row) => row.prev_tier === prev && row.curr_tier === curr) || {
      month, prev_tier: prev, curr_tier: curr, customer_cnt: 0, net_aum_change: 0,
    }));
  }

  function migrationHeatmap(rows) {
    const metricKey = state.migrationMetric === "人数" ? "customer_cnt" : "net_aum_change";
    const max = Math.max(...rows.map((row) => Math.abs(num(row[metricKey]))), 1);
    const cells = [];
    cells.push('<span class="heatmap-corner">上月 \ 本月</span>');
    D.tier_order.forEach((tier) => cells.push(`<span class="heatmap-axis top">${esc(tier)}</span>`));
    D.tier_order.forEach((prev) => {
      cells.push(`<span class="heatmap-axis side">${esc(prev)}</span>`);
      D.tier_order.forEach((curr) => {
        const row = rows.find((item) => item.prev_tier === prev && item.curr_tier === curr);
        const value = num(row[metricKey]);
        const strength = Math.min(1, Math.abs(value) / max);
        let background;
        if (state.migrationMetric === "净AUM" && value < 0) background = `rgba(180,35,24,${0.1 + strength * 0.78})`;
        else background = `rgba(36,82,63,${0.08 + strength * 0.82})`;
        const selected = state.migrationPrev === prev && state.migrationCurr === curr;
        cells.push(`<button type="button" class="heatmap-cell${selected ? " selected" : ""}" data-action="migration-cell" data-prev="${esc(prev)}" data-curr="${esc(curr)}" style="background:${background}" title="${esc(`${prev}→${curr} · ${integer(row.customer_cnt)}人 · 净AUM ${money(row.net_aum_change, true)}`)}"><strong>${integer(row.customer_cnt)}</strong><span>${state.migrationMetric === "净AUM" ? esc(money(row.net_aum_change, true).replace("¥", "")) : "人"}</span></button>`);
      });
    });
    return `<div class="heatmap-scroll" tabindex="0" role="region" aria-label="客户层级迁移矩阵，可横向滚动"><div class="heatmap-grid">${cells.join("")}</div></div>`;
  }

  function cohortChart(rows) {
    if (!rows.length) return empty("至少选择一条 cohort。");
    const groups = [...new Set(rows.map((row) => row.cohort))].map((cohort) => ({ cohort, rows: rows.filter((row) => row.cohort === cohort).sort((a, b) => num(a.months_since) - num(b.months_since)) }));
    const compact = isCompactViewport();
    const W = compact ? 420 : 820, H = compact ? 280 : 330, L = compact ? 46 : 56, R = compact ? 12 : 20, T = 22, B = compact ? 42 : 48, pw = W - L - R, ph = H - T - B;
    const xmax = Math.max(...rows.map((row) => num(row.months_since)), 1);
    const x = (v) => L + v / xmax * pw, y = (v) => T + (1 - v) * ph;
    let out = "";
    for (let i = 0; i <= 4; i += 1) {
      const v = i / 4;
      out += `<line class="chart-grid" x1="${L}" y1="${y(v)}" x2="${W - R}" y2="${y(v)}"/><text class="chart-axis" x="${L - 8}" y="${y(v) + 4}" text-anchor="end">${pct(v, 0)}</text>`;
    }
    for (let i = 0; i <= xmax; i += Math.max(1, Math.ceil(xmax / (compact ? 4 : 6)))) out += `<text class="chart-axis" x="${x(i)}" y="${H - 16}" text-anchor="middle">M${i}</text>`;
    groups.forEach((group, index) => {
      const color = COLORS[index % COLORS.length];
      out += `<polyline class="chart-line" points="${group.rows.map((row) => `${x(num(row.months_since))},${y(num(row.retention_rate))}`).join(" ")}" fill="none" stroke="${color}"/>`;
      group.rows.forEach((row) => { out += `<circle class="chart-point" cx="${x(num(row.months_since))}" cy="${y(num(row.retention_rate))}" r="3" fill="${color}"><title>${esc(`${cohortLabel(group.cohort)} · M${row.months_since} · ${pct(row.retention_rate)}`)}</title></circle>`; });
    });
    return svgFrame(W, H, out, "首购 cohort 持有留存") + chartLegend(groups.map((group, index) => ({ label: cohortLabel(group.cohort), color: COLORS[index % COLORS.length], kind: "line" })), "首购月份与渠道图例");
  }

  function precursorChart(rows) {
    if (!rows.length) return empty("暂无该客户的历史事件。");
    const sorted = [...rows].sort((a, b) => String(a.date).localeCompare(String(b.date)));
    const dates = [...new Set(sorted.map((row) => row.date))];
    const compact = isCompactViewport();
    const W = compact ? 420 : 820, H = compact ? 350 : 410, L = compact ? 46 : 58, R = compact ? 12 : 18, T = 18, B = compact ? 36 : 44, pw = W - L - R;
    const x = (date) => L + (dates.length === 1 ? pw / 2 : dates.indexOf(date) * pw / (dates.length - 1));
    const tracks = compact ? [
      { type: "AUM", top: 18, bottom: 118 },
      { type: "交易", top: 140, bottom: 238 },
      { type: "APP", top: 266, bottom: 312 },
    ] : [
      { type: "AUM", top: 20, bottom: 145 },
      { type: "交易", top: 170, bottom: 285 },
      { type: "APP", top: 315, bottom: 370 },
    ];
    let out = tracks.map((track) => `<text class="chart-axis-title" x="${L}" y="${track.top + 13}">${track.type}</text><line class="chart-grid" x1="${L}" y1="${track.bottom}" x2="${W - R}" y2="${track.bottom}"/>`).join("");
    const aumMax = Math.max(...sorted.map((row) => num(row.aum_after)), 1);
    const aumPoints = sorted.map((row) => `${x(row.date)},${tracks[0].bottom - num(row.aum_after) / aumMax * 95}`).join(" ");
    out += `<polyline class="chart-line" points="${aumPoints}" fill="none" stroke="#24523f"/>`;
    const amountMax = Math.max(...sorted.map((row) => num(row.amount)), 1);
    sorted.forEach((row) => {
      if (row.event_type === "APP事件") {
        out += `<line x1="${x(row.date)}" y1="${tracks[2].bottom}" x2="${x(row.date)}" y2="${tracks[2].bottom - 20}" stroke="#6952a8" stroke-width="2"><title>${esc(`${row.date} · ${row.event_detail}`)}</title></line>`;
      } else {
        const height = 6 + num(row.amount) / amountMax * 76;
        const color = row.event_type === "赎回" ? "#b42318" : "#22714f";
        out += `<rect x="${x(row.date) - 3}" y="${tracks[1].bottom - height}" width="6" height="${height}" fill="${color}"><title>${esc(`${row.date} · ${row.event_type} · ${row.event_detail} · ${money(row.amount)}`)}</title></rect>`;
      }
    });
    const labelStep = Math.max(1, Math.ceil(dates.length / (compact ? 4 : 7)));
    dates.forEach((date, index) => { if (index % labelStep === 0 || index === dates.length - 1) out += `<text class="chart-axis" x="${x(date)}" y="${H - 14}" text-anchor="middle">${esc(date.slice(5))}</text>`; });
    return svgFrame(W, H, out, "流失前兆三轨回放") + chartLegend([
      { label: "AUM", color: "#24523f", kind: "line" }, { label: "申购", color: "#22714f", kind: "bar" },
      { label: "赎回", color: "#b42318", kind: "bar" }, { label: "APP事件", color: "#6952a8", kind: "line" },
    ], "客户行为轨道图例");
  }

  function renderCustomers() {
    const tabBar = tabs(state.customerTab, [{ id: "migration", label: "客户迁移与名单" }, { id: "retention", label: "Cohort 与流失前兆" }], "customer-tab");
    return `${drillBanner("客户群")}${tabBar}${state.customerTab === "migration" ? renderMigration() : renderRetention()}
      ${dataNote("迁移来自相邻月末公司总AUM快照，因此不套用产品筛选。客户、cohort与前兆时间线均为模拟数据；静态资源中的客户ID也是模拟编号。")}`;
  }

  function renderMigration() {
    if (state.drill?.entity_type === "客户群") {
      const drillMonth = monthOf(state.drill.end);
      if (migrationMonths.includes(drillMonth)) state.migrationMonth = drillMonth;
    }
    if (!migrationMonths.includes(state.migrationMonth)) state.migrationMonth = migrationMonths[migrationMonths.length - 1];
    const grid = migrationGrid(state.migrationMonth);
    const rank = Object.fromEntries(D.tier_order.map((tier, index) => [tier, index]));
    const upgraded = grid.filter((row) => rank[row.curr_tier] > rank[row.prev_tier]);
    const downgraded = grid.filter((row) => rank[row.curr_tier] < rank[row.prev_tier]);
    const upgrades = upgraded.reduce((sum, row) => sum + num(row.customer_cnt), 0), downgrades = downgraded.reduce((sum, row) => sum + num(row.customer_cnt), 0);
    const upgradeAum = upgraded.reduce((sum, row) => sum + num(row.net_aum_change), 0), downgradeAum = downgraded.reduce((sum, row) => sum + num(row.net_aum_change), 0);
    const dormant = D.dormant[state.migrationMonth] || { customers: 0, aum: 0 };
    const cell = grid.find((row) => row.prev_tier === state.migrationPrev && row.curr_tier === state.migrationCurr) || grid[0];
    const details = D.migration_detail.filter((row) => row.month === state.migrationMonth && row.prev_tier === state.migrationPrev && row.curr_tier === state.migrationCurr).sort((a, b) => num(a.aum_change) - num(b.aum_change));
    const redemptions = (D.migration_redemptions || []).filter((row) => row.month === state.migrationMonth && row.prev_tier === state.migrationPrev && row.curr_tier === state.migrationCurr).sort((a, b) => num(b.customers) - num(a.customers) || num(b.redeem_amount) - num(a.redeem_amount));
    const fallbackProducts = [...details.reduce((map, row) => {
      const current = map.get(row.main_fund_code) || { product_code: row.main_fund_code, customers: 0, redeem_amount: 0 };
      current.customers += 1; current.redeem_amount += Math.max(0, -num(row.aum_change)); map.set(row.main_fund_code, current); return map;
    }, new Map()).values()].sort((a, b) => b.customers - a.customers);
    const productBreakdown = redemptions.length ? redemptions : fallbackProducts;
    const top = productBreakdown[0];
    const controls = `<div class="filter-panel compact">
      <label class="control"><span>迁移月份</span><select data-control="migration-month">${migrationMonths.map((month) => `<option${month === state.migrationMonth ? " selected" : ""}>${esc(month)}</option>`).join("")}</select></label>
      <div class="control"><span>热力颜色</span>${segmented(state.migrationMetric, [{ id: "人数", label: "人数" }, { id: "净AUM", label: "净AUM" }], "migration-metric")}</div>
    </div>`;
    const drillControls = `<div class="filter-panel compact">
      <label class="control"><span>上月层级</span><select data-control="migration-prev">${D.tier_order.map((tier) => `<option value="${esc(tier)}"${tier === state.migrationPrev ? " selected" : ""}>${esc(D.tier_labels[tier])}</option>`).join("")}</select></label>
      <label class="control"><span>本月层级</span><select data-control="migration-curr">${D.tier_order.map((tier) => `<option value="${esc(tier)}"${tier === state.migrationCurr ? " selected" : ""}>${esc(D.tier_labels[tier])}</option>`).join("")}</select></label>
      <label class="toggle-control"><input type="checkbox" data-control="full-customer-id"${state.showFullCustomerId ? " checked" : ""}><span></span>显示完整模拟ID</label>
    </div>`;
    const detailTable = details.length ? table(details, [
      { key: "customer_id", label: "客户ID", format: (v) => state.showFullCustomerId ? v : maskCustomer(v) }, { key: "channel", label: "主渠道" },
      { key: "prev_tier", label: "上月层" }, { key: "curr_tier", label: "本月层" }, { key: "aum_change", label: "AUM变化", format: (v) => money(v, true) },
      { key: "main_fund_code", label: "主要交易产品" },
    ]) : empty("该迁移格没有跨层客户明细。");
    return `${controls}${metricGrid([
      { label: "跨层升级客户", value: `${integer(upgrades)} 人`, delta: money(upgradeAum, true) },
      { label: "跨层降级客户", value: `${integer(downgrades)} 人`, delta: money(downgradeAum, true) },
      { label: "沉睡标签客户", value: `${integer(dormant.customers)} 人`, delta: `月末保有 ${money(dormant.aum)}` },
    ])}
    ${panel("Movement", "相邻月末客户层级迁移", "格内文字始终是人数；颜色可切换为人数或净AUM。点击格子可直接下钻。", migrationHeatmap(grid))}
    ${panel("Drill", "选择格子查看客户", "默认落在净AUM下降最大的跨层格；完整ID仅指模拟编号。", `${drillControls}<p class="selection-summary"><strong>${esc(state.migrationMonth)} · ${esc(state.migrationPrev)}→${esc(state.migrationCurr)}</strong>：${integer(cell.customer_cnt)} 人，净AUM ${esc(money(cell.net_aum_change, true))}</p>${detailTable}
      ${top ? `${insight(`这批客户在迁移窗口内赎回人数最多的产品是 <strong>${esc(productMap.get(top.product_code)?.fund_name || top.fund_name || top.product_code)}（${esc(top.product_code)}）</strong>：${integer(top.customers)} 人，赎回 ${esc(money(top.redeem_amount))}。`, num(cell.net_aum_change) < 0 ? "risk" : "normal")}<details class="inline-details"><summary>查看该迁移格的赎回产品分布</summary>${table(productBreakdown, [
        { key: "product_code", label: "产品代码" }, { key: "fund_name", label: "产品名称", value: (r) => r.fund_name || productMap.get(r.product_code)?.fund_name || "—" }, { key: "customers", label: "赎回客户", format: integer }, { key: "redeem_amount", label: "赎回金额", format: money },
      ])}</details>` : ""}
      ${state.migrationMonth === "2026-07" && state.migrationPrev === "T3" && state.migrationCurr === "T1" ? insight("<strong>重点降级：</strong>41名客户由T3降至T1，净AUM约−391万；其中36人赎回017560.OF。", "risk") : ""}`)} `;
  }

  function renderRetention() {
    const selectedRows = D.cohort.filter((row) => state.cohortPicks.slice(0, 4).includes(row.cohort));
    const timeline = D.precursor.filter((row) => row.customer_id === state.precursorCustomer);
    const churn = [...D.churn_list].sort((a, b) => num(b["churn前AUM峰值"]) - num(a["churn前AUM峰值"]));
    return `${state.cohortPicks.length > 4 ? `<div class="warning-box">为保证曲线可读，仅展示前4条。</div>` : ""}
    ${panel("Retention", "首购 cohort 持有留存", "留存定义：目标月末客户总AUM>1,000元；不是复购次数。图例同时标明首购月份、渠道名称与渠道类型。", `<label class="control multiselect-control"><span>对比 cohort（最多4条）</span><select multiple size="6" data-control="cohort-picks">${cohortOptions.map((option) => `<option value="${esc(option)}"${state.cohortPicks.includes(option) ? " selected" : ""}>${esc(cohortLabel(option))}</option>`).join("")}</select></label>${cohortChart(selectedRows)}`)}
    ${panel("Precursor", "流失前兆三轨回放", "AUM、申赎、APP行为分轨共享时间轴；赎回使用红色。", `<label class="control inline-control"><span>历史案例客户</span><select data-control="precursor-customer">${precursorCustomers.map((id) => `<option value="${esc(id)}"${id === state.precursorCustomer ? " selected" : ""}>${esc(maskCustomer(id))}</option>`).join("")}</select></label>${precursorChart(timeline)}${state.precursorCustomer === "U102733" ? insight("5月活跃度归零，6月多次浏览赎回页，7月集中赎回。数据没有 CANCEL_DCA 原生事件，因此不展示不存在的前兆。", "warn") : ""}`)}
    ${panel("Evidence", "历史已流失样本", "这份名单用于规则复盘，不是仍可挽留的当前机会名单。", table(churn, [
      { key: "customer_id", label: "客户ID", format: maskCustomer }, { key: "channel", label: "渠道" }, { key: "churn前AUM峰值", label: "流失前AUM峰值", format: money },
      { key: "清零日期", label: "清零日期" }, { key: "最后赎回基金", label: "最后赎回基金" },
    ]))}`;
  }

  function shiftMonth(month, delta) {
    const [year, mon] = month.split("-").map(Number);
    const date = new Date(Date.UTC(year, mon - 1 + delta, 1));
    return `${date.getUTCFullYear()}-${String(date.getUTCMonth() + 1).padStart(2, "0")}`;
  }

  function shiftDay(date, delta) {
    const value = new Date(`${date}T00:00:00Z`);
    value.setUTCDate(value.getUTCDate() + delta);
    return value.toISOString().slice(0, 10);
  }

  function monthReturn(navRows, month) {
    const monthly = new Map();
    navRows.forEach((row) => {
      const key = monthOf(row.date);
      const current = monthly.get(key);
      if (!current || String(row.date) > String(current.date)) monthly.set(key, row);
    });
    const current = monthly.get(month), previous = monthly.get(shiftMonth(month, -1));
    if (!current || !previous || !num(previous.unit_nav)) return null;
    return num(current.unit_nav) / num(previous.unit_nav) - 1;
  }

  function navFlowChart(navRows, flowRows) {
    return `<div class="chart-stack">${lineChart(navRows, [{ key: "unit_nav", label: "单位净值", color: "#24523f", format: (v) => v.toFixed(4) }], "date", { axisFormat: (v) => v.toFixed(2), label: "单位净值趋势" })}${barChart(flowRows, "net_flow", "week", { valueFormat: (v) => money(v, true), trimLabel: 5, label: "周度净申购" })}</div>`;
  }

  function renderProducts() {
    if (state.product === "ALL" || !productMap.has(state.product)) state.product = defaultProduct;
    const selected = state.product, meta = productMap.get(selected), values = kpi(selected);
    const health = D.health_by_month[state.month] || [];
    const h = health.find((row) => (row.product_code || row.fund_code) === selected);
    const startMonth = shiftMonth(state.month, -13);
    let navRows = D.nav.filter((row) => row.fund_code === selected && monthOf(row.date) >= startMonth && monthOf(row.date) <= state.month);
    let flowRows = D.weekly_flow.filter((row) => row.fund_code === selected && monthOf(row.week) >= startMonth && monthOf(row.week) <= state.month);
    const ret = monthReturn(D.nav.filter((row) => row.fund_code === selected), state.month);
    let drillCaption = "";
    if (state.drill?.entity_type === "产品" && state.drill.entity_id === selected) {
      const start = shiftDay(state.drill.start, -45), end = shiftDay(state.drill.end, 20);
      navRows = D.nav.filter((row) => row.fund_code === selected && row.date >= start && row.date <= end);
      flowRows = D.weekly_flow.filter((row) => row.fund_code === selected && row.week >= start && row.week <= end);
      drillCaption = `<div class="drill-window">图形窗口已收窄到 ${esc(start)} 至 ${esc(end)}。</div>`;
    }
    const tabBar = tabs(state.productTab, [{ id: "operations", label: "产品经营复盘" }, { id: "benchmark", label: "精选竞品与外部锚点" }], "product-tab");
    return `${drillBanner("产品")}${tabBar}${state.productTab === "operations" ? `
      ${metricGrid([
        { label: "分析月收益", value: ret == null ? "—" : pct(ret, 1, true) }, { label: "风险等级", value: meta.risk_level, delta: meta.fund_type_l2 },
        { label: "管理费率", value: `${num(meta.mgmt_fee_rate).toFixed(2)}%` },
        { label: "近2季规模增长", value: h ? pct(h.growth_2q, 1, true) : "—" },
        { label: "产品首次买入客90日留存", value: h ? pct(h.retention_90d) : "—" },
        { label: "累计申购额排名", value: h ? `第 ${integer(h.sales_rank)} 名` : "—" },
      ])}
      ${panel("Behavior", "净值与周度净申购", "上下分面共享时间轴；净申购为负表示赎回超过申购。", `${drillCaption}${navFlowChart(navRows, flowRows)}${selected === "017560.OF" && state.month === "2026-07" ? insight("017560 在7月出现异常赎回；41名 T3→T1 客户中有36人赎回该产品，优先建立客户挽留名单。", "risk") : ""}${selected === "588290.SH" && state.month === "2026-07" ? insight("588290 仅在直销渠道持有，不与 ANT 或银行渠道客户事件合并归因。", "warn") : ""}`)}
      ${panel("Quality", "产品健康度", "X=近2季规模增长，Y=产品首次买入客90日留存；参考线为样本中位数。", scatterChart(health, {
        xKey: "growth_2q", yKey: "retention_90d", rKey: "purchase_amount", labelKey: "fund_name", xLabel: "近2季规模增长", yLabel: "90日持有留存",
        xFormat: (v) => pct(v, 0), yFormat: (v) => pct(v, 0), xMid: median(health.map((r) => num(r.growth_2q))), yMid: median(health.map((r) => num(r.retention_90d))),
        selected: (row) => (row.product_code || row.fund_code) === selected, color: (row) => row.is_own_product ? "#24523f" : "#a5822f",
        tip: (row) => `${row.fund_name} · 增长 ${pct(row.growth_2q)} · 留存 ${pct(row.retention_90d)} · 申购排名 ${row.sales_rank}`,
      }))}` : renderProductBenchmarks(selected)}
      ${dataNote(`净值来源：${esc(navRows[0]?.data_source || "按产品数据源标记")}。产品净值、季度规模和AMAC排名含真实来源；客户交易、持有与留存为模拟数据。竞品仅为精选样本，不能解释为行业分位或市场份额。`)}`;
  }

  function renderProductBenchmarks(selected) {
    const allRisk = D.risk_by_month[state.month] || [];
    const risk = state.includeSimulated ? allRisk : allRisk.filter((row) => !row.is_simulated);
    const scaleMap = new Map();
    D.scale_sample.forEach((row) => {
      if (!scaleMap.has(row.quarter_id)) scaleMap.set(row.quarter_id, { quarter: row.quarter_id, own: 0, competitor: 0 });
      scaleMap.get(row.quarter_id)[row.is_own_product ? "own" : "competitor"] = num(row.aum_yi);
    });
    const scale = [...scaleMap.values()].sort((a, b) => a.quarter.localeCompare(b.quarter));
    const periods = [...new Set(D.amac.map((row) => row.period_id))].sort().reverse();
    if (!periods.includes(state.amacPeriod)) state.amacPeriod = periods[0];
    const amac = D.amac.filter((row) => row.period_id === state.amacPeriod && row.channel_code);
    const toggle = `<label class="toggle-control benchmark-toggle"><input type="checkbox" data-control="include-simulated"${state.includeSimulated ? " checked" : ""}><span></span>包含3只模拟货基净值</label>`;
    return `${panel("Risk / return", "近1年风险收益样本", "最大回撤按每日净值相对历史滚动峰值计算；货基模拟净值默认排除。", `${toggle}${scatterChart(risk, {
      xKey: "max_drawdown", yKey: "period_return", labelKey: "fund_name", xLabel: "最大回撤", yLabel: "区间收益",
      xFormat: (v) => pct(v, 0), yFormat: (v) => pct(v, 0), selected: (row) => row.fund_code === selected,
      color: (row) => row.is_own_product ? "#24523f" : "#a5822f", tip: (row) => `${row.fund_name} · 收益 ${pct(row.period_return)} · 最大回撤 ${pct(row.max_drawdown)}`,
    })}`)}
    <div class="content-grid two-col">
      ${panel("Sample", "精选产品样本规模", "这是25只项目样本的绝对规模，不是行业规模、市场份额或行业β。", lineChart(scale, [
        { key: "own", label: "自有产品", color: "#24523f", format: (v) => `${v.toFixed(1)}亿` }, { key: "competitor", label: "竞品", color: "#a5822f", format: (v) => `${v.toFixed(1)}亿` },
      ], "quarter", { axisFormat: (v) => `${v.toFixed(0)}亿`, label: "样本季度规模" }))}
      ${panel("External anchor", "AMAC 销售机构排名", "外部排名只到2025H2，与内部经营数据截止日不同。", `<label class="control inline-control"><span>披露期</span><select data-control="amac-period">${periods.map((period) => `<option${period === state.amacPeriod ? " selected" : ""}>${esc(period)}</option>`).join("")}</select></label>${table(amac, [
        { key: "rank", label: "排名", format: integer }, { key: "org_name", label: "机构" }, { key: "org_type", label: "类型" },
        { key: "channel_code", label: "内部映射" }, { key: "non_money_aum_yi", label: "非货保有（亿）", format: integer }, { key: "equity_aum_yi", label: "权益保有（亿）", format: integer },
      ])}`)}
    </div>`;
  }

  function campaignDumbbell(row) {
    const values = [
      { label: "自然基线", value: num(row.baseline_conv), color: "#6f7268" },
      { label: "原始转化", value: num(row.observed_conv), color: "#24523f" },
      { label: "行情中性化", value: num(row.neutralized_conv), color: "#a5822f" },
    ];
    const compact = isCompactViewport();
    const W = compact ? 420 : 820, H = compact ? 170 : 180, L = compact ? 76 : 130, R = compact ? 14 : 28, T = 24, B = 40, pw = W - L - R;
    const max = Math.max(...values.map((item) => item.value), 0.01) * 1.14;
    const x = (v) => L + v / max * pw;
    let out = `<line class="chart-connector solid" x1="${x(Math.min(...values.map((i) => i.value)))}" y1="80" x2="${x(Math.max(...values.map((i) => i.value)))}" y2="80"/>`;
    values.forEach((item, index) => {
      const cy = 64 + index * 16;
      out += `<circle cx="${x(item.value)}" cy="80" r="8" fill="${item.color}"><title>${esc(`${item.label} · ${pct(item.value, 2)}`)}</title></circle><text class="chart-label" x="${x(item.value)}" y="${index === 1 ? 124 : 52}" text-anchor="middle">${esc(`${item.label} ${pct(item.value, 2)}`)}</text>`;
    });
    for (let i = 0; i <= 4; i += 1) {
      const value = max * i / 4;
      out += `<text class="chart-axis" x="${x(value)}" y="${H - 14}" text-anchor="middle">${pct(value, 1)}</text>`;
    }
    return svgFrame(W, H, out, "活动转化口径对照");
  }

  function renderMarketing() {
    let campaigns = state.marketingProduct === "ALL" ? D.campaigns : D.campaigns.filter((row) => row.promote_fund_code === state.marketingProduct);
    if (!campaigns.length) campaigns = D.campaigns;
    if (!campaigns.some((row) => row.campaign_id === state.selectedCampaign)) state.selectedCampaign = campaigns.some((row) => row.campaign_id === "CP_C") ? "CP_C" : campaigns[0].campaign_id;
    const selected = campaigns.find((row) => row.campaign_id === state.selectedCampaign) || campaigns[0];
    const valueKey = state.campaignMode === "原始" ? "observed_conv" : "neutralized_conv";
    const ranking = [...campaigns].sort((a, b) => num(b[valueKey]) - num(a[valueKey]));
    const ratios = [
      { stage: "曝光→点击", rate: num(selected["曝光"]) ? num(selected["点击"]) / num(selected["曝光"]) : 0 },
      { stage: "点击→产品页", rate: num(selected["点击"]) ? num(selected["产品页"]) / num(selected["点击"]) : 0 },
      { stage: "产品页→开户", rate: num(selected["产品页"]) ? num(selected["开户"]) / num(selected["产品页"]) : 0 },
      { stage: "开户→风测", rate: num(selected["开户"]) ? num(selected["风测"]) / num(selected["开户"]) : 0 },
    ];
    const delta = num(selected.neutralized_conv) - num(selected.observed_conv);
    const explanation = delta < -0.001 ? "剔除行情系数后转化下降，活动原始表现可能吃到了市场顺风。" : delta > 0.001 ? "剔除行情系数后转化上升，活动在逆风环境下的相对质量更好。" : "行情校准前后接近，市场因子对该活动的方向影响有限。";
    const productOptions = `<option value="ALL">全部推广产品</option>${campaignProducts.map((code) => `<option value="${esc(code)}"${state.marketingProduct === code ? " selected" : ""}>${esc(productLabel(code))}</option>`).join("")}`;
    const filters = `<div class="filter-panel compact"><label class="control"><span>推广产品</span><select data-control="marketing-product">${productOptions}</select></label><div class="control"><span>排行榜口径</span>${segmented(state.campaignMode, [{ id: "原始", label: "原始" }, { id: "行情中性化", label: "行情中性化" }], "campaign-mode")}</div></div>`;
    return `${filters}<div class="context-inline">${chip(state.marketingProduct === "ALL" ? "全部推广产品" : productLabel(state.marketingProduct))}${chip(`活动 ${campaigns.length} 个`)}${chip(`${selected.channel_code} · ${campaignChannelType(selected)}`)}${selected.is_subsidy ? chip("补贴活动", "warning") : ""}</div>
    ${panel("Compare", "活动转化比较", "条形颜色区分活动渠道类型；补贴活动在名称后单独标注。切换口径后观察排名变化，并用自然基线判断是否真正超预期。", `${channelLegend(ranking.map(campaignChannelType))}${horizontalBars(ranking.map((row) => ({ ...row, channel_type_cn: campaignChannelType(row), display: `${row.campaign_name} · ${row.campaign_id}${row.is_subsidy ? " · 补贴" : ""}` })), valueKey, "display", { format: (v) => pct(v, 2), color: (row) => channelStyle(row.channel_type_cn).color })}`)}
    <div class="filter-panel compact"><label class="control"><span>复盘活动</span><select data-control="selected-campaign">${campaigns.map((row) => `<option value="${esc(row.campaign_id)}"${row.campaign_id === selected.campaign_id ? " selected" : ""}>${esc(row.campaign_name)} · ${esc(row.campaign_id)}</option>`).join("")}</select></label></div>
    ${metricGrid([
      { label: "原始转化", value: pct(selected.observed_conv, 2) }, { label: "行情中性化", value: pct(selected.neutralized_conv, 2), delta: `较原始 ${pct(delta, 2, true)}` },
      { label: "自然基线", value: pct(selected.baseline_conv, 2) }, { label: "90日持有留存", value: pct(selected.retention_90d) },
      { label: "活动窗口申购", value: money(selected["申购金额"]) },
      { label: "买入后30天赎回", value: money(selected["30天赎回金额"]), delta: num(selected["申购金额"]) ? `占窗口申购 ${pct(num(selected["30天赎回金额"]) / num(selected["申购金额"]))}` : "" },
    ])}
    ${panel("Calibration", "基线、原始与中性化转化", "三种口径并列展示，避免把校准结果误解为因果增量。", campaignDumbbell(selected))}
    <div class="content-grid two-col">
      ${panel("Journey", "获客链路阶段量比", "这些是聚合量之间的比率，不代表同一批用户逐级转化。", horizontalBars(ratios, "rate", "stage", { format: (v) => pct(v, 1), color: (_, i) => COLORS[i] }))}
      ${panel("Outcome", "交易与复购计数", "源字段 repurchase_cnt 应称复购，不应改名成30天留存。", `<div class="mini-metrics"><article><span>申购计数（聚合）</span><strong>${integer(selected["申购"])}</strong></article><article><span>复购计数（聚合）</span><strong>${integer(selected["30天留存"])}</strong></article></div>${insight(`<strong>校准解释：</strong>${esc(explanation)}`, "normal")}`)}
    </div>
    ${selected.campaign_id === "CP_C" ? insight("<strong>管理提示：</strong>CP_C带来约4,399万窗口申购，但随后相关产品净流出约1,329万；补贴活动应以净保有和90日留存考核。", "warn") : ""}
    <details class="panel details-panel"><summary>为什么这里不展示“真实ROI”</summary><p class="detail-copy">现有导出ROI使用总申购×年化管理费率，没有使用相对基线的增量申购、实际持有天数、完整成本和对照组，因此最多是情景估计。</p>${table(campaigns, [
      { key: "campaign_id", label: "活动" }, { key: "campaign_name", label: "名称" }, { key: "channel_code", label: "渠道" }, { key: "observed_conv", label: "原始转化", format: (v) => pct(v, 2) },
      { key: "neutralized_conv", label: "中性化", format: (v) => pct(v, 2) }, { key: "baseline_conv", label: "自然基线", format: (v) => pct(v, 2) },
      { key: "retention_90d", label: "90日留存", format: pct }, { key: "申购金额", label: "申购金额", format: money },
      { key: "30天赎回金额", label: "修正后30天赎回", format: money }, { key: "30天赎回金额_原导出", label: "原导出", format: money },
    ])}</details>
    ${dataNote("阶段指标为聚合量比，不代表同一用户漏斗；复购计数不是30天留存。转化校准为market_factor曝光加权情景调整，不构成因果归因或真实ROI。")}`;
  }

  function buildReport() {
    const scope = currentScope(), scoped = scope !== "ALL", product = scoped ? productMap.get(scope) : null, values = kpi(scope);
    const channels = channelRows(scope), worstChannel = [...channels].sort((a, b) => num(a.net_inflow) - num(b.net_inflow))[0];
    let alerts = allAlerts().filter((row) => monthOf(row.window_end) === state.month);
    if (scoped) alerts = alerts.filter((row) => row.entity_type === "产品" && row.entity_id === scope);
    const red = alerts.filter((row) => row.level === "红");
    const redEntities = new Set(red.map((row) => `${row.entity_type}|${row.entity_id}`)).size;
    let migrationSentence = "产品月报不对公司级迁移结果做事后过滤；请在客户页按公司总AUM层级分析。";
    if (!scoped) {
      const cross = D.migration.filter((row) => row.month === state.month && row.prev_tier !== row.curr_tier).sort((a, b) => num(a.net_aum_change) - num(b.net_aum_change));
      migrationSentence = cross.length ? `净AUM下降最大的跨层格为 ${cross[0].prev_tier}→${cross[0].curr_tier}：${integer(cross[0].customer_cnt)}人，${money(cross[0].net_aum_change, true)}。` : "该月没有可用的相邻快照迁移结果。";
    }
    const totalChange = num(values.net) + num(values.nav);
    const attribution = totalChange < 0 && values.net < 0 && values.nav < 0 ? `本月下降约 ${pct(Math.abs(values.net) / Math.abs(totalChange), 0)} 来自经营净流出、${pct(Math.abs(values.nav) / Math.abs(totalChange), 0)} 来自净值影响。` : "经营净申购与净值影响方向不同或均为正，应分别解读，不做单一归因。";
    const actions = [];
    if (worstChannel && num(worstChannel.net_inflow) < 0) actions.push(`复盘${worstChannel.channel_name}净流出：先按产品贡献定位，再按客户层级生成名单。`);
    const productAlert = red.filter((row) => row.entity_type === "产品").sort((a, b) => num(b.metric_value) - num(a.metric_value))[0];
    if (productAlert) actions.push(`对${productAlert.entity_name}异常赎回建立对象级事件，避免逐日命中生成重复工单。`);
    if (!num(values.new_customers)) actions.push("新增首购为0：先核查数据是否完整，再决定是否启动拉新专项。");
    if (!actions.length) actions.push("维持常规监控，并用次月留存与迁移验证本月增长质量。");
    const title = scoped ? `产品经营月报 · ${product.fund_name}（${scope}）· ${state.month}` : `基金零售经营月报 · ${state.month}`;
    const channelLine = worstChannel ? `当月净申购最低渠道为 **${worstChannel.channel_name}**：${money(worstChannel.net_inflow, true)}；月流失率 ${pct(worstChannel["月流失率"])}。` : "暂无渠道结果。";
    const markdown = `# ${title}\n\n> 客户经营快照日：${values.snapshot}。${scoped ? `当前仅统计产品 ${product.fund_name}（${scope}）的持仓、申赎和净值归因。` : "当前统计全部产品。"}客户、交易与行为数据为模拟；预警日志为精选演示案例。\n\n## 1. 总量与归因\n\n- ${scoped ? "产品" : "月末"} AUM：**${money(values.aum)}**，环比 **${pct(values.aum_mom, 1, true)}**。\n- 申购 **${money(values.subscribe)}**，赎回 **${money(values.redeem)}**，经营净申购 **${money(values.net, true)}**。\n- 净值影响 **${money(values.nav, true)}**。${attribution}\n- 自有产品年化管理费粗估 **${money(values.fee_annual)}**，不等同财务确认收入。\n\n## 2. 客户\n\n- 月末${scoped ? "产品持有人" : "持仓客户"} **${integer(values.holding_customers)}人**，${scoped ? "产品首购客户" : "新增首购客户"} **${integer(values.new_customers)}人**。\n- 当前总AUM≥50万元的${scoped ? "高价值持有人" : "高价值客户"} **${integer(values.high_value_customers)}人**。\n- ${scoped ? `产品持有流失率 ${pct(values.product_churn)}。` : migrationSentence}\n\n## 3. 渠道\n\n- ${channelLine}\n\n## 4. 预警\n\n- 本月红色**命中记录** **${integer(red.length)}条**，涉及 **${integer(redEntities)}个对象**。\n- 命中记录不等同待处理工单；同一对象连续多日命中应先合并为事件。\n\n## 5. 下月动作\n\n${actions.map((text, i) => `${i + 1}. ${text}`).join("\n")}`;
    const facts = [
      { metric: scoped ? "产品AUM" : "月末AUM", value: values.aum, unit: "元", source: "fact_holding_snapshot" },
      { metric: "经营净申购", value: values.net, unit: "元", source: "fact_aum_change_daily" },
      { metric: "净值影响", value: values.nav, unit: "元", source: "fact_aum_change_daily" },
      { metric: scoped ? "产品持有人" : "持仓客户", value: values.holding_customers, unit: "人", source: "fact_holding_snapshot" },
      { metric: scoped ? "产品首购" : "新增首购", value: values.new_customers, unit: "人", source: "fact_fund_transaction" },
      { metric: scoped ? "高价值持有人" : "高价值客户", value: values.high_value_customers, unit: "人", source: "fact_holding_snapshot" },
      ...(scoped ? [{ metric: "产品持有流失率", value: values.product_churn, unit: "比例", source: "fact_holding_snapshot" }] : []),
      { metric: "红色命中记录", value: red.length, unit: "条", source: "data/pbi/alert_log.csv" },
      { metric: "红色涉及对象", value: redEntities, unit: "个", source: "data/pbi/alert_log.csv" },
    ];
    return { title, markdown, facts, values, product, scoped, worstChannel, red, redEntities, migrationSentence, attribution, actions, channelLine };
  }

  function renderReport() {
    const report = buildReport();
    const actions = `<div class="toolbar"><button type="button" class="button ghost" data-action="reload-snapshot">重新载入快照</button><button type="button" class="button primary" data-action="download-report">下载 Markdown 月报</button></div>`;
    const tabBar = tabs(state.reportTab, [{ id: "preview", label: "月报预览" }, { id: "facts", label: "事实表与来源" }], "report-tab");
    const preview = `<article class="report-preview"><header><span>Management Report</span><h2>${esc(report.title)}</h2><p>客户经营快照日：${esc(report.values.snapshot)} · ${report.scoped ? `产品 ${esc(report.product.fund_name)}（${esc(currentScope())}）` : "全部产品"} · 客户经营数据为模拟</p></header>
      <section><h3>01 · 总量与归因</h3><ul><li>${report.scoped ? "产品" : "月末"} AUM <strong>${esc(money(report.values.aum))}</strong>，环比 ${esc(pct(report.values.aum_mom, 1, true))}。</li><li>经营净申购 <strong>${esc(money(report.values.net, true))}</strong>；净值影响 ${esc(money(report.values.nav, true))}。</li><li>${esc(report.attribution)}</li></ul></section>
      <section><h3>02 · 客户</h3><ul><li>${report.scoped ? "产品持有人" : "持仓客户"} ${integer(report.values.holding_customers)} 人；${report.scoped ? "产品首购" : "新增首购"} ${integer(report.values.new_customers)} 人。</li><li>高价值客户 ${integer(report.values.high_value_customers)} 人。</li><li>${esc(report.scoped ? `产品持有流失率 ${pct(report.values.product_churn)}。` : report.migrationSentence)}</li></ul></section>
      <section><h3>03 · 渠道</h3><p>${esc(report.channelLine.replaceAll("**", ""))}</p></section>
      <section><h3>04 · 预警</h3><p>本月红色命中 ${integer(report.red.length)} 条，涉及 ${integer(report.redEntities)} 个对象。命中记录不等同待处理工单。</p></section>
      <section><h3>05 · 下月动作</h3><ol>${report.actions.map((item) => `<li>${esc(item)}</li>`).join("")}</ol></section>
    </article>`;
    const facts = table(report.facts, [
      { key: "metric", label: "指标" }, { key: "value", label: "值", format: (value, row) => row.unit === "元" ? money(value, true) : row.unit === "比例" ? pct(value) : integer(value) },
      { key: "unit", label: "单位" }, { key: "source", label: "来源" },
    ]);
    return `${actions}${tabBar}${state.reportTab === "preview" ? preview : panel("Evidence", "月报事实表", "所有展示值保留来源标识，便于口径审计。", facts)}${dataNote("月报模板不修改源数据。当前项目没有目标表、预算表和正式工单状态库，因此不生成目标完成度、预算差异或真实待处理工单。")}`;
  }

  function renderApp() {
    const config = PAGE_CONFIG[state.page];
    if (config.productOnly && (state.product === "ALL" || !productMap.has(state.product))) state.product = defaultProduct;
    titleEl.textContent = config.title;
    eyebrowEl.textContent = config.eyebrow;
    document.title = `${config.title} — Retail Analytics`;
    document.querySelectorAll(".nav-item[data-page]").forEach((button) => {
      const active = button.dataset.page === state.page;
      button.classList.toggle("active", active);
      button.setAttribute("aria-current", active ? "page" : "false");
    });

    monthSelect.innerHTML = D.months.map((month) => `<option value="${esc(month)}"${month === state.month ? " selected" : ""}>${esc(month)}</option>`).join("");
    monthSelect.value = state.month;
    if (config.productScope) {
      const options = `${config.productOnly ? "" : '<option value="ALL">全部产品</option>'}${D.products.map((product) => `<option value="${esc(product.fund_code)}">${esc(product.fund_name)} · ${esc(product.fund_code)}</option>`).join("")}`;
      productSelect.innerHTML = options;
      productSelect.disabled = false;
      productControl.classList.remove("disabled");
      productSelect.value = currentScope();
    } else {
      productSelect.innerHTML = '<option value="ALL">本页使用对象级筛选</option>';
      productSelect.value = "ALL";
      productSelect.disabled = true;
      productControl.classList.add("disabled");
    }
    const scope = currentScope();
    contextText.textContent = `月份 ${state.month} · ${productLabel(scope)} · ${PAGE_CONFIG[state.page].title}`;
    snapshotBadge.textContent = `数据截至 ${D.meta.latest_snapshot}`;

    const renderers = {
      overview: renderOverview,
      alerts: renderAlerts,
      channels: renderChannels,
      customers: renderCustomers,
      products: renderProducts,
      marketing: renderMarketing,
      report: renderReport,
    };
    try {
      root.innerHTML = renderers[state.page]();
    } catch (error) {
      console.error(error);
      root.innerHTML = `<div class="error-state"><strong>页面渲染失败</strong><p>${esc(error.message || error)}</p><button class="button primary" data-action="reload-snapshot">重新加载</button></div>`;
    }
    closeMobileMenu();
  }

  function navigate(page) {
    if (!validPages.includes(page)) return;
    state.page = page;
    if (page === "products" && state.product === "ALL") state.product = defaultProduct;
    if (location.hash !== `#${page}`) history.pushState(null, "", `#${page}`);
    renderApp();
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function updateAlertDraft(target) {
    const id = target.dataset.alertId, field = target.dataset.alertField;
    if (!id || !field) return;
    const base = savedAlertOverlay[id] || {};
    state.alertDraft[id] = { ...base, ...(state.alertDraft[id] || {}), [field]: target.value };
  }

  function downloadReport() {
    const report = buildReport();
    const blob = new Blob([report.markdown], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    const scope = currentScope();
    anchor.href = url;
    anchor.download = `retail-operations-${state.month}${scope === "ALL" ? "" : `-${scope.replaceAll(".", "-")}`}.md`;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    toast("Markdown 月报已生成");
  }

  function openMobileMenu() {
    document.body.classList.add("menu-open");
    document.getElementById("menu-toggle").setAttribute("aria-expanded", "true");
    const sidebar = document.getElementById("sidebar");
    sidebar?.setAttribute("aria-hidden", "false");
    if (sidebar) sidebar.inert = false;
    setTimeout(() => document.querySelector('.nav-item.active, .nav-item[aria-current="page"]')?.focus?.(), 0);
  }

  function closeMobileMenu(restoreFocus = false) {
    document.body.classList.remove("menu-open");
    document.getElementById("menu-toggle").setAttribute("aria-expanded", "false");
    const width = Number(window.innerWidth);
    const isMobile = Number.isFinite(width) && width <= 820;
    const sidebar = document.getElementById("sidebar");
    sidebar?.setAttribute("aria-hidden", isMobile ? "true" : "false");
    if (sidebar) sidebar.inert = isMobile;
    if (restoreFocus) document.getElementById("menu-toggle")?.focus?.();
  }

  document.addEventListener("click", (event) => {
    const nav = event.target.closest(".nav-item[data-page]");
    if (nav) {
      navigate(nav.dataset.page);
      if (Number(window.innerWidth) <= 820) document.getElementById("menu-toggle")?.focus?.();
      return;
    }
    const actionTarget = event.target.closest("[data-action]");
    if (!actionTarget) return;
    const action = actionTarget.dataset.action, value = actionTarget.dataset.value;
    if (action === "navigate") {
      if (value === "customers" && actionTarget.dataset.view) state.customerTab = actionTarget.dataset.view;
      if (value === "products" && actionTarget.dataset.view) state.productTab = actionTarget.dataset.view;
      navigate(value);
    }
    else if (action === "save-alerts") saveAlertOverlay();
    else if (action === "clear-drill") { state.drill = null; renderApp(); }
    else if (action === "drill-alert") {
      const row = allAlerts().find((item) => item.alert_id === value);
      if (!row || !TARGET_PAGE[row.target_page]) return;
      state.drill = {
        alert_id: row.alert_id, rule_id: row.rule_id, entity_type: row.entity_type,
        entity_id: row.entity_id, entity_name: row.entity_name,
        start: String(row.window_start).slice(0, 10), end: String(row.window_end).slice(0, 10),
      };
      if (row.entity_type === "产品" && productMap.has(row.entity_id)) state.product = row.entity_id;
      if (row.entity_type === "渠道") state.selectedChannel = row.entity_id;
      if (row.entity_type === "客户群" && migrationMonths.includes(monthOf(row.window_end))) state.migrationMonth = monthOf(row.window_end);
      navigate(TARGET_PAGE[row.target_page]);
    } else if (action === "customer-tab") { state.customerTab = value; renderApp(); }
    else if (action === "migration-metric") { state.migrationMetric = value; renderApp(); }
    else if (action === "migration-cell") { state.migrationPrev = actionTarget.dataset.prev; state.migrationCurr = actionTarget.dataset.curr; renderApp(); }
    else if (action === "product-tab") { state.productTab = value; renderApp(); }
    else if (action === "campaign-mode") { state.campaignMode = value; renderApp(); }
    else if (action === "report-tab") { state.reportTab = value; renderApp(); }
    else if (action === "download-report") downloadReport();
    else if (action === "reload-snapshot") location.reload();
  });

  document.addEventListener("input", (event) => {
    if (event.target.matches("[data-alert-id][data-alert-field]")) updateAlertDraft(event.target);
  });

  document.addEventListener("change", (event) => {
    const target = event.target;
    if (target.matches("[data-alert-id][data-alert-field]")) {
      updateAlertDraft(target);
      return;
    }
    if (target.id === "month-select") { state.month = target.value; renderApp(); return; }
    if (target.id === "product-select") { state.product = target.value; renderApp(); return; }
    const control = target.dataset.control;
    if (!control) return;
    if (control === "alert-scope") state.alertScope = target.value;
    else if (control === "alert-level") {
      state.alertLevels = target.checked ? [...new Set([...state.alertLevels, target.value])] : state.alertLevels.filter((level) => level !== target.value);
    } else if (control === "alert-entity") { state.alertEntityType = target.value; state.alertProduct = "ALL"; }
    else if (control === "alert-product") state.alertProduct = target.value;
    else if (control === "selected-alert") state.selectedAlert = target.value;
    else if (control === "selected-channel") state.selectedChannel = target.value;
    else if (control === "migration-month") {
      state.migrationMonth = target.value;
      const worstCell = migrationGrid(state.migrationMonth)
        .filter((row) => row.prev_tier !== row.curr_tier)
        .sort((a, b) => num(a.net_aum_change) - num(b.net_aum_change))[0];
      if (worstCell) { state.migrationPrev = worstCell.prev_tier; state.migrationCurr = worstCell.curr_tier; }
    }
    else if (control === "migration-prev") state.migrationPrev = target.value;
    else if (control === "migration-curr") state.migrationCurr = target.value;
    else if (control === "full-customer-id") state.showFullCustomerId = target.checked;
    else if (control === "cohort-picks") state.cohortPicks = [...target.selectedOptions].map((option) => option.value);
    else if (control === "precursor-customer") state.precursorCustomer = target.value;
    else if (control === "include-simulated") state.includeSimulated = target.checked;
    else if (control === "amac-period") state.amacPeriod = target.value;
    else if (control === "marketing-product") { state.marketingProduct = target.value; state.selectedCampaign = "CP_C"; }
    else if (control === "selected-campaign") state.selectedCampaign = target.value;
    renderApp();
  });

  document.getElementById("reset-filters").addEventListener("click", () => {
    state.month = latestMonth;
    state.product = state.page === "products" ? defaultProduct : "ALL";
    renderApp();
    toast("全局切片已重置");
  });
  document.getElementById("menu-toggle").addEventListener("click", () => {
    document.body.classList.contains("menu-open") ? closeMobileMenu(true) : openMobileMenu();
  });
  document.getElementById("sidebar-overlay").addEventListener("click", () => closeMobileMenu(true));
  document.addEventListener("keydown", (event) => { if (event.key === "Escape" && document.body.classList.contains("menu-open")) closeMobileMenu(true); });
  window.addEventListener("hashchange", () => {
    const page = location.hash.replace("#", "");
    if (validPages.includes(page) && page !== state.page) { state.page = page; renderApp(); }
  });

  let compactLayout = isCompactViewport();
  let mobileNavLayout = Number(window.innerWidth) <= 820;
  let resizeTimer = null;
  window.addEventListener("resize", () => {
    const width = Number(window.innerWidth);
    const nextMobileNav = Number.isFinite(width) && width <= 820;
    if (nextMobileNav !== mobileNavLayout) {
      mobileNavLayout = nextMobileNav;
      closeMobileMenu(false);
    }
    const nextCompact = isCompactViewport();
    if (nextCompact === compactLayout) return;
    compactLayout = nextCompact;
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(renderApp, 120);
  });

  renderApp();
})();
