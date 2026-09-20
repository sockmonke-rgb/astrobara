#!/usr/bin/env python3
"""V2.10.1 -> V2.10.2. The site field stops previewing codes while you type.
Guarded: every replacement must match exactly once."""
import sys, pathlib
src, dst = sys.argv[1], sys.argv[2]
h = pathlib.Path(src).read_text()

def rep(old, new, count=1):
    global h
    n = h.count(old)
    assert n == count, f'expected {count} match(es), found {n}:\n{old[:160]}'
    h = h.replace(old, new)

rep('ASTROBARA V2.10.1', 'ASTROBARA V2.10.2')
rep('content="Astrobara V2.10.1', 'content="Astrobara V2.10.2')
rep("const BUILD = 'V2.10.1';", "const BUILD = 'V2.10.2';")

rep("""'placeholder="a code, or any words at all" ' +""",
    """'placeholder="WORD-WORD-###" ' +""")

# Every keystroke of half-typed text hashed to a fresh, unrelated code — WTF
# showed NOON-DAY-699 — which read as noise. The line under the field now only
# speaks about what you are typing: the format until it is a code, a tick once
# it is one, and the fix when it is a code with a slip in it.
rep("""function paintSeedEchoText(e){
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
}""",
"""function paintSeedEchoText(e){
  e.textContent = ''; e.className = 'seedecho'; delete e.dataset.fix;
  const sd = codeToSeed(seedDraft);
  if(sd === null) return;
  const near = nearCode(seedDraft);
  if(near){
    const fix = document.createElement('div');
    fix.className = 'seedfix';
    fix.textContent = (near.swapped ? near.bad + ' is the wrong way round'
                                    : near.bad + ' is not a site word')
                    + ' \\u2014 did you mean ' + near.fix + '? Tap to use it.';
    e.appendChild(fix);
    e.dataset.fix = near.fix;
    return;
  }
  const canon = seedToCode(sd);
  // a real code: said back, as a tick, with where it is if you are on it
  const norm = seedDraft.trim().toUpperCase().replace(/\\s+/g,'-');
  if(canon === norm || sd === LEGACY_SEED){
    e.textContent = '\\u2713 ' + canon + (G && sd === G.seed ? ' \\u00b7 you are already here' : '');
    return;
  }
  // anything else: the shape a code takes, and nothing more
  e.textContent = 'WORD-WORD-###';
}""")

pathlib.Path(dst).write_text(h)
print('patched ->', dst)
