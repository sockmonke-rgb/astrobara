/* Replay the opening on a colony that is already standing, and check that it
   gives everything back. The bug this exists for: endCine() wrote G.turn = 0,
   so a replay on sol 25 put the colony on sol 1 and the next save wrote it.

   Usage:  node cine-check.js <build.html> */

const { chromium } = require('playwright');
const path = require('path');

const file = process.argv[2] || 'astrobara-v2_12_1.html';

function snap() {
  // Runs in the page.
  const dug = [], built = [];
  for (let i = 0; i < G.tiles.length; i++) {
    const t = G.tiles[i];
    if (t.dug) dug.push(i);
    if (t.b) built.push(i + ':' + t.b.type);
  }
  return {
    turn: G.turn, crew: G.crew, power: G.power, water: G.water,
    he3: G.he3, morale: G.morale, seed: G.seed,
    dug: dug.join(','), built: built.join(','),
    birth: (G.birth || []).length
  };
}

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 402, height: 708 }, deviceScaleFactor: 3 });
  const errs = [];
  page.on('pageerror', e => errs.push(String(e)));
  page.on('console', m => { if (m.type() === 'error') errs.push('console: ' + m.text()); });

  await page.goto('file://' + path.resolve(file));
  await page.waitForFunction(() => typeof G !== 'undefined' && !!G && typeof startCine === 'function');
  await page.evaluate(() => { saveWorks = false; });

  // A colony with history on it. Playing 700 turns needs a bot; what this
  // test needs is only the *shape* of a late colony — a turn number well past
  // zero, and ground that newGame() did not lay — so it is set directly.
  // A rewind to birth would strip the extra tiles and reset the turn, which
  // is exactly what is being checked for.
  const state = await page.evaluate(`(() => {
    OPT.cine = false;
    newGame(922881);
    const hab = G.tiles.findIndex(t => t.b && t.b.type === 'HAB');
    const hx = hab % CFG.cols, hy = Math.floor(hab / CFG.cols);
    // A drift out from the habitat, and a couple of things at the end of it.
    for (let d = 1; d <= 6; d++) {
      const t = G.tiles[idx(hx + d, hy)];
      if (t) { t.dug = true; t.rock = false; }
    }
    const a = G.tiles[idx(hx + 5, hy)], b2 = G.tiles[idx(hx + 6, hy)];
    if (a) a.b = { type: 'MINE' };
    if (b2) b2.b = { type: 'TANK' };
    // Two tiles newGame() itself laid: one rebuilt as something else, one
    // stripped. cineSet() reverts exactly these, so they are what proves the
    // replay is not winding G.birth back over a played colony. Structures on
    // tiles birth never touched cannot catch it — which is why the first
    // version of this test passed on a build that had the bug.
    const builds = (G.birth || []).filter(s => s.k !== 'd');
    if (builds.length >= 2) {
      G.tiles[idx(builds[0].x, builds[0].y)].b = { type: 'PROC' };
      G.tiles[idx(builds[builds.length - 1].x, builds[builds.length - 1].y)].b = null;
    }
    G.turn = 706; G.crew = 40; G.morale = 100;
    knownMap = null;
    recompute();
    G.power = G.cap; G.water = 1935; G.he3 = 609.4;
    ${snap.toString()}
    return snap();
  })()`);
  console.log(`  site seed ${state.seed}  turn ${state.turn}  crew ${state.crew}  ` +
              `${state.dug.split(',').length} dug  ${state.built.split(',').length} built  ` +
              `(birth laid ${state.birth})`);

  if (state.turn < 100) { console.log('  FAIL  the colony did not get far enough to be a test'); process.exit(1); }

  // Zoomed in and panned off before the replay, so the framing check below
  // has something to correct. The animatic is composed for the whole map.
  const viewBefore = await page.evaluate(() => {
    zoom = 2.4; panX = 140; panY = -90; layout(); draw();
    return { zoom, panX: Math.round(panX), panY: Math.round(panY) };
  });
  console.log(`  view before the replay: zoom ${viewBefore.zoom}, ` +
              `pan ${viewBefore.panX},${viewBefore.panY}`);

  // Replay, the way the DISPLAY button does it.
  await page.evaluate(() => { cineSpeed = 1; startCine(true, true); });
  const playing = await page.evaluate(() => ({ raf: !!cineRaf, survey: cineSurvey, turn: cineTurn }));
  console.log(`  replay running: raf ${playing.raf}  survey ${playing.survey}  turn held ${playing.turn}`);

  // Mid-sweep: the ground must still be the colony's, not bare rock.
  await page.waitForTimeout(2200);
  const mid = await page.evaluate(`(() => { ${snap.toString()} return Object.assign(snap(), { raf: !!cineRaf, phase: cinePhase(cineClock).k }); })()`);
  console.log(`  mid-sweep phase ${mid.phase}  ${mid.dug.split(',').length} dug  ${mid.built.split(',').length} built`);

  // Let it run out.
  await page.waitForFunction(() => !cineRaf, null, { timeout: 20000 });
  const after = await page.evaluate(`(() => { ${snap.toString()} return snap(); })()`);

  const checks = [
    ['the survey pass never rewinds the ground', mid.dug === state.dug && mid.built === state.built],
    ['a structure built over a birth tile survives the replay',
     /:PROC\b/.test(after.built)],
    ['a stripped birth structure stays stripped',
     after.built.split(',').length === state.built.split(',').length],
    ['the turn comes back', after.turn === state.turn],
    ['crew unchanged', after.crew === state.crew],
    ['power unchanged', after.power === state.power],
    ['water unchanged', after.water === state.water],
    ['he-3 unchanged', after.he3 === state.he3],
    ['morale unchanged', after.morale === state.morale],
    ['every dug tile still dug', after.dug === state.dug],
    ['every structure still standing', after.built === state.built],
    ['cineTurn released', await page.evaluate(() => cineTurn === null)],
    ['survey flag cleared', await page.evaluate(() => cineSurvey === false)],
    ['app is out of cine class', await page.evaluate(() => !document.getElementById('app').classList.contains('cine'))],
    ['no page errors', errs.length === 0]
  ];

  // The animatic is composed for the whole site, so it plays on the view the
  // game opens with and leaves it there — the same framing newGame() gives.
  const viewAfter = await page.evaluate(() => {
    const fresh = (() => { const z = zoom, px = panX, py = panY;
      fitView(); const r = { zoom, panX, panY };
      zoom = z; panX = px; panY = py; layout(); draw(); return r; })();
    return { zoom, panX, panY, fresh };
  });
  console.log(`  view after the replay: zoom ${viewAfter.zoom}, ` +
              `pan ${Math.round(viewAfter.panX)},${Math.round(viewAfter.panY)}  ` +
              `(a fresh fit is zoom ${viewAfter.fresh.zoom}, ` +
              `pan ${Math.round(viewAfter.fresh.panX)},${Math.round(viewAfter.fresh.panY)})`);
  checks.push(
    ['the replay leaves the view where the game opens it',
     viewAfter.zoom === viewAfter.fresh.zoom &&
     Math.abs(viewAfter.panX - viewAfter.fresh.panX) < 1 &&
     Math.abs(viewAfter.panY - viewAfter.fresh.panY) < 1]
  );

  // And the opening, full fat, still lands on turn 0 with the birth colony.
  const open = await page.evaluate(`(() => {
    OPT.cine = true;
    newGame(922881);
    ${snap.toString()}
    const born = snap();
    startCine(false);
    return { born, raf: !!cineRaf, survey: cineSurvey, beats: cineBeats().length };
  })()`);
  await page.waitForFunction(() => !cineRaf, null, { timeout: 30000 });
  const openAfter = await page.evaluate(`(() => { ${snap.toString()} return snap(); })()`);
  checks.push(
    ['the opening still plays all eight beats', open.raf && open.survey === false && open.beats === 8],
    ['the opening ends on turn 0', openAfter.turn === 0],
    ['the opening leaves the birth colony intact',
     openAfter.dug === open.born.dug && openAfter.built === open.born.built]
  );

  // LAND HERE AGAIN: two taps, same seed, fresh colony, back on the splash.
  const again = await page.evaluate(`(() => {
    saveWorks = false;
    newGame(922881);
    ${snap.toString()}
    const was = snap();
    for (let i = 0; i < 300; i++) { if (!G.dead) endTurn(); }
    const spent = snap();
    paintRunPane();
    const btn = document.getElementById('againgo');
    if (!btn) return { missing: true };
    const label1 = btn.textContent;
    btn.click();                                   // arms
    const armed = document.getElementById('againgo');
    const label2 = armed.textContent;
    armed.click();                                 // fires
    const now = snap();
    return {
      missing: false, label1, label2,
      seedWas: was.seed, seedNow: now.seed,
      turnSpent: spent.turn, turnNow: now.turn,
      dugWas: was.dug, dugNow: now.dug,
      splash: document.getElementById('splash').style.display !== 'none'
    };
  })()`);
  console.log(`  land-here-again: "${again.label1}" -> "${again.label2}"  ` +
              `seed ${again.seedWas} -> ${again.seedNow}  turn ${again.turnSpent} -> ${again.turnNow}`);
  checks.push(
    ['LAND HERE AGAIN exists on the RUN tab', !again.missing],
    ['it arms before it fires', /LAND HERE AGAIN/.test(again.label1 || '') &&
                                /CONFIRM/.test(again.label2 || '')],
    ['it lands on the same seed', again.seedNow === again.seedWas],
    ['it lands a fresh colony', again.turnNow === 0 && again.dugNow === again.dugWas],
    ['it comes back to the splash, so the opening plays', again.splash === true]
  );

  // The sky ahead of the probe. V2.12.4 painted the unseen columns flat
  // vacuum, which took the stars and Earth with them; this counts lit pixels
  // in a band that is unquestionably ahead of the reveal.
  const sky = await page.evaluate(`(() => {
    saveWorks = false; OPT.cine = true;
    newGame(922881);
    document.getElementById('splash').style.display='none';
    resize(); fitView(); recompute();
    startCine(true, false);
    return true;
  })()`);
  await page.waitForFunction(() => {
    if (!cineRaf) return false;
    const ph = cinePhase(cineClock);
    if (ph.k !== 'sweep' || ph.p < 0.35) return false;
    cineSpeed = 0;
    return true;
  }, null, { polling: 16, timeout: 20000 });
  await page.waitForTimeout(200);
  const lit = await page.evaluate(`(() => {
    // Last column the probe has revealed, then three clear of it.
    let last = -1;
    for (let x = 0; x < CFG.cols; x++) if (cineSeen[x]) last = x;
    const sx = offX + (last + 3) * cell;
    const c = ctx.canvas;
    const kx = c.width / stageW, ky = c.height / stageH;
    const x0 = Math.max(0, Math.round(sx * kx));
    const x1 = Math.min(c.width, Math.round((offX + CFG.cols * cell) * kx));
    // Inside the map rectangle, above the terrain — the exact band the old
    // fog filled with flat vacuum. Sampling above offY proves nothing,
    // because the old fill started there.
    let hi = CFG.rows;
    for (let x = last + 3; x < CFG.cols; x++) hi = Math.min(hi, G.surf[x]);
    const y0 = Math.round((offY + cell * 0.5) * ky);
    const y1 = Math.min(c.height, Math.round((offY + hi * cell * 0.85) * ky));
    if (x1 - x0 < 8 || y1 - y0 < 8) return { skipped: true };
    const d = ctx.getImageData(x0, y0, x1 - x0, y1 - y0).data;
    let bright = 0, peak = 0;
    for (let i = 0; i < d.length; i += 4) {
      const v = (d[i] * 299 + d[i+1] * 587 + d[i+2] * 114) / 1000;
      if (v > peak) peak = v;
      if (v > 45) bright++;
    }
    return { skipped: false, bright, peak, lastSeen: last, cols: CFG.cols };
  })()`);
  await page.evaluate(() => { cineSpeed = 8; });
  await page.waitForFunction(() => !cineRaf, null, { timeout: 20000 });
  console.log(`  sky ahead of the probe: ${lit.bright} lit pixels, peak luma ` +
              `${lit.peak && lit.peak.toFixed(0)} (revealed to column ${lit.lastSeen}/${lit.cols})`);
  checks.push(
    ['the sweep leaves a sky ahead of the probe, not a black rectangle',
     lit.skipped === false && lit.bright > 20 && lit.peak > 80]
  );

  // Nothing on the board may move independently of the map when you pan.
  // V2.12.5 drew the star field in screen space, so it stayed put while the
  // terrain slid past — read as the fog crawling, because the fog's blur keeps
  // collecting stars under a sheet that is moving.
  const pan = await page.evaluate(`(() => {
    saveWorks = false; OPT.cine = false; OPT.fog = true; OPT.grid = true;
    OPT.glass = true;
    newGame(922881);
    document.getElementById('splash').style.display = 'none';
    document.getElementById('app').classList.add('glass');
    resize(); fitView(); zoom = 20.8 / baseCell; layout(); recompute();
    const c = ctx.canvas, kx = c.width / stageW;
    const base = panX;
    draw();
    const a = ctx.getImageData(0, 0, c.width, c.height);
    let sum = 0, n = 0, big = 0;
    for (const dx of [1, 2, 3, 5, 7]) {
      panX = base + dx; layout(); draw();
      const b2 = ctx.getImageData(0, 0, c.width, c.height);
      const sh = Math.round(dx * kx), w = c.width, h = c.height;
      for (let y = 0; y < h; y += 2) for (let x = 0; x + sh < w; x += 2) {
        const i = (y * w + x) * 4, j = (y * w + x + sh) * 4;
        const d = Math.abs(a.data[i] - b2.data[j])
                + Math.abs(a.data[i+1] - b2.data[j+1])
                + Math.abs(a.data[i+2] - b2.data[j+2]);
        sum += d; n++; if (d > 24) big++;
      }
    }
    panX = base; layout(); draw();
    return { mean: sum / n, bigPct: (big / n) * 100 };
  })()`);
  console.log(`  pan residual: mean ${pan.mean.toFixed(2)}, ` +
              `${pan.bigPct.toFixed(3)}% of pixels moving against the map`);
  checks.push(
    ['nothing pans independently of the map', pan.bigPct < 0.01]
  );

  // Glow overhang past the ends of the map. structureGlow() reaches 1.2 cells
  // wider than its tile, and cineDrawFog's clip used to stop at the first and
  // last column boundary, so a lit structure in an end column threw a warm
  // square onto ground the probe had not reached. Needs a view where the map
  // is narrower than the stage, which is what the landscape page gives.
  const wide = await browser.newPage({ viewport: { width: 874, height: 402 }, deviceScaleFactor: 2 });
  await wide.goto('file://' + path.resolve(file));
  await wide.waitForFunction(() => typeof G !== 'undefined' && !!G);
  await wide.evaluate(`(() => {
    saveWorks = false; OPT.cine = true; OPT.fog = true; OPT.glass = true;
    newGame(922881);
    document.getElementById('splash').style.display = 'none';
    document.getElementById('app').classList.add('glass');
    resize(); fitView();
    // Zoomed out so the map is narrower than the stage: without a margin off
    // the ends there is nothing for the overhang to land on.
    zoom = 0.7; layout();
    // A drift from the habitat out to both edges, so a reactor at each end is
    // actually connected and therefore actually lit. An isolated one draws no
    // glow at all, which made the first version of this check pass on a build
    // that had the bug.
    const hab = G.tiles.findIndex(t => t.b && t.b.type === 'HAB');
    const hy = Math.floor(hab / CFG.cols);
    for (let x = 0; x < CFG.cols; x++) {
      const t = G.tiles[idx(x, hy)];
      if (t) { t.dug = true; t.rock = false; }
    }
    for (const x of [0, CFG.cols - 1]) {
      const t = G.tiles[idx(x, hy)];
      t.b = { type: 'FUSION' };
    }
    G.ignited = true; knownMap = null; recompute();
    startCine(true, true);
    // Frozen in the same tick it starts, so the frame under test is always
    // the first one — the dark beat, nothing surveyed. Polling for the beat
    // and freezing from outside raced: three runs failed and five passed on
    // the same build, which is a test that cannot be trusted either way.
    cineSpeed = 0;
  })()`);
  await wide.waitForFunction(
    () => !!cineRaf && cinePhase(cineClock).k === 'dark',
    null, { polling: 8, timeout: 20000 });
  await wide.waitForTimeout(200);
  const over = await wide.evaluate(`(() => {
    const c = ctx.canvas, kx = c.width / stageW;
    const mapL = Math.round(offX * kx);
    const mapR = Math.round((offX + CFG.cols * cell) * kx);
    if (mapL <= 2 && mapR >= c.width - 2) return { skipped: true };
    const d = ctx.getImageData(0, 0, c.width, c.height).data;
    let warm = 0, peak = 0;
    for (let i = 0; i < d.length; i += 4) {
      const x = (i / 4) % c.width;
      if (x >= mapL && x <= mapR) continue;         // over the map: not this test
      // The overhang is faint — the glow gradient is at about 5% alpha by the
      // time it clears the tile — so the threshold has to be low. The sky it
      // sits on is #02040A, R=2 and bluer than it is red, so nothing about the
      // background can trip this.
      const R = d[i], Gc = d[i+1], B = d[i+2];
      if (R > Gc + 2 && Gc > B + 1 && R > 9) { warm++; if (R > peak) peak = R; }
    }
    return { skipped: false, warm, peak, mapL, mapR, w: c.width };
  })()`);
  await wide.close();
  if (over.skipped) {
    console.log('  glow overhang: map fills the stage, nothing to test here');
  } else {
    console.log(`  glow overhang: ${over.warm} warm px off the ends of the map ` +
                `(peak R ${over.peak}; map spans ${over.mapL}..${over.mapR} of ${over.w})`);
  }
  checks.push(
    ['no glow past the ends of the map during the survey',
     over.skipped === true || over.warm === 0]
  );

  let bad = 0;
  for (const [label, ok] of checks) {
    console.log(`  ${ok ? 'ok  ' : 'FAIL'}  ${label}`);
    if (!ok) bad++;
  }
  if (errs.length) errs.slice(0, 5).forEach(e => console.log('        ' + e));
  console.log(`\n  ${checks.length - bad}/${checks.length} passed`);

  await browser.close();
  process.exit(bad ? 1 : 0);
})();
