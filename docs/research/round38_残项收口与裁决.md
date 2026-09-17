# round38 · 残项收口与孤儿分支裁决

> 分支 `arena/01a099f2-dachuang-szls`（自 `bd5f5e8` R37 起），2026-09-13。
> 用户口径：把「还没优化的残项」自行排序、拆成子任务、逐个做完，每完成一项 push 一次；
> 孤儿分支 `arena/01a074a3-dachuang-szls` 由我判断是否是好版本；不确定的自己裁决，按呈现效果最佳执行。
> 本轮全程遵守既定红线：暗调冰青 / 低饱和莫兰迪 / 克制不惹眼 / 不引入新色相 /
> 贴地真值 `terrainSurfaceY` 零改动 / 不虚构数据（数字必须来自实测，否则标【代理/示意】）。

---

## 〇、基线复测（2026-09-13，本沙箱 2 核 + SwiftShader）

| 指标 | 实测 | 说明 |
|---|---|---|
| `npm run selftest` | **84 通过 / 0 失败** | 与 R37 提交信息一致，无回归 |
| `npx tsc -b --noEmit` | **0 错误** | |
| `npm run lint` | **0 warnings / 0 errors**（52 files） | |
| `npm run build` | **✓ 1.36s** | three 单包 1,278 kB（gzip 384）· 业务 150 kB（gzip 58）· floris3d 130 kB（gzip 26）· CSS 385 kB（gzip 162） |
| `?q=high` 单帧 | **250 calls / 636,718 tris / 47,384 lines / 105 geoms / 36 tex** | `window.__aeolus_stats()`，与 R36 文档记录完全一致 |
| `?q=medium` | 250 calls / 562,318 tris | = 基线 487,918 + 2400 株×31 三角 |
| `?q=low` | 222 calls / 417,538 tris | 树 0 株（487,918 − 70,380 后期/粒子等） |
| 帧时长 median / p90 / max | high 104 / 2535 / 5114 ms · medium 79 / 4831 / 4901 · low 100 / 4133 / 4784 | **软渲染，绝对值无意义**；但 p90 尖峰见 §三-T3b（首帧后长停顿） |

> 新增 `twin/scripts/perftier.mjs`（`npm run perftier`）：三档同参同机位（`?q=…&cam=60,22,990&t=15`）
> 一次跑完，计数为确定值、帧时长只作档间比较。此前各轮只有 `perfstats.mjs` 单档计数，**没有跨档回归口径**。

## 一、孤儿分支 `arena/01a074a3-dachuang-szls` 裁决

**它是 1 ahead / 4 behind main 的单 commit `595daf2`**（R36 同期开工的另一版海面/天空细化），
权威记录只在它自己的 `docs/11_R36_场景细化_海洋天空v2借鉴.md`（main 上没有 docs/11）。

**判定：不是"改烂被丢"，是"与主线并行开工、被主线击败后没人收口"。** 依据：
1. 自测口径齐全且绿：selftest 66/66、tsc 0 错、oxlint 0/0、build ✓；
2. 带**量化过曝守卫**（hero 海面 mean 97.1→98.1、P99.9 254 持平；天空 max 244→239）——红线意识在线；
3. `docs/11` §一有一张 12 条能力取舍表，7 取 5 不取，**每条"不取"都给了理由**（毛细波在 23m 网格必混叠、
   双 mesh 会在 2400m 边界 Z-fighting、EDT 收益不成立…），方法论比主线 R36 文档更严谨；
4. 死因是结构性的：它的 parent 是 R36 之前的 main，**没有 treeField / R36b 月落 / R36c 夜陆 / R37 色温**；
   且证据图写进 `twin/docs/research/shots/r36/`（主线口径是 `docs/research/shots/`），
   `coastSignedDist` 与主线 `shoreSigned` 是同一件事的两套实现 → 直接 merge 必冲突。

**逐项裁决（决策权已移交，此处落章）**

| 它的改动 | 裁决 | 理由（读了代码，非读 commit message） |
|---|---|---|
| FRAG `waveHeight` 与 VERT 波系**同方向同相位** | ✅ **采纳（改法不照抄）** | 见 §二：`WorldTerrain.tsx:149` 的 `waveHeight` 是 5 条独立正弦 + fbm，与 `:92-93` 的两条 Gerstner（k=2π/2400、2π/1500，c=√(9.8/k)）**毫无关系** → 泡沫/浪脊/高光骑在另一套波上，几何浪峰与着色浪峰错位。这是真缺陷。 |
| `seaSky` 真天空反射替代平涂 `skyRef` | ✅ **采纳（须改写）** | `:230` 的 `skyRef = mix(0.014,0.032,0.054 → 0.150,0.290,0.385, uDayF)` 是**与视角无关的两色平涂**：海面反射的是一个不存在于天空中的颜色。它那份色板是 R37 之前的硬编码，必须改成消费 `skyState.warmF`/`uFogColor` 同源，否则正午海面反白光、日出海面不金山。 |
| 云画在星空/极光之后、日月画在云之后 | ⚠️ **部分成立** | 实测 `SkyAurora.tsx`：日轮在 `:152`（云 `:171` **之前**）、月盘在 `:180`（云**之后**）→ 现状是"云掩日、不掩月"，不一致。修法是**统一在云之后画日月**（云可遮日）而非它写的"日月都穿云"。 |
| 波群 2→5 波（2400/1500/620/380/240m）+ 场心收敛 0.5→0.25 | ❌ **否决（并入 §三-T5 专项）** | 它动的正是 R36c/R37 反复用"海面带零回归"守住的**已验收浪形基线**；且 240m 波在 23m 网格上仅 ~10 采样/波长，接近 Nyquist，软渲染下必出走样。它指出的「±16.8m 涌浪压在塔基」我复核为**真问题**（0.06·2400/2π + 0.045·1500/2π = 22.9+10.7 = 33.6m × 场心 amp 0.5 ≈ ±16.8m，与它给的数字逐位吻合），但该正面立项重标定浪形，而不是搭本轮顺风车。 |
| `coastSignedDist` 闭式岸距 | ❌ **否决** | 主线 `shoreSigned` 是北/西岸 + 岛/海岬/海蚀柱的 **SDF 并集**；它这份只算两条岸、显式声明"离岸岛不在此场"，严格劣于。 |
| 浅水冰青着色（岸外 80m） | 🔶 **试做后定** | R34「深度三色」意图确实在重构中被吃掉；值得一次 A/B，但不得违反"不引入新色相"。 |

## 二、T4 · 波系同源（进行中）

（本节在实现后回填实测数字与 A/B 证据。）

## 三、残项清单与状态

| # | 任务 | 状态 |
|---|---|---|
| T1 | 门面文档回填：`README.md` / `twin/README.md` / `HANDOFF.md` / `HANDOFF_NEXT.md` 的过期数字与口径 | ✅ **本轮完成**（见 §四） |
| T1b | 三档画质基线探针 `npm run perftier`（跨档回归口径此前不存在） | ✅ 随 T1 入库 |
| T2 | 仓库卫生：16 个 0 字节假证据 PNG 出库、证据树合并、根目录 zip 出库、`.gitignore` 补 | ✅ **本轮完成**（见 §五） |
| T3 | CI 化：`.github/workflows/qa.yml`（tsc+lint+selftest+build）兑现 docs/08「全部进 CI 可跑」 | ✅ **本轮完成**（见 §六） |
| T3b | 首帧后长尖峰：`treeField` 延迟落位 4800 株一次性拒绝采样（p90 尖峰 2.5–5.1 s 的来源）→ 分帧预算摊销 | ⬜ |
| T4 | 采纳孤儿分支的三项技法（波系同源 / 真天空反射 / 云掩日月次序） | ⬜ |
| T5 | 浪形重标定专项：塔基 ±16.8m 涌浪是否合理（场心 amp），独立 A/B 后裁决 | ⬜ |
| T6 | low 档远岸森林整片消失（4800/2400/**0**）→ 改为可看的低密度档 | ⬜ |
| T7 | 岛/海岬无树（`treeAccept` 把岛心判山地带）→ 给岛植被例外 | ⬜ |
| T8 | `grassField` 挂账 6 轮（R32 起）→ 裁决：相机跟随草地域，仅陆侧机位激活 | ⬜ |
| T9 | 碎浪带 → HUD 浪高/音频同源（标【代理】，不伪装实测） | ⬜ |
| T10 | 性能与上线账：三档帧率基线入库 + Pages 首屏实测替换 08-24 PoC 数字 | ⬜ |
| T11 | `docs/07`/`docs/08` 状态回填 + Round-9 的 `STALE-PENDING-RESHOOT` 欠账销账 | ⬜ |

## 四、T1 · 门面文档回填（完成）

**问题**：四份门面文档全部停在 2026-08-28~08-30 的 v3 交付轮，与本仓现状不符——撞项目"不虚构"红线。

| 文档 | 过期处 | 修法 |
|---|---|---|
| `README.md` | 「selftest 22/22、35 draw calls」；docs 索引缺 09/10 与 round*.md | 换成实测表（84/0、250 calls / 636,718 tris、三档计数、产物体积）+ 补索引；08-24 选型 PoC 一节显式标注"不要与当前状态混读" |
| `twin/README.md` | 「22 断言」「实测 35 draw calls」；scripts 清单漏了 R36/R37 期间新增的 6 个探针；已知边界无 R36–R38 | 数字换实测、补 `perftier`、scripts 清单补全、已知边界加"帧率禁用沙箱值"警示并指向本轮文档 |
| `HANDOFF.md` | 抬头写 round25；仓库名 `0824-2026`；lint 23 warnings；**手搓编译 NSS 30 分钟配方**；「调试参数记得最终清掉」；`B7 间距≈3.5D`、`18 站位` | 顶部加"历史交接"声明 + 过期数字速查；§3 换成 `bootstrap.sh`（桩库 2 秒）+ 现行调试键；§4 表前加"现状要点列是当时缺陷清单、已收口"警告并补 R29–R37 新增文件 |
| `HANDOFF_NEXT.md` | 整篇是 08-28 的 P0/P1 待办快照（含"不能声称视觉验收通过""无 LOD/无基线/运镜不可跳"），其中大半已解决 | 重写为**当前**交接：现状 / 已验证 / 开放项（= §三 表）/ 红线 / 一句话口径 |

**验证**：本任务只动 markdown 与 package.json 脚本注册项 → `npm run lint` 0/0、`npx tsc -b --noEmit` 0 错误、
`npm run selftest` 84/84、`npm run build` ✓（表内数字即本任务实测来源）。

## 五、T2 · 仓库卫生 + 证据链守卫（完成）

**做的四件事**

1. **删假证据**：`twin/shots/` 16 个 PNG 全部 0 字节且 md5 彼此相同——它们挂着 `stepA10_hero / stepA10_peak`
   这类"分步对拍"的名字，实际是一次崩溃的无头截图残留。已出库 + `twin/shots/` 进 `.gitignore`。
2. **证据树合一**：`twin/docs/research/**`（R30–R34，21 文件）`git mv` 进 `docs/research/`，
   `twin/docs/` 目录消失；5 处引用同步改写（docs/10、round31、学习笔记、terrainUtil 头注、提示词自引）。
   合并前先验证**无同名冲突、无内容重复**（`md5` 全树比对：唯一重复就是上面那 16 个空壳）。
3. **删冗余 zip**：根目录 `hyper-realistic-3d-coastal-landscape.zip`（180 kB）——与
   `docs/research/external/coastal_3d_v2/` 逐条目比对，zip 独有的 4 项只是空目录条目，即 100% 冗余；
   新增 `external/README.md` 写清来源、比对结论与"只借技法不引代码"的许可口径。
4. **docs/10 §七「未收口事项」7 条逐条销账**（这张表从 R32 起就一直挂着）：

| 当时列的事项 | 本轮核对结论 |
|---|---|
| 17 张 r33 截图无 README | 已补 `shots/r33/README.md`；实际现存 4 张，"17 张"对今天的树已过期 |
| `r32/` 3 张图无 README | 已补 `shots/r32/README.md`（+ `r34/`，同批） |
| `r32_hero_1920.png` 是否与 `r32/r32_hero.png` 重复 | **不重复**：同 1920×1080，md5 不同（`2311f325…` / `0515dc07…`）→ 两份都保留 |
| `grassField.tsx` 37 行红方块 debug | 现为 195 行正式组件、无红方块；**仍未挂载** → 转 §三-T8 处理 |
| `r33_verify.py / r33_verify2.py` 保留还是废弃 | 两文件已不在库内，视为已废弃 |
| 参考 zip 未完整入库 | zip 与 `external/coastal_3d_v2/` 等价 → zip 出库，来源改记 `external/README.md` |
| 叶片投影（R33 修过）与 R31 移交说明 | 现存 `HoloTurbine.tsx:407 ENABLE_BLADE_SHADOW=false` + `shadow_blade_verdict.md`，与用户裁决一致 |

**证据链守卫（+2 断言，84→86）**：`selftest` 现在会 ①拒绝证据树里的 0 字节图片；
②逐个检查 `docs/**/*.md` 引用的图片名是否存在（通配符/`<占位符>`/命令行行不查）。
守卫**第一轮就抓出 16 处真实断链**，全部定性修完：

- `docs/09` 承诺回填 `r34_ocean_hero_1920 / _coast / _night`——前两张其实以 `shots/r34/r34_hero.png`、
  `r34_coast.png` 入库（改名未回写文档），**夜场那张从未拍过**。已在 docs/09 顶部就地校正，
  并注明"不要拿今天的代码造一张 R34 夜景充证据"，夜间口径改指 R36c 的 `r36/nightland/`。
- `round29` 证据表写的是迭代临时名（`ocean_day_v6` 等）→ 改为实际入库名（`r29_ocean_day_hero.png` 等），
  并注明"文件名口径"。
- `docs/08` 把三张方位图并成一格（east / west / north 用斜杠连写）、round11 把 sunset 与 noon 连写——
  这种速记机器不可查，已分别写全为真实文件名。
- `sky-realistic-cyan.png`（Round-9 按裁决删除的 1.9 MB 无许可位图）进守卫的 `GONE` 例外表，
  注释明确"不许为通过检查往里塞"。

**验证**：`npm run selftest` **86/86** · `npm run lint` 0/0 · `npx tsc -b --noEmit` 0 错 · `npm run build` ✓。
本任务只动 markdown/图片/gitignore/selftest 守卫，未触碰任何 `src/` 渲染代码（`terrainUtil.ts` 仅改注释里的文档路径）。

## 六、T3 · QA 门槛自动化（完成，但**启用需要人点一下头**）

**先说一个硬事实**：本仓连接的 GitHub App 没有 `workflows` 权限，任何写 `.github/workflows/*` 的推送
都被远端拒绝（`refusing to allow a GitHub App to create or update workflow … without 'workflows' permission`）。
我没有绕开权限（也不该绕）。所以 T3 交付的是**可一键启用的成品**，而不是"CI 已绿"这种说不清的话：

- `ci/qa-gates.yml`：`tsc -b --noEmit` → `oxlint`(0/0) → `selftest`(86，含 R38 两项证据链守卫) → `vite build`；
  Node 22（selftest 靠原生类型剥离）、`npm ci` + lockfile 缓存、触发 push/PR→main + 手动；
  附一条**非阻断**哨兵（>3 MB 入库图片/压缩包清单 + 证据树 0 字节图计数）。
- 启用只需：`mkdir -p .github/workflows && git mv ci/qa-gates.yml .github/workflows/qa-gates.yml && git push`
  （文件头注释里写了这三行，含"为什么先放在 ci/"的说明）。
- `npm run verify`（twin）：`lint && selftest && build`，**本地与 CI 同一口径**，不依赖任何权限，今天就能用。
- 明确不进 CI：`shot.mjs` / `perftier` 的帧时长（SwiftShader 在 runner 上不可比），按 `shots/README.md` 的 SOP 做。
- 顺带把 `docs/08` §四 E7 里「全部进 CI 可跑」这句**标注为不实宣称并校正**——原文不删，只加【R38 校正】，
  保留审计痕迹（本项目一贯做法）。

**验证**：YAML 解析通过（1 job / 8 steps）；四条命令本地预跑全绿（lint 0/0 · selftest 86/86 · tsc 0 错 · build ✓）；
`find ../docs -type f -size 0` 在 `working-directory: twin` 下路径成立（已实测）。
守卫自身在 T3 期间还拦下过一次：我在本文里引用旧速记写法时被它判为断链——**误报也照改**，
因为"文档里出现的每个 .png 名字都必须存在"这条规矩一旦能打折就守不住。

