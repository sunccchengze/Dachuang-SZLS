# Learnings

Corrections, insights, and knowledge gaps captured during development.

**Categories**: correction | insight | knowledge_gap | best_practice

---

## [LRN-20260810-01] 必须在每条回复开头强制声明大师与技能 (Zero Exception)
- **Logged**: 2026-08-10T08:00:00Z
- **Priority**: critical
- **Status**: verified
- **Category**: correction
- **Trigger**: user_correction
- **Context**: 助手与用户的每一次对话交互
- **What Happened**: 助手或新 Session 的 Agent 在回复时偶发遗漏了开篇的显式调用声明，遭到用户严厉指出。
- **Correct Approach**:
  1. **每条回复第一行必须以绝对一致的格式显式声明**：
     ```markdown
     ### 🛠️ 技能调用与执行声明
     - **本次显式调度大师**：【大师名】（角色定位）
     - **本次显式调用SKILL**：`技能路径`
     ```
  2. 严禁以任何理由省略该声明头。

---

## [LRN-20260810-02] 战役进度客观实事求是，严禁虚报“已完成”
- **Logged**: 2026-08-10T08:05:00Z
- **Priority**: critical
- **Status**: verified
- **Category**: correction
- **Trigger**: user_correction
- **Context**: 14 天四大战役推进进度核算
- **What Happened**: 助手轻率地向新 Session 传递了“战役一和战役二已完成”的虚假信息。事实是：战役一仅锁定了 70c398e 基准，真正的高阶优化尚未完成；战役二仅交付了讲义，承泽尚未展开系统互动通识学习。
- **Correct Approach**:
  1. **战役一 (Web 工作台)**：【进行中】（基线锁定 commit 70c398e，等待后续平稳优化）；
  2. **战役二 (物理与算法通识)**：【进行中】（讲义就绪，等待承泽逐章互动吃透）；
  3. **战役三 (PS 300DPI)**：【待开展】；
  4. **战役四 (20页 PPT 与答辩)**：【待开展】；
  5. 严禁任何夸大进度的浮夸宣称。

---

## [LRN-20260810-03] 孙承泽团队角色与定位精确校准
- **Logged**: 2026-08-10T06:50:00Z
- **Priority**: critical
- **Status**: verified
- **Category**: correction
- **Trigger**: user_correction
- **Context**: 大创项目成员角色确权
- **What Happened**: 孙承泽是大创项目中的组员，具体负责**“可视化与交互系统（Visualization & Interactive System）模块”**（非总负责人）。
- **Correct Approach**: 指导教师为李良星副教授，其他队友为田铭雨（CFD）、袁夫达（代理模型）、厉今飞（基线）、洪祖名（PPO 优化）。

---

## [LRN-20260810-04] 网页视觉状态永久以 70c398e 为黄金基准
- **Logged**: 2026-08-10T06:40:00Z
- **Priority**: critical
- **Status**: verified
- **Category**: best_practice
- **Trigger**: user_feedback
- **Context**: 静态站 `site/` 的视觉基调
- **Correct Approach**: 保持纯正莫兰迪米白底（`#F8F6F0`）、旋转风机背景视频（`bg.mp4`）、高透毛玻璃遮罩（`media.css`）与学术宋体-简 (Songti SC)。严禁篡改为深海军蓝。
