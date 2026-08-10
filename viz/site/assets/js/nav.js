// 统一顶部导航注入与高亮状态同步。
// - 自动识别当前页面（支持带 .html 或 Cloudflare Pages clean URLs 无扩展名路由）。
// - 无论页面是手写导航还是空容器，均自动、动态、精准地为当前页面添加 .active 高亮类。
// - 在窄屏水平滚动时，自动将激活项滚动至可视区域中央。
(function () {
  var ITEMS = [
    ["index.html", "首页"],
    ["wake.html", "尾流"],
    ["optimization.html", "优化"],
    ["overview.html", "总览"],
    ["3d_surface.html", "3D曲面"],
    ["3d_volume.html", "3D体"],
    ["3d_farm.html", "3D风场"],
    ["heatmap.html", "热力矩阵"],
    ["solver.html", "求解器"],
    ["pod.html", "POD"],
    ["array.html", "阵列"],
    ["power_tracking.html", "功率跟踪"],
    ["dashboard.html", "Dashboard"],
    ["windrose.html", "风玫瑰"],
    ["model.html", "模型精度"],
    ["interface.html", "接口"]
  ];

  function getSlug(path) {
    if (!path) return "index";
    var s = (path.split("/").pop() || "index").toLowerCase();
    s = s.replace(/\.html$/, "").replace(/\/$/, "");
    if (s === "" || s === "index") s = "index";
    return s;
  }

  function init() {
    var curSlug = getSlug(location.pathname);

    document.querySelectorAll(".nav-links").forEach(function (nav) {
      // 1. 如果容器为空，自动注入 16 个标准化链接
      if (nav.children.length === 0) {
        ITEMS.forEach(function (it) {
          var a = document.createElement("a");
          a.href = it[0];
          a.textContent = it[1];
          var itSlug = getSlug(it[0]);
          if (itSlug === curSlug) {
            a.className = "active";
          }
          nav.appendChild(a);
        });
      } else {
        // 2. 如果已有手写链接，动态核验并设置 active 类
        var links = nav.querySelectorAll("a");
        links.forEach(function (a) {
          var href = a.getAttribute("href") || "";
          var aSlug = getSlug(href);
          var isCurrent = (aSlug === curSlug);
          if (isCurrent) {
            a.classList.add("active");
          } else {
            a.classList.remove("active");
          }
        });
      }

      // 3. 自动将激活标签平滑滚动至视口可见位置
      var activeEl = nav.querySelector(".active");
      if (activeEl && typeof activeEl.scrollIntoView === "function") {
        try {
          activeEl.scrollIntoView({ inline: "center", block: "nearest", behavior: "smooth" });
        } catch (e) {
          // 容错降级
        }
      }
    });
  }

  if (document.readyState !== "loading") {
    init();
  } else {
    document.addEventListener("DOMContentLoaded", init);
  }
})();
