// WealthOps 页面图表库（纯前端，无第三方依赖）。
// 数据来自 viz-data.js（由 tableau_data/build_viz_data.py 生成）。
// 每个页面挂载一个最具代表性的 Tableau 风格图表，带筛选器与悬浮提示。
(function () {
  "use strict";

  var D = window.VIZ_DATA || {};

  var ASSET_COLORS = {
    "现金/货币": "#2563a8",
    "固收/理财": "#0f766e",
    "固收+": "#22714f",
    "权益基金/ETF": "#6952a8",
    "黄金/另类": "#a86405",
  };

  // 每个图表自己的筛选状态，跨重渲染保留
  var F = {
    strategy: { branch: "全部" },
    segment: { branch: "全部", asset: "全部" },
    diagnosis: { branch: "全部" },
    product: { risk: "R2" },
    governance: { metric: "全部" },
  };

  // ---------- 工具 ----------
  function uniq(a) { return a.filter(function (v, i) { return a.indexOf(v) === i; }); }
  function sum(a) { return a.reduce(function (s, x) { return s + (+x || 0); }, 0); }
  function avg(a) { return a.length ? sum(a) / a.length : 0; }
  function money(v) {
    v = +v; var s = v < 0 ? "-" : ""; v = Math.abs(v);
    if (v >= 1e8) return s + "¥" + (v / 1e8).toFixed(2) + "亿";
    if (v >= 1e4) return s + "¥" + Math.round(v / 1e4) + "万";
    return s + "¥" + Math.round(v);
  }
  function pct(v, d) { return (v * 100).toFixed(d == null ? 0 : d) + "%"; }
  function signPct(v) { return (v >= 0 ? "+" : "") + (v * 100).toFixed(1) + "%"; }
  function hexToRgb(h) { h = h.replace("#", ""); return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)]; }
  function mix(a, b, t) {
    t = Math.max(0, Math.min(1, t));
    var x = hexToRgb(a), y = hexToRgb(b);
    return "rgb(" + Math.round(x[0] + (y[0] - x[0]) * t) + "," + Math.round(x[1] + (y[1] - x[1]) * t) + "," + Math.round(x[2] + (y[2] - x[2]) * t) + ")";
  }
  function gapColor(g) {
    var t = Math.min(1, Math.abs(g) / 0.18);
    return g >= 0 ? mix("#eef2ee", "#b42318", t) : mix("#eef2ee", "#0f766e", t);
  }
  function walletColor(w) { return mix("#e3ede9", "#0f766e", Math.max(0, Math.min(1, (w - 0.45) / 0.3))); }

  // 悬浮提示（单例）
  var tip;
  function showTip(html, x, y) {
    if (!tip) { tip = document.createElement("div"); tip.className = "viz-tip"; document.body.appendChild(tip); }
    tip.innerHTML = html; tip.style.display = "block";
    var w = 240;
    tip.style.left = Math.min(window.innerWidth - w, x + 14) + "px";
    tip.style.top = (y + 14) + "px";
  }
  function hideTip() { if (tip) tip.style.display = "none"; }
  function wireTips(root) {
    root.querySelectorAll("[data-tip]").forEach(function (el) {
      el.addEventListener("mousemove", function (e) { showTip(el.getAttribute("data-tip"), e.clientX, e.clientY); });
      el.addEventListener("mouseleave", hideTip);
    });
  }

  function filterBar(defs) {
    return '<div class="viz-filter">' + defs.map(function (d) {
      return '<label class="viz-ctl"><span>' + d.label + '</span><select data-f="' + d.id + '">' +
        d.options.map(function (o) { return '<option value="' + o + '"' + (o === d.value ? " selected" : "") + ">" + o + "</option>"; }).join("") +
        "</select></label>";
    }).join("") + "</div>";
  }

  function shell(container, opt) {
    container.innerHTML =
      '<div class="viz-head"><div><div class="viz-title">' + opt.title + '</div>' +
      '<div class="viz-sub">' + opt.sub + "</div></div>" + (opt.filter || "") + "</div>" +
      '<div class="viz-canvas"></div>' +
      '<div class="viz-foot">' + (opt.source || "") + "</div>";
    return container.querySelector(".viz-canvas");
  }

  function bindFilter(container, key, draw) {
    container.addEventListener("change", function (e) {
      if (e.target.dataset && e.target.dataset.f) { F[key][e.target.dataset.f] = e.target.value; draw(); }
    });
  }

  // ---------- 图1 · 配置缺口热力矩阵（strategy） ----------
  function mountStrategy() {
    var c = document.getElementById("viz-strategy");
    if (!c) return;
    var canvas = shell(c, {
      title: "配置缺口热力矩阵（Tableau Public）",
      sub: "使用外部仪表板替代本地热力矩阵，保留交互筛选能力",
      source: '来源：SPD1 | Tableau Public · <a href="https://public.tableau.com/app/profile/wenbo.bi/viz/SPD1_17828965970110/Dashboard1?publish=yes" target="_blank" rel="noopener noreferrer">新窗口打开</a>',
    });
    canvas.innerHTML =
      '<div class="viz-embed-wrap">' +
      '<iframe class="viz-embed" title="SPD1 Tableau Dashboard" src="https://public.tableau.com/views/SPD1_17828965970110/Dashboard1?:showVizHome=no" loading="lazy" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>' +
      '</div>' +
      '<div class="viz-embed-note">若公司网络策略阻止嵌入，请使用下方链接在新窗口打开 Tableau Public。</div>';
  }

  // ---------- 图2 · 服务机会转化漏斗（segment） ----------
  function mountSegment() {
    var c = document.getElementById("viz-segment"); if (!c || !D.funnel) return;
    var branches = ["全部"].concat(uniq(D.funnel.map(function (r) { return r.branch; })));
    var assets = ["全部"].concat(uniq(D.funnel.map(function (r) { return r.asset_class; })));
    function draw() {
      var f = F.segment;
      var canvas = shell(c, {
        title: "配置服务机会转化漏斗",
        sub: "机会客户 → 触达 → 方案 → 成交 · " + f.branch + " · " + f.asset,
        filter: filterBar([
          { label: "分行", id: "branch", options: branches, value: f.branch },
          { label: "资产", id: "asset", options: assets, value: f.asset },
        ]),
        source: "数据：09_rebalance_action_funnel · " + (D.funnel_month || ""),
      });
      var rows = D.funnel.filter(function (r) { return (f.branch === "全部" || r.branch === f.branch) && (f.asset === "全部" || r.asset_class === f.asset); });
      var a = {
        target: sum(rows.map(function (r) { return r.target; })),
        contacted: sum(rows.map(function (r) { return r.contacted; })),
        proposal: sum(rows.map(function (r) { return r.proposal; })),
        converted: sum(rows.map(function (r) { return r.converted; })),
        opp: sum(rows.map(function (r) { return r.opportunity; })),
        conv: sum(rows.map(function (r) { return r.converted_amount; })),
      };
      var stages = [["机会客户", a.target, "#2563a8"], ["已触达", a.contacted, "#0f766e"], ["已出方案", a.proposal, "#6952a8"], ["已成交", a.converted, "#22714f"]];
      var top = Math.max(a.target, 1);
      var html = '<div class="funnel">' + stages.map(function (s) {
        var w = Math.max(4, (s[1] / top) * 100), rate = (s[1] / top * 100).toFixed(0);
        return '<div class="fn-row"><div class="fn-label">' + s[0] + '</div><div class="fn-track">' +
          '<div class="fn-bar" style="width:' + w + "%;background:" + s[2] + '" data-tip="' + s[0] + "<br>客户数 <b>" + s[1] + "</b><br>占机会客户 " + rate + '%"></div>' +
          '<span class="fn-val">' + s[1] + " · " + rate + "%</span></div></div>";
      }).join("") + "</div>";
      html += '<div class="viz-stat"><div><span>机会金额</span><strong>' + money(a.opp) + "</strong></div>" +
        "<div><span>已承接金额</span><strong>" + money(a.conv) + "</strong></div>" +
        "<div><span>金额完成率</span><strong>" + pct(a.opp ? a.conv / a.opp : 0, 1) + "</strong></div></div>";
      canvas.innerHTML = html;
      wireTips(canvas);
    }
    bindFilter(c, "segment", draw);
    draw();
  }

  // ---------- 图3 · 客户生命周期漏斗（diagnosis） ----------
  function mountDiagnosis() {
    var c = document.getElementById("viz-diagnosis"); if (!c || !D.lifecycle) return;
    var branches = ["全部"].concat(uniq(D.lifecycle.map(function (r) { return r.branch; })));
    function draw() {
      var b = F.diagnosis.branch;
      var canvas = shell(c, {
        title: "客户生命周期阶段漏斗",
        sub: "各阶段客户规模与钱包份额（颜色深=份额高）· " + b,
        filter: filterBar([{ label: "分行", id: "branch", options: branches, value: b }]),
        source: "数据：03_lifecycle_funnel",
      });
      var agg = [1, 2, 3, 4].map(function (o) {
        var rows = D.lifecycle.filter(function (r) { return r.stage_order === o && (b === "全部" || r.branch === b); });
        var cnt = sum(rows.map(function (r) { return r.customer_count; }));
        return {
          life: rows[0].life_stage, cnt: cnt,
          ws: cnt ? sum(rows.map(function (r) { return r.avg_wallet_share * r.customer_count; })) / cnt : 0,
          post: cnt ? sum(rows.map(function (r) { return r.post_invest_completion * r.customer_count; })) / cnt : 0,
          touch: rows[0].key_touchpoint, pain: rows[0].key_painpoint,
        };
      });
      var top = Math.max.apply(null, agg.map(function (a) { return a.cnt; }).concat([1]));
      var html = '<div class="funnel">' + agg.map(function (a) {
        var w = Math.max(6, (a.cnt / top) * 100);
        return '<div class="fn-row"><div class="fn-label">' + a.life + '</div><div class="fn-track">' +
          '<div class="fn-bar" style="width:' + w + "%;background:" + walletColor(a.ws) + '" data-tip="' + a.life + "<br>客户数 <b>" + a.cnt + "</b> 户<br>钱包份额 <b>" + pct(a.ws) + "</b> · 投后完成 " + pct(a.post) + "<br>触点：" + a.touch + "<br>痛点：" + a.pain + '"></div>' +
          '<span class="fn-val">' + a.cnt + " 户 · 钱包 " + pct(a.ws) + "</span></div></div>";
      }).join("") + "</div>";
      html += '<div class="viz-legend"><span>钱包份额低</span><i class="lg" style="background:' + walletColor(0.45) + '"></i><i class="lg" style="background:' + walletColor(0.6) + '"></i><i class="lg" style="background:' + walletColor(0.75) + '"></i><span>高</span></div>';
      canvas.innerHTML = html;
      wireTips(canvas);
    }
    bindFilter(c, "diagnosis", draw);
    draw();
  }

  // ---------- 图4 · 产品适配气泡矩阵（product） ----------
  function mountProduct() {
    var c = document.getElementById("viz-product"); if (!c || !D.products) return;
    var risks = ["R2", "R3", "R4"];
    function draw() {
      var rk = F.product.risk;
      var canvas = shell(c, {
        title: "产品适配气泡矩阵",
        sub: "预期收益 × 建议期限，气泡=可投放容量，颜色=资产类别 · " + rk,
        filter: filterBar([{ label: "目标风险", id: "risk", options: risks, value: rk }]),
        source: "数据：08_product_recommendation",
      });
      var rows = D.products.filter(function (p) { return p.target_risk_level === rk; });
      canvas.innerHTML = scatterSvg(rows) + assetLegend(rows);
      wireTips(canvas);
    }
    bindFilter(c, "product", draw);
    draw();
  }

  function scatterSvg(rows) {
    var W = 720, H = 320, L = 54, R = 18, T = 16, B = 44, pw = W - L - R, ph = H - T - B;
    var mids = rows.map(function (p) { return (p.ret_low + p.ret_high) / 2; });
    var xmax = Math.max.apply(null, mids.concat([0.02])) * 1.15;
    var ymax = Math.max.apply(null, rows.map(function (p) { return p.duration_months; }).concat([6])) * 1.1;
    var caps = rows.map(function (p) { return p.capacity_amount; });
    var cmin = Math.min.apply(null, caps), cmax = Math.max.apply(null, caps);
    function x(v) { return L + (v / xmax) * pw; }
    function y(v) { return T + ph - (v / ymax) * ph; }
    function rad(v) { return cmax === cmin ? 12 : 6 + (v - cmin) / (cmax - cmin) * 14; }
    var s = '<svg class="viz-svg" viewBox="0 0 ' + W + " " + H + '" preserveAspectRatio="xMidYMid meet">';
    // Y 网格与刻度（期限）
    [0, 6, 12, 18, 24].filter(function (v) { return v <= ymax; }).forEach(function (v) {
      s += '<line x1="' + L + '" y1="' + y(v) + '" x2="' + (W - R) + '" y2="' + y(v) + '" class="viz-grid"/>';
      s += '<text x="' + (L - 8) + '" y="' + (y(v) + 4) + '" class="viz-axis" text-anchor="end">' + v + "月</text>";
    });
    // X 刻度（收益）
    for (var k = 0; k <= 4; k++) {
      var xv = xmax * k / 4;
      s += '<text x="' + x(xv) + '" y="' + (H - B + 18) + '" class="viz-axis" text-anchor="middle">' + (xv * 100).toFixed(1) + "%</text>";
    }
    s += '<text x="' + (L + pw / 2) + '" y="' + (H - 6) + '" class="viz-axis-title" text-anchor="middle">预期年化收益（中值）</text>';
    s += '<text x="14" y="' + (T + ph / 2) + '" class="viz-axis-title" text-anchor="middle" transform="rotate(-90 14 ' + (T + ph / 2) + ')">建议持有期限（月）</text>';
    // 气泡
    rows.forEach(function (p) {
      var mid = (p.ret_low + p.ret_high) / 2;
      s += '<circle cx="' + x(mid).toFixed(1) + '" cy="' + y(p.duration_months).toFixed(1) + '" r="' + rad(p.capacity_amount).toFixed(1) +
        '" fill="' + (ASSET_COLORS[p.asset_class] || "#888") + '" fill-opacity="0.8" stroke="#fff" stroke-width="1" data-tip="' +
        p.product_name + "<br>" + p.product_type + " · " + p.product_risk_level + "<br>收益 " + pct(p.ret_low, 1) + "~" + pct(p.ret_high, 1) +
        "<br>期限 " + p.duration_months + "月 · 流动性 " + p.liquidity + "<br>容量 " + money(p.capacity_amount) + " · " + p.recommendation_tag + '"/>';
    });
    s += "</svg>";
    return s;
  }

  function assetLegend(rows) {
    var present = uniq(rows.map(function (r) { return r.asset_class; }));
    return '<div class="viz-legend">' + present.map(function (a) {
      return '<span class="lg-chip"><i class="lg" style="background:' + (ASSET_COLORS[a] || "#888") + '"></i>' + a + "</span>";
    }).join("") + "</div>";
  }

  // ---------- 图5 · 智能体治理监控趋势（governance） ----------
  function mountGovernance() {
    var c = document.getElementById("viz-governance"); if (!c || !D.governance) return;
    var metrics = ["全部", "引用率", "幻觉率", "采纳率"];
    function draw() {
      var m = F.governance.metric;
      var canvas = shell(c, {
        title: "智能体治理监控趋势",
        sub: "调用量（柱）+ 质量指标（线）· 版本 v0.1→v0.3 · " + m,
        filter: filterBar([{ label: "指标线", id: "metric", options: metrics, value: m }]),
        source: "数据：02_governance_trend · 近90天",
      });
      canvas.innerHTML = trendSvg(m) + trendLegend(m);
      wireTips(canvas);
    }
    bindFilter(c, "governance", draw);
    draw();
  }

  function trendSvg(metric) {
    var g = D.governance, n = g.length;
    var W = 720, H = 320, L = 46, R = 46, T = 30, B = 52, pw = W - L - R, ph = H - T - B;
    var callsMax = Math.max.apply(null, g.map(function (d) { return d.ai_calls; })) * 1.15;
    function x(i) { return L + (i + 0.5) * (pw / n); }
    function yc(v) { return T + ph - (v / callsMax) * ph; }
    function yr(v) { return T + ph - v * ph; }
    var bw = (pw / n) * 0.7;
    var s = '<svg class="viz-svg" viewBox="0 0 ' + W + " " + H + '" preserveAspectRatio="xMidYMid meet">';
    // 版本背景带（按版本自动分段）
    var bandColors = ["rgba(37,99,168,0.05)", "rgba(105,82,168,0.06)", "rgba(34,113,79,0.06)"];
    var bands = [], bi = 0, bk = 0;
    while (bi < n) {
      var vv = g[bi].version, bstart = bi;
      while (bi < n && g[bi].version === vv) bi++;
      bands.push([bstart, bi, vv, bandColors[bk % bandColors.length]]);
      bk++;
    }
    bands.forEach(function (bd) {
      var x0 = L + bd[0] * (pw / n), x1 = L + bd[1] * (pw / n);
      s += '<rect x="' + x0 + '" y="' + T + '" width="' + (x1 - x0) + '" height="' + ph + '" fill="' + bd[3] + '"/>';
      s += '<text x="' + ((x0 + x1) / 2) + '" y="' + (T - 10) + '" class="viz-axis" text-anchor="middle">' + bd[2] + "</text>";
    });
    // 左轴（调用量）
    for (var k = 0; k <= 4; k++) {
      var cv = callsMax * k / 4;
      s += '<line x1="' + L + '" y1="' + yc(cv) + '" x2="' + (W - R) + '" y2="' + yc(cv) + '" class="viz-grid"/>';
      s += '<text x="' + (L - 8) + '" y="' + (yc(cv) + 4) + '" class="viz-axis" text-anchor="end">' + Math.round(cv) + "</text>";
    }
    // 右轴（%）
    [0, 0.25, 0.5, 0.75, 1].forEach(function (rv) {
      s += '<text x="' + (W - R + 8) + '" y="' + (yr(rv) + 4) + '" class="viz-axis" text-anchor="start">' + (rv * 100) + "%</text>";
    });
    // 柱（调用量）
    g.forEach(function (d, i) {
      s += '<rect x="' + (x(i) - bw / 2).toFixed(1) + '" y="' + yc(d.ai_calls).toFixed(1) + '" width="' + bw.toFixed(1) + '" height="' + (T + ph - yc(d.ai_calls)).toFixed(1) + '" fill="#cdd8e6"/>';
    });
    // 幻觉率阈值线
    if (metric === "全部" || metric === "幻觉率") {
      s += '<line x1="' + L + '" y1="' + yr(0.02) + '" x2="' + (W - R) + '" y2="' + yr(0.02) + '" class="viz-threshold"/>';
      s += '<text x="' + (W - R) + '" y="' + (yr(0.02) - 4) + '" class="viz-axis" text-anchor="end" fill="#b42318">幻觉率阈值 2%</text>';
    }
    // 折线
    var lines = [["citation_rate", "引用率", "#0f766e"], ["hallucination_rate", "幻觉率", "#b42318"], ["adopt_rate", "采纳率", "#22714f"]];
    lines.forEach(function (ln) {
      if (metric !== "全部" && metric !== ln[1]) return;
      var pts = g.map(function (d, i) { return x(i).toFixed(1) + "," + yr(d[ln[0]]).toFixed(1); }).join(" ");
      s += '<polyline points="' + pts + '" fill="none" stroke="' + ln[2] + '" stroke-width="2"/>';
      g.forEach(function (d, i) { s += '<circle cx="' + x(i).toFixed(1) + '" cy="' + yr(d[ln[0]]).toFixed(1) + '" r="2.4" fill="' + ln[2] + '"/>'; });
    });
    // X 轴标签（自适应密度）
    var lblStep = Math.max(1, Math.round(n / 12));
    g.forEach(function (d, i) {
      if (i % lblStep === 0 || i === n - 1) s += '<text x="' + x(i) + '" y="' + (H - B + 18) + '" class="viz-axis" text-anchor="middle">' + d.date.slice(5) + "</text>";
    });
    // 悬浮列
    g.forEach(function (d, i) {
      s += '<rect x="' + (L + i * (pw / n)).toFixed(1) + '" y="' + T + '" width="' + (pw / n).toFixed(1) + '" height="' + ph + '" fill="transparent" data-tip="' +
        d.date + " · " + d.version + "<br>调用量 <b>" + d.ai_calls + "</b><br>引用率 " + pct(d.citation_rate, 1) + " · 幻觉率 " + pct(d.hallucination_rate, 1) + "<br>采纳率 " + pct(d.adopt_rate, 1) + " · 人工复核 " + pct(d.manual_review_rate, 1) + '"/>';
    });
    s += "</svg>";
    return s;
  }

  function trendLegend(metric) {
    var items = [['<i class="lg" style="background:#cdd8e6"></i>调用量']];
    var lines = [["引用率", "#0f766e"], ["幻觉率", "#b42318"], ["采纳率", "#22714f"]];
    lines.forEach(function (l) { if (metric === "全部" || metric === l[0]) items.push(['<span class="lg-line" style="background:' + l[1] + '"></span>' + l[0]]); });
    return '<div class="viz-legend">' + items.map(function (i) { return '<span class="lg-chip">' + i + "</span>"; }).join("") + "</div>";
  }

  var MOUNTS = {
    strategy: mountStrategy,
    segment: mountSegment,
    diagnosis: mountDiagnosis,
    product: mountProduct,
    governance: function () {},
  };

  window.WealthViz = {
    mount: function (page) {
      var fn = MOUNTS[page];
      if (fn) { try { fn(); } catch (e) { console.error("viz mount error", page, e); } }
    },
  };
})();
