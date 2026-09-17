# r36/ocean_v2 —— 并行分支 a3 的像素证据（原样并入）

> 来源：分支 `arena/01a074a3-dachuang-szls`，commit `595daf2`（R36 海面/天空并行实现）。
> 2026-09-17 随该分支 merge（`44efb33`）一并入库；原先写在 `twin/docs/research/shots/r36/`，
> R38-T2「证据树合一」后本仓只有 `docs/research/` 一棵证据树，故归位到此处。

| 图 | 机位 / 时刻（`?debug=1`） | 说明 |
|---|---|---|
| `before_hero.png` / `after_hero.png` | `t=10&cam=60,22,990` | 海面从「平玻璃」→ 中浪浪脊 + 天光反射 |
| `before_coast.png` / `after_coast.png` | `t=10&cam=10,8,1500` | 低机位：岸线 90m 内浅水冰青 + 滚动碎浪带 |
| `before_night.png` / `after_night.png` | `t=22&cam=60,22,990` | 夜场：月光反射 / SSS |
| `before_sky2.png` / `after_sky2.png` | `t=14&cam=25,10,2600` | 天空：平渐变 → 冰青云族（覆盖率 ~30%） |
| `before_sky_day.png` | `t=14`（日间） | 天空云族对照（before 单边） |

**口径提醒（重要）**：这 9 张图是**那条并行分支自己的 before/after**，拍摄基线是该分支
（其父提交为 PR#7 的 `961d2f3`，不含主线 R36b/R36c/R37 的任何改动）。它们证明的是
「a3 当时的改动发生了哪些变化」，**不能**当作合并后主线的验收证据 —— 主线验收请看
`docs/research/shots/r36/`（R36 主线四机位）与 `docs/research/round39_*.md` 里 R39 的新图。

文字记录见 `docs/11_R36_场景细化_海洋天空v2借鉴.md`（已加合并状态抬头）。
