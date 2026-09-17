// ================================================================
// L4 物理内核 · 场景系封装（twin 唯一物理求值入口）
// ----------------------------------------------------------------
// 坐标映射（全项目唯一口径）：
//   场景系：+x=东, +z=南（three.js Y-up）
//   FLORIS 系：x=东, y=北 → y = −z
//   来风方位 fromDeg：气象口径（风 FROM 的方向，0=北）
//     · 北来风 fromDeg=0 → 流向 +z（南）
//     · FLORIS wind_directions 同为气象口径 → 直接传入 fromDeg
// 用法：evaluateFarmScene(...) → 逐机 {uAvg,uEff,ct,aI,ti,powerKw} + totalKw
// 纯函数：同输入同输出；60fps 调用安全（<0.1 ms/次，9 机 3×3 网格）。
// ================================================================

import { runGCH, type GCHWind, type GCHResult } from './gch.ts'

export interface SceneFarm {
  /** 场景系 x（东，m） */
  x: number[]
  /** 场景系 z（南，m） */
  z: number[]
}

export interface SceneWind {
  /** 轮毂高参考风速 (m/s) */
  uInf: number
  /** 来风方位（气象：FROM，°，0=北） */
  fromDeg: number
  /** 环境湍流强度 */
  ti: number
}

/** 场景坐标 → FLORIS 惯用坐标（x=东, y=北） */
export function sceneToFloris(scene: SceneFarm): { xFloris: number[]; yFloris: number[] } {
  return {
    xFloris: scene.x.slice(),
    yFloris: scene.z.map((z) => -z),
  }
}

/**
 * 对场景风场求 GCH 稳态解（FLORIS 4.6.6 默认口径）。
 * @param scene 机组场景坐标
 * @param wind 风况
 * @param yawDeg 各机偏航指令（°）
 */
export function evaluateFarmScene(scene: SceneFarm, wind: SceneWind, yawDeg: number[]): GCHResult {
  const { xFloris, yFloris } = sceneToFloris(scene)
  const g: GCHWind = { uInf: wind.uInf, fromDeg: wind.fromDeg, ti: wind.ti }
  return runGCH(xFloris, yFloris, g, yawDeg)
}
