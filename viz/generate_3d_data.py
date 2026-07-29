from floris import FlorisModel
from pathlib import Path
from scipy.interpolate import griddata
import floris
import numpy as np
import os

print("=" * 40)
print("开始生成三维流场数据")
print("=" * 40)

# 初始化FLORIS
floris_dir = Path(floris.__file__).parent
config_path = floris_dir / "default_inputs.yaml"
fmodel = FlorisModel(str(config_path))

fmodel.set(
    layout_x=[0.0, 630.0],
    layout_y=[0.0, 0.0],
    wind_directions=[270.0],
    wind_speeds=[8.0],
    turbulence_intensities=[0.06],
)

# 要计算的高度层（20m到180m，共9层）
heights = np.linspace(20, 180, 9)
print(f"计算高度层：{heights} m")

# 要计算的偏航角
yaw_angles = [-30, -15, 0, 15, 30]
print(f"计算偏航角：{yaw_angles} °")

os.makedirs("fields_3d", exist_ok=True)

for yaw in yaw_angles:
    print(f"\n偏航角 = {yaw:+.0f}°")
    fmodel.set(yaw_angles=np.array([[float(yaw), 0.0]]))
    fmodel.run()

    # 用于存储所有高度层的数据
    U_3d = []

    for h in heights:
        plane = fmodel.calculate_horizontal_plane(
            height=float(h),
            x_resolution=64,
            y_resolution=32,
            x_bounds=(-200, 900),
            y_bounds=(-300, 300),
        )

        x_vals = plane.df["x1"].values
        y_vals = plane.df["x2"].values
        u_vals = plane.df["u"].values

        x_unique = np.unique(x_vals)
        y_unique = np.unique(y_vals)
        X_grid, Y_grid = np.meshgrid(x_unique, y_unique)

        U_grid = griddata(
            points=(x_vals, y_vals),
            values=u_vals,
            xi=(X_grid, Y_grid),
            method="linear"
        )

        # 修复NaN
        nan_mask = np.isnan(U_grid)
        if nan_mask.any():
            U_nearest = griddata(
                points=(x_vals, y_vals),
                values=u_vals,
                xi=(X_grid, Y_grid),
                method="nearest"
            )
            U_grid[nan_mask] = U_nearest[nan_mask]

        U_3d.append(U_grid)
        print(f"  高度 {h:.0f}m 完成")

    # 叠成三维数组：shape = (n_heights, n_y, n_x)
    U_3d = np.array(U_3d)

    # 保存
    filename = f"fields_3d/yaw_{yaw:+03d}.npz"
    np.savez(
        filename,
        x=x_unique,
        y=y_unique,
        z=heights,
        u=U_3d
    )
    print(f"  已保存：{filename}  形状：{U_3d.shape}")

print("\n✅ 全部三维数据生成完毕")
print("文件结构：")
print("fields_3d/")
for yaw in yaw_angles:
    print(f"  yaw_{yaw:+03d}.npz")