import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
matplotlib.rcParams['axes.unicode_minus'] = False

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="优化结果", page_icon="🎯", layout="wide")

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

st.markdown("## 🎯 优化结果")
st.divider()

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@st.cache_data
def load_cases():
    return pd.read_csv(os.path.join(BASE, "cases.csv"))

@st.cache_data
def load_field(case_id):
    path = os.path.join(BASE, "fields", f"{case_id}.npz")
    if os.path.exists(path):
        d = np.load(path)
        return d["x"], d["y"], d["u"]
    return None, None, None

@st.cache_data
def load_result():
    with open(os.path.join(BASE, "optimizer_result.json")) as f:
        return json.load(f)

df = load_cases()
df["power_total"] = df["power_1"] + df["power_2"]
result = load_result()

# ===== 侧边栏 =====
with st.sidebar:
    st.markdown("## ⚙️ 对比设置")
    st.divider()
    yaw_compare = st.slider(
        "对比偏航角 (°)",
        min_value=int(df["yaw_1"].min()),
        max_value=int(df["yaw_1"].max()),
        value=int(result["recommended_yaw"]),
        step=5
    )

# ===== 顶部优化结果横幅 =====
r1, r2, r3, r4 = st.columns(4)
r1.metric("原偏航角", f"{result['original_yaw']}°")
r2.metric("推荐偏航角", f"{result['recommended_yaw']}°")
r3.metric("优化前总功率", f"{result['power_before']:.0f} kW")
r4.metric("优化后总功率", f"{result['power_after']:.0f} kW",
          delta=f"+{result['power_gain_pct']}%")

st.markdown("<br>", unsafe_allow_html=True)

# ===== 找工况 =====
idx_compare = (df["yaw_1"] - yaw_compare).abs().idxmin()
row_compare = df.loc[idx_compare]
case_id_compare = row_compare["case_id"]
case_id_base = df[df["yaw_1"] == 0]["case_id"].values[0]

x0, y0, u0 = load_field(case_id_base)
x1, y1, u1 = load_field(case_id_compare)

# ===== 三列对比图 =====
st.markdown("#### 🔄 偏航前后尾流对比")

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
        height=300,
        margin=dict(l=10, r=60, t=40, b=45),
        paper_bgcolor="#111827", plot_bgcolor="#111827",
        font=dict(color="#e8edf5")
    )
    return fig

col_b, col_a, col_d = st.columns(3)

with col_b:
    if u0 is not None:
        st.plotly_chart(
            make_heatmap(x0, y0, u0, "优化前（偏航 0°）"),
            use_container_width=True)

with col_a:
    if u1 is not None:
        st.plotly_chart(
            make_heatmap(x1, y1, u1,
                         f"优化后（偏航 {row_compare['yaw_1']:+.0f}°）"),
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
            height=300,
            margin=dict(l=10, r=60, t=40, b=45),
            paper_bgcolor="#111827", plot_bgcolor="#111827",
            font=dict(color="#e8edf5")
        )
        st.plotly_chart(fig_diff, use_container_width=True)

st.divider()

# ===== 动画展示 =====
st.markdown("#### 🎬 偏航角扫描动画")
col_gif, col_desc = st.columns([3, 1])

with col_gif:
    gif_path = os.path.join(BASE, "wake_animation.gif")
    if os.path.exists(gif_path):
        with open(gif_path, "rb") as f:
            gif_bytes = f.read()
        st.image(gif_bytes, use_container_width=True)
    else:
        st.warning("未找到 wake_animation.gif，请先运行 export_gif.py")

with col_desc:
    st.markdown("""
**动画说明**

偏航角从 **-30°** 扫描至 **+30°** 再返回。

**关键现象：**
- 偏航角 = 0° 时，下游风机完全处于尾流遮挡区
- 偏航角 ≠ 0° 时，尾流向侧方偏转，下游入流风速回升
- 最优偏航角约为 **+25°**，总功率提升 **8.1%**
    """)