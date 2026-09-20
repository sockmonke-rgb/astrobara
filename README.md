# Astrobara

A turn-based lunar survival colony builder. A herd of capybaras holds a colony
on the Shackleton crater rim, where the antagonist is the night.

One HTML file. No dependencies, no build step, no network. Open it and play.

**V2.10.2** · MIT · Mark Florentino LLC and Kittenmancer

---

## The problem

A lunar day is 29 turns and 15 of them are lit. During the other 14 your arrays
make nothing, and habitat heating goes from 3 power per turn to 9. Everything
you build during the light is a bill that comes due in the dark.

The two resources you need are scarce in opposite ways. Water ice sits deep in
the crater basin, in shadow that never lifts. Helium-3 sits shallow, in the
sunlight on the rim. You cannot put your colony in one place and have both.

The decision the game is built around is what to switch off. Mines and
processors can idle and cost nothing. Life support and heating cannot. Working
out what you can carry through fourteen dark turns, and shedding the rest before
the bank runs dry, is the whole game. A reactor ends the argument permanently,
but it costs 140 power and 25 helium-3 to build, and you have to survive long
enough to bank that.

Most colonies die the same way: habitats built during the light, without
battery capacity to carry them through the dark.

## The visual language

Nine glyphs, none of them letters or digits, the same on the map as in the
build menu.

| Glyph | Build | Costs | Does |
|---|---|---|---|
| `▒` | DIG | 4 power, 1 labour | opens the tile, then costs nothing |
| `×` | CLEAR | free, 1 labour | strips a building for half its cost, or backfills a tunnel |
| `◫` | ARRAY | 22 power, 1 labour | +13/turn while lit, nothing at night |
| `▮` | BATTERY | 20 power, 1 labour | +120 storage, no upkeep |
| `∩` | HABITAT | 45 power, 25 water, 2 labour | houses 4 · heating 3/turn by day, 9 at night · needs 3 rows of cover |
| `≋` | ICE MINE | 30 power, 8 water, 2 labour | draws 7/turn while running, nothing when idled |
| `▤` | PROCESSOR | 50 power, 2 labour | draws 22/turn while running, your heaviest load |
| `~` | WALLOW | 18 power, 70 water, 1 labour | 4 water/turn, no power · +25 morale beside a habitat |
| `*` | FUSION | 140 power, 25 He-3, 3 labour | burns 1 He-3/turn for +90 power, day or night |

**Idled machines draw grey**, whatever they are, so the thing you scan the map
for reads at a glance. Unpowered draws alarm red, which outranks both.

Two things are drawn rather than lettered: the wallow's basin, because standing
water reads as itself, and the capybaras in a habitat, because the herd is who
you are playing for. A wallow beside a habitat shows a capybara sitting in it
with a citrus on its head — the tile's way of saying it is earning its +25.

**A glow means fusion is running** and that structure is one of the loads it is
carrying. Daylight produces no glow — nothing on this surface makes its own
light. The lit tiles at night are exactly the ones spending helium-3, so an
idled processor goes dark the turn you shed it.

**A warm crest line means sunlight.** The line along the terrain is rim light
and only falls on columns the sun actually reaches, tested with the same
function the power model uses. Shadowed ground keeps a dim neutral edge.

## Everything is deterministic

The only `Math.random()` in the file picks a seed for a new game. Nothing after
that is random. The same seed and the same moves produce the same colony, the
same morale, the same deaths, every time.

Morale, for instance, is a target computed fresh each turn from a base of 50:
a wallow beside a habitat is +25, positive power net +10, load shedding −12, a
brownout −35, running dry −25, a habitat under thin cover −10, and being down to
one capybara −20, because herd animals do badly alone. Morale then closes 35% of
the gap to that target each turn. It never snaps, it chases — which is why it
appears to drift when nothing obvious has changed.

Morale is not cosmetic: `work = 0.5 + morale/100` scales extraction, so a shed
turn costs you output for several turns afterwards.

## Playing

- Pick a tool, tap a tile, then press the **action cell** in the lane. It names
  what will happen — DIG, BUILD, STRIP, BACKFILL — or, in two words at most,
  why it cannot.
- Tap a mine, processor, wallow or reactor to get **IDLE** or **RESTART** in the
  same cell. With nothing selected the cell offers **IDLE ALL**.
- The **ledger** (tap the day counter) lists the turn's power and water flows,
  what the night will cost, and how many structures are standing.
- The **arrows** step the selected tile one at a time and keep it in view.
- A drag that starts on or just beside the build column scrolls the column and
  never the map.
- **LEDGER**, under the day counter, shows the current turn's power and water
  arithmetic, line by line, and the log. Nothing in this game is hidden from
  you.
- Pinch to zoom, drag to pan. **FIT**, a double tap, or **DISPLAY · Reset map
  view** returns to the whole colony. A new colony opens on its crest.
- When a colony ends, the card reads itself out: the verdict fills from the
  top, the run types line by line, and the buttons appear once it is done. A
  tap speeds it up; a second tap ends it.
- Progress saves to local storage automatically. A saved run does not carry
  across builds. Achievements carry across every build within a major version
  and start fresh when the major version changes (V2 to V3). The board always
  carries, and names the build each row was set on.

## Tools

Everything else lives in one panel, `[≡]`, in five tabs.

- **SURVEY** shades tiles by ore grade.
- **IDLE** lists every class of machine with its draw and yield, and switches a
  whole class at once — because idling mines saves power and silently stops the
  water.
- **DISPLAY** — below.
- **BOARD** lists colonies that carried a whole night on fusion, with the site
  code for each so any run on it can be played again, and offers the rows as
  text. Eleven achievements are listed under it, locked ones included.
- **RUN** shows this site's code and difficulty, takes a code to land somewhere
  else, or lands somewhere random. Codes look like `WORD-WORD-###`; any words
  at all also make a site. A code with a slip in it is flagged, with the code
  it was probably meant to be.

## Sites

Every site comes from a seed and is written as a pronounceable code,
`WORD-WORD-N`, rated one to five stars: MILD, FAIR, LEAN, HARSH, BRUTAL. Codes
are exact — they round-trip to the same site on any device, in any build.
`SHACKLETON`, the original hand-made map, is the default. `SEEDS.txt` lists two
typical sites per rating.

## Display options

Switches: high-contrast ore, larger glyphs, tile grid lines, glass panels, FPS
meter, objective hints, reveal map (review only), and rotate view in portrait.

- **Objective hints** are off by default. Working out that the night needs
  batteries is the game. The offer is made once, after a colony is lost.
- **Glass panels**, on by default: the map runs full-bleed and the panels float on it. Off:
  the V2.9.4 layout, panels beside the map. The splash, the verdict and the
  portrait gate follow the same setting. With
  `prefers-reduced-transparency` set, the panels keep the floating layout but
  draw opaque.
- **Controls** sets which hand the layout is for, and moves every control
  together:

  | | lane | build column |
  |---|---|---|
  | LEFT | arrows · action · description · FIT | left |
  | RIGHT | FIT · description · action · arrows | right |
  | BALANCED | arrows · FIT · description · action | right |

  BALANCED gives each thumb one job: arrows on the left, building on the right.
  FIT is in the lane with glass on, and a chip over the map with glass off.
- **Text size** cycles AUTO / S / M / L. A tile is the same size at every
  setting; the view pans instead.
- **FPS meter** shows `now · low · avg` and a count of dips under 30 — a
  turn-based game needs nothing more than a steady 30. It skips
  two seconds of warm-up, restarts when glass is toggled, and costs nothing
  while off.
- **Reset map view** and **Fix touch alignment** — the second for when iOS
  standalone mode desynchronises the hit test.
- **Copy diagnostics** puts one block on the clipboard: build, site, turn, view
  and page measurements, text scale, frame rate and each dip with what was open
  at the time, where the last eight touches began and what they became, every
  option, achievements, board and log. Paste it with any bug
  report.

The pane also reports what the map is doing — zoom, cell against base cell,
stage size against map size — which is what to screenshot if the view ever
looks wrong.

## Building on it

The file is meant to be read. Constants live in `CFG` and `COST` near the top
and are commented with what they mean rather than what they are. Changes are
made with guarded patch scripts — assertion-based replacements that fail loudly
if the source has moved — and verified headlessly before publishing.

### Versions

- **V2.x — development.** Anything can change, including the model.
- **V3.0-RC*n* — release candidates.** Presentation only: layout, type, colour,
  copy, animation. Nothing that changes how a turn resolves — costs, yields,
  growth, morale, the night, site generation, achievement conditions. An RC
  that needs a gameplay fix goes back to V2.x.
- **Achievements** are cleared once when the major version changes, and never
  between builds inside one. RCs never wipe them.

Every build carries a version watermark in the splash and in `const BUILD`. When
reporting a bug, that string is the most useful thing you can include — or,
better, Copy diagnostics, which starts with it.

`preflight.py` runs Tier 0 of the test plan: twelve static checks that need no
device, from the script parsing to every published seed regenerating its site.

    python3 preflight.py astrobara-v2_10_2.html SEEDS.txt

It needs `seedcheck.js` beside it and Node on the path.

## License

MIT. Copyright (c) 2026 Mark Florentino LLC and Kittenmancer.
