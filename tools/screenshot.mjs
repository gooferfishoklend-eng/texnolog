// Снимок 3D-вида: node tools/screenshot.mjs <viewer.html> <out.png> ["&az=..&el=..&d=.."]
// Путь к Chromium поправьте под свою систему (executablePath).
import { chromium } from 'playwright-core';
const [,, html, png, query=''] = process.argv;
const b = await chromium.launch({executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const p = await b.newPage({viewport:{width:1600,height:1000}});
p.on('console', m => console.log('console:', m.text()));
p.on('pageerror', e => console.log('err:', e.message));
await p.goto('file://' + html + '?noui=1' + query);
await p.waitForFunction(() => window.__ready, null, {timeout: 120000});
await p.waitForTimeout(500);
await p.screenshot({path: png});
await b.close();
