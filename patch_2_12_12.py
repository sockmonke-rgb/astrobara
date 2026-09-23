#!/usr/bin/env python3
"""
ASTROBARA  V2.12.12

The copy said one thing and the code did another.

"Held a night" reads as surviving until sunrise. In the build it means
fusionNightTurns >= 12 — twelve consecutive dark turns on a live reactor, the
same test as the win. A colony that comes through the dark on stored power has
held nothing, by the game's own definition, and gets no award. Nine of the
eleven sit behind `if(!G.selfSufficient) return;`, including the line that
writes the per-site ratings tally, which is why the board also reads
`held none` after a night that plainly happened.

Three vocabularies were in the table for one condition — "a night held",
"a night carried", "self-sufficient" — and two clues named no condition at
all. This states the condition once, at the top of a group, and lets each clue
carry only the part that is its own:

    UNLOCKED · 0 of 11
    A NIGHT CARRIED ON FUSION
      · [LOCKED]  at every rating
      · [LOCKED]  on a 5-star site
      ...
    ANY TIME
      · [LOCKED]  40 capybaras at once

FULL CAPYCITY and POOLS OPEN! are awarded before that return, so they are the
two the grouping separates out — the only two whose clues were already honest.

Two clue strings for five of them, because there are two surfaces. The board has the
group heading above it and takes the short form. The unlock card has nothing
above it, so it takes `cf` — the long form — and a card reading "at every
rating" would only have moved the bug rather than fixed it.

`w` is the flag the grouping reads. verify.js P13 checks it against where
award() actually appears in checkAchv, so the flag cannot drift away from the
gate it describes.

Usage:  python3 patch_2_12_12.py <in.html> <out.html>
"""

import hashlib
import sys

EDITS = []


def edit(name, old, new):
    EDITS.append((name, old, new))


edit(
    "the table: short clue, long clue, and the gate flag",
    """const ACHV = [
  {id:'all_ratings',    n:'THE LONG SURVEY',    c:'a night held at every rating',      g:'\\u25eb'},
  {id:'brutal',         n:'THE DARK SIDE',      c:'a night held on a 5-star site',     g:'*'},
  {id:'twice_rated',    n:'SISTER COLONY',      c:'two different sites, same rating',  g:'\\u2229'},
  {id:'no_losses',      n:'MOISTURIZED',        c:'self-sufficient, nobody lost',      g:'~'},
  {id:'no_brownout',    n:'NOSE ABOVE WATER',   c:'never blacked out',                 g:'\\u25ae'},
  {id:'salvager',       n:'SECOND HELPING',     c:'self-sufficient after stripping',   g:'\\u00d7'},
  {id:'lean',           n:'SKELETON CREW',      c:'under '+ACHV_LEAN_MAX+' structures standing', g:'\\u25a4'},
  {id:'morale_floor',   n:'UNBOTHERED',         c:'morale never under '+ACHV_MORALE,   g:'\\u2248'},
  {id:'big_herd',       n:'FULL CAPYCITY',      c:ACHV_HERD+' capybaras at once',      g:'\\u2592'},
  {id:'full_wallows',   n:'POOLS OPEN!',        c:'three bathing in every wallow',     g:'~'},
  {id:'single_reactor', n:'TWIN SUNS',          c:'a night carried on one reactor',    g:'*'}
];""",
    """// c  — the clue as the board shows it, under a heading that already names the
//      condition. Short, because the heading is carrying the rest.
// cf — the same clue for the unlock card, which floats over the map with
//      nothing above it. Falls back to c where the short form already stands
//      on its own.
// w  — this award is unreachable until the colony has carried a whole night on
//      fusion: checkAchv() returns before it otherwise. The board groups on
//      this, and verify.js P13 checks it against where award() really is.
const ACHV = [
  {id:'all_ratings',    n:'THE LONG SURVEY',    c:'at every rating',                   g:'\\u25eb', w:1,
   cf:'a night carried at every rating'},
  {id:'brutal',         n:'THE DARK SIDE',      c:'on a 5-star site',                  g:'*', w:1,
   cf:'a night carried on a 5-star site'},
  {id:'twice_rated',    n:'SISTER COLONY',      c:'two different sites, same rating',  g:'\\u2229', w:1},
  {id:'no_losses',      n:'MOISTURIZED',        c:'nobody lost',                       g:'~', w:1,
   cf:'a night carried, nobody lost'},
  {id:'no_brownout',    n:'NOSE ABOVE WATER',   c:'never blacked out',                 g:'\\u25ae', w:1,
   cf:'a night carried, never blacked out'},
  {id:'salvager',       n:'SECOND HELPING',     c:'after stripping',                   g:'\\u00d7', w:1,
   cf:'a night carried after stripping'},
  {id:'lean',           n:'SKELETON CREW',      c:'under '+ACHV_LEAN_MAX+' structures standing', g:'\\u25a4', w:1},
  {id:'morale_floor',   n:'UNBOTHERED',         c:'morale never under '+ACHV_MORALE,   g:'\\u2248', w:1},
  {id:'big_herd',       n:'FULL CAPYCITY',      c:ACHV_HERD+' capybaras at once',      g:'\\u2592'},
  {id:'full_wallows',   n:'POOLS OPEN!',        c:'three bathing in every wallow',     g:'~'},
  {id:'single_reactor', n:'TWIN SUNS',          c:'a night carried on one reactor',    g:'*', w:1}
];
// The board reads this in order. A group with nothing in it is not drawn, so
// the headings cannot appear over an empty list.
const ACHV_GROUPS = [
  [1, 'A NIGHT CARRIED ON FUSION'],
  [0, 'ANY TIME']
];""",
)

edit(
    "the board groups on the flag and names the condition once",
    """  let list = '<div class="achvlist">';
  for(let i=0;i<ACHV.length;i++){
    const d = ACHV[i], got = !!a.got[d.id];
    if(got) earned++;
    list += '<div class="ar'+(got?' got':'')+'">'
         +  '<span class="ag2">'+(got ? d.g : '\\u00b7')+'</span>'
         +  '<span class="atx"><span class="an">'+(got ? d.n : '[LOCKED]')+'</span>'
         +  '<span class="ac">'+d.c+'</span></span></div>';
  }
  list += '</div>';""",
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
)

edit(
    "the unlock card takes the long clue",
    """    + '<span class="a3">'+def.c+'</span></span>';""",
    """    + '<span class="a3">'+(def.cf || def.c)+'</span></span>';""",
)

edit(
    "the group heading",
    """#pane-board .bhead{margin-top:11px;padding-top:8px;border-top:1px solid var(--rule);
  font-size:calc(9px * var(--ts));letter-spacing:.16em;color:var(--dim);margin-bottom:5px;}""",
    """#pane-board .bhead{margin-top:11px;padding-top:8px;border-top:1px solid var(--rule);
  font-size:calc(9px * var(--ts));letter-spacing:.16em;color:var(--dim);margin-bottom:5px;}
/* The condition a group of awards shares, said once above them instead of
   nine times inside them. Gold, because it is the thing being asked of you,
   and a step under the UNLOCKED count so it reads as a subheading of it. */
#pane-board .ghead{margin-top:9px;margin-bottom:2px;
  font-size:calc(8.5px * var(--ts));letter-spacing:.14em;color:var(--sunlit);opacity:.85;}""",
)

edit(
    "the empty board says it the same way",
    """    html = '<div class="bnone">No colony has held a night yet.<br><br>'""",
    """    html = '<div class="bnone">No colony has carried a night yet.<br><br>'""",
)

edit(
    "so does the exported board",
    """  const txt = 'ASTROBARA \\u2014 colonies that held a night\\n' + boardText();""",
    """  const txt = 'ASTROBARA \\u2014 colonies that carried a night\\n' + boardText();""",
)

edit(
    "and the comment over the gate stops using the ambiguous word",
    """  // Everything below is gated on having held a night, which is the unit of
  // success this whole ladder is built on.""",
    """  // Everything below is gated on having CARRIED a night — fusionNightTurns
  // >= 12, the same test as the win — which is the unit of success this whole
  // ladder is built on. Not the same thing as reaching sunrise: a colony can
  // come through the dark on stored power and earn none of these. The board
  // groups on ACHV[].w to say so once, rather than in every clue.""",
)

edit(
    "and the comment over finish()",
    """  // that reached self-sufficiency and then died of thirst still held a night.""",
    """  // that reached self-sufficiency and then died of thirst still carried one.""",
)

edit("header stamp", "  ASTROBARA V2.12.11", "  ASTROBARA V2.12.12")
edit("meta stamp", 'content="Astrobara V2.12.11 —', 'content="Astrobara V2.12.12 —')
edit("BUILD stamp", "const BUILD = 'V2.12.11';", "const BUILD = 'V2.12.12';")


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
    pane = text.split("function paintBoardPane(){")[1].split("\n}")[0]

    checks = [
        ("V2.12.12 stamped three times", text.count("V2.12.12") == 3),
        ("no V2.12.11 left", "V2.12.11" not in text),
        # The table still has eleven rows and every id survived.
        ("eleven awards", table.count("{id:'") == 11),
        ("nine carry the flag", table.count("w:1") == 9),
        ("the two ungated ones do not",
         "n:'FULL CAPYCITY'" in table and "n:'POOLS OPEN!'" in table
         and "c:ACHV_HERD+' capybaras at once',      g:'\\u2592'}" in table
         and "c:'three bathing in every wallow',     g:'~'}" in table),
        ("five long forms for the card", table.count("cf:'a night carried") == 5),
        # Mark's two calls on the mockup.
        ("SISTER COLONY keeps the full wording",
         "c:'two different sites, same rating'" in table),
        ("TWIN SUNS keeps the verb",
         "c:'a night carried on one reactor'" in table),
        # The groups.
        ("two groups", text.count("const ACHV_GROUPS = [") == 1
         and "[1, 'A NIGHT CARRIED ON FUSION']" in text
         and "[0, 'ANY TIME']" in text),
        ("the board reads the flag", "if((d.w ? 1 : 0) !== want) continue;" in pane),
        ("an empty group draws no heading", "if(!rows) continue;" in pane),
        ("the heading is drawn", "'<div class=\"ghead\">'+ACHV_GROUPS[gi][1]+'</div>'" in pane),
        ("the count still runs over every award", pane.count("if(got) earned++;") == 1),
        ("the card takes the long form", "(def.cf || def.c)" in text),
        # One vocabulary on every surface: no user-facing string still says
        # "held a night", which is the phrase that caused the report.
        ("no 'held a night' left in the copy",
         "held a night" not in text.split("</style>")[1]),
        ("the empty board says carried",
         "No colony has carried a night yet." in text),
        ("the export says carried",
         "colonies that carried a night" in text),
        ("nothing else reads d.c bare", text.count("+d.c+") == 1),
        # One CSS rule, no markup.
        ("one css rule added",
         text.split("</style>")[0].count("{")
         == before.split("</style>")[0].count("{") + 1),
        ("the rule is scoped to the board", "#pane-board .ghead{" in text),
        # The static markup, not the strings the board builds at runtime: the
        # new group heading is one of those, so a whole-file count would move.
        ("no divs in the markup",
         text.split("<script")[0].count("<div")
         == before.split("<script")[0].count("<div")),
        ("exactly one runtime div added",
         text.count("<div") == before.count("<div") + 1),
        ("no ids added", text.count(" id=") == before.count(" id=")),
        ("balanced braces", text.count("{") == text.count("}")),
        # Everything since V2.12.0 is still in here.
        ("endCine is still guarded",
         "if(cineTurn !== null){\n    G.turn = cineTurn; cineTurn = null;" in text),
        ("the replay still fits the view", "\n  fitView();\n" in text),
        ("the card still cannot show under an overlay",
         "if(achvShowing || !achvQueue.length || achvBlocked()) return;" in text),
        ("the clip still runs to the stage edge", "Math.min(0, offX)" in text),
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
