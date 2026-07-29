import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

st.set_page_config(page_title="POD分析", page_icon="🔬", layout="wide")

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

st.markdown("## 🔬 POD 本征正交分解分析")
st.caption("Principal Orthogonal Decomposition · 流场降阶核心技术")
st.divider()

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@st.cache_data
def load_pod():
    path = os.path.join(BASE, "pod_results", "pod_data.npz")
    raw  = np.load(path)
    return {k: raw[k] for k in raw.files}

pod = load_pod()

x            = pod["x"]
y            = pod["y"]
x_mean       = pod["x_mean"]
modes        = pod["modes"]
energy_frac  = pod["energy_frac"]
energy_cum   = pod["energy_cum"]
coefficients = pod["coefficients"]
yaw_angles   = pod["yaw_angles"]
n_snapshots  = int(pod["n_snapshots"])

# ===== 侧边栏 =====
with st.sidebar:
    st.markdown("## ⚙️ 分析设置")
    st.divider()

    k_recon = st.slider(
        "重构使用模态数 k",
        min_value=1,
        max_value=int(n_snapshots),
        value=3,
        step=1
    )

    st.divider()
    mode_view = st.selectbox(
        "查看第几阶模态",
        options=list(range(1, min(11, n_snapshots + 1))),
        index=0
    )

    st.divider()
    snap_idx = st.selectbox(
        "对比工况",
        options=list(range(n_snapshots)),
        format_func=lambda i: f"偏航 {yaw_angles[i]:+.0f}°",
        index=6
    )

# ===== 顶部指标 =====
k_95 = int(np.searchsorted(energy_cum, 0.95)) + 1
k_99 = int(np.searchsorted(energy_cum, 0.99)) + 1

c1, c2, c3, c4 = st.columns(4)
c1.metric("快照数量",       f"{n_snapshots} 个")
c2.metric("95% 能量模态数", f"{k_95} 个")
c3.metric("99% 能量模态数", f"{k_99} 个")
c4.metric(f"前 {k_recon} 模态能量",
          f"{energy_cum[k_recon-1]*100:.2f}%")

st.markdown("<br>", unsafe_allow_html=True)

# ===== 第一行：能量分布 =====
st.markdown("#### 📊 模态能量分布")
col_bar, col_cum = st.columns(2)

with col_bar:
    fig_energy = go.Figure()
    colors = ["#4a9eff" if i < k_recon else "#2d3f5a"
              for i in range(n_snapshots)]
    fig_energy.add_trace(go.Bar(
        x=[f"模态 {i+1}" for i in range(n_snapshots)],
        y=energy_frac * 100,
        marker_color=colors,
        text=[f"{e*100:.2f}%" for e in energy_frac],
        textposition="outside",
        textfont=dict(color="#a8bcdf", size=10),
        name="各模态能量占比"
    ))
    fig_energy.update_layout(
        title=dict(text="各模态能量占比（蓝色=当前选择模态数）",
                   font=dict(color="#e8edf5", size=13), x=0.5),
        xaxis=dict(color="#8899bb", showgrid=False),
        yaxis=dict(title="能量占比 (%)", color="#8899bb",
                   showgrid=True, gridcolor="#1e2d4a"),
        height=300,
        margin=dict(l=10, r=10, t=40, b=40),
        paper_bgcolor="#111827", plot_bgcolor="#111827",
        font=dict(color="#e8edf5"),
        showlegend=False
    )
    st.plotly_chart(fig_energy, use_container_width=True)

with col_cum:
    fig_cum = go.Figure()
    fig_cum.add_trace(go.Scatter(
        x=list(range(1, n_snapshots + 1)),
        y=energy_cum * 100,
        mode="lines+markers",
        line=dict(color="#4a9eff", width=2.5),
        marker=dict(size=8, color="#4a9eff"),
        fill="tozeroy",
        fillcolor="rgba(74,158,255,0.08)",
        name="累计能量"
    ))
    # 95% 和 99% 参考线
    fig_cum.add_hline(y=95, line_dash="dash",
                      line_color="#27ae60", line_width=1.5,
                      annotation_text="95%",
                      annotation_font=dict(color="#27ae60"))
    fig_cum.add_hline(y=99, line_dash="dash",
                      line_color="#e67e22", line_width=1.5,
                      annotation_text="99%",
                      annotation_font=dict(color="#e67e22"))
    # 当前选择竖线
    fig_cum.add_vline(x=k_recon, line_dash="dot",
                      line_color="#e74c3c", line_width=1.5,
                      annotation_text=f"k={k_recon}",
                      annotation_font=dict(color="#e74c3c"))
    fig_cum.update_layout(
        title=dict(text="累计能量 vs 模态数",
                   font=dict(color="#e8edf5", size=13), x=0.5),
        xaxis=dict(title="模态数 k", color="#8899bb",
                   showgrid=True, gridcolor="#1e2d4a",
                   tickmode="linear", dtick=1),
        yaxis=dict(title="累计能量 (%)", color="#8899bb",
                   showgrid=True, gridcolor="#1e2d4a",
                   range=[0, 101]),
        height=300,
        margin=dict(l=10, r=10, t=40, b=40),
        paper_bgcolor="#111827", plot_bgcolor="#111827",
        font=dict(color="#e8edf5"),
        showlegend=False
    )
    st.plotly_chart(fig_cum, use_container_width=True)

st.divider()

# ===== 第二行：均值场 + 选定模态 =====
st.markdown(f"#### 🗺️ 均值流场 与 第 {mode_view} 阶空间模态")
col_mean, col_mode = st.columns(2)

def make_field_plot(data, title, colorscale, zmid=None, zmin=None, zmax=None):
    fig = go.Figure(go.Heatmap(
        z=data, x=x, y=y,
        colorscale=colorscale,
        zmid=zmid, zmin=zmin, zmax=zmax,
        colorbar=dict(thickness=12, len=0.85,
                      title=dict(text="m/s", side="right"))
    ))
    fig.add_trace(go.Scatter(
        x=[0, 630], y=[0, 0], mode="markers",
        marker=dict(size=12, color="#e8edf5", symbol="triangle-up"),
        showlegend=False
    ))
    fig.update_layout(
        title=dict(text=title,
                   font=dict(size=13, color="#e8edf5"), x=0.5),
        xaxis=dict(title="x (m)", showgrid=False, color="#8899bb"),
        yaxis=dict(title="y (m)", showgrid=False, color="#8899bb"),
        height=300,
        margin=dict(l=10, r=60, t=40, b=45),
        paper_bgcolor="#111827", plot_bgcolor="#111827",
        font=dict(color="#e8edf5")
    )
    return fig

with col_mean:
    st.plotly_chart(
        make_field_plot(x_mean, "均值流场 ū(x,y)",
                        "RdBu_r", zmin=4, zmax=9),
        use_container_width=True)

with col_mode:
    mode_data = modes[mode_view - 1]
    abs_max   = np.max(np.abs(mode_data))
    st.plotly_chart(
        make_field_plot(mode_data,
                        f"第 {mode_view} 阶 POD 空间模态  "
                        f"（能量占比 {energy_frac[mode_view-1]*100:.2f}%）",
                        "RdBu", zmid=0,
                        zmin=-abs_max, zmax=abs_max),
        use_container_width=True)

st.divider()

# ===== 第三行：重构对比 =====
st.markdown(f"#### 🔄 流场重构对比（前 {k_recon} 个模态）")

# 重新做重构
import pandas as pd
df_cases = pd.read_csv(os.path.join(BASE, "cases.csv"))
df_cases = df_cases.sort_values("yaw_1").reset_index(drop=True)

snapshots = []
for _, row in df_cases.iterrows():
    path = os.path.join(BASE, "fields", f"{row['case_id']}.npz")
    d    = np.load(path)
    snapshots.append(d["u"].flatten())
X      = np.column_stack(snapshots)
x_mean_vec = X.mean(axis=1, keepdims=True)
X_c    = X - x_mean_vec

U_svd, S_svd, Vt_svd = np.linalg.svd(X_c, full_matrices=False)

# 重构选定快照
X_recon_vec = (x_mean_vec +
               U_svd[:, :k_recon] @
               np.diag(S_svd[:k_recon]) @
               Vt_svd[:k_recon, :])

original = X[:, snap_idx].reshape(64, 128)
recon    = X_recon_vec[:, snap_idx].reshape(64, 128)
error    = recon - original
rel_err  = np.mean(error**2) / np.mean(original**2) * 100

col_orig, col_recon, col_err = st.columns(3)

with col_orig:
    st.plotly_chart(
        make_field_plot(original,
                        f"原始流场（偏航 {yaw_angles[snap_idx]:+.0f}°）",
                        "RdBu_r", zmin=4, zmax=9),
        use_container_width=True)

with col_recon:
    st.plotly_chart(
        make_field_plot(recon,
                        f"POD重构（前 {k_recon} 个模态）",
                        "RdBu_r", zmin=4, zmax=9),
        use_container_width=True)

with col_err:
    abs_max_err = max(np.abs(error).max(), 1e-6)
    fig_err = go.Figure(go.Heatmap(
        z=error, x=x, y=y,
        colorscale="RdBu", zmid=0,
        zmin=-abs_max_err, zmax=abs_max_err,
        colorbar=dict(thickness=12, len=0.85,
                      title=dict(text="Δm/s", side="right"))
    ))
    fig_err.add_trace(go.Scatter(
        x=[0, 630], y=[0, 0], mode="markers",
        marker=dict(size=12, color="#e8edf5", symbol="triangle-up"),
        showlegend=False
    ))
    fig_err.update_layout(
        title=dict(
            text=f"重构误差  |  相对误差 = {rel_err:.4f}%",
            font=dict(size=13, color="#e8edf5"), x=0.5),
        xaxis=dict(title="x (m)", showgrid=False, color="#8899bb"),
        yaxis=dict(title="y (m)", showgrid=False, color="#8899bb"),
        height=300,
        margin=dict(l=10, r=60, t=40, b=45),
        paper_bgcolor="#111827", plot_bgcolor="#111827",
        font=dict(color="#e8edf5")
    )
    st.plotly_chart(fig_err, use_container_width=True)

# 误差指标
e1, e2, e3 = st.columns(3)
e1.metric("相对均方误差", f"{rel_err:.4f}%")
e2.metric("最大绝对误差", f"{np.abs(error).max():.4f} m/s")
e3.metric("平均绝对误差", f"{np.abs(error).mean():.4f} m/s")

st.divider()

# ===== 第四行：POD系数 vs 偏航角 =====
st.markdown("#### 📈 POD 时间系数 vs 偏航角")
st.caption("展示每个工况在各模态上的投影系数，反映偏航角如何激励不同模态")

fig_coef = go.Figure()
colors_coef = ["#4a9eff", "#27ae60", "#e67e22",
                "#e74c3c", "#9b59b6", "#1abc9c"]

for i in range(min(6, n_snapshots)):
    fig_coef.add_trace(go.Scatter(
        x=yaw_angles,
        y=coefficients[i],
        mode="lines+markers",
        name=f"模态 {i+1}（{energy_frac[i]*100:.1f}%）",
        line=dict(color=colors_coef[i], width=2),
        marker=dict(size=6)
    ))

fig_coef.update_layout(
    xaxis=dict(title="偏航角 (°)", showgrid=True,
               gridcolor="#1e2d4a", color="#8899bb"),
    yaxis=dict(title="POD 系数", showgrid=True,
               gridcolor="#1e2d4a", color="#8899bb"),
    height=300,
    margin=dict(l=10, r=10, t=20, b=50),
    paper_bgcolor="#111827", plot_bgcolor="#111827",
    font=dict(color="#e8edf5"),
    legend=dict(orientation="h", y=-0.25, x=0,
                font=dict(size=11),
                bgcolor="rgba(0,0,0,0)")
)
st.plotly_chart(fig_coef, use_container_width=True)