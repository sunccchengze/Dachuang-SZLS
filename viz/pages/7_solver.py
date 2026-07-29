import streamlit as st
import numpy as np
import plotly.graph_objects as go
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from surrogate_model import predict_power, find_optimal_yaw, U_min, U_max

st.set_page_config(page_title="优化求解器", page_icon="⚡", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #080d1a; }
[data-testid="stMetric"] {
    background-color: #111827;
    border: 1px solid #1e2d4a;
    border-radius: 12px;
    padding: 16px 20px;
}
[data-testid="stMetricLabel"] {
    font-size: 13px !important;
    color: #8899bb !important;
    font-weight: 600 !important;
}
[data-testid="stMetricValue"] {
    font-size: 22px !important;
    color: #e8edf5 !important;
    font-weight: 700 !important;
}
[data-testid="stSidebar"] { background-color: #0d1526; }
[data-testid="stSidebar"] * { color: #e8edf5 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("## ⚡ 实时偏航优化求解器")
st.caption("输入任意风速，系统自动搜索最优偏航角，实时输出优化结果")
st.divider()

# ===== 侧边栏 =====
with st.sidebar:
    st.markdown("## ⚙️ 输入参数")
    st.divider()

    U_input = st.slider(
        "来流风速 (m/s)",
        min_value=float(U_min),
        max_value=float(U_max),
        value=8.0,
        step=0.1
    )

    st.divider()
    st.markdown("**模型说明**")
    st.markdown(f"""
- 插值范围：**{U_min:.0f} - {U_max:.0f} m/s**
- 偏航搜索：**120个候选点**
- 插值方法：**二维线性插值**
- 底层数据：**FLORIS GCH**
    """)

# ===== 求解 =====
best_yaw, best_p1, best_p2, best_total, gain_pct = find_optimal_yaw(U_input)
baseline_p1, baseline_p2 = predict_power(0.0, U_input)
baseline_total = baseline_p1 + baseline_p2

# ===== 顶部结果卡片 =====
st.markdown("### 🎯 优化结果")
c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("输入风速",       f"{U_input:.1f} m/s")
c2.metric("推荐偏航角",     f"{best_yaw:+.1f}°")
c3.metric("优化后总功率",   f"{best_total:.0f} kW",
          delta=f"{best_total - baseline_total:+.0f} kW")
c4.metric("功率增益",       f"{gain_pct:+.1f}%")
c5.metric("下游风机增益",
          f"{best_p2:.0f} kW",
          delta=f"{best_p2 - baseline_p2:+.0f} kW vs 0°")

st.markdown("<br>", unsafe_allow_html=True)

# ===== 主图区 =====
col_left, col_right = st.columns([3, 2])

with col_left:
    st.markdown("#### 📈 总功率 vs 偏航角（当前风速）")

    yaw_fine  = np.linspace(-30, 30, 200)
    p_fine    = [predict_power(y, U_input)[0] +
                 predict_power(y, U_input)[1] for y in yaw_fine]
    p1_fine   = [predict_power(y, U_input)[0] for y in yaw_fine]
    p2_fine   = [predict_power(y, U_input)[1] for y in yaw_fine]

    fig_main = go.Figure()

    # 总功率填充曲线
    fig_main.add_trace(go.Scatter(
        x=yaw_fine, y=p_fine,
        mode="lines", name="总功率",
        line=dict(color="#4a9eff", width=2.5),
        fill="tozeroy",
        fillcolor="rgba(74,158,255,0.08)"
    ))

    # P1 曲线
    fig_main.add_trace(go.Scatter(
        x=yaw_fine, y=p1_fine,
        mode="lines", name="上游 P₁",
        line=dict(color="#e67e22", width=1.5, dash="dot")
    ))

    # P2 曲线
    fig_main.add_trace(go.Scatter(
        x=yaw_fine, y=p2_fine,
        mode="lines", name="下游 P₂",
        line=dict(color="#2980b9", width=1.5, dash="dot")
    ))

    # 最优点
    fig_main.add_trace(go.Scatter(
        x=[best_yaw], y=[best_total],
        mode="markers+text",
        name=f"最优 {best_yaw:+.1f}°",
        marker=dict(size=16, color="#27ae60",
                    symbol="star",
                    line=dict(color="white", width=1.5)),
        text=[f"  最优 {best_yaw:+.1f}°<br>  {best_total:.0f} kW"],
        textposition="middle right",
        textfont=dict(color="#27ae60", size=11)
    ))

    # 基准点（偏航0°）
    fig_main.add_trace(go.Scatter(
        x=[0], y=[baseline_total],
        mode="markers+text",
        name="基准 0°",
        marker=dict(size=12, color="#a8bcdf",
                    symbol="circle",
                    line=dict(color="white", width=1.5)),
        text=[f"  基准 {baseline_total:.0f} kW"],
        textposition="middle right",
        textfont=dict(color="#a8bcdf", size=11)
    ))

    # 最优位置竖线
    fig_main.add_vline(
        x=best_yaw,
        line_dash="dash", line_color="#27ae60", line_width=1.5
    )

    fig_main.update_layout(
        xaxis=dict(title="偏航角 (°)", showgrid=True,
                   gridcolor="#1e2d4a", color="#8899bb"),
        yaxis=dict(title="功率 (kW)", showgrid=True,
                   gridcolor="#1e2d4a", color="#8899bb"),
        height=420,
        margin=dict(l=10, r=10, t=20, b=50),
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font=dict(color="#e8edf5"),
        legend=dict(orientation="h", y=-0.2, x=0,
                    font=dict(size=11),
                    bgcolor="rgba(0,0,0,0)")
    )
    st.plotly_chart(fig_main, use_container_width=True)

with col_right:
    st.markdown("#### 🔄 优化前后对比")

    categories = ["上游 P₁", "下游 P₂", "总功率"]
    before_vals = [baseline_p1, baseline_p2, baseline_total]
    after_vals  = [best_p1,     best_p2,     best_total]

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        name="优化前（偏航 0°）",
        x=categories,
        y=before_vals,
        marker_color="#4a5568",
        text=[f"{v:.0f}" for v in before_vals],
        textposition="outside",
        textfont=dict(color="#a8bcdf", size=11)
    ))
    fig_bar.add_trace(go.Bar(
        name=f"优化后（偏航 {best_yaw:+.1f}°）",
        x=categories,
        y=after_vals,
        marker_color="#27ae60",
        text=[f"{v:.0f}" for v in after_vals],
        textposition="outside",
        textfont=dict(color="#e8edf5", size=11)
    ))
    fig_bar.update_layout(
        barmode="group",
        xaxis=dict(color="#8899bb"),
        yaxis=dict(title="功率 (kW)", showgrid=True,
                   gridcolor="#1e2d4a", color="#8899bb"),
        height=200,
        margin=dict(l=10, r=10, t=20, b=40),
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font=dict(color="#e8edf5"),
        legend=dict(orientation="h", y=-0.35, x=0,
                    font=dict(size=10),
                    bgcolor="rgba(0,0,0,0)")
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("#### 🌐 不同风速的最优偏航角")
    U_scan   = np.linspace(U_min, U_max, 60)
    opt_yaws = [find_optimal_yaw(U)[0] for U in U_scan]
    opt_gain = [find_optimal_yaw(U)[4] for U in U_scan]

    fig_opt = go.Figure()
    fig_opt.add_trace(go.Scatter(
        x=U_scan, y=opt_yaws,
        mode="lines",
        name="最优偏航角",
        line=dict(color="#4a9eff", width=2),
        yaxis="y"
    ))
    fig_opt.add_trace(go.Scatter(
        x=U_scan, y=opt_gain,
        mode="lines",
        name="功率增益 %",
        line=dict(color="#27ae60", width=2, dash="dot"),
        yaxis="y2"
    ))
    # 当前风速竖线
    fig_opt.add_vline(
        x=U_input,
        line_dash="dot", line_color="#e74c3c", line_width=1.5,
        annotation_text=f"{U_input:.1f} m/s",
        annotation_font=dict(color="#e74c3c", size=10)
    )
    fig_opt.update_layout(
        xaxis=dict(title="风速 (m/s)", showgrid=True,
                   gridcolor="#1e2d4a", color="#8899bb"),
        yaxis=dict(title="最优偏航角 (°)",
                   showgrid=True, gridcolor="#1e2d4a",
                   color="#4a9eff"),
        yaxis2=dict(title="功率增益 (%)",
                    overlaying="y", side="right",
                    color="#27ae60"),
        height=195,
        margin=dict(l=10, r=50, t=15, b=40),
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font=dict(color="#e8edf5"),
        legend=dict(orientation="h", y=-0.4, x=0,
                    font=dict(size=10),
                    bgcolor="rgba(0,0,0,0)")
    )
    st.plotly_chart(fig_opt, use_container_width=True)