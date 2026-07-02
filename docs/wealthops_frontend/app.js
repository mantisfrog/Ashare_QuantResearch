const ASSETS = [
  { key: "cash", label: "现金/货币" },
  { key: "fixedIncome", label: "固收/理财" },
  { key: "fixedPlus", label: "固收+" },
  { key: "equity", label: "权益基金/ETF" },
  { key: "gold", label: "黄金/另类" },
];

const RISK_SCORE = { R1: 1, R2: 2, R3: 3, R4: 4, R5: 5 };
const LIQUIDITY_SCORE = { "极低": 0, "低": 1, "中": 2, "高": 3 };

// 演示基准日（保持确定性输出）
const AS_OF = new Date("2026-07-02");

// 资产类别演示参数：年化波动率 / 压力情景回撤（用于风险预算测算）
const ASSET_VOL = { cash: 0.005, fixedIncome: 0.02, fixedPlus: 0.05, equity: 0.18, gold: 0.14 };
const ASSET_STRESS = { cash: 0, fixedIncome: -0.01, fixedPlus: -0.04, equity: -0.25, gold: -0.15 };

// 风险预算基准（按风险等级）：最大可接受年化波动 / 压力回撤
const RISK_BUDGET_BASE = {
  R1: { maxVol: 0.02, maxDrawdown: 0.02 },
  R2: { maxVol: 0.045, maxDrawdown: 0.05 },
  R3: { maxVol: 0.075, maxDrawdown: 0.1 },
  R4: { maxVol: 0.13, maxDrawdown: 0.18 },
  R5: { maxVol: 0.2, maxDrawdown: 0.25 },
};

const JOURNEY_STAGES = ["已诊断", "已生成建议", "已筛选产品", "话术已复核", "已触达", "投后跟踪中"];

const SCRIPT_SCENARIOS = [
  { key: "firstTouch", label: "首次配置触达" },
  { key: "maturity", label: "到期资金承接" },
  { key: "drawdown", label: "回撤安抚" },
  { key: "rebalance", label: "再平衡建议" },
  { key: "afterReject", label: "被拒后跟进" },
];

const pageTitles = {
  strategy: "市场观点与分层配置模板",
  segment: "客群资产配置服务机会识别",
  diagnosis: "单客户配置诊断与投后触发",
  product: "产品适配筛选与 AI 产品解读",
  governance: "智能体治理看板与反馈闭环",
  chatbot: "产品解读 Copilot（对话式 Demo）",
};

const state = {
  page: initialPage(),
  branch: "全部",
  risk: "R3",
  selectedCustomerId: "C001",
  selectedProductId: "P002",
  marketViews: {
    cash: "中性",
    fixedIncome: "积极",
    fixedPlus: "积极",
    equity: "谨慎",
    gold: "积极",
  },
  feedback: [
    { id: "F001", customerId: "C001", productId: "P002", action: "accepted", reason: "-", comment: "配置缺口明确，客户可接受净值波动" },
    { id: "F002", customerId: "C014", productId: "P003", action: "rejected", reason: "风险过高", comment: "客户对权益波动仍较敏感" },
    { id: "F003", customerId: "C027", productId: "P005", action: "accepted", reason: "-", comment: "用于小比例分散配置" },
    { id: "F004", customerId: "C036", productId: "P006", action: "rejected", reason: "流动性不匹配", comment: "资金可能 12 个月内用于购房" },
    { id: "F005", customerId: "C052", productId: "P002", action: "pending", reason: "待跟进", comment: "客户需要家庭会议后确认" },
    { id: "F006", customerId: "C014", productId: "P004", action: "rejected", reason: "风险过高", comment: "客户明确表示不接受高波动产品" },
  ],
  scriptScenario: "firstTouch",
  journey: { C001: 2, C014: 4, C027: 1, C036: 0, C052: 5, C066: 1 },
  chatMessages: [],
  chatEvidence: null,
  chatPeriod: "3M",
  aiAuditLog: [
    { logId: "L001", time: "07-01 09:32", advisor: "上海-张敏", customerId: "C001", productId: "P002", scenario: "产品解读", promptVersion: "v0.3", kbVersion: "2026-06", scanResult: "pass", reviewStatus: "auto-pass", delivered: true },
    { logId: "L002", time: "07-01 10:18", advisor: "深圳-李强", customerId: "C014", productId: "P003", scenario: "首次配置触达", promptVersion: "v0.3", kbVersion: "2026-06", scanResult: "pass", reviewStatus: "auto-pass", delivered: true },
    { logId: "L003", time: "07-01 11:05", advisor: "杭州-王芳", customerId: "C027", productId: "P001", scenario: "到期资金承接", promptVersion: "v0.3", kbVersion: "2026-06", scanResult: "hit", reviewStatus: "pending-review", delivered: false },
    { logId: "L004", time: "07-01 14:40", advisor: "深圳-李强", customerId: "C052", productId: "P004", scenario: "回撤安抚", promptVersion: "v0.3", kbVersion: "2026-06", scanResult: "pass", reviewStatus: "approved", delivered: true },
    { logId: "L005", time: "07-02 09:10", advisor: "上海-张敏", customerId: "C036", productId: "P001", scenario: "产品解读", promptVersion: "v0.3", kbVersion: "2026-06", scanResult: "pass", reviewStatus: "pending-review", delivered: false },
  ],
};

function initialPage() {
  const page = window.location.hash.replace("#", "");
  return pageTitles?.[page] ? page : "strategy";
}

const baseTemplates = {
  R2: { cash: 0.15, fixedIncome: 0.6, fixedPlus: 0.15, equity: 0.05, gold: 0.05 },
  R3: { cash: 0.1, fixedIncome: 0.45, fixedPlus: 0.25, equity: 0.15, gold: 0.05 },
  R4: { cash: 0.05, fixedIncome: 0.3, fixedPlus: 0.25, equity: 0.35, gold: 0.05 },
};

const customers = [
  {
    id: "C001",
    name: "王女士",
    branch: "上海分行",
    age: 35,
    lifeStage: "家庭成长期",
    risk: "R3",
    aum: 800000,
    horizonYears: 3,
    liquidityNeed: "中",
    lastContactDays: 42,
    maturityAmount: 180000,
    maturityDays: 12,
    drawdown: -0.035,
    portfolio: { cash: 0.3, fixedIncome: 0.45, fixedPlus: 0.15, equity: 0.1, gold: 0 },
    kyc: { assessDate: "2025-11-20", validUntil: "2026-11-20", score: 62, investYears: 5, experiencedTypes: ["理财", "基金", "固收+"] },
    behavior: { tradeFreqPerYear: 6, avgHoldingMonths: 14, chaseIndex: 0.3, hasSIP: true, panicRedeemed: false },
  },
  {
    id: "C014",
    name: "陈先生",
    branch: "深圳分行",
    age: 48,
    lifeStage: "事业成熟期",
    risk: "R3",
    aum: 850000,
    horizonYears: 2,
    liquidityNeed: "中",
    lastContactDays: 68,
    maturityAmount: 90000,
    maturityDays: 45,
    drawdown: -0.021,
    portfolio: { cash: 0.18, fixedIncome: 0.62, fixedPlus: 0.1, equity: 0.08, gold: 0.02 },
    kyc: { assessDate: "2025-10-15", validUntil: "2026-10-15", score: 55, investYears: 8, experiencedTypes: ["理财", "基金"] },
    behavior: { tradeFreqPerYear: 4, avgHoldingMonths: 18, chaseIndex: 0.2, hasSIP: false, panicRedeemed: true },
  },
  {
    id: "C027",
    name: "李女士",
    branch: "杭州分行",
    age: 56,
    lifeStage: "退休规划期",
    risk: "R3",
    aum: 2000000,
    horizonYears: 3,
    liquidityNeed: "低",
    lastContactDays: 21,
    maturityAmount: 620000,
    maturityDays: 8,
    drawdown: -0.012,
    portfolio: { cash: 0.25, fixedIncome: 0.52, fixedPlus: 0.13, equity: 0.08, gold: 0.02 },
    kyc: { assessDate: "2026-03-02", validUntil: "2027-03-02", score: 58, investYears: 12, experiencedTypes: ["理财", "基金", "黄金"] },
    behavior: { tradeFreqPerYear: 3, avgHoldingMonths: 22, chaseIndex: 0.15, hasSIP: false, panicRedeemed: false },
  },
  {
    id: "C036",
    name: "赵先生",
    branch: "上海分行",
    age: 39,
    lifeStage: "子女教育期",
    risk: "R2",
    aum: 620000,
    horizonYears: 1,
    liquidityNeed: "高",
    lastContactDays: 96,
    maturityAmount: 240000,
    maturityDays: 18,
    drawdown: -0.006,
    portfolio: { cash: 0.4, fixedIncome: 0.45, fixedPlus: 0.08, equity: 0.04, gold: 0.03 },
    kyc: { assessDate: "2025-05-20", validUntil: "2026-05-20", score: 41, investYears: 3, experiencedTypes: ["理财"] },
    behavior: { tradeFreqPerYear: 10, avgHoldingMonths: 7, chaseIndex: 0.5, hasSIP: false, panicRedeemed: false },
  },
  {
    id: "C052",
    name: "周先生",
    branch: "深圳分行",
    age: 31,
    lifeStage: "财富积累期",
    risk: "R4",
    aum: 1200000,
    horizonYears: 5,
    liquidityNeed: "中",
    lastContactDays: 17,
    maturityAmount: 80000,
    maturityDays: 92,
    drawdown: -0.092,
    portfolio: { cash: 0.08, fixedIncome: 0.42, fixedPlus: 0.2, equity: 0.27, gold: 0.03 },
    kyc: { assessDate: "2026-01-12", validUntil: "2027-01-12", score: 74, investYears: 6, experiencedTypes: ["基金", "权益", "黄金"] },
    behavior: { tradeFreqPerYear: 15, avgHoldingMonths: 6, chaseIndex: 0.72, hasSIP: true, panicRedeemed: false },
  },
  {
    id: "C066",
    name: "沈女士",
    branch: "杭州分行",
    age: 44,
    lifeStage: "家庭资产升级期",
    risk: "R3",
    aum: 1380000,
    horizonYears: 4,
    liquidityNeed: "中",
    lastContactDays: 75,
    maturityAmount: 120000,
    maturityDays: 14,
    drawdown: -0.048,
    portfolio: { cash: 0.22, fixedIncome: 0.5, fixedPlus: 0.12, equity: 0.11, gold: 0.05 },
    kyc: { assessDate: "2025-07-25", validUntil: "2026-07-25", score: 57, investYears: 7, experiencedTypes: ["理财", "基金"] },
    behavior: { tradeFreqPerYear: 5, avgHoldingMonths: 13, chaseIndex: 0.35, hasSIP: false, panicRedeemed: true },
  },
];

const marketRows = [
  { key: "cash", action: "保留流动性" },
  { key: "fixedIncome", action: "作为组合底仓" },
  { key: "fixedPlus", action: "替代部分低收益理财" },
  { key: "equity", action: "控制比例、分批配置" },
  { key: "gold", action: "用于分散风险" },
];

function marketActionText(assetKey, view) {
  const matrix = {
    cash: {
      积极: "提升流动性防御仓位",
      中性: "保留流动性",
      谨慎: "控制现金占比，转向配置资产",
    },
    fixedIncome: {
      积极: "提升固收底仓权重",
      中性: "作为组合底仓",
      谨慎: "降低久期和信用暴露",
    },
    fixedPlus: {
      积极: "替代部分低收益理财",
      中性: "小比例增强配置",
      谨慎: "压缩增强仓位，回归纯固收",
    },
    equity: {
      积极: "分批提升权益仓位",
      中性: "维持中枢仓位，择机定投",
      谨慎: "控制比例、分批配置",
    },
    gold: {
      积极: "提升黄金分散权重",
      中性: "用于分散风险",
      谨慎: "保留小比例对冲仓位",
    },
  };
  return matrix[assetKey]?.[view] || "保持观察";
}

const products = [
  {
    id: "P001",
    name: "稳健月月盈",
    type: "银行理财",
    risk: "R2",
    horizonMonths: 6,
    liquidity: "中",
    assetClass: "fixedIncome",
    role: "固收底仓",
    drawdownLevel: "低",
    fee: "低",
    volatility: 0.015,
    maxDrawdownHist: -0.008,
    benchmark: "中债综合财富指数",
    fees: "认购 0 · 管理 0.3%/年 · 赎回 0",
    openFrequency: "每月开放申赎",
    inceptionDate: "2022-06-01",
    salesStatus: "在售 · 代销准入有效",
    audienceTags: ["理财替代", "到期承接"],
    docExcerpts: {
      investScope: "本产品 90% 以上投资于国债、金融债、高等级信用债及银行存款类资产，不直接投资于股票。",
      riskDisclosure: "本产品为净值型理财产品，不保证本金和收益，净值可能因利率变动出现小幅波动。",
    },
    docSources: ["产品说明书-投资范围", "产品池字段-风险等级 R2"],
  },
  {
    id: "P002",
    name: "固收增强 A",
    type: "固收+基金",
    risk: "R3",
    horizonMonths: 12,
    liquidity: "中",
    assetClass: "fixedPlus",
    role: "固收增强",
    drawdownLevel: "中",
    fee: "中",
    volatility: 0.045,
    maxDrawdownHist: -0.038,
    benchmark: "中债综合×90% + 中证800×10%",
    fees: "申购 0.3% · 管理 0.6%/年 · 赎回 持有<180天 0.5%",
    openFrequency: "每日开放 · 赎回 T+1",
    inceptionDate: "2021-03-15",
    salesStatus: "在售 · 代销准入有效",
    audienceTags: ["固收增强", "到期承接", "理财替代"],
    docExcerpts: {
      investScope: "本基金 80% 以上投资于债券类资产，不超过 20% 投资于股票、可转债等权益类资产。",
      riskDisclosure: "本基金为净值型产品，不保证本金和收益；历史最大回撤 -3.8%，持有不足 180 天赎回需支付赎回费。",
    },
    docSources: ["产品说明书-投资范围", "产品说明书-风险揭示", "产品池字段-风险等级 R3"],
  },
  {
    id: "P003",
    name: "中证红利 ETF",
    type: "权益 ETF",
    risk: "R3",
    horizonMonths: 36,
    liquidity: "高",
    assetClass: "equity",
    role: "低波动权益增强",
    drawdownLevel: "中高",
    fee: "低",
    volatility: 0.16,
    maxDrawdownHist: -0.18,
    benchmark: "中证红利指数",
    fees: "管理 0.5%/年 · 场内交易佣金",
    openFrequency: "场内实时交易",
    inceptionDate: "2019-11-28",
    salesStatus: "在售 · 代销准入有效",
    audienceTags: ["低波权益", "红利策略", "长期配置"],
    docExcerpts: {
      investScope: "本基金采用完全复制策略跟踪中证红利指数，成分股为高股息率蓝筹。",
      riskDisclosure: "权益类产品净值波动较大，历史最大回撤 -18%，适合长期持有并接受阶段性亏损的客户。",
    },
    docSources: ["指数基金招募说明书-跟踪标的", "产品说明书-风险揭示"],
  },
  {
    id: "P004",
    name: "科技成长基金",
    type: "权益基金",
    risk: "R4",
    horizonMonths: 36,
    liquidity: "高",
    assetClass: "equity",
    role: "高弹性权益配置",
    drawdownLevel: "高",
    fee: "中",
    volatility: 0.24,
    maxDrawdownHist: -0.31,
    benchmark: "中证 TMT 指数×85% + 中债综合×15%",
    fees: "申购 1.2% · 管理 1.5%/年 · 赎回 持有<365天 0.5%",
    openFrequency: "每日开放 · 赎回 T+2",
    inceptionDate: "2020-05-18",
    salesStatus: "在售 · 代销准入有效",
    audienceTags: ["高弹性", "卫星仓位"],
    docExcerpts: {
      investScope: "本基金主要投资于科技、半导体、人工智能等成长行业上市公司股票，股票仓位 60%-95%。",
      riskDisclosure: "本基金属高波动权益产品，历史最大回撤 -31%，仅适合风险承受能力较高且长期投资的客户。",
    },
    docSources: ["基金合同-投资策略", "产品说明书-风险揭示"],
  },
  {
    id: "P005",
    name: "黄金 ETF",
    type: "商品 ETF",
    risk: "R3",
    horizonMonths: 12,
    liquidity: "高",
    assetClass: "gold",
    role: "组合分散资产",
    drawdownLevel: "中",
    fee: "低",
    volatility: 0.14,
    maxDrawdownHist: -0.12,
    benchmark: "国内黄金现货价格",
    fees: "管理 0.5%/年 · 场内交易佣金",
    openFrequency: "场内实时交易",
    inceptionDate: "2018-08-08",
    salesStatus: "在售 · 代销准入有效",
    audienceTags: ["分散配置", "抗通胀"],
    docExcerpts: {
      investScope: "本基金主要投资于上海黄金交易所挂牌的黄金现货合约，紧密跟踪金价。",
      riskDisclosure: "黄金价格受国际宏观因素影响波动较大，历史最大回撤 -12%，建议作为组合分散资产小比例配置。",
    },
    docSources: ["产品说明书-投资范围", "产品说明书-风险揭示"],
  },
  {
    id: "P006",
    name: "增额终身寿",
    type: "保险",
    risk: "R2",
    horizonMonths: 120,
    liquidity: "极低",
    assetClass: "insurance",
    role: "长期储蓄/保障",
    drawdownLevel: "低",
    fee: "中",
    volatility: 0.002,
    maxDrawdownHist: 0,
    benchmark: "预定利率 2.5%",
    fees: "初年费用较高 · 详见保险条款",
    openFrequency: "犹豫期后长期锁定 · 退保按现金价值",
    inceptionDate: "2023-01-01",
    salesStatus: "在售 · 需完成保险需求分析",
    audienceTags: ["长期储蓄", "传承规划"],
    docExcerpts: {
      investScope: "本产品为增额终身寿险，保额按年递增，现金价值按合同约定演进。",
      riskDisclosure: "持有早期现金价值可能低于已交保费，提前退保将损失部分本金，适合长期不动用的资金。",
    },
    docSources: ["保险条款-现金价值", "保险条款-退保风险"],
  },
];

const prohibitedPhrases = ["保本", "稳赚", "一定收益", "无风险", "刚性兑付", "guaranteed return"];

// 业绩归因演示数据（Brinson 简化框架，纯演示）：按产品 × 区间
const attributionData = {
  P001: {
    "3M": { rows: [
      { label: "票息收益", value: 0.0055, note: "底仓债券持有收益", drill: "组合以高等级信用债与金融债为主，票息是最稳定的收益来源。" },
      { label: "久期/利率", value: 0.001, note: "利率下行小幅贡献资本利得", drill: "区间内 1 年期利率下行约 8bp，短久期策略下资本利得有限。" },
      { label: "信用利差", value: 0.0004, note: "利差总体稳定", drill: "持仓以 AAA 为主，利差变动对净值影响很小。" },
      { label: "费用", value: -0.0008, note: "管理费+托管费", drill: "费率合计约 0.32%/年，按日计提。" },
    ], benchmark: 0.0055, brinson: { allocation: 0.0004, selection: 0.0003, interaction: -0.0001 } },
    "1Y": { rows: [
      { label: "票息收益", value: 0.023, note: "全年票息主贡献", drill: "全年票息贡献稳定，是产品收益主体。" },
      { label: "久期/利率", value: 0.0028, note: "利率中枢下移", drill: "全年利率中枢下移带来资本利得。" },
      { label: "信用利差", value: 0.0012, note: "利差小幅收窄", drill: "优质城投与金融债利差收窄贡献正收益。" },
      { label: "费用", value: -0.003, note: "全年费率", drill: "费率合计约 0.32%/年。" },
    ], benchmark: 0.022, brinson: { allocation: 0.0012, selection: 0.001, interaction: -0.0002 } },
  },
  P002: {
    "3M": { rows: [
      { label: "票息收益", value: 0.0082, note: "底仓债券持有收益", drill: "80% 以上仓位为中高等级信用债，票息是稳定器。" },
      { label: "久期/利率", value: 0.0031, note: "利率下行资本利得", drill: "组合久期约 2.1 年，区间利率下行带来正贡献。" },
      { label: "信用利差", value: -0.0012, note: "利差走阔小幅拖累", drill: "部分产业债利差走阔，拖累约 12bp，属正常波动范围。" },
      { label: "权益增强", value: -0.0045, note: "可转债+股票仓位回撤", drill: "权益仓位约 12%，区间股市回调拖累 45bp——这是本区间跑输纯债基金的主因，也是未来弹性来源。" },
      { label: "费用", value: -0.0015, note: "管理费+托管费", drill: "费率合计约 0.62%/年，按日计提。" },
    ], benchmark: 0.0028, brinson: { allocation: 0.0009, selection: 0.0006, interaction: -0.0002 } },
    "1Y": { rows: [
      { label: "票息收益", value: 0.033, note: "全年票息主贡献", drill: "票息贡献全年收益的主体部分。" },
      { label: "久期/利率", value: 0.0085, note: "利率中枢下移", drill: "拉长久期策略在利率下行周期贡献显著。" },
      { label: "信用利差", value: 0.0024, note: "利差收窄正贡献", drill: "全年看信用利差整体收窄。" },
      { label: "权益增强", value: 0.0062, note: "全年正贡献", drill: "尽管季度间有回撤，全年权益增强仍贡献 +62bp。" },
      { label: "费用", value: -0.006, note: "全年费率", drill: "费率合计约 0.62%/年。" },
    ], benchmark: 0.036, brinson: { allocation: 0.0045, selection: 0.0042, interaction: -0.0006 } },
  },
  P003: {
    "3M": { rows: [
      { label: "市场β", value: -0.021, note: "大盘回调拖累", drill: "区间宽基指数下跌约 2.5%，指数基金被动承受市场β。" },
      { label: "红利风格", value: 0.012, note: "低波/红利风格跑赢", drill: "防御性风格在回调市道中走强，风格贡献 +1.2%。" },
      { label: "股息收益", value: 0.008, note: "成分股分红", drill: "成分股股息率约 5.2%，季度分红贡献稳定。" },
      { label: "跟踪误差", value: -0.0005, note: "复制偏差", drill: "完全复制策略，跟踪误差控制在 0.5% 以内。" },
      { label: "费用", value: -0.0013, note: "管理费", drill: "费率 0.5%/年，低于主动权益基金。" },
    ], benchmark: -0.0035, brinson: { allocation: 0.008, selection: 0, interaction: 0 } },
    "1Y": { rows: [
      { label: "市场β", value: 0.045, note: "全年市场上行", drill: "全年市场整体上行，β贡献主体收益。" },
      { label: "红利风格", value: 0.028, note: "风格持续占优", drill: "低利率环境下高股息资产持续获得资金青睐。" },
      { label: "股息收益", value: 0.031, note: "全年分红", drill: "全年股息再投资贡献稳定。" },
      { label: "跟踪误差", value: -0.0012, note: "复制偏差", drill: "全年跟踪误差在目标范围内。" },
      { label: "费用", value: -0.005, note: "全年费率", drill: "费率 0.5%/年。" },
    ], benchmark: 0.099, brinson: { allocation: 0.0, selection: -0.0012, interaction: 0 } },
  },
  P004: {
    "3M": { rows: [
      { label: "市场β", value: -0.032, note: "成长板块回调", drill: "科技成长板块区间回调幅度大于宽基指数。" },
      { label: "行业配置", value: -0.018, note: "超配半导体拖累", drill: "半导体超配约 12pct，区间该行业跌幅领先，配置效应为负。" },
      { label: "个股选择", value: 0.009, note: "选股正贡献", drill: "重仓股相对行业指数超额 +0.9%，选股能力体现。" },
      { label: "仓位择时", value: -0.004, note: "高仓位承受回调", drill: "区间仓位维持 90% 以上，未做防御性减仓。" },
      { label: "费用", value: -0.0038, note: "管理费较高", drill: "费率合计约 1.5%/年。" },
    ], benchmark: -0.041, brinson: { allocation: -0.018, selection: 0.009, interaction: -0.002 } },
    "1Y": { rows: [
      { label: "市场β", value: 0.06, note: "全年成长风格占优", drill: "全年看成长风格贡献主体收益。" },
      { label: "行业配置", value: 0.035, note: "AI/算力链贡献", drill: "超配算力产业链全年贡献显著。" },
      { label: "个股选择", value: 0.022, note: "选股超额", drill: "重仓股全年超额明显。" },
      { label: "仓位择时", value: -0.011, note: "择时负贡献", drill: "高波动阶段未降仓，择时效应为负。" },
      { label: "费用", value: -0.015, note: "全年费率", drill: "费率合计约 1.5%/年。" },
    ], benchmark: 0.082, brinson: { allocation: 0.035, selection: 0.022, interaction: -0.005 } },
  },
  P005: {
    "3M": { rows: [
      { label: "金价变动", value: 0.026, note: "避险需求推升金价", drill: "地缘不确定性与实际利率下行推升金价，是收益主因。" },
      { label: "汇率因素", value: 0.003, note: "人民币计价折算", drill: "国内金价含汇率折算，区间汇率小幅贡献。" },
      { label: "跟踪误差", value: -0.0006, note: "复制偏差", drill: "跟踪上金所现货合约，误差很小。" },
      { label: "费用", value: -0.0013, note: "管理费", drill: "费率 0.5%/年。" },
    ], benchmark: 0.028, brinson: { allocation: 0, selection: -0.0006, interaction: 0 } },
    "1Y": { rows: [
      { label: "金价变动", value: 0.112, note: "全年金价强势", drill: "全年金价上行是收益绝对主体。" },
      { label: "汇率因素", value: 0.008, note: "汇率折算贡献", drill: "全年汇率因素小幅正贡献。" },
      { label: "跟踪误差", value: -0.0015, note: "复制偏差", drill: "全年跟踪误差控制良好。" },
      { label: "费用", value: -0.005, note: "全年费率", drill: "费率 0.5%/年。" },
    ], benchmark: 0.116, brinson: { allocation: 0, selection: -0.0015, interaction: 0 } },
  },
};

// 合规话术库：必含句式（白名单）+ 建议替换
const complianceLibrary = {
  mandatory: {
    净值型: "本产品为净值型产品，净值随市场波动，过往业绩不代表未来表现。",
    保险: "保险产品早期退保可能损失部分本金，请确认长期资金安排与保障需求。",
    首购: "您是首次购买该类产品，需完成风险确认与录音录像（双录）流程。",
  },
  replacements: {
    "保本": "本金波动相对较小（不构成保本承诺）",
    "稳赚": "历史波动较低（不代表未来收益）",
    "无风险": "风险相对较低",
  },
};

// 客群级产品加载建议（数据口径对齐 tableau_data/generated_full/06_segment_snapshot.csv）
const segmentSnapshots = [
  { branch: "上海分行", risk: "R2", customers: 160, aum: 180000000, shortfallAsset: "固收/理财", shortfallAmount: 27000000, cashOverweight: 27000000, loadProducts: ["P001"], expectedUplift: 16000000, enablement: "理财到期承接演练 + 净值型话术培训" },
  { branch: "上海分行", risk: "R3", customers: 420, aum: 420000000, shortfallAsset: "固收+", shortfallAmount: 47880000, cashOverweight: 75600000, loadProducts: ["P002", "P001"], expectedUplift: 45000000, enablement: "固收+产品培训包 + 活期沉淀盘活专项" },
  { branch: "上海分行", risk: "R4", customers: 110, aum: 150000000, shortfallAsset: "权益基金/ETF", shortfallAmount: 21000000, cashOverweight: 16500000, loadProducts: ["P003", "P004"], expectedUplift: 12000000, enablement: "分批建仓策略培训 + 回撤预期管理" },
  { branch: "深圳分行", risk: "R2", customers: 130, aum: 140000000, shortfallAsset: "固收/理财", shortfallAmount: 18000000, cashOverweight: 21000000, loadProducts: ["P001"], expectedUplift: 10000000, enablement: "存款分流承接话术包" },
  { branch: "深圳分行", risk: "R3", customers: 350, aum: 360000000, shortfallAsset: "固收+", shortfallAmount: 41000000, cashOverweight: 54000000, loadProducts: ["P002", "P005"], expectedUplift: 26000000, enablement: "固收+专题直播 + 黄金分散配置话术" },
  { branch: "深圳分行", risk: "R4", customers: 120, aum: 150000000, shortfallAsset: "权益基金/ETF", shortfallAmount: 32000000, cashOverweight: 12000000, loadProducts: ["P003", "P004"], expectedUplift: 18000000, enablement: "核心-卫星组合培训" },
  { branch: "杭州分行", risk: "R2", customers: 140, aum: 120000000, shortfallAsset: "固收/理财", shortfallAmount: 15000000, cashOverweight: 18000000, loadProducts: ["P001"], expectedUplift: 9000000, enablement: "到期提醒 SOP 落地辅导" },
  { branch: "杭州分行", risk: "R3", customers: 300, aum: 290000000, shortfallAsset: "权益基金/ETF", shortfallAmount: 26000000, cashOverweight: 43500000, loadProducts: ["P003", "P002"], expectedUplift: 15000000, enablement: "低波权益策略培训 + 定投工具推广" },
  { branch: "杭州分行", risk: "R4", customers: 90, aum: 110000000, shortfallAsset: "权益基金/ETF", shortfallAmount: 17000000, cashOverweight: 9900000, loadProducts: ["P004", "P003"], expectedUplift: 9500000, enablement: "高波动产品适当性专项培训" },
];

function fmtMoney(value) {
  if (value >= 100000000) return `¥${(value / 100000000).toFixed(2)} 亿`;
  if (value >= 10000) return `¥${(value / 10000).toFixed(0)} 万`;
  return `¥${value.toLocaleString("zh-CN")}`;
}

function fmtPct(value, digits = 0) {
  return `${(value * 100).toFixed(digits)}%`;
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function assetLabel(key) {
  if (key === "insurance") return "长期保障/储蓄";
  return ASSETS.find((asset) => asset.key === key)?.label || key;
}

// 市场观点映射：让观点变化对模板和缺口变化更可见
function applyMarketViewAdjustments(template, notes = null) {
  const t = { ...template };
  const push = (text) => {
    if (Array.isArray(notes)) notes.push(text);
  };

  if (state.marketViews.cash === "积极") {
    t.cash += 0.03;
    t.fixedPlus -= 0.02;
    t.equity -= 0.01;
    push("现金积极 → 现金 +3pct");
  } else if (state.marketViews.cash === "谨慎") {
    t.cash -= 0.03;
    t.fixedIncome += 0.02;
    t.fixedPlus += 0.01;
    push("现金谨慎 → 现金 -3pct");
  }

  if (state.marketViews.fixedIncome === "积极") {
    t.fixedIncome += 0.04;
    t.cash -= 0.02;
    t.fixedPlus -= 0.01;
    t.equity -= 0.01;
    push("固收积极 → 固收 +4pct");
  } else if (state.marketViews.fixedIncome === "谨慎") {
    t.fixedIncome -= 0.04;
    t.fixedPlus += 0.02;
    t.equity += 0.02;
    push("固收谨慎 → 固收 -4pct");
  }

  if (state.marketViews.fixedPlus === "积极") {
    t.fixedPlus += 0.05;
    t.cash -= 0.03;
    t.fixedIncome -= 0.02;
    push("固收+积极 → 固收+ +5pct");
  } else if (state.marketViews.fixedPlus === "谨慎") {
    t.fixedPlus -= 0.05;
    t.fixedIncome += 0.03;
    t.cash += 0.02;
    push("固收+谨慎 → 固收+ -5pct");
  }

  if (state.marketViews.equity === "积极") {
    t.equity += 0.05;
    t.fixedIncome -= 0.03;
    t.cash -= 0.02;
    push("权益积极 → 权益 +5pct");
  } else if (state.marketViews.equity === "谨慎") {
    t.equity -= 0.05;
    t.fixedIncome += 0.03;
    t.cash += 0.02;
    push("权益谨慎 → 权益 -5pct");
  }

  if (state.marketViews.gold === "积极") {
    t.gold += 0.03;
    t.cash -= 0.02;
    t.fixedIncome -= 0.01;
    push("黄金积极 → 黄金 +3pct");
  } else if (state.marketViews.gold === "谨慎") {
    t.gold -= 0.03;
    t.fixedIncome += 0.02;
    t.cash += 0.01;
    push("黄金谨慎 → 黄金 -3pct");
  }

  return t;
}

function getTemplate(risk = state.risk) {
  const template = applyMarketViewAdjustments({ ...baseTemplates[risk] });
  return normalizeTemplate(template);
}

function normalizeTemplate(template) {
  const clean = {};
  let total = 0;
  ASSETS.forEach(({ key }) => {
    clean[key] = clamp(template[key], 0, 0.8);
    total += clean[key];
  });
  ASSETS.forEach(({ key }) => {
    clean[key] = clean[key] / total;
  });
  return clean;
}

// ===================== 客户画像引擎 =====================

function daysBetween(dateStr) {
  return Math.round((new Date(dateStr) - AS_OF) / 86400000);
}

function kycStatus(customer) {
  const daysLeft = daysBetween(customer.kyc.validUntil);
  if (daysLeft < 0) return { state: "expired", daysLeft, label: `已过期 ${-daysLeft} 天` };
  if (daysLeft <= 30) return { state: "expiring", daysLeft, label: `${daysLeft} 天后到期` };
  return { state: "valid", daysLeft, label: `有效（余 ${daysLeft} 天）` };
}

function riskRejectionCount(customerId) {
  return state.feedback.filter((item) => item.customerId === customerId && item.action === "rejected" && item.reason === "风险过高").length;
}

// 可解释标签：每个标签都带生成规则，页面可展示
function deriveTags(customer) {
  const tags = [];
  const kyc = kycStatus(customer);
  if (customer.behavior.panicRedeemed || riskRejectionCount(customer.id) >= 2) {
    tags.push({ label: "波动敏感", rule: customer.behavior.panicRedeemed ? "历史大跌期间恐慌赎回" : "“风险过高”拒绝反馈 ≥2 次", tone: "amber" });
  }
  if (customer.behavior.avgHoldingMonths < 12) {
    tags.push({ label: "短持有期", rule: `平均持有期 ${customer.behavior.avgHoldingMonths} 个月 < 12 个月`, tone: "blue" });
  }
  if (customer.behavior.chaseIndex > 0.6) {
    tags.push({ label: "追涨倾向", rule: `追涨杀跌指数 ${customer.behavior.chaseIndex} > 0.6，话术自动附加分批建议`, tone: "amber" });
  }
  if (customer.behavior.hasSIP) {
    tags.push({ label: "定投习惯", rule: "存在有效定投计划", tone: "green" });
  }
  if ((customer.portfolio.cash || 0) > (baseTemplates[customer.risk]?.cash || 0.1) + 0.1) {
    tags.push({ label: "现金沉淀", rule: "现金占比超过目标 +10pct", tone: "teal" });
  }
  if (kyc.state === "expired") {
    tags.push({ label: "测评已过期", rule: `风险测评有效期至 ${customer.kyc.validUntil}，已过期，触发全产品拦截`, tone: "red" });
  } else if (kyc.state === "expiring") {
    tags.push({ label: "测评临期", rule: `风险测评 ${kyc.daysLeft} 天后到期，建议提前重测`, tone: "amber" });
  }
  return tags;
}

function hasTag(customer, label) {
  return deriveTags(customer).some((tag) => tag.label === label);
}

// 风险预算：基准（按风险等级）× 行为修正
function deriveRiskBudget(customer) {
  const base = RISK_BUDGET_BASE[customer.risk];
  let factor = 1;
  const notes = [`基准：${customer.risk} 波动预算 ${fmtPct(base.maxVol, 1)} / 回撤预算 ${fmtPct(base.maxDrawdown, 1)}`];
  if (hasTag(customer, "波动敏感")) {
    factor *= 0.65;
    notes.push("命中“波动敏感”标签：预算 ×0.65");
  }
  return {
    maxVol: base.maxVol * factor,
    maxDrawdown: base.maxDrawdown * factor,
    factor,
    notes,
  };
}

function portfolioVol(weights) {
  return ASSETS.reduce((sum, { key }) => sum + (weights[key] || 0) * ASSET_VOL[key], 0);
}

function portfolioStress(weights) {
  return ASSETS.reduce((sum, { key }) => sum + (weights[key] || 0) * ASSET_STRESS[key], 0);
}

// 目标配置引擎：f(风险等级, 投资期限, 流动性, 市场观点, 风险预算)，输出可解释调整轨迹
function getTargetAllocation(customer) {
  const trace = [];
  let t = { ...baseTemplates[customer.risk] };
  trace.push(`基准：${customer.risk} 分层模板`);

  if (customer.horizonYears < 2) {
    t.equity = Math.max(0, t.equity - 0.05);
    t.cash += 0.05;
    trace.push(`期限 ${customer.horizonYears} 年 < 2 年：权益 -5pct、现金 +5pct`);
  } else if (customer.horizonYears >= 5) {
    t.equity += 0.05;
    t.fixedIncome = Math.max(0, t.fixedIncome - 0.05);
    trace.push(`期限 ${customer.horizonYears} 年 ≥5 年：权益 +5pct、固收 -5pct`);
  } else {
    trace.push(`期限 ${customer.horizonYears} 年：无调整`);
  }

  if (customer.liquidityNeed === "高" && t.cash < 0.2) {
    const shift = 0.2 - t.cash;
    t.fixedIncome = Math.max(0, t.fixedIncome - shift);
    t.cash = 0.2;
    trace.push(`流动性需求高：现金下限提至 20%（固收 -${fmtPct(shift)}）`);
  } else {
    trace.push(`流动性需求${customer.liquidityNeed}：无调整`);
  }

  const viewNotes = [];
  t = applyMarketViewAdjustments(t, viewNotes);
  trace.push(viewNotes.length ? `市场观点：${viewNotes.join("；")}` : "市场观点：无调整");

  let weights = normalizeTemplate(t);

  const budget = deriveRiskBudget(customer);
  let vol = portfolioVol(weights);
  const equityBefore = weights.equity;
  let guard = 0;
  while (vol > budget.maxVol && weights.equity > 0.02 && guard < 30) {
    weights.equity -= 0.01;
    weights.fixedIncome += 0.01;
    vol = portfolioVol(weights);
    guard += 1;
  }
  if (guard > 0) {
    trace.push(`风险预算 ${fmtPct(budget.maxVol, 1)} 约束：权益 ${fmtPct(equityBefore)} → ${fmtPct(weights.equity)}，固收相应上调`);
  } else {
    trace.push(`风险预算校验：预估波动 ${fmtPct(vol, 1)} ≤ 预算 ${fmtPct(budget.maxVol, 1)}，通过`);
  }

  return { weights, trace, budget, vol, stress: portfolioStress(weights) };
}

// 调仓方案：缺口 → 资金来源（到期承接优先）→ 分批动作
function buildRebalancePlan(customer) {
  const gaps = portfolioGaps(customer).filter((item) => item.gap > 0.015).sort((a, b) => b.gapAmount - a.gapAmount);
  const totalNeed = gaps.reduce((sum, item) => sum + item.gapAmount, 0);
  const target = getTargetAllocation(customer).weights;
  const fundingSources = [];
  let remaining = totalNeed;

  if (customer.maturityAmount > 0 && customer.maturityDays <= 45 && remaining > 0) {
    const take = Math.min(customer.maturityAmount, remaining);
    fundingSources.push({ source: `到期产品承接（${customer.maturityDays} 天后到期 ${fmtMoney(customer.maturityAmount)}）`, amount: take });
    remaining -= take;
  }
  const cashFloor = Math.max(target.cash, 0.1);
  const cashExcess = Math.max(0, (customer.portfolio.cash - cashFloor)) * customer.aum;
  if (remaining > 0 && cashExcess > 0) {
    const take = Math.min(cashExcess, remaining);
    fundingSources.push({ source: `活期/现金沉淀调降（保留 ${fmtPct(cashFloor)} 现金底线）`, amount: take });
    remaining -= take;
  }
  if (remaining > 1000) {
    fundingSources.push({ source: "分期转入 / 他行资金回流（需客户确认）", amount: remaining });
  }

  const actions = gaps.map((item) => {
    let batches = 1;
    let note = "";
    if (item.key === "equity") {
      batches = hasTag(customer, "追涨倾向") || hasTag(customer, "波动敏感") ? 3 : 2;
      note = hasTag(customer, "追涨倾向") ? "客户有追涨标签，建议定投/分批建仓" : hasTag(customer, "波动敏感") ? "客户波动敏感，小步分批降低体验风险" : "分批买入控制建仓成本";
    } else if (item.key === "gold") {
      batches = 2;
      note = "小比例分散配置，避免单点择时";
    } else {
      note = "可一次性配置，优先承接到期资金";
    }
    return { asset: item.key, label: item.label, direction: "买入", amount: item.gapAmount, batches, note };
  });

  const overweights = portfolioGaps(customer).filter((item) => item.gap < -0.05);
  overweights.forEach((item) => {
    if (item.key !== "cash") {
      actions.push({ asset: item.key, label: item.label, direction: "减持", amount: Math.abs(item.gap) * customer.aum, batches: 1, note: "超配资产逐步调降，优先到期自然承接" });
    }
  });

  const constraints = [
    "单一产品建议金额不超过可投资资产 20%（集中度上限）",
    `不突破 ${customer.risk} 风险等级与风险预算`,
    `调整后现金不低于 ${fmtPct(cashFloor)}`,
  ];

  return { gaps, totalNeed, fundingSources, actions, constraints };
}

function filteredCustomers() {
  return customers.filter((customer) => {
    const branchOk = state.branch === "全部" || customer.branch === state.branch;
    return branchOk && customer.risk === state.risk;
  });
}

function selectedCustomer() {
  return customers.find((customer) => customer.id === state.selectedCustomerId) || customers[0];
}

function selectedProduct() {
  return products.find((product) => product.id === state.selectedProductId) || products[1];
}

function portfolioGaps(customer = selectedCustomer()) {
  const target = getTargetAllocation(customer).weights;
  return ASSETS.map(({ key, label }) => {
    const current = customer.portfolio[key] || 0;
    const gap = target[key] - current;
    return {
      key,
      label,
      current,
      target: target[key],
      gap,
      gapAmount: Math.max(gap, 0) * customer.aum,
    };
  });
}

function positiveGapAssets(customer = selectedCustomer()) {
  return portfolioGaps(customer)
    .filter((item) => item.gap > 0.015)
    .map((item) => item.key);
}

function customerPriority(customer) {
  const totalGap = portfolioGaps(customer).reduce((sum, item) => sum + item.gapAmount, 0);
  const contactScore = clamp(customer.lastContactDays / 120, 0, 1) * 100000;
  return totalGap * 0.5 + customer.maturityAmount * 0.3 + contactScore * 0.2;
}

// 产品类型 → KYC 品类映射（用于首购判断）
const KYC_CATEGORY = { "银行理财": "理财", "固收+基金": "固收+", "权益 ETF": "权益", "权益基金": "权益", "商品 ETF": "黄金", "保险": "保险" };
const RULE_VERSION = "v0.9";

// 适当性校验：规则清单驱动，输出带痕迹（规则 ID / 版本 / 结果）
function fitProduct(customer, product) {
  const reasons = [];
  const cautions = [];
  const blocks = [];
  const trace = [];
  let score = 0;
  const gaps = positiveGapAssets(customer);
  const kyc = kycStatus(customer);

  function mark(ruleId, result, detail) {
    trace.push({ ruleId, version: RULE_VERSION, result, detail });
  }

  // S-02 风险测评有效期（全局硬拦截）
  if (kyc.state === "expired") {
    blocks.push(`风险测评已过期（${customer.kyc.validUntil}），需先邀约重测`);
    mark("S-02", "blocked", `测评有效期至 ${customer.kyc.validUntil}，${kyc.label}`);
  } else {
    mark("S-02", "pass", `测评${kyc.label}`);
  }

  // S-01 风险等级
  if (RISK_SCORE[product.risk] > RISK_SCORE[customer.risk]) {
    blocks.push("产品风险等级高于客户风险承受能力");
    mark("S-01", "blocked", `产品 ${product.risk} > 客户 ${customer.risk}`);
  } else if (product.risk === customer.risk) {
    score += 25;
    reasons.push("产品风险等级与客户匹配");
    mark("S-01", "pass", `产品 ${product.risk} = 客户 ${customer.risk}，+25`);
  } else {
    score += 15;
    reasons.push("产品风险等级低于客户风险承受能力");
    mark("S-01", "pass", `产品 ${product.risk} < 客户 ${customer.risk}，+15`);
  }

  // B-01 配置缺口
  if (gaps.includes(product.assetClass)) {
    score += 40;
    reasons.push(`对应客户 ${assetLabel(product.assetClass)} 配置缺口`);
    mark("B-01", "pass", `命中正向缺口 ${assetLabel(product.assetClass)}，+40`);
  } else if (product.assetClass === "insurance") {
    cautions.push("保险产品不直接对应本次资产配置缺口");
    mark("B-01", "caution", "保险不计入五大类配置缺口");
  } else {
    cautions.push("不是当前最大配置缺口资产类别");
    mark("B-01", "caution", "未命中正向缺口，+0");
  }

  // C-01 期限
  if (product.horizonMonths <= customer.horizonYears * 12) {
    score += 15;
    reasons.push("产品建议持有期与客户投资期限匹配");
    mark("C-01", "pass", `产品 ${product.horizonMonths} 个月 ≤ 客户 ${customer.horizonYears * 12} 个月，+15`);
  } else {
    cautions.push("产品期限长于客户当前投资期限");
    score -= 20;
    mark("C-01", "caution", `产品 ${product.horizonMonths} 个月 > 客户 ${customer.horizonYears * 12} 个月，-20`);
  }

  // 流动性
  if (LIQUIDITY_SCORE[product.liquidity] >= LIQUIDITY_SCORE[customer.liquidityNeed]) {
    score += 10;
    reasons.push("产品流动性满足客户需求");
    mark("C-05", "pass", `产品流动性${product.liquidity} ≥ 客户需求${customer.liquidityNeed}，+10`);
  } else {
    cautions.push("产品流动性弱于客户需求");
    score -= product.type === "保险" ? 30 : 15;
    mark("C-05", "caution", `产品流动性${product.liquidity} < 客户需求${customer.liquidityNeed}，${product.type === "保险" ? "-30" : "-15"}`);
  }

  // 回撤特征 + C-03 波动敏感标签
  if (product.drawdownLevel === "低" || product.drawdownLevel === "中") {
    score += 10;
    mark("C-03", "pass", `回撤等级${product.drawdownLevel}，+10`);
  } else if (hasTag(customer, "波动敏感")) {
    score -= 10;
    cautions.push("客户有“波动敏感”标签，高回撤产品需重点提示并控制比例");
    mark("C-03", "caution", `回撤等级${product.drawdownLevel} × 波动敏感标签，-10`);
  } else if (customer.risk !== "R4") {
    cautions.push("产品净值波动需要重点提示");
    mark("C-03", "caution", `回撤等级${product.drawdownLevel}，需风险提示`);
  } else {
    mark("C-03", "pass", `R4 客户可接受${product.drawdownLevel}回撤`);
  }

  // C-02 首次购买品类（双录提示）
  const category = KYC_CATEGORY[product.type];
  const firstPurchase = category && !customer.kyc.experiencedTypes.includes(category);
  if (firstPurchase) {
    cautions.push(`客户首次购买“${category}”类产品，需风险确认与双录流程`);
    mark("C-02", "caution", `KYC 已投品类不含“${category}”，触发双录提示`);
  } else {
    mark("C-02", "pass", `客户已有“${category || "-"}”品类投资经验`);
  }

  // C-04 测评临期
  if (kyc.state === "expiring") {
    cautions.push(`风险测评 ${kyc.daysLeft} 天后到期，建议同步安排重测`);
    mark("C-04", "caution", `测评${kyc.label}`);
  }

  // S-03 保险专项
  if (product.type === "保险") {
    cautions.push("保险产品需额外说明长期锁定、现金价值和退保风险");
    if (customer.liquidityNeed !== "低") {
      blocks.push("长期锁定与客户流动性需求不匹配");
      mark("S-03", "blocked", `保险长期锁定 × 客户流动性需求${customer.liquidityNeed}`);
    } else {
      mark("S-03", "pass", "客户流动性需求低，可评估长期锁定产品");
    }
  }

  // B-02 客户经理反馈回流
  const rejectedSame = state.feedback.some((item) => item.customerId === customer.id && item.action === "rejected" && products.find((p) => p.id === item.productId)?.assetClass === product.assetClass);
  const acceptedSame = state.feedback.some((item) => item.customerId === customer.id && item.action === "accepted" && products.find((p) => p.id === item.productId)?.assetClass === product.assetClass);
  if (rejectedSame) {
    score -= 10;
    cautions.push("该客户历史拒绝过同类资产产品（反馈回流 -10）");
    mark("B-02", "caution", "同类资产历史拒绝记录，-10");
  } else if (acceptedSame) {
    score += 5;
    reasons.push("客户历史采纳过同类资产产品（反馈回流 +5）");
    mark("B-02", "pass", "同类资产历史采纳记录，+5");
  }

  // S-04 集中度：建议金额按 20% AUM 降额
  const gapItem = portfolioGaps(customer).find((item) => item.key === product.assetClass);
  let suggestedAmount = gapItem ? gapItem.gapAmount : 0;
  const cap = customer.aum * 0.2;
  let capped = false;
  if (suggestedAmount > cap) {
    suggestedAmount = cap;
    capped = true;
    cautions.push(`建议金额已按集中度上限 20% 降额至 ${fmtMoney(cap)}`);
    mark("S-04", "caution", `缺口金额超过 AUM 20%，降额至 ${fmtMoney(cap)}`);
  } else {
    mark("S-04", "pass", `建议金额 ${fmtMoney(suggestedAmount)} 在集中度上限内`);
  }

  const boundedScore = clamp(score, 0, 100);
  let status = "candidate";
  if (blocks.length) status = "blocked";
  else if (boundedScore < 62 || cautions.length) status = "caution";

  return { product, score: boundedScore, reasons, cautions, blocks, status, trace, suggestedAmount, capped, firstPurchase };
}

function productFits(customer = selectedCustomer()) {
  return products.map((product) => fitProduct(customer, product)).sort((a, b) => b.score - a.score);
}

function generateTriggers(customer = selectedCustomer()) {
  const gaps = portfolioGaps(customer);
  const triggers = [];
  const kyc = kycStatus(customer);
  const maxDeviation = Math.max(...gaps.map((item) => Math.abs(item.gap)));
  if (kyc.state === "expired") {
    triggers.push({ type: "测评过期", rule: "风险测评超过有效期", action: "邀约重测 + 暂停产品推荐" });
  } else if (kyc.state === "expiring") {
    triggers.push({ type: "测评临期", rule: "风险测评 30 天内到期", action: "生成重测邀约提醒" });
  }
  if (maxDeviation > 0.1) {
    triggers.push({ type: "配置偏离", rule: "任一资产类别偏离目标权重 >10%", action: "生成再平衡提醒" });
  }
  if (customer.maturityDays <= 15) {
    triggers.push({ type: "产品到期", rule: "产品到期前 15 天", action: "生成续接提醒" });
  }
  if (customer.drawdown <= -0.08) {
    triggers.push({ type: "市场波动", rule: "组合或权益类持仓回撤超过阈值", action: "生成投后安抚话术" });
  }
  if (!triggers.length) {
    triggers.push({ type: "持续跟踪", rule: "本周未触发强提醒", action: "保持月度配置跟踪" });
  }
  return triggers;
}

function aiInterpretation(product = selectedProduct(), customer = selectedCustomer()) {
  const gapLabels = positiveGapAssets(customer).map(assetLabel).join("、") || "暂无明显缺口";
  const base = {
    positioning: `${product.name} 可作为 ${customer.risk} 客户组合中的${product.role}部分，当前客户缺口集中在 ${gapLabels}。`,
    returnSource: product.type.includes("ETF")
      ? "主要来自标的资产价格变化、指数成分收益和组合再平衡。"
      : product.type === "保险"
        ? "主要来自合同约定的保障责任、现金价值演进和长期储蓄安排。"
        : "主要来自债券票息、久期管理、信用利差和少量增强资产贡献。",
    risks: product.type === "保险"
      ? ["长期锁定风险", "退保损失风险", "现金价值低于已交保费的阶段性风险"]
      : ["净值波动风险", "信用风险", "利率风险", "流动性风险"],
    suitable: `${customer.risk} 及以上、投资期限 ${Math.max(1, Math.ceil(product.horizonMonths / 12))} 年以上，并能接受产品风险特征的客户。`,
    notSuitable: product.type === "保险"
      ? "短期资金需求明确、无法接受长期锁定或未完成保险需求分析的客户。"
      : "只能接受本金不波动、短期随时支取或风险等级低于产品等级的客户。",
    advisorScript: `该产品可用于补充客户组合中的${assetLabel(product.assetClass)}配置，需要结合客户现有持仓、风险等级和流动性需求控制比例。`,
    customerScript: product.type === "保险"
      ? "这类产品更偏长期规划和保障安排，资金灵活性较低，配置前需要确认未来现金流和保障需求。"
      : "这类产品不是现金类工具，净值会有波动。它更适合作为组合中的一部分，不建议集中配置。",
    compliance: "不得承诺收益，不得替代客户适当性确认，客户触达前需完成人工复核。",
    sources: [
      `产品说明书摘要（受控知识库）：「${product.docExcerpts.investScope}」`,
      ...product.docSources,
    ],
  };
  return base;
}

function complianceHits(text) {
  return prohibitedPhrases.filter((phrase) => text.toLowerCase().includes(phrase.toLowerCase()));
}

// ===================== 场景化话术引擎 =====================
// 流程：受控摘要 + 客户变量注入 → 模板装配 → 必含句式 → 禁止词扫描 → 输出+来源标注

function generateScript(scenarioKey, customer = selectedCustomer(), product = selectedProduct()) {
  const gaps = portfolioGaps(customer).filter((item) => item.gap > 0.015).sort((a, b) => b.gapAmount - a.gapAmount);
  const mainGap = gaps[0];
  const fit = fitProduct(customer, product);
  const scenarioLabel = SCRIPT_SCENARIOS.find((s) => s.key === scenarioKey)?.label || scenarioKey;
  const mandatory = [];
  if (product.type === "保险") mandatory.push(complianceLibrary.mandatory.保险);
  else mandatory.push(complianceLibrary.mandatory.净值型);
  if (fit.firstPurchase) mandatory.push(complianceLibrary.mandatory.首购);

  const variables = [];
  let advisorText = "";
  let customerText = "";

  if (scenarioKey === "maturity") {
    variables.push(`到期金额 ${fmtMoney(customer.maturityAmount)}`, `到期天数 ${customer.maturityDays} 天`);
    advisorText = `${customer.name}有 ${fmtMoney(customer.maturityAmount)} 产品将于 ${customer.maturityDays} 天后到期，建议提前预约沟通承接方案：优先用 ${product.name} 承接（建议金额不超 ${fmtMoney(fit.suggestedAmount || customer.maturityAmount)}），对应客户 ${mainGap ? mainGap.label : "组合分散"} 缺口，避免到期资金回落活期。`;
    customerText = `您有一笔 ${fmtMoney(customer.maturityAmount)} 的产品 ${customer.maturityDays} 天后到期。结合您 ${customer.risk} 的风险评估和 ${customer.horizonYears} 年的投资安排，我们建议到期后可以考虑用 ${product.name} 承接一部分，它属于${product.role}，${product.openFrequency}。`;
  } else if (scenarioKey === "drawdown") {
    variables.push(`当前回撤 ${fmtPct(customer.drawdown, 1)}`, `产品历史最大回撤 ${fmtPct(product.maxDrawdownHist, 1)}`);
    advisorText = `${customer.name}组合近期回撤 ${fmtPct(customer.drawdown, 1)}，建议主动触达安抚：先对齐客户风险预算（回撤预算 ${fmtPct(deriveRiskBudget(customer).maxDrawdown, 1)}），说明当前回撤仍在预算内；再结合持仓结构说明回撤主要来源，不建议此时恐慌赎回。${hasTag(customer, "追涨倾向") ? "客户有追涨标签，提醒勿在低点恢复后追高加仓。" : ""}`;
    customerText = `近期市场波动较大，您的组合回撤约 ${fmtPct(Math.abs(customer.drawdown), 1)}，仍在您风险评估对应的承受范围内。类似产品历史上也出现过阶段性回撤，短期波动不等于永久损失。建议我们约个时间把持仓结构梳理一遍，再决定是否需要调整。`;
  } else if (scenarioKey === "rebalance") {
    const over = portfolioGaps(customer).filter((item) => item.gap < -0.05);
    variables.push(`最大正向缺口 ${mainGap ? mainGap.label + " " + fmtPct(mainGap.gap) : "无"}`);
    advisorText = `${customer.name}组合偏离目标超阈值：${over.map((item) => `${item.label}超配 ${fmtPct(Math.abs(item.gap))}`).join("、") || "无明显超配"}；${gaps.map((item) => `${item.label}不足 ${fmtPct(item.gap)}`).join("、")}。建议按调仓方案分步再平衡，优先用到期资金自然承接，避免集中赎回。`;
    customerText = `根据您的目标配置，目前组合里${mainGap ? mainGap.label + "的比例还有提升空间" : "结构基本均衡"}。我们建议分批、小步地做再平衡，不需要一次性大调，这样既控制风险也降低择时压力。`;
  } else if (scenarioKey === "afterReject") {
    const lastReject = state.feedback.filter((item) => item.customerId === customer.id && item.action === "rejected").slice(-1)[0];
    const alternative = productFits(customer).find((f) => f.status === "candidate" && f.product.id !== product.id);
    variables.push(`拒绝原因 ${lastReject ? lastReject.reason : "未记录"}`);
    advisorText = `${customer.name}上次拒绝原因：${lastReject ? lastReject.reason + "（" + lastReject.comment + "）" : "未记录"}。建议不重复推同一产品，改为回应顾虑：${lastReject && lastReject.reason === "风险过高" ? `从更低波动的替代方案切入${alternative ? "，如 " + alternative.product.name : ""}，并明确回撤预期。` : "先了解客户真实资金安排再谈配置。"}`;
    customerText = `上次您提到的顾虑我们记下了。这次不是推同一个产品，而是想和您确认一下资金的使用计划，看看有没有更稳健、更匹配您需求的安排。`;
  } else {
    // firstTouch
    variables.push(`主缺口 ${mainGap ? mainGap.label + " " + fmtMoney(mainGap.gapAmount) : "无"}`, `未触达 ${customer.lastContactDays} 天`);
    advisorText = `${customer.name}已 ${customer.lastContactDays} 天未触达，诊断显示${mainGap ? `${mainGap.label}缺口约 ${fmtMoney(mainGap.gapAmount)}` : "配置基本均衡"}。建议以“配置体检”名义邀约，先展示诊断结果再引出 ${product.name}，建议金额不超 ${fmtMoney(fit.suggestedAmount || 0)}。${hasTag(customer, "波动敏感") ? "客户波动敏感，重点讲回撤控制而非收益弹性。" : ""}`;
    customerText = `最近帮您做了一次资产配置体检，您目前${mainGap ? mainGap.label + "的比例低于同类型客户的参考水平" : "整体结构比较均衡"}。如果您方便，想约个时间把体检报告给您过一遍，您听完再决定要不要调整。`;
  }

  const sources = [
    `产品说明书摘要：“${product.docExcerpts.riskDisclosure}”`,
    ...product.docSources,
    "合规话术库 v2026-06（必含句式 + 禁止词表）",
  ];
  const fullText = [advisorText, customerText, ...mandatory].join(" ");
  const hits = complianceHits(fullText);

  return { scenarioKey, scenarioLabel, advisorText, customerText, mandatory, variables, sources, hits, firstPurchase: fit.firstPurchase };
}

// 生成留痕：每次解读/话术生成写入审计日志，命中禁止词或首购场景转人工复核
let logSeq = 100;
function logAiGeneration(scenarioLabel, customer, product, hits, firstPurchase) {
  logSeq += 1;
  const now = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  const entry = {
    logId: `L${logSeq}`,
    time: `${pad(now.getMonth() + 1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}`,
    advisor: "当前演示用户",
    customerId: customer.id,
    productId: product.id,
    scenario: scenarioLabel,
    promptVersion: "v0.3",
    kbVersion: "2026-06",
    scanResult: hits.length ? "hit" : "pass",
    reviewStatus: hits.length || firstPurchase ? "pending-review" : "auto-pass",
    delivered: false,
  };
  state.aiAuditLog.unshift(entry);
  return entry;
}

// 今日待办：从规则与日志派生，不手工维护
function buildTodos() {
  const todos = [];
  customers.forEach((customer) => {
    const kyc = kycStatus(customer);
    if (kyc.state === "expired") todos.push({ type: "测评重测邀约", who: `${customer.id} ${customer.name}`, detail: `测评${kyc.label}，产品推荐已全部拦截`, page: "diagnosis", customerId: customer.id, tone: "red" });
    if (customer.maturityDays <= 15) todos.push({ type: "到期承接", who: `${customer.id} ${customer.name}`, detail: `${fmtMoney(customer.maturityAmount)} 于 ${customer.maturityDays} 天后到期`, page: "diagnosis", customerId: customer.id, tone: "amber" });
    const maxDev = Math.max(...portfolioGaps(customer).map((item) => Math.abs(item.gap)));
    if (maxDev > 0.1) todos.push({ type: "再平衡提醒", who: `${customer.id} ${customer.name}`, detail: `最大偏离 ${fmtPct(maxDev)} 超过 10% 阈值`, page: "diagnosis", customerId: customer.id, tone: "teal" });
    if (customer.drawdown <= -0.08) todos.push({ type: "回撤安抚", who: `${customer.id} ${customer.name}`, detail: `组合回撤 ${fmtPct(customer.drawdown, 1)}，建议主动触达`, page: "product", customerId: customer.id, tone: "amber" });
  });
  state.feedback.filter((item) => item.action === "pending").forEach((item) => {
    todos.push({ type: "反馈跟进", who: item.customerId, detail: item.comment, page: "governance", customerId: item.customerId, tone: "blue" });
  });
  state.aiAuditLog.filter((item) => item.reviewStatus === "pending-review").forEach((item) => {
    todos.push({ type: "话术复核", who: `${item.customerId} · ${item.scenario}`, detail: `${item.logId} 等待人工复核（${item.scanResult === "hit" ? "命中禁止词" : "首购/高风险场景"}）`, page: "governance", customerId: item.customerId, tone: "violet" });
  });
  return todos;
}

// ===================== 06 · 产品解读 Copilot（对话式 Demo） =====================

const CHAT_QUICK_QUESTIONS = [
  "这只产品最近为什么跌了？",
  "近 1 年业绩归因怎么看？",
  "适合当前客户吗？",
  "和稳健月月盈比哪个好？",
  "收益从哪里来？",
  "最大风险是什么？",
  "客户问会不会保本，怎么回答？",
  "帮我生成一段到期承接话术",
];

function escapeChatText(text) {
  return String(text).replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function fmtBp(value) {
  const pct = (value * 100).toFixed(2);
  return `${value >= 0 ? "+" : ""}${pct}%`;
}

function chatIntent(question) {
  const q = question.toLowerCase();
  if (["保本", "稳赚", "无风险", "一定收益"].some((w) => q.includes(w))) return "compliance";
  if (q.includes("话术") || q.includes("承接话")) return "script";
  if (q.includes("贡献") && (q.includes("为什么") || q.includes("怎么"))) return "drill";
  if (q.includes("归因") || q.includes("为什么跌") || q.includes("为什么涨") || q.includes("表现怎么")) return "attribution";
  if (q.includes("适合")) return "fit";
  if (q.includes("比哪个") || q.includes("对比") || q.includes("相比")) return "compare";
  if (q.includes("收益") && (q.includes("哪") || q.includes("来源"))) return "returnSource";
  if (q.includes("风险")) return "risk";
  return "fallback";
}

function chatAttributionCard(product, period) {
  const data = attributionData[product.id]?.[period];
  if (!data) return null;
  const total = data.rows.reduce((sum, row) => sum + row.value, 0);
  const excess = total - data.benchmark;
  const maxAbs = Math.max(...data.rows.map((row) => Math.abs(row.value)), 0.0001);
  const periodLabel = period === "1Y" ? "近 1 年" : "近 3 个月";
  const worst = [...data.rows].sort((a, b) => a.value - b.value)[0];
  const best = [...data.rows].sort((a, b) => b.value - a.value)[0];

  return `
    <p>${product.name} ${periodLabel}区间回报 <strong>${fmtBp(total)}</strong>，基准 ${fmtBp(data.benchmark)}，超额 <strong class="${excess >= 0 ? "delta positive" : "delta negative"}">${fmtBp(excess)}</strong>。主要正贡献来自${best.label}，主要拖累来自${worst.label}。</p>
    <div class="chat-toolbar">
      ${[["3M", "近 3 个月"], ["1Y", "近 1 年"]].map(([key, label]) => `<button class="button ${period === key ? "primary" : ""}" data-action="chat-ask" data-question="${key === "1Y" ? "近 1 年业绩归因怎么看？" : "这只产品最近为什么跌了？"}" type="button">${label}</button>`).join("")}
    </div>
    <div class="wf-list">
      ${data.rows.map((row) => `
        <button class="wf-row" data-action="chat-ask" data-question="${row.label}的贡献为什么是${row.value >= 0 ? "正" : "负"}的？" type="button" title="点击下钻追问">
          <span class="wf-label">${row.label}</span>
          <span class="wf-track"><span class="wf-fill ${row.value >= 0 ? "pos" : "neg"}" style="width:${clamp((Math.abs(row.value) / maxAbs) * 100, 4, 100)}%"></span></span>
          <span class="wf-value ${row.value >= 0 ? "delta positive" : "delta negative"}">${fmtBp(row.value)}</span>
        </button>
      `).join("")}
      <div class="wf-row wf-total">
        <span class="wf-label">区间总回报</span>
        <span class="wf-track"></span>
        <span class="wf-value ${total >= 0 ? "delta positive" : "delta negative"}">${fmtBp(total)}</span>
      </div>
    </div>
    <p class="chat-meta">Brinson 超额拆解：配置效应 ${fmtBp(data.brinson.allocation)} · 选券/选股效应 ${fmtBp(data.brinson.selection)} · 交互项 ${fmtBp(data.brinson.interaction)}。点击任意归因行可下钻追问。</p>
    <p class="chat-meta">演示数据 · 归因结果仅供内部分析，不构成业绩承诺。</p>
  `;
}

function buildChatAnswer(question, customer, product) {
  const intent = chatIntent(question);
  const kyc = kycStatus(customer);
  const baseSources = [`产品说明书摘要：「${product.docExcerpts.riskDisclosure}」`, ...product.docSources];

  if (intent === "attribution") {
    if (question.includes("1年") || question.includes("1 年")) state.chatPeriod = "1Y";
    else state.chatPeriod = "3M";
    if (product.assetClass === "insurance") {
      return { intent, intentLabel: "业绩归因", html: `<p>${product.name}为保险产品，无净值型业绩归因；其价值按合同约定的现金价值表演进，不随市场波动。建议关注退保现金价值曲线与长期锁定期。</p>`, sources: baseSources, hits: [] };
    }
    const card = chatAttributionCard(product, state.chatPeriod);
    return {
      intent, intentLabel: "业绩归因",
      html: card || `<p>暂无 ${product.name} 的归因数据。</p>`,
      sources: [`业绩归因引擎 v0.1（演示数据）· 区间 ${state.chatPeriod === "1Y" ? "近 1 年" : "近 3 个月"}`, `业绩比较基准：${product.benchmark}`, ...product.docSources],
      hits: [],
    };
  }

  if (intent === "drill") {
    const data = attributionData[product.id]?.[state.chatPeriod];
    const row = data?.rows.find((item) => question.includes(item.label));
    if (row) {
      const tagTip = hasTag(customer, "波动敏感") && row.value < 0 ? `<p class="chat-meta">提示：当前客户有“波动敏感”标签，沟通时建议侧重回撤控制与持有体验，而非短期收益。</p>` : "";
      return {
        intent, intentLabel: "归因下钻",
        html: `<p><strong>${row.label} ${fmtBp(row.value)}</strong>：${row.drill}</p>${tagTip}`,
        sources: [`业绩归因引擎 v0.1 · ${row.label}明细（演示数据）`],
        hits: [],
      };
    }
  }

  if (intent === "fit") {
    const fit = fitProduct(customer, product);
    const statusLabel = fit.status === "candidate" ? "可进入候选清单" : fit.status === "caution" ? "谨慎使用" : "自动拦截";
    const points = [...fit.blocks.map((b) => `⛔ ${b}`), ...fit.cautions.slice(0, 2).map((c) => `⚠ ${c}`), ...fit.reasons.slice(0, 2).map((r) => `✓ ${r}`)];
    return {
      intent, intentLabel: "适当性问答",
      html: `<p>${product.name} 对 ${customer.name}（${customer.risk}）的适配结果：<span class="pill ${fit.status === "candidate" ? "green" : fit.status === "caution" ? "amber" : "red"}">${statusLabel}</span>，评分 ${fit.score}。</p><ul class="chat-list">${points.map((p) => `<li>${p}</li>`).join("")}</ul><p class="chat-meta">完整校验痕迹（${fit.trace.length} 条规则）见 04 页状态展开。结果仅供参考，需人工适当性确认。</p>`,
      sources: [`适当性规则库 ${RULE_VERSION}（S/C/B 三类规则）`, ...baseSources],
      hits: [],
    };
  }

  if (intent === "compare") {
    const other = product.id === "P001" ? products.find((p) => p.id === "P002") : products.find((p) => p.id === "P001");
    const fitA = fitProduct(customer, product);
    const fitB = fitProduct(customer, other);
    const better = fitA.score >= fitB.score ? product : other;
    return {
      intent, intentLabel: "产品对比",
      html: `
        <div class="table-wrap"><table class="chat-table">
          <thead><tr><th>维度</th><th>${product.name}</th><th>${other.name}</th></tr></thead>
          <tbody>
            <tr><td>风险/回撤</td><td>${product.risk} · 历史回撤 ${fmtPct(product.maxDrawdownHist, 1)}</td><td>${other.risk} · ${fmtPct(other.maxDrawdownHist, 1)}</td></tr>
            <tr><td>波动率</td><td>${fmtPct(product.volatility, 1)}</td><td>${fmtPct(other.volatility, 1)}</td></tr>
            <tr><td>期限/流动性</td><td>${product.horizonMonths} 个月 · ${product.liquidity}</td><td>${other.horizonMonths} 个月 · ${other.liquidity}</td></tr>
            <tr><td>费率</td><td>${product.fees}</td><td>${other.fees}</td></tr>
            <tr><td>适配评分（当前客户）</td><td><strong>${fitA.score}</strong>（${fitA.status}）</td><td><strong>${fitB.score}</strong>（${fitB.status}）</td></tr>
          </tbody>
        </table></div>
        <p>结合 ${customer.name} 的缺口与风险预算，当前适配度更高的是<strong>${better.name}</strong>。没有“更好”只有“更匹配”：两者分属不同风险收益特征，不构成推荐结论。</p>`,
      sources: [`适当性规则库 ${RULE_VERSION}`, `产品池字段：${product.name} / ${other.name}`],
      hits: [],
    };
  }

  if (intent === "returnSource") {
    const interp = aiInterpretation(product, customer);
    return {
      intent, intentLabel: "收益来源",
      html: `<p>${interp.returnSource}</p><p class="chat-meta">投资范围（说明书摘要）：「${product.docExcerpts.investScope}」</p>`,
      sources: baseSources,
      hits: [],
    };
  }

  if (intent === "risk") {
    const interp = aiInterpretation(product, customer);
    return {
      intent, intentLabel: "风险揭示",
      html: `<p>主要风险：${interp.risks.join("、")}。</p><p class="chat-meta">风险揭示（说明书摘要）：「${product.docExcerpts.riskDisclosure}」</p><p class="chat-meta">${complianceLibrary.mandatory[product.type === "保险" ? "保险" : "净值型"]}</p>`,
      sources: baseSources,
      hits: [],
    };
  }

  if (intent === "compliance") {
    const hit = prohibitedPhrases.find((w) => question.includes(w)) || "保本";
    const replacement = complianceLibrary.replacements[hit] || "合规替代表述";
    return {
      intent, intentLabel: "禁止词拦截",
      html: `<p><span class="pill red">已拦截</span> “${hit}”属于禁止性表述，不能向客户承诺。</p><p>建议回答：“这只产品${replacement}，${complianceLibrary.mandatory.净值型}”</p><p class="chat-meta">本次提问命中禁止词，已记录并转入人工复核队列（见 05 页）。</p>`,
      sources: ["合规话术库 v2026-06（禁止词表 + 替换建议）"],
      hits: [hit],
    };
  }

  if (intent === "script") {
    if (kyc.state === "expired") {
      return { intent, intentLabel: "话术生成", html: `<p><span class="pill red">已拦截（S-02）</span> ${customer.name}风险测评已过期，不能生成产品触达话术，请先邀约重测。</p>`, sources: [`适当性规则库 ${RULE_VERSION} · S-02`], hits: [] };
    }
    const script = generateScript("maturity", customer, product);
    return {
      intent, intentLabel: "话术生成",
      html: `<p><strong>客户经理版：</strong>${script.advisorText}</p><p><strong>客户沟通版：</strong>${script.customerText}</p><p class="chat-meta">必含句式：${script.mandatory.join(" / ")}</p>`,
      sources: script.sources,
      hits: script.hits,
      firstPurchase: script.firstPurchase,
    };
  }

  return {
    intent: "fallback", intentLabel: "受控拒答",
    html: `<p>该问题超出受控知识库范围，为避免无依据回答，已记录待知识库补充。您可以试试左侧的快捷问题，或转人工产品专家支持。</p>`,
    sources: ["受控知识库 2026-06（未命中条目 → 拒答策略）"],
    hits: [],
  };
}

function askChat(question) {
  const text = String(question || "").trim();
  if (!text) return;
  state.chatMessages.push({ role: "user", html: escapeChatText(text) });
  state.chatMessages.push({ role: "bot", pending: true, html: "正在基于受控知识库生成…" });
  renderApp();
  setTimeout(() => {
    const customer = selectedCustomer();
    const product = selectedProduct();
    const answer = buildChatAnswer(text, customer, product);
    const entry = logAiGeneration(`Chatbot·${answer.intentLabel}`, customer, product, answer.hits, answer.firstPurchase || false);
    const pending = state.chatMessages.find((msg) => msg.pending);
    if (pending) {
      pending.pending = false;
      pending.html = answer.html;
      pending.meta = { intentLabel: answer.intentLabel, logId: entry.logId, scan: entry.scanResult, review: entry.reviewStatus };
    }
    state.chatEvidence = {
      question: text,
      intentLabel: answer.intentLabel,
      sources: answer.sources,
      scan: entry.scanResult,
      review: entry.reviewStatus,
      logId: entry.logId,
      time: entry.time,
    };
    renderApp();
  }, 450);
}

function chatBubble(msg) {
  if (msg.role === "user") {
    return `<div class="chat-bubble user">${msg.html}</div>`;
  }
  return `<div class="chat-bubble bot ${msg.pending ? "pending" : ""}">
    ${msg.html}
    ${msg.meta ? `<div class="chat-meta chat-trace">意图：${msg.meta.intentLabel} · 扫描：${msg.meta.scan === "pass" ? "通过" : "命中禁止词"} · 留痕：${msg.meta.logId}${msg.meta.review === "pending-review" ? " · 待人工复核" : ""}</div>` : ""}
  </div>`;
}

function renderChatbot() {
  const customer = selectedCustomer();
  const product = selectedProduct();
  const kyc = kycStatus(customer);
  const evidence = state.chatEvidence;

  if (!state.chatMessages.length) {
    state.chatMessages.push({
      role: "bot",
      html: `<p>你好，我是产品解读 Copilot。我只基于<strong>受控知识库</strong>（产品说明书摘要、适当性规则库、合规话术库、归因引擎）回答，每次回答都会标注来源并写入审计日志。试试左侧的快捷问题，或切换客户/产品后再问——同一问题的答案会随上下文变化。</p>`,
    });
  }

  return `
    <div class="chat-grid">
      <section class="section chat-side">
        <div class="section-header">
          <div class="section-title">
            <h2>对话上下文</h2>
            <p>切换客户/产品后，同一问题的答案会变化。</p>
          </div>
        </div>
        <label class="control" style="margin-bottom:10px">
          <span>客户</span>
          <select id="chat-customer">
            ${customers.map((item) => `<option value="${item.id}" ${item.id === customer.id ? "selected" : ""}>${item.id} ${item.name}</option>`).join("")}
          </select>
        </label>
        <label class="control" style="margin-bottom:12px">
          <span>产品</span>
          <select id="chat-product">
            ${products.map((item) => `<option value="${item.id}" ${item.id === product.id ? "selected" : ""}>${item.name}</option>`).join("")}
          </select>
        </label>
        <div class="note" style="margin-bottom:12px">
          <strong>${customer.name} · ${customer.risk}</strong>
          <span>标签：${deriveTags(customer).map((tag) => tag.label).join("、") || "无"}</span>
          <span>测评：${kyc.label}</span>
          <strong>${product.name}</strong>
          <span>${product.type} · ${product.risk} · 波动 ${fmtPct(product.volatility, 1)} · 历史回撤 ${fmtPct(product.maxDrawdownHist, 1)}</span>
        </div>
        <div class="section-title" style="margin-bottom:8px"><h3>快捷问题</h3></div>
        <div class="chat-chips">
          ${CHAT_QUICK_QUESTIONS.map((q) => `<button class="chat-chip" data-action="chat-ask" data-question="${q}" type="button">${q}</button>`).join("")}
        </div>
        <button class="button" data-action="chat-clear" type="button" style="margin-top:12px">清空对话</button>
      </section>

      <section class="section chat-main">
        <div class="section-header">
          <div class="section-title">
            <h2>产品解读 Copilot</h2>
            <p>意图匹配 → 受控模板 + 变量注入 → 禁止词扫描 → 留痕，纯前端脚本化演示，无大模型调用。</p>
          </div>
        </div>
        <div class="chat-flow" id="chat-flow">
          ${state.chatMessages.map(chatBubble).join("")}
        </div>
        <div class="chat-input-row">
          <input type="text" id="chat-input" placeholder="输入问题，如：最近为什么跌了 / 适合这位客户吗 / 会不会保本" autocomplete="off" />
          <button class="button primary" data-action="chat-send" type="button">发送</button>
        </div>
        <p class="chat-meta" style="margin-top:8px">AI 输出仅作客户经理辅助材料，触达客户前需完成适当性确认与人工复核。</p>
      </section>

      <section class="section chat-side">
        <div class="section-header">
          <div class="section-title">
            <h2>证据与留痕</h2>
            <p>最近一次回答的完整生成链路。</p>
          </div>
        </div>
        ${evidence ? `
          <div class="note">
            <strong>问题</strong><span>${escapeChatText(evidence.question)}</span>
            <strong>意图 / 模板</strong><span>${evidence.intentLabel} · Prompt v0.3 · KB 2026-06</span>
            <strong>来源引用</strong>
            ${evidence.sources.map((s) => `<span>· ${s}</span>`).join("")}
            <strong>禁止词扫描</strong>
            <span>${evidence.scan === "pass" ? "未命中禁止性表述" : "命中，已转人工复核"}</span>
            <strong>审计留痕</strong>
            <span>${evidence.logId} · ${evidence.time} · ${evidence.review === "auto-pass" ? "免复核" : "待复核（见 05 页队列）"}</span>
          </div>
        ` : `<div class="empty-state">发送一个问题后，这里会展示回答的来源引用、扫描结果和审计日志 ID。</div>`}
        <div class="note" style="margin-top:12px">
          <strong>Demo 边界</strong>
          <span>· 回答全部来自预置受控模板，未命中意图时拒答</span>
          <span>· 每次回答写入 05 页审计台账（调用量实时 +1）</span>
          <span>· 归因为演示数据，不构成业绩承诺</span>
        </div>
      </section>
    </div>
  `;
}

function renderApp() {
  if (window.location.hash.replace("#", "") !== state.page) {
    window.history.replaceState(null, "", `#${state.page}`);
  }
  document.querySelectorAll(".nav-item").forEach((button) => {
    button.classList.toggle("active", button.dataset.page === state.page);
  });
  document.getElementById("page-title").textContent = pageTitles[state.page];
  document.getElementById("branch-select").value = state.branch;
  document.getElementById("risk-select").value = state.risk;
  renderGlobalMetrics();
  const root = document.getElementById("page-root");
  root.innerHTML = {
    strategy: renderStrategy(),
    segment: renderSegment(),
    diagnosis: renderDiagnosis(),
    product: renderProduct(),
    governance: renderGovernance(),
    chatbot: renderChatbot(),
  }[state.page];
  if (window.WealthViz) window.WealthViz.mount(state.page);
  if (state.page === "chatbot") {
    requestAnimationFrame(() => {
      const flow = document.getElementById("chat-flow");
      if (flow) flow.scrollTop = flow.scrollHeight;
    });
  }
}

function renderGlobalMetrics() {
  const strip = document.getElementById("global-metrics");
  if (state.page !== "strategy") {
    strip.innerHTML = "";
    return;
  }
  const scopedCustomers = filteredCustomers();
  const opportunityCustomers = scopedCustomers.filter((customer) => portfolioGaps(customer).some((item) => item.gap > 0.08));
  const totalGap = scopedCustomers.reduce((sum, customer) => {
    return sum + portfolioGaps(customer).reduce((inner, item) => inner + item.gapAmount, 0);
  }, 0);
  const blockCount = scopedCustomers.reduce((sum, customer) => {
    return sum + productFits(customer).filter((fit) => fit.status === "blocked").length;
  }, 0);
  const accepted = state.feedback.filter((item) => item.action === "accepted").length;
  const decided = state.feedback.filter((item) => item.action !== "pending").length || 1;
  strip.innerHTML = [
    metric("服务客群", `${scopedCustomers.length || 0} 户`, `${state.branch} ${state.risk}`),
    metric("配置缺口规模", fmtMoney(totalGap), "按正向缺口估算"),
    metric("适当性拦截", `${blockCount} 次`, "风险、期限、流动性规则"),
    metric("分行采纳率", `${Math.round((accepted / decided) * 100)}%`, `${opportunityCustomers.length} 户存在明显服务机会`),
  ].join("");
}

function renderStrategyMarketRows() {
  return marketRows.map((row) => `
    <tr>
      <td>${assetLabel(row.key)}</td>
      <td>
        <select data-market="${row.key}">
          ${["谨慎", "中性", "积极"].map((view) => `<option value="${view}" ${state.marketViews[row.key] === view ? "selected" : ""}>${view}</option>`).join("")}
        </select>
      </td>
      <td>${marketActionText(row.key, state.marketViews[row.key])}</td>
    </tr>
  `).join("");
}

// 只刷新策略页的动态区域，避免重建 Tableau iframe 导致控件刷新。
function updateStrategyLiveRegion() {
  if (state.page !== "strategy") return;
  const selectedTemplate = getTemplate(state.risk);

  const rowsBody = document.getElementById("strategy-market-rows");
  if (rowsBody) rowsBody.innerHTML = renderStrategyMarketRows();

  ASSETS.forEach(({ key }) => {
    const valueEl = document.querySelector(`[data-template-value="${key}"]`);
    const fillEl = document.querySelector(`[data-template-fill="${key}"]`);
    if (valueEl) valueEl.textContent = fmtPct(selectedTemplate[key]);
    if (fillEl) fillEl.style.setProperty("--value", `${selectedTemplate[key] * 100}%`);
  });

  const reasonEl = document.getElementById("strategy-reason");
  if (reasonEl) {
    reasonEl.textContent = `低利率环境下，适度提升固收+与黄金类分散资产权重；权益类当前观点为${state.marketViews.equity}，建议结合客户风险预算分批执行。`;
  }

  const templateRows = document.getElementById("strategy-template-rows");
  if (templateRows) {
    templateRows.innerHTML = ["R2", "R3", "R4"].map((risk) => {
      const template = getTemplate(risk);
      return `<tr>
        <td><span class="pill ${risk === "R2" ? "green" : risk === "R3" ? "teal" : "violet"}">${risk}</span></td>
        ${ASSETS.map(({ key }) => `<td>${fmtPct(template[key])}</td>`).join("")}
      </tr>`;
    }).join("");
  }

  renderGlobalMetrics();
}

function metric(label, value, foot) {
  return `<div class="metric"><div class="metric-label">${label}</div><div class="metric-value">${value}</div><div class="metric-foot">${foot}</div></div>`;
}

function renderStrategy() {
  const templateRows = ["R2", "R3", "R4"].map((risk) => {
    const template = getTemplate(risk);
    return `<tr>
      <td><span class="pill ${risk === "R2" ? "green" : risk === "R3" ? "teal" : "violet"}">${risk}</span></td>
      ${ASSETS.map(({ key }) => `<td>${fmtPct(template[key])}</td>`).join("")}
    </tr>`;
  }).join("");

  const selectedTemplate = getTemplate(state.risk);
  return `
    <div class="grid-2">
      <section class="section">
        <div class="section-header">
          <div class="section-title">
            <h2>总行市场观点输入</h2>
            <p>规则模型根据风险等级、投资期限、流动性需求和市场观点生成模板。</p>
          </div>
          <button class="button primary" data-action="reset-views" type="button">恢复本月观点</button>
        </div>
        <div class="table-wrap">
          <table id="strategy-market-table">
            <thead><tr><th>资产类别</th><th>本月观点</th><th>配置动作</th></tr></thead>
            <tbody id="strategy-market-rows">${renderStrategyMarketRows()}</tbody>
          </table>
        </div>
      </section>

      <section class="section">
        <div class="section-header">
          <div class="section-title">
            <h2>${state.risk} 模板权重</h2>
            <p>当前版本 v1.2，适用于分行客户经理配置服务参考。</p>
          </div>
        </div>
        <div class="bar-list">
          ${ASSETS.map(({ key, label }, index) => `
            <div class="bar-row">
              <div class="bar-label">${label}</div>
              <div class="track"><div data-template-fill="${key}" class="fill ${index % 3 === 0 ? "green" : index % 3 === 1 ? "blue" : "amber"}" style="--value:${selectedTemplate[key] * 100}%"></div></div>
              <div class="delta" data-template-value="${key}">${fmtPct(selectedTemplate[key])}</div>
            </div>
          `).join("")}
        </div>
        <div class="note" style="margin-top:14px">
          <strong>调整原因</strong>
          <span id="strategy-reason">低利率环境下，适度提升固收+与黄金类分散资产权重；权益类当前观点为${state.marketViews.equity}，建议结合客户风险预算分批执行。</span>
          <strong>合规边界</strong>
          <span>模板不是最终投资建议，需结合客户 KYC、风险测评、适当性确认和人工复核。</span>
        </div>
      </section>
    </div>

    <section class="section"><div id="viz-strategy"></div></section>

    <section class="section">
      <div class="section-header">
        <div class="section-title">
          <h2>R2/R3/R4 客户配置模板</h2>
          <p>演示阶段采用可解释规则模型，后续可替换为参数化模型和版本审批流。</p>
        </div>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>客户类型</th>${ASSETS.map((asset) => `<th>${asset.label}</th>`).join("")}</tr></thead>
          <tbody id="strategy-template-rows">${templateRows}</tbody>
        </table>
      </div>
    </section>
  `;
}

function renderSegment() {
  const scoped = filteredCustomers().sort((a, b) => customerPriority(b) - customerPriority(a));
  const totalGap = scoped.reduce((sum, customer) => sum + portfolioGaps(customer).reduce((inner, item) => inner + item.gapAmount, 0), 0);
  const cashHigh = scoped.filter((customer) => customer.portfolio.cash > getTemplate(customer.risk).cash + 0.1).length;
  const fixedPlusGap = scoped.filter((customer) => portfolioGaps(customer).some((item) => item.key === "fixedPlus" && item.gap > 0.05)).length;
  const equityGap = scoped.filter((customer) => portfolioGaps(customer).some((item) => item.key === "equity" && item.gap > 0.05)).length;

  return `
    <section class="section">
      <div class="section-header">
        <div class="section-title">
          <h2>客群配置服务机会识别</h2>
          <p>该页面不是销售名单，而是基于资产配置缺口识别出的专业服务机会。</p>
        </div>
      </div>
      <div class="kpi-grid">
        ${miniKpi(`${state.risk} 客户总数`, `${scoped.length} 户`, "当前筛选范围")}
        ${miniKpi("配置不达标客户", `${scoped.filter((customer) => portfolioGaps(customer).some((item) => item.gap > 0.08)).length} 户`, "任一正向缺口 >8%")}
        ${miniKpi("现金占比过高", `${cashHigh} 户`, "流动性沉淀明显")}
        ${miniKpi("机会规模", fmtMoney(totalGap), "按目标缺口估算")}
      </div>
    </section>

    <div class="grid-2">
      <section class="section">
        <div class="section-header">
          <div class="section-title">
            <h2>Top 优先服务名单</h2>
            <p>优先级综合配置缺口、到期资金和未触达时间。</p>
          </div>
        </div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>客户</th><th>分行</th><th>可投资资产</th><th>当前主要问题</th><th>配置缺口</th><th>动作</th></tr></thead>
            <tbody>
              ${scoped.map((customer) => {
                const gaps = portfolioGaps(customer).filter((item) => item.gap > 0.02).sort((a, b) => b.gap - a.gap);
                const issue = customer.portfolio.cash > getTemplate(customer.risk).cash + 0.1 ? "现金类占比过高" : "结构分散不足";
                return `<tr class="clickable">
                  <td><strong>${customer.id}</strong><br><span class="item-meta">${customer.name} · ${customer.risk}</span></td>
                  <td>${customer.branch}</td>
                  <td>${fmtMoney(customer.aum)}</td>
                  <td>${issue}</td>
                  <td>${gaps.map((gap) => gap.label).slice(0, 3).join("、") || "暂无明显缺口"}</td>
                  <td><button class="button" data-action="select-customer" data-customer="${customer.id}" data-page-target="diagnosis" type="button">查看诊断</button></td>
                </tr>`;
              }).join("") || `<tr><td colspan="6"><div class="empty-state">当前筛选条件下没有客户</div></td></tr>`}
            </tbody>
          </table>
        </div>
      </section>

      <section class="section">
        <div class="section-header">
          <div class="section-title">
            <h2>缺口分布</h2>
            <p>用于总行制定分行赋能和产品加载重点。</p>
          </div>
        </div>
        <div class="bar-list">
          ${bar("固收+ 配置缺口", fixedPlusGap, scoped.length, "teal")}
          ${bar("权益/ETF 配置缺口", equityGap, scoped.length, "blue")}
          ${bar("黄金/另类配置缺口", scoped.filter((customer) => portfolioGaps(customer).some((item) => item.key === "gold" && item.gap > 0.02)).length, scoped.length, "amber")}
          ${bar("产品到期触发", scoped.filter((customer) => customer.maturityDays <= 15).length, scoped.length, "green")}
        </div>
        <div class="script-box warning-box" style="margin-top:14px">
          后续仍需客户经理结合客户需求、风险测评和适当性规则进行人工确认。
        </div>
      </section>
    </div>

    <section class="section">
      <div class="section-header">
        <div class="section-title">
          <h2>客群级产品加载建议（总行视角）</h2>
          <p>基于客群缺口快照输出分行产品加载与赋能动作，数据口径对齐 06_segment_snapshot。</p>
        </div>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>客群</th><th>客户数</th><th>最大缺口资产</th><th>缺口规模</th><th>现金沉淀</th><th>建议加载产品</th><th>预计承接</th><th>分行赋能动作</th></tr></thead>
          <tbody>
            ${segmentSnapshots
              .filter((row) => (state.branch === "全部" || row.branch === state.branch) && row.risk === state.risk)
              .map((row) => `<tr>
                <td><strong>${row.branch} · ${row.risk}</strong></td>
                <td>${row.customers} 户</td>
                <td>${row.shortfallAsset}</td>
                <td>${fmtMoney(row.shortfallAmount)}</td>
                <td>${fmtMoney(row.cashOverweight)}</td>
                <td>${row.loadProducts.map((id) => products.find((p) => p.id === id)?.name || id).join("、")}</td>
                <td>${fmtMoney(row.expectedUplift)}</td>
                <td>${row.enablement}</td>
              </tr>`).join("") || `<tr><td colspan="8"><div class="empty-state">当前筛选条件下无客群快照</div></td></tr>`}
          </tbody>
        </table>
      </div>
    </section>

    <section class="section"><div id="viz-segment"></div></section>
  `;
}

function journeyStepper(customer) {
  const stageIndex = state.journey[customer.id] ?? 0;
  return `<div class="stepper">
    ${JOURNEY_STAGES.map((stage, index) => `
      <div class="step ${index < stageIndex ? "done" : ""} ${index === stageIndex ? "current" : ""}">
        <span class="step-dot">${index < stageIndex ? "✓" : index + 1}</span>
        <span class="step-label">${stage}</span>
      </div>
    `).join('<span class="step-line"></span>')}
  </div>`;
}

function tagChips(tags) {
  if (!tags.length) return `<span class="item-meta">暂无派生标签</span>`;
  return tags.map((tag) => `<span class="tag ${tag.tone}" title="${tag.rule}">${tag.label}</span>`).join("");
}

function renderDiagnosis() {
  const customer = selectedCustomer();
  const gaps = portfolioGaps(customer);
  const triggers = generateTriggers(customer);
  const tags = deriveTags(customer);
  const kyc = kycStatus(customer);
  const alloc = getTargetAllocation(customer);
  const currentVol = portfolioVol(customer.portfolio);
  const currentStress = portfolioStress(customer.portfolio);
  const plan = buildRebalancePlan(customer);

  return `
    <section class="section">
      <div class="section-header">
        <div class="section-title">
          <h2>标准化服务流程 · ${customer.id} ${customer.name}</h2>
          <p>诊断 → 配置建议 → 产品筛选 → 话术生成 → 投后跟踪，每位客户挂流程状态。</p>
        </div>
        <label class="control">
          <span>客户</span>
          <select id="customer-select">
            ${customers.map((item) => `<option value="${item.id}" ${item.id === customer.id ? "selected" : ""}>${item.id} ${item.name}</option>`).join("")}
          </select>
        </label>
      </div>
      ${journeyStepper(customer)}
    </section>

    <div class="grid-2">
      <section class="section">
        <div class="section-header">
          <div class="section-title">
            <h2>客户画像（KYC + 行为）</h2>
            <p>标签由规则派生，悬停可查看生成规则，可解释、可追溯。</p>
          </div>
        </div>
        <div class="tag-row">${tagChips(tags)}</div>
        <div class="asset-grid" style="margin-top:12px">
          ${[
            ["风险等级", customer.risk, "适当性匹配上限"],
            ["可投资资产", fmtMoney(customer.aum), customer.branch],
            ["投资期限", `${customer.horizonYears} 年`, `流动性需求：${customer.liquidityNeed}`],
            ["产品到期", `${customer.maturityDays} 天`, fmtMoney(customer.maturityAmount)],
            ["最近触达", `${customer.lastContactDays} 天`, customer.lifeStage],
          ].map(([label, value, meta]) => `<div class="asset-tile"><span>${label}</span><strong>${value}</strong><span>${meta}</span></div>`).join("")}
        </div>
        <div class="asset-grid" style="margin-top:10px">
          ${[
            ["风险测评", kyc.state === "expired" ? "已过期" : kyc.state === "expiring" ? "临期" : "有效", `${customer.kyc.validUntil} · ${kyc.label}`],
            ["测评得分", `${customer.kyc.score} 分`, `投资经验 ${customer.kyc.investYears} 年`],
            ["已投品类", customer.kyc.experiencedTypes.join("/"), "首购品类需双录"],
            ["年申赎次数", `${customer.behavior.tradeFreqPerYear} 次`, `平均持有 ${customer.behavior.avgHoldingMonths} 个月`],
            ["追涨杀跌指数", customer.behavior.chaseIndex.toFixed(2), customer.behavior.hasSIP ? "有定投习惯" : "无定投"],
          ].map(([label, value, meta]) => `<div class="asset-tile"><span>${label}</span><strong>${value}</strong><span>${meta}</span></div>`).join("")}
        </div>
        ${kyc.state === "expired" ? `<div class="script-box danger-box" style="margin-top:12px"><strong>适当性拦截（S-02）：</strong>风险测评已过期，产品推荐已全部拦截，请先邀约客户完成重测。</div>` : ""}
      </section>

      <section class="section">
        <div class="section-header">
          <div class="section-title">
            <h2>诊断结论与风险预算</h2>
            <p>组合风险测算 vs 客户风险预算（基准 × 行为标签修正）。</p>
          </div>
        </div>
        <div class="script-box">
          ${customer.name} 当前配置偏${customer.portfolio.cash > getTemplate(customer.risk).cash + 0.1 ? "保守，现金/低波动资产占比较高" : "集中，组合分散度仍需提升"}。
          建议在不突破 ${customer.risk} 风险等级与风险预算的前提下，优先补充 ${positiveGapAssets(customer).map(assetLabel).join("、") || "缺口较小的分散资产"}。
        </div>
        <div class="table-wrap" style="margin-top:12px">
          <table>
            <thead><tr><th>指标</th><th>当前组合</th><th>目标组合</th><th>风险预算</th><th>判定</th></tr></thead>
            <tbody>
              <tr>
                <td>预期年化波动</td>
                <td>${fmtPct(currentVol, 1)}</td>
                <td>${fmtPct(alloc.vol, 1)}</td>
                <td>≤ ${fmtPct(alloc.budget.maxVol, 1)}</td>
                <td><span class="pill ${alloc.vol <= alloc.budget.maxVol ? "green" : "red"}">${alloc.vol <= alloc.budget.maxVol ? "在预算内" : "超预算"}</span></td>
              </tr>
              <tr>
                <td>压力情景回撤</td>
                <td>${fmtPct(currentStress, 1)}</td>
                <td>${fmtPct(alloc.stress, 1)}</td>
                <td>≥ -${fmtPct(alloc.budget.maxDrawdown, 1)}</td>
                <td><span class="pill ${Math.abs(alloc.stress) <= alloc.budget.maxDrawdown ? "green" : "red"}">${Math.abs(alloc.stress) <= alloc.budget.maxDrawdown ? "在预算内" : "超预算"}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="note" style="margin-top:12px">
          <strong>风险预算依据</strong>
          ${alloc.budget.notes.map((note) => `<span>${note}</span>`).join("")}
        </div>
        <div class="bar-list" style="margin-top:14px">
          ${gaps.map((item) => `
            <div class="bar-row">
              <div class="bar-label">${item.label}</div>
              <div class="track"><div class="fill ${item.gap >= 0 ? "green" : "amber"}" style="--value:${clamp(Math.abs(item.gap) * 220, 4, 100)}%"></div></div>
              <div class="delta ${item.gap >= 0 ? "positive" : "negative"}">${item.gap >= 0 ? "+" : ""}${fmtPct(item.gap)}</div>
            </div>
          `).join("")}
        </div>
      </section>
    </div>

    <section class="section">
      <div class="section-header">
        <div class="section-title">
          <h2>目标配置生成轨迹</h2>
          <p>target = f(风险等级, 投资期限, 流动性需求, 市场观点, 风险预算)，每一步可解释。</p>
        </div>
      </div>
      <div class="trace-list">
        ${alloc.trace.map((step, index) => `<div class="trace-step"><span class="trace-index">${index + 1}</span><span>${step}</span></div>`).join("")}
      </div>
    </section>

    <section class="section">
      <div class="section-header">
        <div class="section-title">
          <h2>配置诊断表</h2>
          <p>偏离为目标比例减当前比例，正数代表需要补充。</p>
        </div>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>资产类别</th><th>当前比例</th><th>目标比例（个性化）</th><th>偏离</th><th>诊断</th></tr></thead>
          <tbody>
            ${gaps.map((item) => `<tr>
              <td>${item.label}</td>
              <td>${fmtPct(item.current)}</td>
              <td>${fmtPct(item.target)}</td>
              <td><span class="delta ${item.gap >= 0 ? "positive" : "negative"}">${item.gap >= 0 ? "+" : ""}${fmtPct(item.gap)}</span></td>
              <td>${Math.abs(item.gap) < 0.025 ? "匹配" : item.gap > 0 ? "不足" : "偏高"}</td>
            </tr>`).join("")}
          </tbody>
        </table>
      </div>
    </section>

    <section class="section">
      <div class="section-header">
        <div class="section-title">
          <h2>建议调仓方案（配置建议环节）</h2>
          <p>缺口 → 资金来源 → 分批动作，到期资金优先自然承接。</p>
        </div>
        <button class="button primary" data-action="goto-product" type="button">查看适配产品 →</button>
      </div>
      <div class="grid-2">
        <div>
          <h3 style="margin-bottom:10px">资金来源（优先级排序）</h3>
          <div class="split-list">
            ${plan.fundingSources.map((source, index) => `
              <div class="note"><strong>${index + 1}. ${source.source}</strong><span>可用金额约 ${fmtMoney(source.amount)}</span></div>
            `).join("") || `<div class="empty-state">暂无正向缺口，无需筹措资金</div>`}
          </div>
        </div>
        <div>
          <h3 style="margin-bottom:10px">执行约束</h3>
          <div class="split-list">
            ${plan.constraints.map((rule) => `<div class="note"><span>${rule}</span></div>`).join("")}
          </div>
        </div>
      </div>
      <div class="table-wrap" style="margin-top:14px">
        <table>
          <thead><tr><th>动作</th><th>资产类别</th><th>建议金额</th><th>分批</th><th>说明</th></tr></thead>
          <tbody>
            ${plan.actions.map((action) => `<tr>
              <td><span class="pill ${action.direction === "买入" ? "green" : "amber"}">${action.direction}</span></td>
              <td>${action.label}</td>
              <td>${fmtMoney(action.amount)}</td>
              <td>${action.batches} 期</td>
              <td>${action.note}</td>
            </tr>`).join("") || `<tr><td colspan="5"><div class="empty-state">当前无调仓动作</div></td></tr>`}
          </tbody>
        </table>
      </div>
    </section>

    <section class="section">
      <div class="section-header">
        <div class="section-title">
          <h2>投后触发规则</h2>
          <p>触发结果可进入客户经理待办、续接提醒或投后话术生成。</p>
        </div>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>触发事件</th><th>规则</th><th>系统动作</th><th>状态</th></tr></thead>
          <tbody>
            ${triggers.map((trigger) => `<tr>
              <td>${trigger.type}</td>
              <td>${trigger.rule}</td>
              <td>${trigger.action}</td>
              <td><span class="pill ${trigger.type === "持续跟踪" ? "blue" : trigger.type === "测评过期" ? "red" : "amber"}">${trigger.type === "持续跟踪" ? "跟踪" : "已触发"}</span></td>
            </tr>`).join("")}
          </tbody>
        </table>
      </div>
    </section>

    <section class="section"><div id="viz-diagnosis"></div></section>
  `;
}

function renderProduct() {
  const customer = selectedCustomer();
  const fits = productFits(customer);
  const product = selectedProduct();
  const selectedFit = fits.find((fit) => fit.product.id === product.id);
  const interpretation = aiInterpretation(product, customer);
  const aiText = Object.values(interpretation).flat().join(" ");
  const hits = complianceHits(aiText);
  const script = generateScript(state.scriptScenario, customer, product);
  const kyc = kycStatus(customer);
  const groups = [
    ["candidate", "可进入候选清单", "green"],
    ["caution", "谨慎使用", "amber"],
    ["blocked", "自动拦截", "red"],
  ];

  return `
    ${kyc.state === "expired" ? `<section class="section"><div class="script-box danger-box"><strong>全局适当性拦截（S-02）：</strong>${customer.name} 风险测评已过期（${customer.kyc.validUntil}），所有产品推荐已自动拦截，仅可查看解读。请先完成重测邀约。</div></section>` : ""}
    <div class="grid-2">
      <section class="section">
        <div class="section-header">
          <div class="section-title">
            <h2>产品池与适配结果</h2>
            <p>当前客户：${customer.id} ${customer.name}，风险 ${customer.risk}，标签：${deriveTags(customer).map((tag) => tag.label).join("、") || "无"}。点击状态可展开校验痕迹。</p>
          </div>
          <label class="control">
            <span>切换客户</span>
            <select id="customer-select-product">
              ${customers.map((item) => `<option value="${item.id}" ${item.id === customer.id ? "selected" : ""}>${item.id} ${item.name}</option>`).join("")}
            </select>
          </label>
        </div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>产品</th><th>风险</th><th>期限</th><th>建议金额</th><th>评分</th><th>状态 / 校验痕迹</th></tr></thead>
            <tbody>
              ${fits.map((fit) => `<tr class="clickable ${fit.product.id === product.id ? "row-active" : ""}">
                <td>
                  <button class="button ghost" data-action="select-product" data-product="${fit.product.id}" type="button">${fit.product.name}</button>
                  <div class="item-meta">${fit.product.type} · ${assetLabel(fit.product.assetClass)} · 波动 ${fmtPct(fit.product.volatility, 1)} · 历史回撤 ${fmtPct(fit.product.maxDrawdownHist, 1)}</div>
                </td>
                <td>${fit.product.risk}</td>
                <td>${fit.product.horizonMonths >= 12 ? `${Math.round(fit.product.horizonMonths / 12)} 年以上` : `${fit.product.horizonMonths} 个月`}</td>
                <td>${fit.status === "blocked" ? "—" : fit.suggestedAmount > 0 ? fmtMoney(fit.suggestedAmount) + (fit.capped ? "（已降额）" : "") : "小比例"}</td>
                <td><strong>${fit.score}</strong></td>
                <td>
                  <details class="trace-details">
                    <summary><span class="pill ${fit.status === "candidate" ? "green" : fit.status === "caution" ? "amber" : "red"}">${fit.status === "candidate" ? "候选" : fit.status === "caution" ? "谨慎" : "拦截"}</span></summary>
                    <div class="trace-list small">
                      ${fit.trace.map((entry) => `<div class="trace-step ${entry.result}"><span class="trace-index">${entry.ruleId}</span><span>${entry.detail}<em class="trace-meta">规则版本 ${entry.version} · ${entry.result === "pass" ? "通过" : entry.result === "caution" ? "谨慎" : "拦截"}</em></span></div>`).join("")}
                    </div>
                  </details>
                </td>
              </tr>`).join("")}
            </tbody>
          </table>
        </div>
        <div class="note" style="margin-top:12px">
          <strong>产品画像（KYP）· ${product.name}</strong>
          <span>业绩基准：${product.benchmark} ｜ 费率：${product.fees} ｜ 开放：${product.openFrequency} ｜ 成立：${product.inceptionDate} ｜ ${product.salesStatus} ｜ 适配标签：${product.audienceTags.join("、")}</span>
          <strong>说明书摘要（受控知识库）</strong>
          <span>投资范围：「${product.docExcerpts.investScope}」</span>
          <span>风险揭示：「${product.docExcerpts.riskDisclosure}」</span>
        </div>
      </section>

      <section class="section">
        <div class="section-header">
          <div class="section-title">
            <h2>AI 产品解读</h2>
            <p>规则引擎先分类，AI 只解释原因；输出基于受控摘要并做禁止词扫描。</p>
          </div>
        </div>
        ${renderAiPanel(interpretation, hits)}
      </section>
    </div>

    <section class="section">
      <div class="section-header">
        <div class="section-title">
          <h2>场景化话术生成（可留痕）</h2>
          <p>模板装配 → 变量注入 → 必含句式 → 禁止词扫描 → 写入审计日志。切换场景即生成一条留痕。</p>
        </div>
        <div class="toolbar">
          ${SCRIPT_SCENARIOS.map((scenario) => `<button class="button ${scenario.key === state.scriptScenario ? "primary" : ""}" data-action="select-scenario" data-scenario="${scenario.key}" type="button">${scenario.label}</button>`).join("")}
        </div>
      </div>
      <div class="grid-2">
        <div class="split-list">
          <div class="script-box"><strong>客户经理版 · ${script.scenarioLabel}：</strong>${script.advisorText}</div>
          <div class="script-box warning-box"><strong>客户沟通版：</strong>${script.customerText}</div>
          ${script.mandatory.map((phrase) => `<div class="script-box danger-box"><strong>必含合规句式：</strong>${phrase}</div>`).join("")}
        </div>
        <div class="split-list">
          <div class="note">
            <strong>注入变量</strong>
            <span>${script.variables.join(" ｜ ") || "无"}</span>
            <strong>来源依据</strong>
            ${script.sources.map((source) => `<span>· ${source}</span>`).join("")}
            <strong>禁止词扫描</strong>
            <span>${script.hits.length ? `命中：${script.hits.join("、")}，已转人工复核` : "未命中禁止性表述"}</span>
            <strong>留痕状态</strong>
            <span>${script.hits.length || script.firstPurchase ? "本次生成需人工复核后方可触达客户（见治理页待复核队列）" : "自动通过，日志已写入治理页审计台账"}</span>
          </div>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="section-header">
        <div class="section-title">
          <h2>适配分组</h2>
          <p>规则引擎先完成候选、谨慎和拦截分类，AI 只解释原因和生成话术。</p>
        </div>
      </div>
      <div class="grid-3">
        ${groups.map(([status, title, color]) => `
          <div class="list-item">
            <div class="item-head"><div class="item-title">${title}</div><span class="pill ${color}">${fits.filter((fit) => fit.status === status).length}</span></div>
            <div class="split-list">
              ${fits.filter((fit) => fit.status === status).map((fit) => `
                <div class="note">
                  <strong>${fit.product.name} · ${fit.score} 分</strong>
                  <span>${[...fit.reasons, ...fit.cautions, ...fit.blocks].slice(0, 3).join("；")}</span>
                </div>
              `).join("") || `<div class="empty-state">暂无产品</div>`}
            </div>
          </div>
        `).join("")}
      </div>
    </section>

    <section class="section"><div id="viz-product"></div></section>
  `;
}

function renderAiPanel(interpretation, hits) {
  return `
    <div class="split-list">
      ${[
        ["产品定位", interpretation.positioning],
        ["收益来源或保障逻辑", interpretation.returnSource],
        ["主要风险", interpretation.risks.join("、")],
        ["适合客户", interpretation.suitable],
        ["不适合客户", interpretation.notSuitable],
      ].map(([label, value]) => `<div class="note"><strong>${label}</strong><span>${value}</span></div>`).join("")}
      <div class="script-box"><strong>客户经理专业版：</strong>${interpretation.advisorScript}</div>
      <div class="script-box warning-box"><strong>客户沟通版：</strong>${interpretation.customerScript}</div>
      <div class="script-box danger-box"><strong>合规提示：</strong>${interpretation.compliance}</div>
      <div class="note">
        <strong>来源依据</strong>
        <span>${interpretation.sources.join("；")}</span>
        <strong>禁止词扫描</strong>
        <span>${hits.length ? `命中：${hits.join("、")}，需人工复核` : "未命中禁止性表述"}</span>
      </div>
    </div>
  `;
}

function renderGovernance() {
  const total = state.feedback.length;
  const accepted = state.feedback.filter((item) => item.action === "accepted").length;
  const rejected = state.feedback.filter((item) => item.action === "rejected").length;
  const pending = state.feedback.filter((item) => item.action === "pending").length;
  const rejectReasons = state.feedback
    .filter((item) => item.action === "rejected")
    .reduce((acc, item) => {
      acc[item.reason] = (acc[item.reason] || 0) + 1;
      return acc;
    }, {});

  const log = state.aiAuditLog;
  const scanHits = log.filter((item) => item.scanResult === "hit").length;
  const pendingReview = log.filter((item) => item.reviewStatus === "pending-review");
  const blockCount = customers.reduce((sum, customer) => sum + productFits(customer).filter((fit) => fit.status === "blocked").length, 0);
  const todos = buildTodos();

  return `
    <section class="section">
      <div class="section-header">
        <div class="section-title">
          <h2>AI 治理指标（实时聚合自审计日志）</h2>
          <p>在产品页切换产品或场景即写入一条生成日志，指标随之刷新。</p>
        </div>
      </div>
      <div class="kpi-grid">
        ${miniKpi("AI 生成调用", `${log.length}`, "解读 + 场景话术累计")}
        ${miniKpi("受控知识库引用率", `${log.length ? Math.round((log.filter((item) => item.kbVersion).length / log.length) * 100) : 0}%`, "带 kbVersion 的生成占比")}
        ${miniKpi("适当性拦截", `${blockCount} 次`, "S 类硬规则（含测评过期）")}
        ${miniKpi("禁止词/待复核", `${scanHits} / ${pendingReview.length}`, "命中扫描 · 人工复核队列")}
      </div>
    </section>

    <section class="section">
      <div class="section-header">
        <div class="section-title">
          <h2>今日待办工作台</h2>
          <p>由规则与日志自动派生：测评重测、到期承接、再平衡、回撤安抚、话术复核、反馈跟进。</p>
        </div>
        <span class="pill teal">${todos.length} 项</span>
      </div>
      <div class="grid-3">
        ${todos.map((todo) => `
          <div class="list-item">
            <div class="item-head">
              <div>
                <div class="item-title">${todo.type}</div>
                <div class="item-meta">${todo.who}</div>
              </div>
              <span class="pill ${todo.tone}">待办</span>
            </div>
            <div class="item-meta">${todo.detail}</div>
            <div class="toolbar"><button class="button" data-action="goto" data-page-target="${todo.page}" data-customer="${todo.customerId}" type="button">去处理</button></div>
          </div>
        `).join("") || `<div class="empty-state">今日无待办</div>`}
      </div>
    </section>

    <section class="section">
      <div class="section-header">
        <div class="section-title">
          <h2>待复核队列（人工复核流转）</h2>
          <p>命中禁止词或首购/高风险场景的生成内容，通过后方可触达客户，驳回则退回重写。</p>
        </div>
      </div>
      <div class="split-list">
        ${pendingReview.map((item) => `
          <div class="list-item">
            <div class="item-head">
              <div>
                <div class="item-title">${item.logId} · ${item.customerId} · ${products.find((p) => p.id === item.productId)?.name || item.productId}</div>
                <div class="item-meta">${item.time} · ${item.advisor} · 场景：${item.scenario} · ${item.scanResult === "hit" ? "命中禁止词" : "首购/高风险场景"}</div>
              </div>
              <span class="pill amber">待复核</span>
            </div>
            <div class="toolbar">
              <button class="button" data-action="review" data-log="${item.logId}" data-value="approved" type="button">复核通过</button>
              <button class="button" data-action="review" data-log="${item.logId}" data-value="rejected" type="button">驳回重写</button>
            </div>
          </div>
        `).join("") || `<div class="empty-state">复核队列已清空</div>`}
      </div>
    </section>

    <section class="section">
      <div class="section-header">
        <div class="section-title">
          <h2>AI 生成审计台账（可留痕）</h2>
          <p>谁、何时、什么场景、Prompt/知识库版本、扫描与复核结果、是否已触达。</p>
        </div>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>日志</th><th>时间</th><th>发起人</th><th>客户/产品</th><th>场景</th><th>版本</th><th>扫描</th><th>复核</th><th>触达</th></tr></thead>
          <tbody>
            ${log.slice(0, 10).map((item) => `<tr>
              <td><strong>${item.logId}</strong></td>
              <td>${item.time}</td>
              <td>${item.advisor}</td>
              <td>${item.customerId} · ${products.find((p) => p.id === item.productId)?.name || item.productId}</td>
              <td>${item.scenario}</td>
              <td>${item.promptVersion} / KB ${item.kbVersion}</td>
              <td><span class="pill ${item.scanResult === "pass" ? "green" : "red"}">${item.scanResult === "pass" ? "通过" : "命中"}</span></td>
              <td><span class="pill ${item.reviewStatus === "auto-pass" ? "green" : item.reviewStatus === "approved" ? "teal" : item.reviewStatus === "rejected" ? "red" : "amber"}">${item.reviewStatus === "auto-pass" ? "免复核" : item.reviewStatus === "approved" ? "已通过" : item.reviewStatus === "rejected" ? "已驳回" : "待复核"}</span></td>
              <td>${item.delivered ? "已触达" : "未触达"}</td>
            </tr>`).join("")}
          </tbody>
        </table>
      </div>
    </section>

    <div class="grid-2">
      <section class="section">
        <div class="section-header">
          <div class="section-title">
            <h2>业务运营指标</h2>
            <p>分行采纳和拒绝原因用于回流优化配置模板、评分规则和话术库。</p>
          </div>
        </div>
        <div class="bar-list">
          ${bar("分行采纳率", accepted, Math.max(accepted + rejected, 1), "green")}
          ${bar("人工待复核", pending, total, "amber")}
          ${bar("配置服务覆盖", 168, 420, "blue")}
          ${bar("投后提醒完成", 73, 100, "teal")}
        </div>
        <div class="audit-grid" style="margin-top:14px">
          ${Object.keys(rejectReasons).map((reason) => `<div class="mini-kpi"><span>${reason}</span><strong>${rejectReasons[reason]}</strong><span>拒绝原因 · 回流客户标签与评分</span></div>`).join("") || `<div class="empty-state">暂无拒绝原因</div>`}
        </div>
        <div class="note" style="margin-top:12px">
          <strong>反馈回流规则（已生效）</strong>
          <span>· 同一客户“风险过高”拒绝 ≥2 次 → 自动挂“波动敏感”标签，收紧风险预算（×0.65）</span>
          <span>· 客户拒绝过的同类资产产品 → 适配评分 -10（规则 B-02）</span>
          <span>· 采纳过的同类资产 → 评分 +5，优先推同类低波动方案</span>
        </div>
      </section>

      <section class="section">
        <div class="section-header">
          <div class="section-title">
            <h2>反馈闭环</h2>
            <p>点击动作可模拟客户经理采纳或拒绝，实时刷新治理指标与客户标签。</p>
          </div>
        </div>
        <div class="split-list">
          ${state.feedback.map((item) => {
            const customer = customers.find((entry) => entry.id === item.customerId);
            const product = products.find((entry) => entry.id === item.productId);
            return `<div class="list-item">
              <div class="item-head">
                <div>
                  <div class="item-title">${customer?.id || item.customerId} · ${product?.name || item.productId}</div>
                  <div class="item-meta">${item.comment}</div>
                </div>
                <span class="pill ${item.action === "accepted" ? "green" : item.action === "rejected" ? "red" : "amber"}">${item.action === "accepted" ? "已采纳" : item.action === "rejected" ? "已拒绝" : "待跟进"}</span>
              </div>
              <div class="toolbar">
                <button class="button" data-action="feedback" data-feedback="${item.id}" data-value="accepted" type="button">采纳</button>
                <button class="button" data-action="feedback" data-feedback="${item.id}" data-value="rejected" type="button">拒绝</button>
                <button class="button" data-action="feedback" data-feedback="${item.id}" data-value="pending" type="button">待跟进</button>
              </div>
            </div>`;
          }).join("")}
        </div>
      </section>
    </div>

    <section class="section">
      <div class="section-header">
        <div class="section-title">
          <h2>版本治理与报备状态</h2>
          <p>上线后需将 Prompt、知识库、规则版本和人工复核状态写入审计日志。</p>
        </div>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>对象</th><th>当前版本</th><th>变更内容</th><th>状态</th><th>负责人</th></tr></thead>
          <tbody>
            <tr><td>配置模板</td><td>v1.2</td><td>提升固收+和黄金分散权重</td><td><span class="pill green">已审批</span></td><td>总行资配团队</td></tr>
            <tr><td>适当性规则库</td><td>${RULE_VERSION}</td><td>新增测评有效期 S-02、集中度 S-04、首购双录 C-02、反馈回流 B-02</td><td><span class="pill amber">待复核</span></td><td>产品加载团队</td></tr>
            <tr><td>AI Prompt / 话术库</td><td>v0.3 / 2026-06</td><td>新增五场景模板、必含句式校验与生成留痕</td><td><span class="pill amber">待报备</span></td><td>智能体治理团队</td></tr>
            <tr><td>风险预算模型</td><td>v0.2</td><td>基准预算 × 行为标签修正，接入目标配置引擎</td><td><span class="pill amber">报批中</span></td><td>数智化项目组</td></tr>
          </tbody>
        </table>
      </div>
    </section>
  `;
}

function miniKpi(label, value, meta) {
  return `<div class="mini-kpi"><span>${label}</span><strong>${value}</strong><span>${meta}</span></div>`;
}

function bar(label, value, total, color = "teal") {
  const pct = total ? clamp((value / total) * 100, 0, 100) : 0;
  return `<div class="bar-row">
    <div class="bar-label">${label}</div>
    <div class="track"><div class="fill ${color}" style="--value:${pct}%"></div></div>
    <div class="delta">${total === 100 ? `${value}%` : `${value}/${total}`}</div>
  </div>`;
}

document.addEventListener("click", (event) => {
  const button = event.target.closest("button");
  if (!button) return;

  if (button.dataset.page) {
    state.page = button.dataset.page;
    renderApp();
    return;
  }

  if (button.dataset.action === "reset-views") {
    state.marketViews = {
      cash: "中性",
      fixedIncome: "积极",
      fixedPlus: "积极",
      equity: "谨慎",
      gold: "积极",
    };
    renderApp();
    return;
  }

  if (button.dataset.action === "select-customer") {
    state.selectedCustomerId = button.dataset.customer;
    if (button.dataset.pageTarget) state.page = button.dataset.pageTarget;
    renderApp();
    return;
  }

  if (button.dataset.action === "goto") {
    if (button.dataset.customer && button.dataset.customer !== "undefined") state.selectedCustomerId = button.dataset.customer;
    if (button.dataset.pageTarget) state.page = button.dataset.pageTarget;
    renderApp();
    return;
  }

  if (button.dataset.action === "goto-product") {
    state.page = "product";
    state.journey[state.selectedCustomerId] = Math.max(state.journey[state.selectedCustomerId] || 0, 2);
    renderApp();
    return;
  }

  if (button.dataset.action === "select-product") {
    state.selectedProductId = button.dataset.product;
    const customer = selectedCustomer();
    const product = selectedProduct();
    const interpretation = aiInterpretation(product, customer);
    const hits = complianceHits(Object.values(interpretation).flat().join(" "));
    logAiGeneration("产品解读", customer, product, hits, false);
    renderApp();
    return;
  }

  if (button.dataset.action === "select-scenario") {
    state.scriptScenario = button.dataset.scenario;
    const customer = selectedCustomer();
    const product = selectedProduct();
    const script = generateScript(state.scriptScenario, customer, product);
    logAiGeneration(script.scenarioLabel, customer, product, script.hits, script.firstPurchase);
    renderApp();
    return;
  }

  if (button.dataset.action === "review") {
    const entry = state.aiAuditLog.find((item) => item.logId === button.dataset.log);
    if (entry) {
      entry.reviewStatus = button.dataset.value;
      if (button.dataset.value === "approved") {
        entry.delivered = true;
        state.journey[entry.customerId] = Math.max(state.journey[entry.customerId] || 0, 4);
      }
    }
    renderApp();
    return;
  }

  if (button.dataset.action === "chat-ask") {
    askChat(button.dataset.question);
    return;
  }

  if (button.dataset.action === "chat-send") {
    const input = document.getElementById("chat-input");
    if (input && input.value.trim()) {
      const question = input.value.trim();
      input.value = "";
      askChat(question);
    }
    return;
  }

  if (button.dataset.action === "chat-clear") {
    state.chatMessages = [];
    state.chatEvidence = null;
    renderApp();
    return;
  }

  if (button.dataset.action === "feedback") {
    const item = state.feedback.find((feedback) => feedback.id === button.dataset.feedback);
    if (item) {
      item.action = button.dataset.value;
      item.reason = item.action === "rejected" ? "客户暂不接受" : item.action === "pending" ? "待跟进" : "-";
    }
    renderApp();
  }
});

document.addEventListener("change", (event) => {
  const target = event.target;
  if (target.id === "branch-select") {
    state.branch = target.value;
    if (state.page === "strategy") {
      renderGlobalMetrics();
    } else {
      renderApp();
    }
    return;
  }
  if (target.id === "risk-select") {
    state.risk = target.value;
    const scoped = filteredCustomers();
    if (scoped.length) state.selectedCustomerId = scoped[0].id;
    if (state.page === "strategy") {
      updateStrategyLiveRegion();
    } else {
      renderApp();
    }
    return;
  }
  if (target.id === "customer-select" || target.id === "customer-select-product") {
    state.selectedCustomerId = target.value;
    renderApp();
    return;
  }
  if (target.id === "chat-customer" || target.id === "chat-product") {
    if (target.id === "chat-customer") state.selectedCustomerId = target.value;
    else state.selectedProductId = target.value;
    const customer = selectedCustomer();
    const product = selectedProduct();
    state.chatMessages.push({ role: "bot", html: `<p class="chat-meta">上下文已切换：${customer.id} ${customer.name} · ${product.name}。后续回答将基于新上下文生成。</p>` });
    renderApp();
    return;
  }
  if (target.dataset.market) {
    state.marketViews[target.dataset.market] = target.value;
    updateStrategyLiveRegion();
  }
});

window.addEventListener("hashchange", () => {
  const nextPage = window.location.hash.replace("#", "");
  if (pageTitles[nextPage]) {
    state.page = nextPage;
    renderApp();
  }
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && event.target.id === "chat-input") {
    const question = event.target.value.trim();
    if (question) {
      event.target.value = "";
      askChat(question);
    }
  }
});

renderApp();
