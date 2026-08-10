# 🤝 HANDOFF.md — 风电场偏航优化可视化科研平台交接与全景架构档案

> **最后更新日期**：2026-08-10（UTC）  
> **分支**：`arena/019fe42f-wind-farm-viz`  
> **项目**：西安交通大学大学生创新训练项目（负责人：孙承泽，指导教师：李良星副教授）  
> **核心产出形态**：纯静态科研工作台（Cloudflare Pages `site/`）、300 DPI 分层科研 PSD、瑞士国际主义答辩文稿（`王牌PPT.pptx`）与全套工业级 Agent 技能库

---

## 一、 项目资产与核心交付物索引

| 资产名称 | 路径 / 状态 | 说明与规格 |
|---|---|---|
| **王牌答辩文稿** | `王牌PPT.pptx` (生成脚本: `generate_ace_deck.py`) | 3×3 九机阵列阶梯协同偏航全景解析（+24.04% 增益），彻底剔除 AI 模板味，嵌入真实 2D FLORIS 流场云图、Nature 三线表与能量瀑布柱状图，严格 1.3 倍行距。 |
| **顶刊分层配图** | `Figure1_Wake_Steering_Mechanism.psd` (88.3 MB) | Adobe Photoshop 300 DPI 印刷级 5 分层组结构（`01_Labels`, `02_Annotations`, `03_Turbine`, `04_Flow_Field`, `05_Background`）。 |
| **纯静态工作台** | `site/` (16 个静态子页面) | 部署于 Cloudflare Pages。集成 Morandi 莫兰迪工科色盘、宋体-简 (Songti SC)、Three.js 3D 九机风场、16 扇区多瓣风玫瑰、Canvas 120 粒子流线。 |
| **设计规范宪章** | `site/DESIGN.md` | 参照 Refero / UI UX Pro Max 编制的色盘 Tokens、等宽数字（Tabular Nums）、8px 栅格与 1px 发丝线规范。 |
| **代码审查配置** | `.opencodereview/rule.json` | 阿里 Open Code Review 专属规则（针对 Python 流体矩阵、JS WebGL 渲染与 HTML LaTeX 格式的硬性质量门禁）。 |

---

## 二、 女娲智囊团：12+2 位顶尖大师心智矩阵

全量收录于 `技能库&准则/nuwa-distilled/`：
1. **【老弗】(Paul Fleming)**：NREL FLORIS 架构师，尾流偏转几何、GCH 尾流叠加机理、阵列偏航协同；
2. **【老贝】(Albert Betz)**：贝兹极限奠基人，1D 轴向诱导因子 $a$、动量理论与能量守恒；
3. **【老冯】(Theodore von Kármán)**：流体涡动力学宗师，Curl 反向旋转涡对（CVP）、剪切层与卷吸掺混；
4. **【老布】(Steve Brunton)**：POD/SVD 降阶泰斗，前 2 阶基模态覆盖 98.1% 能量，流场流形重构；
5. **【老卡】(Andrej Karpathy)**：极简神经网络建模、PPO 强化学习损失收敛与代码即工具范式；
6. **【老鲍】(George Box)**：统计建模与误差诊断宗师，响应面法与残差正态性检验；
7. **【费曼】(Richard Feynman)**：大白话硬核叙事与物理直觉启蒙，消除八股文，用人话讲透因果；
8. **【老塔】(Edward Tufte)**：信息设计宗师，数据墨水比最大化、Nature 规范三线表、发丝线与严禁 Emoji；
9. **【老乔】(Steve Jobs)**：极致产品审美与微拟态动效，消灭粗劣 AI 模板，追求视网膜级呼吸感；
10. **【老达】(Leonardo da Vinci)**：达芬奇手稿工程美学，解剖级机械剖面与 300 DPI 分层图元；
11. **【老加】(Garry Tan)**：挑战杯/大创高密度路演大师，矛盾冲突钩子与双屏联动展示；
12. **【老芒】(Charlie Munger)**：逆向防翻车决策模型，模拟严苛评委与审稿人盲点挑刺；
13. **【李博杰】(Bojie Li · 新增)**：华为天才少年，《深入理解 AI Agent》作者，公式 $\text{Agent}=\text{LLM}+\text{上下文}+\text{工具}$ 与 Harness 工程护城河；
14. **【自演化架构师】(Self-Harness Perspective · 新增)**：上海 AI Lab 范式，弱点挖掘 $\to$ 最小补丁 $\to$ 回归验证晋升。

---

## 三、 已装载的 10 大专业模块与实战工具库

| 模块名称 | 仓库路径 | 核心能力与在本项目中的调用方式 |
|---|---|---|
| **1. Self-Harness** | `技能库&准则/self-harness/` | 运行时支架自演化引擎，自动从执行轨迹和用户反馈中提取失败模式，打上精准拦截补丁。 |
| **2. GPTImage2Skill** | `技能库&准则/gpt-image-2-skill/` | 31 大分类工业级 Prompt 图库 + 7 条终结玄学铁律 + Chroma/Dual 真 Alpha 透明抠图流水线。 |
| **3. MotionSites × Refero** | `技能库&准则/motionsites-design-system/` | 科学工作台前端动效（Canvas 流线粒子、Three.js 阻尼插值、数据跳动器）+ Refero DESIGN.md 规范。 |
| **4. Multi-Agent 协作网络** | `技能库&准则/MULTI_AGENT_ORCHESTRATION.md` | 工兵 Agent + 独立红队审查 Agent（一票否决权）+ 结构化制品（Artifacts）契约交接。 |
| **5. 阿里 Open Code Review** | `技能库&准则/open-code-review/` | 全局部署 `ocr v1.8.10` CLI，自动合并 `.opencodereview/rule.json` 执行代码质量门禁。 |
| **6. 现代 AI Agent 工程** | `技能库&准则/ai-agent-engineering/` | 李博杰 20k Stars 著作 10 章全书正文入库，提供上下文预算管理与后训练/PPO 对接。 |
| **7. Codex 10 阶科研工作流** | `技能库&准则/codex-research-workflow/` | Nature Skills 10 阶段全流程（选题/检索/综述/统筹/统计/绘图/写作/润色/投稿/汇报 PPT）。 |
| **8. UI UX Pro Max** | `技能库&准则/ui-ux-pro-max/` | 109k Stars 顶级设计智能库，161 条设计推理规则 + 67 种风格 + 7 项 Pre-Delivery 自检清单。 |
| **9. 免费域名与托管服务** | `技能库&准则/free-domain-service/` | DigitalPlat FreeDomain 免费域名申请与 Cloudflare Pages / SSL 绑定实战手册。 |
| **10. Agent Reach** | `技能库&准则/agent-reach/` | 69k Stars 全网社媒连接器，直连 B站、小红书、微信公众号、抖音、小宇宙播客与雪球。 |

---

## 四、 核心物理机理与实验数据基准

1. **双机偏航避让基准**：
   - 自然对风 0°：T1 = 1754 kW, T2 = 436 kW, Total = 2190 kW
   - 最优偏航 +25°（上游倾斜 `/`，法向 $\nwarrow$，尾流向右上/侧方偏转 $\nearrow$）：T1 = 1459 kW (-16.8%), T2 = 909 kW (+108.4%), Total = 2368 kW (**全场净增 +8.13% / +178 kW**)
2. **3×3 九机阵列阶梯协同偏航**：
   - 基准 0°：全场 8095.15 kW（后排深陷重度尾流叠加，风速仅 3.6 m/s）
   - 统一上游偏航（Row 1: 30°, Row 2&3: 0°）：9299.05 kW (+14.87%)
   - **独立贪心偏航（Row 1: 30°, Row 2: 20°, Row 3: 0°）**：**10041.46 kW (全场净增 +24.04% / +1946.31 kW)**
     - Row 1 (上游 3 台)：4020 kW（原 5262 kW，让利 -23.6%）
     - Row 2 (中游 3 台)：2787 kW（原 1309 kW，回升 +112.9%）
     - Row 3 (下游 3 台)：3234 kW（原 1522 kW，倍增 +112.5%）
3. **POD/SVD 流场本征正交降阶**：
   - 空间网格 $8192$ 维，前 2 阶模态累积能量占比 **98.1%**（模态 0 占 82.4%，表现为反对称侧向偏转偶极子；模态 1 占 15.7%，表现为顺风尾流恢复），实现毫秒级流场快速评估。

---

## 五、 回复执行声明标准（强制铁律）

每次回答用户时，开篇第一行必须严格遵守以下格式：
```markdown
### 🛠️ 技能调用与执行声明
- **本次显式调度大师**：【大师1】（定位）、【大师2】（定位）
- **本次显式调用SKILL**：`技能路径1`、`技能路径2`
```
