# Astrobara — test plan

**Plan version 1.4** · 20 September 2026 · covers Astrobara V2.10.2

The single HTML file is the unit under test; there is no build step to verify.
The plan is versioned separately from the game: quote both when reporting, as in
"plan 1.3 against V2.10.0". Revision history is at the foot of the document.

Four tiers, in order of cost:

- **Tier 0 — pre-flight.** Static checks on the file. No device, runs in seconds.
  Nothing is handed over until these pass.
- **Tier 1 — view and text.** The class of bug that produced V2.0.4 through
  V2.7.3, and most of the glass line: a view you could not escape, text that did
  not fit, a control you could not reach, and two crashes. About fifteen minutes.
- **Tier 2 — model and loop.** The simulation, and the tiles that report it.
  About twenty minutes.
- **Tier 3 — achievements.** Proof that all eleven can actually be earned. Four
  runs, an hour or so. Run this before any release that changes the model.

The build stamp appears on the splash watermark, in the ledger header, and in
`const BUILD`. Record it with every result.

---

## Which tiers, when

| Build | Tier 0 | Tier 1 | Tier 2 | Tier 3 |
|---|---|---|---|---|
| V2.x dev, layout or copy only | every build | the checks the change touches | — | — |
| V2.x dev, model change | every build | the checks the change touches | all | the runs it could affect |
| V3.0-RC1 | yes | all, glass on and off | all | all |
| V3.0-RC2 onward | yes | all, glass on and off | — | — |

**The release-candidate rule.** An RC may change how the game looks — layout,
type, colour, copy, animation — and nothing about how a turn resolves: costs,
yields, growth, morale, the night, site generation, achievement conditions. That
is why a later RC does not need Tiers 2 and 3 again. An RC that needs a gameplay
fix is not an RC; it goes back to V2.x.

**Achievements across builds.** They carry across every build within a major
version, RCs included, and are cleared once when the major version changes
(V2 to V3). See A2.

---

## Tier 0 — pre-flight (static)

| # | Check | How |
|---|---|---|
| P1 | Script parses | Extract the inline `<script>` and run `node --check` |
| P2 | One source for the version | The header comment, the `<meta name="description">` and `const BUILD` all agree. Reads `V2.10.0` and `V3.0-RC1` alike |
| P3 | No duplicate element IDs | Collect `id="..."`, assert set size equals count |
| P4 | Every `getElementById("x")` target exists in the markup | Cross-reference against P3's set |
| P5 | Tags balance inside `#app` | Stack-walk `<div>`; the count must match the previous build's |
| P6 | Storage keys | Only `astrobara.run`, `astrobara.board`, `astrobara.achv`. Any fourth key is a regression |
| P7 | No network at all | No `fetch`, `XMLHttpRequest`, `src=http`, `@import`, or webfont URL |
| P8 | Every `font-size` is scaled | Each resolves through `var(--ts)` or `var(--tsb)`; zero bare `px` font sizes |
| P9 | Every `touch-action` is justified | Each either names `pinch-zoom` or is a drag grip. A list of pan gestures alone silently refuses the system zoom |
| P10 | Achievement table integrity | Ids unique, names unique, every id in `ACHV` is awarded somewhere in `checkAchv`, and every `award('...')` names a declared id |
| P11 | Seed round-trip | Every code in `SEEDS.txt` regenerates through `codeToSeed` to the site and star rating the file claims |
| P12 | CSS braces balance | Brace-count the `<style>` block |

P8 would have caught V2.6.2's sky label, unreadable because it alone did not
scale. P9 would have caught V2.7.1 without a device. P10 catches an achievement
renamed out from under its check.

---

## Tier 1 — view and text

Three separate zoom mechanisms, routinely confused with one another:

| mechanism | what it is | controlled by |
|---|---|---|
| map zoom | pinch on the map | the game; FIT resets it |
| text size | the app's own scaling | TOOLS · DISPLAY · Text size |
| system zoom | the browser's page zoom | pinch anywhere that is not the map |

Run Tier 1 with **glass on**, then again with **TOOLS · DISPLAY · Glass panels
off**. They are two layouts, and a fix to one has broken the other before.

### Frame rate

Glass blurs a live canvas, which is the expensive case. Turn on **TOOLS ·
DISPLAY · FPS meter** and read `now · low · avg`. The bar is a steady **30**:
this is a turn-based game and nothing in it needs more. The meter counts a
second under 30 as a dip, and Copy diagnostics lists each one with what was
open at the time.

- **F1** — baseline. Glass OFF, FIT, then end ten turns. Note the low.
- **F2** — glass ON, same ten turns from the same seed. Note the low.
- **F3** — pan the map continuously for ten seconds with glass on. Panning
  redraws the canvas every frame under every pane, so this is the worst case.
- **F4** — open the tools panel and the ledger over the map and pan again. Now
  two more surfaces are compositing.
- **F5** — the same four with the text size at L, which enlarges every pane.
- **F6** — a night turn with a built-up colony (thirty crew or more), glass on,
  tools open.

Pass: the low stays at or near 30 in F2 to F6. Report the **low**, not the
average — an average hides exactly the stutter worth finding. *First evidence,
V2.9.7: turn 140, night, 41 crew, tools open, glass on — low 29, two dips.*

### Zoom stability

Hold each pinch for a slow count of five. A flick will not reproduce either
crash; both needed sustained gesture events.

- **V1 — pinch in on the tools panel body.** Hold at full zoom, pan around,
  release. Repeat three times without reloading.
- **V2 — pinch out on the same panel**, from zoomed and from 100%. Below 100% it
  should refuse to go further, not crash. *Zoom out is its own test, not the
  same test backwards.*
- **V3 — both directions on the ledger**, opened from the day counter.
- **V4 — both directions on the board tab** with several achievements listed.
- **V5 — both directions on the top readout, the build column, the status bar.**

Pass: the page zooms, nothing reloads, nothing goes blank.
**A reload or a white screen is the crash — stop and report the build.**

Guards V2.7.2 (pinch in: canvas reallocated every frame, layout re-entered
without bound) and V2.7.3 (pinch out: a one-sided scale guard ran the scroll
reset on every scroll event, and the scroll reset fires scroll events itself).

### Zoom function

- **V6** — zoomed to about 200%, every line in the tools panel is reachable by
  panning. Nothing is permanently off-screen.
- **V7** — pinching on the map zooms the map, not the page.
- **V8** — dragging the tools panel by its title bar still moves the panel.

Guards V2.7.1.

### Text size

For each of S, M, L and AUTO:

- **V9** — the top readout fits without scrolling at AUTO, M and L. At larger
  sizes it may scroll sideways, but every figure must be reachable; clipped
  with no way to see it is a failure. Guards V2.6.0 and V2.9.14, where LABOR
  was cut off at 135%.
- **V10** — the objective line wraps rather than cutting.
- **V11** — build rows are two lines each, name above cost, all the same height.
- **V12 — the map tiles are the same size at every setting.** Open TOOLS ·
  DISPLAY and read `cell`; it must not change between settings. This is the
  single most useful number in the app for layout bugs.
- **V13** — the arrow row is no shorter than a build row and comfortably
  thumb-sized.

Guards V2.5.3 (constant cell), V2.6.0 (readout clipping), V2.6.4 (arrows).

### The view cannot be lost

- **V14** — FIT is always visible: in the bottom lane with glass on, over the
  bottom-right of the map with glass off. It sits above the tools panel, the
  ledger and an achievement banner.
- **V15** — pinch the map right in, then FIT: the whole colony returns. The
  arrow keys bring the view with the selection. TOOLS · DISPLAY · Reset map view
  does the same as FIT.

Guards V2.0.4 and V2.1.2, where a zoomed map had no reachable way back.

### Every control can be reached

For each handedness — BALANCED, LEFT, RIGHT — with glass on and with glass off:

- **V16** — scroll the build column to its end: FUSION, the last row, takes a
  tap and arms. Guards V2.9.7, where the arrow pad floated over it.
- **V17** — start a drag on the map just beside the build column, including
  the strip between the column and the screen edge: the column scrolls and the
  map does not move. The `touch` line in Copy diagnostics should read `scroll`,
  not `pan`. Guards V2.9.8.
- **V18** — turn glass off: the panels sit beside the map and are opaque, and
  the map is boxed rather than full-bleed. Turn it back on: the panels float
  again. Nothing is left transparent or stranded in either direction. Guards
  V2.9.7, where turning glass off left a transparent build column.
- **V19** — the tools button, shut, is a rounded pill, not a square inside a
  rounded shadow. Guards V2.9.11.

### Typing a site code

- **V21** — on the RUN tab, type `SCRAP-REGOLITH-192`. The field flags SCRAP,
  offers SCARP-REGOLITH-192, and tapping the offer fills it in. The warning and
  LAND THERE are in view without scrolling the panel by hand. While typing
  anything that is not yet a code, the line under the field reads only
  `WORD-WORD-###` — never a code you did not type. Guards V2.10.1 and V2.10.2.
- **V22** — type words with spaces and digits into the same field: the spaces
  appear, no turn ends, no build tool arms, SURVEY does not toggle. Guards
  V2.10.1, where Space in the field ended a turn.

### The end card

- **V20** — lose a colony. Nothing on the card can be pressed until it has
  finished; one tap speeds it up, a second ends it. The run sits in two
  columns, the hints line is one line at AUTO, M and L, and the attribution
  sits above the buttons. Guards V2.9.9 to V2.9.11.

### The three do not interfere

- Set text size L, system-zoom in, pinch the map, tap FIT. The map returns to
  reference scale; text size is still L; page zoom is unaffected.
- Rotate to portrait and back at each text size with the page zoomed. Nothing is
  stranded off-screen.

### Fixtures

| Context | Portrait | Landscape | Binds on |
|---|---|---|---|
| iPhone, in-app viewer | 402×~700 | ~874×~325 | height |
| iPhone, full-screen browser | 402×844 | 874×390 | height |
| iPad | 768×1024 | 1024×768 | width in portrait |
| Rotated view (portrait gate ON) | 402×844 | — | both |

---

## Tier 2 — model and loop

### The ledger tells the truth

- **M1** — solar in, minus life support, heat, mines and processors, equals the
  power net in the readout.
- **M2** — idle a processor; upkeep drops by 22 next turn.
- **M3** — the `night` line appears under both POWER and WATER, and goes red
  when the bank will not cover it.
- **M4** — run a night short of power: a brownout is announced and morale falls.
- **M5** — morale is deterministic. Note the seed, play ten turns, restart the
  same seed, repeat the same moves: the same morale to the decimal.

### Actions

- **M6** — CLEAR costs nothing but labour, and the button states the salvage
  before you commit (`STRIP WALLOW · +9p +35w`).
- **M7** — strip a structure: power and water rise by exactly half its cost,
  power capped at the bank.
- **M8** — with CLEAR held, a running machine offers **both** IDLE and STRIP.
  (Guards V2.3.4, where CLEAR shadowed idling for the whole session.)
- **M9** — build on an occupied tile: the action reads the reason, not silence.

### The herd

- **M10** — a habitat shows capybaras, and the count matches crew divided across
  habitats.
- **M11** — a wallow beside a habitat shows a bather with a citrus; one built
  away from a habitat does not.
- **M12** — bathers plus housed capybaras never exceed the crew figure.
- **M13** — at most three bathe per wallow, never more than half the herd.
- **M14** — capybaras behind others are dimmer and never merge into one shape.

### The board

- **M15** — reach self-sufficiency: a banner slides in from the lower left.
- **M16** — tap a banner: it holds and says TAP TO DISMISS. Tap again, it goes.
  Several at once queue rather than overlapping.
- **M17** — TOOLS · BOARD lists the run with the right site code, sol, crew and
  power. Locked rows read `[LOCKED]` and their condition.
- **M18** — COPY AS TEXT puts the board on the clipboard.
- **M19 — storage across builds.** Note the unlocked count and the board rows,
  open the next build of the same major version, check again. Both should be
  unchanged. A drop means this host scopes storage per file, and the export is
  the only record. Worth re-testing on every host, not every build.
- **M24** — the ledger's `structures standing` matches a count of the
  structures on the map, idled ones included.

### Platform

- **M20** — portrait shows the gate; the rotate control on it turns the view, and
  the same switch in TOOLS · DISPLAY turns it back.
- **M21** — reload mid-run: same turn, same colony, same site code.
- **M22** — start a colony by code from `SEEDS.txt`; the rating matches the file.
- **M23** — the file opens from `file://` in aeroplane mode.

---

## Tier 3 — achievements are obtainable

Eleven achievements. A release that changes the model can make one unreachable
without any error appearing anywhere — which is exactly what happened to
SOL SURVIVOR, removed in V2.5.0 after an audit found no path to it at all.

Clear `astrobara.achv` before starting, or read the count in TOOLS · BOARD and
work from there.

### Run A — the clean colony · `SLOPE-BASALT-82` (3★)

Play to self-sufficiency without losing a capybara, without a brownout, and
keeping morale above 60 the whole way. Strip at least one structure en route,
and carry the night on a single reactor.

| Earns | Condition |
|---|---|
| MOISTURIZED | self-sufficient, nobody lost |
| NOSE ABOVE WATER | never blacked out |
| UNBOTHERED | morale never under 60 |
| SECOND HELPING | self-sufficient after stripping |
| TWIN SUNS | a night carried on one reactor |
| SKELETON CREW | under 20 structures standing |

SKELETON CREW and MOISTURIZED pull against each other: the safe play is more
batteries. The floor is about nine structures, so 20 should be comfortable —
**if this one will not come, say so, because 20 is a guess that has never been
tested against a real colony.** The ledger's `structures standing` shows the
count as you go.

Then keep playing the same colony: grow to 40 capybaras (ten habitats) with
three bathing in every wallow.

| Earns | Condition |
|---|---|
| FULL CAPYCITY | 40 capybaras at once |
| POOLS OPEN! | three bathing in every wallow |

POOLS OPEN! needs crew ≥ 6 × the number of wallows, so build few wallows or a
large herd.

### Run B — the second 3★ · `BLACK-WALL-719`

Reach self-sufficiency again, nothing else required.

| Earns | Condition |
|---|---|
| SISTER COLONY | two sites at the same rating |

### Run C — brutal · `GLASS-HERD-935` (5★)

| Earns | Condition |
|---|---|
| THE DARK SIDE | a night held on a 5-star site |

### Run D — fill the scale · `HEARTH-HELIUM-752` (1★), `PALE-PROBE-299` (2★), `SLOW-PEAK-538` (4★)

Three more colonies to self-sufficiency, one at each remaining rating.

| Earns | Condition |
|---|---|
| THE LONG SURVEY | a night held at every rating |

### Bookkeeping checks

- **A1** — replaying an earned site awards nothing new. Twenty turns on an
  already-held site must not re-award SISTER COLONY.
- **A2** — an achievement survives any build within a major version, release
  candidates included, and is cleared once when the major version changes.
  `astrobara.run` is cleared on every build change; `astrobara.board` never is.
  The rule is checked headlessly with each build that touches it; on a device,
  read the count before and after moving between two builds of one major
  version.
- **A3** — the count in TOOLS · BOARD matches the rows shown as unlocked.
- **A4** — a locked row shows its condition, so there is something to aim at.

### If one will not come

Say which, and what the colony looked like when you gave up. An unreachable
achievement is a model bug, not a player failure — the SOL SURVIVOR audit found
the morale target at one capybara was 65 against a growth gate of 70, so no
death path left it earnable. The same arithmetic can bite any of these.

---

## Running Tier 0

`preflight.py` implements P1–P12. It needs `seedcheck.js` beside it and a copy
of `SEEDS.txt`:

    python3 preflight.py astrobara-v2_10_1.html SEEDS.txt

It exits non-zero on any failure and prints the evidence for every check, not
just a verdict, so a pass is auditable. Run it on every build before the build
leaves the machine it was made on.

---

## Does Astrobara need a probe?

**Not a full one.** Ink Strike needed a probe because its gate verdicts were
invisible — there was no way to see why a stroke was rejected. Astrobara's model
is already legible:

- the **LEDGER** shows the turn's arithmetic line by line, which is what a probe
  would have printed;
- the **LOG** tab files each turn's events under the numbers that produced them;
- **TOOLS · DISPLAY** reports zoom, cell against base cell, and stage against map
  size — the three numbers that identify every layout bug this project has had.

What is missing is **portability**. A tester can see all of it and cannot send
any of it. The board has COPY AS TEXT; nothing else does.

**Built in V2.8.0: TOOLS · DISPLAY · Copy diagnostics.** One block covering the
build stamp, the site code and seed, the turn and colony state, the view
numbers, the text scale requested against the scale applied, the page and
visual viewport with the current page zoom, the frame rate with each dip and
what was open at the time, where the last eight touches began and what they
became, every display option, the unlocked achievement ids, the ratings tally,
the board size, **which storage keys actually exist on this host**, and the last
ten log lines.

Paste it into any report. Items 1 to 4 of *Reporting a failure* below are all in
it, which is the point: nothing in a report should have to be typed out by hand
and got wrong.

---

## Reporting a failure

1. The build stamp, from the splash or the ledger header.
2. Orientation, text size setting, glass on or off, and the site code.
3. The three lines from TOOLS · DISPLAY, if the complaint is about the view.
4. The ledger, if the complaint is about a number.
5. A screenshot only if the complaint is visual — overlap, clipping, position.

For a suspected model bug, say the seed and the moves. The simulation is
deterministic, so a seed and a move list reproduces it exactly.

---

## Revision history

| Plan | Date | Against | Changes |
|---|---|---|---|
| 1.0 | 15 Sep 2026 | V2.7.3 | First issue. Tier 0 pre-flight (P1–P12), Tier 1 view and text (V1–V15), Tier 2 model and loop (M1–M23), Tier 3 achievements (Runs A–D, A1–A4). |
| 1.1 | 15 Sep 2026 | V2.8.0 | Tier 0 automated as `preflight.py`. Probe section replaced: COPY DIAGNOSTICS built in V2.8.0. |
| 1.2 | 17 Sep 2026 | V2.9.4 · V2.9.6-GLASS | Added frame-rate checks F1–F5 for the glass branch, which blurs a live canvas. Report the low, not the average. |
| 1.3 | 19 Sep 2026 | V2.10.0 | Glass is the main line. Added *Which tiers, when* and the release-candidate rule. Tier 1 runs with glass on and off. Frame-rate bar set at 30; F6 added. V9 tightened to fit at L. New V16–V20 for fixes made on the glass line that the plan did not catch. A2 and M19 rewritten: achievements carry within a major version. M3 follows the *night* wording; M24 added for the structure count. MAXIMUM OCCUPANCY renamed FULL CAPYCITY. |
| 1.4 | 20 Sep 2026 | V2.10.1 · V2.10.2 | V21 and V22 for the site field: mistyped codes, and keyboard shortcuts firing while typing. |

When a build fixes something this plan did not catch, add the check here in the
same commit as the fix, and note the build it was first seen in.
