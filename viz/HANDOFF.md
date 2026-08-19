# HANDOFF.md — 历史交接索引

> 本文件原先保存 2026-08-10 至 2026-08-18 的研发中交接指令。网页已于 **2026-08-19** 最终封板，旧的“继续改版”“调用大师/技能”及阶段战役说明全部失效，不得再作为执行依据。

## 当前唯一交接入口

1. `HANDOFF_NEXT_AGENT.md`：最终产品状态、可信数字、部署方式、审计结果和维护边界。
2. `FREEZE.md`：`v1.3-final` 冻结范围、最终门禁和变更禁令。
3. `README.md` / `site/README.md`：项目入口、数据管道和静态部署说明。

## 最终状态

- 固定分支：`arena/01a012f1-wind-farm-viz`。
- 现役产品：`site/` 下 15 页纯静态站，导航 `00–13 + MAP`。
- 状态：`FINAL`，不再新增页面或继续视觉重构。
- 最终代码审计基线：`21a385e1 chore(site): harden final release checks and assets`。

历史物理口径、错误记录与研发过程仍可通过 Git 历史和 `.learnings/` 查阅；如历史文本与最终交接冲突，一律以 `HANDOFF_NEXT_AGENT.md` 和 `FREEZE.md` 为准。
