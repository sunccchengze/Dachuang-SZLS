import streamlit as st

st.set_page_config(
    page_title="风电场偏航优化演示系统",
    page_icon="🌬️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.stApp {
    background-color: #060b18;
    background-image:
        radial-gradient(ellipse 80% 60% at 10% 20%,
            rgba(74,158,255,0.18) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 90% 80%,
            rgba(39,174,96,0.14) 0%, transparent 60%),
        radial-gradient(ellipse 50% 40% at 50% 50%,
            rgba(155,89,182,0.08) 0%, transparent 60%);
    min-height: 100vh;
}

/* ===== 侧边栏深色主题 ===== */
[data-testid="stSidebar"] {
    background-color: #0a1020 !important;
    border-right: 1px solid rgba(255,255,255,0.08) !important;
}
[data-testid="stSidebar"] * {
    color: #a8bcdf !important;
}
[data-testid="stSidebarNav"] {
    padding-top: 8px;
}
[data-testid="stSidebarNav"] a {
    background: transparent !important;
    border-radius: 10px !important;
    padding: 8px 12px !important;
    margin: 2px 8px !important;
    transition: background 0.2s !important;
}
[data-testid="stSidebarNav"] a:hover {
    background: rgba(74,158,255,0.12) !important;
}
[data-testid="stSidebarNav"] a[aria-current="page"] {
    background: rgba(74,158,255,0.15) !important;
    border-left: 2px solid #4a9eff !important;
}
[data-testid="stSidebarNav"] span {
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #a8bcdf !important;
}

/* ===== hero ===== */
.hero {
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 24px;
    padding: 64px 56px 56px 56px;
    text-align: center;
    position: relative;
    overflow: hidden;
    margin-bottom: 28px;
}
.hero::before {
    content: "";
    position: absolute;
    top: -80px; left: -80px;
    width: 400px; height: 400px;
    background: radial-gradient(circle,
        rgba(74,158,255,0.15) 0%, transparent 65%);
    pointer-events: none;
}
.hero::after {
    content: "";
    position: absolute;
    bottom: -80px; right: -80px;
    width: 360px; height: 360px;
    background: radial-gradient(circle,
        rgba(39,174,96,0.12) 0%, transparent 65%);
    pointer-events: none;
}
.hero-tag {
    display: inline-block;
    background: rgba(74,158,255,0.12);
    border: 1px solid rgba(74,158,255,0.35);
    color: #4a9eff;
    font-size: 11px; font-weight: 700;
    letter-spacing: 2.5px; padding: 5px 16px;
    border-radius: 20px; margin-bottom: 24px;
    text-transform: uppercase;
}
.hero-title {
    font-size: 46px; font-weight: 800;
    color: #ffffff; margin: 0 0 16px 0;
    line-height: 1.15; letter-spacing: -1px;
}
.hero-title span {
    background: linear-gradient(90deg, #4a9eff 0%, #27ae60 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    font-size: 16px; color: rgba(168,188,223,0.85);
    margin: 0 0 36px 0; line-height: 1.7;
}
.hero-badges {
    display: flex; justify-content: center;
    gap: 10px; flex-wrap: wrap;
}
.badge {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.10);
    color: rgba(168,188,223,0.9);
    font-size: 12px; padding: 5px 14px; border-radius: 20px;
}

/* ===== 统计卡片 ===== */
.stats-bar {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px; margin-bottom: 28px;
}
.stat-card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 16px; padding: 28px 20px;
    text-align: center; position: relative; overflow: hidden;
    transition: transform 0.25s ease, box-shadow 0.25s ease,
                border-color 0.25s ease;
}
.stat-card::before {
    content: "";
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg,
        transparent, rgba(255,255,255,0.2), transparent);
}
.stat-card:hover {
    transform: scale(1.05);
    border-color: rgba(74,158,255,0.45);
    box-shadow: 0 0 20px rgba(74,158,255,0.15),
                0 0 40px rgba(74,158,255,0.08);
}
.stat-number {
    font-size: 36px; font-weight: 800;
    color: #4a9eff; margin: 0; line-height: 1;
}
.stat-unit { font-size: 16px; color: #4a9eff; margin-left: 2px; }
.stat-label {
    font-size: 12px; color: rgba(136,153,187,0.8); margin: 8px 0 0 0;
}

/* ===== 功能卡片 ===== */
.section-title {
    font-size: 13px; font-weight: 700;
    color: rgba(136,153,187,0.7);
    letter-spacing: 2px; text-transform: uppercase;
    margin: 0 0 16px 4px;
}
.page-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px; margin-bottom: 28px;
}
.page-card {
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px; padding: 24px 20px;
    position: relative; overflow: hidden;
    transition: transform 0.25s ease, border-color 0.25s ease,
                background 0.25s ease, box-shadow 0.25s ease;
}
.page-card::before {
    content: "";
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg,
        transparent, rgba(255,255,255,0.15), transparent);
}
.page-card:hover {
    background: rgba(255,255,255,0.07);
    border-color: rgba(74,158,255,0.45);
    transform: scale(1.05);
    box-shadow: 0 0 20px rgba(74,158,255,0.15),
                0 0 40px rgba(74,158,255,0.08),
                inset 0 1px 0 rgba(255,255,255,0.15);
}
.page-icon { font-size: 26px; margin-bottom: 12px; display: block; }
.page-name {
    font-size: 14px; font-weight: 700;
    color: #e8edf5; margin: 0 0 6px 0;
}
.page-desc {
    font-size: 12px; color: rgba(107,122,153,0.9);
    margin: 0; line-height: 1.55;
}
.page-tag {
    display: inline-block; font-size: 10px; font-weight: 700;
    padding: 2px 8px; border-radius: 8px; margin-top: 12px;
    letter-spacing: 0.8px; text-transform: uppercase;
}
.tag-core     { background:rgba(74,158,255,0.12);  color:#4a9eff;
                border:1px solid rgba(74,158,255,0.25); }
.tag-3d       { background:rgba(155,89,182,0.12);  color:#b07fd4;
                border:1px solid rgba(155,89,182,0.25); }
.tag-analysis { background:rgba(39,174,96,0.12);   color:#27ae60;
                border:1px solid rgba(39,174,96,0.25); }
.tag-ai       { background:rgba(230,126,34,0.12);  color:#e67e22;
                border:1px solid rgba(230,126,34,0.25); }
.tag-pod      { background:rgba(232,67,147,0.12);  color:#e84393;
                border:1px solid rgba(232,67,147,0.25); }
.tag-coming   { background:rgba(255,255,255,0.05);
                color:rgba(136,153,187,0.6);
                border:1px solid rgba(255,255,255,0.08); }

/* ===== 技术栈 ===== */
.tech-bar {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px; padding: 18px 28px;
    display: flex; align-items: center;
    gap: 28px; flex-wrap: wrap; margin-top: 8px;
}
.tech-label {
    font-size: 11px; color: rgba(74,85,104,0.9);
    font-weight: 700; letter-spacing: 1.5px;
    text-transform: uppercase; white-space: nowrap;
}
.tech-items { display: flex; gap: 8px; flex-wrap: wrap; }
.tech-item {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    color: rgba(136,153,187,0.8);
    font-size: 11px; padding: 3px 10px; border-radius: 6px;
}
</style>
""", unsafe_allow_html=True)

# ===== 侧边栏品牌标题 =====
with st.sidebar:
    st.markdown("""
    <div style="
        padding: 16px 12px 20px 12px;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 8px;
    ">
        <div style="font-size:14px; font-weight:800; color:#e8edf5;">
            🌬️ 风电场偏航优化
        </div>
        <div style="font-size:11px; color:rgba(136,153,187,0.7);
                    margin-top:4px;">
            可视化演示系统
        </div>
    </div>
    """, unsafe_allow_html=True)

# ===== 主横幅 =====
st.markdown("""
<div class="hero">
    <div class="hero-tag">🏫 西安交通大学 · 大创项目</div>
    <h1 class="hero-title">
        风电场偏航优化<br><span>可视化演示系统</span>
    </h1>
    <p class="hero-sub">
        融合数据-物理驱动 · FLORIS GCH 尾流模型 · NREL 5MW 基准风机<br>
        从流场感知到机组协同调控的完整技术链路演示
    </p>
    <div class="hero-badges">
        <span class="badge">🌬️ 两台串列布局</span>
        <span class="badge">📐 NREL 5MW</span>
        <span class="badge">⚙️ GCH 尾流模型</span>
        <span class="badge">🧠 二维插值代理模型</span>
        <span class="badge">🔬 POD 降阶分析</span>
        <span class="badge">🎯 网格搜索优化</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ===== 统计数字栏 =====
st.markdown("""
<div class="stats-bar">
    <div class="stat-card">
        <p class="stat-number">8.1<span class="stat-unit">%</span></p>
        <p class="stat-label">最大功率提升（8 m/s）</p>
    </div>
    <div class="stat-card">
        <p class="stat-number">2</p>
        <p class="stat-label">POD模态覆盖98%能量</p>
    </div>
    <div class="stat-card">
        <p class="stat-number">+25<span class="stat-unit">°</span></p>
        <p class="stat-label">最优偏航角</p>
    </div>
    <div class="stat-card">
        <p class="stat-number">8</p>
        <p class="stat-label">演示功能页面</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ===== 功能卡片 =====
st.markdown('<p class="section-title">功能模块</p>', unsafe_allow_html=True)
st.markdown("""
<div class="page-grid">
    <div class="page-card">
        <span class="page-icon">📊</span>
        <p class="page-name">尾流分析</p>
        <p class="page-desc">交互式速度场云图，代理模型实时预测任意偏航角下的功率输出</p>
        <span class="page-tag tag-core">CORE</span>
    </div>
    <div class="page-card">
        <span class="page-icon">🎯</span>
        <p class="page-name">优化结果</p>
        <p class="page-desc">偏航前后尾流对比、速度差值图、偏航角扫描动画</p>
        <span class="page-tag tag-core">CORE</span>
    </div>
    <div class="page-card">
        <span class="page-icon">📋</span>
        <p class="page-name">数据总览</p>
        <p class="page-desc">全工况功率柱状图、P₁/P₂分解曲线、原始数据表格</p>
        <span class="page-tag tag-analysis">ANALYSIS</span>
    </div>
    <div class="page-card">
        <span class="page-icon">🌐</span>
        <p class="page-name">3D 尾流曲面</p>
        <p class="page-desc">三维速度曲面可视化，鼠标拖拽旋转，直观感受尾流空间结构</p>
        <span class="page-tag tag-3d">3D</span>
    </div>
    <div class="page-card">
        <span class="page-icon">🫧</span>
        <p class="page-name">3D 体渲染</p>
        <p class="page-desc">真实三维尾流低速泡，含风机转子几何，多高度层叠加渲染</p>
        <span class="page-tag tag-3d">3D</span>
    </div>
    <div class="page-card">
        <span class="page-icon">🔥</span>
        <p class="page-name">热力矩阵</p>
        <p class="page-desc">偏航角 × 风速功率增益矩阵，覆盖 6~12 m/s 全风速工况</p>
        <span class="page-tag tag-analysis">ANALYSIS</span>
    </div>
    <div class="page-card">
        <span class="page-icon">⚡</span>
        <p class="page-name">优化求解器</p>
        <p class="page-desc">输入任意风速，实时网格搜索最优偏航角，输出完整优化结果</p>
        <span class="page-tag tag-ai">AI · OPT</span>
    </div>
    <div class="page-card">
        <span class="page-icon">🔬</span>
        <p class="page-name">POD 降阶分析</p>
        <p class="page-desc">本征正交分解，模态能量分布，流场重构对比，误差定量评估</p>
        <span class="page-tag tag-pod">POD · ROM</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ===== 技术栈 =====
st.markdown("""
<div class="tech-bar">
    <span class="tech-label">TECH STACK</span>
    <div class="tech-items">
        <span class="tech-item">Python 3.13</span>
        <span class="tech-item">Streamlit 1.51</span>
        <span class="tech-item">Plotly 6.3</span>
        <span class="tech-item">FLORIS 4.6.6</span>
        <span class="tech-item">NumPy 2.3</span>
        <span class="tech-item">SciPy 1.16</span>
        <span class="tech-item">Pandas 2.3</span>
    </div>
</div>
""", unsafe_allow_html=True)