// R40b 取证：节点图级「远距真静音」验证（不靠人耳）：
//   A 海滩近岸：碎浪 base>0 + 风机声部在
//   B 内陆 3km 山头：碎浪 base=0、涌浪床 ≤0.02、风机声部 0
//   C 外海 6km：碎浪 0、涌浪床满、风机声部 0（过可闻地平线）
import puppeteer from 'puppeteer-core'
import chromium from '@sparticuz/chromium'
const browser = await puppeteer.launch({
  executablePath: await chromium.executablePath(),
  env: { ...process.env, LD_LIBRARY_PATH: '/tmp/nsslibs' },
  args: [...chromium.args, '--no-sandbox', '--disable-gpu-sandbox', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'],
  defaultViewport: { width: 960, height: 540, deviceScaleFactor: 1 }, headless: 'shell',
})
const POSES = [
  ['A-beach', 'http://127.0.0.1:5173/?debug=1&q=low&intro0&cam=78,3.1,-90,-470,25,-2260'],
  ['B-inland3km', 'http://127.0.0.1:5173/?debug=1&q=low&intro0&cam=2450,320,2350,-560,25,-2190'],
  ['C-sea6km', 'http://127.0.0.1:5173/?debug=1&q=low&intro0&cam=20,18,3900,-560,25,-2190'],
]
for (const [name, url] of POSES) {
  const page = await browser.newPage()
  await page.goto(url, { waitUntil: 'load', timeout: 90000 })
  await new Promise((r) => setTimeout(r, 9000))
  await page.click('.topbar .sound button')
  await new Promise((r) => setTimeout(r, 3000))
  const out = await page.evaluate(() => {
    const p = window.__aeolus.audio.probe()
    const f = window.__aeolus.audio.frame
    return {
      shore: Math.round(f.shore), surfModel: +f.surfGain.toFixed(3),
      swellModel: +f.swellGain.toFixed(3), voicesModel: f.voices.length,
      surfNodes: p.beds.surf.map((v) => +v.toFixed(4)),
      swellNode: +p.beds.swell.toFixed(4), windNode: +p.beds.wind.toFixed(4),
      voiceNodes: p.voices.map((v) => `${v.idx}:${v.gain.toFixed(4)}@${Math.round(v.airHz)}Hz`),
    }
  })
  console.log(name, JSON.stringify(out))
  await page.close()
}
await browser.close()
