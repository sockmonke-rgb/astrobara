/* Does the unlock card actually get seen?

   Self-sufficiency awards several achievements and shows the verdict in the
   same breath. The card sits at z-index 21, every overlay at 30 or above, so
   a card shown while the verdict is up is a card nobody sees: it runs its
   3.6 seconds behind it and removes itself.

   This watches #achvslot with a MutationObserver and records, for every card
   that appears, whether an overlay was up at the time.

   Usage:  node achv-check.js <build.html>  */

const { chromium } = require('playwright');
const path = require('path');
const file = process.argv[2] || 'astrobara-v2_12_11.html';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 874, height: 402 }, deviceScaleFactor: 2 });
  const errs = [];
  page.on('pageerror', e => errs.push(String(e)));
  await page.goto('file://' + path.resolve(file));
  await page.waitForFunction(() => typeof G !== 'undefined' && !!G);

  await page.evaluate(() => {
    saveWorks = false; OPT.cine = false;
    try { localStorage.removeItem('astrobara.achv'); } catch (e) {}
    window.__seen = [];
    const slot = document.getElementById('achvslot');
    const up = () => ['over', 'splash', 'portraitgate'].some(id => {
      const el = document.getElementById(id);
      return el && getComputedStyle(el).display !== 'none';
    });
    new MutationObserver(ms => {
      for (const m of ms) for (const n of m.addedNodes) {
        if (n.nodeType === 1 && n.classList.contains('achvcard')) {
          window.__seen.push({
            name: (n.querySelector('.a2') || {}).textContent || '?',
            covered: up()
          });
        }
      }
    }).observe(slot, { childList: true });
  });

  // Drive a colony to self-sufficiency: the moment several awards and the
  // verdict arrive together.
  const got = await page.evaluate(`(() => {
    newGame(922881);
    document.getElementById('splash').style.display = 'none';
    resize(); fitView(); recompute();
    // Reach it by the shortest honest route the model allows: the flags the
    // turn loop reads, then one endTurn to resolve.
    // fusionNightTurns is reset every dark turn that fusion is not carrying,
    // so it cannot be poked from outside — the colony has to actually hold the
    // night on a reactor. Give it one, connected, with fuel, and let it run.
    const hab = G.tiles.findIndex(t => t.b && t.b.type === 'HAB');
    const hx = hab % CFG.cols, hy = Math.floor(hab / CFG.cols);
    for (let d = 1; d <= 3; d++) {
      const t = G.tiles[idx(hx + d, hy)];
      if (t) { t.dug = true; t.rock = false; }
    }
    const r = G.tiles[idx(hx + 3, hy)];
    if (r) r.b = { type: 'FUSION' };
    G.he3 = 5000; G.water = 5000; G.power = G.cap;
    knownMap = null; recompute();
    for (let i = 0; i < 120 && !G.won && !G.dead; i++) {
      G.he3 = Math.max(G.he3, 500);
      G.water = Math.max(G.water, 500);
      endTurn();
    }
    return { won: !!G.won, ss: !!G.selfSufficient,
             overUp: getComputedStyle(document.getElementById('over')).display !== 'none' };
  })()`);
  console.log(`  self-sufficient ${got.ss}, won ${got.won}, verdict up ${got.overUp}`);
  if (!got.ss) { console.log('  FAIL  could not reach self-sufficiency'); process.exit(1); }

  await page.waitForTimeout(600);
  // checkAchv() runs before finish(), so a card can legitimately appear a
  // moment BEFORE the verdict opens. What matters is not the instant it was
  // inserted — it is whether the player ever got to see it with nothing on
  // top. So: what was announced before the verdict closed, and what after.
  const during = await page.evaluate(() => window.__seen.slice());
  await page.evaluate(() => { const k = document.getElementById('keep'); if (k) k.click(); });
  await page.waitForTimeout(1500);
  const total = await page.evaluate(() => window.__seen.slice());
  const after = total.slice(during.length);

  const awarded = await page.evaluate(() => Object.keys(loadAchv().got).length);
  console.log(`  ${awarded} awarded; cards before the verdict closed: ${during.length}` +
              (during.length ? ' (' + during.map(c => c.name).join(', ') + ')' : '') +
              `; after: ${after.length}` +
              (after.length ? ' (' + after.map(c => c.name).join(', ') + ')' : ''));

  // Every name that only ever appeared while an overlay was up, or that was
  // taken down by one, has to come back.
  const seenClear = new Set(after.map(c => c.name)
    .concat(during.filter(c => !c.covered).map(c => c.name)));
  const lost = during.filter(c => c.covered && !seenClear.has(c.name)).map(c => c.name);

  // The BOARD tab, left open while you play. paintBoardPane() had one caller —
  // showTab('board') — so the list froze at whatever it said when the tab was
  // opened: [LOCKED] rows that were no longer locked, and a count that never
  // moved. Reported from a real run at V2.12.12 with nine of eleven earned and
  // the pane still showing SKELETON CREW locked.
  const board = await page.evaluate(() => {
    const tools = document.getElementById('tools');
    if (tools) tools.classList.remove('shut');
    showTab('board');
    const pane = document.getElementById('pane-board');
    const read = () => {
      const txt = pane.innerText;
      const m = txt.match(/UNLOCKED[^\n]*of\s+(\d+)/);
      return {
        count: Number((txt.match(/UNLOCKED\s*\u00b7\s*(\d+)/) || [])[1]),
        locked: (txt.match(/\[LOCKED\]/g) || []).length,
        of: m ? Number(m[1]) : 0
      };
    };
    const before = read();

    // Something not yet earned, awarded the way the game awards it.
    const id = ACHV.map(a => a.id).filter(i => !loadAchv().got[i])[0] || null;
    if (!id) return { skipped: 'everything was already awarded' };
    award(id);
    const after = read();

    // And the reader's place in the list is kept across the repaint.
    const body = document.getElementById('toolsbody');
    let scrollKept = true;
    if (body && body.scrollHeight > body.clientHeight + 4) {
      body.scrollTop = 20;
      const id2 = ACHV.map(a => a.id).filter(i => !loadAchv().got[i])[0];
      if (id2) { award(id2); scrollKept = body.scrollTop === 20; }
    }
    return { before, after, id, scrollKept, stored: !!loadAchv().got[id] };
  });
  if (board.skipped) {
    console.log('  note  board repaint not exercised: ' + board.skipped);
  } else {
    console.log(`  board pane on award of ${board.id}: ` +
                `${board.before.count}/${board.before.of} -> ${board.after.count}/${board.after.of}, ` +
                `[LOCKED] rows ${board.before.locked} -> ${board.after.locked}`);
  }

  const checks = [
    ['the open board pane counts the new award',
      !!board.skipped || (board.stored && board.after.count === board.before.count + 1)],
    ['the row it belongs to stops saying [LOCKED]',
      !!board.skipped || board.after.locked === board.before.locked - 1],
    ['the repaint keeps the reader\'s scroll position',
      !!board.skipped || board.scrollKept === true],
    ['self-sufficiency awarded something', awarded > 0],
    ['a card was announced', total.length > 0],
    ['nothing was announced only underneath the verdict', lost.length === 0],
    ['the queue runs once the verdict closes', after.length > 0],
    ['no page errors', errs.length === 0]
  ];
  if (lost.length) console.log('        lost: ' + lost.join(', '));
  let bad = 0;
  for (const [label, ok] of checks) { console.log(`  ${ok ? 'ok  ' : 'FAIL'}  ${label}`); if (!ok) bad++; }
  if (errs.length) errs.slice(0, 3).forEach(e => console.log('        ' + e));
  console.log(`\n  ${checks.length - bad}/${checks.length} passed`);
  await browser.close();
  process.exit(bad ? 1 : 0);
})();
