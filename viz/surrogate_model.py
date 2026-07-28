import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline
from pathlib import Path

# 无论从哪里导入，都能找到cases.csv
BASE = Path(__file__).parent
df = pd.read_csv(BASE / "cases.csv")
df = df.sort_values("yaw_1").reset_index(drop=True)

yaw_data = df["yaw_1"].values.astype(float)
p1_data  = df["power_1"].values.astype(float)
p2_data  = df["power_2"].values.astype(float)

cs_p1 = CubicSpline(yaw_data, p1_data)
cs_p2 = CubicSpline(yaw_data, p2_data)

def predict_power(yaw_angle):
    yaw = float(np.clip(yaw_angle, -30, 30))
    p1  = float(cs_p1(yaw))
    p2  = float(cs_p2(yaw))
    return p1, p2

if __name__ == "__main__":
    print("验证插值模型：")
    for angle in [-30, -15, 0, 12, 25, 30]:
        p1, p2 = predict_power(angle)
        print(f"  偏航={angle:+5.1f}°  P1={p1:.1f}kW  "
              f"P2={p2:.1f}kW  总={p1+p2:.1f}kW")
    print("✅ 代理模型就绪")