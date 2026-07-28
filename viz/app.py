import streamlit as st

st.set_page_config(
    page_title="风电场偏航优化演示",
    page_icon="🌬️",
    layout="wide"
)

st.markdown("""
<style>
.stApp { background-color: #080d1a; }
.main-header {
    background: linear-gradient(135deg, #0d1526 0%, #1a3a6e 100%);
    padding: 40px 40px;
    border-radius: 16px;
    border: 1px solid #1e2d4a;
    margin-bottom: 32px;
}
.card {
    background-color: #111827;
    border: 1px solid #1e2d4a;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 16px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1 style="margin:0; color:white; font-size:28px;">
        🌬️ 风电场偏航优化可视化演示系统
    </h1>
    <p style="margin:10px 0 0 0; color:#a8bcdf; font-size:15px;">
        西安交通大学 · 能源与动力工程学院 · 大创项目
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
<div class="card">
    <h3 style="color:#4a9eff; margin:0 0 8px 0;">📊 尾流分析</h3>
    <p style="color:#8899bb; margin:0; font-size:14px;">
        交互式尾流速度场云图，拖动滑块实时查看不同偏航角下的尾流分布与功率变化。
    </p>
</div>
""", unsafe_allow_html=True)

with col2:
    st.markdown("""
<div class="card">
    <h3 style="color:#27ae60; margin:0 0 8px 0;">🎯 优化结果</h3>
    <p style="color:#8899bb; margin:0; font-size:14px;">
        偏航前后尾流对比图、速度差值图，以及偏航角扫描动画演示。
    </p>
</div>
""", unsafe_allow_html=True)

with col3:
    st.markdown("""
<div class="card">
    <h3 style="color:#e67e22; margin:0 0 8px 0;">📋 数据总览</h3>
    <p style="color:#8899bb; margin:0; font-size:14px;">
        全部工况数据表格，以及各工况功率分布统计图。
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style="color:#8899bb; font-size:13px; padding: 16px 0;">
    👈 从左侧导航栏选择页面
</div>
""", unsafe_allow_html=True)