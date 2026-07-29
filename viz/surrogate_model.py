import numpy as np
import pandas as pd
from scipy.interpolate import RegularGridInterpolator
from pathlib import Path

BASE = Path(__file__).parent

# ===== 读取多风速数据 =====
df = pd.read_csv(BASE / "cases_multi.csv")
df["power_total"] = df["power_1"] + df["power_2"]

wind_speeds = sorted(df["U_inf"].unique())
yaw_angles  = sorted(df["yaw_1"].unique())

# 构建二维网格矩阵
P1_matrix   = np.zeros((len(wind_speeds), len(yaw_angles)))
P2_matrix   = np.zeros((len(wind_speeds), len(yaw_angles)))
Ptot_matrix = np.zeros((len(wind_speeds), len(yaw_angles)))

for i, U in enumerate(wind_speeds):
    for j, yaw in enumerate(yaw_angles):
        row = df[(df["U_inf"] == U) & (df["yaw_1"] == yaw)].iloc[0]
        P1_matrix[i, j]   = row["power_1"]
        P2_matrix[i, j]   = row["power_2"]
        Ptot_matrix[i, j] = row["power_total"]

# 二维插值器
interp_p1   = RegularGridInterpolator(
    (wind_speeds, yaw_angles), P1_matrix,   method="linear")
interp_p2   = RegularGridInterpolator(
    (wind_speeds, yaw_angles), P2_matrix,   method="linear")
interp_ptot = RegularGridInterpolator(
    (wind_speeds, yaw_angles), Ptot_matrix, method="linear")

U_min, U_max     = min(wind_speeds), max(wind_speeds)
yaw_min, yaw_max = min(yaw_angles),  max(yaw_angles)


def predict_power(yaw_angle, U_inf=8.0):
    """
    输入偏航角和风速，返回 (p1, p2)
    yaw_angle : float，度，范围 -30 到 +30
    U_inf     : float，m/s，范围 6 到 12
    """
    U   = float(np.clip(U_inf,     U_min,   U_max))
    yaw = float(np.clip(yaw_angle, yaw_min, yaw_max))
    p1  = float(interp_p1([[U, yaw]]).item())
    p2  = float(interp_p2([[U, yaw]]).item())
    return p1, p2


def find_optimal_yaw(U_inf=8.0, n_search=120):
    """
    给定风速，网格搜索最优偏航角
    返回 (best_yaw, best_p1, best_p2, best_total, gain_pct)
    """
    U = float(np.clip(U_inf, U_min, U_max))
    yaw_candidates = np.linspace(yaw_min, yaw_max, n_search)

    totals     = [float(interp_ptot([[U, y]]).item()) for y in yaw_candidates]
    best_idx   = int(np.argmax(totals))
    best_yaw   = yaw_candidates[best_idx]
    best_total = totals[best_idx]

    p1, p2   = predict_power(best_yaw, U)
    baseline = float(interp_ptot([[U, 0.0]]).item())
    gain_pct = (best_total - baseline) / baseline * 100

    return best_yaw, p1, p2, best_total, gain_pct


if __name__ == "__main__":
    print("验证二维插值模型：")
    for U in [6, 8, 10, 12]:
        yaw, p1, p2, ptot, gain = find_optimal_yaw(U)
        print(f"  风速={U}m/s  最优偏航={yaw:+.1f}°  "
              f"P1={p1:.0f}kW  P2={p2:.0f}kW  "
              f"总={ptot:.0f}kW  增益={gain:+.1f}%")
    print("✅ 二维代理模型就绪")