#!/usr/bin/env python3
"""
ASTROBARA  V2.12.14

A twelfth award, a rename, and the star rating on the board.

ESCAPE VELOCITY — every other award earned. It sits at the foot of the list,
below both groups and behind a rule, with no heading of its own: the list then
reads in the order you earn it. It is the only award that is not about a
colony, so it belongs to neither group.

THE LONG SURVEY becomes ABUNDANCE. Same id, same condition — a night carried
at every rating. The ratings are difficulty, so the 1-star end is the generous
ground and the 5-star end is BRUTAL; carrying a night on all five is making a
colony out of plenty and out of almost nothing alike.

ESCAPE VELOCITY could not have gone in the fusion group, whichever name won.
Every award under A NIGHT CARRIED ON FUSION *is* an escape velocity — that is
what the heading says — so the name would have described eight of its
neighbours as well as itself and distinguished nothing. Outside the groups it
has no neighbours to compete with.

The capstone is checked in the ungated part of checkAchv(), which runs every
turn, and again at the end of award(). Either alone is a hole:

  * award() alone — if all eleven are already earned when this build arrives,
    there is no twelfth award to fire the check and it would never land.
  * checkAchv() alone — the ungated part runs before the gated awards, so the
    eleventh landing this turn would not be seen until the next one.

And the board rows carry the site's star rating, in gold, between the code and
the run. It is a property of the site rather than of the run, so it sits with
the code. All three renderers: the BOARD tab, the end card, and COPY AS TEXT.

Usage:  python3 patch_2_12_14.py <in.html> <out.html>
"""

import hashlib
import sys

EDITS = []


def edit(name, old, new):
    EDITS.append((name, old, new))


edit(
    "THE LONG SURVEY becomes ABUNDANCE, and the capstone joins the table",
    """  {id:'all_ratings',    n:'THE LONG SURVEY',    c:'at every rating',                   g:'\\u25eb', w:1,
   cf:'a night carried at every rating'},""",
    """  {id:'all_ratings',    n:'ABUNDANCE',          c:'at every rating',                   g:'\\u25eb', w:1,
   cf:'a night carried at every rating'},""",
)

edit(
    "the capstone",
    """  {id:'single_reactor', n:'TWIN SUNS',          c:'a night carried on one reactor',    g:'*', w:1}
];""",
    """  {id:'single_reactor', n:'TWIN SUNS',          c:'a night carried on one reactor',    g:'*', w:1},
  // cap — belongs to neither group. It is the only award that is not about a
  // colony, and every award under A NIGHT CARRIED ON FUSION already is an
  // escape velocity, so this name would have distinguished nothing in there.
  {id:'all_awards',     n:'ESCAPE VELOCITY',    c:'every other award',                 g:'\\u2191', cap:1,
   cf:'every other award earned'}
];""",
)

edit(
    "one row, built in one place, so the capstone cannot drift from the rest",
    """  let list = '';
  for(let gi=0;gi<ACHV_GROUPS.length;gi++){
    const want = ACHV_GROUPS[gi][0];
    let rows = '';
    for(let i=0;i<ACHV.length;i++){
      const d = ACHV[i];
      if((d.w ? 1 : 0) !== want) continue;
      const got = !!a.got[d.id];
      if(got) earned++;
      rows += '<div class="ar'+(got?' got':'')+'">'
           +  '<span class="ag2">'+(got ? d.g : '\\u00b7')+'</span>'
           +  '<span class="atx"><span class="an">'+(got ? d.n : '[LOCKED]')+'</span>'
           +  '<span class="ac">'+d.c+'</span></span></div>';
    }
    if(!rows) continue;
    list += '<div class="ghead">'+ACHV_GROUPS[gi][1]+'</div>'
         +  '<div class="achvlist">'+rows+'</div>';
  }""",
    """  const achvRow = function(d, got){
    return '<div class="ar'+(got?' got':'')+'">'
         +  '<span class="ag2">'+(got ? d.g : '\\u00b7')+'</span>'
         +  '<span class="atx"><span class="an">'+(got ? d.n : '[LOCKED]')+'</span>'
         +  '<span class="ac">'+d.c+'</span></span></div>';
  };
  let list = '';
  for(let gi=0;gi<ACHV_GROUPS.length;gi++){
    const want = ACHV_GROUPS[gi][0];
    let rows = '';
    for(let i=0;i<ACHV.length;i++){
      const d = ACHV[i];
      if(d.cap) continue;                       // the capstone is not in a group
      if((d.w ? 1 : 0) !== want) continue;
      const got = !!a.got[d.id];
      if(got) earned++;
      rows += achvRow(d, got);
    }
    if(!rows) continue;
    list += '<div class="ghead">'+ACHV_GROUPS[gi][1]+'</div>'
         +  '<div class="achvlist">'+rows+'</div>';
  }
  // Below both groups, behind a rule, with no heading: the list reads in the
  // order you earn it, and a heading over a single row is furniture.
  for(let i=0;i<ACHV.length;i++){
    const d = ACHV[i];
    if(!d.cap) continue;
    const got = !!a.got[d.id];
    if(got) earned++;
    list += '<div class="achvlist caplist">'+achvRow(d, got)+'</div>';
  }""",
)

edit(
    "the rule above the capstone",
    """#pane-board .ghead{margin-top:9px;margin-bottom:2px;
  font-size:calc(8.5px * var(--ts));letter-spacing:.14em;color:var(--sunlit);opacity:.85;}""",
    """#pane-board .ghead{margin-top:9px;margin-bottom:2px;
  font-size:calc(8.5px * var(--ts));letter-spacing:.14em;color:var(--sunlit);opacity:.85;}
/* The capstone stands apart from both groups. A rule rather than a heading:
   one row does not need a label, and the gap says the same thing. */
#pane-board .caplist{margin-top:9px;padding-top:7px;border-top:1px solid var(--rule);}
/* The site's rating, between the code and the run. Gold, because it is the
   thing the row is worth scanning for. */
.board .br .bs{flex:0 0 auto;color:var(--sunlit);}""",
)

edit(
    "the capstone check",
    """// Called every turn. Each test reads state the turn loop already keeps, so
// nothing here can disagree with the colony it is describing.
function checkAchv(){
  if(!G || G.review) return;
  const conn = connectedSet();""",
    """// Every other award earned. Read off the store rather than the colony, like
// SISTER COLONY and ABUNDANCE, because it is a fact about the player and not
// about this run.
//
// Called from two places, and both are needed. checkAchv() runs it every turn,
// which is what catches a player who already had all eleven when this build
// arrived — there is no twelfth award left to fire it. award() runs it too,
// because checkAchv()'s ungated part runs BEFORE the gated awards, so the
// eleventh landing this turn would otherwise wait for the next one.
function checkCapstone(){
  const got = loadAchv().got;
  for(let i=0;i<ACHV.length;i++){
    const d = ACHV[i];
    if(d.cap) continue;
    if(!got[d.id]) return;
  }
  award('all_awards');
}

// Called every turn. Each test reads state the turn loop already keeps, so
// nothing here can disagree with the colony it is describing.
function checkAchv(){
  if(!G || G.review) return;
  const conn = connectedSet();
  checkCapstone();""",
)

edit(
    "an award may have been the eleventh",
    """  refreshBoardPane();
  return true;
}""",
    """  refreshBoardPane();
  if(id !== 'all_awards') checkCapstone();
  return true;
}""",
)

edit(
    "the star on the BOARD tab",
    """           +  '<span class="bc">'+e.code+'</span>'
           +  '<span class="bd">sol '+e.sol+(e.night?' \\u00b7 night '+e.night:'')""",
    """           +  '<span class="bc">'+e.code+'</span>'
           +  (e.stars ? '<span class="bs">'+e.stars+'\\u2605</span>' : '')
           +  '<span class="bd">sol '+e.sol+(e.night?' \\u00b7 night '+e.night:'')""",
)

edit(
    "the star on the end card",
    """        +  '<span class="bc">'+e.code+'</span>'
        +  '<span class="bd">sol '+e.sol+(e.night?' \\u00b7 night '+e.night:'')""",
    """        +  '<span class="bc">'+e.code+'</span>'
        +  (e.stars ? '<span class="bs">'+e.stars+'\\u2605</span>' : '')
        +  '<span class="bd">sol '+e.sol+(e.night?' \\u00b7 night '+e.night:'')""",
)

edit(
    "the star in COPY AS TEXT",
    """    return (i+1)+'. '+e.code+' \\u00b7 sol '+e.sol+(e.night?' night '+e.night:'')""",
    """    return (i+1)+'. '+e.code+(e.stars ? ' \\u00b7 '+e.stars+'\\u2605' : '')
         + ' \\u00b7 sol '+e.sol+(e.night?' night '+e.night:'')""",
)

edit("header stamp", "  ASTROBARA V2.12.13", "  ASTROBARA V2.12.14")
edit("meta stamp", 'content="Astrobara V2.12.13 —', 'content="Astrobara V2.12.14 —')
edit("BUILD stamp", "const BUILD = 'V2.12.13';", "const BUILD = 'V2.12.14';")


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

    table = text.split("const ACHV = [")[1].split("\n];")[0]
    pane = text.split("function paintBoardPane(){")[1].split("\n}\n")[0]
    award = text.split("function award(id){")[1].split("\n}")[0]

    checks = [
        ("V2.12.14 stamped three times", text.count("V2.12.14") == 3),
        ("no V2.12.13 left", "V2.12.13" not in text),
        # The table.
        ("twelve awards", table.count("{id:'") == 12),
        ("THE LONG SURVEY is gone", "THE LONG SURVEY" not in text),
        ("ABUNDANCE has the same condition",
         "{id:'all_ratings',    n:'ABUNDANCE',          c:'at every rating'" in table),
        ("ESCAPE VELOCITY exists", "n:'ESCAPE VELOCITY'" in table),
        ("it has a card form", "cf:'every other award earned'" in table),
        ("exactly one capstone", table.count("cap:1") == 1),
        ("the capstone is in neither group",
         "{id:'all_awards'" in table
         and " w:1" not in table.split("{id:'all_awards'")[1]),
        ("still nine in the fusion group", table.count("w:1") == 9),
        # The check, and both hooks.
        ("the check exists", "function checkCapstone(){" in text),
        ("it skips itself", "if(d.cap) continue;\n    if(!got[d.id]) return;" in text),
        ("it awards by literal id, which P10 needs", "award('all_awards');" in text),
        ("checkAchv runs it every turn, ungated",
         "const conn = connectedSet();\n  checkCapstone();" in text),
        ("it is above the self-sufficiency return",
         text.index("checkCapstone();\n") < text.index("if(!G.selfSufficient) return;")),
        ("award runs it too", "if(id !== 'all_awards') checkCapstone();" in award),
        ("no runaway recursion: the capstone does not re-check",
         "if(id !== 'all_awards')" in text),
        # The pane.
        ("one row builder", pane.count("const achvRow = function(d, got){") == 1),
        ("groups skip the capstone", "if(d.cap) continue;                       // the capstone" in pane),
        ("the capstone is drawn below them", "'<div class=\"achvlist caplist\">'+achvRow(d, got)+'</div>'" in pane),
        ("it still counts toward the total", pane.count("if(got) earned++;") == 2),
        # The stars, all three renderers.
        ("three star renderers",
         text.count("e.stars ? '<span class=\"bs\">'") == 2
         and "e.stars ? ' \\u00b7 '+e.stars+'\\u2605' : ''" in text),
        ("legacy rows without a rating render nothing",
         text.count("e.stars ? ") == 3),
        # Two CSS rules, no markup.
        ("two css rules added",
         text.split("</style>")[0].count("{")
         == before.split("</style>")[0].count("{") + 2),
        ("no divs in the markup",
         text.split("<script")[0].count("<div")
         == before.split("<script")[0].count("<div")),
        ("no ids added", text.count(" id=") == before.count(" id=")),
        ("balanced braces", text.count("{") == text.count("}")),
        # Everything since V2.12.0 is still in here.
        ("the board pane still repaints itself", "function refreshBoardPane(){" in text),
        ("the groups are still there", "[1, 'A NIGHT CARRIED ON FUSION']" in text),
        ("endCine is still guarded",
         "if(cineTurn !== null){\n    G.turn = cineTurn; cineTurn = null;" in text),
        ("no 'held a night' left, in any case",
         "held a night" not in text.split("</style>")[1].lower()),
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
