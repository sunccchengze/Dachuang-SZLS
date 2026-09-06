#!/usr/bin/env python3
"""horizoncheck.py — 地平线假缝检测：中央列带逐行平均亮度，找最大行间台阶。
用法: python3 horizoncheck.py <a.png> <b.png>
输出: 每图最大 |Δrow| 位置/幅度 + 0.30~0.70 画面高区间的台阶排名（Top5）。
"""
import sys
import numpy as np
from PIL import Image

def analyze(path):
    im = np.asarray(Image.open(path).convert('L'), dtype=np.float32) / 255.0
    h, w = im.shape
    band = im[:, int(w*0.35):int(w*0.65)]  # 中央 30% 列带，避开 HUD 侧栏
    rows = band.mean(axis=1)
    d = np.abs(np.diff(rows))
    # 只看画面 25%~75% 高度（海平线/切边预期落区）
    lo, hi = int(h*0.25), int(h*0.75)
    top = np.argsort(d[lo:hi])[::-1][:5] + lo
    print(f'== {path}')
    print(f'  全图最大台阶: row={int(np.argmax(d))}/{h} |ΔL|={d.max():.4f}')
    for r in sorted(top):
        print(f'    row={r} (y={r/h*100:.1f}%) |ΔL|={d[r]:.4f}  L({r-1})={rows[r-1]:.3f} → L({r})={rows[r]:.3f}')
    return d

for p in sys.argv[1:3]:
    analyze(p)
