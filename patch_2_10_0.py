#!/usr/bin/env python3
"""V2.9.15-GLASS -> V2.10.0. Glass becomes the main line.
Guarded: every replacement must match exactly once."""
import sys, pathlib
src, dst = sys.argv[1], sys.argv[2]
h = pathlib.Path(src).read_text()

def rep(old, new, count=1):
    global h
    n = h.count(old)
    assert n == count, f'expected {count} match(es), found {n}:\n{old[:160]}'
    h = h.replace(old, new)

# ---- version: no suffix, glass is the game
rep('ASTROBARA V2.9.15-GLASS', 'ASTROBARA V2.10.0')
rep('content="Astrobara V2.9.15-GLASS', 'content="Astrobara V2.10.0')
rep("const BUILD = 'V2.9.15-GLASS';", "const BUILD = 'V2.10.0';")

# ---- branch wording in the code
rep("""/* ---------------- GLASS BRANCH ----------------
   The map is the screen. Every panel floats on it.""",
"""/* ---------------- GLASS ----------------
   The map is the screen. Every panel floats on it. This is the layout from
   V2.10.0 on; it began as the V2.9.4-GLASS branch.""")
rep("""   Every rule here is scoped to #app.glass. Turning glass off removes the class
   and the layout above this block is the layout, unchanged from V2.9.4. Before""",
"""   Every rule here is scoped to #app.glass. Turning glass off in DISPLAY removes
   the class and the layout above this block is the layout — the boxed one from
   V2.9.4, kept so both can be tested. Before""")
rep("// hides exactly the stutter worth finding, which on this branch is a blur",
    "// hides exactly the stutter worth finding, which with glass on is a blur")

# ---- achievements: cleared when the major version changes, never within one
rep("""// An award says this build can be beaten that way, so it is only worth what the
// build it was set on is worth: a version bump clears the sheet, the same way a
// saved run does not carry across builds. Runs first, before anything reads it.
(function clearAchvOnNewBuild(){
  try {
    const raw = localStorage.getItem(ACHV_KEY);
    if(!raw) return;
    const d = JSON.parse(raw);
    if(!d || d.build !== BUILD) localStorage.removeItem(ACHV_KEY);
  } catch(err){ /* storage off, or nothing there to clear */ }
})();""",
"""// Awards belong to a major version. Dev builds and release candidates inside one
// keep them — an RC may only change how the game looks, never how it plays, so
// an award set on RC1 is as good on RC2. A new major version is a new game and
// starts a clean sheet, once. Runs first, before anything reads the record.
function buildMajor(b){
  const m = /^V(\\d+)\\./.exec(b || '');
  return m ? m[1] : null;
}
// The stamp arrived in V2.9.15; a record without one was written by V2.
const ACHV_UNSTAMPED_MAJOR = '2';
(function clearAchvOnNewMajor(){
  try {
    const raw = localStorage.getItem(ACHV_KEY);
    if(!raw) return;
    const d = JSON.parse(raw);
    const was = (d && d.build) ? buildMajor(d.build) : ACHV_UNSTAMPED_MAJOR;
    if(!d || !d.got || was !== buildMajor(BUILD)) localStorage.removeItem(ACHV_KEY);
  } catch(err){ /* storage off, or nothing there to clear */ }
})();""")

pathlib.Path(dst).write_text(h)
print('patched ->', dst)
