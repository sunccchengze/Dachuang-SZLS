import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from surrogate_model import predict_power, find_optimal_yaw, U_min, U_max

st.set_page_config(page_title="功率需求跟踪", page_icon="🎛️", layout="wide")

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

st.markdown("## 🎛️ 电网功率需求跟踪")
st.caption("输入电网下发的目标功率，系统自动搜索满足需求的最优偏航角组合")
st.divider()

# ===== 读取数据 =====
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@st.cache_data
def load_cases():
    df = pd.read_csv(os.path.join(BASE, "cases_multi.csv"))
    df["power_total"] = df["power_1"] + df["power_2"]
    return df

df = load_cases()

# ===== 当前风速下的功率范围 =====
def get_power_range(U_inf):
    """计算当前风速下的功率范围"""
    yaw_scan = np.linspace(-30, 30, 120)
    totals   = [sum(predict_power(y, U_inf)) for y in yaw_scan]
    return min(totals), max(totals)

def find_yaw_for_target(target_power, U_inf, n_search=120):
    """
    给定目标功率和风速，搜索最接近目标功率的偏航角
    返回：(best_yaw, actual_power, error_pct)
    ⚠️ 注意：这里用的是插值代理模型（样条插值）
    开学后接入控制组真实优化算法时，替换此函数即可
    """
    yaw_candidates = np.linspace(-30, 30, n_search)
    totals = [sum(predict_power(y, U_inf)) for y in yaw_candidates]

    # 找最接近目标功率的偏航角
    errors   = [abs(t - target_power) for t in totals]
    best_idx = int(np.argmin(errors))
    best_yaw = yaw_candidates[best_idx]
    actual   = totals[best_idx]
    err_pct  = abs(actual - target_power) / target_power * 100

    return best_yaw, actual, err_pct

# ===== 侧边栏 =====
with st.sidebar:
    st.markdown("## ⚙️ 输入参数")
    st.divider()

    U_input = st.slider(
        "当前来流风速 (m/s)",
        min_value=float(U_min),
        max_value=float(U_max),
        value=8.0, step=0.1
    )

    # 动态计算当前风速下的功率范围
    p_min, p_max = get_power_range(U_input)

    st.divider()
    st.markdown("**当前风速可用功率范围**")
    st.markdown(f"""
- 最小可控功率：**{p_min:.0f} kW**
- 最大可用功率：**{p_max:.0f} kW**
    """)

    st.divider()

    target_power = st.slider(
        "电网目标功率需求 (kW)",
        min_value=int(p_min * 0.95),
        max_value=int(p_max * 1.05),
        value=int((p_min + p_max) / 2),
        step=10
    )

    st.divider()
    st.markdown("**⚠️ 模型说明**")
    st.markdown("""
当前使用**样条插值代理模型**。

开学后接入控制组真实优化算法时，
只需替换 `find_yaw_for_target()` 函数，
界面无需修改。
    """)

# ===== 求解 =====
best_yaw, actual_power, err_pct = find_yaw_for_target(
    target_power, U_input)
best_p1, best_p2 = predict_power(best_yaw, U_input)

# 判断是否可达
feasible = (p_min * 0.95 <= target_power <= p_max * 1.05)

# ===== 顶部状态栏 =====
if not feasible:
    st.error(f"⚠️ 目标功率 {target_power:.0f} kW 超出当前风速（{U_input:.1f} m/s）"
             f"的可控范围 [{p_min:.0f}, {p_max:.0f}] kW，无法满足。")
elif err_pct < 2.0:
    st.success(f"✅ 找到满足需求的偏航角，跟踪误差 {err_pct:.2f}%")
else:
    st.warning(f"⚠️ 最接近方案误差 {err_pct:.2f}%，超过 2% 阈值，建议调整目标功率。")

st.markdown("<br>", unsafe_allow_html=True)

# ===== 指标卡片 =====
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("目标功率",   f"{target_power:.0f} kW")
c2.metric("推荐偏航角", f"{best_yaw:+.1f}°")
c3.metric("实际输出",
          f"{actual_power:.0f} kW",
          delta=f"{actual_power - target_power:+.0f} kW")
c4.metric("跟踪误差",   f"{err_pct:.2f}%")
c5.metric("上游 P₁ / 下游 P₂",
          f"{best_p1:.0f} / {best_p2:.0f} kW")

st.markdown("<br>", unsafe_allow_html=True)

# ===== 主图区 =====
col_left, col_right = st.columns([3, 2])

with col_left:
    st.markdown("#### 📈 功率输出 vs 偏航角（当前风速）")

    yaw_fine  = np.linspace(-30, 30, 200)
    p_fine    = [sum(predict_power(y, U_input)) for y in yaw_fine]

    fig_main = go.Figure()

    # 可达功率范围填充
    fig_main.add_hrect(
        y0=p_min, y1=p_max,
        fillcolor="rgba(39,174,96,0.06)",
        line_width=0,
        annotation_text="可控功率范围",
        annotation_position="top left",
        annotation_font=dict(color="#27ae60", size=11)
    )

    # 功率曲线
    fig_main.add_trace(go.Scatter(
        x=yaw_fine, y=p_fine,
        mode="lines", name="总功率曲线",
        line=dict(color="#4a9eff", width=2.5),
        fill="tozeroy",
        fillcolor="rgba(74,158,255,0.06)"
    ))

    # 目标功率水平线
    fig_main.add_hline(
        y=target_power,
        line_dash="dash", line_color="#e74c3c", line_width=2,
        annotation_text=f"目标 {target_power:.0f} kW",
        annotation_position="right",
        annotation_font=dict(color="#e74c3c", size=12)
    )

    # 最优点
    fig_main.add_trace(go.Scatter(
        x=[best_yaw], y=[actual_power],
        mode="markers+text",
        name=f"推荐偏航 {best_yaw:+.1f}°",
        marker=dict(size=16, color="#27ae60",
                    symbol="star",
                    line=dict(color="white", width=1.5)),
        text=[f"  {best_yaw:+.1f}°<br>  {actual_power:.0f} kW"],
        textposition="middle right",
        textfont=dict(color="#27ae60", size=11)
    ))

    fig_main.update_layout(
        xaxis=dict(title="偏航角 (°)", showgrid=True,
                   gridcolor="#1e2d4a", color="#8899bb"),
        yaxis=dict(title="总功率 (kW)", showgrid=True,
                   gridcolor="#1e2d4a", color="#8899bb"),
        height=420,
        margin=dict(l=10, r=80, t=20, b=50),
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font=dict(color="#e8edf5"),
        legend=dict(orientation="h", y=-0.18, x=0,
                    font=dict(size=11),
                    bgcolor="rgba(0,0,0,0)")
    )
    st.plotly_chart(fig_main, use_container_width=True)

with col_right:
    # 目标功率 vs 实际输出 对比
    st.markdown("#### 🔄 目标 vs 实际输出")

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=actual_power,
        delta=dict(
            reference=target_power,
            valueformat=".0f",
            suffix=" kW",
            increasing=dict(color="#27ae60"),
            decreasing=dict(color="#e74c3c")
        ),
        gauge=dict(
            axis=dict(
                range=[p_min * 0.9, p_max * 1.1],
                tickcolor="#8899bb",
                tickfont=dict(color="#8899bb", size=10)
            ),
            bar=dict(color="#4a9eff"),
            bgcolor="#1e2d4a",
            bordercolor="#1e2d4a",
            steps=[
                dict(range=[p_min * 0.9, p_min],
                     color="rgba(230,126,34,0.2)"),
                dict(range=[p_min, p_max],
                     color="rgba(39,174,96,0.1)"),
                dict(range=[p_max, p_max * 1.1],
                     color="rgba(230,126,34,0.2)"),
            ],
            threshold=dict(
                line=dict(color="#e74c3c", width=3),
                thickness=0.85,
                value=target_power
            )
        ),
        number=dict(
            suffix=" kW",
            font=dict(color="#e8edf5", size=28)
        ),
        title=dict(
            text=f"实际输出功率<br>"
                 f"<span style='font-size:13px;color:#8899bb'>"
                 f"目标：{target_power:.0f} kW</span>",
            font=dict(color="#e8edf5", size=14)
        )
    ))
    fig_gauge.update_layout(
        height=280,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="#111827",
        font=dict(color="#e8edf5")
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

    # 不同目标功率所需偏航角
    st.markdown("#### 🗺️ 功率-偏航角映射")
    target_scan = np.linspace(p_min, p_max, 50)
    yaw_scan    = [find_yaw_for_target(t, U_input)[0] for t in target_scan]

    fig_map = go.Figure()
    fig_map.add_trace(go.Scatter(
        x=target_scan, y=yaw_scan,
        mode="lines",
        line=dict(color="#9b59b6", width=2),
        fill="tozeroy",
        fillcolor="rgba(155,89,182,0.08)",
        name="所需偏航角"
    ))
    fig_map.add_trace(go.Scatter(
        x=[target_power], y=[best_yaw],
        mode="markers",
        marker=dict(size=12, color="#e74c3c",
                    line=dict(color="white", width=2)),
        name="当前目标"
    ))
    fig_map.update_layout(
        xaxis=dict(title="目标功率 (kW)", showgrid=True,
                   gridcolor="#1e2d4a", color="#8899bb"),
        yaxis=dict(title="所需偏航角 (°)", showgrid=True,
                   gridcolor="#1e2d4a", color="#8899bb"),
        height=190,
        margin=dict(l=10, r=10, t=15, b=40),
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font=dict(color="#e8edf5"),
        legend=dict(orientation="h", y=-0.4, x=0,
                    font=dict(size=10),
                    bgcolor="rgba(0,0,0,0)")
    )
    st.plotly_chart(fig_map, use_container_width=True)

st.divider()

# ===== 多风速功率跟踪能力总览 =====
st.markdown("#### 🌐 多风速下的功率跟踪能力")
st.caption("展示不同风速下系统的可控功率范围，帮助调度员了解当前风场的调节能力")

U_levels = [6.0, 8.0, 10.0, 12.0]
ranges   = [get_power_range(U) for U in U_levels]
p_mins   = [r[0] for r in ranges]
p_maxs   = [r[1] for r in ranges]

fig_range = go.Figure()
fig_range.add_trace(go.Bar(
    name="可控功率范围",
    x=[f"{U:.0f} m/s" for U in U_levels],
    y=[mx - mn for mx, mn in zip(p_maxs, p_mins)],
    base=p_mins,
    marker_color="rgba(74,158,255,0.5)",
    marker_line=dict(color="#4a9eff", width=1.5),
    text=[f"{mn:.0f}~{mx:.0f} kW"
          for mn, mx in zip(p_mins, p_maxs)],
    textposition="inside",
    textfont=dict(color="white", size=11)
))

# 当前目标功率水平线
fig_range.add_hline(
    y=target_power,
    line_dash="dash", line_color="#e74c3c", line_width=1.5,
    annotation_text=f"当前目标 {target_power:.0f} kW",
    annotation_font=dict(color="#e74c3c", size=11)
)

fig_range.update_layout(
    xaxis=dict(title="来流风速", color="#8899bb", showgrid=False),
    yaxis=dict(title="功率 (kW)", showgrid=True,
               gridcolor="#1e2d4a", color="#8899bb"),
    height=280,
    margin=dict(l=10, r=10, t=20, b=50),
    paper_bgcolor="#111827",
    plot_bgcolor="#111827",
    font=dict(color="#e8edf5"),
    showlegend=False
)
st.plotly_chart(fig_range, use_container_width=True)

st.divider()

# ===== 接口预留说明 =====
# ===== 接口预留说明 =====
with st.expander("🔗 控制组接口预留说明（开学后对接用）"):
    st.markdown("**当前使用的占位函数：**")
    st.code("""
def find_yaw_for_target(target_power, U_inf, n_search=120):
    # 当前：样条插值代理模型的暴力搜索
    # 开学后替换为控制组的真实优化算法
    yaw_candidates = np.linspace(-30, 30, n_search)
    totals = [sum(predict_power(y, U_inf)) for y in yaw_candidates]
    best_idx = int(np.argmin([abs(t - target_power) for t in totals]))
    return yaw_candidates[best_idx], totals[best_idx], ...
""", language="python")

    st.markdown("**控制组需要提供的接口格式：**")
    st.code("""
def find_yaw_for_target(target_power, U_inf):
    # 输入：target_power (kW), U_inf (m/s)
    # 输出：best_yaw (°), actual_power (kW), error_pct (%)
    ...
    return best_yaw, actual_power, error_pct
""", language="python")

    st.markdown("""
**替换方法：**
将上面的函数放入 `surrogate_model.py`，覆盖现有同名函数，
本页面无需做任何修改即可接入控制组算法。
    """)