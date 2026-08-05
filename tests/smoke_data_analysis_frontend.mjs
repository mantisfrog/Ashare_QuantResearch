import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
import { fileURLToPath } from "node:url";
import path from "node:path";

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, "..");
const dataSource = fs.readFileSync(path.join(repo, "docs/data_analysis/data.js"), "utf8");
const appSource = fs.readFileSync(path.join(repo, "docs/data_analysis/app.js"), "utf8");
const cssSource = fs.readFileSync(path.join(repo, "docs/data_analysis/styles.css"), "utf8");
const pageSource = fs.readFileSync(path.join(repo, "docs/data_analysis/index.html"), "utf8");
const homeSource = fs.readFileSync(path.join(repo, "docs/index.html"), "utf8");
const methodologySource = fs.readFileSync(path.join(repo, "docs/methodology.html"), "utf8");
const snapshot = JSON.parse(
  dataSource.trim().slice("window.RETAIL_DATA=".length).replace(/;$/, ""),
);
assert.equal(snapshot.meta.schema_version, "retail-static-v1", "snapshot schema version changed");

const globalLatest = snapshot.kpis.find((row) => row.month === "2026-07" && row.scope === "ALL");
assert.ok(Math.abs(globalLatest.aum - 159469423.91) < 0.01, "latest AUM anchor changed");
assert.ok(Math.abs(globalLatest.net - (-7939012.88)) < 0.01, "latest net-flow anchor changed");
assert.equal(globalLatest.high_value_customers, 30, "high-value customer anchor changed");
assert.equal(globalLatest.red_alert_records, 18, "red-alert anchor changed");
const migrationAnchor = snapshot.migration_redemptions.find((row) => row.month === "2026-07" && row.prev_tier === "T3" && row.curr_tier === "T1" && row.product_code === "017560.OF");
assert.equal(migrationAnchor.customers, 36, "migration redemption anchor changed");
const channelAnchor = snapshot.channel_alert_flows.AL_R1_02[0];
assert.equal(channelAnchor.product_code, "040038.OF", "channel drill product anchor changed");
assert.ok(Math.abs(channelAnchor.net_inflow - (-1091310.13)) < 0.01, "channel drill flow anchor changed");
const campaignAnchor = snapshot.campaigns.find((row) => row.campaign_id === "CP_C");
assert.ok(Math.abs(campaignAnchor["30天赎回金额"] - 12553176.32) < 0.01, "campaign redemption anchor changed");
assert.ok(Math.abs(snapshot.direct_app_retention - 11 / 12) < 1e-12, "direct retention anchor changed");
assert.ok(cssSource.includes("@media (max-width: 820px)"), "mobile breakpoint is missing");
const mobileCss = cssSource.slice(cssSource.indexOf("@media (max-width: 820px)"));
assert.match(mobileCss, /\.sidebar\s*\{[\s\S]*?position:\s*static;/, "mobile navigation is not in normal document flow");
assert.ok(mobileCss.includes("grid-template-columns: repeat(2, minmax(0, 1fr));"), "mobile navigation does not use the wealth-style two-column layout");
const narrowMobileCss = cssSource.slice(cssSource.indexOf("@media (max-width: 520px)"));
assert.match(narrowMobileCss, /\.nav-list\s*\{[\s\S]*?grid-template-columns:\s*1fr;/, "narrow mobile navigation is not single-column");
assert.ok(pageSource.includes('class="sidebar reveal d1"'), "top navigation container is missing");
assert.ok(!pageSource.includes('id="menu-toggle"'), "legacy mobile menu toggle still exists");
assert.ok(!pageSource.includes('id="sidebar-overlay"'), "legacy mobile sidebar overlay still exists");
assert.ok(!appSource.includes("openMobileMenu"), "legacy mobile menu open logic still exists");
assert.ok(!appSource.includes("closeMobileMenu"), "legacy mobile menu close logic still exists");
assert.ok(!appSource.includes("menu-open"), "legacy mobile menu state still exists");
assert.ok(!appSource.includes("sidebar.inert"), "legacy inert sidebar state still exists");
assert.ok(!appSource.includes("capabilityHero"), "ability-chain renderer still exists");
assert.ok(!cssSource.includes(".capability-flow"), "ability-chain styles still exist");
assert.ok(cssSource.includes(".heatmap-cell.selected"), "heatmap selection styling is missing");
assert.ok(cssSource.includes("@media (max-width: 520px)"), "single-column mobile filters are missing");
assert.ok(cssSource.includes(".alert-editor td::before"), "mobile alert cards are missing field labels");
assert.ok(cssSource.includes("grid-template-columns: 54px repeat(6, minmax(42px, 1fr))"), "compact migration matrix is missing");
assert.ok(cssSource.includes(".legend-symbol.diamond"), "channel shape legend styling is missing");
assert.ok(homeSource.includes("Quant Research · Data Analysis"), "home kicker is missing");
assert.ok(homeSource.includes("毕闻博作品集"), "home title is missing");
assert.ok(homeSource.includes("UWA商业分析硕士（荣誉），具有金融和数据复合背景"), "user-updated home introduction is missing");
assert.ok(homeSource.includes("./data_analysis/index.html"), "data-analysis entry is missing");
assert.equal((homeSource.match(/class="entry"/g) || []).length, 3, "home must expose exactly three entries");
assert.ok(homeSource.includes('href="./methodology.html"'), "home methodology entry is missing");
assert.ok(homeSource.includes("数据属性、处理链路、验证方法与演示边界"), "home methodology summary is missing");
assert.ok(homeSource.indexOf('class="engineering-note') > homeSource.lastIndexOf('class="entry"'), "home methodology entry must follow the three portfolio entries");
assert.ok(homeSource.indexOf('class="engineering-note') < homeSource.indexOf('class="footer"'), "home methodology entry must precede the footer");
assert.match(homeSource, /@media \(max-width: 640px\)[\s\S]*?\.engineering-note\s*\{\s*grid-template-columns:\s*1fr;/, "home methodology entry is not mobile responsive");
assert.ok(methodologySource.includes('name="viewport"'), "methodology page has no mobile viewport");
assert.match(methodologySource, /@media \(max-width: 600px\)[\s\S]*?\.module-head,[\s\S]*?grid-template-columns:\s*1fr;/, "methodology details do not collapse on mobile");
assert.equal((methodologySource.match(/<article class="module"/g) || []).length, 3, "methodology page must document exactly three modules");
for (const id of ["factor", "wealth", "data-analysis"]) {
  assert.ok(methodologySource.includes(`id="${id}"`), `methodology page is missing ${id}`);
}
for (const label of ["数据来源", "处理链路", "验证方法", "技术栈", "演示边界"]) {
  assert.ok(methodologySource.includes(label), `methodology page is missing ${label}`);
}
assert.ok(methodologySource.includes("真实市场数据 · 静态快照"), "factor data property is not disclosed");
assert.ok(methodologySource.includes("合成业务数据 · 规则原型"), "wealth demo data property is not disclosed");
assert.ok(methodologySource.includes("市场/产品数据 + 模拟经营数据"), "analytics mixed data property is not disclosed");
assert.equal((methodologySource.match(/<ol class="pipeline"/g) || []).length, 3, "module pipelines are not exposed as semantic lists");
assert.ok(methodologySource.includes("MAD×3 缩尾"), "factor preprocessing method is missing");
assert.ok(methodologySource.includes("当前没有接入真实 CRM、交易系统、后端 API 或生成式模型"), "wealth AI boundary is missing");
assert.ok(methodologySource.includes("localStorage"), "analytics persistence boundary is missing");
assert.ok(methodologySource.includes("并非七条规则的全量扫描"), "analytics alert-sample boundary is missing");
assert.ok(methodologySource.includes("不代表因果增量或真实 ROI"), "analytics campaign boundary is missing");
assert.ok(!methodologySource.includes("严谨性如何落实到 Demo"), "removed rigor section still exists");
assert.ok(!methodologySource.includes(".quality-grid"), "removed rigor-section styles still exist");
assert.ok(!methodologySource.includes('class="hero-copy"'), "removed methodology introduction still exists");
assert.ok(!methodologySource.includes('class="principle-strip"'), "removed methodology principle cards still exist");
assert.ok(!methodologySource.includes('class="module-index"'), "removed methodology module index still exists");
assert.ok(!methodologySource.includes("数据有出处"), "removed provenance heading still exists");
assert.ok(!methodologySource.includes("指标有口径"), "removed methodology heading still exists");
assert.ok(!methodologySource.includes("结论有边界"), "removed boundary heading still exists");
assert.match(methodologySource, /<h1>数据与工程说明<\/h1>\s*<\/section>\s*<article class="module" id="factor">/, "factor module must immediately follow the methodology title section");
assert.ok(methodologySource.includes('href="./index.html"'), "methodology page has no path back home");
assert.ok(!fs.existsSync(path.join(repo, "docs/weekly_views.html")), "weekly index still exists");
assert.ok(!fs.existsSync(path.join(repo, "docs/weekly/2026-07-03-weekly-review.html")), "weekly article still exists");

const expected = {
  overview: "AUM经营归因瀑布",
  alerts: "处置工作台",
  channels: "渠道价值地图",
  customers: "相邻月末客户层级迁移",
  products: "净值与周度净申购",
  marketing: "活动转化比较",
  report: "基金零售经营月报",
};

function classList() {
  const values = new Set();
  return {
    add: (...names) => names.forEach((name) => values.add(name)),
    remove: (...names) => names.forEach((name) => values.delete(name)),
    contains: (name) => values.has(name),
    toggle: (name, force) => {
      if (force === true) values.add(name);
      else if (force === false) values.delete(name);
      else if (values.has(name)) values.delete(name);
      else values.add(name);
    },
  };
}

function element(id = "") {
  const listeners = {};
  return {
    id,
    value: "",
    textContent: "",
    innerHTML: "",
    disabled: false,
    dataset: {},
    classList: classList(),
    attributes: {},
    setAttribute(name, value) { this.attributes[name] = String(value); },
    listeners,
    addEventListener(type, handler) { listeners[type] = handler; },
    appendChild() {},
    remove() {},
    click() {},
    focus() { this.focused = true; },
  };
}

function render(page, options = {}) {
  const ids = [
    "page-root", "page-title", "page-kicker", "month-select", "product-select",
    "context-text", "snapshot-badge", "reset-filters", "sidebar", "toast",
  ];
  const elements = Object.fromEntries(ids.map((id) => [id, element(id)]));
  const productControl = element("product-control");
  const navItems = Object.keys(expected).map((name) => {
    const item = element();
    item.dataset.page = name;
    return item;
  });
  const body = element("body");
  const errors = [];
  const documentListeners = {};
  const document = {
    title: "",
    body,
    getElementById: (id) => elements[id] || null,
    querySelector: (selector) => selector === ".product-control" ? productControl : null,
    querySelectorAll: (selector) => selector === ".nav-item[data-page]" ? navItems : [],
    addEventListener(type, handler) { documentListeners[type] = handler; },
    createElement: () => element(),
  };
  const local = new Map();
  const windowListeners = {};
  const context = {
    document,
    location: { hash: `#${page}`, reload() {} },
    history: { pushState() {} },
    localStorage: {
      getItem: (key) => local.get(key) || null,
      setItem: (key, value) => local.set(key, String(value)),
    },
    console: { ...console, error: (...args) => errors.push(args.join(" ")) },
    setTimeout,
    clearTimeout,
    Blob,
    URL,
    scrollTo() {},
    innerWidth: options.width || 1280,
    addEventListener(type, handler) { windowListeners[type] = handler; },
  };
  context.window = context;
  context.globalThis = context;
  vm.createContext(context);
  vm.runInContext(dataSource, context, { filename: "data.js" });
  vm.runInContext(appSource, context, { filename: "app.js" });
  assert.deepEqual(errors, [], `${page} logged a render error: ${errors.join(" | ")}`);
  assert.ok(elements["page-root"].innerHTML.length > 500, `${page} rendered too little content`);
  assert.ok(!elements["page-root"].innerHTML.includes("error-state"), `${page} rendered its error state`);
  assert.ok(elements["page-root"].innerHTML.includes(expected[page]), `${page} is missing its primary content anchor`);
  return { elements, documentListeners, windowListeners, context, errors, navItems };
}

for (const page of Object.keys(expected)) render(page);

function actionEvent(action, value, extra = {}) {
  const target = {
    dataset: { action, value, ...extra },
    closest(selector) {
      if (selector === ".nav-item[data-page]") return null;
      if (selector === "[data-action]") return this;
      return null;
    },
  };
  return { target };
}

const customers = render("customers");
customers.documentListeners.click(actionEvent("customer-tab", "retention"));
assert.ok(customers.elements["page-root"].innerHTML.includes("流失前兆三轨回放"), "customer retention tab did not render");
assert.ok(customers.elements["page-root"].innerHTML.includes("蚂蚁财富（互联网）"), "cohort channel legend is not human-readable");

const products = render("products");
const productOperationsHtml = products.elements["page-root"].innerHTML;
const desktopNavMarkers = [...productOperationsHtml.matchAll(/class="chart-point chart-point-dense"[^>]*r="1\.4"/g)];
assert.ok(desktopNavMarkers.length >= 2 && desktopNavMarkers.length <= 48, "desktop NAV markers were not reduced to the dense-series limit");
const navSvg = productOperationsHtml.match(/<svg[^>]*aria-label="单位净值趋势"[^>]*>([\s\S]*?)<\/svg>/);
assert.ok(navSvg, "NAV trend SVG is missing");
const navPolyline = navSvg[1].match(/<polyline[^>]*points="([^"]+)"/);
assert.ok(navPolyline, "NAV trend polyline is missing");
const latestNavMonth = snapshot.months.at(-1);
const [latestNavYear, latestNavMonthNumber] = latestNavMonth.split("-").map(Number);
const navWindowStartDate = new Date(Date.UTC(latestNavYear, latestNavMonthNumber - 1 - 13, 1));
const navWindowStart = `${navWindowStartDate.getUTCFullYear()}-${String(navWindowStartDate.getUTCMonth() + 1).padStart(2, "0")}`;
const expectedNavPoints = snapshot.nav.filter((row) => row.fund_code === "017560.OF" && row.date.slice(0, 7) >= navWindowStart && row.date.slice(0, 7) <= latestNavMonth).length;
assert.equal(navPolyline[1].trim().split(/\s+/).length, expectedNavPoints, "NAV line was downsampled together with its markers");
products.documentListeners.click(actionEvent("product-tab", "benchmark"));
assert.ok(products.elements["page-root"].innerHTML.includes("AMAC 销售机构排名"), "product benchmark tab did not render");

const report = render("report");
report.documentListeners.click(actionEvent("report-tab", "facts"));
assert.ok(report.elements["page-root"].innerHTML.includes("月报事实表"), "report facts tab did not render");

const overview = render("overview");
assert.match(overview.elements["page-root"].innerHTML, /class="chart-point"[^>]*r="3\.2"/, "standard monthly chart markers were changed globally");
assert.ok(!overview.elements["page-root"].innerHTML.includes("从多源零售数据到经营增量机会"), "ability chain still renders");
assert.ok(overview.elements["page-root"].innerHTML.includes("领导摘要：结论、归因、对象与动作"), "executive brief is missing");
assert.ok(overview.elements["page-root"].innerHTML.includes("零售全业务场景分析体系"), "scenario capability map is missing");
overview.documentListeners.change({ target: { id: "product-select", value: "017560.OF", dataset: {}, matches: () => false } });
assert.ok(overview.elements["page-root"].innerHTML.includes("产品持有流失率"), "overview product scope did not apply");
assert.ok(overview.elements["page-root"].innerHTML.includes("61.1%"), "overview product churn anchor is missing");
overview.documentListeners.click(actionEvent("navigate", "products", { view: "benchmark" }));
assert.ok(overview.elements["page-root"].innerHTML.includes("AMAC 销售机构排名"), "capability-map deep link did not open the requested subview");

const alerts = render("alerts");
alerts.documentListeners.click(actionEvent("drill-alert", "AL_R1_02"));
assert.ok(alerts.elements["page-root"].innerHTML.includes("预警窗口的产品贡献"), "alert-to-channel drill did not apply");
assert.ok(alerts.elements["page-root"].innerHTML.includes("040038.OF"), "drill product contribution anchor is missing");

const channels = render("channels");
assert.ok(channels.elements["page-root"].innerHTML.includes("aria-label=\"渠道类型图例\""), "channel type legend is missing");
assert.ok(channels.elements["page-root"].innerHTML.includes("legend-symbol square"), "internet channel square encoding is missing");
assert.ok(channels.elements["page-root"].innerHTML.includes("legend-symbol diamond"), "direct channel diamond encoding is missing");
assert.ok(channels.elements["page-root"].innerHTML.includes("金色描边＝当前重点"), "selected-channel legend is missing");

const mobileChannels = render("channels", { width: 390 });
assert.ok(mobileChannels.elements["page-root"].innerHTML.includes('viewBox="0 0 420'), "mobile charts did not switch to compact geometry");
const mobileProducts = render("products", { width: 390 });
const mobileNavMarkers = [...mobileProducts.elements["page-root"].innerHTML.matchAll(/class="chart-point chart-point-dense"[^>]*r="1\.4"/g)];
assert.ok(mobileNavMarkers.length >= 2 && mobileNavMarkers.length <= 24, "mobile NAV markers were not reduced to the compact limit");
assert.ok(mobileProducts.elements["page-root"].innerHTML.includes('viewBox="0 0 420 260"'), "mobile NAV chart did not use compact geometry");
const mobileOverview = render("overview", { width: 390 });
mobileOverview.documentListeners.click({
  target: {
    dataset: { page: "alerts" },
    closest(selector) {
      if (selector === ".nav-item[data-page]") return this;
      return null;
    },
  },
});
assert.equal(mobileOverview.elements["page-title"].textContent, "预警与行动", "mobile top navigation is not clickable");
assert.ok(mobileOverview.elements["page-root"].innerHTML.includes("处置工作台"), "mobile navigation did not render the selected page");
assert.equal(mobileOverview.navItems.filter((item) => item.attributes["aria-current"] === "page").length, 1, "mobile active navigation state is invalid");
const mobileAlerts = render("alerts", { width: 390 });
assert.ok(mobileAlerts.elements["page-root"].innerHTML.includes('data-label="Owner"'), "mobile alert editor labels are missing");
const marketing = render("marketing");
assert.ok(marketing.elements["page-root"].innerHTML.includes("条形颜色区分活动渠道类型"), "campaign channel encoding note is missing");
assert.ok(marketing.elements["page-root"].innerHTML.includes("补贴活动"), "campaign subsidy status is missing");

for (const result of [customers, products, report, overview, alerts, channels, mobileChannels, mobileProducts, mobileOverview, mobileAlerts, marketing]) {
  assert.deepEqual(result.errors, [], `interaction logged a render error: ${result.errors.join(" | ")}`);
}

console.log(`Static frontend smoke passed: ${Object.keys(expected).length} workspaces and core interactions rendered.`);
