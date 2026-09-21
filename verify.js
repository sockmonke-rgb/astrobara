"use strict";
/* Astrobara build verification — runs the real file in Chromium.
 *
 *   node verify.js <build.html> <SEEDS.txt> [outdir]
 *
 * P1  the script parses and the page raises no errors
 * P2  header comment, meta description and const BUILD agree
 * P3  no duplicate element ids
 * P4  every getElementById target exists
 * P6  only the three storage keys
 * P7  no network of any kind
 * P8  every font-size resolves through a scale variable
 * P9  every touch-action names pinch-zoom or is a drag grip
 * P10 achievement table integrity
 * P11 every code in SEEDS.txt regenerates its site and rating
 * P12 CSS braces balance
 *
 * Then the thing hex values cannot settle: the tunnel tones are read back off
 * the rendered canvas and compared with the rock beside them, at every depth,
 * lit and unlit.
 */

const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const BUILD_PATH = process.argv[2];
const SEEDS_PATH = process.argv[3];
const OUT = process.argv[4] || '/home/claude/verify-out';

if (!BUILD_PATH || !SEEDS_PATH) {
  console.error('usage: node verify.js <build.html> <SEEDS.txt> [outdir]');
  process.exit(2);
}
fs.mkdirSync(OUT, { recursive: true });

const src = fs.readFileSync(BUILD_PATH, 'utf8');
let fails = 0;
function check(id, ok, evidence) {
  if (!ok) fails++;
  console.log((ok ? '  ok   ' : '  FAIL ') + id.padEnd(5) + evidence);
}

/* ---------------- static checks ---------------- */

function staticChecks() {
  // P2
  const header = (src.match(/ASTROBARA (V[\w.\-]+)/) || [])[1];
  const meta = (src.match(/content="Astrobara (V[\w.\-]+)/) || [])[1];
  const konst = (src.match(/const BUILD = '([^']+)'/) || [])[1];
  check('P2', header && header === meta && meta === konst,
    'header ' + header + ' · meta ' + meta + ' · const ' + konst);

  // P3
  const ids = [...src.matchAll(/\sid="([^"]+)"/g)].map(m => m[1]);
  const uniq = new Set(ids);
  check('P3', uniq.size === ids.length,
    ids.length + ' ids, ' + uniq.size + ' unique');

  // P4
  const targets = [...src.matchAll(/getElementById\(['"]([^'"]+)['"]\)/g)].map(m => m[1]);
  const missing = [...new Set(targets)].filter(t => !uniq.has(t));
  check('P4', missing.length === 0,
    new Set(targets).size + ' targets, missing: ' + (missing.join(', ') || 'none'));

  // P6
  const keys = [...new Set([...src.matchAll(/['"]astrobara\.(\w+)['"]/g)].map(m => m[1]))].sort();
  check('P6', keys.join(',') === 'achv,board,run', 'keys: ' + keys.join(' '));

  // P7
  const net = [];
  if (/\bfetch\s*\(/.test(src)) net.push('fetch');
  if (/XMLHttpRequest/.test(src)) net.push('XMLHttpRequest');
  if (/src\s*=\s*["']https?:/i.test(src)) net.push('remote src');
  if (/@import/.test(src)) net.push('@import');
  if (/href\s*=\s*["']https?:/i.test(src)) net.push('remote href');
  check('P7', net.length === 0, net.length ? net.join(', ') : 'no network references');

  // P8 — every font-size in the stylesheet routes through a scale variable
  const style = (src.match(/<style>([\s\S]*?)<\/style>/) || [])[1] || '';
  const sizes = [...style.matchAll(/font-size\s*:\s*([^;}]+)[;}]/g)].map(m => m[1].trim());
  const bare = sizes.filter(v => !/var\(--ts[bgw]?\)/.test(v) && !/inherit|100%|-apple-system-body/.test(v));
  check('P8', bare.length === 0,
    sizes.length + ' font sizes, unscaled: ' + (bare.join(' | ') || 'none'));

  // P9
  const ta = [...src.matchAll(/touch-action\s*:\s*([^;}'"]+)/g)].map(m => m[1].trim());
  const badTa = ta.filter(v => !/pinch-zoom/.test(v) && !/^none$/.test(v) && !/^auto$/.test(v));
  check('P9', badTa.length === 0,
    ta.length + ' declarations, unjustified: ' + (badTa.join(' | ') || 'none'));

  // P10
  const declared = [...src.matchAll(/\{id:'([a-z_]+)',\s*n:'([^']+)'/g)].map(m => ({ id: m[1], n: m[2] }));
  const awarded = [...new Set([...src.matchAll(/award\('([a-z_]+)'\)/g)].map(m => m[1]))];
  const dIds = declared.map(d => d.id);
  const dNames = declared.map(d => d.n);
  const notAwarded = dIds.filter(i => !awarded.includes(i));
  const undeclared = awarded.filter(i => !dIds.includes(i));
  check('P10',
    new Set(dIds).size === dIds.length &&
    new Set(dNames).size === dNames.length &&
    notAwarded.length === 0 && undeclared.length === 0,
    declared.length + ' achievements, ' + awarded.length + ' awarded' +
    (notAwarded.length ? ', never awarded: ' + notAwarded.join(',') : '') +
    (undeclared.length ? ', undeclared: ' + undeclared.join(',') : ''));

  // P12
  const open = (style.match(/\{/g) || []).length, close = (style.match(/\}/g) || []).length;
  check('P12', open === close, open + ' open, ' + close + ' close');
}

/* ---------------- SEEDS.txt expectations ---------------- */

function parseSeeds(text) {
  const out = [];
  const lines = text.split('\n');
  let stars = null;
  for (const line of lines) {
    const band = line.match(/^(\d) STAR/);
    if (band) { stars = Number(band[1]); continue; }
    const code = line.match(/^\s{2}([A-Z]+-[A-Z]+-\d+)\s*$/);
    if (code && stars) out.push({ code: code[1], stars });
  }
  return out;
}

/* ---------------- the page ---------------- */

(async () => {
  console.log('ASTROBARA verification · ' + path.basename(BUILD_PATH) + '\n');
  console.log('Tier 0 — static');
  staticChecks();

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 900, height: 420 }, deviceScaleFactor: 2 });

  const errors = [];
  page.on('pageerror', e => errors.push('pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
  page.on('request', r => {
    if (!r.url().startsWith('file://') && !r.url().startsWith('data:')) errors.push('network: ' + r.url());
  });

  await page.goto('file://' + path.resolve(BUILD_PATH));
  await page.waitForTimeout(600);
  await page.evaluate(() => { const b = document.getElementById('begin'); if (b) b.click(); });
  await page.waitForTimeout(400);

  console.log('\nTier 0 — in the page');
  check('P1', errors.length === 0, errors.length ? errors.join(' | ') : 'parsed, no page errors');

  // P11
  const expect = parseSeeds(fs.readFileSync(SEEDS_PATH, 'utf8'));
  const got = await page.evaluate((codes) => codes.map(c => {
    const seed = codeToSeed(c);
    const s = generateSite(seed);
    return { code: c, back: s && s.code, stars: s && s.difficulty && s.difficulty.stars };
  }), expect.map(e => e.code));
  const bad = [];
  expect.forEach((e, i) => {
    const g = got[i];
    if (g.back !== e.code || g.stars !== e.stars) bad.push(e.code + ' -> ' + g.back + ' ' + g.stars + '*');
  });
  check('P11', bad.length === 0,
    expect.length + ' codes, wrong: ' + (bad.join('; ') || 'none'));

  /* ------------- rendered contrast ------------- */
  console.log('\nTunnel contrast, read off the rendered canvas');

  const probe = await page.evaluate(() => {
    // A column of open ground from the surface to the floor, beside untouched
    // rock, so every depth band has a tunnel next to it.
    const x = 6;
    const top = G.surf[x];
    for (let y = top; y < CFG.rows; y++) { const t = G.tiles[idx(x, y)]; t.dug = true; t.rock = false; }
    // Zoom in so a tile is comfortably bigger than the sampling window.
    zoom = 1; panX = 0; panY = 0;
    baseCell = 28; cell = 28;
    offX = 20; offY = 10;

    function sample(night, fusion) {
      G.turn = night ? 20 : 4;
      // A lit reactor, if asked for, so the warm tunnel tone is exercised.
      for (let i = 0; i < G.tiles.length; i++) {
        const b = G.tiles[i].b;
        if (b && b.type === 'FUSION') b.off = true;
      }
      if (fusion) {
        const fy = G.hy;
        G.tiles[idx(G.sx + 1, fy)].b = { type: 'FUSION' };
        G.he3 = 200;
      }
      recompute();
      draw();
      const c = document.getElementById('cv');
      const g = c.getContext('2d');
      const dpr = c.width / stageW;
      const read = (cx, cy) => {
        const d = g.getImageData(Math.round(cx * dpr), Math.round(cy * dpr), 1, 1).data;
        return [d[0], d[1], d[2]];
      };
      const luma = p => 0.2126 * p[0] + 0.7152 * p[1] + 0.0722 * p[2];
      const rows = [];
      for (let y = G.surf[x] + 1; y < CFG.rows; y++) {
        // Middle of the tile vertically, avoiding the roof highlight and the
        // dark floor band the renderer draws inside every tunnel.
        const ty = offY + y * cell + cell * 0.45;
        const tun = read(offX + x * cell + cell * 0.5, ty);
        const rock = read(offX + (x + 2) * cell + cell * 0.5, ty);
        rows.push({
          depth: y - G.surf[x],
          tunnel: tun, rock: rock,
          sep: Math.abs(luma(tun) - luma(rock))
        });
      }
      return rows;
    }
    return { unlit: sample(false, false), night: sample(true, false), fusion: sample(true, true) };
  });

  for (const [name, rows] of Object.entries(probe)) {
    let worst = Infinity, at = null;
    for (const r of rows) if (r.sep < worst) { worst = r.sep; at = r; }
    const ok = worst >= 12;
    check(name.toUpperCase().slice(0, 5), ok,
      'closest at depth ' + at.depth +
      ': tunnel rgb(' + at.tunnel.join(',') + ') vs rock rgb(' + at.rock.join(',') + ')' +
      ' — separation ' + worst.toFixed(1));
  }

  await page.screenshot({ path: path.join(OUT, 'map.png'), clip: { x: 0, y: 0, width: 900, height: 420 } });
  console.log('\nscreenshot: ' + path.join(OUT, 'map.png'));

  await browser.close();
  console.log('\n' + (fails ? fails + ' CHECK(S) FAILED' : 'all checks passed'));
  process.exit(fails ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
