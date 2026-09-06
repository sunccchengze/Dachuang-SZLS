// sunprobe.mjs — 日轮活体探针：真实相机投影太阳屏幕坐标 + 天空球 uniform 快照
import puppeteer from 'puppeteer-core'
import chromium from '@sparticuz/chromium'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const here = path.dirname(fileURLToPath(import.meta.url))
const repoLibs = path.join(here, '..', 'nsslibs')
const url = process.argv[2]
const out = process.argv[3] || '/tmp/sunprobe.png'
const waitMs = Number(process.argv[4] || 12000)

const browser = await puppeteer.launch({
  executablePath: await chromium.executablePath(),
  env: { ...process.env, LD_LIBRARY_PATH: repoLibs + ':/tmp/nsslibs' },
  args: [...chromium.args, '--no-sandbox', '--disable-gpu-sandbox', '--enable-unsafe-swiftshader'],
  defaultViewport: { width: 1920, height: 1080, deviceScaleFactor: 1 },
  headless: 'shell',
})
const page = await browser.newPage()
await page.goto(url, { waitUntil: 'load', timeout: 60000 })
await new Promise((r) => setTimeout(r, waitMs))
const probe = await page.evaluate(() => {
  const w = window
  const cam = w.__aeolus_cam
  if (!cam) return { err: 'no __aeolus_cam' }
  // dayNight 同式：太阳方向
  const t = w.__aeolus?.useSim?.getState?.()?.tHours ?? null
  const th = ((t - 5.4) / 24) * Math.PI * 2
  const elD = 54 * Math.sin(th)
  const el = (elD * Math.PI) / 180
  const az = ((90 + 180 * (th / Math.PI)) * Math.PI) / 180
  const sd = [Math.sin(az) * Math.cos(el), Math.sin(el), -Math.cos(az) * Math.cos(el)]
  // 投影到屏幕
  const v = cam.position.clone(); v.x += sd[0] * 1e7; v.y += sd[1] * 1e7; v.z += sd[2] * 1e7
  v.project(cam)
  const px = (v.x + 1) / 2 * innerWidth
  const py = (1 - v.y) / 2 * innerHeight
  // 找天空球（半径 6800 的球）读 uniform
  let sky = null
  const scene = w.__aeolus_scene
  scene?.traverse?.((o) => {
    if (sky || !o.geometry?.parameters) return
    if (o.geometry.parameters.radius === 6800) {
      const u = o.material?.uniforms ?? {}
      sky = {
        uSunDir: u.uSunDir?.value?.toArray?.().map((x) => +x.toFixed(4)),
        uWarmF: u.uWarmF?.value,
        uDay: u.uDay?.value,
        visible: o.visible,
        camPos: w.__aeolus_cam?.position?.toArray?.().map((x) => +x.toFixed(1)),
      }
    }
  })
  return { t, elD, sd: sd.map((x) => +x.toFixed(4)), px: +px.toFixed(1), py: +py.toFixed(1), sky }
})
console.log(JSON.stringify(probe, null, 2))
await page.screenshot({ path: out })
console.log('shot', out)
await browser.close()
