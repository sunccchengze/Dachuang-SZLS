# HANDOFF_NEXT · 当前阶段交接（2026-09-13，R38 收口轮）

> 上一版本文写于 2026-08-28（`arena/01a04884-0824-2026`），其"尚未完成"清单**大半已在本仓后续 10 轮中解决**，
> 已整体重写。历史版本可从 `git log -- HANDOFF_NEXT.md` 取回；第 2 任的完整交接见 [`HANDOFF.md`](HANDOFF.md)
> （那份也已加"历史文档"声明与过期数字速查）。

## 一句话口径（准确的，不是好看的）

**信息口径与联动闭环已收口（docs/07/08，P0/P1/P2 全绿并留证据）；场景层已从"灰色噪声平板"推进到
R29→R37 的海洋/海岸/森林/天空/色温体系，工程基线全绿（selftest 84/84、lint 0/0、tsc 0 错、build ✓）。
仍未做的集中在三处：真实数据接入与 V&V（E 类）、渲染体系的性能与 LOD 口径、以及本轮列出的场景残项。
不要用"可以直接答辩"这类表述。**

## 现状（2026-09-13 实测）

- 提交：main = `bd5f5e8`（R37 日照金山），113 commits，0 open PR；
- `npm run selftest` **84/84** · `npm run lint` **0/0** · `npx tsc -b --noEmit` **0 错** · `npm run build` **✓ 1.36s**；
- 单帧渲染计数（`?q=high&t=15&cam=60,22,990`）：**250 draw calls / 636,718 tris**（medium 250/562,318、low 222/417,538）；
- 取证链路：`bash twin/scripts/bootstrap.sh` 一键恢复 npm + 无头 Chromium（NSS 桩库）；
  `npm run perftier` 出三档基线；`scripts/{shot,abdiff,framestats,horizoncheck,sunprobe,moontrack}.mjs|py` 出像素证据。

## 开放项（本轮 R38 逐项处理，状态见 `docs/research/round38_残项收口与裁决.md` §三）

1. 门面文档口径回填（README / twin/README / HANDOFF）——**已做**；
2. 仓库卫生：`twin/shots/` 下 **16 个 0 字节 PNG 假证据**、`twin/docs/` 与 `docs/` 双证据树、根目录 180 kB 参考 zip；
3. "全部进 CI 可跑"目前**没有仓库内 CI**（`.github/workflows` 不存在）；
4. 首帧后 2.5–5.1 s 长尖峰（`treeField` 4800 株延迟落位一次性采样，未分帧摊销）；
5. 片元波系与顶点 Gerstner **不同源**（泡沫/浪脊/高光骑在另一套波上）+ 海面用**平涂 skyRef** 而非真天空反射
   + 云掩日不掩月 —— 三项来自孤儿分支 `01a074a3` 的正确诊断，见裁决；
6. 塔基涌浪实测量级 **±16.8 m**（场心 amp 0.5）是否合理 → 独立专项；
7. low 档远岸森林实例数 = 0（整片消失，不是 LOD）；
8. 岛/海岬无树（`treeAccept` 把岛心判为山地带）；
9. `grassField` 自 R32 起写好但**连续 6 轮未挂载**；
10. 碎浪带只有视觉，未与 HUD 浪高/音频同源；
11. 帧率与 Pages 首屏无实测基线（README 里 1.18s / 382 kB 是 08-24 选型期 PoC 数）；
12. Round-9 记的 `STALE-PENDING-RESHOOT`（v3 全套 after_* 重拍承诺）未见兑现记录。

## 仍然有效的红线（沿袭 docs/03 / docs/04 / HANDOFF §8）

- 全息线稿美学不回退：不引入写实 PBR 机身、不开 Bloom 糊白线；
- **暗调冰青 / 低饱和莫兰迪 / 克制不惹眼 / 不引入新色相**；任何改动必须过"海面/天空不得比基线更亮"的守卫；
- 不虚构数据来源：接不了真 FLORIS/SCADA 就写"演示/代理/示意"，meta、README、界面角标三处必须一致；
- `terrainSurfaceY` 是唯一贴地真值，波浪等视觉位移**不得污染**静态贴地基准（selftest 有断言）；
- 大改前先出 before/after 对比，逐条给根因，不接受参数创可贴；
- **帧率类数字不得引用沙箱值**（SwiftShader + 2 核），只作档间相对比较；实机 GPU 另行验收。

## 交付门槛（沿用 2026-08-28 定的九条，未废止）

1. 每个 P0：代码 + 运行验证 + 前后对比图；2. 全部 P1 处理；3. P2 可见问题清零；
4. `npm run build` 通过；5. `npm run lint` 无 error 且剩余 warning 有解释；
6. 1920×1080 固定机位 + ≥2 方位 + 窄/移动尺寸检查；7. 滑杆/播放暂停/时间轴/告警/矩阵/3D 真实联动；
8. `docs/08` 无"待完成/待截图"条目；9. 交付说明区分 真实 / 演示 / 示意。

当前对照：**1–7 已达成并留证（docs/08 §〇）**；8 由本轮 R38 收口；9 已上界面角标与 README。
