// 数据来源 / 模型状态 全局配置与状态条。
// 真实数据替换时，只改本文件的 CONFIG 与（可选）PROVENANCE，界面其余部分零改动。
// 被每页在 nav.js 之后加载；自动在 <nav> 下方插入一条可关闭的状态条。
(function () {
  // ===== 替换真实数据时只改这里 =====
  var CONFIG = {
    // 数据成熟度："sim"（仿真占位）| "provisional"（初步真实）| "validated"（已验证）
    maturity: "sim",
    dataSource: "FLORIS 4.6.6 · GCH 工程尾流模型（模拟占位数据）",
    surrogate: "二维双线性插值（待替换为神经网络代理模型）",
    optimizer: "网格搜索 argmax(P₁+P₂)（待接入真实优化算法）",
    // 数据可信域：超出此范围的插值为外推，会在状态条中提示
    trustDomain: {
      windSpeed: [6, 12],   // m/s
      yaw: [-30, 30]        // °
    },
    // 设为 true 可彻底关闭状态条（正式答辩/发布时如已验证可关）
    hidden: false
  };
  window.WF_DATA_CONFIG = CONFIG;

  var MATURITY_META = {
    sim:         { label: "模拟占位", cls: "wf-banner-sim",     icon: "🧪" },
    provisional: { label: "初步真实", cls: "wf-banner-prov",    icon: "🟡" },
    validated:   { label: "已验证",   cls: "wf-banner-valid",   icon: "✅" }
  };

  function outOfRangeNote() {
    var notes = [];
    // 页面可通过 window.WF_PAGE_CONTEXT 声明当前风速/偏航，做越界提示
    var ctx = window.WF_PAGE_CONTEXT || {};
    var td = CONFIG.trustDomain;
    if (typeof ctx.U === "number" && (ctx.U < td.windSpeed[0] || ctx.U > td.windSpeed[1])) {
      notes.push("风速 " + ctx.U + " m/s 超出可信域 " + td.windSpeed[0] + "–" + td.windSpeed[1]);
    }
    if (typeof ctx.yaw === "number" && (ctx.yaw < td.yaw[0] || ctx.yaw > td.yaw[1])) {
      notes.push("偏航 " + ctx.yaw + "° 超出可信域 " + td.yaw[0] + "–" + td.yaw[1]);
    }
    return notes;
  }

  function inject() {
    if (CONFIG.hidden) return;
    if (document.querySelector(".wf-banner")) return; // 防重复
    var meta = MATURITY_META[CONFIG.maturity] || MATURITY_META.sim;
    var nav = document.querySelector("nav");
    if (!nav) return;

    var bar = document.createElement("div");
    bar.className = "wf-banner " + meta.cls;
    bar.innerHTML =
      '<span class="wf-banner-icon">' + meta.icon + "</span>" +
      '<span class="wf-banner-tag">数据状态：' + meta.label + "</span>" +
      '<span class="wf-banner-sep">·</span>' +
      '<span class="wf-banner-text">流场：' + CONFIG.dataSource + "</span>" +
      '<span class="wf-banner-sep">·</span>' +
      '<span class="wf-banner-text">代理模型：' + CONFIG.surrogate + "</span>" +
      '<button class="wf-banner-close" title="关闭本页状态条" aria-label="关闭">×</button>';

    var warn = outOfRangeNote();
    if (warn.length) {
      var w = document.createElement("div");
      w.className = "wf-banner-warn";
      w.textContent = "⚠️ 外推提示：" + warn.join("；") + "（插值结果仅供参考）";
      bar.appendChild(w);
    }

    var spacer = document.createElement("div");
    spacer.className = "wf-banner-spacer";
    nav.insertAdjacentElement("afterend", bar);
    bar.insertAdjacentElement("afterend", spacer);

    function setOffset() { spacer.style.height = bar.offsetHeight + "px"; }
    setOffset();
    window.addEventListener("resize", setOffset);

    bar.querySelector(".wf-banner-close").addEventListener("click", function () {
      bar.style.display = "none";
      spacer.style.height = "0px";
    });
  }

  if (document.readyState !== "loading") inject();
  else document.addEventListener("DOMContentLoaded", inject);
})();
