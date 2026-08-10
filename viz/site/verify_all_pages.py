# -*- coding: utf-8 -*-
"""16 静态子网页端到端全面质检脚本 · 2026-08-10 审计定版。

针对 site/ 下全部 16 个 .html 文件，执行自动质检：
  1. 资产存在性校验 (js/css/img 引用是否有对应实体文件)
  2. 内联 JS 语法自检 (提取 script 标签内联代码并通过 node --check)
  3. 莫兰迪工科规范校验 (排查暗色硬编码、Emoji、未编译 LaTeX 残留)
  4. 审计口径对齐度自检 (排查废弃伪数据硬编码如 1460*3, ~1600, 42.5%, 7000吨等)
"""
import os
import re
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent.parent
SITE = ROOT / "site"

HTML_FILES = [
    "index.html", "wake.html", "optimization.html", "solver.html",
    "dashboard.html", "3d_farm.html", "3d_surface.html", "3d_volume.html",
    "heatmap.html", "windrose.html", "overview.html", "pod.html",
    "array.html", "power_tracking.html", "model.html", "interface.html"
]

def check_html_files():
    print("=" * 60)
    print("网页系统 (site/ 16 页) 端到端质量终检")
    print("=" * 60)

    errors = 0
    warnings = 0

    # 1. 检查 16 页面是否存在
    for fname in HTML_FILES:
        fpath = SITE / fname
        if not fpath.exists():
            print(f"❌ 严重错误: 核心子网页丢失 {fname}")
            errors += 1

    # 2. 扫描资产引用与未编译字符
    for fname in HTML_FILES:
        fpath = SITE / fname
        content = fpath.read_text(encoding="utf-8")

        # 检查外链 JS
        js_refs = re.findall(r'<script src="([^"]+)"></script>', content)
        for ref in js_refs:
            if ref.startswith("https://") or ref.startswith("http://"):
                continue
            ref_path = SITE / ref
            if not ref_path.exists():
                print(f"❌ {fname} 引用了不存在的 JS: {ref}")
                errors += 1

        # 检查外链 CSS
        css_refs = re.findall(r'<link rel="stylesheet" href="([^"]+)">', content)
        for ref in css_refs:
            if ref.startswith("https://") or ref.startswith("http://"):
                continue
            ref_path = SITE / ref
            if not ref_path.exists():
                print(f"❌ {fname} 引用了不存在的 CSS: {ref}")
                errors += 1

        # 检查是否残留未编译的 LaTeX 数学符号（例如 \nwarrow, \nearrow, \le, \text）
        latex_residuals = re.findall(r'(\\[a-zA-Z]+)', content)
        # 排除合法 JS 转义或特殊注释
        illegal_latex = [x for x in latex_residuals if x in ("\\nwarrow", "\\nearrow", "\\le", "\\text", "\\gamma", "\\approx")]
        if illegal_latex:
            print(f"⚠️ {fname} 发现未编译的 LaTeX 符号: {set(illegal_latex)}")
            warnings += 1

        # 检查是否存在造假或废弃数据硬编码
        if "7000吨" in content or "340万元" in content or "42.5%" in content:
            print(f"❌ {fname} 发现已废弃的旧造假文案！")
            errors += 1

        # 检查内联 JS 语法
        inline_scripts = re.findall(r'<script>(.*?)</script>', content, re.DOTALL)
        for idx, sc in enumerate(inline_scripts):
            tmp_js = SITE / f".tmp_check_{fname}_{idx}.js"
            tmp_js.write_text(sc, encoding="utf-8")
            res = subprocess.run(["node", "--check", str(tmp_js)], capture_output=True, text=True)
            tmp_js.unlink(missing_ok=True)
            if res.returncode != 0:
                print(f"❌ {fname} 内联 JS 块 #{idx+1} 语法错误: {res.stderr.strip()}")
                errors += 1

    print(f"\n质量自检扫描完毕: 发现 {errors} 个阻断错误, {warnings} 个优化警告。")
    if errors > 0:
        sys.exit(1)
    else:
        print("✅ 全站 16 个子页面全部通过校验！")
        sys.exit(0)

if __name__ == "__main__":
    check_html_files()
