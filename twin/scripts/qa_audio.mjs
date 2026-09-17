import puppeteer from 'puppeteer-core'
import chromium from '@sparticuz/chromium'
const browser = await puppeteer.launch({
  executablePath: await chromium.executablePath(),
  env: { ...process.env, LD_LIBRARY_PATH: '/tmp/nsslibs' },
  args: [...chromium.args, '--no-sandbox', '--disable-gpu-sandbox', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'],
  defaultViewport: { width: 1280, height: 720, deviceScaleFactor: 1 },
  headless: 'shell',
})
const page = await browser.newPage()
const errs = []
page.on('pageerror', (e) => errs.push(String(e).slice(0, 200)))
await page.goto('http://127.0.0.1:5173/?debug=1&q=medium&intro0&cam=141.8,4.5,120,450,19,-2590', { waitUntil: 'load', timeout: 90000 })
await new Promise((r) => setTimeout(r, 9000))
// 1) 未开声：引擎未创建 AudioContext
const pre = await page.evaluate(() => ({ state: window.__aeolus.audio.state, on: window.__aeolus.useSim.getState().audioOn }))
// 2) 真点击声音按钮（用户手势）
await page.click('.topbar .sound button')
await new Promise((r) => setTimeout(r, 2500))
const post = await page.evaluate(() => {
  const a = window.__aeolus.audio
  const f = a.frame
  return {
    state: a.state, on: window.__aeolus.useSim.getState().audioOn,
    shore: f ? +f.shore.toFixed(1) : null, swell: f ? +f.swellGain.toFixed(3) : null,
    surf: f ? +f.surfGain.toFixed(3) : null, wind: f ? +f.windGain.toFixed(3) : null,
    voices: f ? f.voices.map((v) => `${v.idx}:${v.gain.toFixed(3)}`) : null,
    period: f ? +f.swellPeriod.toFixed(1) : null,
  }
})
// 3) 陆上机位：碎浪应 ≈0（离岸 >600m），涌浪底噪 <1；再切到海岸机位看碎浪起来
// 贴岸口径用纯函数复核（相机运行时瞬移不支持；岸距门控单调性两头都要实测到）
const shore2 = await page.evaluate(async () => {
  const m = await import('/src/audio/audioModel.ts')
  const f = m.acousticFrame({ lx: -780, ly: 6, lz: -2260, fx: 0, fy: 0, fz: 1, ux: 0, uy: 1, uz: 0, tHours: 9, t: 30, windSpeed: 9, windFromDeg: 4, units: [] })
  return { shore: +f.shore.toFixed(1), surf: +f.surfGain.toFixed(3), swell: +f.swellGain.toFixed(3) }
})
// 4) 偏航执行器：下指令 30°，3s 后实际角应 ≈0.9°（0.3°/s）且 slewing
await page.evaluate(() => window.__aeolus.useSim.getState().setUnitYaw(0, 30))
await new Promise((r) => setTimeout(r, 4000))
const yaw = await page.evaluate(() => {
  const st = window.__aeolus.useSim.getState().yawBank.states[0]
  return { cmd: st.cmd, actual: +st.actual.toFixed(2), rate: +st.rate.toFixed(3), slewing: st.slewing, act: window.__aeolus.useSim.getState().actYaw[0] }
})
// 5) M 键静音往返
await page.keyboard.press('KeyM')
await new Promise((r) => setTimeout(r, 400))
const muted = await page.evaluate(() => ({ on: window.__aeolus.useSim.getState().audioOn, state: window.__aeolus.audio.state }))
console.log('PRE ', JSON.stringify(pre))
console.log('POST', JSON.stringify(post))
console.log('SHORE-BEACH', JSON.stringify(shore2))
console.log('YAW-4s', JSON.stringify(yaw))
console.log('AFTER-M', JSON.stringify(muted))
console.log('ERRS', errs.slice(0, 5))
await browser.close()
