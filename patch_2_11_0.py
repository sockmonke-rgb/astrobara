#!/usr/bin/env python3
"""V2.10.7 -> V2.11.0. A thin crest floors the rating at 3 stars; contrast and
large glyphs on by default. Guarded: every replacement must match exactly once."""
import sys, pathlib
src, dst = sys.argv[1], sys.argv[2]
h = pathlib.Path(src).read_text()

def rep(old, new, count=1):
    global h
    n = h.count(old)
    assert n == count, f'expected {count} match(es), found {n}:\n{old[:160]}'
    h = h.replace(old, new)

rep('ASTROBARA V2.10.7', 'ASTROBARA V2.11.0')
rep('content="Astrobara V2.10.7', 'content="Astrobara V2.11.0')
rep("const BUILD = 'V2.10.7';", "const BUILD = 'V2.11.0';")

# The rating is an average of six factors, and ice carries 44% of it. A site can
# therefore be generous with ice, be handed a heavy lander, and still be brutal
# to power, because the crest it has to put arrays on is four columns wide — and
# the average votes that away. Measured on VAST-GATE-900: crest 4, ice close and
# plentiful, rated 2 stars at a score of 0.240 against a 2-star cut of 0.235.
# Power is not a factor that averages: below five sunlit columns there is no
# amount of ice that makes the nights easy.
rep("""  const CUT = [0.235, 0.313, 0.437, 0.550];
  let stars = 1;
  while(stars < 5 && score >= CUT[stars-1]) stars++;""",
"""  const CUT = [0.235, 0.313, 0.437, 0.550];
  let stars = 1;
  while(stars < 5 && score >= CUT[stars-1]) stars++;
  if(M.eternal < CREST_FLOOR_COLS && stars < CREST_FLOOR_STARS) stars = CREST_FLOOR_STARS;""")
rep("""function rateDifficulty(M){""",
"""// A crest this thin is a hard site whatever else it has going for it.
const CREST_FLOOR_COLS = 5, CREST_FLOOR_STARS = 3;
function rateDifficulty(M){""")

# Both were switchable because they were guesses; neither has a downside on a
# phone in daylight, which is where this is played.
rep("""const OPT = { contrast:false, bigGlyph:false, grid:true, reveal:false, autorotate:false,""",
    """const OPT = { contrast:true, bigGlyph:true, grid:true, reveal:false, autorotate:false,""")

pathlib.Path(dst).write_text(h)
print('patched ->', dst)
