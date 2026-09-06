#!/usr/bin/env python3
"""moontrack.py — 画面中月轮定位：上半天空最亮致密光斑的质心/峰值/面积。
用法: python3 moontrack.py <frame.png> [...]
用途：月落/月出动画的客观验证（质心高度应随时间下降；托底 bug 则高度恒定）。
"""
import sys
import numpy as np
from PIL import Image

def track(path):
    im = np.asarray(Image.open(path).convert('RGB'), dtype=np.float32) / 255.0
    h, w, _ = im.shape
    lum = 0.2126 * im[..., 0] + 0.7152 * im[..., 1] + 0.0722 * im[..., 2]
    # 天空区：上 55% 高 × 中部 56% 宽（避开 HUD 侧栏与海面月路/波光）
    x0, x1 = int(w * 0.22), int(w * 0.78)
    y1 = int(h * 0.55)
    sky = lum[0:y1, x0:x1]
    idx = np.argmax(sky)
    my0, mx0 = np.unravel_index(idx, sky.shape)
    peak = sky[my0, mx0]
    if peak < 0.45:
        print(f'{path.split("/")[-1]:28s} moon: NOT FOUND (sky peak={peak:.2f})')
        return
    # 月轮+内晕：argmax 周围 90px 窗内 > peak*0.72 的像素聚类
    yy0, yy1 = max(0, my0 - 90), min(y1, my0 + 90)
    xx0, xx1 = max(0, mx0 - 90), min(sky.shape[1], mx0 + 90)
    win = sky[yy0:yy1, xx0:xx1]
    mask = win > max(peak * 0.72, 0.5)
    ys, xs = np.where(mask)
    my = yy0 + ys.mean()
    mx = xx0 + xs.mean() + x0
    print(f'{path.split("/")[-1]:28s} moon: x={mx:6.0f} y={my:6.0f} (y%={my/h*100:4.1f}%) '
          f'peak={peak:.3f} area={len(ys)}px r≈{(len(ys)/np.pi)**0.5:.1f}')

for p in sys.argv[1:]:
    track(p)
