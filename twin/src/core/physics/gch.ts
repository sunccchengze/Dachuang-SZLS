// ================================================================
// L4 物理内核 · FLORIS 4.6.6 GCH 默认配置的 TypeScript 移植
// ----------------------------------------------------------------
// 移植对象（源码行级对照，FLORIS 4.6.6 /usr 安装版 core/）：
//   · sequential_solver        core/solver.py
//   · GaussVelocityDeficit     core/wake_velocity/gauss.py
//   · GaussVelocityDeflection  core/wake_deflection/gauss.py
//   · CrespoHernandez          core/wake_turbulence/crespo_hernandez.py
//   · SOSFS                    core/wake_combination/sosfs.py
//   · CosineLossTurbine        core/turbine/operation_models.py（功率链）
//   · TurbineGrid(3×3,±D/4)    core/grid.py（radius_ratio=0.5, cubic-mean）
//   · rotate_coordinates_rel_west utilities.py（wind_delta=(wd−270) mod 360）
//
// 配置 = FlorisModel('defaults')（GCH）：
//   velocity=gauss(alpha .58 beta .077 ka .38 kb .004)
//   deflection=gauss(同参) + secondary_steering + yaw_added_recovery
//   transverse velocities（6 涡 + 地面镜像, eps=0.2D, κ=0.41, lmda=D/8）
//   turbulence=crespo_hernandez(.1/.5/.8/−.32)  combination=sosfs
//   风场 shear=0.12（参考高=轮毂 90m）, veer=0, rho=1.225
//
// V&V：scripts/selftest.mts 的 G 节对 docs/research/oracle/
//   floris_gch_oracle_v1.json（FLORIS 4.6.6 实算）逐项对拍。
// 本文件为纯函数、无副作用、无依赖 —— 渲染层与控制层共用同一真值。
// ================================================================

import { TURBINE, powerTableKw, ctTable, effectiveVelocity, axialInduction } from './florisTable.ts'

// ---- GCH 参数（default_inputs.yaml 原文）----
export const GCH = {
  alpha: 0.58,
  beta: 0.077,
  ka: 0.38,
  kb: 0.004,
  ch: { initial: 0.1, constant: 0.5, ai: 0.8, downstream: -0.32 },
  shear: 0.12,
  veer: 0.0,
  rho: 1.225,
  gchGain: 2, // yaw_added_recovery 增益（solver.py 硬编码）
  epsGain: 0.2, // 涡核尺度系数（gauss.py 硬编码）
  numEps: 0.001, // BaseModel.NUM_EPS
} as const

const DEG = Math.PI / 180
const clamp01 = (v: number) => (v < 0 ? 0 : v > 1 ? 1 : v)

export interface GCHWind {
  /** 轮毂高参考风速 (m/s) */
  uInf: number
  /** 来风方位（气象口径：风 FROM 的方向，°） */
  fromDeg: number
  /** 环境湍流强度 */
  ti: number
}

export interface TurbineEval {
  /** 转子立方平均风速 (m/s) */
  uAvg: number
  /** 有效风速（含偏航/密度修正，查表口径） */
  uEff: number
  /** 推力系数（有效风速处表值） */
  ct: number
  /** 轴向诱导因子 */
  aI: number
  /** 该机组处湍流强度（含上游尾流诱发，转子平均） */
  ti: number
  /** 并网功率 (kW) */
  powerKw: number
}

export interface GCHResult {
  /** 原始布局顺序的逐机结果 */
  turbines: TurbineEval[]
  totalKw: number
}

/**
 * FLORIS 4.6.6 GCH 顺序求解（turbine_grid 3×3 口径）。
 * @param xFloris 东向坐标 (m)
 * @param yFloris 北向坐标 (m)
 * @param wind 风况
 * @param yawDeg 各机偏航指令（°，FLORIS 约定：正=机头顺时针）
 */
export function runGCH(
  xFloris: number[],
  yFloris: number[],
  wind: GCHWind,
  yawDeg: number[],
): GCHResult {
  const n = xFloris.length
  const D = TURBINE.D
  const HH = TURBINE.HH
  const { alpha, beta, ka, kb, shear, gchGain, epsGain, numEps, rho } = GCH

  // ---- 坐标旋转（流向 +x'）----
  const delta = ((((wind.fromDeg - 270) % 360) + 360) % 360) * DEG
  let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity
  for (let i = 0; i < n; i++) {
    if (xFloris[i] < minX) minX = xFloris[i]
    if (xFloris[i] > maxX) maxX = xFloris[i]
    if (yFloris[i] < minY) minY = yFloris[i]
    if (yFloris[i] > maxY) maxY = yFloris[i]
  }
  const cx = (minX + maxX) / 2
  const cy = (minY + maxY) / 2
  const cosD = Math.cos(delta), sinD = Math.sin(delta)
  const xr = new Array(n), yr = new Array(n)
  for (let i = 0; i < n; i++) {
    const ox = xFloris[i] - cx, oy = yFloris[i] - cy
    xr[i] = ox * cosD - oy * sinD + cx
    yr[i] = ox * sinD + oy * cosD + cy
  }

  // ---- 排序（上游→下游，稳定）----
  const order = Array.from({ length: n }, (_, i) => i)
  order.sort((a, b) => xr[a] - xr[b] || a - b)
  const unsort = new Array(n)
  for (let i = 0; i < n; i++) unsort[order[i]] = i

  // ---- 3×3 转子网格（±D/4，cubic-mean 口径）----
  const NG = 9
  const off = [-D / 4, 0, D / 4]
  const px = new Float64Array(n * NG)
  const py = new Float64Array(n * NG)
  const pz = new Float64Array(n * NG)
  for (let i = 0; i < n; i++) {
    for (let g = 0; g < NG; g++) {
      const k = i * NG + g
      px[k] = xr[i]
      py[k] = yr[i] + off[(g % 3)]
      pz[k] = HH + off[(g / 3) | 0]
    }
  }

  // ---- 初始流场（剪切廓线，参考高=轮毂）----
  const uInit = new Float64Array(n * NG)
  const dudz = new Float64Array(n * NG)
  const refH = HH
  let uInitSum = 0
  for (let p = 0; p < n * NG; p++) {
    const z = pz[p]
    uInit[p] = wind.uInf * Math.pow(z / refH, shear)
    dudz[p] = wind.uInf * shear * Math.pow(1 / refH, shear) * Math.pow(z, shear - 1)
    uInitSum += uInit[p]
  }
  const uInfMean = uInitSum / (n * NG)

  // ---- 状态场 ----
  const u = uInit.slice()
  const v = new Float64Array(n * NG)
  const w = new Float64Array(n * NG)
  const wake = new Float64Array(n * NG)
  const tiGrid = new Float64Array(n * NG).fill(wind.ti)
  const defl = new Float64Array(n * NG)
  const deficit = new Float64Array(n * NG)
  const vWake = new Float64Array(n * NG)
  const wWake = new Float64Array(n * NG)

  const eps = epsGain * D
  const eps2 = eps * eps
  const velTop = Math.pow((HH + D / 2) / HH, shear)
  const velBot = Math.pow((HH - D / 2) / HH, shear)

  for (let si = 0; si < n; si++) {
    const t = order[si]
    const yi = yr[t]
    const xi = xr[t]
    const yawT = yawDeg[t]
    const base = si * NG

    // ---- 机组 i 当前状态 ----
    let u3 = 0
    let vSum = 0
    for (let g = 0; g < NG; g++) {
      const k = base + g
      u3 += u[k] * u[k] * u[k]
      vSum += v[k]
    }
    const uAvgI = Math.cbrt(u3 / NG)
    const uEffI = uAvgI > 0 ? effectiveVelocity(uAvgI, yawT, rho) : 0
    let ctI = uAvgI > 0 ? ctTable(uEffI) : 0.0001
    if (ctI > 0.9999) ctI = 0.9999 // 防护（验证域内不触发）
    const aI = axialInduction(ctI)
    const tiI = tiGrid[base]
    const avgV = vSum / NG

    // ---- 二次导向：wake_added_yaw ----
    let effYaw = yawT
    if (uAvgI > 0 && ctI > 0) {
      const gTop = (Math.PI / 8) * D * velTop * uInfMean * ctI
      const gBot = -(Math.PI / 8) * D * velBot * uInfMean * ctI
      const gRot = 0.25 * 2 * Math.PI * D * (aI - aI * aI) * uAvgI / TURBINE.TSR
      const vz = [HH + D / 2, HH - D / 2, HH]
      const gk = [gTop, gBot, gRot]
      const vMeans = [0, 0, 0]
      for (let g = 0; g < NG; g++) {
        const k = base + g
        const yRel = py[k] - yi + numEps
        for (let q = 0; q < 3; q++) {
          const zRel = pz[k] - vz[q] + numEps
          const r2 = yRel * yRel + zRel * zRel
          const core = 1 - Math.exp(-r2 / eps2)
          vMeans[q] += (gk[q] * zRel) / (2 * Math.PI * r2) * core
        }
      }
      for (let q = 0; q < 3; q++) vMeans[q] /= NG
      let val = (2 * (avgV - vMeans[2])) / (vMeans[0] + vMeans[1])
      if (val < -1) val = -1
      if (val > 1) val = 1
      // FLORIS: y = degrees(0.5 * arcsin(val))
      effYaw = yawT + Math.asin(val) / 2 / DEG
    }

    // ---- 偏折场（gauss，作用于全部网格点）----
    // 内部符号约定：yaw_m = −effYaw
    const yawM = -effYaw
    const yawMr = yawM * DEG
    const cosYm = Math.cos(yawMr)
    const s1ct = Math.sqrt(1 - ctI)
    const x0 = xi + (D * cosYm * (1 + s1ct)) / (Math.SQRT2 * (4 * alpha * tiI + 2 * beta * (1 - s1ct)))
    const kyD = ka * tiI + kb
    const thetaC0 = (0.3 * yawMr / cosYm) * (1 - Math.sqrt(1 - ctI * cosYm))
    const delta0 = Math.tan(thetaC0) * (x0 - xi)
    const eA = Math.exp(1 / 12), eB = Math.exp(1 / 3)
    for (let p = 0; p < n * NG; p++) {
      const up = uInit[p]
      const cosYct = ctI * cosYm
      const uR = (up * ctI * cosYm) / (2 * (1 - Math.sqrt(1 - cosYct)))
      const u0 = up * s1ct
      const sz0 = (D / 2) * Math.sqrt(uR / (up + u0))
      const sy0 = sz0 * cosYm
      const C0 = 1 - u0 / up
      const M0 = C0 * (2 - C0)
      const E0 = C0 * C0 - 3 * eA * C0 + 3 * eB
      const dNear = ((px[p] - xi) / (x0 - xi)) * delta0 * ((px[p] >= xi) && (px[p] <= x0) ? 1 : 0)
      let dFar = 0
      if (px[p] > x0) {
        const sy = kyD * (px[p] - x0) + sy0
        const sz = kyD * (px[p] - x0) + sz0
        const mt = Math.sqrt((sy * sz) / (sy0 * sz0))
        const ms = Math.sqrt(M0)
        const lnNum = (1.6 + ms) * (1.6 * mt - ms)
        const lnDen = (1.6 - ms) * (1.6 * mt + ms)
        const mid = (thetaC0 * E0 / 5.2) * Math.sqrt((sy0 * sz0) / (kyD * kyD * M0)) * Math.log(lnNum / lnDen)
        dFar = delta0 + mid
      }
      defl[p] = dNear + dFar
    }

    // ---- 横向速度（6 涡 + 地面镜像，全部网格点）----
    const yawTr = yawT * DEG
    const sinc = Math.sin(yawTr) * Math.cos(yawTr)
    const gTop2 = sinc * (Math.PI / 8) * D * velTop * uInfMean * ctI
    const gBot2 = -sinc * (Math.PI / 8) * D * velBot * uInfMean * ctI
    const gRot2 = uAvgI > 0 ? 0.25 * 2 * Math.PI * D * (aI - aI * aI) * uAvgI / TURBINE.TSR : 0
    for (let p = 0; p < n * NG; p++) {
      const dx = px[p] - xi
      if (dx < 0) {
        vWake[p] = 0
        wWake[p] = 0
        continue
      }
      const z = pz[p]
      const lm = (0.41 * z) / (1 + (0.41 * z) / (D / 8))
      const nu = lm * lm * Math.abs(dudz[p])
      const decay = eps2 / (4 * nu * (dx / uInfMean) + eps2)
      const yLoc = py[p] - yi + numEps
      // [Γ, zRel, sign] —— sign=+1 实涡, −1 镜像
      const vorts = [
        gTop2, z - (HH + D / 2) + numEps, 1,
        gBot2, z - (HH - D / 2) + numEps, 1,
        gRot2, z - HH + numEps, 1,
        gTop2, z + (HH + D / 2) + numEps, -1,
        gBot2, z + (HH - D / 2) + numEps, -1,
        gRot2, z + HH + numEps, -1,
      ]
      let vv = 0, ww = 0
      for (let q = 0; q < 6; q++) {
        const G = vorts[q * 3], zRel = vorts[q * 3 + 1], sgn = vorts[q * 3 + 2]
        const r2 = yLoc * yLoc + zRel * zRel
        const core = 1 - Math.exp(-r2 / eps2)
        const f = (G * core * decay) / (2 * Math.PI * r2)
        vv += sgn * f * zRel
        ww += -sgn * f * yLoc
      }
      vWake[p] = vv
      wWake[p] = ww > 0 ? ww : 0
    }

    // ---- 偏航附加湍流恢复（yaw_added_recovery, gch_gain=2）----
    let tiNew = tiI
    if (uAvgI > 0) {
      let vw = 0, wv = 0
      for (let g = 0; g < NG; g++) {
        const k = base + g
        vw += v[k] + vWake[k]
        wv += w[k] + wWake[k]
      }
      const vTerm = vw / NG
      const wTerm = wv / NG
      const kTke = (uAvgI * tiI) * (uAvgI * tiI) / (2 / 3)
      const uTerm = Math.sqrt(2 * kTke)
      const kTotal = 0.5 * (uTerm * uTerm + vTerm * vTerm + wTerm * wTerm)
      const iTot = Math.sqrt((2 / 3) * kTotal) / uAvgI
      tiNew = tiI + gchGain * (iTot - tiI)
    }
    for (let g = 0; g < NG; g++) tiGrid[base + g] = tiNew

    // ---- 速度亏损（gauss，近/远场，全部网格点）----
    const yawV = -yawT // 模型内部符号约定（仅 cos，等价）
    const yawVr = yawV * DEG
    const cosYv = Math.cos(yawVr)
    const x0v = xi + (D * cosYv * (1 + s1ct)) / (Math.SQRT2 * (4 * alpha * tiNew + 2 * beta * (1 - s1ct)))
    const kyV = ka * tiNew + kb
    const s1ctV = s1ct
    for (let p = 0; p < n * NG; p++) {
      const up = uInit[p]
      let dfc = 0
      if (ctI > 0 && up > 0) {
        const uR = (up * ctI) / (2 * (1 - s1ctV))
        const u0 = up * s1ctV
        const sz0 = (D / 2) * Math.sqrt(uR / (up + u0))
        const sy0 = sz0 * cosYv
        const xP = px[p]
        const dY = py[p] - yi - defl[p]
        const dZ = pz[p] - HH
        if (xP > xi + 0.1 && xP < x0v) {
          const rampUp = (xP - xi) / (x0v - xi)
          const rampDown = (x0v - xP) / (x0v - xi)
          const sy = (rampDown * 0.501 * D * Math.sqrt(ctI / 2) + rampUp * sy0) * (xP >= xi ? 1 : 0) + (xP < xi ? D * 0.5 : 0)
          const sz = (rampDown * 0.501 * D * Math.sqrt(ctI / 2) + rampUp * sz0) * (xP >= xi ? 1 : 0) + (xP < xi ? D * 0.5 : 0)
          const r2 = (dY * dY) / (2 * sy * sy) + (dZ * dZ) / (2 * sz * sz)
          const Cc = 1 - Math.sqrt(clamp01(1 - (ctI * cosYv) / ((8 * sy * sz) / (D * D))))
          dfc = Cc * Math.exp(-r2)
        } else if (xP >= x0v) {
          const sy = kyV * (xP - x0v) + sy0
          const sz = kyV * (xP - x0v) + sz0
          const r2 = (dY * dY) / (2 * sy * sy) + (dZ * dZ) / (2 * sz * sz)
          const Cc = 1 - Math.sqrt(clamp01(1 - (ctI * cosYv) / ((8 * sy * sz) / (D * D))))
          dfc = Cc * Math.exp(-r2)
        }
      }
      deficit[p] = dfc
    }

    // ---- 组合（SOSFS：亏损平方和开方）----
    for (let p = 0; p < n * NG; p++) {
      wake[p] = Math.hypot(wake[p], deficit[p] * uInit[p])
    }

    // ---- 尾流诱发湍流（crespo_hernandez + 面积重叠门）----
    const tiAdded = new Float64Array(n * NG)
    for (let p = 0; p < n * NG; p++) {
      const dxp = px[p] - xi
      if (dxp <= -0.1) { tiAdded[p] = 0; continue }
      const dEff = dxp <= 0.1 ? 1 : dxp
      tiAdded[p] =
        GCH.ch.constant *
        Math.pow(aI, GCH.ch.ai) *
        Math.pow(wind.ti, GCH.ch.initial) *
        Math.pow(dEff / D, GCH.ch.downstream)
    }
    for (let tj = 0; tj < n; tj++) {
      let hit = 0
      for (let g = 0; g < NG; g++) {
        const k = tj * NG + g
        if (deficit[k] * uInit[k] > 0.05) hit++
      }
      const ov = hit / NG
      const yj = yr[tj]
      for (let g = 0; g < NG; g++) {
        const k = tj * NG + g
        const m =
          (px[k] > xi ? 1 : 0) *
          (Math.abs(yj - py[k]) < 2 * D ? 1 : 0) *
          (px[k] <= xi + 15 * D ? 1 : 0)
        const add = ov * tiAdded[k] * m
        const cand = Math.sqrt(add * add + wind.ti * wind.ti)
        if (cand > tiGrid[k]) tiGrid[k] = cand
      }
    }

    // ---- 流场更新 ----
    for (let p = 0; p < n * NG; p++) {
      u[p] = uInit[p] - wake[p]
      v[p] += vWake[p]
      w[p] += wWake[p]
    }
  }

  // ---- 机组结果（unsort 回原始顺序）----
  const turbines: TurbineEval[] = new Array(n)
  let totalKw = 0
  for (let si = 0; si < n; si++) {
    const t = unsort[si]
    const base = si * NG
    let u3 = 0, tiSum = 0
    for (let g = 0; g < NG; g++) {
      const k = base + g
      u3 += u[k] * u[k] * u[k]
      tiSum += tiGrid[k]
    }
    const uAvg = Math.cbrt(u3 / NG)
    const uEff = uAvg > 0 ? effectiveVelocity(uAvg, yawDeg[t], rho) : 0
    const ct = uAvg > 0 ? ctTable(uEff) : 0.0001
    const pKw = powerTableKw(uEff)
    totalKw += pKw
    turbines[t] = {
      uAvg, uEff, ct,
      aI: axialInduction(Math.min(ct, 0.9999)),
      ti: tiSum / NG,
      powerKw: pKw,
    }
  }
  return { turbines, totalKw }
}
