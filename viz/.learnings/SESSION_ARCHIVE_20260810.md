# 会话断点存档 · 2026-08-10（PPO 复现工程暂停点）

> 用途：本会话被用户主动暂停于此。恢复工作时以此文件为唯一真相入口。
> 分支纪律不变：只推 `arena/019feacd-wind-farm-viz`，永不 merge main。

## 一、已完成且已推送（commit 链 44dacabd → b6a17de8 → 54a6631c）

1. **3×3 阵列全风向贪心扫描**（`generate_array_windrose.py` 双通道版，自检通过：
   270°/8 m/s 锚点 8095.15 / 10041.46 kW 复现）：
   12 风向×4 风速×157 求解 = 7536 次；八扇区结构（轴向 90/270° +24.0% 级、
   列轴 0/180° +21.6%、晶格对角 +10.7~11.3%、四斜向≈0）；等权 ΔAEP +8.86%。
   全链路：data.js（`array_rose`）、windrose.html 双布局切换、契约校验扩展，全绿。
2. **P2 清理**：array.html 深挖坐实 4 处隐藏造假（占位值、unified 伪数组与口径错乱、
   对比柱图硬编码、desc 编造值）全部修复并对齐 csv/json 锚点；Streamlit 留档
   「三次样条」文案、cos^1.5 注释；pod_analysis.py 死分支删除。
   台账：`.learnings/AUDIT_20260810.md` §五/§六。

## 二、PPO 复现工程 · 精确断点（本轮唯一未完事项）

### 包体解剖结论（事实，已坐实）
- `model/ppo_tracking_v3_seed42.pt` 原包为 **0 B 占位**；train/eval/demo 三脚本逐字节
  相同，均不训练不加载权重；env obs 实现 3 维 ≠ 汇报契约 4 维（缺 power_current）；
  env 物理上限 p_base@8 m/s = 1759.6 kW < 默认 target 1800 kW（**指标口径不可达**，stub
  冒烟可复现：10×2.5° 后 P=1462.5、err=337.5 kW）；「42% 平滑度」无基线定义。

### 已落盘修复（本次已提交）
- `simplified_turbine_env.py`：obs 对齐 4 维契约 `[u_inf, yaw, power_current, target]`；
  原 stub 冒烟通过（4 维打印正常）。
- `ppo_repro_train.py`（新）：忠实复现训练管线，显式假设 5 条钉死在 docstring
  （dt=0.1 s/step、target∈[0.35,0.99]·p_base、u∈[6,12]、奖励原结构整体 ×0.01、
  obs 归一化）。
- `model/README.md`：`ppo_repro_v1_nonconverged_DONOTSHIP.pt`（v1 产物 41 KB，
  901,120 步未收敛，err 250~600 kW 振荡）仅存档对照；契约文件名恢复 0 B 占位
  ——**未达标前此名下不放权重**。

### v1 失败机理（推断，证据=训练日志）
- 观测裸值（p≈千级）直灌 tanh → 激活饱和，梯度信号弱；
- 奖励缩放只作用于误差项（err×0.01 而 0.05|a| 未缩放）→ err:action 相对权重被
  扭曲 100×，保真性破坏。v2 已两处修正。

### 恢复动作清单（按序）
1. `cd 20260810洪/extracted && python3 ppo_repro_train.py`（CPU 数分钟，600 iters）；
   验收：训练尾段 abs_err_mean 应降到 **<20 kW 量级**（≈1.2% 口径的前置迹象），否则
   继续调（熵正则/课程式 target 域收窄）再报断点。
2. 编写 `ppo_repro_eval.py`（未写）：200 个随机 episode（seed 固定），
   指标=稳态 MAE%（后 50% 步）、调节时间（dt=0.1 s，进 ±1.5% 带不回逸）、
   动作变化率 mean|a| 与贪心基线对比 → `metrics_repro.json`。
3. 达标后：权重落契约名 `model/ppo_tracking_v3_seed42.pt`；`site/interface.html`
   L66 注记换实测口径；台账补 §七；未达标则如实记录差异（42% 平滑度等）。
4. 全仓验证：`python3 site/check_contract.py`；提交推送。

### 环境注（事实）
- 沙箱 Python 3.11：torch 2.13.0+cu130（`pip --break-system-packages`，沙箱级；
  仓库 requirements.txt **未动**——PPO 复现为留档侧工程，不污染站点依赖）；
  floris 4.6.6 / numpy 2.4.6 / scipy 1.17.1 / pandas 3.0.5 已装。

## 三、待用户决策（恢复时以选择题确认）
- 「我选4」消歧：第三轮问题列表的 4 = PPO 重训（本工程，已开工被叫停）；
  前一轮的 4 = P2 清理（已完成）。ask_user 卡片两轮返回 skipped——恢复时
  先确认卡片可见性。
- 下轮候选：① PPO v2 续跑验收 ② 本地预览验收 ③ 增设「前两排+30°」第 4 策略卡
  （9935 kW/+22.72%，新授信）④ 答辩素材战役。
