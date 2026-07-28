import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
matplotlib.rcParams['axes.unicode_minus'] = False

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import json
import os
from surrogate_model import predict_power

# ===== 页面配置 =====
st.set_page_config(
    page_title="风电场偏航优化演示",
    page_icon="🌬️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== 注入CSS =====
st.markdown("""
<style>
.stApp { background-color: #080d1a; }
[data-testid="stMetric"] {
    background-color: #111827;
    border: 1px solid #1e2d4a;
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
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
[data-testid="stPlotlyChart"] {
    background-color: #111827;
    border-radius: 12px;
    padding: 8px;
}
hr { border-color: #1e2d4a !important; }
.main-header {
    background: linear-gradient(135deg, #0d1526 0%, #1a3a6e 100%);
    color: white;
    padding: 24px 32px;
    border-radius: 16px;
    margin-bottom: 24px;
    border: 1px solid #1e2d4a;
}
</style>
""", unsafe_allow_html=True)

# ===== 顶部标题 =====
st.markdown("""
<div class="main-header">
    <h2 style="margin:0; color:white; font-size:24px;">
        🌬️ 风电场偏航优化可视化演示系统
    </h2>
    <p style="margin:6px 0 0 0; color:#a8bcdf; font-size:14px;">
        西安交通大学 · 能源与动力工程学院 · 大创项目
        &nbsp;｜&nbsp; NREL 5MW 基准风机
        &nbsp;｜&nbsp; 两台串列布局
        &nbsp;｜&nbsp; FLORIS GCH 尾流模型
    </p>
</div>
""", unsafe_allow_html=True)

# ===== 读取数据 =====
@st.cache_data
def load_cases():
    return pd.read_csv("cases.csv")

@st.cache_data
def load_field(case_id):
    path = f"fields/{case_id}.npz"
    if os.path.exists(path):
        d = np.load(path)
        return d["x"], d["y"], d["u"]
    return None, None, None

@st.cache_data
def load_result():
    with open("optimizer_result.json") as f:
        return json.load(f)

df = load_cases()
df["power_total"] = df["power_1"] + df["power_2"]
result = load_result()
baseline = df[df["yaw_1"] == 0]["power_total"].values[0]

# ===== 侧边栏 =====
with st.sidebar:
    st.markdown("## ⚙️ 参数控制台")
    st.markdown("---")

    # 连续滑块：step=1，任意整数角度
    yaw_input = st.slider(
        "上游风机偏航角 γ₁ (°)",
        min_value=-30,
        max_value=30,
        value=0,
        step=1
    )

    st.markdown("---")
    st.markdown("**📋 数据集信息**")
    st.markdown(f"""
- 工况数量：**{len(df)}** 个（预计算）
- 代理模型：**三次样条插值**
- 风机型号：**NREL 5MW**
- 来流风速：**8.0 m/s**
- 湍流强度：**6%**
- 机组间距：**630 m（5D）**
- 尾流模型：**GCH**
    """)

    st.markdown("---")
    st.markdown("**🎯 全局最优结果**")
    st.markdown(f"""
- 最优偏航角：**{result['recommended_yaw']}°**
- 功率提升：**+{result['power_gain_pct']}%**
- 优化前：**{result['power_before']:.0f} kW**
- 优化后：**{result['power_after']:.0f} kW**
    """)

# ===== 代理模型实时预测 =====
p1_pred, p2_pred = predict_power(yaw_input)
p_total_pred = p1_pred + p2_pred
gain_pred = (p_total_pred - baseline) / baseline * 100

# 找最近工况（用于显示流场云图）
idx = (df["yaw_1"] - yaw_input).abs().idxmin()
row = df.loc[idx]
case_id = row["case_id"]

# ===== 顶部指标卡片（使用代理模型预测值）=====
c1, c2, c3, c4 = st.columns(4)

with c1:
    p1_base = df[df["yaw_1"] == 0]["power_1"].values[0]
    st.metric("⬆️ 上游风机 P₁",
              f"{p1_pred:.0f} kW",
              delta=f"{p1_pred - p1_base:+.0f} kW")
with c2:
    p2_base = df[df["yaw_1"] == 0]["power_2"].values[0]
    st.metric("⬇️ 下游风机 P₂",
              f"{p2_pred:.0f} kW",
              delta=f"{p2_pred - p2_base:+.0f} kW")
with c3:
    st.metric("⚡ 总功率",
              f"{p_total_pred:.0f} kW",
              delta=f"{p_total_pred - baseline:+.0f} kW vs 无偏航")
with c4:
    st.metric("📈 相对基准增益",
              f"{gain_pred:+.1f}%")

st.markdown("<br>", unsafe_allow_html=True)

# ===== 主图区 =====
col_map, col_curves = st.columns([3, 2])

with col_map:
    st.markdown(f"#### 🗺️ 尾流速度场（最近工况：{row['yaw_1']:+.0f}°）")
    x, y, u = load_field(case_id)

    if u is not None:
        fig_map = go.Figure()
        fig_map.add_trace(go.Heatmap(
            z=u, x=x, y=y,
            colorscale="RdBu_r", zmin=4, zmax=9,
            colorbar=dict(
                title=dict(text="风速 (m/s)", side="right"),
                thickness=15, len=0.8, x=1.02
            )
        ))
        fig_map.add_trace(go.Scatter(
            x=[0, 630], y=[0, 0],
            mode="markers+text",
            marker=dict(size=16, color="#e8edf5", symbol="triangle-up",
                        line=dict(color="#1a3a6e", width=1.5)),
            text=["  风机1（可调偏航）", "  风机2（固定0°）"],
            textposition="middle right",
            textfont=dict(size=12, color="#e8edf5"),
            showlegend=True, name="风机位置"
        ))
        fig_map.add_trace(go.Scatter(
            x=[0, 900], y=[0, 0],
            mode="lines",
            line=dict(color="white", width=1, dash="dot"),
            name="中心线", opacity=0.4, showlegend=True
        ))
        fig_map.update_layout(
            xaxis=dict(title="顺风方向 x (m)", showgrid=False,
                       color="#8899bb"),
            yaxis=dict(title="横向 y (m)", showgrid=False,
                       color="#8899bb"),
            height=420,
            margin=dict(l=10, r=70, t=20, b=50),
            paper_bgcolor="#111827",
            plot_bgcolor="#111827",
            font=dict(color="#e8edf5"),
            legend=dict(orientation="h", y=-0.18, x=0,
                        font=dict(size=11), bgcolor="rgba(0,0,0,0)")
        )
        st.plotly_chart(fig_map, use_container_width=True)

with col_curves:
    # 总功率曲线（含插值预测点）
    st.markdown("#### 📈 总功率 vs 偏航角")

    # 生成连续曲线（代理模型）
    yaw_fine = np.linspace(-30, 30, 200)
    p_fine = [predict_power(y)[0] + predict_power(y)[1] for y in yaw_fine]

    fig_total = go.Figure()
    fig_total.add_trace(go.Scatter(
        x=yaw_fine, y=p_fine,
        mode="lines", name="代理模型曲线",
        line=dict(color="#4a9eff", width=2),
        fill="tozeroy", fillcolor="rgba(74,158,255,0.08)"
    ))
    fig_total.add_trace(go.Scatter(
        x=df["yaw_1"], y=df["power_total"],
        mode="markers", name="FLORIS计算点",
        marker=dict(size=7, color="#a8bcdf", symbol="circle")
    ))
    fig_total.add_trace(go.Scatter(
        x=[yaw_input], y=[p_total_pred],
        mode="markers", name=f"当前 {yaw_input}°",
        marker=dict(size=14, color="#e74c3c",
                    line=dict(color="white", width=2))
    ))
    fig_total.add_vline(
        x=result["recommended_yaw"],
        line_dash="dash", line_color="#27ae60", line_width=1.5,
        annotation_text=f"最优 {result['recommended_yaw']}°",
        annotation_font=dict(color="#27ae60", size=11)
    )
    fig_total.update_layout(
        xaxis=dict(title="偏航角 (°)", showgrid=True,
                   gridcolor="#1e2d4a", color="#8899bb"),
        yaxis=dict(title="总功率 (kW)", showgrid=True,
                   gridcolor="#1e2d4a", color="#8899bb"),
        height=190,
        margin=dict(l=10, r=10, t=15, b=40),
        paper_bgcolor="#111827", plot_bgcolor="#111827",
        font=dict(color="#e8edf5"),
        legend=dict(orientation="h", y=-0.38, x=0,
                    font=dict(size=10), bgcolor="rgba(0,0,0,0)")
    )
    st.plotly_chart(fig_total, use_container_width=True)

    # P1/P2 分解曲线
    st.markdown("#### ⚡ 上下游功率分解")
    p1_fine = [predict_power(y)[0] for y in yaw_fine]
    p2_fine = [predict_power(y)[1] for y in yaw_fine]

    fig_split = go.Figure()
    fig_split.add_trace(go.Scatter(
        x=yaw_fine, y=p1_fine,
        name="上游 P₁", mode="lines",
        line=dict(color="#e67e22", width=2)
    ))
    fig_split.add_trace(go.Scatter(
        x=yaw_fine, y=p2_fine,
        name="下游 P₂", mode="lines",
        line=dict(color="#2980b9", width=2)
    ))
    fig_split.add_vline(x=yaw_input, line_dash="dot",
                        line_color="#e74c3c", line_width=1.5)
    fig_split.update_layout(
        xaxis=dict(title="偏航角 (°)", showgrid=True,
                   gridcolor="#1e2d4a", color="#8899bb"),
        yaxis=dict(title="功率 (kW)", showgrid=True,
                   gridcolor="#1e2d4a", color="#8899bb"),
        height=190,
        margin=dict(l=10, r=10, t=15, b=40),
        paper_bgcolor="#111827", plot_bgcolor="#111827",
        font=dict(color="#e8edf5"),
        legend=dict(orientation="h", y=-0.42, x=0,
                    font=dict(size=10), bgcolor="rgba(0,0,0,0)")
    )
    st.plotly_chart(fig_split, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ===== 偏航前后对比图 =====
st.markdown("#### 🔄 偏航前后尾流对比")
col_b, col_a, col_d = st.columns(3)

x0, y0, u0 = load_field(df[df["yaw_1"] == 0]["case_id"].values[0])
x1, y1, u1 = load_field(case_id)

def make_heatmap(x, y, u, title):
    fig = go.Figure(go.Heatmap(
        z=u, x=x, y=y,
        colorscale="RdBu_r", zmin=4, zmax=9,
        colorbar=dict(thickness=12, len=0.85,
                      title=dict(text="m/s", side="right"))
    ))
    fig.add_trace(go.Scatter(
        x=[0, 630], y=[0, 0], mode="markers",
        marker=dict(size=12, color="#e8edf5", symbol="triangle-up"),
        showlegend=False
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(size=13, color="#e8edf5"), x=0.5),
        xaxis=dict(title="x (m)", showgrid=False, color="#8899bb"),
        yaxis=dict(title="y (m)", showgrid=False, color="#8899bb"),
        height=280,
        margin=dict(l=10, r=60, t=40, b=45),
        paper_bgcolor="#111827", plot_bgcolor="#111827",
        font=dict(color="#e8edf5")
    )
    return fig

with col_b:
    if u0 is not None:
        st.plotly_chart(make_heatmap(x0, y0, u0, "优化前（偏航 0°）"),
                        use_container_width=True)
with col_a:
    if u1 is not None:
        st.plotly_chart(
            make_heatmap(x1, y1, u1, f"优化后（最近工况 {row['yaw_1']:+.0f}°）"),
            use_container_width=True)
with col_d:
    if u0 is not None and u1 is not None:
        delta_u = u1 - u0
        fig_diff = go.Figure(go.Heatmap(
            z=delta_u, x=x1, y=y1,
            colorscale="RdBu", zmid=0,
            colorbar=dict(thickness=12, len=0.85,
                          title=dict(text="Δm/s", side="right"))
        ))
        fig_diff.add_trace(go.Scatter(
            x=[0, 630], y=[0, 0], mode="markers",
            marker=dict(size=12, color="#e8edf5", symbol="triangle-up"),
            showlegend=False
        ))
        fig_diff.update_layout(
            title=dict(text="速度变化量（红=增加 蓝=减少）",
                       font=dict(size=13, color="#e8edf5"), x=0.5),
            xaxis=dict(title="x (m)", showgrid=False, color="#8899bb"),
            yaxis=dict(title="y (m)", showgrid=False, color="#8899bb"),
            height=280,
            margin=dict(l=10, r=60, t=40, b=45),
            paper_bgcolor="#111827", plot_bgcolor="#111827",
            font=dict(color="#e8edf5")
        )
        st.plotly_chart(fig_diff, use_container_width=True)

# ===== 动画展示 =====
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("#### 🎬 偏航角扫描动画")
col_gif, col_desc = st.columns([3, 1])

with col_gif:
    if os.path.exists("wake_animation.gif"):
        with open("wake_animation.gif", "rb") as f:
            gif_bytes = f.read()
        st.image(gif_bytes, use_container_width=True)
    else:
        st.warning("未找到 wake_animation.gif，请先运行 export_gif.py")

with col_desc:
    st.markdown("""
**动画说明**

偏航角从 **-30°** 扫描至 **+30°** 再返回，展示尾流随偏航角的完整偏转过程。

**关键现象：**
- 偏航角 = 0° 时，下游风机完全处于尾流遮挡区
- 偏航角 ≠ 0° 时，尾流向侧方偏转，下游入流风速回升
- 最优偏航角约为 **+25°**，总功率提升 **8.1%**
    """)

# ===== 底部数据表格 =====
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("📋 查看全部工况数据"):
    st.dataframe(
        df[["case_id", "yaw_1", "power_1",
            "power_2", "power_total"]].rename(columns={
            "case_id":     "工况编号",
            "yaw_1":       "偏航角 (°)",
            "power_1":     "P₁ (kW)",
            "power_2":     "P₂ (kW)",
            "power_total": "总功率 (kW)"
        }),
        use_container_width=True,
        hide_index=True
    )