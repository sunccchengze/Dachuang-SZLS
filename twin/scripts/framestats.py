#!/usr/bin/env python3
"""framestats.py — 无视觉能力下的客观帧分析。
用法: python3 framestats.py <img.png> [<img2.png> ...]
输出: 全图/九宫格亮度与色相统计、上方 1/3 天空带、中部海面带、饱和度分布。
"""
import sys
import numpy as np
from PIL import Image

def stats(path):
    im = np.asarray(Image.open(path).convert('RGB'), dtype=np.float32) / 255.0
    h, w, _ = im.shape
    lum = 0.2126 * im[..., 0] + 0.7152 * im[..., 1] + 0.0722 * im[..., 2]
    mx = im.max(axis=-1); mn = im.min(axis=-1)
    sat = np.where(mx > 1e-6, (mx - mn) / np.maximum(mx, 1e-6), 0)
    print(f'== {path}  {w}x{h}')
    print(f'  global   lum mean={lum.mean():.4f} p50={np.median(lum):.4f} p95={np.quantile(lum,0.95):.4f} p99={np.quantile(lum,0.99):.4f}  sat mean={sat.mean():.4f}')
    # 色相平均（只算有色像素）
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    tint = np.stack([r - lum, g - lum, b - lum], axis=-1)
    print(f'  tint     R-G={ (r-g).mean():+.4f}  G-B={ (g-b).mean():+.4f}  (正=偏暖/负=偏青)')
    bands = [('sky top 0-18%', 0.0, 0.18), ('horizon 18-38%', 0.18, 0.38), ('sea 38-70%', 0.38, 0.70), ('fore 70-100%', 0.70, 1.0)]
    for name, a, bnd in bands:
        seg = im[int(h*a):int(h*bnd)]
        lseg = lum[int(h*a):int(h*bnd)]
        sseg = sat[int(h*a):int(h*bnd)]
        rr, gg, bb = seg[..., 0].mean(), seg[..., 1].mean(), seg[..., 2].mean()
        print(f'  {name:16s} lum={lseg.mean():.4f} p95={np.quantile(lseg,0.95):.4f} sat={sseg.mean():.4f} rgb=({rr:.3f},{gg:.3f},{bb:.3f})')
    # 高亮像素占比（波光/雪/白线）
    for t in (0.35, 0.5, 0.75):
        frac = (lum > t).mean()
        print(f'  lum>{t:.2f}  frac={frac*100:6.2f}%')

for p in sys.argv[1:]:
    stats(p)
