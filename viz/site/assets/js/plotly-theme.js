/* Plotly light Morandi theme + 全局配色令牌 */
(function () {
  // 同步 css/style.css :root 的设计令牌，供各页面统一引用
  window.WF = {
    bg: "#f1ede6", plotBg: "#f6f3ec", card: "#fbfaf6",
    txt: "#3b3f46", sub: "#73787f", grid: "#e2dccf", axis: "#b9b2a3",
    blue: "#6b8cae", blueDeep: "#547394", blueSoft: "#9db1c7",
    sage: "#8aa17a", sageDeep: "#6f8761",
    clay: "#b08968", lavender: "#8e88a6", gold: "#c2a86b", rose: "#b98484"
  };

  // 坐标轴/版式默认（浅底深字）
  window.PD = {
    paper_bgcolor: "rgba(0,0,0,0)", plot_bgcolor: WF.plotBg,
    font: { color: WF.txt, family: '"SF Pro Display","Inter",-apple-system,"PingFang SC","Noto Sans SC",sans-serif', size: 12 },
    margin: { l: 55, r: 20, t: 15, b: 45 },
    legend: { orientation: "h", y: -0.18, x: 0, font: { size: 11, color: WF.sub }, bgcolor: "rgba(0,0,0,0)" },
    hoverlabel: { bgcolor: WF.card, bordercolor: WF.axis, font: { color: WF.txt, size: 12 } }
  };
  window.PAx = { color: WF.sub, gridcolor: WF.grid, linecolor: WF.axis, zerolinecolor: WF.axis, tickfont: { color: WF.sub, size: 11 }, title: { font: { color: WF.txt, size: 12 } } };

  // 连续色：米杏 → 雾蓝（用于速度场/热力，低饱和）
  window.BlueSeq = [
    [0, "#ece3d2"], [0.2, "#c7d2df"], [0.4, "#9fb6cc"],
    [0.6, "#7d9ebb"], [0.8, "#5f85a8"], [1, "#466b8c"]
  ];
  // 热力增益：浅陶 → 雾蓝 → 鼠尾草
  window.BlueSeqMid = [
    [0, "#e7ddd0"], [0.5, "#9fb6cc"], [1, "#6f8761"]
  ];
  // 速度场云图：低速暖米 → 高速雾蓝（莫兰迪、投影可辨）
  window.FieldSeq = [
    [0, "#e8dfd0"], [0.25, "#cfc6b4"], [0.5, "#a9bdcf"],
    [0.75, "#7d9ebb"], [1, "#547394"]
  ];
  // 增益热力图：0% 浅米 → 中雾蓝 → 深雾蓝（纯正值顺序色阶，保证在白底上每一档都可见）
  window.GainSeq = [
    [0, "#f0e9dc"], [0.25, "#c2d1e0"], [0.5, "#84a4c2"],
    [0.75, "#547394"], [1, "#3a5470"]
  ];
  // 3D 体渲染蓝白色系：低速（尾流核心）乳白 → 高速背景深蓝
  window.VolumeSeq = [
    [0, "#f4f1ea"], [0.25, "#d6e0ea"], [0.5, "#a9c2d8"],
    [0.75, "#6f93b5"], [1, "#3a5470"]
  ];

  WF.FieldSeq = window.FieldSeq;
  WF.GainSeq = window.GainSeq;
  WF.BlueSeq = window.BlueSeq;
  WF.BlueSeqMid = window.BlueSeqMid;
  WF.VolumeSeq = window.VolumeSeq;

  // 浅底深度合并工具
  function ml(o) {
    var b = JSON.parse(JSON.stringify({
      paper_bgcolor: PD.paper_bgcolor, plot_bgcolor: PD.plot_bgcolor,
      font: PD.font, margin: PD.margin, legend: PD.legend, hoverlabel: PD.hoverlabel,
      xaxis: Object.assign({}, PAx), yaxis: Object.assign({}, PAx)
    }));
    (function d(t, s) {
      for (var k in s) {
        if (typeof s[k] === "object" && s[k] && !Array.isArray(s[k])) {
          t[k] = t[k] || {}; d(t[k], s[k]);
        } else t[k] = s[k];
      }
    })(b, o);
    return b;
  }
  window.ml = ml;

  // pr(id, traces, layout, cfg) — 统一应用主题
  window.pr = function (id, tr, ly, cfg) {
    Plotly.newPlot(id, tr, ml(ly), Object.assign({
      responsive: true, displayModeBar: "hover",
      modeBarButtonsToRemove: ["lasso2d", "select2d"]
    }, cfg || {}));
  };
})();
