# model/ 交付状态（2026-08-10 存档）

| 文件 | 状态 |
|---|---|
| `ppo_tracking_v3_seed42.pt` | **契约文件名占位（0 B）**。原包即 0 B；复现工程未达标前，此名下不放任何权重——避免未验证策略冒充交付物。 |
| `ppo_repro_v1_nonconverged_DONOTSHIP.pt` | 复现 v1 产物（41 KB，901,120 步，seed 42）。**未收敛**（稳态 err 均值 250~600 kW 振荡，距 MAE<1.2% 口径尚远），仅存档供对照调试，禁止对外引用。 |

复现管线：`../ppo_repro_train.py`（v2，含 obs 归一化与奖励失真修正，就绪待跑）。
断点全文：`../../../.learnings/SESSION_ARCHIVE_20260810.md`。
