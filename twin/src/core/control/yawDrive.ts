// ================================================================
// P2 · 偏航执行器（死区 + 机械速率限制 + 起停滞环）—— 纯函数层
// ----------------------------------------------------------------
// 残项来源：此前偏航响应是「一阶平滑插值 dt×3.5」（≈0.29s 走完全程），
// HUD 滑杆一拨、三维机头与尾流瞬间到位 —— 真实风电场不可能这样：
//   · 偏航电机额定速率 ~0.3°/s（NREL 5MW baseline：YawNeutron 0.3 deg/s，
//     机舱从 0° 转到 30° 需要 100s），不是「秒到位」；
//   · 对风死区：偏差在 ±5° 内不启停（否则偏航电机每小时上百次点动，
//     齿轮与刹车片寿命直接崩），且停机判据要比起动判据更宽（滞环），
//     否则在死区边界会持续抖动（hunting）；
//   · 起动/停机有加减速过程（电机不可能瞬时到额定转速）；
//   · 指令本身还有一层控制器滤波（偏航计数器 10 分钟平均是真实控制律，
//     这里用 1.5s 一阶滤波近似「PLC 扫描 + 指令下发」的滞后）。
//
// 口径落地（重要）：本模块的输出 `actual` 是**全场唯一的机舱实际方位偏差**，
// 三维机头、尾流偏折、GCH 物理解算、HUD 读数全部读它；滑杆/寻优给的是
// **指令** `cmd`。指令与实际之间从此有了真实的分钟级滞后 —— 这正是
// 「偏航优化下发指令 → 机组逐步执行 → 功率逐步爬升」的工业叙事。
//
// 诚实边界：单自由度刚体偏航 + 速率/死区限制，不是 OpenFAST 的
// 传动链扭转弹性模型（塔架前后振动、机舱柔性仍属未做项，见 HANDOFF_NEXT）。
// ================================================================

/** 偏航电机额定速率 (°/s)：NREL 5MW baseline 口径 0.3°/s */
export const YAW_RATE_DPS = 0.3
/** 起停加减速时间常数 (s)：0→额定速率 ~1.2s（变频器斜坡） */
export const YAW_RAMP_TAU = 1.2
/** 对风死区 (°)：|err| < 5° 不起动 */
export const YAW_DEADBAND_DEG = 5
/** 停机滞环 (°)：|err| < 3° 才停（起动 5° / 停机 3° → 无 hunting） */
export const YAW_STOP_BAND_DEG = 3
/** 指令滤波时间常数 (s)：控制器/PLC 侧滞后 */
export const YAW_CMD_TAU = 1.5
/** 指令量程（与 HUD 滑杆、store.setUnitYaw 同一约束） */
export const YAW_CMD_LIMIT_DEG = 30

export interface YawActuatorState {
  /** 指令（滑杆/寻优给的值，经量程钳制） */
  cmd: number
  /** 滤波后的指令（控制器内部量） */
  cmdF: number
  /** 机舱实际偏航偏差 Δψ (°) —— 全场唯一真值 */
  actual: number
  /** 当前偏航速率 (°/s，带符号) */
  rate: number
  /** 电机是否在执行偏航 */
  slewing: boolean
  /** 本次连续偏航已走的角度 (°)，停机归零 */
  travelDeg: number
  /** 累计起动次数（真实运维关心的偏航动作计数：点动越多，齿轮/刹车寿命越短） */
  cycles: number
  /** 当前落在死区里、不会引起动作的指令偏差 (°) */
  deadbandErr: number
}

export function createYawActuator(cmd = 0): YawActuatorState {
  const c = clampCmd(cmd)
  return {
    cmd: c, cmdF: c, actual: c, rate: 0, slewing: false,
    travelDeg: 0, cycles: 0, deadbandErr: 0,
  }
}

export function clampCmd(v: number): number {
  if (!Number.isFinite(v)) return 0
  return Math.max(-YAW_CMD_LIMIT_DEG, Math.min(YAW_CMD_LIMIT_DEG, v))
}

/**
 * 推进一步（纯函数：返回新状态，不修改入参 → selftest 可直接跑时间序列）。
 * @param s 当前状态
 * @param cmd 新指令（°，滑杆/寻优值）
 * @param dt 步长（s，钳到 [0, 0.5] 防后台标签页大步长）
 */
export function stepYaw(s: YawActuatorState, cmd: number, dt: number): YawActuatorState {
  const h = Math.max(0, Math.min(0.5, dt))
  const c = clampCmd(cmd)
  // ① 指令一阶滤波（控制器/PLC 滞后）
  const aF = 1 - Math.exp(-h / YAW_CMD_TAU)
  const cmdF = s.cmdF + (c - s.cmdF) * aF
  const err = cmdF - s.actual

  // ② 死区 + 滞环：起动看 5°，停机看 3°（同一阈值会 hunting）
  let slewing = s.slewing
  if (!slewing && Math.abs(err) > YAW_DEADBAND_DEG) slewing = true
  else if (slewing && Math.abs(err) < YAW_STOP_BAND_DEG) slewing = false

  // ③ 速率限制 + 起停斜坡（变频器加减速：0→0.3°/s 约 1.2s）
  const dir = Math.sign(err)
  const target = slewing ? dir * YAW_RATE_DPS : 0
  const aR = 1 - Math.exp(-h / YAW_RAMP_TAU)
  const rate = s.rate + (target - s.rate) * aR
  // 停机时速率按 τ=0.25s 归零（电机抱闸），不是硬切 0（硬切会有机械冲击感）
  const eff = slewing ? rate : rate * Math.exp(-h / 0.25)
  let actual = s.actual + eff * h

  // ④ 到位判定：本步跨过目标（符号翻转）或已进入停机带 → 贴到停机带边缘并抱闸
  let cycles = s.cycles
  let travelDeg = slewing ? s.travelDeg + Math.abs(eff * h) : 0
  if (slewing) {
    const crossed = dir !== 0 && (cmdF - actual) * dir <= 0
    if (crossed || Math.abs(cmdF - actual) < YAW_STOP_BAND_DEG) {
      actual = cmdF - dir * Math.min(YAW_STOP_BAND_DEG * 0.8, Math.abs(err) * 0.5)
      slewing = false
      cycles += 1
      travelDeg = 0
    }
  }

  return {
    cmd: c,
    cmdF,
    actual: Math.abs(actual) < 1e-9 ? 0 : actual,
    rate: eff,
    slewing,
    travelDeg,
    cycles,
    deadbandErr: Math.abs(c - actual) <= YAW_DEADBAND_DEG ? c - actual : 0,
  }
}

/**
 * 从当前状态走到目标指令还需多久 (s)：HUD 的「预计到位」读数。
 * 0 = 已到位（或落在死区里，电机按设计**不会**动作）。
 */
export function yawEtaS(s: YawActuatorState): number {
  return yawEtaFrom(s.cmd, s.actual)
}

/** 同上，但只吃「指令 / 实际」两个数（HUD 轻量读数用，不必持有完整状态） */
export function yawEtaFrom(cmd: number, actual: number): number {
  const err = Math.abs(cmd - actual)
  if (err <= YAW_DEADBAND_DEG) return 0 // 死区保持：设计上就不动
  return err / YAW_RATE_DPS + YAW_RAMP_TAU * 1.6 // 两端加减速各 ~1.6τ
}

// ---- 全场 9 机执行器组（运行时单例；物理/HUD/三维共用）----
export interface YawBank {
  states: YawActuatorState[]
  /** 最近一次步长（s） */
  lastDt: number
}

export function createYawBank(n: number, cmd: number[] = []): YawBank {
  return {
    states: Array.from({ length: n }, (_, i) => createYawActuator(cmd[i] ?? 0)),
    lastDt: 0,
  }
}

/** 就地推进整组（运行时热路径：不新建对象，直接改 states[i] 字段） */
export function stepYawBank(bank: YawBank, cmds: number[], dt: number): void {
  const h = Math.max(0, Math.min(0.5, dt))
  bank.lastDt = h
  for (let i = 0; i < bank.states.length; i++) {
    const next = stepYaw(bank.states[i], cmds[i] ?? 0, h)
    bank.states[i] = next
  }
}

/**
 * QA / 截图回归专用：把整组执行器瞬移到指令角（跳过速率限制与死区）。
 * 运行时 UI 永不调用 —— 真实界面必须看到 0.3°/s 的分钟级滞后；
 * 只有稳态对比（docs/08 的联动证据、before/after 帧差）需要「指令已到位」。
 */
export function snapYawBank(bank: YawBank, cmds: number[]): void {
  for (let i = 0; i < bank.states.length; i++) {
    const c = clampCmd(cmds[i] ?? 0)
    bank.states[i] = {
      cmd: c, cmdF: c, actual: c, rate: 0, slewing: false,
      travelDeg: 0, cycles: bank.states[i].cycles, deadbandErr: 0,
    }
  }
}

/** 量化到 0.5°（farmFrame 的缓存键口径，避免浮点尾数击穿记忆化） */
export function quantizeYaw(v: number): number {
  return Math.round(v * 2) / 2
}

/** 整组实际偏航（量化后）—— farmFrame / AirflowField / HoloTurbine 的唯一输入 */
export function bankActual(bank: YawBank): number[] {
  return bank.states.map((s) => quantizeYaw(s.actual))
}
