# 风电场偏航优化可视化系统

西安交通大学 · 能源与动力工程学院 · 大学生创新训练项目
可视化与交互系统模块负责人：孙承泽 ｜ 指导教师：李良星 副教授
团队成员：田铭雨（CFD 仿真）· 袁夫达（降阶与代理模型）· 厉今飞（基线数据）· 洪祖名（优化与 PPO）

---

## 两个形态

| 形态 | 状态 | 入口 |
|---|---|---|
| 纯静态演示系统（`site/`，16 页） | **现役产品**，Cloudflare Pages 部署 | https://wind-farm-viz.pages.dev/ |
| Streamlit 应用（`app.py` + `pages/`，10 页） | 留档本地工具，离线探索与答辩断网备胎 | 本地 `streamlit run app.py` |

静态站零后端：数据经构建脚本注入 `assets/data*.js`，浏览器内双线性插值（`assets/js/interp.js`），Plotly.js / three.js 出图。

## 静态站页面（16 页）

| 页面 | 文件 | 一句话 |
|---|---|---|
| 主页 | `index.html` | 项目入口、KPI、偏航原理图 |
| 尾流分析 | `wake.html` | 偏航角滑块联动尾流云图与功率 |
| 优化结果 | `optimization.html` | 0° vs +25° 对比，含速度场与功率分解 |
| 优化求解器 | `solver.html` | 任意风速实时搜索最优偏航角，算法开销对比表（实测） |
| Dashboard | `dashboard.html` | 数据-物理-控制一屏总控 |
| 3D 风电场 | `3d_farm.html` | 九机 three.js 场景，转子旋转与尾流偏转 |
| 3D 尾流曲面 | `3d_surface.html` | 三维速度曲面 |
| 3D 体渲染 | `3d_volume.html` | 尾流低速泡等值面 |
| 热力矩阵 | `heatmap.html` | 偏航角 × 风速增益矩阵 |
| 风玫瑰与 AEP | `windrose.html` | 12 风向实扫描收益，AEP 等权假设显式声明 |
| 数据总览 | `overview.html` | 全工况表与分解曲线 |
| POD 降阶 | `pod.html` | 模态能量 76.4% / 21.6%，前 2 阶累计 98.0%（97.97%） |
| 3×3 阵列优化 | `array.html` | 统一 +14.87% / 逐排贪心 +24.04% |
| 功率需求跟踪 | `power_tracking.html` | 目标功率反求偏航角 |
| 模型精度 | `model.html` | XGBoost 图源级佐证（仓内复现资产待补） |
| 统一数据接口 | `interface.html` | 三组数据契约与接入状态 |

## 快速开始

```bash
# 静态站本地预览(零依赖)
python3 -m http.server 8000 --directory site

# Streamlit 留档工具
pip install -r requirements.txt
streamlit run app.py
```

## 数据管道

```bash
python generate_data.py             # 两台串列 8 m/s × 13 偏航 → cases.csv + fields/
python generate_multiwind_data.py   # 4 风速 × 13 偏航 → cases_multi.csv
python generate_3d_data.py          # 5 偏航 × 9 高度层 → fields_3d/
python generate_array_data.py       # 3×3 阵列统一偏航 → cases_array.csv
python generate_array_independent.py# 阵列逐排贪心优化 → array_independent_result.json
python generate_windrose_data.py    # 12 风向 × 4 风速 × 13 偏航 → cases_windrose*.csv
python pod_analysis.py              # POD/SVD 分解 → pod_results/
python site/build_data.py           # csv/json → site/assets/data.js(纯标准库)
python site/build_3d_data.py        # npz → site/assets/data_3d.js
python site/check_contract.py       # 契约自检(部署前必跑,退出码非 0 禁部署)
python site/benchmark_solver.py     # solver 页算法对比表复跑口径
```

## 数据契约（三组接口，字段形状不可变更）

### 仿真组：`cases.csv` / `fields/case_XXXX.npz` / `fields_3d/yaw_±XX.npz`

| 变量 | 形状 | 单位 | 说明 |
|---|---|---|---|
| x / y | (128,) / (64,) | m | 顺风 / 横向坐标 |
| u | (64, 128) | m/s | 轮毂高度水平截面风速（绝对风速，不归一化） |
| 3D 版 | x(64,) y(32,) z(9,)，u(9,32,64) | m/s | 20~180 m 九层 |

### 控制组：`optimizer_result.json` 与功率跟踪函数

`find_yaw_for_target(target_power, U_inf) -> (best_yaw, actual_power, error_pct)`，放入 `surrogate_model.py` 覆盖同名函数即可被留档页自动调用；静态站等价契约见下。

### AI 组：`predict_power`

- Python（留档）：`predict_power(yaw_angle, U_inf) -> (p1, p2)` kW
- JS（静态站 `assets/js/interp.js`）：`predict_power(yaw, U) -> {p1, p2, ptot, outOfRange, reasons}`，可信域 6~12 m/s、±30°，越界自动提示

## 当前数据口径（2026-08-10 审计定版）

| 项 | 口径 |
|---|---|
| 仿真来源 | FLORIS 4.6.6 默认配置：GCH（gauss 速度/偏转 + 二次转向 + 偏航附加恢复 + 横向速度） |
| 风机 | NREL 5MW（额定 5 MW @ 11.4 m/s，轮毂 90 m，转子标称 126 m） |
| 两台串列 | 间距 5D，8 m/s，TI 6%：最优 +25°，全场 +8.13%（本地复现偏差 < 0.01 kW） |
| 3×3 阵列 | 第一排偏航 +14.87%、前两排接力 +22.72% (9935 kW)、逐排贪心 [30/20/0]° +24.04%（Row 均速 7.97 / 5.10 / 5.31 m/s） |
| POD | 前 2 阶累计 97.97%（模态 0 偶极子 76.4%，模态 1 恢复 21.6%） |
| 风玫瑰（两台串列） | 仅 270° 正对扇区有收益；等权 ΔAEP +0.51%，西风 30% 示例 +1.97% |
| 风玫瑰（3×3 阵列） | 12 风向双通道贪心（7536 次求解）：8 扇区非零——轴向 90°/270° +24.0% 级、列轴 0°/180° +21.6%、晶格对角 60°/120°/240°/300° +10.7~11.3%；等权 ΔAEP +8.86%，西风 30% 示例 +11.37%（8 m/s 口径） |
| PPO 闭环 | 200 独立测试回合实测稳态 MAE = 0.523% (< 1.2%)、平均调节时间 = 0.944 s (~0.8 s)、稳态零抖动（4 维契约权重 55 KB） |
| 待补全 | XGBoost 精度（图表 png 已有，原始压缩包资产待补） |

每页顶部有数据状态条；全部数字的可信口径见 `.learnings/AUDIT_20260810.md`（审计台账）。

## 依赖

`requirements.txt` 已锁定验证区间：Python 3.11（审计复核环境）与 3.13（开发机），FLORIS 钉死 4.6.6（API 敏感），其余给出已验证上下限。静态站 `site/` 不依赖任何 Python 包。

## 仓库治理

- 工作分支：`arena/019feacd-wind-farm-viz`（Cloudflare Pages 生产分支同此）；历史基线 `arena/019fe42f-wind-farm-viz`；**永不 merge 到 `main`**。
- 交接与计划：`HANDOFF.md`、`14_DAYS_MASTER_PLAN.md`、`.learnings/`（更正/错误/特性/审计四类记忆）。
- 提交约定：小步、单主题、每个 diff 可追溯到实证来源；任何数字改动必须附复算路径。
