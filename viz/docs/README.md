# 风电场偏航优化可视化项目 · 文档中心

> 分支：`arena/019fd504-wind-farm-viz` ｜ 模块维护人：孙承泽（可视化）｜ 指导老师：李良星
> 本目录用于把**全组的工作**沉淀下来，给组内（厉今飞 / 袁夫达 / 田铭雨 / 洪祖名 / 孙承泽）一个统一、可查、可交付的阶段快照。

---

## 0. 怎么用这个 docs 文件夹

| 文件 | 作用 |
| --- | --- |
| `README.md`（本文件） | 总览 + 当前进度 + 给组内的阶段性交付说明 |
| `team_inventory.md` | 谁做了什么：文件 → 负责人 → 状态 → 下一步，一图看清全组资产 |
| `delivery_plan.md` | 阶段性交付方案：里程碑 M0–M5、各组交付物、集成点、时间线 |
| `research_overview.md` | 研究目标拆解 + 方法合理性分析（直接回应李良星老师建议 3、4） |
| `question.md` | **李良星老师对孙承泽的 20 个问题**（角色代入，分 7 类） |
| `communication_log.md` | 群内关键沟通记录（厉今飞 / 袁夫达 / 李良星） |
| `chat_20260808_digest.md` | ⚠️ 待补充——2026-08-08 群聊压缩包尚未进入工作区，收到后立即消化补入 |

---

## 1. 当前进度（一句话）

**数据底座（袁 / 厉）→ 代理模型（厉 NN + 孙插值）→ 可视化演示系统（孙）→ 阵列偏航优化（洪，双机 +8.1%、9 机阵列独立偏航 +24.0%）** 已形成一条**可演示闭环**；PINN 物理融合与智能调控闭环为下一阶段。

---

## 2. 给组内的“阶段性交付”是什么

详见 `delivery_plan.md`。阶段一（当前可交付）的核心交付物：

1. **可视化演示系统（孙承泽）**：`app.py` + `pages/dashboard.py` + 动画（`array_animation.gif` / `wake_animation.gif`），全组可点开看。
2. **数据底座说明（袁夫达）**：FLORIS GCH/CC 1224 样本 + 3×3 阵列 / 风玫瑰数据的来源与合理性。
3. **代理模型报告（厉今飞）**：NN 架构、测试指标（CC/GCH R²≈0.998）、激活函数选择理由。
4. **阵列优化结果（洪祖名）**：贪心 / 统一 / 独立偏航增益汇总（`optimizer_result.json` / `array_independent_result.json`）。
5. **仿真流场（田铭雨）**：FLORIS 流场 `.npz`（`fields/` `fields_3d/` `fields_array/`）+ POD 模态分析（`pod_analysis.py`）。

把上面 5 份用本 docs 串成一份“阶段一交付包”，即可在组会 / 中期检查直接汇报。

---

## 3. 如何本地运行

```bash
pip install -r requirements.txt
streamlit run app.py
# 多页：streamlit run pages/dashboard.py
```

数据 / 模型入口：

- 双机插值代理：`surrogate_model.py`（读 `cases_multi.csv`，`RegularGridInterpolator`）
- FLORIS 神经网络代理（厉）：`floris(1).zip` → `output_cc/`、`output_gch/` 下的 `.keras` 模型与指标
- 流场生成 / 优化脚本：`generate_*.py`、`pod_analysis.py`

---

## 4. 已知缺口 / 待办

- ⚠️ **2026-08-08 群聊压缩包未收到**（见 `chat_20260808_digest.md`），收到后立刻消化并补入沟通记录与交付计划。
- PINN 物理融合尚未启动（申请书路线中的第二环）。
- 真·高保真 CFD（Fluent）数据待田组推进，目前 `fields/` 均为 FLORIS 工程尾流模型输出。
- 可视化（孙）与神经网络模型（厉）的接口尚未统一（见 `question.md` Q1）。
