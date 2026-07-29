import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="热力矩阵", page_icon="🔥", layout="wide")

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

st.markdown("## 🔥 多风速偏航优化热力矩阵")
st.divider()

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@st.cache_data
def load_multi():
    return pd.read_csv(os.path.join(BASE, "cases_multi.csv"))

df = load_multi()
df["power_total"] = df["power_1"] + df["power_2"]

wind_speeds = sorted(df["U_inf"].unique())
yaw_angles  = sorted(df["yaw_1"].unique())

# ===== 侧边栏 =====
with st.sidebar:
    st.markdown("## ⚙️ 显示设置")
    st.divider()

    metric = st.radio(
        "显示指标",
        ["总功率 (kW)", "功率增益 (%)", "下游风机 P₂ (kW)"],
        index=1
    )

    st.divider()
    st.markdown("**数据说明**")
    st.markdown(f"""
- 风速范围：**{min(wind_speeds)}-{max(wind_speeds)} m/s**
- 偏航角范围：**-30° 到 +30°**
- 工况总数：**{len(df)}** 个
- 风机型号：**NREL 5MW**
- 额定功率：**5000 kW**
    """)

# ===== 构建矩阵数据 =====
matrix = np.zeros((len(wind_speeds), len(yaw_angles)))
text_matrix = []

for i, U in enumerate(wind_speeds):
    row_text = []
    baseline = df[(df["U_inf"] == U) & (df["yaw_1"] == 0)]["power_total"].values[0]

    for j, yaw in enumerate(yaw_angles):
        row = df[(df["U_inf"] == U) & (df["yaw_1"] == yaw)].iloc[0]
        p_total = row["power_total"]
        gain    = (p_total - baseline) / baseline * 100

        if metric == "总功率 (kW)":
            val = p_total
            text = f"{p_total:.0f} kW"
        elif metric == "功率增益 (%)":
            val = gain
            text = f"{gain:+.1f}%"
        else:
            val = row["power_2"]
            text = f"{row['power_2']:.0f} kW"

        matrix[i, j] = val
        row_text.append(text)
    text_matrix.append(row_text)

# ===== 配色方案 =====
if metric == "功率增益 (%)":
    colorscale = "RdYlGn"
    zmid = 0
else:
    colorscale = "Viridis"
    zmid = None

# ===== 热力矩阵图 =====
fig_heatmap = go.Figure(go.Heatmap(
    z=matrix,
    x=[f"{y:+.0f}°" for y in yaw_angles],
    y=[f"{U:.0f} m/s" for U in wind_speeds],
    text=text_matrix,
    texttemplate="%{text}",
    textfont=dict(size=12, color="white"),
    colorscale=colorscale,
    zmid=zmid,
    colorbar=dict(
        title=metric,
        thickness=15,
        len=0.8
    )
))

fig_heatmap.update_layout(
    title=dict(
        text=f"偏航角 × 风速 热力矩阵  |  指标：{metric}",
        font=dict(color="#e8edf5", size=15),
        x=0.5
    ),
    xaxis=dict(
        title="上游风机偏航角",
        color="#8899bb",
        tickfont=dict(size=12)
    ),
    yaxis=dict(
        title="来流风速",
        color="#8899bb",
        tickfont=dict(size=12)
    ),
    height=380,
    margin=dict(l=10, r=10, t=60, b=50),
    paper_bgcolor="#111827",
    plot_bgcolor="#111827",
    font=dict(color="#e8edf5")
)

st.plotly_chart(fig_heatmap, use_container_width=True)

st.divider()

# ===== 每个风速的功率曲线 =====
st.markdown("#### 📈 各风速下总功率 vs 偏航角")

fig_curves = go.Figure()
colors = ["#4a9eff", "#27ae60", "#e67e22", "#e74c3c"]

for U, color in zip(wind_speeds, colors):
    df_U = df[df["U_inf"] == U].sort_values("yaw_1")
    baseline = df_U[df_U["yaw_1"] == 0]["power_total"].values[0]
    best_yaw = df_U.loc[df_U["power_total"].idxmax(), "yaw_1"]

    fig_curves.add_trace(go.Scatter(
        x=df_U["yaw_1"],
        y=df_U["power_total"],
        mode="lines+markers",
        name=f"{U:.0f} m/s（最优 {best_yaw:+.0f}°）",
        line=dict(color=color, width=2),
        marker=dict(size=6)
    ))

fig_curves.update_layout(
    xaxis=dict(
        title="偏航角 (°)",
        showgrid=True, gridcolor="#1e2d4a",
        color="#8899bb"
    ),
    yaxis=dict(
        title="总功率 (kW)",
        showgrid=True, gridcolor="#1e2d4a",
        color="#8899bb"
    ),
    height=320,
    margin=dict(l=10, r=10, t=20, b=50),
    paper_bgcolor="#111827",
    plot_bgcolor="#111827",
    font=dict(color="#e8edf5"),
    legend=dict(
        orientation="h", y=-0.25, x=0,
        font=dict(size=11),
        bgcolor="rgba(0,0,0,0)"
    )
)

st.plotly_chart(fig_curves, use_container_width=True)

st.divider()

# ===== 每个风速的最优偏航角汇总 =====
st.markdown("#### 🎯 各风速最优偏航角汇总")

cols = st.columns(len(wind_speeds))
for col, U in zip(cols, wind_speeds):
    df_U    = df[df["U_inf"] == U]
    best    = df_U.loc[df_U["power_total"].idxmax()]
    baseline = df_U[df_U["yaw_1"] == 0]["power_total"].values[0]
    gain    = (best["power_total"] - baseline) / baseline * 100
    col.metric(
        label=f"风速 {U:.0f} m/s",
        value=f"偏航 {best['yaw_1']:+.0f}°",
        delta=f"+{gain:.1f}%"
    )