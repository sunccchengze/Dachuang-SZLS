# 成员工作清单（team inventory）

> 目的：把“谁做了什么”列清楚，便于阶段交付时各取所需、避免重复劳动。
> 标注（推测）的条目为根据文件名 / 内容推断，请在组会上确认归属。

## 一、按成员划分

### 袁夫达（建模组）
| 产出 | 文件 / 位置 | 状态 | 下一步 |
| --- | --- | --- | --- |
| FLORIS GCH/CC 数据生成 | `floris(1).zip` → `output_cc/`、`output_gch/` 的 `training_data_*.csv`、`train_wind_farm_model.py` | 已完成（1224 样本 / 套） | 原始 input 文件夹与批处理脚本归档进仓库 |
| 3×3 阵列数据 | `generate_array_data.py`、`cases_array.csv` | 已完成 | 与洪组优化脚本对齐格式 |
| 风玫瑰数据 | `generate_windrose_data.py`、`cases_windrose.csv`、`cases_windrose_opt.csv` | 已完成 | 写入交付包 |
| 流场数据（FLORIS） | `generate_*_fields.py`、`fields/` `fields_3d/` `fields_array/` `.npz` | 已完成（工程模型） | 推进 Fluent 高保真 |

### 厉今飞（AI 组，项目主持人）
| 产出 | 文件 / 位置 | 状态 | 下一步 |
| --- | --- | --- | --- |
| 神经网络代理模型 | `floris(1).zip` → `wind_farm_results/wind_farm_power_model.keras`、`test_metrics.csv`、`true_vs_pred_*.png` | 已完成（CC/GCH 两套，R²≈0.998） | 与可视化接口对齐（Q1） |
| 数据 / 模型说明 | `floris(1).zip` → `说明.docx` | 已完成 | 转成 `research_overview.md` 的技术小节 |
| 大创申请书 | `20260329-大创申请书-终版.docx` | 终版 | 作为项目目标基准 |

### 田铭雨（仿真组）
| 产出 | 文件 / 位置 | 状态 | 下一步 |
| --- | --- | --- | --- |
| 流场快照 | `fields/*.npz`（13 工况）、`fields_3d/yaw_*.npz`、`fields_array/*.npz` | 已完成（FLORIS） | 接 Fluent 高保真 |
| POD 本征正交分解 | `pod_analysis.py`、`pod_results/` | 进行中 | 明确 POD 用途：降维代理 or PINN 模态基（Q13） |
| 流场校验 | `check_fields.py`、`check_fields.png` | 已完成 | — |

### 洪祖名（优化控制组）
| 产出 | 文件 / 位置 | 状态 | 下一步 |
| --- | --- | --- | --- |
| 双机偏航优化 | `optimizer_result.json`（yaw 0→25°，+8.13%） | 已完成 | 接入可视化与电网需求追踪 |
| 9 机阵列优化 | `generate_array_independent.py`、`array_independent_result.json`（独立 +24.04%、统一 +14.87%） | 已完成 | 扩展到大风场（Q15） |
| 独立偏航策略 | `genarate_independent_field.py` | 进行中 | 与田组流场联动验证 |

### 孙承泽（可视化组，本分支维护人）
| 产出 | 文件 / 位置 | 状态 | 下一步 |
| --- | --- | --- | --- |
| Streamlit 演示系统 | `app.py`、`pages/dashboard.py` | 已完成（plotly_dark 修复） | 统一 NN / 插值模型接口 |
| 动画与图 | `animation.py`、`export_gif.py`、`array_animation.gif`、`wake_animation.gif`、`my_first_wake.png` | 已完成 | 写入交付包 |
| 双机插值代理（后端） | `surrogate_model.py`（读 `cases_multi.csv`） | 已完成（过渡模型） | 评估是否替换为厉的 NN（Q1） |
| 文档中心 | `docs/*` | 维护中 | 持续更新 |

## 二、按数据/资产类型划分

| 资产 | 关键文件 | 负责人（主） |
| --- | --- | --- |
| 原始样本（CC/GCH 1224） | `floris(1).zip` | 袁夫达 |
| 神经网络模型与指标 | `floris(1).zip` → `wind_farm_results/` | 厉今飞 |
| 双机偏航扫掠 | `cases.csv`、`cases_multi.csv` | 袁夫达 / 孙承泽 |
| 阵列与风玫瑰 | `cases_array.csv`、`cases_windrose*.csv` | 袁夫达 |
| 流场快照 | `fields/`、`fields_3d/`、`fields_array/` | 田铭雨 |
| 优化结果 | `optimizer_result.json`、`array_independent_result.json` | 洪祖名 |
| 演示与文档 | `app.py`、`pages/`、`docs/` | 孙承泽 |

## 三、协作链路（现状）

```
袁夫达(FLORIS数据) ─┐
厉今飞(NN模型)     ─┼─► 孙承泽(可视化/插值后端) ─► 全组可看
田铭雨(流场/POD)   ─┤
洪祖名(优化结果)   ─┘
```

**已知卡点**：可视化目前吃的是 `cases_multi.csv` 的双机插值，而非厉今飞的 NN；优化结果（洪）以 JSON 写死，尚未在演示系统里做成可调。详见 `question.md` Q1、Q4、Q14。
