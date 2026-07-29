import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import os

st.set_page_config(page_title="阵列优化", page_icon="⚡", layout="wide")

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

st.markdown("## ⚡ 3×3 风机阵列协同优化")
st.caption("上游三台同步偏航，尾流偏转累积效应最大化全场功率")
st.divider()

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@st.cache_data
def load_array():
    df = pd.read_csv(os.path.join(BASE, "cases_array.csv"))
    return df

df = load_array()
baseline = df[df["yaw_upstream"] == 0]["power_total"].values[0]
best     = df.loc[df["power_total"].idxmax()]

# ===== 侧边栏 =====
with st.sidebar:
    st.markdown("## ⚙️ 参数设置")
    st.divider()
    yaw_select = st.select_slider(
        "上游偏航角 (°)",
        options=sorted(df["yaw_upstream"].astype(int).tolist()),
        value=0
    )
    st.divider()
    st.markdown("**📐 阵列参数**")
    st.markdown("""
- 布局：**3×3 九台风机**
- 顺风间距：**5D = 630 m**
- 横向间距：**3D = 378 m**
- 控制策略：**上游统一偏航**
- 下游偏航：**固定 0°**
    """)
    st.divider()
    st.markdown("**🎯 全局最优**")
    st.markdown(f"""
- 最优偏航角：**{best['yaw_upstream']:+.0f}°**
- 最优总功率：**{best['power_total']:.0f} kW**
- 最大增益：**+{best['gain_pct']:.1f}%**
    """)

# ===== 找当前工况 =====
row = df[df["yaw_upstream"] == yaw_select].iloc[0]
p_total  = row["power_total"]
gain_pct = row["gain_pct"]
powers   = [row[f"power_{i+1}"] for i in range(9)]

# ===== 顶部指标 =====
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("当前偏航角",   f"{yaw_select:+.0f}°")
c2.metric("总功率",
          f"{p_total:.0f} kW",
          delta=f"{p_total - baseline:+.0f} kW vs 0°")
c3.metric("功率增益",     f"{gain_pct:+.1f}%")
c4.metric("最优偏航角",   f"{best['yaw_upstream']:+.0f}°")
c5.metric("最大增益",     f"+{best['gain_pct']:.1f}%")

st.markdown("<br>", unsafe_allow_html=True)

# ===== 主图区 =====
col_layout, col_curves = st.columns([3, 2])

with col_layout:
    st.markdown("#### 🗺️ 风机阵列功率分布图")

    D = 126.0
    layout_x = [row_i * 5 * D for row_i in range(3) for col_i in range(3)]
    layout_y = [(col_i - 1) * 3 * D for row_i in range(3) for col_i in range(3)]

    # 功率归一化到颜色
    p_max = max(powers)
    p_min = min(powers)

    fig_layout = go.Figure()

    # 画尾流示意（简单箭头方向线）
    yaw_rad = np.radians(yaw_select)
    for i in range(3):
        tx = layout_x[i]
        ty = layout_y[i]
        dx = 400 * np.cos(yaw_rad)
        dy = 400 * np.sin(yaw_rad)
        fig_layout.add_trace(go.Scatter(
            x=[tx, tx + dx],
            y=[ty, ty + dy],
            mode="lines",
            line=dict(color="rgba(74,158,255,0.3)",
                      width=30),
            showlegend=False,
            hoverinfo="skip"
        ))

    # 画风机（圆圈，颜色表示功率）
    for i, (tx, ty, p) in enumerate(zip(layout_x, layout_y, powers)):
        row_i = i // 3 + 1
        col_i = i % 3 + 1
        is_upstream = (row_i == 1)

        # 归一化颜色
        norm = (p - p_min) / (p_max - p_min + 1e-6)
        r = int(74 + (230 - 74) * (1 - norm))
        g = int(158 + (126 - 158) * (1 - norm))
        b = int(255 + (34 - 255) * (1 - norm))

        fig_layout.add_trace(go.Scatter(
            x=[tx], y=[ty],
            mode="markers+text",
            marker=dict(
                size=40,
                color=f"rgb({r},{g},{b})",
                symbol="circle",
                line=dict(
                    color="white" if is_upstream else "rgba(255,255,255,0.3)",
                    width=3 if is_upstream else 1
                )
            ),
            text=[f"T{i+1}<br>{p:.0f}"],
            textposition="middle center",
            textfont=dict(size=10, color="white"),
            name=f"风机{i+1}（{p:.0f}kW）",
            showlegend=True,
            hovertemplate=(
                f"<b>风机 {i+1}</b><br>"
                f"第 {row_i} 排第 {col_i} 列<br>"
                f"功率：{p:.0f} kW<br>"
                f"{'🔵 上游（可调偏航）' if is_upstream else '⚪ 下游（固定0°）'}"
                "<extra></extra>"
            )
        ))

    # 坐标轴标注
    fig_layout.add_annotation(
        x=630, y=-550, text="风向 →",
        showarrow=False,
        font=dict(color="#8899bb", size=12)
    )

    fig_layout.update_layout(
        xaxis=dict(
            title="顺风方向 x (m)",
            showgrid=True, gridcolor="#1e2d4a",
            color="#8899bb",
            range=[-200, 1500]
        ),
        yaxis=dict(
            title="横向 y (m)",
            showgrid=True, gridcolor="#1e2d4a",
            color="#8899bb",
            range=[-600, 600],
            scaleanchor="x", scaleratio=1
        ),
        height=460,
        margin=dict(l=10, r=10, t=20, b=50),
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font=dict(color="#e8edf5"),
        legend=dict(
            orientation="v",
            x=1.02, y=1,
            font=dict(size=10),
            bgcolor="rgba(0,0,0,0)"
        ),
        showlegend=False
    )
    st.plotly_chart(fig_layout, use_container_width=True)
    st.caption("圆圈颜色：蓝=高功率，橙=低功率 | 白色粗边框=上游可调风机 | 蓝色光晕=尾流偏转方向")

with col_curves:
    # 总功率曲线
    st.markdown("#### 📈 总功率 vs 偏航角")
    fig_total = go.Figure()
    fig_total.add_trace(go.Scatter(
        x=df["yaw_upstream"], y=df["power_total"],
        mode="lines+markers", name="总功率",
        line=dict(color="#4a9eff", width=2.5),
        marker=dict(size=6),
        fill="tozeroy",
        fillcolor="rgba(74,158,255,0.08)"
    ))
    fig_total.add_trace(go.Scatter(
        x=[yaw_select], y=[p_total],
        mode="markers", name="当前",
        marker=dict(size=14, color="#e74c3c",
                    line=dict(color="white", width=2))
    ))
    fig_total.add_vline(
        x=best["yaw_upstream"],
        line_dash="dash", line_color="#27ae60",
        annotation_text=f"最优 {best['yaw_upstream']:+.0f}°",
        annotation_font=dict(color="#27ae60", size=11)
    )
    fig_total.update_layout(
        xaxis=dict(title="上游偏航角 (°)", showgrid=True,
                   gridcolor="#1e2d4a", color="#8899bb"),
        yaxis=dict(title="总功率 (kW)", showgrid=True,
                   gridcolor="#1e2d4a", color="#8899bb"),
        height=200,
        margin=dict(l=10, r=10, t=15, b=40),
        paper_bgcolor="#111827", plot_bgcolor="#111827",
        font=dict(color="#e8edf5"),
        legend=dict(orientation="h", y=-0.35, x=0,
                    font=dict(size=10), bgcolor="rgba(0,0,0,0)")
    )
    st.plotly_chart(fig_total, use_container_width=True)

    # 各排平均功率
    st.markdown("#### 🏭 各排平均功率")
    row1_avg = np.mean([row[f"power_{i+1}"] for i in range(3)])
    row2_avg = np.mean([row[f"power_{i+1}"] for i in range(3, 6)])
    row3_avg = np.mean([row[f"power_{i+1}"] for i in range(6, 9)])

    fig_rows = go.Figure()
    fig_rows.add_trace(go.Bar(
        x=["第1排（上游）", "第2排（中游）", "第3排（下游）"],
        y=[row1_avg, row2_avg, row3_avg],
        marker_color=["#4a9eff", "#27ae60", "#e67e22"],
        text=[f"{v:.0f} kW" for v in [row1_avg, row2_avg, row3_avg]],
        textposition="outside",
        textfont=dict(color="#e8edf5", size=11)
    ))
    fig_rows.update_layout(
        xaxis=dict(color="#8899bb", showgrid=False),
        yaxis=dict(title="平均功率 (kW)", showgrid=True,
                   gridcolor="#1e2d4a", color="#8899bb",
                   range=[0, max(row1_avg, row2_avg, row3_avg) * 1.2]),
        height=200,
        margin=dict(l=10, r=10, t=15, b=40),
        paper_bgcolor="#111827", plot_bgcolor="#111827",
        font=dict(color="#e8edf5"),
        showlegend=False
    )
    st.plotly_chart(fig_rows, use_container_width=True)

st.divider()

# ===== 九台风机功率热力图 =====
st.markdown("#### 🔥 全场功率分布热力图（偏航角 × 风机编号）")

power_matrix = np.zeros((len(df), 9))
for i, r in df.iterrows():
    for j in range(9):
        power_matrix[i, j] = r[f"power_{j+1}"]

fig_hm = go.Figure(go.Heatmap(
    z=power_matrix,
    x=[f"风机{i+1}\n(排{i//3+1}列{i%3+1})" for i in range(9)],
    y=[f"{y:+.0f}°" for y in df["yaw_upstream"]],
    colorscale="Viridis",
    colorbar=dict(title="功率 (kW)", thickness=15),
    text=[[f"{v:.0f}" for v in row] for row in power_matrix],
    texttemplate="%{text}",
    textfont=dict(size=10, color="white")
))
fig_hm.update_layout(
    xaxis=dict(title="风机编号", color="#8899bb"),
    yaxis=dict(title="上游偏航角", color="#8899bb"),
    height=380,
    margin=dict(l=10, r=10, t=20, b=50),
    paper_bgcolor="#111827", plot_bgcolor="#111827",
    font=dict(color="#e8edf5")
)
st.plotly_chart(fig_hm, use_container_width=True)

st.divider()

# ===== 对比两台 vs 九台 =====
st.markdown("#### 📊 两台串列 vs 3×3 阵列：偏航控制效果对比")

df2 = pd.read_csv(os.path.join(BASE, "cases.csv"))
df2["power_total"] = df2["power_1"] + df2["power_2"]
base2 = df2[df2["yaw_1"] == 0]["power_total"].values[0]
df2["gain_pct"] = (df2["power_total"] - base2) / base2 * 100

fig_cmp = go.Figure()
fig_cmp.add_trace(go.Scatter(
    x=df2["yaw_1"], y=df2["gain_pct"],
    mode="lines+markers", name="两台串列",
    line=dict(color="#4a9eff", width=2),
    marker=dict(size=6)
))
fig_cmp.add_trace(go.Scatter(
    x=df["yaw_upstream"], y=df["gain_pct"],
    mode="lines+markers", name="3×3 阵列",
    line=dict(color="#27ae60", width=2),
    marker=dict(size=6)
))
fig_cmp.add_hline(y=0, line_dash="dot",
                  line_color="#4a5568", line_width=1)
fig_cmp.update_layout(
    xaxis=dict(title="上游偏航角 (°)", showgrid=True,
               gridcolor="#1e2d4a", color="#8899bb"),
    yaxis=dict(title="功率增益 (%)", showgrid=True,
               gridcolor="#1e2d4a", color="#8899bb"),
    height=280,
    margin=dict(l=10, r=10, t=20, b=50),
    paper_bgcolor="#111827", plot_bgcolor="#111827",
    font=dict(color="#e8edf5"),
    legend=dict(orientation="h", y=-0.25, x=0,
                font=dict(size=11), bgcolor="rgba(0,0,0,0)")
)
st.plotly_chart(fig_cmp, use_container_width=True)