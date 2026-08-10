# Learnings

Corrections, insights, and knowledge gaps captured during development.

**Categories**: correction | insight | knowledge_gap | best_practice

---

## [LRN-20260810-01] 网页视觉基线与莫兰迪设计规范
- **Logged**: 2026-08-10T06:40:00Z
- **Priority**: critical
- **Status**: verified
- **Category**: best_practice
- **Trigger**: user_feedback
- **Context**: 静态站 `site/` 的视觉基调与用户审美偏好
- **What Happened**: 探索过程中曾发生配色偏离（改写为暗色海军蓝），破坏了原版的莫兰迪浅色与动态视频背景，被用户严厉纠偏并完全回滚。
- **Correct Approach**:
  1. 静态站 `site/` 视觉状态永久以 commit `70c398e` 为黄金基准；
  2. 保持纯正莫兰迪工科米白底（`#F8F6F0`）、旋转风机背景视频（`bg.mp4`）与高透毛玻璃遮罩（`media.css`）；
  3. 大标题统一采用学术宋体-简 (Songti SC)，所有 3D 页面（`3d_farm.html`, `3d_surface.html`, `3d_volume.html`）保持原有 Plotly 数据流正常运转。

---

## [LRN-20260810-02] 孙承泽团队角色与定位精确校准
- **Logged**: 2026-08-10T06:50:00Z
- **Priority**: critical
- **Status**: verified
- **Category**: correction
- **Trigger**: user_correction
- **Context**: 大创项目成员角色确权
- **What Happened**: 助手在总结中曾误称孙承泽为“项目总负责人”。
- **Correct Approach**:
  1. 孙承泽是大创项目中的组员，具体负责**“可视化与交互系统（Visualization & Interactive System）模块”**；
  2. 指导教师为李良星副教授，其他高年级队友分工为：田铭雨（CFD 流场）、袁夫达（插值代理模型）、厉今飞（基线实验与工况）、洪祖名（优化算法与 PPO 强化学习）；
  3. 严禁任何跨越事实的角色臆断。

---

## [LRN-20260810-03] 技能学习与吸收协议 (GitHub First Protocol)
- **Logged**: 2026-08-10T07:00:00Z
- **Priority**: high
- **Status**: verified
- **Category**: best_practice
- **Trigger**: user_correction
- **Context**: 技能库扩充与工具链建设
- **What Happened**: 面对用户提到的新技能时，曾出现未深入检索 GitHub 原生高 Star 仓库就自行推断定义的现象。
- **Correct Approach**:
  1. 面对用户给出的任何技能或框架（如 `self-improving-agent`, `agent-memory`, `open-code-review`），**第一步必须在 GitHub 上检索对应的高 Star 权威开源仓库**；
  2. 下载、分析其真实源码（代码、Prompt、Hooks、References），严格按照上游规范吸收；
  3. 若在 GitHub 无法检索到开源实现，必须向用户汇报，在获得用户明确许可后方可自行定制。

---

## [LRN-20260810-04] 工科路演与答辩 PPT“零 AI 味”标准
- **Logged**: 2026-08-10T04:20:00Z
- **Priority**: high
- **Status**: verified
- **Category**: best_practice
- **Trigger**: user_feedback
- **Context**: 王牌答辩幻灯片制作
- **What Happened**: 初版 PPT 采用了通用圆角卡片、Emoji 装饰与彩色气泡伪风机，被用户指出 AI 模板味极重。
- **Correct Approach**:
  1. 严格遵循瑞士国际主义工科排版（Swiss Grid），1.3 倍行距，零 Emoji；
  2. 必须嵌入由 FLORIS / Matplotlib 生成的真实 2D 流场云图、Nature 标准三线表与阶梯能量瀑布柱状图；
  3. 风机必须绘制真实偏航倾斜叶轮面（$\gamma_1=+30^\circ$ 倾斜实线段）。
