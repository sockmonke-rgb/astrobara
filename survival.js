"use strict";
/* Astrobara survival bot — plays the shipped build, in the shipped build.
 *
 *   node survival.js index.html [sites] [turns] [baseline.json]
 *
 * The bot runs inside the page and calls the game's own newGame, canPlace,
 * doPlace, setIdle and endTurn. There is no second copy of the rules to drift
 * out of step: if the model changes, this changes with it, which is the whole
 * point of running it on every commit.
 *
 * Rendering is stubbed for the run — draw() and paintUI() are presentation and
 * nothing in a turn depends on them — so a few hundred colonies fit in a CI
 * job rather than an afternoon.
 *
 * Exits non-zero when a rate moves further from the baseline than its
 * tolerance, or when the ladder stops being a ladder.
 */

const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const BUILD = process.argv[2] || 'index.html';
const SITES = Number(process.argv[3] || 240);
const TURNS = Number(process.argv[4] || 290);
const BASELINE = process.argv[5] || 'survival-baseline.json';

/* ---------------------------------------------------------------- the bot */
/* Runs in the page. Everything it calls is the game's own. */
function runSurvey(opts) {
  const { sites, turns } = opts;

  // Presentation only; a turn does not depend on either.
  draw = function () {};
  paintUI = function () {};
  saveWorks = false;

  const DARK = CFG.solLength - CFG.dayLength;

  function forbiddenDigs() {
    const bad = new Set();
    for (let y = 0; y < CFG.rows; y++) for (let x = 0; x < CFG.cols; x++) {
      const t = G.tiles[idx(x, y)];
      if (t.b && t.b.type === 'HAB') for (let k = y - 1; k >= 0; k--) bad.add(idx(x, k));
    }
    return bad;
  }

  function digPath(conn, tx, ty, bad) {
    const prev = new Map(), seen = new Set(), q = [];
    for (const i of conn) { seen.add(i); q.push(i); }
    let head = 0;
    const target = idx(tx, ty);
    if (seen.has(target)) return [];
    while (head < q.length) {
      const cur = q[head++];
      const cx = cur % CFG.cols, cy = (cur - cx) / CFG.cols;
      for (const d of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
        const nx = cx + d[0], ny = cy + d[1];
        if (!inb(nx, ny)) continue;
        const ni = idx(nx, ny);
        if (seen.has(ni) || bad.has(ni)) continue;
        const t = G.tiles[ni];
        if (t.b) continue;
        if (!t.dug && !t.rock) continue;
        seen.add(ni); prev.set(ni, cur);
        if (ni === target) {
          const out = [];
          let p = ni;
          while (prev.has(p)) { out.push(p); p = prev.get(p); }
          return out.reverse()
            .map(i => ({ x: i % CFG.cols, y: (i - i % CFG.cols) / CFG.cols }))
            .filter(c => !G.tiles[idx(c.x, c.y)].dug);
        }
        q.push(ni);
      }
    }
    return null;
  }

  function bestTile(conn, bad, score, costPer) {
    const cp = costPer === undefined ? 0.004 : costPer;
    let tile = null, p2 = null, bestV = 0;
    for (let y = 0; y < CFG.rows; y++) for (let x = 0; x < CFG.cols; x++) {
      const v = score(G.tiles[idx(x, y)], x, y);
      if (v <= 0 || v <= bestV) continue;
      const p = digPath(conn, x, y, bad);
      if (p === null) continue;
      const adj = v - p.length * cp;
      if (adj > bestV) { bestV = adj; tile = { x, y }; p2 = p; }
    }
    return tile ? { tile, path: p2 } : null;
  }

  function avgSolar() {
    const lit = litProfile(G.surf);
    let s = 0;
    for (let x = 0; x < CFG.cols; x++) {
      const t = G.tiles[idx(x, G.surf[x])];
      if (t.b && t.b.type === 'SOLAR') s += CFG.solarPeak * lit[x] / CFG.dayLength;
    }
    return s;
  }

  function industryDraw() {
    let p = 0;
    for (let i = 0; i < G.tiles.length; i++) {
      const b = G.tiles[i].b;
      if (!b) continue;
      if (b.type === 'MINE') p += CFG.minePower;
      else if (b.type === 'PROC') p += CFG.procPower;
    }
    return p;
  }

  function solWant(L) {
    const day = (L.life + L.habs * CFG.habHeatDay + industryDraw()) * CFG.dayLength;
    const night = (L.life + L.habs * CFG.habHeatNight) * DARK;
    return Math.max(0, (day + night - L.fusion * CFG.solLength) / CFG.dayLength);
  }

  function outlook() {
    const t = G.turn % CFG.solLength;
    const night = t >= CFG.dayLength;
    const dayLeft = night ? 0 : CFG.dayLength - t;
    const darkLeft = night ? CFG.solLength - t : DARK;
    const need = nightLoad(G.ledger, false) * darkLeft;
    const proj = Math.min(G.cap, G.power + Math.max(0, G.ledger.net) * dayLeft);
    return { night, dayLeft, darkLeft, need, proj, safe: proj >= need * 1.08 };
  }

  function freeLitCols() {
    const lit = litProfile(G.surf);
    const out = [];
    for (let x = 0; x < CFG.cols; x++) {
      const t = G.tiles[idx(x, G.surf[x])];
      if (t.b || t.dug || lit[x] <= 0) continue;
      out.push({ x, lit: lit[x] });
    }
    out.sort((a, b) => b.lit - a.lit);
    return out;
  }

  function dimArray() {
    const lit = litProfile(G.surf);
    let worst = null, worstLit = CFG.dayLength * 0.5;
    for (let x = 0; x < CFG.cols; x++) {
      const t = G.tiles[idx(x, G.surf[x])];
      if (!t.b || t.b.type !== 'SOLAR') continue;
      if (lit[x] < worstLit) { worstLit = lit[x]; worst = { x, y: G.surf[x] }; }
    }
    return worst;
  }

  function manageIndustry(st) {
    setIdle(['MINE', 'PROC'], false);
    let o = outlook();
    if (!o.safe || G.ledger.net < 0) { setIdle(['PROC'], true); o = outlook(); }
    if (!o.safe || G.ledger.net < 0) {
      const L = G.ledger;
      const dryIfIdled = G.water < L.waterOut * o.darkLeft;
      const canCarry = G.power >= o.need + L.mining * o.darkLeft;
      if (!(dryIfIdled && canCarry)) setIdle(['MINE'], true);
    }
    if (!st.wallowOff && G.water < 25) st.wallowOff = true;
    else if (st.wallowOff && G.water > 70) st.wallowOff = false;
    setIdle(['WALLOW'], st.wallowOff);
  }

  function plan(st) {
    const conn = connectedSet();
    const bad = forbiddenDigs();
    const L = G.ledger;
    const acts = [];
    const push = (type, x, y, pri) => acts.push({ type, x, y, pri });

    const o = outlook();
    const shortSolar = avgSolar() < solWant(L) * 1.25;
    const dryIn = L.waterNet < 0 ? G.water / -L.waterNet : 999;
    const hasFusion = G.tiles.some(t => t.b && t.b.type === 'FUSION');
    const secure = o.safe && L.mines >= 1 && dryIn > 25;

    if (shortSolar) {
      const cols = freeLitCols();
      if (cols.length) push('SOLAR', cols[0].x, G.surf[cols[0].x], 100);
      const dim = dimArray();
      if (dim && avgSolar() > 0 && G.power < COST.SOLAR.p * 2) push('CLEAR', dim.x, dim.y, 99);
    }

    if (G.cap < o.need * 1.12 && !o.night) {
      const spot = bestTile(conn, bad, (t, x, y) => t.dug && !t.b && conn.has(idx(x, y)) ? 1 : 0);
      if (spot && spot.path.length === 0) push('BATTERY', spot.tile.x, spot.tile.y, 90);
    }

    if (L.mines < 1 || (L.waterNet < 3 && L.mines < 10 && secure)) {
      const target = bestTile(conn, bad, t => t.b ? 0 : t.ice, 0.006);
      if (target) {
        const urgent = L.mines < 1 && dryIn < target.path.length + 4;
        const pri = urgent ? 105 : (L.mines < 1 ? 95 : 70);
        if (target.path.length === 0) push('MINE', target.tile.x, target.tile.y, pri);
        else push('DIG', target.path[0].x, target.path[0].y, pri - 1);
      }
    }

    if (!hasFusion && G.he3 >= COST.FUSION.h) {
      const spot = bestTile(conn, bad, (t, x, y) => t.dug && !t.b && conn.has(idx(x, y)) ? 1 : 0);
      if (spot && spot.path.length === 0) push('FUSION', spot.tile.x, spot.tile.y, 97);
    }

    if (!secure) { acts.sort((a, b) => b.pri - a.pri); return acts; }

    if (L.procs < 3 && !shortSolar) {
      const target = bestTile(conn, bad,
        (t, x, y) => (t.b || (y - G.surf[x]) > 3) ? 0 : t.he3, 0.006);
      if (target) {
        if (target.path.length === 0) push('PROC', target.tile.x, target.tile.y, 65);
        else push('DIG', target.path[0].x, target.path[0].y, 64);
      }
    }

    const wantWallows = Math.max(1, Math.ceil(G.crew / CFG.wallowPerCrew));
    if (L.wallows < wantWallows && G.water > COST.WALLOW.w + CFG.growthWater) {
      const spot = bestTile(conn, bad,
        (t, x, y) => t.dug && !t.b && conn.has(idx(x, y)) && adjacentHab(x, y, conn) ? 1 : 0);
      if (spot && spot.path.length === 0) {
        push('WALLOW', spot.tile.x, spot.tile.y, L.wallows === 0 ? 75 : 45);
      } else {
        const nb = bestTile(conn, bad, (t, x, y) => {
          if (t.dug || t.b) return 0;
          for (const d of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
            const hx = x + d[0], hy = y + d[1];
            if (!inb(hx, hy)) continue;
            const h = G.tiles[idx(hx, hy)];
            if (h.b && h.b.type === 'HAB' && conn.has(idx(hx, hy))) return 1;
          }
          return 0;
        });
        if (nb && nb.path.length) push('DIG', nb.path[0].x, nb.path[0].y, L.wallows === 0 ? 74 : 44);
      }
    }

    if (G.crew >= L.habs * CFG.habCap && L.habs < 14 && st.nightsHeld >= 1) {
      const spot = bestTile(conn, bad, (t, x, y) =>
        t.dug && !t.b && conn.has(idx(x, y)) && overburden(x, y) >= CFG.minOverburden ? 1 : 0);
      if (spot && spot.path.length === 0) push('HAB', spot.tile.x, spot.tile.y, 60);
      else {
        const deep = bestTile(conn, bad, (t, x, y) =>
          !t.dug && !t.b && (y - G.surf[x]) >= CFG.minOverburden ? 1 : 0);
        if (deep && deep.path.length) push('DIG', deep.path[0].x, deep.path[0].y, 59);
      }
    }

    acts.sort((a, b) => b.pri - a.pri);
    return acts;
  }

  function affordable(a) {
    const c = COST[a.type];
    if (c.p <= 0) return true;
    const o = outlook();
    const L = G.ledger;
    if (a.type === 'DIG') return G.power - c.p >= (o.night ? o.need * 0.55 : 0);
    if (a.type === 'SOLAR') {
      const lit = litProfile(G.surf);
      const payback = CFG.solarPeak * (lit[a.x] / CFG.dayLength) * Math.max(o.dayLeft, 0);
      if (o.night) return G.power - c.p >= o.need;
      return payback >= c.p || o.safe;
    }
    if (a.type === 'BATTERY') {
      if (o.night) return G.power - c.p >= o.need;
      return G.power - c.p >= 0;
    }
    if (a.type === 'MINE') {
      const dryIn = L.waterNet < 0 ? G.water / -L.waterNet : 999;
      if (L.mines < 1 && dryIn < o.darkLeft + o.dayLeft + 8)
        return G.power - c.p >= (o.night ? o.need * 0.6 : 0);
    }
    const addNight = a.type === 'HAB' ? CFG.habHeatNight
      : a.type === 'FUSION' ? -CFG.fusionPower : 0;
    const need = Math.max(0, nightLoad(L, false) + addNight) * o.darkLeft;
    const after = Math.min(G.cap, G.power - c.p + Math.max(0, L.net) * o.dayLeft);
    return after >= need * 1.18;
  }

  function playTurn(st) {
    manageIndustry(st);
    let guard = 0;
    const done = {};
    while (G.labor > 0 && guard++ < 30) {
      const acts = plan(st);
      for (const a of acts) a.pri -= (done[a.type] || 0) * 9;
      acts.sort((a, b) => b.pri - a.pri);
      let did = false;
      for (const a of acts) {
        if (G.labor < COST[a.type].l) continue;
        if (!affordable(a)) continue;
        if (canPlace(a.x, a.y, a.type)) continue;
        doPlace(a.x, a.y, a.type);
        done[a.type] = (done[a.type] || 0) + 1;
        did = true;
        break;
      }
      if (!did) break;
    }
    const wasNight = isNight(G.turn);
    endTurn();
    if (!isNight(G.turn) && wasNight) st.nightsHeld++;
    if (G.won) {           // keep the colony running past self-sufficiency
      st.selfSufficient = true;
      G.won = false;
      const over = document.getElementById('over');
      if (over) over.style.display = 'none';
      if (typeof endOverIntro === 'function') endOverIntro();
    }
  }

  // ---- the survey ----
  const rows = {};
  const bucket = s => (rows[s] = rows[s] ||
    { n: 0, survived: 0, ss: 0, crew: 0, peak: 0, morale: 0, floor: 0, brown: 0 });

  let seed = 0, done = 0;
  while (done < sites) {
    const probe = generateSite(seed);
    seed++;
    if (!probe || !probe.ok) continue;
    done++;
    newGame(probe.seed);
    const st = { nightsHeld: 0, wallowOff: false, selfSufficient: false };
    while (!G.dead && G.turn < turns) playTurn(st);
    const b = bucket(G.site.stars);
    b.n++;
    if (!G.dead) b.survived++;
    if (G.selfSufficient || st.selfSufficient) b.ss++;
    b.crew += G.crew; b.peak += G.peakCrew;
    b.morale += G.morale; b.floor += G.moraleFloor;
    if (G.everBrownout) b.brown++;
  }
  return { rows, build: BUILD, sites: done };
}

/* ------------------------------------------------------------------ main */
(async () => {
  const buildPath = path.resolve(BUILD);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 900, height: 420 } });
  const errs = [];
  page.on('pageerror', e => errs.push(e.message));
  await page.goto('file://' + buildPath);
  await page.waitForTimeout(500);
  await page.evaluate(() => { const b = document.getElementById('begin'); if (b) b.click(); });

  const t0 = Date.now();
  const res = await page.evaluate(runSurvey, { sites: SITES, turns: TURNS });
  const secs = ((Date.now() - t0) / 1000).toFixed(1);
  const build = await page.evaluate(() => BUILD);
  await browser.close();

  if (errs.length) {
    console.error('page errors during the survey:\n  ' + errs.join('\n  '));
    process.exit(1);
  }

  const pct = (a, b) => b ? 100 * a / b : 0;
  const stats = {};
  const total = { n: 0, survived: 0, ss: 0, crew: 0, peak: 0, morale: 0, floor: 0, brown: 0 };
  for (const s of [1, 2, 3, 4, 5]) {
    const b = res.rows[s];
    if (!b) continue;
    stats[s] = {
      n: b.n,
      survived: +pct(b.survived, b.n).toFixed(1),
      ss: +pct(b.ss, b.n).toFixed(1),
      peak: +(b.peak / b.n).toFixed(1),
      morale: +(b.morale / b.n).toFixed(1)
    };
    for (const k in total) total[k] += b[k];
  }
  stats.all = {
    n: total.n,
    survived: +pct(total.survived, total.n).toFixed(1),
    ss: +pct(total.ss, total.n).toFixed(1),
    peak: +(total.peak / total.n).toFixed(1),
    morale: +(total.morale / total.n).toFixed(1)
  };

  console.log('ASTROBARA survival bot · ' + build + ' · ' + res.sites +
    ' sites · ' + TURNS + ' turns · ' + secs + 's\n');
  console.log('  star      n   survived      s-s   peak crew   mean morale');
  for (const k of [1, 2, 3, 4, 5, 'all']) {
    const r = stats[k];
    if (!r) continue;
    console.log('  ' + String(k === 'all' ? 'all' : k + '*').padEnd(5) +
      String(r.n).padStart(5) + String(r.survived).padStart(10) + '%' +
      String(r.ss).padStart(8) + '%' + String(r.peak).padStart(11) +
      String(r.morale).padStart(14));
  }

  let bad = 0;
  const fail = m => { bad++; console.log('\n  FAIL  ' + m); };

  // The ladder must stay a ladder. Pooled either side of the middle and gated
  // on sample size: a single band can hold five colonies in a short run, and
  // five colonies say nothing about difficulty.
  const pool = ks => {
    let n = 0, s = 0;
    for (const k of ks) if (stats[k]) { n += stats[k].n; s += stats[k].survived * stats[k].n; }
    return { n, rate: n ? s / n : 0 };
  };
  const easy = pool([1, 2]), hard = pool([4, 5]);
  if (easy.n >= 30 && hard.n >= 30) {
    if (easy.rate < hard.rate - 5)
      fail('1–2 star survival (' + easy.rate.toFixed(1) + '%, n=' + easy.n +
        ') is below 4–5 star (' + hard.rate.toFixed(1) + '%, n=' + hard.n +
        ') — the difficulty ordering has inverted');
  } else {
    console.log('\n  ladder check skipped — needs 30 sites either side, has ' +
      easy.n + ' and ' + hard.n);
  }

  // And against the last agreed numbers, if there are any.
  const basePath = path.resolve(BASELINE);
  if (fs.existsSync(basePath)) {
    const base = JSON.parse(fs.readFileSync(basePath, 'utf8'));
    const TOL = base.tolerance || 8;
    console.log('\n  against ' + path.basename(basePath) +
      ' (' + base.build + ', tolerance ' + TOL + ' points)');
    for (const k of ['all', 1, 2, 3, 4, 5]) {
      if (!base.stats[k] || !stats[k]) continue;
      for (const metric of ['survived', 'ss']) {
        const d = stats[k][metric] - base.stats[k][metric];
        if (Math.abs(d) > TOL)
          fail(k + ' ' + metric + ': ' + base.stats[k][metric] + '% -> ' +
            stats[k][metric] + '% (' + (d > 0 ? '+' : '') + d.toFixed(1) + ')');
      }
    }
  } else {
    console.log('\n  no baseline at ' + basePath + ' — writing one');
    fs.writeFileSync(basePath, JSON.stringify(
      { build, sites: res.sites, turns: TURNS, tolerance: 8, stats }, null, 2) + '\n');
  }

  console.log('\n' + (bad ? bad + ' regression(s)' : 'within tolerance'));
  process.exit(bad ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
