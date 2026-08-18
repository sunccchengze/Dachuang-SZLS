# 网页封板记录：v1.1-data-trust

**分支**：`arena/01a012f1-wind-farm-viz`
**日期**：2026-08-18
**状态**：功能冻结；后续只修渲染、布局、死链、数据契约和文字溢出问题。

## 本轮封板范围

- `af6d9b12`：PPO 真实 200 回合评测数据替换模拟轨迹和虚构五种子图。
- `f81220ea`：四策略生成同源、3D 功率硬编码清除、死链修复、离线依赖和质量门禁升级。
- `69e2b075`：尾流页精密浅色设计重构，保留动态在上、静态证据沉底。
- `699927fc`：3D 策略几何与 FLORIS 数值速度场边界写清，几何扰动改为确定性。

## 质量门禁

```bash
python3 site/check_contract.py
python3 site/verify_all_pages.py
```

封板结果：

- 源 CSV/JSON、`data.js`、`data_3d.js`、`data_3d_real.js` 同源通过。
- 16 个现役页面及 `index_v2.html`、`slides_823.html` 资源检查通过。
- 普通链接、CSS URL、JavaScript 语法、统一导航、离线依赖和已知伪数据扫描 0 错误、0 警告。
- Plotly 2.35.2、Three.js 0.160.0、Geist 1.7.2 已存入仓库，核心站点断网可用。
- `site/test_wake_runtime.js` 已接入全站门禁：加载真实 `data.js/data_3d.js` 并执行尾流页内联脚本；0°与 +25°均创建三幅 Plotly 图，+25°得到 P₁=1459 kW、P₂=909 kW、Ptot=2368 kW、增益 +8.13%。

## 现役资产

- `site/`：16 页产品导航，另含主页原型和组会 Web Deck。
- `figures_nature/`：17 张科研图（主工厂 9 张、扩展 8 张），提供 PDF/PNG，部分另有 SVG/灰度版。
- `20260810洪/extracted/ppo_eval_traces.json`：200 回合逐回合指标与真实代表轨迹。
- `array_independent_result.json`：四策略总功率和四组九机功率。
- `site/assets/vendor/`：本地 Plotly/Three.js；`site/assets/fonts/geist/`：本地字体与许可证。

## 科研表达边界

1. FLORIS 结果是数值模拟，不写成现场实测。
2. `power_tracking.html` 的浏览器交互是双线性代理反向搜索，不写成浏览器 PPO 推理。
3. PPO 当前只验证 seed 42 权重的 200 个测试回合，不声称五模型种子稳定性。
4. 3×3 尾流包络是确定性策略示意；双机速度纹理读取 FLORIS 三维网格。
5. 前两排 +30°策略增益按 `9934.99/8095.15` 同源公式取两位小数为 `22.73%`。

## 演示主线

`index → wake → optimization → array → dashboard → pod → 3d_farm`

推荐现场动作：

1. 在 `wake.html` 拖动 0°到 +25°，说明上游让利和下游回升。
2. 在 `array.html` 切换四策略，落到 `[30,20,0]° / +24.04%`。
3. 在 `3d_farm.html` 先展示九机策略，再切双机 FLORIS 数据，并主动说明辅助流管不是 CFD 等值面。

## 冻结规则

不新增页面，不恢复已删除的势流彩蛋，不增加无数据来源的指标、种子、速度场或经济收益。任何数字改动必须先修改源文件和生成脚本，再重建前端数据并通过两道门禁。
