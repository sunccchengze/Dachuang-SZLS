// perfstats.mjs — 单帧渲染计数（draw calls / 三角面 / 几何）+ 实例树落位耗时
// 用法: node scripts/perfstats.mjs [url]
import puppeteer from 'puppeteer-core'
import chromium from '@sparticuz/chromium'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const here = path.dirname(fileURLToPath(import.meta.url))
const repoLibs = path.join(here, '..', 'nsslibs')
const url = process.argv[2] || 'http://127.0.0.1:5173/?debug=1&q=high&cam=60,22,990&t=15'

const browser = await puppeteer.launch({
  executablePath: await chromium.executablePath(),
  env: { ...process.env, LD_LIBRARY_PATH: repoLibs + ':/tmp/nsslibs' },
  args: [...chromium.args, '--no-sandbox', '--disable-gpu-sandbox', '--enable-unsafe-swiftshader'],
  defaultViewport: { width: 1280, height: 720, deviceScaleFactor: 1 },
  headless: 'shell',
})
const page = await browser.newPage()
const errs = []
page.on('pageerror', (e) => errs.push(String(e).slice(0, 200)))
await page.goto(url, { waitUntil: 'load', timeout: 60000 })
await new Promise((r) => setTimeout(r, 20000))
const stats = await page.evaluate(() => {
  const w = window
  const out = { quality: null, stats: null }
  try { out.quality = w.__aeolus?.sim?.getState?.()?.quality ?? null } catch { /* noop */ }
  if (typeof w.__aeolus_stats === 'function') out.stats = w.__aeolus_stats()
  return out
})
console.log(JSON.stringify({ quality: stats.quality, ...stats.stats, pageErrors: errs }, null, 2))
await browser.close()
