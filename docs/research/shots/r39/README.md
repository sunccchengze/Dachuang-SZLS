# r39 —— T4（波系同源 / 真天空反射 / 云掩日月次序）的 before/after 证据

> 轮次记录：`docs/research/round39_分支合并与T4落地.md` §四
> 渲染环境：沙箱 SwiftShader 软渲染（**帧率无意义，只做同参像素对照**）
> 机位/时刻：`?debug=1&t=10&cam=60,22,990`（日间）、`?debug=1&t=22&cam=60,22,990`（夜间），1600×900

| 图 | 说明 |
|---|---|
| `before_hero_1600.png` / `after_hero_1600.png` | 日间；before = `b143c81`（R38 合并后、T4 之前），after = T4 之后 |
| `before_night_1600.png` / `after_night_1600.png` | 夜间；同上口径 |
| `after_hero.png` | 1920×1080 单张留档（T4 之后）——**没有配对的 before**，不作为对照证据 |

**量化结论**（`twin/scripts/framestats.py`，数字见 round39 §四 表）：
日间全局 mean 0.3308→0.3305、夜间 0.1820→0.1836；色相不漂；`lum>0.50` 占比两场景均**下降**
（4.25%→4.06% / 2.45%→2.40%）→ 无新增过曝。

**复现**（沙箱需先 `bash twin/scripts/bootstrap.sh`）：

```bash
cd twin && npm run dev -- --host 0.0.0.0 &
node scripts/shot.mjs 'http://127.0.0.1:5173/?debug=1&t=10&cam=60,22,990' ../docs/research/shots/r39/after_hero_1600.png 12000 1600 900
python3 scripts/framestats.py ../docs/research/shots/r39/before_hero_1600.png ../docs/research/shots/r39/after_hero_1600.png
```
