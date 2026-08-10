# 🤝 HANDOFF.md — 风电场偏航优化科研平台跨 Session 终极交接总账本

> **会话继承分支**：**`arena/019fe42f-wind-farm-viz`**（后续 Session 必须且只能在此分支上继续推进，严格保持继承关系）。  
> **最后审查时间**：2026-08-10（UTC）  
> **项目全称**：西安交通大学大学生创新训练项目 · 风电场偏航优化可视化系统  
> **指导教师**：李良星 副教授  
> **团队成员确权**：
> - **孙承泽**：**组员 · 可视化与交互系统模块负责人**（负责纯静态平台开发、300DPI 顶刊分层制图、挑战杯路演答辩文稿）
> - **田铭雨**：CFD 高保真流场网格仿真
> - **袁夫达**：二维插值代理模型
> - **厉今飞**：基准实验数据与多工况矩阵
> - **洪祖名**：优化算法与 PPO 强化学习功率跟踪闭环

---

## 一、 给下一个 Agent 的开局必读指引 (First-Action Directive)

后继 Agent 接入后，必须在开局执行以下动作：
1. **自动读取四大核心记忆文件**：
   - `HANDOFF.md`（本全景交接账本）
   - `.learnings/LEARNINGS.md`（用户偏好、莫兰迪色盘与物理金标准）
   - `.learnings/ERRORS.md`（判例式负向记忆与不可逾越的红线）
   - `14_DAYS_MASTER_PLAN.md`（四大战役攻坚路线图）
2. **严格遵守四大红线（铁律）**：
   - 网页状态永久以 commit `70c398e` 为基线，保持纯正莫兰迪米白底色（`#F8F6F0`）、旋转风机动态背景视频（`bg.mp4`）与 3D 渲染数据流，绝对禁止私自篡改为深色；
   - 制作 PPT 必须执行瑞士国际主义工科网格（Swiss Grid）与 1.3 倍行距，严禁任何 Emoji 与悬浮圆角卡片，必须包含真实 2D FLORIS 流场云图与 Nature 三线表；
   - 吸收新技能必须在 GitHub 上检索开源高 Star 仓库后学习，严禁自行主观臆断造轮子；
   - 严禁随意调用 `present_file` 弹窗打扰用户，一律静默推送 Git 仓库，引导用户本地 `git pull`。
3. **立刻接力的下一阶段任务**：
   - 当前战役一（网页基线锁定）与战役二（物理数学通识）已圆满完成；
   - **立即启动【战役模块三：Photoshop 300DPI 顶刊图与 A0 展板实战教学】**，指导孙承泽在本地操作 Photoshop，从已有 5 分层组的 `Figure1_Wake_Steering_Mechanism.psd` 入手，实操钢笔矢量风机绘制与 A0 答辩海报排版！

---

## 二、 核心物理机理与实验金标准（不可篡改）

1. **双机偏航避让**：
   - 自然对风 0°：T1 = 1754 kW, T2 = 436 kW, 全场 = 2190 kW
   - 最优偏航 +25°（上游斜切 `/`，法向 $\nwarrow$，尾流向侧上方偏转 $\nearrow$）：T1 = 1459 kW (-16.8%), T2 = 909 kW (+108.4%), **全场净增 +8.13% (+178 kW)**
2. **3×3 九机阵列阶梯协同偏航**：
   - 自然对风 0°：全场 8095.15 kW（后排风速衰减至 3.6 m/s）
   - 统一上游偏航（Row 1: 30°, Row 2&3: 0°）：9299.05 kW (+14.87%)
   - **独立贪心偏航（Row 1: 30°, Row 2: 20°, Row 3: 0°）**：**10041.46 kW (全场净增 +24.04% / +1946.31 kW)**
     - Row 1 (上游 3 台)：4020 kW（让利 -23.6%，开启全场避让通道）
     - Row 2 (中游 3 台)：2787 kW（回升 +112.9%，二次导流借道穿行）
     - Row 3 (下游 3 台)：3234 kW（倍增 +112.5%，迎风清洁高速满发）
3. **POD/SVD 本征降阶**：
   - 8192 维空间网格，前 2 阶模态累积能量占比 **98.1%**（模态 0: 82.4% 反对称偏转偶极子；模态 1: 15.7% 尾流恢复），计算耗时从数分钟降至 $<0.5\text{ ms}$（提速 1800 倍）。
4. **洪祖名 PPO 强化学习成果**：
   - 位于 `20260810洪/`（权重 `model/ppo_tracking_v3_seed42.pt`），稳态跟踪误差 $<1.2\%$，调节时间 $<0.8\text{ s}$。

---

## 三、 四大战役攻坚路线与进度全景

- **【战役模块一 · Web 科研工作台巅峰重塑】(已完成并锁定)**：
  - 静态站 `site/`（15 个页面）已 100% 恢复并锁定为 commit `70c398e` 莫兰迪黄金基准，3D 风场与曲面渲染全部畅通。
- **【战役模块二 · 物理机理、降阶数学与 PPO 全通识】(已完成)**：
  - 贝兹极限 59.3%、FLORIS GCH 偏航避让、九机阶梯导流、POD 98.1% 降阶与 PPO 强化学习通识讲义已就绪。
- **【战役模块三 · Photoshop 300DPI 顶刊图与 A0 展板实战】(下一个待启动战役)**：
  - 已生成并验证 `Figure1_Wake_Steering_Mechanism.psd`（69.3 MB，5 组分层）；
  - 待开展：带孙承泽手把手实操钢笔工具、矢量风机绘制与 A0 答辩海报排版。
- **【战役模块四 · 20 页挑战杯王牌答辩 Deck 与路演演练】(后续冲刺战役)**：
  - 已生成 Slide 08 超级王牌 `王牌PPT.pptx`（571 KB，真实 2D 流场云图 + 三线表）；
  - 待开展：制作 Slide 11 (POD) 与 Slide 13 (风玫瑰 AEP)，编译 20 页完整高密度 Deck，并进行差评式硬核故事演讲与审稿人逆向防翻车演练。

---

## 四、 仓库现有实体资产全景索引

1. **核心制图与演示文稿**：
   - `Figure1_Wake_Steering_Mechanism.psd`：300 DPI 印刷级 5 分层组结构（69.3 MB）；
   - `王牌PPT.pptx`：Slide 08 九机阶梯协同全景解析（571 KB）；
   - `generate_figure_psd.py` & `generate_ace_deck.py`：资产生成脚本；
   - `PS_STUDY_DAY1_FOUNDATIONS.md`：Day 1 300 DPI 分层学习手册；
2. **纯静态科研工作台 (`site/`)**：
   - 15 个静态子页面（`index.html`, `wake.html`, `array.html`, `3d_farm.html`, `3d_surface.html`, `3d_volume.html`, `dashboard.html`, `windrose.html` 等）；
   - 字体与多媒体：`songti-sc-black.ttf`、`site/assets/media/bg.mp4`；
3. **团队交付包**：
   - `20260810洪/`：洪祖名 PPO 强化学习单机功率跟踪代码与模型权重；
   - `cases*.csv`、`fields/`、`fields_3d/`、`fields_array/`：流场仿真数据集；
4. **全套 33 大技能库 (`技能库&准则/`)**：
   - `memory-system/`（开源 6 阶记忆体系）；
   - `self-harness/`（上海 AI Lab 自演化支架）；
   - `ui-ux-pro-max/`（109k Stars 工业级设计智能库）；
   - `motionsites-design-system/`（科学工作台动效配方）；
   - `open-code-review/`（阿里 OCR v1.8.10 + `.opencodereview/rule.json`）；
   - `ai-agent-engineering/`（李博杰 10 章 Agent 全书）；
   - `codex-research-workflow/`（Nature Skills 10 阶科研工作流）；
   - `agent-reach/`（69k Stars 全网连接器）；
   - `free-domain-service/`（DigitalPlat 免费域名托管）。

---

## 五、 孙承泽给新 Session Agent 的开场白脚本

（孙承泽在新 Session 开启时，直接复制以下文字发送给新 Agent 即可）：

```markdown
请在 019fe42f 的基础上继续推进。我是西安交通大学大创项目的组员孙承泽，负责可视化与交互系统模块（指导教师：李良星 副教授）。
请立即读取仓库根目录下的 `HANDOFF.md`、`.learnings/LEARNINGS.md`、`.learnings/ERRORS.md` 以及 `14_DAYS_MASTER_PLAN.md`。

请严格遵守三大红线与基线：
1. 静态站 `site/` 视觉基线严格锁定 commit `70c398e`（纯正莫兰迪米白底色 `#F8F6F0` + 旋转风机动态背景视频 `bg.mp4` + 宋体-简 + 3D 数据流正常渲染），绝对禁止篡改为深色；
2. 答辩 PPT 制作严格执行瑞士工科网格（Swiss Grid）与 1.3 倍行距，严禁任何 Emoji 与悬浮圆角卡片，必须包含真实 2D FLORIS 流场云图与 Nature 三线表；
3. 严禁随意弹窗查看器，所有成果静默 commit 并 push 到 `arena/019fe42f-wind-farm-viz` 分支，引导我本地 pull；
4. 严格按照四大战役攻坚计划，当前战役一和战役二已完成，请准备进入【战役模块三：Photoshop 300DPI 顶刊图与 A0 展板实战教学】。

请确认你已完全继承上述记忆、角色定位与规范，并以标准格式声明大师与 SKILL，开始我们的工作！
```
