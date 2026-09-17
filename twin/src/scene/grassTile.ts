// ================================================================
// P1 · T8 草地系统 · 分块落位模型（纯函数层，无 three 依赖）
// ----------------------------------------------------------------
// 为什么不能像原实现那样「一次性 6 万株全场铺开」：
//   ① 构建期：6 万株拒绝采样 = 数十万次 landMask/terrainSurfaceY 求值，
//      实测与 treeField 旧版同一量级（首帧后 2.5~5.1s 长尖峰，round38 开放项 4）；
//   ② 运行期：全场 6 万 blade × 8 顶点 = 48 万顶点常驻，且 frustumCulled=false
//      → 相机在海上特写风机时，2km 外内陆的草也在被顶点着色器算（纯浪费）。
// 本模型的两条裁决：
//   · 【空间分块】把采样域切成 GRASS_TILE_M 的瓦片，只对「相机视距环内」的
//     瓦片建数据、上屏；瓦片进出视距即回收槽位（池化，不重建几何/程序）；
//   · 【重要性采样】不再全域盲投，而是先在瓦片内 4×4 子格上求 biome 权重
//     （biomeWeights 与 landMask 同源：草带 0.14<L<0.62、林带 0.38<L<0.82），
//     再按权重配额落株 —— 分布与旧的「均匀投 + 权重接受」同一期望密度，
//     但求值次数从「几十万次盲投」降到「每瓦片 16 次权重 + 每株 1 次贴地高度」。
//
// 同源红线：只消费 terrainUtil 的 biomeWeights / terrainSurfaceY / mulberry32，
// 不新增任何地形真值；selftest R40 断言「海洋瓦片零株、草带/林带密度比与
// biome 权重一致、同种子同落位（可复现）」。
// ================================================================

import { biomeWeights, terrainSurfaceY, mulberry32, TREE_SPAN_M } from '../scene/terrainUtil.ts'

/** 采样域半边长（与草地/森林同一域，m） */
export const GRASS_SPAN_M = TREE_SPAN_M // 4550
/** 瓦片边长（m）：512 → 全域 18×18 = 324 瓦片，视距环内约 25~49 瓦片 */
export const GRASS_TILE_M = 512
/** 每瓦片 4×4 子格（128m）：权重求解与配额分配的粒度 */
export const GRASS_SUBCELLS = 4
/** 全域【满密度】目标株数（草原带 + 林下）：按陆地 biome 权重摊到瓦片。
 *  运行时按「相机到瓦片距离」截断 instanceCount 画其中一部分（见 drawnFrac）——
 *  近处满密度成片、远处稀疏剪影，而瓦片数据只建一次（截断不触发重建）。 */
export const GRASS_TARGET_TOTAL = 46000
/** 单瓦片株数上限（池槽容量按它开数组；密度最高的草带瓦片不被截断） */
export const GRASS_TILE_CAP = 3600
/** 一丛草的株数：落位以「丛」为单位聚簇（单株全域撒 = 稀疏尖刺感，R32 挂账的根因） */
export const GRASS_BLADES_PER_CLUMP = 10
/** 丛半径（m）：丛内高斯散布，丛间留裸地 —— 真实草甸就是斑块状的 */
export const GRASS_CLUMP_R = 1.6

/**
 * 丛级贴地平面（菱形五点插值）。
 * terrainSurfaceY 是全场最贵的纯函数（~13µs/次）：逐株调用 = 48ms/瓦片尖峰。
 * 五点（中心 + 四向 q 米）在丛尺度（≤3m）上把地形当双线性曲面，
 * 连「北/西双岸 ramp 的 max() 折痕」这类梯度不连续处也能压到 ≤0.35m
 * （selftest R40 断言；单点前向差分平面在折痕上实测 0.97m，弃用）。
 */
export interface ClumpPlane { y0: number; ya: number; yb: number; yc: number; yd: number; q: number }
export function clumpPlane(x: number, z: number, q = 2.0): ClumpPlane {
  return {
    y0: terrainSurfaceY(x, z),
    ya: terrainSurfaceY(x + q, z),
    yb: terrainSurfaceY(x - q, z),
    yc: terrainSurfaceY(x, z + q),
    yd: terrainSurfaceY(x, z - q),
    q,
  }
}
/**
 * 丛内高度：按象限取轴向坡度做双线性外推（gx/gz 各自带符号乘本象限坡度）。
 * 平面地形上精确；max() 折痕这类梯度不连续处按「丛心所在象限」取侧，
 * 误差被丛半径（≤3.2m）界住（selftest R40 断言 ≤0.35m）。
 */
export function planeY(p: ClumpPlane, gx: number, gz: number): number {
  const sx = gx >= 0 ? (p.ya - p.y0) / p.q : (p.y0 - p.yb) / p.q
  const sz = gz >= 0 ? (p.yc - p.y0) / p.q : (p.y0 - p.yd) / p.q
  return p.y0 + gx * sx + gz * sz
}

/**
 * 丛心二阶差分（曲率代理）：五点采样白送，不新增求值。
 * 陡坡上的山脊/沟谷折痕（实测 ~70° 坡 + 米级折痕）五点平面压不住，
 * 曲率超阈的丛退回逐株真值贴地（粗糙丛占少数，构建预算仍受控）。
 */
export function planeCurvature(p: ClumpPlane): number {
  return Math.max(Math.abs(p.ya + p.yb - 2 * p.y0), Math.abs(p.yc + p.yd - 2 * p.y0))
}
/** 曲率阈值（m / q²）：>0.12 视为「折痕丛」，逐株求真值 */
export const PLANE_ROUGH_THRESH = 0.12

export const GRASS_TILES_PER_SIDE = Math.ceil((GRASS_SPAN_M * 2) / GRASS_TILE_M)
export const GRASS_TILE_COUNT = GRASS_TILES_PER_SIDE * GRASS_TILES_PER_SIDE

/** 两种草：0 = 草原带 blade（高、干黄/湿绿对比强），1 = 林下 blade（矮、偏暗） */
export type GrassKind = 0 | 1

export interface GrassTileIndex {
  ti: number
  /** 瓦片中心（世界坐标） */
  cx: number
  cz: number
  ix: number
  iz: number
}

export function tileIndexAt(ix: number, iz: number): number {
  return iz * GRASS_TILES_PER_SIDE + ix
}

export function tileFromIndex(ti: number): GrassTileIndex {
  const ix = ti % GRASS_TILES_PER_SIDE
  const iz = Math.floor(ti / GRASS_TILES_PER_SIDE)
  const cx = -GRASS_SPAN_M + (ix + 0.5) * GRASS_TILE_M
  const cz = -GRASS_SPAN_M + (iz + 0.5) * GRASS_TILE_M
  return { ti, cx, cz, ix, iz }
}

/** 世界坐标 → 瓦片下标（域外返回 -1） */
export function tileAt(x: number, z: number): number {
  const ix = Math.floor((x + GRASS_SPAN_M) / GRASS_TILE_M)
  const iz = Math.floor((z + GRASS_SPAN_M) / GRASS_TILE_M)
  if (ix < 0 || iz < 0 || ix >= GRASS_TILES_PER_SIDE || iz >= GRASS_TILES_PER_SIDE) return -1
  return tileIndexAt(ix, iz)
}

/** 瓦片内 4×4 子格的 biome 权重（草原带 / 林下）—— 构建期的唯一「地面采样」 */
export function tileSubcellWeights(ti: number): { grass: number[]; forest: number[] } {
  const { cx, cz } = tileFromIndex(ti)
  const half = GRASS_TILE_M / 2
  const step = GRASS_TILE_M / GRASS_SUBCELLS
  const grass: number[] = []
  const forest: number[] = []
  for (let j = 0; j < GRASS_SUBCELLS; j++) {
    for (let i = 0; i < GRASS_SUBCELLS; i++) {
      const x = cx - half + (i + 0.5) * step
      const z = cz - half + (j + 0.5) * step
      // 陆地上 biomeWeights 内部已做 landMask 分带（海面返回全零）
      const w = biomeWeights(x, z)
      grass.push(w.grass)
      forest.push(w.forest)
    }
  }
  return { grass, forest }
}

/** 陆地占比（按 128m 子格权重求和估算）：把全域目标株数摊到每瓦片 */
let landAreaCache: { sum: number; tiles: number[] } | null = null
export function grassLandStats(): { sum: number; tiles: number[] } {
  if (landAreaCache) return landAreaCache
  let sum = 0
  const tiles: number[] = new Array(GRASS_TILE_COUNT).fill(0)
  for (let ti = 0; ti < GRASS_TILE_COUNT; ti++) {
    const w = tileSubcellWeights(ti)
    let t = 0
    for (let k = 0; k < w.grass.length; k++) t += w.grass[k] + w.forest[k]
    tiles[ti] = t
    sum += t
  }
  landAreaCache = { sum, tiles }
  return landAreaCache
}

/** 每瓦片目标株数（全域 36000 按 biome 权重摊派；纯海瓦片 = 0，一次地形求值都不做） */
export function bladesPerTile(ti: number): number {
  const { sum, tiles } = grassLandStats()
  if (sum <= 0) return 0
  const raw = (GRASS_TARGET_TOTAL * tiles[ti]) / sum
  return Math.min(GRASS_TILE_CAP, Math.round(raw))
}

export interface Blade {
  x: number
  y: number
  z: number
  /** 株高缩放（m） */
  s: number
  /** 摆动相位 */
  phase: number
  /** 朝向角 */
  ang: number
  kind: GrassKind
}

/**
 * 单瓦片落株（确定性：同 ti 同 seed 永远同一批草）。
 * 配额 = 子格权重占比 × 瓦片目标株数；株位在子格内均匀随机 → 无格子感也无空带。
 */
export function buildTileBlades(
  ti: number,
  target: number,
  seed = 0x6a3f,
  kindScale: { grass?: number; forest?: number } = {},
): Blade[] {
  if (target <= 0) return []
  const { cx, cz } = tileFromIndex(ti)
  const half = GRASS_TILE_M / 2
  const step = GRASS_TILE_M / GRASS_SUBCELLS
  const w = tileSubcellWeights(ti)
  const kg = kindScale.grass ?? 1
  const kf = kindScale.forest ?? 1
  let total = 0
  for (let k = 0; k < w.grass.length; k++) total += w.grass[k] * kg + w.forest[k] * kf
  if (total <= 1e-9) return []

  const rnd = mulberry32((seed ^ (ti * 2654435761)) >>> 0)
  const out: Blade[] = []
  // 余数分配：先按比例取整，再把剩余名额按小数部分从大到小补齐（不丢株、不超发）
  const quota: number[] = []
  let assigned = 0
  const frac: Array<{ k: number; f: number }> = []
  for (let k = 0; k < w.grass.length; k++) {
    const wk = w.grass[k] * kg + w.forest[k] * kf
    const q = (target * wk) / total
    const qi = Math.floor(q)
    quota.push(qi)
    assigned += qi
    frac.push({ k, f: q - qi })
  }
  frac.sort((a, b) => b.f - a.f)
  for (let i = 0; i < target - assigned && i < frac.length; i++) quota[frac[i].k]++

  for (let k = 0; k < quota.length; k++) {
    const n = quota[k]
    if (n <= 0) continue
    const ix = k % GRASS_SUBCELLS
    const iz = Math.floor(k / GRASS_SUBCELLS)
    const x0 = cx - half + ix * step
    const z0 = cz - half + iz * step
    // 草原带占该子格配额的比重（其余为林下矮草）
    const wk = w.grass[k] * kg + w.forest[k] * kf
    const grassShare = wk > 0 ? (w.grass[k] * kg) / wk : 0
    // —— 聚簇落位：先撒「丛心」，再在丛半径内高斯散布单株 ——
    // 单株全域均匀撒 = 每 200+m² 一根尖刺（R32 版看起来像稀疏杂草的原因）；
    // 丛内 10 株 / 半径 ~2m = 局部密度 ~0.8 株/m²，中距离即可读成草甸斑块。
    let placed = 0
    while (placed < n) {
      const clumpX = x0 + rnd() * step
      const clumpZ = z0 + rnd() * step
      const clumpKind: GrassKind = rnd() < grassShare ? 0 : 1
      const clumpN = Math.min(GRASS_BLADES_PER_CLUMP, n - placed)
      const clumpScale = 0.8 + rnd() * 0.5 // 丛与丛之间的高矮差（斑块感）
      // 丛级贴地平面（5 次真值求值/丛 = 0.5 次/株）：见 clumpPlane 注释
      const plane = clumpPlane(clumpX, clumpZ)
      const rough = planeCurvature(plane) > PLANE_ROUGH_THRESH
      for (let b = 0; b < clumpN; b++) {
        // 高斯近似：两个均匀量之和（Box-Muller 的便宜替代，确定性不受影响）
        const gx = (rnd() + rnd() - 1) * GRASS_CLUMP_R
        const gz = (rnd() + rnd() - 1) * GRASS_CLUMP_R
        const x = clumpX + gx
        const z = clumpZ + gz
        const edge = 1 - Math.min(1, Math.hypot(gx, gz) / (GRASS_CLUMP_R * 1.6))
        const s =
          (clumpKind === 0 ? 0.9 + rnd() * 0.9 : 0.55 + rnd() * 0.6) *
          clumpScale * (0.75 + 0.35 * edge) // 丛心略高、丛缘略矮
        out.push({
          x,
          // 根部微埋 0.15m，避免悬空（与原实现同口径）；折痕丛逐株真值
          y: (rough ? terrainSurfaceY(x, z) : planeY(plane, gx, gz)) - 0.15,
          z,
          s,
          phase: rnd() * Math.PI * 2,
          ang: rnd() * Math.PI,
          kind: clumpKind,
        })
        placed++
      }
    }
  }
  return out
}

/**
 * 运行时密度截断：相机到瓦片距离 → 画满密度瓦片的百分之几。
 * 单调不增（selftest R40 断言）；截断走 instanceCount，不重建瓦片数据。
 */
export function drawnFrac(dist: number): number {
  if (dist < 320) return 1
  if (dist < 760) return 0.5
  if (dist < 1300) return 0.26
  return 0.14
}

/** 视距裁决：相机周围半径内的瓦片，按距离升序（近的先建、先上屏） */
export function tilesInView(
  camX: number,
  camZ: number,
  radius: number,
  out: number[] = [],
): number[] {
  out.length = 0
  const r = Math.max(0, radius)
  const ix0 = Math.max(0, Math.floor((camX - r + GRASS_SPAN_M) / GRASS_TILE_M))
  const ix1 = Math.min(GRASS_TILES_PER_SIDE - 1, Math.floor((camX + r + GRASS_SPAN_M) / GRASS_TILE_M))
  const iz0 = Math.max(0, Math.floor((camZ - r + GRASS_SPAN_M) / GRASS_TILE_M))
  const iz1 = Math.min(GRASS_TILES_PER_SIDE - 1, Math.floor((camZ + r + GRASS_SPAN_M) / GRASS_TILE_M))
  const cand: Array<{ ti: number; d: number }> = []
  for (let iz = iz0; iz <= iz1; iz++) {
    for (let ix = ix0; ix <= ix1; ix++) {
      const ti = tileIndexAt(ix, iz)
      // 纯海瓦片直接跳过（连距离排序都不进）—— 海域占本场景大部分面积
      if (bladesPerTile(ti) <= 0) continue
      const t = tileFromIndex(ti)
      // 瓦片是方形，用「相机到瓦片 AABB 的最近距离」排序（不是中心距）
      const dx = Math.max(Math.abs(camX - t.cx) - GRASS_TILE_M / 2, 0)
      const dz = Math.max(Math.abs(camZ - t.cz) - GRASS_TILE_M / 2, 0)
      cand.push({ ti, d: Math.hypot(dx, dz) })
    }
  }
  cand.sort((a, b) => a.d - b.d)
  for (const c of cand) out.push(c.ti)
  return out
}
