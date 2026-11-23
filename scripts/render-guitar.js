// Renders the README preview (assets/guitar.webp) from docs/guitar.js in headless Chromium.
//   npm install three@0.160.0 playwright
//   node scripts/render-guitar.js docs node_modules/three frames 80 1200 520 4
//   ffmpeg -framerate 20 -i frames/f%03d.png -vf scale=1000:-1:flags=lanczos -c:v libwebp_anim -quality 85 -loop 0 assets/guitar.webp
// usage: node render3d.js <docsDir> <threeDir> <outPng|outDir> [frames] [w] [h] [T]
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const [docs, three, out, frames = '1', w = '1200', h = '520', T = '4'] = process.argv.slice(2);
const types = { '.js': 'text/javascript', '.html': 'text/html' };
(async () => {
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: +w, height: +h } });
  p.on('console', m => console.log('console:', m.text()));
  p.on('pageerror', e => console.log('pageerror:', e.message));
  await p.route('**/*', (route) => {
    const u = new URL(route.request().url());
    let file;
    if (u.hostname === 'local.test') file = path.join(docs, u.pathname === '/' ? 'index.html' : u.pathname);
    else if (u.hostname === 'cdn.jsdelivr.net') file = path.join(three, u.pathname.replace(/^\/npm\/three@[^/]+\//, ''));
    if (!file || !fs.existsSync(file)) return route.fulfill({ status: 404, body: 'nope ' + u });
    route.fulfill({ status: 200, contentType: types[path.extname(file)] || 'application/octet-stream', body: fs.readFileSync(file) });
  });
  await p.goto(`https://local.test/index.html?render&w=${w}&h=${h}&T=${T}`);
  await p.waitForFunction(() => window.__ready === true, null, { timeout: 60000 });
  const n = +frames;
  if (n === 1) {
    await p.evaluate((t) => window.__frame(t), +(process.env.TIME || 0.55));
    await p.locator('canvas').screenshot({ path: out });
  } else {
    fs.mkdirSync(out, { recursive: true });
    for (let k = 0; k < n; k++) {
      await p.evaluate((t) => window.__frame(t), k * (+T) / n);
      await p.locator('canvas').screenshot({ path: path.join(out, `f${String(k).padStart(3, '0')}.png`) });
    }
  }
  await b.close();
})();
