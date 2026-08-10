# Learnings

Corrections, insights, and knowledge gaps captured during development.

**Categories**: correction | insight | knowledge_gap | best_practice

---

## [LRN-20260810-01] 必须在每条回复开头强制声明大师与技能 (Zero Exception)
- **Logged**: 2026-08-10T08:00:00Z
- **Priority**: critical
- **Status**: verified
- **Category**: best_practice
- **Trigger**: user_correction
- **Context**: 助手与用户的每一次对话交互
- **Correct Approach**:
  每条回复第一行必须以绝对一致的格式显式声明：
  ```markdown
  ### 🛠️ 技能调用与执行声明
  - **本次显式调度大师**：【大师名】（角色定位）
  - **本次显式调用SKILL**：`技能路径`
  ```

---

## [LRN-20260810-02] 网页优化原则：保持莫兰迪基调，继续稳步提升
- **Logged**: 2026-08-10T08:20:00Z
- **Priority**: critical
- **Status**: verified
- **Category**: correction
- **Trigger**: user_correction
- **Context**: 静态站 `site/` 的后续优化与视觉准则
- **What Happened**: 助手使用了“基线锁死”等机械术语，给用户造成了“不能再优化网页”的误解。用户的真实诉求是：**喜欢莫兰迪浅色风格（米白底色、风机旋转背景视频、宋体-简）和现有的 3D 数据渲染体系，反对粗暴改成深海军蓝，但希望在现有基础上继续把网页改好、改精**。
- **Correct Approach**:
  1. 在现有 `site/` 莫兰迪风格的基础上稳步推进优化；
  2. 保持浅色米白底、动态背景视频与 3D 流场渲染功能；
  3. 后续优化以细节提升（如精细 SVG 图标、消除未编译 LaTeX、数值排版）为主，绝不破坏整体视觉与功能。

---

## [LRN-20260810-03] 孙承泽团队角色与定位精确校准
- **Logged**: 2026-08-10T06:50:00Z
- **Priority**: critical
- **Status**: verified
- **Category**: correction
- **Trigger**: user_correction
- **Context**: 大创项目成员角色确权
- **Correct Approach**: 孙承泽为交大大创组员，具体负责**“可视化与交互系统（Visualization & Interactive System）模块”**（非总负责人）。指导教师为李良星副教授，其他队友为田铭雨（CFD）、袁夫达（代理模型）、厉今飞（基线）、洪祖名（PPO 优化）。

---

## [LRN-20260810-04] 真实进度客观核算，严禁虚报完成
- **Logged**: 2026-08-10T08:05:00Z
- **Priority**: high
- **Status**: verified
- **Category**: correction
- **Trigger**: user_correction
- **Context**: 14 天四大战役推进进度
- **Correct Approach**:
  1. 战役模块一（网页系统优化）：进行中（在现有莫兰迪基础上继续打磨）；
  2. 战役模块二（物理与算法通识）：进行中（讲义就绪，等待承泽逐项深入学习）；
  3. 战役模块三（PS 300DPI 顶刊图与 A0 展板实战）：待开展；
  4. 战役模块四（20页 PPT 与答辩）：待开展。
