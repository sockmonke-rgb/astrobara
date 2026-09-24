#!/usr/bin/env python3
"""
ASTROBARA  V2.12.13

The BOARD tab never repainted itself.

paintBoardPane() had exactly one caller — showTab('board'). Open the tab, keep
playing, and the list is frozen at whatever it said the moment you opened it.
Earn SKELETON CREW and the store has it, Copy diagnostics reports it, the
unlock card announces it, and the pane you are looking at still says
"[LOCKED] under 20 structures standing" and "UNLOCKED · 0 of 11".

The other two panes were already handled. paintDisplayPane() repaints itself on
a system text-size change, and paintRunPane() from half a dozen places. The
board was the one that only ever painted on the way in, which is also the one
whose content changes while you are not touching it.

Two hooks, both on the events that actually change what the pane shows:

  * award()       — a row flips from [LOCKED] and the count goes up
  * recordScore() — a run lands on the board

Nothing on the turn loop. Repainting every recompute would rebuild the list
sixty turns a sol to no purpose, and it would throw away the scroll position
while someone was reading it.

Which is the other half of this: the pane scrolls, so the repaint restores
scrollTop. Getting the award is not a reason to lose your place in the list.

Usage:  python3 patch_2_12_13.py <in.html> <out.html>
"""

import hashlib
import sys

EDITS = []


def edit(name, old, new):
    EDITS.append((name, old, new))


edit(
    "a repaint that only runs when the pane is actually up",
    """function paintBoardPane(){""",
    """// paintBoardPane() rebuilds innerHTML, so calling it on a pane nobody is
// looking at is pure work, and calling it on one somebody IS looking at moves
// the scroll back to the top. This does neither: it returns immediately when
// the tab is not showing, and puts the reader back where they were when it is.
function refreshBoardPane(){
  const p = document.getElementById('pane-board');
  if(!p || p.style.display === 'none') return;
  const body = document.getElementById('toolsbody');
  const top = body ? body.scrollTop : 0;
  paintBoardPane();
  if(body) body.scrollTop = top;
}

function paintBoardPane(){""",
)

edit(
    "an award repaints the list it belongs to",
    """  achvQueue.push(def);
  pumpAchv();
  return true;
}""",
    """  achvQueue.push(def);
  pumpAchv();
  // The card announces it and the store has it; the open list has to agree.
  // Without this the row you are looking at stays [LOCKED] for the rest of the
  // run, which is how this was found.
  refreshBoardPane();
  return true;
}""",
)

edit(
    "a finished run repaints the rows",
    """  try { localStorage.setItem(SCORE_KEY, JSON.stringify(board)); } catch(err){ /* storage off */ }
  return entry;
}""",
    """  try { localStorage.setItem(SCORE_KEY, JSON.stringify(board)); } catch(err){ /* storage off */ }
  // The rows change too, not just the awards.
  refreshBoardPane();
  return entry;
}""",
)

edit(
    "the board heading V2.12.12 missed",
    '''  let out = '<div class="board"><div class="bh">COLONIES THAT HELD A NIGHT</div>';''',
    '''  let out = '<div class="board"><div class="bh">COLONIES THAT CARRIED A NIGHT</div>';''',
)

edit("header stamp", "  ASTROBARA V2.12.12", "  ASTROBARA V2.12.13")
edit("meta stamp", 'content="Astrobara V2.12.12 —', 'content="Astrobara V2.12.13 —')
edit("BUILD stamp", "const BUILD = 'V2.12.12';", "const BUILD = 'V2.12.13';")


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    src, dst = sys.argv[1], sys.argv[2]
    text = open(src, encoding="utf-8").read()
    before = text

    for name, old, new in EDITS:
        found = text.count(old)
        if found != 1:
            raise AssertionError(
                "%s: expected 1 occurrence, found %d.\nAnchor was:\n---\n%s\n---"
                % (name, found, old))
        text = text.replace(old, new, 1)
        print("  ok  %s" % name)

    award = text.split("function award(id){")[1].split("\n}")[0]
    checks = [
        ("V2.12.13 stamped three times", text.count("V2.12.13") == 3),
        ("no V2.12.12 left", "V2.12.12" not in text),
        ("the helper exists", "function refreshBoardPane(){" in text),
        ("it bails when the pane is hidden",
         "if(!p || p.style.display === 'none') return;" in text),
        ("it keeps the scroll position",
         "const top = body ? body.scrollTop : 0;" in text
         and "if(body) body.scrollTop = top;" in text),
        ("award repaints", "refreshBoardPane();" in award),
        ("award still returns true after it", "refreshBoardPane();\n  return true;" in text),
        ("recording a run repaints",
         "// The rows change too, not just the awards.\n  refreshBoardPane();\n  return entry;" in text),
        # V2.12.12's sweep was case-sensitive and this heading is upper case,
        # so it shipped. The check below is not.
        ("no 'held a night' left, in any case",
         "held a night" not in text.split("</style>")[1].lower()),
        ("the board heading says carried",
         "COLONIES THAT CARRIED A NIGHT" in text),
        ("two call sites — award, and recording a run",
         text.count("refreshBoardPane();") == 2),
        # Nothing on the turn loop: a repaint every recompute would reset the
        # scroll under the reader.
        ("not called from recompute",
         "refreshBoardPane" not in text.split("function recompute(){")[1].split("\n}")[0]),
        ("not called from paintUI",
         "refreshBoardPane" not in text.split("function paintUI(){")[1].split("\n}")[0]),
        ("paintBoardPane itself is unchanged",
         "function paintBoardPane(){\n  const p = document.getElementById('pane-board');" in text),
        ("showTab still paints it directly", "if(name === 'board') paintBoardPane();" in text),
        # No markup, no CSS, no model.
        ("no divs in the markup",
         text.split("<script")[0].count("<div")
         == before.split("<script")[0].count("<div")),
        ("no runtime divs added", text.count("<div") == before.count("<div")),
        ("no ids added", text.count(" id=") == before.count(" id=")),
        ("no css rules added",
         text.split("</style>")[0].count("{")
         == before.split("</style>")[0].count("{")),
        ("balanced braces", text.count("{") == text.count("}")),
        # Everything since V2.12.0 is still in here.
        ("the groups are still there", "[1, 'A NIGHT CARRIED ON FUSION']" in text),
        ("the card still takes the long clue", "(def.cf || def.c)" in text),
        ("endCine is still guarded",
         "if(cineTurn !== null){\n    G.turn = cineTurn; cineTurn = null;" in text),
        ("the card still cannot show under an overlay",
         "if(achvShowing || !achvQueue.length || achvBlocked()) return;" in text),
    ]
    for label, ok in checks:
        if not ok:
            raise AssertionError("post-condition failed: %s" % label)
        print("  ok  %s" % label)

    open(dst, "w", encoding="utf-8").write(text)
    print("\n  %s  %d bytes  md5 %s"
          % (dst, len(text.encode()), hashlib.md5(text.encode()).hexdigest()))


if __name__ == "__main__":
    main()
