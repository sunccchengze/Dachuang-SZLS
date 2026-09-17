# AEOLUS TWIN — 风电场偏航优化 · 数字孪生演示平台

> 用户原图「未来能源数字孪生系统」的高保真演示平台（1920×1080 等比舞台，深空蓝 · 纯白全息线稿）。
> 定位（docs/03 裁决）：大创结题法定交付物"多机协同智能功率控制与数字孪生演示平台"的**浏览器端演示形态**；零后端、完全离线。

## 技术栈
Vite 8 + React 19 + TS 6 + three 0.185 + R3F 9 + drei + @react-three/postprocessing + zustand。
字体全部 @fontsource 自托管（Noto Sans SC / Rajdhani / Share Tech Mono），无外部网络请求。

## 运行 / 自检
```bash
npm install
npm run dev        # http://localhost:5173/
npm run build      # tsc -b && vite build → dist/（0 错误）
npm run lint       # oxlint（0 警告 0 错误；R3F 每帧 ref/uniform 惯用法为带注释的文件级豁免）
npm run selftest   # 数据契约/渲染口径 84 断言（Node 22 原生类型剥离，无浏览器依赖）
node scripts/shot.mjs <url> <out.png> [settleMs] [w] [h]  # 无头自拍（沙箱需 /tmp/nsslibs，真机无需）
node scripts/probe.mjs <url含debug> [settleMs] [fpsMs]  # FPS/DrawCall/三角面/控制台错误探针
npm run perftier   # 三档画质单帧计数 + 帧时长（high/medium/low，同参同机位）
npm run verify     # ★ 四条闸门一次跑完：lint → selftest → tsc + build（CI 同口径）
node scripts/qa2.mjs <baseUrl含debug> <curtail.png> <optimize.png>  # 联动/闭环证据注入器
```

## 数据口径（诚实三分法，界面有同色角标）
| 角标 | 含义 | 本仓实例 |
|---|---|---|
| 【演示】 | 确定性演示数据皮肤，非实时/场站真值 | 功率总览、矩阵、雷达、告警流水 |
| 【代理】 | 浏览器端代理模型推算（Jensen k=0.06 + NREL 5MW 曲线） | 尾流损失、年电量推算、实时功率曲线、偏航寻优 |
| 【示意】 | 几何/构图示意，非工程数据 | 地形（程序噪声非 DEM）、场位 3×3 布局（列距 3.2–3.6D，未做微观选址）、升压站构造 |
| 真实 | 离线实算引用，**只出现在文档/报告**，不在演示界面与代理数字混写 | FLORIS：+24.04% 增益、97.97% 收敛、76.38% 捕获、MAE 0.523%（钦定表，docs/03） |

页脚固定声明：**浏览器端演示数据 · 非 SCADA/FLORIS 实时值**。遥测接入按 `src/data/telemetry.ts` 契约
（默认 DemoSource；`?ws=<url>` 启用 DTAP-JSON over WebSocket 骨架，断线自动回退演示源）。

## 运行语义（数据契约，docs/08 §一）
- 坐标：+x=东，+z=南；风从北来 = windFrom 0°；**偏航 0°=对北来风**（绝对机舱方位，无 +8° 魔法偏移）。
- 唯一真值源：`farmFrame(tHours, unitYaw[9], targetMW) → FarmFrame`（纯函数、确定性、双层 memo）。
  HUD / 3D（frameBus 推送）/ 告警 / 图表 / 雷达读同一对象——联动即同一帧。
- 闭环（研究内容③）：需求功率 4–45MW → derateFrac/curtail 反馈；一键寻优 → 9 机偏航角输出。
- 时间：真实 50s = 模拟 24h；可暂停/任意 seek（=任意时刻确定性回放）。

## 调试/QA 键（生产构建需先 `?debug=1` 解锁；dev 常开）
`?cam=方位角,仰角,距离[,tx,ty,tz]` 机位锁定（自动跳过开场）· `?t=10.2` 锁定时刻并暂停（A/B 截图可复现）
· `?noveil=1` 关闭风纱层 · `?q=low|medium|high` 画质锁定 · `?intro0=1` 跳过开场 ·
`window.__aeolus`（useSim/farmFrameNow）与 `window.__aeolus_stats()`（手动单帧渲染计数；
2026-09-13 实测 `?q=high` **250 draw calls / 636,718 tris**，medium 250/562,318，low 222/417,538）。

## 结构
```
src/
  data/       rng · turbinePhysics(NREL5MW+Jensen) · farmSim(真值源+寻优+告警引擎) · paths(等弧长LUT) · debug · telemetry(接入契约) · selftest 断言对象
  state/      simStore(zustand 控制态 + 时钟 + useFarmFrame)
  scene/      terrainUtil(世界真值) · turbine/geometry(NREL 5MW 参数化几何) · HoloTurbine/TurbineField
              CableNetwork · WindVeil · Substation · WorldTerrain · SkyAurora · SparkleGround
              TreeField(远岸森林, R36) · grassField(未挂载) · Callouts(防重叠/避让HUD) ·
              CameraRig(13节点+书签+跳过) · Effects(三档) · PerfGovernor · EnvSetup · frameBus
  hud/        Hud.tsx(1920×1080 等比舞台：KPI/矩阵/雷达/图表/控制台/告警/信息卡/时间轴)
scripts/      shot.mjs · shot2.mjs · shotlocal.mjs · probe.mjs · qa2.mjs · perftier.mjs ·
              sunprobe.mjs · moontrack.py · framestats.py · horizoncheck.py ·
              abdiff.py · selftest.mts · calibrateWake.mts · bootstrap.sh（沙箱一键恢复依赖）
```

## 已知边界（v3 阶段工作，非缺陷隐瞒）
- 浏览器内不集成 FLORIS（包体/依赖越"零后端"红线）；代理模型与 FLORIS 的系统偏差未实测（E7 口径见 docs/08 §四）。
- 多用户/权限/审计、真实 DEM 与测风塔接入、在线自整定控制：见 docs/02 路线图与 docs/08 §五。
- 构建 chunk>500kB 提示来自 three 单包（1,278 kB / gzip 384 kB）；业务代码 150 kB、floris3d 数据 130 kB 已各自分包。
- R29–R37 场景层进度与遗留：见 `../docs/research/round36_海岸真实化与远岸森林.md`（含 R36b/R36c/R37）
  与 `../docs/research/round38_残项收口与裁决.md`（草地组件 `grassField` 仍未挂载、岛上无树、软渲染性能口径等）。
- 帧率类数字**一律不要引用沙箱值**：SwiftShader 软件渲染（本沙箱 2 核）与真机 GPU 差一个量级，
  `npm run perftier` 只用于档间相对比较与计数回归。
