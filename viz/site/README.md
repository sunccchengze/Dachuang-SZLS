# 风电场偏航优化可视化 · 静态站点

纯静态、零后端的偏航优化可视化演示系统（替代原 Streamlit 版本，Streamlit 根目录版本保留作本地工具），可直接部署到 Cloudflare Pages。

## 本地预览
```bash
python3 -m http.server 8000 --directory site
# 浏览器打开 http://localhost:8000
```

## 部署到 Cloudflare Pages
**方式 A（Dashboard，推荐）**

连接 GitHub 仓库 `sunccchengze/wind_farm_viz` 后：

| 字段 | 值 |
|---|---|
| 生产分支 | `arena/019fe42f-wind-farm-viz` |
| 框架预设 | None |
| 构建命令 | 留空 |
| 构建输出目录 | `site` |
| 根目录 | 留空 |
| 环境变量 | 无 |

**方式 B（CLI）**
```bash
npx wrangler pages deploy site --project-name wind-farm-viz
```

## 数据与构建
- `assets/data.js` 由 `build_data.py` 从仓库根的 CSV/JSON 导出（纯标准库，无需 numpy）
- `assets/data_3d.js` 由 `build_3d_data.py` 从 `fields/`、`fields_3d/` 导出（需 numpy/pandas）
- 重新导出：
  ```bash
  python3 site/build_data.py
  python3 site/build_3d_data.py        # 需要 numpy/pandas
  python3 site/render_assets.py        # 重新生成 POD/3D 等 PNG（需 matplotlib/numpy）
  ```
- 模型精度图来自队友交付的 `floris(1).zip` 与 `代理模型优化交付_20260808.zip`。

## 替换真实数据 / 真实模型（界面零改动）

数据契约见根 `README.md`。替换步骤：

1. **更新源数据**：用真实数据覆盖仓库根的 `cases*.csv`、`fields*/`、`optimizer_result.json`、`array_independent_result.json`（保持字段、单位、数组形状不变）。
2. **重新导出前端数据**：运行上面的 `build_data.py` / `build_3d_data.py`。
3. **替换代理模型**（可选）：只改 `assets/js/interp.js` 中 `predict_power` / `find_yaw_for_target` 的函数体，保持返回字段兼容：
   - `predict_power(yaw, U)` 返回 `{p1, p2, ptot, outOfRange, reasons}`
   - `find_yaw_for_target(target, U)` 返回 `{yaw, ptot, error, base, outOfRange, reasons}`
4. **更新数据状态条**：改 `assets/js/data-source.js` 顶部 `CONFIG`（`maturity` 改为 `"provisional"`/`"validated"`，更新来源说明）；已验证正式发布时可设 `hidden: true` 关闭状态条。
5. **契约自检（必跑）**：
   ```bash
   python3 site/check_contract.py
   ```
   校验 data.js/data_3d.js 的字段、形状、功率非负、`ptot≈p1+p2`、增益公式一致性。退出码非 0 时先修正再部署。

> 所有页面顶部有统一"数据状态条"，明确标注当前是 FLORIS 模拟占位、代理模型类型，避免答辩时被误认为实测数据；超出可信域（风速 6–12 m/s、偏航 ±30°）会显示外推提示。

## 接口契约
- `predict_power(yaw_angle, U_inf) -> {p1,p2,ptot}` kW —— 见 `assets/js/interp.js`
- `find_yaw_for_target(target_power, U_inf) -> {yaw,ptot,error,base}`

当前为 FLORIS 工程尾流模型占位；待袁夫达（NN 代理）/厉今飞（基线）/洪祖名（优化）提供真实结果后，按上述步骤替换即可。
