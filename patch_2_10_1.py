#!/usr/bin/env python3
"""V2.10.0 -> V2.10.1. A mistyped site code says so, and offers the fix.
Guarded: every replacement must match exactly once."""
import sys, pathlib
src, dst = sys.argv[1], sys.argv[2]
h = pathlib.Path(src).read_text()

def rep(old, new, count=1):
    global h
    n = h.count(old)
    assert n == count, f'expected {count} match(es), found {n}:\n{old[:160]}'
    h = h.replace(old, new)

rep('ASTROBARA V2.10.0', 'ASTROBARA V2.10.1')
rep('content="Astrobara V2.10.0', 'content="Astrobara V2.10.1')
rep("const BUILD = 'V2.10.0';", "const BUILD = 'V2.10.1';")

# ---- the near-miss finder, beside the parser it second-guesses
rep("""function randomSeed(){ return Math.floor(Math.random()*SEED_SPACE); }""",
"""function randomSeed(){ return Math.floor(Math.random()*SEED_SPACE); }

// Anything typed is a seed, which is the point — but it means a code with one
// letter wrong (SCRAP for SCARP) quietly lands on some other site, and typing
// it again lands on the same wrong one. When the text is shaped like a code and
// a word is not on its list, find what it was probably meant to be.
function editDist(a, b){
  // Optimal string alignment: insertions, deletions, swaps of two neighbours.
  const d = [];
  for(let i=0;i<=a.length;i++){ d.push([i]); }
  for(let j=1;j<=b.length;j++) d[0][j] = j;
  for(let i=1;i<=a.length;i++){
    for(let j=1;j<=b.length;j++){
      const c = a[i-1] === b[j-1] ? 0 : 1;
      d[i][j] = Math.min(d[i-1][j] + 1, d[i][j-1] + 1, d[i-1][j-1] + c);
      if(i > 1 && j > 1 && a[i-1] === b[j-2] && a[i-2] === b[j-1])
        d[i][j] = Math.min(d[i][j], d[i-2][j-2] + 1);
    }
  }
  return d[a.length][b.length];
}
function nearestWord(w, list){
  let best = null, bestD = 99;
  for(let i=0;i<list.length;i++){
    const dd = editDist(w, list[i]);
    if(dd < bestD){ bestD = dd; best = list[i]; }
  }
  // one slip in a short word, two in a long one — beyond that it was not a typo
  return bestD <= (w.length <= 4 ? 1 : 2) ? best : null;
}
// Returns { bad: the word that is off, fix: the code it was probably meant as },
// or null when the text is a good code, or not shaped like a code at all.
function nearCode(text){
  const up = String(text||'').trim().toUpperCase();
  const m = up.replace(/\\s+/g,'-').split(/[-_.\\/]+/).filter(Boolean);
  if(m.length !== 3 || !/^\\d+$/.test(m[2])) return null;
  const n = parseInt(m[2],10);
  if(n >= SEED_N) return null;
  const inA = SEED_A.indexOf(m[0]) >= 0, inB = SEED_B.indexOf(m[1]) >= 0;
  if(inA && inB) return null;
  // the two words the right way round, typed the wrong way round
  if(SEED_B.indexOf(m[0]) >= 0 && SEED_A.indexOf(m[1]) >= 0)
    return { bad: m[0] + '-' + m[1], fix: m[1] + '-' + m[0] + '-' + n, swapped: true };
  const a = inA ? m[0] : nearestWord(m[0], SEED_A);
  const b = inB ? m[1] : nearestWord(m[1], SEED_B);
  if(!a || !b) return null;
  return { bad: inA ? m[1] : m[0], fix: a + '-' + b + '-' + n };
}""")

# ---- the echo: say what the text will do, and say it plainly when it is a slip
rep("""// Type anything and it becomes a seed. Show which one, so it can be shared.
function paintSeedEcho(){
  const e = document.getElementById('seedecho');
  if(!e) return;
  const sd = codeToSeed(seedDraft);
  if(sd === null){ e.textContent = ''; e.className = 'seedecho'; return; }
  const canon = seedToCode(sd);
  e.className = 'seedecho';
  e.textContent = canon === seedDraft.trim().toUpperCase() ? '\\u2713 ' + canon : '\\u2192 ' + canon;
}""",
"""// Type anything and it becomes a seed. Show which one, so it can be shared —
// and when the text is a code with a slip in it, say so before it costs a run.
function paintSeedEcho(){
  const e = document.getElementById('seedecho');
  if(!e) return;
  e.textContent = ''; e.className = 'seedecho'; delete e.dataset.fix;
  const sd = codeToSeed(seedDraft);
  if(sd === null) return;
  const canon = seedToCode(sd);
  const here = G && sd === G.seed ? ' \\u00b7 you are already here' : '';
  const near = nearCode(seedDraft);
  if(near){
    const fix = document.createElement('div');
    fix.className = 'seedfix';
    fix.textContent = (near.swapped ? near.bad + ' is the wrong way round'
                                    : near.bad + ' is not a site word')
                    + ' \\u2014 did you mean ' + near.fix + '? Tap to use it.';
    const as = document.createElement('div');
    as.textContent = 'As typed, it lands on ' + canon + here + '.';
    e.appendChild(fix); e.appendChild(as);
    e.dataset.fix = near.fix;
    return;
  }
  const exact = canon === seedDraft.trim().toUpperCase() ||
                (sd === LEGACY_SEED && canon === LEGACY_CODE);
  e.textContent = (exact ? '\\u2713 ' : '\\u2192 ') + canon + here;
}""")
# The echo sat below the fold of the tools panel, so what the text would do was
# out of sight while typing. Scroll the panel, not the page, so the echo and
# LAND THERE come up under the field. Layout offsets, not screen rects: the
# rotated portrait view turns screen axes but not these.
rep("""function paintSeedEcho(){
  const e = document.getElementById('seedecho');
  if(!e) return;
  e.textContent = ''; e.className = 'seedecho'; delete e.dataset.fix;""",
"""function offsetIn(el, anc){
  let y = 0;
  while(el && el !== anc){ y += el.offsetTop; el = el.offsetParent; }
  return y;
}
function showSeedEcho(){
  const body = document.getElementById('toolsbody'), tools = document.getElementById('tools');
  const inp = document.getElementById('seedin'), go = document.getElementById('seedgo');
  if(!body || !tools || !inp || !go) return;
  const base = offsetIn(body, tools);
  const inTop = offsetIn(inp, tools) - base;
  const goBottom = offsetIn(go, tools) - base + go.offsetHeight + 6;
  // as much as fits below the field, without pushing the field itself away
  const want = Math.min(goBottom, inTop + body.clientHeight);
  if(want > body.scrollTop + body.clientHeight) body.scrollTop = want - body.clientHeight;
}
function paintSeedEcho(){
  const e = document.getElementById('seedecho');
  if(!e) return;
  paintSeedEchoText(e);
  if(document.activeElement === document.getElementById('seedin') || e.dataset.fix) showSeedEcho();
}
function paintSeedEchoText(e){
  e.textContent = ''; e.className = 'seedecho'; delete e.dataset.fix;""")

# tapping the suggestion puts it in the field
rep("""  inp.addEventListener('blur', function(){ resetScroll(); recalibrate(); resize(); });
""",
"""  inp.addEventListener('blur', function(){ resetScroll(); recalibrate(); resize(); });
  document.getElementById('seedecho').addEventListener('click', function(ev){
    ev.stopPropagation();
    const fix = this.dataset.fix;
    if(!fix) return;
    seedDraft = fix; inp.value = fix;
    if(newRunArmed === 'seed') newRunArmed = '';
    paintSeedEcho();
  });
""")

# ---- keyboard shortcuts stand down while a text field has the focus.
# Space ended a turn and never reached the field, digits armed build tools, V
# toggled SURVEY — so typing 'any words at all' into the site field could end a
# turn per space. On a phone the software keyboard sends the same keydowns.
rep("""window.addEventListener('keydown', e => {
  if(e.key===' '){ e.preventDefault(); endTurn(); }""",
"""function typingInField(e){
  const t = e.target;
  return !!t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' ||
                 t.tagName === 'SELECT' || t.isContentEditable);
}
window.addEventListener('keydown', e => {
  if(typingInField(e)) return;
  if(e.key===' '){ e.preventDefault(); endTurn(); }""")

rep("""#pane-run .seedecho.bad{color:var(--alarm);}""",
"""#pane-run .seedecho.bad{color:var(--alarm);}
#pane-run .seedecho .seedfix{color:var(--alarm);cursor:pointer;margin-bottom:2px;}""")

pathlib.Path(dst).write_text(h)
print('patched ->', dst)
