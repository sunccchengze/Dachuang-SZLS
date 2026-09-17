// ================================================================
// L4 物理内核 · 机组表（FLORIS 4.6.6 nrel_5MW.yaml 原样 54 点）
// ----------------------------------------------------------------
// 来源：docs/research/oracle/floris_gch_oracle_v1.json（生成器
//   docs/research/scripts/generate_floris_gch_oracle.py，
//   FlorisModel('defaults') 环境直读 turbine_library/nrel_5MW.yaml，
//   逐位一致存档）。
// 口径对齐 FLORIS v4 CosineLossTurbine：
//   · 功率/推力表以 ref_tilt=5° 为基准 → 定倾角机组（tilt=ref_tilt）
//     无需倾斜修正；
//   · 偏航/空气密度修正在【速度域】做（cos^1.88 等价于
//     u_eff *= cos(yaw)^(1.88/3) 后查表）；
//   · 表外（u<0 或 u>50 m/s）：功率填 0，推力填 0.0001（interp1d 语义）。
// 注：uEff 在 3 m/s 切出点表内 Ct=1.132>1 会使 √(1−Ct) 无定义 ——
//   本仓验证域（5–13.2 m/s，Ct≤0.82）不会触及；gch.ts 内有防护钳位。
// ================================================================

import { ORACLE } from '../../data/oracle/florisGchOracle.ts'

export const TURBINE = {
  /** 转子直径 (m) —— yaml rotor_diameter（含预锥） */
  D: ORACLE.turbine.D,
  /** 轮毂高 (m) */
  HH: ORACLE.turbine.HH,
  /** 额定尖速比 */
  TSR: ORACLE.turbine.TSR,
  /** 功率/推力表基准空气密度 (kg/m³) */
  refRho: ORACLE.turbine.refRho,
  /** 偏航余弦损失指数（cos^1.88） */
  expYaw: ORACLE.turbine.expYaw,
  /** 倾斜余弦损失指数 */
  expTilt: ORACLE.turbine.expTilt,
  /** 功率/推力表基准倾角 (°) */
  refTilt: ORACLE.turbine.refTilt,
}

const T = ORACLE.turbine.table
const U_TAB: number[] = new Array(T.length)
const P_TAB: number[] = new Array(T.length) // kW
const CT_TAB: number[] = new Array(T.length)
for (let i = 0; i < T.length; i++) {
  U_TAB[i] = T[i].u
  P_TAB[i] = T[i].kW
  CT_TAB[i] = T[i].Ct
}

/** interp1d（线性、表外填 fill）—— 与 scipy 默认口径一致 */
function interp1d(x: number[], y: number[], v: number, fill: number): number {
  if (v <= x[0]) return v === x[0] ? y[0] : fill
  const n = x.length
  if (v >= x[n - 1]) return v === x[n - 1] ? y[n - 1] : fill
  let i = 0
  while (i < n - 2 && x[i + 1] < v) i++
  const t = (v - x[i]) / (x[i + 1] - x[i])
  return y[i] + (y[i + 1] - y[i]) * t
}

/** 单机并网功率 (kW)：FLORIS 表（5° 基准）在有效风速处的线性插值 */
export function powerTableKw(uEff: number): number {
  return interp1d(U_TAB, P_TAB, uEff, 0)
}

/** 推力系数：FLORIS 表线性插值（表外 0.0001） */
export function ctTable(uEff: number): number {
  return interp1d(U_TAB, CT_TAB, uEff, 0.0001)
}

/**
 * FLORIS v4 有效风速链（速度域修正）：
 *   u_eff = u_avg · (ρ/ρref)^(1/3) · cos(yaw)^(expYaw/3) · (cos(tilt)/cos(refTilt))^(expTilt/3)
 * 定倾角机组（tilt = refTilt）：倾斜项恒为 1，本实现即此口径。
 */
export function effectiveVelocity(
  uAvg: number,
  yawDeg: number,
  rho: number,
  tiltDeg = TURBINE.refTilt,
): number {
  const d = Math.PI / 180
  const tiltF =
    tiltDeg === TURBINE.refTilt
      ? 1
      : (Math.cos(tiltDeg * d) / Math.cos(TURBINE.refTilt * d)) ** (TURBINE.expTilt / 3)
  return uAvg * (rho / TURBINE.refRho) ** (1 / 3) * Math.cos(yawDeg * d) ** (TURBINE.expYaw / 3) * tiltF
}

/** 轴向诱导因子 a = (1 − √(1−Ct))/2（FLORIS SimpleTurbine.axial_induction 口径） */
export function axialInduction(ct: number): number {
  const c = Math.min(ct, 0.9999) // 防护：验证域内恒 <0.82，钳位不触发
  return (1 - Math.sqrt(1 - c)) / 2
}
