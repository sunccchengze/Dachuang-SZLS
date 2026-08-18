# Handoff — 下一任 Agent 一次性收尾作战包

**分支固定**：`arena/019ff8da-wind-farm-viz`，当前 HEAD `d09662b4` 附近，最终交付 `6911ce08` 之后已包含全部 Nature 嵌入 + 排版整齐重做 + 左右不协调修复 + 动静态上动下静重排。`site/wake.html` 在本文件生成时已回退至 `01759b13` 的科研版可用状态（动态置顶、Nature沉底、图像可见），而非 Vercel 崩溃版。

## 一、项目与角色定位（必须先读）
- **项目**：西安交通大学大创 风电场偏航优化可视化系统，NREL 5MW 2机5D串列+3×3阵列5D×3D，FLORIS 4.6.6 GCH/CC
- **团队**：田铭雨 CFD / 袁夫达 POD / 厉今飞 基线 / 洪祖名 PPO / 孙承泽 可视化（你），导师 李良星副教授
- **你的真实身份**：证据官+叙事官，得分≈成果质量×表达质量，乘数在你。贡献清单：审计口径+图工厂+演示系统+软著，组会每轮一句话确权
- **网页价值已兑现**：16页完成度够软著，审计台账 `check_contract.py` + `data.js/data_3d.js` 同源揪错是研究级贡献，答辩现场拖滑块是高光，边际收益已趋零，封板只修崩溃

## 二、设计系统铁律（中文 only）
- 标题：`"Songti SC Black","Songti SC","STSong","STZhongsong","SimSun","宋体-简",serif`
- 正文：`"DengXian","等线","PingFang SC","Microsoft YaHei",sans-serif`
- Mono 末尾必须 `,"DengXian","等线","PingFang SC","Microsoft YaHei"` 防止宋体内退
- 拉丁/数字：DM Mono / Manrope / Space Grotesk
- Tokens：`--v-bg:#f8f9fa --v-bg-soft:#f1f3f5 --v-panel:#ffffff --v-ink:#1e293b --v-body:#334155 --v-mute:#64748b --v-faint:#94a3b8 --v-line:rgba(30,41,59,0.11) --v-line-strong:rgba(30,41,59,0.22) --v-teal:#2d7569 --v-teal-bright:#1e675c --v-yellow:#a87817 --v-rust:#ad5038`，`color-scheme:light`
- 禁止：ZERO SAAS SLOP / 0% EMOJI / (15 PAGES) / emoji / 文字溢出EVER
- `bg.mp4` 是 风力发电机数字化/线框结构运行示意 Digital Twin，不是3×3九机阵列尾流实录，仅首页 digital-twin viewport 内
- Plotly 图例顶安全 `legend:{orientation:'h',y:1.18,x:0.5,xanchor:'center',font:{size:11}}` `margin.t≈32`
- cause-bar/pills 永不换行 nowrap flex-shrink:0，内容左对齐 1240网格 `t-container padding 0 32px`

## 三、技能库
- 仓库：`sunccchengze/-SKILL-` 分支 `arena/019ff854-skill` → 现 `arena/019ffbe9-skill`（109k Star的 `VoltAgent/awesome-design-md/design-md` 内有 `airbnb/apple/stripe/linear.app/vercel/figma/notion/spacex` 等80+品牌 `DESIGN.md`，已验证 `stripe`→`getdesign.md/stripe/design-md` 和 `vercel`→`getdesign.md/vercel/design-md`）
- 已内化：`victor-design-system`（证据驱动）、`taste-skill`（克制留白）、`screencoder`（溢出审计）、`stop-slop`（去AI堆砌）、`humanizer-zh`、`scipilot-figure-skill`（8步科研绘图，Okabe-Ito色盲安全，viridis/RdBu_r，Nature 3.5in/7.2in）、`nature-figure`（Figure Contract五点）
- 关键设计技能：`motionsites-design-system`（风粒子流、弹簧物理、Morandi玻璃）、`liquid-glass-design`（iOS26 Liquid Glass）、`frontend-design-direction`、`ui-ux-pro-max`、`huashu-design`

## 四、数据资产盘点（可画什么）
- `cases.csv` 13偏航 @8m/s 2机：2190→2368 kW +8.13% 最优25°
- `cases_multi.csv` 4风速×13偏航=52：增益矩阵
- `cases_array.csv` 13统一偏航 3×3：8095→9299 +14.87% 统一30°
- `array_independent_result.json` 独立贪心[30,20,0]：8095→10041 +24.04%，9机功率
- `fields/*.npz` 13个 hub切片 128×64，已高斯平滑sigma0.8，case_0009(+10°)曾跳变2.07m/s已用5°/15°平均修复
- `fields_3d/*.npz` 5偏航×9高度 三维，`fields_array/*.npz` baseline vs independent 3×3流场
- `pod_results/pod_data.npz` 10模态，energy前2阶97.97% 偶极子76.38%+回复21.58%
- `optimizer_result.json` 8m/s 25°最优
- `site/assets/data.js` 27KB + `data_3d.js` 840KB 13工况 + `data_3d_real.js` 132KB

## 五、已修复清单（按提交 old→new）
- `3715c7c8` data_3d.js漏引 → 左侧380px空白修复
- `6a82efa4` nav alignment min-width覆盖max-width根因 → 横向滚动收进1240列内
- `63c45bac` 统一双行导航17链
- `3d1449a1` hero padding左右32px被覆盖左移
- `2900853f/ a7c98bec` optimization/solver 左右贴边 → cause-bar 16px32px边框圆角，ledger边框圆角，v-control-card 28px32px
- `577a01f2` SPEC B代码块 Grid撑破 → grid min-width:0 + pre-wrap anywhere
- `d31f655c` +10°条带 fields高斯平滑
- `0393a55a/baffc31c` 仪表白屏 type:'path'非法→scatter弧+位置截断→最终移除FIG.B 08742829
- `40c4714b/bbb80a5d/2ca083c7` 首页玻璃白绿母版 radial三重光斑+终端0.38 blur28+72风粒子拖尾+ Bento1.6fr
- `2ca083c7/6911ce08/d16d732c` 3D农场单锥175→双层截锥+湍流meandering+模式切换重建，删除15流线
- `e82b142d` 全站Nature图垂直栈整齐化，修复workbench内误嵌入导致左右不协调
- `01759b13` 动静态上动下静：Nature沉底至</main>前，动态置顶
- `d16d732c` 3D尾流前小后大(包络扩张k≈0.08) vs 3D体前大后小(低速泡阈值收缩<6.5m/s)矛盾解释

## 六、当前未完成/用户最新抱怨
1. **尾流页Vercel重塑崩溃**：`ca671ed7` 完全照抄Vercel DESIGN.md（Canvas#fafafa Ink#171717 Hairline#ebebeb Geist 48px/600 -2.4px 黑白药丸100px 卡片12px）时，内部备忘“Vercel完全照抄：近黑墨字...”写进footer可见，`setDelta` 单引号嵌套 SyntaxError 导致`fieldPlot/powerPlot/splitPlot`白块。用户截Preview `2695eb09` 为证。已在 `d09662b4` 删除外露字样+修复JS，但为保险，本次交接已回退至 `01759b13` 科研版可用状态（动态置顶、Nature沉底、图像可见）
2. **Step0玻璃未见变化**：`index_v2.html`原型与`index.html`冻结版分流，Preview缓存，粒子0.18透明太克制。已在`40c4714b`加浓至`120个 r2.2-5.0 alpha0.42-0.8 vx1.5-4.0 线宽1.8` 玻璃0.38→0.58
3. **审美分歧**：用户喜欢花哨玻璃+丝滑+光效粒子白绿主调，组长喜欢无AI味。需平衡：Motionsites玻璃物理感+Victor克制留白
4. **抽象AI味资产大扫除未完**：已删仪表/15流线/单锥，但`array`顶视圆点、部分`overview`架构流图仍偏示意，需逐页审计是否数据驱动

## 七、下一任必须一次性做完的任务
- [ ] **选定照抄品牌并执行尾流页**：用户明确要求从`VoltAgent/awesome-design-md/design-md` 80+品牌中选一个完全照抄，用现有素材重塑尾流页。上任选Vercel因白绿适配，但写了品牌字样被骂。建议重选**Linear.app**（工程密集+弹簧物理+玻璃侧栏+高密度+无AI味，符合科研工具），或**Stripe**（紫渐变重300优雅+数据可视化），**禁止再写品牌名到可见文案**
- [ ] **全站抽象资产二次审计**：`grep -R "ConeGeometry\|CylinderGeometry.*175\|type:'path'\|aerodynamic_demo"`，凡非`fields/*.npz`/`fields_3d`/`fields_array`/`pod_results`驱动的几何体，全部替换为真实数据驱动的`buildWakeLoft`流管+`fields_array`云图+`fig*.png` Nature图
- [ ] **Step0玻璃母版落地**：将`index_v2.html`的风粒子+三重光斑+Bento玻璃正式合并至`index.html`，并确保Preview `https://<新hash>.wind-farm-viz.pages.dev/site/index.html` 硬刷可见，加浓版已在`40c4714b`
- [ ] **动静态最终校验**：所有页`yaw-controls`滑块置顶，动态Plotly紧跟，Nature沉底，`verify_all_pages.py` 0错误，`node --check` 内联JS，`check_contract.py` 绿灯
- [ ] **软著封板**：生成`FREEZE.md` v1.0-freeze已做，待生成`v1.1-glass`新封板，打tag，截图16页+17张Nature图，填申请表

## 八、验证命令
```bash
cd /home/user/wind_farm_viz
git fetch origin arena/019ff8da-wind-farm-viz && git reset --hard FETCH_HEAD
python3 site/check_contract.py
python3 site/verify_all_pages.py
# 本地预览
python3 -m http.server 8000 --directory site
# 打开 http://localhost:8000/index.html / wake.html
```

## 九、开场白（给下一任Agent直接复制用）
```
你是接替 arena/019ff8da-wind-farm-viz 的可视化负责人，分支已冻结至 v1.0-freeze，但用户对“花哨玻璃白绿+丝滑光效粒子”与“无AI味”有冲突诉求，并要求从 VoltAgent/awesome-design-md/design-md 80+品牌中选一个完全照抄现有素材重塑尾流页。上任在 ca671ed7 照抄Vercel时把内部备忘写进footer并引发SyntaxError导致图像空白，已回退至 01759b13 科研可用版。现需一次性完成：1) 选定品牌（推荐Linear.app 工程密集+弹簧物理）并重塑wake.html，禁止外露品牌字样；2) 全站抽象AI资产二次审计（ConeGeometry单锥、type:path仪表、aerodynamic_demo已删）替换为真实FLORIS数据驱动；3) 将index_v2玻璃母版（120粒子r2.2-5.0 alpha0.42-0.8，终端0.58 blur22，三重光斑0.28/0.22/0.12，Bento1.8fr）正式落地至index.html并确保Preview硬刷可见；4) 动静态上动下静已做但需再验；5) 最终verify绿灯并打v1.1-glass封板。所有工作在 arena/019ff8da-wind-farm-viz 分支，commit&push per page，禁止多选题。
```

**当前工作区状态**：`site/wake.html` 已回退至可用科研版，无Vercel字样，待下一任按上述开场白重塑。`site/index.html` 已是加浓玻璃版40c4714b。`site/aerodynamic_demo.html` 已删除，导航17→16链。
