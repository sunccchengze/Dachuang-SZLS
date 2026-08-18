#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""静态站质量门禁。

覆盖 16 个现役页面及站内附加 HTML，检查本地资源、普通超链接、统一导航、
内联/外部 JavaScript 语法、离线依赖、已删除模块残留、已知伪数据和关键页面
的“控制在上、动态图居中、Nature 静态证据沉底”顺序。
"""
from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
CORE_PAGES = [
    "index.html", "wake.html", "optimization.html", "solver.html",
    "dashboard.html", "array.html", "heatmap.html", "windrose.html",
    "pod.html", "model.html", "power_tracking.html", "3d_farm.html",
    "3d_surface.html", "3d_volume.html", "interface.html", "overview.html",
]
EXPECTED_NAV = CORE_PAGES[:-1] + ["overview.html"]
EXTRA_PAGES = ["index_v2.html", "slides_823.html"]
BANNED_TEXT = {
    "aerodynamic_demo.html": "已删除模块残留",
    "7000吨": "无来源碳减排旧文案",
    "340万元": "无来源金额旧文案",
    "42.5%": "已废弃阵列占位值",
    "PPO多种子MAE稳定性": "未执行多模型种子评测",
    "5种子 MAE": "未执行多模型种子评测",
}
BANNED_CODE = {
    "i < 3 ? 1460": "3D 风场硬编码伪功率",
    "920 : 660": "3D 风场硬编码伪功率",
    "type: 'path'": "Plotly 非法仪表路径",
    'type: "path"': "Plotly 非法仪表路径",
}


class RefParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        for key in ("href", "src", "poster"):
            if key in attr:
                self.refs.append((tag, key, attr[key]))


def clean_ref(ref):
    return ref.split("#", 1)[0].split("?", 1)[0]


def is_ignored_ref(ref):
    return not ref or ref.startswith(("#", "data:", "mailto:", "javascript:"))


def node_check(source, label, module=False):
    suffix = ".mjs" if module else ".js"
    with tempfile.NamedTemporaryFile("w", suffix=suffix, encoding="utf-8", delete=False) as fh:
        fh.write(source)
        temp = Path(fh.name)
    try:
        result = subprocess.run(["node", "--check", str(temp)], capture_output=True, text=True)
    finally:
        temp.unlink(missing_ok=True)
    if result.returncode:
        return f"{label} JavaScript 语法错误：{result.stderr.strip()}"
    return None


def main():
    errors = []
    warnings = []
    print("=" * 68)
    print("风电场偏航优化静态站质量门禁")
    print("=" * 68)

    for name in CORE_PAGES + EXTRA_PAGES:
        if not (SITE / name).exists():
            errors.append(f"缺少页面：{name}")

    # 全部 HTML 的 href/src/poster 与离线依赖。
    for path in sorted(SITE.glob("*.html")):
        content = path.read_text(encoding="utf-8")
        parser = RefParser()
        parser.feed(content)
        for tag, attr, ref in parser.refs:
            if is_ignored_ref(ref):
                continue
            if ref.startswith(("http://", "https://")):
                errors.append(f"{path.name} 仍依赖外部资源：{ref}")
                continue
            target = (SITE / clean_ref(ref)).resolve()
            if not target.exists():
                errors.append(f"{path.name} 的 {tag}[{attr}] 死链：{ref}")

        for text, reason in BANNED_TEXT.items():
            if text in content:
                errors.append(f"{path.name} 含 {reason}：{text}")
        if re.search(r"[\U0001F300-\U0001FAFF▶⏸✓✅⚠❌⟳]", content):
            errors.append(f"{path.name} 含装饰性 Emoji 或播放符号")

        illegal_latex = set(re.findall(r"\\(?:nwarrow|nearrow|le|text|gamma|approx)\b", content))
        if illegal_latex:
            warnings.append(f"{path.name} 发现未编译 LaTeX：{sorted(illegal_latex)}")

        # 仅检查无 src、无特殊 MIME type 的内联 JavaScript。
        scripts = re.findall(r"<script(?P<attrs>[^>]*)>(?P<body>.*?)</script>", content, re.S | re.I)
        for index, (attrs, body) in enumerate(scripts, 1):
            if re.search(r"\bsrc\s*=", attrs, re.I):
                continue
            type_match = re.search(r"\btype\s*=\s*['\"]([^'\"]+)", attrs, re.I)
            script_type = type_match.group(1).lower() if type_match else ""
            if script_type in {"importmap", "application/json"} or not body.strip():
                continue
            issue = node_check(body, f"{path.name} 内联脚本 #{index}", module=script_type == "module")
            if issue:
                errors.append(issue)

    # 16 页统一导航：顺序、数量和目标必须完全一致。
    for name in CORE_PAGES:
        content = (SITE / name).read_text(encoding="utf-8")
        nav_match = re.search(r'<div class="t-nav-links".*?</div>\s*</div>', content, re.S)
        if not nav_match:
            errors.append(f"{name} 缺少统一模块导航")
            continue
        links = re.findall(r'href="([^"]+\.html)"', nav_match.group(0))
        if links != EXPECTED_NAV:
            errors.append(f"{name} 导航集合或顺序不一致：{links}")

    # 外部项目脚本语法；vendor 库只校验文件存在与固定版本。
    for path in sorted((SITE / "assets" / "js").glob("*.js")):
        source = path.read_text(encoding="utf-8")
        for text, reason in BANNED_CODE.items():
            if text in source:
                errors.append(f"{path.relative_to(SITE)} 含 {reason}：{text}")
        issue = node_check(source, str(path.relative_to(SITE)), module=path.name == "farm.js")
        if issue:
            errors.append(issue)

    # CSS 的 url() 资源与远程 @import。
    for path in sorted((SITE / "css").glob("*.css")):
        content = path.read_text(encoding="utf-8")
        if re.search(r"https?://", content):
            errors.append(f"{path.relative_to(SITE)} 仍含远程 CSS 依赖")
        for ref in re.findall(r"url\(['\"]?([^)'\"]+)", content):
            if is_ignored_ref(ref) or ref.startswith(("http://", "https://")):
                continue
            if not (path.parent / clean_ref(ref)).resolve().exists():
                errors.append(f"{path.relative_to(SITE)} 的 url() 死链：{ref}")

    # 尾流页必须保持“控制在上、动态图居中、Nature 图沉底”。
    wake = (SITE / "wake.html").read_text(encoding="utf-8")
    order_tokens = ['id="yawSlider"', 'id="fieldPlot"', 'fig1_tandem_yaw.png']
    positions = [wake.find(token) for token in order_tokens]
    if any(p < 0 for p in positions) or positions != sorted(positions):
        errors.append(f"wake.html 动静态顺序错误：{dict(zip(order_tokens, positions))}")

    # 依赖必须本地锁定。
    required_vendor = [
        SITE / "assets/vendor/plotly/plotly-2.35.2.min.js",
        SITE / "assets/vendor/three/three.module.js",
        SITE / "assets/vendor/three/addons/controls/OrbitControls.js",
        SITE / "assets/fonts/geist/Geist-Variable.woff2",
        SITE / "assets/fonts/geist/GeistMono-Variable.woff2",
    ]
    for path in required_vendor:
        if not path.exists() or path.stat().st_size == 0:
            errors.append(f"缺少本地离线依赖：{path.relative_to(ROOT)}")

    print(f"扫描完成：{len(errors)} 个阻断错误，{len(warnings)} 个警告。")
    for message in warnings:
        print("警告：" + message)
    for message in errors:
        print("错误：" + message)
    if errors:
        print("=" * 68)
        print("质量门禁失败。")
        return 1
    print("16 个现役页面及附加页面通过资源、导航、脚本和离线检查。")
    print("=" * 68)
    return 0


if __name__ == "__main__":
    sys.exit(main())
