// ================================================================
// T9 · Web Audio 声场引擎（浏览器层）
// ----------------------------------------------------------------
// 全程序化、零外部音频资产（延续本仓「零外部请求」红线）：
//   · 噪声源 = AudioBuffer 里现算的白/粉/棕噪声（Paul Kellett 粉噪 + 棕噪积分），
//     三条源用互质长度（2.71/3.37/4.09s）循环 + 不同 playbackRate → 无可闻循环点；
//   · 海面：棕噪低频涌浪底 + 粉噪中频水声（滤波频率随浪高走）+ 拍岸碎浪带
//     （bandpass 白噪 + 碎浪 LFO 包络），响度与节奏由 audioModel 给出
//     （与 WorldTerrain 的 Gerstner 同源 → 听到的浪和看到的浪是同一套）；
//   · 风机：每台一条声部 = 切风嘶声（bandpass，中心频率随 rpm）× 叶片通过
//     包络（bladePass LFO，3 叶片）+ 传动链音调（转频×97 的齿轮箱/发电机
//     谐波，压得很低，只在近塔可闻）→ PannerNode('HRTF') 做 3D 定位；
//   · 声部数上限 3（audioModel.selectTurbines 裁决），远排融进底噪；
//   · 全部参数用 setTargetAtTime 平滑（τ=0.25~0.6s），推滑杆/切镜头不会有爆音；
//   · AudioContext 只能在用户手势里创建/恢复（浏览器自动播放策略）：
//     引擎 ensure() 由 HUD 声音按钮触发，未开声时零节点、零开销。
//
// 诚实口径：程序化**示意**声场，非实测声压级/非 IEC 61400-11 数据。
// ================================================================

import { acousticFrame, type AcousticScene, type AcousticFrame } from './audioModel.ts'

/** 声部上限：3 台 PannerNode（近塔可闻的从来只有最近几台） */
const MAX_VOICES = 3
/** 参数平滑时间常数（s） */
const TAU_GAIN = 0.35
const TAU_FILTER = 0.5
const TAU_POS = 0.06
/** 混音基准（0..1 → 实际增益），整体克制：声场是氛围，不是主角 */
const MIX = {
  swell: 0.30, // 远场涌浪底噪
  wash: 0.22, // 中频水声
  surf: 0.34, // 拍岸碎浪
  wind: 0.13, // 大气风噪床
  turbine: 0.55, // 单台风机（近塔满量程）
  tone: 0.10, // 传动链音调（相对切风声）
}

/** 互质噪声循环长度（s）：三条源长度互质 → 叠加后无可闻周期 */
const NOISE_LEN = { brown: 4.09, pink: 3.37, white: 2.71 } as const
const SR_FALLBACK = 48000

// ---- 噪声生成（Paul Kellett 粉噪近似 + 棕噪一阶积分）----
function makeNoiseBuffer(ctx: BaseAudioContext, kind: 'white' | 'pink' | 'brown', seconds: number): AudioBuffer {
  const sr = ctx.sampleRate || SR_FALLBACK
  const n = Math.max(1024, Math.floor(sr * seconds))
  const buf = ctx.createBuffer(1, n, sr)
  const d = buf.getChannelData(0)
  let b0 = 0, b1 = 0, b2 = 0, b3 = 0, b4 = 0, b5 = 0, b6 = 0
  let last = 0
  // 用固定种子的 LCG，保证同一浏览器多次构建同一纹理（可复现，D2 红线）
  let s = 0x2f6e2b1 >>> 0
  const rnd = () => {
    s = (Math.imul(s, 1664525) + 1013904223) >>> 0
    return s / 4294967296
  }
  for (let i = 0; i < n; i++) {
    const w = rnd() * 2 - 1
    if (kind === 'white') {
      d[i] = w * 0.7
    } else if (kind === 'pink') {
      b0 = 0.99886 * b0 + w * 0.0555179
      b1 = 0.99332 * b1 + w * 0.0750759
      b2 = 0.96900 * b2 + w * 0.1538520
      b3 = 0.86650 * b3 + w * 0.3104856
      b4 = 0.55000 * b4 + w * 0.5329522
      b5 = -0.7616 * b5 - w * 0.0168980
      d[i] = (b0 + b1 + b2 + b3 + b4 + b5 + b6 + w * 0.5362) * 0.11
      b6 = w * 0.115926
    } else {
      // 棕噪（Red/Brown）：白噪一阶积分 + 轻泄漏，低频厚重 = 涌浪体量
      last = (last + 0.02 * w) / 1.02
      d[i] = last * 3.5
    }
  }
  // 首尾交叉淡化 40ms：循环点无跳变（否则会听到周期性的「咔」）
  const xf = Math.min(Math.floor(sr * 0.04), Math.floor(n / 4))
  for (let i = 0; i < xf; i++) {
    const k = i / xf
    d[n - xf + i] = d[n - xf + i] * (1 - k) + d[i] * k
  }
  return buf
}

interface LoopVoice {
  src: AudioBufferSourceNode
  gain: GainNode
  filter: BiquadFilterNode
}

interface TurbineVoice {
  panner: PannerNode
  gain: GainNode
  swish: BiquadFilterNode
  swishGain: GainNode
  /** 空气吸收低通：截止频率随距离掉（远声发闷），R40b */
  air: BiquadFilterNode
  bladeLfo: OscillatorNode
  bladeDepth: GainNode
  bladeBias: ConstantSourceNode
  tone: OscillatorNode
  tone2: OscillatorNode
  toneGain: GainNode
  src: AudioBufferSourceNode
  active: boolean
  idx: number
}

/**
 * 声场引擎：单例（一个页面一个 AudioContext）。
 * 生命周期：ensure()（用户手势）→ update(scene)（每帧）→ suspend()/resume() → dispose()
 */
export class AudioEngine {
  private ctx: AudioContext | null = null
  private master: GainNode | null = null
  private oceanBus: GainNode | null = null
  private turbineBus: GainNode | null = null
  private brown: LoopVoice | null = null
  private pink: LoopVoice | null = null
  private white: LoopVoice | null = null
  private surfVoices: LoopVoice[] = []
  private surfLfo: OscillatorNode | null = null
  private surfLfoDepth: GainNode | null = null
  private surfLowLfoDepth: GainNode | null = null
  /** 风床阵 gust LFO + 海床群浪 LFO（R40b：床声不再是一条直线嘶声） */
  private gustLfo: OscillatorNode | null = null
  private gustDepth: GainNode | null = null
  private groupLfo: OscillatorNode | null = null
  private groupDepthBrown: GainNode | null = null
  private groupDepthPink: GainNode | null = null
  private voices: TurbineVoice[] = []
  private lastFrame: AcousticFrame | null = null
  private lastParamAt = 0
  private vol = 0.7
  private muted = true
  /** 开场门（0=压静音，1=正常）：与音量/静音正交，淡入淡出不打架 */
  private gate = 1
  /** 最近一次 update 的场景（重连/恢复时用） */
  private lastScene: AcousticScene | null = null

  get ready(): boolean {
    return this.ctx !== null && this.ctx.state !== 'closed'
  }
  get state(): AudioContextState | 'none' {
    return this.ctx ? this.ctx.state : 'none'
  }
  get frame(): AcousticFrame | null {
    return this.lastFrame
  }

  setVolume(v: number): void {
    this.vol = Math.max(0, Math.min(1, v))
    this.applyMaster(0.12)
  }

  /** 开场巡航门控：introDone 之前淡出全部声音，开场结束淡入（不碰 muted/vol） */
  setGate(g: number): void {
    const v = Math.max(0, Math.min(1, g))
    if (v === this.gate) return
    this.gate = v
    this.applyMaster(0.9) // 开场淡入用更长的 τ，像「场景醒来」而不是「按下播放」
  }

  private applyMaster(tau: number): void {
    if (!this.master || !this.ctx) return
    const g = this.muted ? 0 : this.vol * this.vol * this.gate // 感知近似平方律
    this.master.gain.setTargetAtTime(g, this.ctx.currentTime, tau)
  }

  /**
   * 创建/恢复 AudioContext —— **必须在用户手势调用栈内**。
   * 返回是否成功（浏览器拒绝时 HUD 给提示，不抛异常打断界面）。
   */
  async ensure(): Promise<boolean> {
    try {
      if (!this.ctx) {
        const Ctor: typeof AudioContext | undefined =
          window.AudioContext ?? (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext
        if (!Ctor) return false
        this.ctx = new Ctor({ latencyHint: 'interactive' })
        this.build()
      }
      if (this.ctx.state === 'suspended') await this.ctx.resume()
      this.muted = false
      this.applyMaster(0.25)
      // 恢复后立刻按最近场景刷一遍参数（否则会静音到下一帧）
      if (this.lastScene) this.update(this.lastScene)
      return this.ctx.state === 'running'
    } catch {
      return false
    }
  }

  /** 静音（保留上下文与节点，随时可恢复；标签页隐藏时也走这条） */
  mute(): void {
    this.muted = true
    this.applyMaster(0.08)
  }

  async unmute(): Promise<boolean> {
    return this.ensure()
  }

  /** 构建节点图（只一次） */
  private build(): void {
    const ctx = this.ctx
    if (!ctx) return

    this.master = ctx.createGain()
    this.master.gain.value = 0
    // R40b 主链整形：30Hz 高通（笔记本喇叭不浪费冲程在听不见的次声上）+
    // 压缩器兜底（浪+碎浪+风机全热时不削顶）
    const hp = ctx.createBiquadFilter()
    hp.type = 'highpass'
    hp.frequency.value = 30
    const comp = ctx.createDynamicsCompressor()
    comp.threshold.value = -14
    comp.knee.value = 10
    comp.ratio.value = 3.5
    comp.attack.value = 0.02
    comp.release.value = 0.35
    this.master.connect(hp)
    hp.connect(comp)
    comp.connect(ctx.destination)

    this.oceanBus = ctx.createGain()
    this.oceanBus.gain.value = 1
    this.oceanBus.connect(this.master)

    this.turbineBus = ctx.createGain()
    this.turbineBus.gain.value = 1
    this.turbineBus.connect(this.master)

    // —— 噪声源（三条互质长度循环）——
    const brownBuf = makeNoiseBuffer(ctx, 'brown', NOISE_LEN.brown)
    const pinkBuf = makeNoiseBuffer(ctx, 'pink', NOISE_LEN.pink)
    const whiteBuf = makeNoiseBuffer(ctx, 'white', NOISE_LEN.white)

    // ① 涌浪底（棕噪 → lowpass ~190Hz）
    this.brown = this.makeLoop(brownBuf, 'lowpass', 190, 0.9, this.oceanBus)
    this.brown.src.playbackRate.value = 0.86
    // ② 水声中频（粉噪 → lowpass 随浪高 600~1500Hz）
    this.pink = this.makeLoop(pinkBuf, 'lowpass', 900, 0.7, this.oceanBus)
    this.pink.src.playbackRate.value = 1.07
    // ③ 大气风噪床（白噪 → highpass ~2.6kHz）：叶片切风之外的空气嘶声
    this.white = this.makeLoop(whiteBuf, 'highpass', 2600, 0.7, this.oceanBus)
    this.white.src.playbackRate.value = 1.31

    // ④ 拍岸碎浪（白噪 → bandpass ~1.1kHz）+ 慢 LFO 做「哗——沙——」包络
    const surf = this.makeLoop(whiteBuf, 'bandpass', 1150, 0.85, this.oceanBus)
    surf.src.playbackRate.value = 1.21
    surf.gain.gain.value = 0
    this.surfVoices.push(surf)
    // 碎浪第二层：低频冲刷体量（棕噪 bandpass 320Hz）
    const surfLow = this.makeLoop(brownBuf, 'bandpass', 320, 1.1, this.oceanBus)
    surfLow.src.playbackRate.value = 1.13
    surfLow.gain.gain.value = 0
    this.surfVoices.push(surfLow)

    // R40b 修「离很远还有明显碎浪声」：旧版把 0.5/0.45 的 ConstantSource 直流**硬接**到
    // gain.gain（AudioParam 的外接输入是「加」在本征值上）→ surfGain=0 时包络仍 = 0.5，
    // 碎浪嘶声全图常响。现在直流折进本征值（base×0.5），LFO 深度 = 同值 → 包络 ∈ [0, 2×base]，
    // surfGain→0 时包络与摆幅一起归零（真的静音，不是「小声但一直在」）。
    this.surfLfo = ctx.createOscillator()
    this.surfLfo.type = 'sine'
    this.surfLfo.frequency.value = 0.12 // ≈8.3s 一组浪，update() 里对齐涌浪周期
    this.surfLfoDepth = ctx.createGain()
    this.surfLfoDepth.gain.value = 0
    this.surfLfo.connect(this.surfLfoDepth)
    this.surfLfoDepth.connect(surf.gain.gain)
    const surfLowDepth = ctx.createGain()
    surfLowDepth.gain.value = 0
    this.surfLowLfoDepth = surfLowDepth
    this.surfLfo.connect(surfLowDepth)
    surfLowDepth.connect(surfLow.gain.gain)
    this.surfLfo.start()

    // 风床阵 gust（~14s 一阵 ±25%）与海床群浪（~32s ±15%）：床声呼吸感，R40b
    this.gustLfo = ctx.createOscillator()
    this.gustLfo.type = 'sine'
    this.gustLfo.frequency.value = 0.072
    this.gustDepth = ctx.createGain()
    this.gustDepth.gain.value = 0
    this.gustLfo.connect(this.gustDepth)
    this.gustDepth.connect(this.white.gain.gain)
    this.gustLfo.start()
    this.groupLfo = ctx.createOscillator()
    this.groupLfo.type = 'sine'
    this.groupLfo.frequency.value = 0.031
    this.groupDepthBrown = ctx.createGain()
    this.groupDepthBrown.gain.value = 0
    this.groupDepthPink = ctx.createGain()
    this.groupDepthPink.gain.value = 0
    this.groupLfo.connect(this.groupDepthBrown)
    this.groupLfo.connect(this.groupDepthPink)
    this.groupDepthBrown.connect(this.brown.gain.gain)
    this.groupDepthPink.connect(this.pink.gain.gain)
    this.groupLfo.start()

    // —— 风机声部 ×3（共用一份粉噪 buffer：三条源各自 playbackRate 去相关，
    //     不重复生成 3×3.37s 噪声 —— 构建期 CPU 与内存都省 2/3）——
    const voiceBuf = makeNoiseBuffer(ctx, 'pink', NOISE_LEN.pink)
    for (let i = 0; i < MAX_VOICES; i++) this.voices.push(this.makeTurbineVoice(i, voiceBuf))
  }

  private makeLoop(buf: AudioBuffer, type: BiquadFilterType, freq: number, q: number, dest: AudioNode): LoopVoice {
    const ctx = this.ctx!
    const src = ctx.createBufferSource()
    src.buffer = buf
    src.loop = true
    const filter = ctx.createBiquadFilter()
    filter.type = type
    filter.frequency.value = freq
    filter.Q.value = q
    const gain = ctx.createGain()
    gain.gain.value = 0
    src.connect(filter)
    filter.connect(gain)
    gain.connect(dest)
    src.start()
    return { src, gain, filter }
  }

  private makeTurbineVoice(i: number, voiceBuf: AudioBuffer): TurbineVoice {
    const ctx = this.ctx!
    const panner = ctx.createPanner()
    panner.panningModel = 'HRTF'
    // R40b：距离衰减唯一真值在 audioModel.turbineDistanceGain（可回归）；
    // Panner 只负责 HRTF 方位（rolloff=0 → 不叠加第二份距离衰减，旧版双衰减使
    // 近塔偏闷、且与 selftest 曲线对不上）
    panner.distanceModel = 'inverse'
    panner.refDistance = 120
    panner.maxDistance = 4000
    panner.rolloffFactor = 0
    panner.positionX.value = 0
    panner.positionY.value = -9999 // 未分配声部：推到地下极远，HRTF 也不会漏声
    panner.positionZ.value = 0
    panner.connect(this.turbineBus!)

    const gain = ctx.createGain()
    gain.gain.value = 0
    gain.connect(panner)

    // 切风嘶声：粉噪 → bandpass（中心频率随 rpm）→ 叶片通过包络 → gain
    const src = ctx.createBufferSource()
    src.buffer = voiceBuf
    src.loop = true
    src.playbackRate.value = 0.94 + i * 0.05 // 三声部去相关
    const swish = ctx.createBiquadFilter()
    swish.type = 'bandpass'
    swish.frequency.value = 620
    swish.Q.value = 0.9
    const swishGain = ctx.createGain()
    // R40b：本征值必须为 0 —— 包络直流由 bladeBias(0.65) 外接提供；
    // 旧版本征 1 + 偏置 0.65 = 1.65±depth，切风声整体 hot 了 ~2.5 倍
    swishGain.gain.value = 0
    // 空气吸收低通：远声发闷（截止频率 update() 里随距离掉）
    const air = ctx.createBiquadFilter()
    air.type = 'lowpass'
    air.frequency.value = 7000
    air.Q.value = 0.4
    src.connect(swish)
    swish.connect(swishGain)
    swishGain.connect(air)
    air.connect(gain)

    // 叶片通过包络：LFO(0.35~0.6Hz) → 深度 + 直流偏置 → swishGain（抬升余弦包络）
    const bladeLfo = ctx.createOscillator()
    bladeLfo.type = 'sine'
    bladeLfo.frequency.value = 0.5
    const bladeDepth = ctx.createGain()
    bladeDepth.gain.value = 0.35
    const bladeBias = ctx.createConstantSource()
    bladeBias.offset.value = 0.65
    bladeLfo.connect(bladeDepth)
    bladeDepth.connect(swishGain.gain)
    bladeBias.connect(swishGain.gain)

    // 传动链音调：转频×97（发电机侧）+ 一次谐波，压得很低
    const tone = ctx.createOscillator()
    tone.type = 'triangle'
    tone.frequency.value = 180
    const tone2 = ctx.createOscillator()
    tone2.type = 'sine'
    tone2.frequency.value = 360
    const toneGain = ctx.createGain()
    toneGain.gain.value = 0
    const tone2Gain = ctx.createGain()
    tone2Gain.gain.value = 0.4
    tone.connect(toneGain)
    tone2.connect(tone2Gain)
    tone2Gain.connect(toneGain)
    toneGain.connect(air) // 机械音调同样过空气吸收

    src.start()
    bladeLfo.start()
    bladeBias.start()
    tone.start()
    tone2.start()

    return {
      panner, gain, swish, swishGain, air, bladeLfo, bladeDepth, bladeBias,
      tone, tone2, toneGain, src, active: false, idx: -1,
    }
  }

  /** 每帧：求值声场并把参数平滑推给节点图（未开声时只做纯函数求值，零节点操作） */
  update(scene: AcousticScene): void {
    this.lastScene = scene
    const f = acousticFrame(scene)
    this.lastFrame = f
    const ctx = this.ctx
    if (!ctx || !this.master || ctx.state !== 'running') return

    const now = ctx.currentTime
    // 参数节流：50Hz 足够（setTargetAtTime 本身是连续的），避免每帧上百次调度
    const heavy = now - this.lastParamAt > 0.02
    this.lastParamAt = now

    // —— 听者（相机）位姿 ——
    const L = ctx.listener
    if (L.positionX) {
      L.positionX.setTargetAtTime(scene.lx, now, TAU_POS)
      L.positionY.setTargetAtTime(scene.ly, now, TAU_POS)
      L.positionZ.setTargetAtTime(scene.lz, now, TAU_POS)
      L.forwardX.setTargetAtTime(scene.fx, now, TAU_POS)
      L.forwardY.setTargetAtTime(scene.fy, now, TAU_POS)
      L.forwardZ.setTargetAtTime(scene.fz, now, TAU_POS)
      L.upX.setTargetAtTime(scene.ux, now, TAU_POS)
      L.upY.setTargetAtTime(scene.uy, now, TAU_POS)
      L.upZ.setTargetAtTime(scene.uz, now, TAU_POS)
    } else {
      // 老 Safari 回退
      const legacy = L as unknown as {
        setPosition: (x: number, y: number, z: number) => void
        setOrientation: (fx: number, fy: number, fz: number, ux: number, uy: number, uz: number) => void
      }
      legacy.setPosition?.(scene.lx, scene.ly, scene.lz)
      legacy.setOrientation?.(scene.fx, scene.fy, scene.fz, scene.ux, scene.uy, scene.uz)
    }

    if (!heavy) return

    // —— 海面三层 ——
    if (this.brown) {
      this.brown.gain.gain.setTargetAtTime(MIX.swell * f.swellGain, now, TAU_GAIN)
      // 浪越大，涌浪底越「开」（低频泄漏更多）
      this.brown.filter.frequency.setTargetAtTime(150 + 120 * f.swellGain, now, TAU_FILTER)
    }
    if (this.pink) {
      this.pink.gain.gain.setTargetAtTime(MIX.wash * f.swellGain, now, TAU_GAIN)
      this.pink.filter.frequency.setTargetAtTime(620 + 900 * f.swellGain, now, TAU_FILTER)
    }
    // 碎浪 LFO 节奏对齐涌浪周期（画面浪多久一组，声音就多久一组）
    if (this.surfLfo) {
      const lfoHz = Math.max(0.05, Math.min(0.6, 1 / Math.max(2, f.swellPeriod)))
      this.surfLfo.frequency.setTargetAtTime(lfoHz, now, 1.2)
    }
    // R40b：包络 = base ± depth·lfo，base 与 depth 同值（= MIX×surfGain×层权×0.5）
    // → 摆幅 ∈ [0, 2base]；surfGain→0 时 base 与 depth 一起归零 = 真静音
    for (let i = 0; i < this.surfVoices.length; i++) {
      const sv = this.surfVoices[i]
      const base = MIX.surf * f.surfGain * (i === 0 ? 1 : 0.7) * 0.5
      sv.gain.gain.setTargetAtTime(base, now, TAU_GAIN * 1.6)
      const depth = i === 0 ? this.surfLfoDepth : this.surfLowLfoDepth
      if (depth) depth.gain.setTargetAtTime(base, now, TAU_GAIN * 1.6)
      if (i === 0) sv.filter.frequency.setTargetAtTime(900 + 700 * f.surfGain, now, TAU_FILTER)
    }

    // —— 大气风噪床（第三条白噪）+ gust 呼吸（R40b）——
    if (this.white) {
      const wbase = MIX.wind * f.windGain
      this.white.gain.gain.setTargetAtTime(wbase, now, TAU_GAIN)
      if (this.gustDepth) this.gustDepth.gain.setTargetAtTime(0.25 * wbase, now, TAU_GAIN * 2)
    }
    // 海床群浪呼吸：涌浪底/水声 ±15% 慢摆（R40b）
    if (this.groupDepthBrown && this.brown) {
      this.groupDepthBrown.gain.setTargetAtTime(0.15 * MIX.swell * f.swellGain, now, TAU_GAIN * 2)
    }
    if (this.groupDepthPink && this.pink) {
      this.groupDepthPink.gain.setTargetAtTime(0.15 * MIX.wash * f.swellGain, now, TAU_GAIN * 2)
    }

    // —— 风机声部 ——
    for (let v = 0; v < this.voices.length; v++) {
      const voice = this.voices[v]
      const a = f.voices[v]
      if (!a) {
        if (voice.active) {
          voice.gain.gain.setTargetAtTime(0, now, 0.5)
          voice.active = false
          voice.idx = -1
        }
        continue
      }
      voice.idx = a.idx
      voice.active = true
      voice.panner.positionX.setTargetAtTime(a.x, now, TAU_POS)
      voice.panner.positionY.setTargetAtTime(a.y, now, TAU_POS)
      voice.panner.positionZ.setTargetAtTime(a.z, now, TAU_POS)
      const g = MIX.turbine * Math.min(1, a.gain)
      voice.gain.gain.setTargetAtTime(g, now, TAU_GAIN)
      // 切风中心频率随转速：rpm 高 → 叶片切风更尖（620Hz @6.9rpm → 1050Hz @12.1rpm）
      const rpmN = Math.max(0, Math.min(1, (a.rpm - 6.9) / (12.1 - 6.9)))
      voice.swish.frequency.setTargetAtTime(560 + 520 * rpmN, now, TAU_FILTER)
      voice.swish.Q.setTargetAtTime(0.7 + 0.6 * rpmN, now, TAU_FILTER)
      // 叶片通过包络：频率 = 3×转频，深度随距离收敛（远处只剩平均响度）
      voice.bladeLfo.frequency.setTargetAtTime(Math.max(0.05, a.bladePassHz), now, 0.4)
      voice.bladeDepth.gain.setTargetAtTime(0.12 + 0.34 * Math.min(1, a.gain * 2), now, TAU_GAIN)
      // 空气吸收：7kHz@近塔 → ~0.5kHz@1.5km（远声发闷，R40b）
      voice.air.frequency.setTargetAtTime(400 + 7000 * Math.exp(-a.dist / 900), now, TAU_FILTER)
      // 传动链音调：转频×97（发电机侧）+ 二次谐波；只在近塔可闻
      const ft = Math.max(40, Math.min(1400, a.driveTrainHz))
      voice.tone.frequency.setTargetAtTime(ft, now, TAU_FILTER)
      voice.tone2.frequency.setTargetAtTime(ft * 2, now, TAU_FILTER)
      voice.toneGain.gain.setTargetAtTime(MIX.tone * Math.min(1, a.gain * 2.4), now, TAU_GAIN)
    }
  }

  /**
   * QA 只读探针（scripts/qa_audio.mjs 用）：节点图关键增益的**当前本征值**。
   * R40b 新增：用于机器验证「远距真静音」（surf base=0 / voice gain=0），
   * 不靠人耳听截图。
   */
  probe(): {
    master: number
    beds: { swell: number; wash: number; wind: number; surf: number[] }
    voices: Array<{ idx: number; gain: number; airHz: number }>
  } | null {
    if (!this.ctx) return null
    return {
      master: this.master ? this.master.gain.value : 0,
      beds: {
        swell: this.brown ? this.brown.gain.gain.value : 0,
        wash: this.pink ? this.pink.gain.gain.value : 0,
        wind: this.white ? this.white.gain.gain.value : 0,
        surf: this.surfVoices.map((v) => v.gain.gain.value),
      },
      voices: this.voices.filter((v) => v.active).map((v) => ({
        idx: v.idx, gain: v.gain.gain.value, airHz: v.air.frequency.value,
      })),
    }
  }

  /** 标签页隐藏 / 关闭声音：挂起上下文（省电，且不丢节点图） */
  suspend(): void {
    if (this.ctx && this.ctx.state === 'running') void this.ctx.suspend()
  }

  resume(): void {
    if (this.ctx && this.ctx.state === 'suspended' && !this.muted) void this.ctx.resume()
  }

  dispose(): void {
    const ctx = this.ctx
    this.ctx = null
    this.master = null
    this.voices = []
    this.surfVoices = []
    if (ctx && ctx.state !== 'closed') void ctx.close()
  }
}

/** 全页单例（一个 AudioContext 就够，多了浏览器会限流） */
export const audioEngine = new AudioEngine()
