# round36 · 海岸真实化与远岸森林（以 coastal_3d_v2 为镜）

> 分支 `arena/01a074a4-dachuang-szls`，2026-09-06。
> 用户口径：场景已不错，但仍有优化细化空间；以 `docs/research/external/coastal_3d_v2`
> （PR #7 引入的友参考源码，**只借技法、不引代码**）为参考继续推进。
> 全程遵守既定审美红线：暗调冰青、低饱和莫兰迪、克制不惹眼、不引入新色相；
> 贴地真值源 `terrainSurfaceY` 零改动。

## 一、参考件拆解（coastal_3d_v2 有什么值得搬）

| 参考件技法 | 判断 | 本仓落地 |
|---|---|---|
| ocean.ts：真岸距驱动（浅水波幅阻尼 / 拍岸碎浪带 / swash 水线爬升） | ✅ 搬 | 岸距场 `shoreSigned` + aShore 消费链 |
| ocean.ts：背光浪尖透射（SSS）、双瓣太阳高光（锐+宽） | ✅ 搬（暗调降强版） | WorldTerrain FRAG |
| ocean.ts：远处波纹细节随距离衰减（防欠采样闪烁） | ✅ 搬 | `rippleFade` + 镜面指数随距离升高 |
| ocean.ts：far-ring 思路（真地平线，水面延伸出平面） | ✅ 改造 | 不加环形面：海面 2600→4420m 渐进全雾 + 天空下半球融雾，两侧同色消灭 9200m 平面切边 |
| sky.ts：程序卷云（虚拟平面投影 + 向阳 shading） | ✅ 搬（克制版） | 白昼薄卷云，覆盖低、夜间不可见 |
| vegetation.ts：实例化针叶树 + 坡度/雪线门 + 风摆 | ✅ 搬 | 新 `treeField.tsx`（自定义 shader，不进 PBR 链） |
| heightmap.ts：EDT 精确距离变换、thermal erosion | ❌ 不搬 | 改动 CPU 地形真值 = 破坏贴地契约，收益不成比例 |
| terrain.ts：MeshStandardMaterial + onBeforeCompile PBR | ❌ 不搬 | 本仓是自定义光照体系（全息线稿 + 程序地形），PBR 化是另一次大手术 |
| grass.ts：相机跟随草地域 | ⏸ 挂起 | grassField 保持不挂载（R32 决定）；相机常年在海上，草看不见 |

## 二、核心改动

### 1) 岸距场（`terrainUtil.ts` 新增 `shoreSigned`）
- `coastT` 是**陆侧**渐变（海侧恒 0），无法区分「远海」与「贴岸」——这正是近岸细节做不出来的根因。
- `shoreSigned(x,z)`：北/西岸 `dNorth/dWest` + 岛/海岬/海蚀柱极坐标轮廓的 **SDF 并集**（`max`），
  返回带符号最近岸距（负=海侧离岸米数、正=陆侧深入）。闭式解析、零采样。
- WorldTerrain 顶点新增 `aShore` attribute（夹取 [-700,120]），VERT/FRAG 共用。

### 2) 海面四件套（`WorldTerrain.tsx`，cache key → `terrain-ocean-v5-r36`）
- **浅水波幅阻尼**：涌浪振幅 `×(0.16 + 0.84·smoothstep(0,260,离岸距))` —— 岸线不再被大涌切出硬边；
- **swash 水线爬升**：贴岸 0~32m 水面 ±0.20m 正弦抬升（浪舌舔滩）；
- **拍岸碎浪带**：离岸 0~300m 周期性向岸推进的泡沫带（带间隔 ~114m、传播 24.5m/s、fbm 扰相位
  非机械平行线）；
- **背光浪尖透射 + 双瓣高光 + 防闪烁**：逆光浪尖微透青绿（≤0.4 强度、昼间门控）；
  锐瓣(620+)外加 56 次宽瓣柔晕；微法线细节 120→1500m 距离衰减 + 镜面指数随距离 +480。

### 3) 地平线收边（WorldTerrain + SkyAurora）
- 现象：9200m 平面边缘处海面仅吃 9% 雾、边缘外天空却是亮青辉光带 → 高机位下
  真地平线下方 ~5° 处出现「第二地平线」亮带（数值证据见 §四）。
- 修法：海面雾 `fogF·0.30` → 2600~4420m 渐进到 **全雾**；SkyAurora 新增 `uFogColor`
  （逐帧同场景雾色），下半球 `1-smoothstep(-0.07,0.02,h)` 融雾。两侧同色 → 切边不可见。
- 近场水色不变（2600m 内仍是轻雾保色口径）。

### 4) 白昼薄卷云（`SkyAurora.tsx`）
- 虚拟平面投影（`d.xz/(h+0.10)`）+ 双尺度 fbm + **向太阳采样 shading**（云有受光方向）；
- 覆盖率低（视觉 ~25%）、`×uDay·0.42` 昼间渐显、地平线 0.035~0.16 淡出（不糊极光带）、
  夜间不可见（不抢星野）。云际微暖反光 ≤0.25 强度（不引入新色相感）。

### 5) 远岸森林（新文件 `treeField.tsx`，App 挂载 `<TreeField/>`）
- round31 用户钦定「近海黄沙、**远海森林**」——此前林带只是地形平涂，没有立体天际线。
- 落位：`treeAccept`（terrainUtil 同一真值）：landMask≥0.30（越过沙岸潮带）、
  接受概率 `w.forest + 0.35·w.hill`（林带密/缓丘稀）、高度 < 雪线-40、坡度 ny≥0.62（峭壁不长）；
- 单株 31 三角（5 棱干 + 三层 7 棱锥），`InstancedBufferGeometry` 单批次画完；
- 顶点风摆（梢部 t²、世界相位 + 实例种子、慢阵风包络），风向与场景 `windAt` 同源；
- 着色与 WorldTerrain 陆地同口径：莫兰迪墨绿渐变、昼夜压暗 + 月光冷调、指数雾全吃；
- **画质分档**：high 4800 / medium 2400 / low 0（运行时只调 `instanceCount`，不重建程序）；
- **启动零代价**：4800 株拒绝采样 ≈1.6s CPU，改为首帧后延迟落位（round25 红线：
  不许顶住 Loading 屏）——开场运镜 34s 内无感长齐；low 档不采样。

### 6) 附带修复：`?q=` 画质锁此前不是锁（`PerfGovernor.tsx`）
- 现象：`?q=high` 只设初值，`qualityAuto` 仍真 → 软渲染 QA 下 ~2s 后仍被自动降档
  （本轮树木 low=0 直接受害，QA 截图差点拍了个寂寞）。
- 修法：锁档时 `setQuality(q, true)`（manual → `qualityAuto=false`），与 README「画质锁定」口径对齐。

## 三、涉及文件

| 文件 | 改动 |
|---|---|
| `twin/src/scene/terrainUtil.ts` | +`shoreSigned` / +`treeAccept` / +`treeSampleHits` / +`TREE_SPAN_M`（纯函数，地形真值零改动） |
| `twin/src/scene/WorldTerrain.tsx` | aShore 属性 + 浅水阻尼/swash/碎浪带/SSS/双瓣高光/防闪烁/远海收边 |
| `twin/src/scene/SkyAurora.tsx` | 白昼卷云 + uFogColor 下半球融雾 |
| `twin/src/scene/treeField.tsx` | **新建**：实例化远岸森林 |
| `twin/src/App.tsx` | 挂载 `<TreeField/>` |
| `twin/src/scene/PerfGovernor.tsx` | `?q=` 锁档语义修复 |
| `twin/scripts/selftest.mts` | +11 断言（岸距 3 / 森林 2 / 渲染口径锁 6），62→73 全过 |
| `twin/scripts/framestats.py` / `horizoncheck.py` / `perfstats.mjs` | 本轮数值化验证工具（无视觉也能举证） |

## 四、验证证据（无头截图 + 数值分析）

工程校验：`npm run build` 0 错误；`npm run lint` 0 警告 0 错误；`npm run selftest` **73/73**；
渲染探针 0 pageError。截图目录 `docs/research/shots/r36/`（before/after 四组机位，?t= 锁时）：

| 证据 | 数值 | 结论 |
|---|---|---|
| **性能**（perfstats 单帧计数） | 基线 249 calls / 487,918 tris → R36 250 calls / **636,718 tris** | 森林 = +1 draw call、+14.9 万三角（4800×31），单实例化批次；low 档 0 开销 |
| **地平线假缝**（horizoncheck 行剖面） | 海平线区最大行间台阶 \|ΔL\| **0.019 → 0.008**（-58%） | 「第二地平线」亮带根除，且未引入新台阶 |
| **森林可见性**（coast 机位 abdiff） | 显著变化像素 4.74%，底部 30% 带 36,742 px | 树影落在陆地剪影带上；前景带亮度 0.388→0.363（林带打破平涂） |
| **克制性**（framestats 全局） | day hero 全局均值 0.320→0.312；night 0.211→0.203；tint/sat 基本不变 | 无新色相、无过曝、无整片洗色 |
| **夜景生机**（night abdiff） | 中部海面显著变化（月路/涌动区），P50=60/255 低幅 | 夜海有变化但不闹 |
| 岸距正确性 | 9 机离岸 >400m（最浅 -831m@T01 方向）；岛心>0、岛外 1.5km<0 | SDF 并集方向/量纲正确（selftest 锁定） |

## 五、遗留 / 下一步建议

1. **草地仍不挂载**（R32 决定维持）：相机常年在海上，草不可见；若后续做「登岸漫游」机位，
   grassField 已就绪，接相机跟随域即可（参考件 grass.ts 的 region 跟随）。
2. **岛/海岬无树**：biomeWeights 里岛心 L≈1 判为「山地带」，树被拒。若想「岛上有林」，
   需给岛单独的植被例外（改 treeAccept 或岛 mask 降 L）。
3. **碎浪带与岸边浪的声画联动**：本轮只有视觉；后续可把 surfRoll 相位接到音频/HUD 浪高口径。
4. 参考件的 EDT 精确距离 / thermal erosion / PBR 地形：见 §一「不搬」理由，除非立项「地形 2.0」。
