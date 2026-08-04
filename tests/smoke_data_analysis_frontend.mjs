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
const homeSource = fs.readFileSync(path.join(repo, "docs/index.html"), "utf8");
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
assert.ok(cssSource.includes("body.menu-open .sidebar"), "mobile sidebar state is missing");
assert.ok(cssSource.includes(".heatmap-cell.selected"), "heatmap selection styling is missing");
assert.ok(homeSource.includes("Quant Research · Data Analysis"), "home kicker is missing");
assert.ok(homeSource.includes("毕闻博作品集"), "home title is missing");
assert.ok(homeSource.includes("./data_analysis/index.html"), "data-analysis entry is missing");
assert.equal((homeSource.match(/class="entry"/g) || []).length, 3, "home must expose exactly three entries");
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
  };
}

function render(page) {
  const ids = [
    "page-root", "page-title", "page-kicker", "month-select", "product-select",
    "context-text", "snapshot-badge", "reset-filters", "menu-toggle",
    "sidebar-overlay", "toast",
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
  return { elements, documentListeners, errors };
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

const products = render("products");
products.documentListeners.click(actionEvent("product-tab", "benchmark"));
assert.ok(products.elements["page-root"].innerHTML.includes("AMAC 销售机构排名"), "product benchmark tab did not render");

const report = render("report");
report.documentListeners.click(actionEvent("report-tab", "facts"));
assert.ok(report.elements["page-root"].innerHTML.includes("月报事实表"), "report facts tab did not render");

const overview = render("overview");
overview.documentListeners.change({ target: { id: "product-select", value: "017560.OF", dataset: {}, matches: () => false } });
assert.ok(overview.elements["page-root"].innerHTML.includes("产品持有流失率"), "overview product scope did not apply");
assert.ok(overview.elements["page-root"].innerHTML.includes("61.1%"), "overview product churn anchor is missing");

const alerts = render("alerts");
alerts.documentListeners.click(actionEvent("drill-alert", "AL_R1_02"));
assert.ok(alerts.elements["page-root"].innerHTML.includes("预警窗口的产品贡献"), "alert-to-channel drill did not apply");
assert.ok(alerts.elements["page-root"].innerHTML.includes("040038.OF"), "drill product contribution anchor is missing");

for (const result of [customers, products, report, overview, alerts]) {
  assert.deepEqual(result.errors, [], `interaction logged a render error: ${result.errors.join(" | ")}`);
}

console.log(`Static frontend smoke passed: ${Object.keys(expected).length} workspaces and core interactions rendered.`);
