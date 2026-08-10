# Refero-Style DESIGN.md: 风电场偏航优化科研工作台设计规范

> 本文件参照 styles.refero.design 标准编制，作为本平台所有 16 个静态子页面（Cloudflare Pages）与后续组件开发的设计宪法。

---

## 1. 颜色系统 (Color Tokens)

### 1.1 莫兰迪工科主色盘 (Morandi Engineering Palette)
- **背景底色 (Surface Base)**: `#F8F6F0` (柔和米白纸感，消除纯白刺眼)
- **主卡片底色 (Surface Elevated)**: `rgba(255, 255, 255, 0.88)` ~ `rgba(255, 255, 255, 0.94)` (配合 `backdrop-filter: blur(14px)`)
- **发丝边框 (Hairline Border)**: `1px solid rgba(220, 213, 200, 0.8)`
- **主要文本 (Text Primary)**: `#1E293B` (深岩板灰，严禁纯黑 `#000000`)
- **次要文本 (Text Muted)**: `#64748B` (中性冷灰)
- **主功能色 - 雾蓝 (Engineering Slate Blue)**: `#5B84B1` (系统主色、导航激活、偏航角导向)
- **收益功能色 - 鼠尾草绿 (Sage Green)**: `#6F8761` (正向增益、高出力机组、最优解)
- **让利功能色 - 陶土粉红 (Terracotta Rose)**: `#B98484` (上游让利、低出力、亏损区间)
- **强调色 - 暖秋金 (Warm Amber Gold)**: `#C2A86B` (重要参数、收敛收束、王牌数据)

---

## 2. 字体与排版阶梯 (Typography Hierarchy)

- **中文章节大标题**: `Songti SC (宋体-简)` / `Noto Serif SC`, `font-weight: 700`, 典雅学术气韵
- **西文标题与代码**: `Instrument Sans` / `Inter`, `font-weight: 600`, 极致工科可读性
- **数值与仪表数据**: `JetBrains Mono` / `Space Mono` / `SF Mono`, `font-variant-numeric: tabular-nums` (等宽数字，确保实时跳动不抖动)
- **正文与说明**: `system-ui, -apple-system, sans-serif`, `font-size: 14px`, `line-height: 1.6`

---

## 3. 空间与网格系统 (Spatial Grid)

- **基准网格**: 8px Grid (Padding: 8px, 16px, 24px, 32px; Gap: 12px, 16px, 24px)
- **圆角规范**: 
  - 容器卡片: `border-radius: 8px` ~ `12px` (严禁超过 16px 的浮夸超大圆角)
  - 按钮与标签: `border-radius: 4px` ~ `6px` (微圆角工科风)
- **层级阴影**:
  - `0 1px 3px rgba(0, 0, 0, 0.05)` (Subtle elevation)
  - `0 4px 12px rgba(0, 0, 0, 0.04)` (Hover elevation)

---

## 4. 动效设计守则 (Motion Guidelines)

- **持续时间**: 微交互 150ms ~ 250ms；大转场 300ms ~ 400ms；流场循环持续流动
- **缓动曲线**:
  - 界面展开/收起: `cubic-bezier(0.16, 1, 0.3, 1)` (Out Expo)
  - 物理旋转与阻尼: `cubic-bezier(0.34, 1.56, 0.64, 1)` (Spring overshoot)
