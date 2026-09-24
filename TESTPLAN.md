# Astrobara — test plan

**Plan version 1.19** · 23 September 2026 · covers Astrobara V2.12.13

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

Two more run in `verify.js` rather than `preflight.py`, because they read the
source the same way but belong beside the rendered checks:

| # | Check | How |
|---|---|---|
| P13 | The grouping flag matches the gate | Split `checkAchv()` on `if(!G.selfSufficient) return;`; every `award()` below it must carry `w:1` in `ACHV`, and none above it may |
| P14 | A short clue declares its card form | A clue under four words, or opening with a preposition, must also declare `cf` — the board has a heading above it and the unlock card does not |

P13 exists because the gold group heading is a promise about the code: a flag
on the wrong side of that return prints the V2.12.12 bug back out in gold.

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
- **F7** — *fog, on a site you have barely opened.* A new colony has the most
  unsurveyed ground it will ever have, and the glass fog blurs the canvas a
  second time under a path of its own. Glass ON, fog ON, tone ASH: land, FIT,
  and pan continuously for ten seconds. Then repeat with **Glass panels** off
  and note both lows — that pair is the number that decides whether the glass
  fog stays.
- **F8** — the same pan at tone SMOKE, which draws the largest sheet, and with
  the tools panel open over it.

Pass: the low stays at or near 30 in F2 to F8. Report the **low**, not the
average — an average hides exactly the stutter worth finding. *First evidence,
V2.9.7: turn 140, night, 41 crew, tools open, glass on — low 29, two dips.*
*V2.12.1, iPhone 16 Pro, glass and fog both on, ASH: low 29, avg 54 over 34
seconds, one dip, on a glass toggle at three seconds. Headless Chromium had
put the glass fog at 14ms a frame against 1.5ms flat; the device did not
agree, and the device is the one that counts.*

### Reading the ground

- **V23** — dig a shaft from the surface to the bottom of the map beside
  untouched rock. At every depth, open ground is obviously lighter than the rock
  next to it: in daylight, in the dark, and with a reactor running. Check it on
  the phone in daylight rather than on a monitor — the two tones this replaced
  sat 0.4 and 0.1 luma from the rock they were cut through, which a bright
  screen in a dim room will still separate. Guards V2.11.1.

  The close pair is not the shallow one. Dry regolith is brown and the tunnel
  is blue, so the two are never in doubt; it is the ice-bearing rock at the
  bottom of the map, which is blue-grey, that sits nearest the tunnel. Look
  there first.

### What has been surveyed

- **V24 — the fog covers, it does not hollow out.** On a fresh site, look at
  the ground under the crest. It is one sheet at one strength, not a patchwork:
  no tile edges showing through where the alpha doubled, no seam where two
  regions meet. The outline is **rounded where the region ends and square
  inside it** — the only curve on a board of squares, which is the whole point
  of it. With glass on, the terrain is blurred through the sheet and the top
  edges carry a bright hairline; with **Glass panels** off it flattens to a
  plain tint and neither should look broken. Guards V2.12.0.
- **V24b — every tone is legible, and none of them wins.** Cycle **Fog tone**
  through SLATE, ASH, STONE and SMOKE, glass on and off, in daylight on the
  phone. At each one the fog is lighter than the terrain, and the question to
  answer is whether the unexplored part of the map is pulling the eye away from
  the colony. If SLATE reads as a hole rather than a cover, or SMOKE disappears
  into the sky, say so — the alphas are two numbers per tone and are cheap to
  move. Guards V2.12.0.
- **V25 — digging lifts it.** Drive a drift out from the colony and watch the
  sheet retreat four tiles ahead of the face. Ore specks and strata appear as
  it goes and never before. The surface — crest, basin, profile — is visible
  from turn one and never covered, because the probe surveyed it: if the
  skyline is ever fogged, the opening decision has been broken and that is a
  stop. Guards V2.12.0.

### The opening, and replaying it

- **V26 — the opening plays once, on BEGIN.** Land somewhere new. Dark, then a
  probe crossing with a frustum of scan light, and the ground exists only
  behind it, skyline included. No sun during the pass.
  **The sky does not wait for the beam:** stars and Earth are there ahead of the
  probe as well as behind it, at the same brightness, with **no edge of any
  kind** around the unsurveyed part — no line under it, none down its side. Hold
  the phone in portrait, which is where the bottom edge used to show. The beam
  must not touch ground that has not arrived: no bright contact mark out in the
  dark ahead of the reveal. Guards V2.12.5. Warm caps on the columns
  the sun will reach, cold on the ones it never will. Then dawn, the lander,
  the shaft and habitat and arrays going in, and the HUD sliding back. One
  touch speeds it up, a second ends it, and the board it leaves is the colony
  you then play. **Close and reopen the app: a resumed colony must not play
  it.** Guards V2.12.0.
- **V26b — the switches.** `TOOLS · DISPLAY · Opening animatic` off, then land
  somewhere new: the board is there immediately. Turn the phone's Reduce Motion
  on and land again: the same. Guards V2.12.0.
- **V27 — `Replay the survey` leaves the colony alone.** On a colony well into
  a run — thirty crew or more, several sols in — note the sol and day on the
  counter, then tap `TOOLS · DISPLAY · Replay the survey`. The probe crosses
  your colony as it stands. **Nothing is built and nothing is un-built**, and
  when it ends the counter reads the same sol and day it did before. Then
  background the app and reopen it: still the same sol.
  **Every structure must be the one you left there.** Before replaying, note a
  tile where you have built something *different* from what the colony started
  with — a processor where an array was, or a stripped array — and check it
  after. `cineSet()` reverts birth tiles and only birth tiles, so a structure
  on ground the colony was not born with proves nothing; pick one it was.
  Guards V2.12.8, where the replay wound the opening's layout back over the
  colony before drawing a frame.
  **And it reframes.** Zoom well in, pan into a corner, then replay: the pass
  should snap to the whole-map view first — the same framing FIT gives and a
  new colony opens with — play there, and leave it there. Guards V2.12.9. *V2.12.0 re-enacted the
  landing on top of the colony and reset the turn to zero, and the next save
  wrote that down — this check is the one that would have caught it.* Guards
  V2.12.1.
- **V28 — LAND HERE AGAIN.** On the RUN tab, under THIS SITE. Two taps, same as
  the other two: the first arms it, the second discards the colony and lands a
  fresh one **on the same code**, on the splash, with the full opening. Check
  the code on the line above is the code you get. Guards V2.12.2.

- **V29 — the achievement card is a pane.** Earn one, or tap one that is
  already listed on the BOARD tab, and look at the card that slides in at the
  lower left. With glass on: the terrain is blurred through it, the corners are
  rounded, there is a bright hairline along the top and the gold rule down the
  left follows the curve rather than tapering into a crescent. Tap it to hold
  it — the whole outline goes gold and TAP TO DISMISS appears. Glass off, and
  with the phone's Reduce Transparency on, it is the flat card it always was,
  gold edge included. It is a new blurred surface that can arrive mid-pan, so
  watch the FPS meter while one is on screen. Guards V2.12.3.

- **V30 — the sky is one sky.** At turn zero, in daylight, the stars are
  visible on the phone without cupping a hand over the screen — check it in a
  lit room, not a dark one. Then end turns through to sundown and watch the
  transition: the stars should come **up**, not appear. No star arrives that
  was not already there, and none moves. Land on the same code twice and the
  sky is identical; land on a different one and it is not. Guards V2.12.4,
  where day drew 28 stars at a seventh of the alpha and sundown popped in 64
  more. Watch the FPS meter through the same pan as F3 — this is 92 arcs a
  frame in daylight where it used to be 28.

- **V31 — nothing moves except together.** Zoom in past FIT and pan the map
  slowly, in daylight, with fog and glass on. The stars, Earth, the terrain and
  the fog sheet all travel as one: no part of the picture sits still while the
  rest slides, and nothing crawls inside the fog. Do it slowly — a flick hides
  this, and it was reported off a slow drag. Guards V2.12.6, where the star
  field was laid out in screen space and stayed put while the ground panned.

- **V32 — nothing lit survives the survey.** Build something that glows — a
  reactor, or a habitat with a reactor running somewhere — **hard against the
  first or last column of the map**, then `Replay the survey`. Ahead of the
  probe there must be nothing but sky: no warm smear hanging off the end of the
  map beside the edge column. Check both ends, and check it on a colony large
  enough that the arrays reach the edges too. Guards V2.12.7, where the sky
  repaint was clipped to the map and a glow drawn 1.2 cells wider than its tile
  came through it.

- **V33 — every award is announced where it can be seen.** Reach
  self-sufficiency, which fires several at once and raises the verdict in the
  same breath. Nothing should slide in underneath the verdict; the cards come
  after it is dismissed, one at a time, and the count on the BOARD tab matches
  the number of cards you actually read. Same check on a colony that dies, and
  on an award that lands while the opening animatic is still playing. Guards
  V2.12.11, where the card ran its 3.6 seconds behind the verdict at z-index 30
  and took itself away.

- **V34 — a clue says what the code tests.** Open TOOLS · BOARD on a colony
  that has not won yet. The locked list is in two groups: everything under
  **A NIGHT CARRIED ON FUSION** is unreachable until twelve dark turns have run
  on a live reactor, and the two under **ANY TIME** are not. Read each clue as
  someone who has not seen the source: none of them should imply a condition
  the group heading contradicts, and none should be so short it means nothing
  on its own — which is what the unlock card shows, so check the card text too
  when one is earned. The test this guards: a colony that reaches sunrise on
  stored power has carried nothing and is *correct* to receive no award.
  Guards V2.12.12. Check at 135% and at XXL text — the grouping added markup to
  the pane, and short clues exist so the docked 268px panel keeps one line per
  award.

- **V35 — a panel open while you play keeps up.** Open TOOLS · BOARD and leave
  it open. Earn something — SKELETON CREW on a small colony is the easy one —
  and watch the pane you are already looking at: the row stops saying
  `[LOCKED]` and the `UNLOCKED · n of 11` count goes up, without switching tabs
  or reopening anything. Then scroll partway down the list and earn another:
  you stay where you were. Finish a run and the new board row appears the same
  way. Guards V2.12.13. The general form of this check is worth running on any
  panel that can be left open: DISPLAY and RUN both repaint themselves, BOARD
  did not, and nothing in the plan asked.

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

For each of S, M, L, XL, XXL and AUTO:

- **V9** — the top readout fits without scrolling at AUTO, M and L. At larger
  sizes it may scroll sideways, but every figure must be reachable; clipped
  with no way to see it is a failure. Guards V2.6.0 and V2.9.14, where LABOR
  was cut off at 135%.
- **V9b** — with Text size on AUTO, change Dynamic Type from Control Centre
  while the game is on screen. The app follows within a second or two, without
  leaving the app or touching anything, and the DISPLAY row shows the new
  percentage. On a fixed size, nothing changes. Guards V2.10.4.
- **V10** — the objective line wraps rather than cutting.
- **V11** — build rows are two lines each, name above cost, all the same height.
- **V12 — the map tiles are the same size at every setting.** Open TOOLS ·
  DISPLAY and read `cell`; it must not change between settings. This is the
  single most useful number in the app for layout bugs.
- **V13** — the arrow row is no shorter than a build row and comfortably
  thumb-sized.
- **V13b** — at XL and XXL, every row in the tools panel reads in full, the
  panel stays over the map, and the build column's names and costs are not
  cut off. The top readout may scroll sideways at these sizes. Guards V2.10.5.

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
- **V19b** — select a running or idled machine with CLEAR held: IDLE or RESTART
  and STRIP sit side by side, each glyph over word, neither word cut off, both
  the full height of the lane. Check at text L. Guards V2.10.3.

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

- **V20b** — with the phone rotation-locked in portrait, the gate offers both
  ways out: unlock rotation, or the switch on the card. Guards V2.10.5.
- **V20c** — set the phone's text size large and hold it in portrait: every
  line of the gate is large, in proportion, and the card fits or scrolls.
  Changing the setting while the gate is on screen moves it without a tap.
  The HUD in landscape does not follow past 145%. Guards V2.10.6.
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
- **M4b** — go into a night with the bank covering it: the POWER `night` line
  is not red, and morale does **not** fall across the dark. Then spend the bank
  down mid-night until that line goes red: morale falls from that turn. Morale
  is paid for being able to hold the night, not for a positive net on the turn.
  Guards V2.11.1, where every dark turn cost 10 morale whatever the bank held.
- **M4c** — the ledger's `power secure` row agrees with the POWER `night` line:
  `yes` exactly when the bank covers the figure that line names. They are the
  same test, and if they ever disagree one of them is lying.
- **M5** — morale is deterministic. Note the seed, play ten turns, restart the
  same seed, repeat the same moves: the same morale to the decimal.
- **M5b** — with a crew of seven or more and one served wallow, the ledger reads
  `wallow cover · 1 of 2 served`. Build a second wallow beside a habitat: it
  reads `2 of 2` and morale climbs. Idle one: it drops back. One served wallow
  per six capybaras is full marks.
- **M5c** — a colony with a pool per six capybaras and a bank that covers the
  dark reaches morale 100, and the ledger's work multiplier reads 1.50×.

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
- **M21b** — end a run, win or lose, then leave the app and come back before
  answering the card. The card is there again, END TURN is not dead, and the
  board and the lost-colony count have not moved. In review, no card. Guards
  V2.10.7.
- **M22** — start a colony by code from `SEEDS.txt`; the rating matches the file.
- **M22b** — land on a site whose crest is four columns or fewer (the ledger's
  arrays-live line and the map show it): it is never rated below 3 stars, and
  the reason line names the thin crest. Guards V2.11.0.
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

**UNBOTHERED needs a served wallow standing before you end turn zero.** A fresh
colony's arrays are in shadow and its bank cannot hold a night, so the target on
turn one is 50 and morale lands at 59.75 without one. Dig a tile beside the
habitat and build the wallow first, ahead of everything else.

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
large herd. That is the same ratio the morale bonus wants — one served wallow
per six capybaras — so the configuration that maxes morale is the one that fills
every pool, but only at a crew that divides by six. At 40, FULL CAPYCITY's
threshold, full morale wants seven pools and POOLS OPEN allows six. Take POOLS
OPEN as the herd passes through a multiple of six.

### Run B — the second 3★ · `BLACK-WALL-719`

Reach self-sufficiency again, nothing else required.

| Earns | Condition |
|---|---|
| SISTER COLONY | two different sites, same rating |

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
  **It is two seeds, not two runs.** The tally is keyed by seed, so replaying a
  site overwrites its own entry — SHACKLETON twice is one 3-star site, not two.
  `Copy diagnostics` has the tally on the `held` line (`held 3★×1`), which is
  the only place progress toward this and THE LONG SURVEY is visible.
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

    python3 preflight.py index.html SEEDS.txt

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

**Do not write a probe that reads the canvas.** WebKit treats a canvas on a
`file://` page as tainted, so `getImageData` throws, and a probe that catches
that quietly will report a clean screen while the fault is in plain sight on
it. V2.12.6-PROBE-CINE did exactly that and cost a round trip. Draw the
diagnosis instead: V2.12.6-PROBE-FOG tinted the surveyed columns cyan, the
repainted ones magenta and everything off the ends of the map green, and one
screenshot named the culprit.

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

### What CI runs on every push

`.github/workflows/checks.yml` runs four jobs against `index.html`, so a commit
made on a phone is still checked: `preflight.py` (Tier 0 static), `verify.js`
(Tier 0 in a real page, plus V23 measured off the rendered canvas),
`cine-check.js` (V26's sky assertion, V27, V28, V31's pan residual and V32's
glow overhang, on a colony set to turn 706), `achv-check.js` (V33, on a colony
driven to self-sufficiency), and `survival.js`
(400 colonies against the agreed survival table). None of them replaces a
device: every check in Tier 1 is here because it can only be seen on the phone.

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
| 1.4 | 20 Sep 2026 | V2.10.1 – V2.10.7 | V21 and V22 for the site field: mistyped codes, and keyboard shortcuts firing while typing. V19b for the split IDLE/STRIP cell. V9b for AUTO text size following the system live. V13b for the XL and XXL text steps, V20b for the rotation-locked gate, V20c for the gate at large text sizes. M21b for a run that ended while the app was away. |
| 1.5 | 21 Sep 2026 | V2.11.0 | M22b for the thin-crest rating floor. Model change: Tier 2 in full, and Tier 3 runs B and D, which turn on what a site is rated. |
| 1.6 | 21 Sep 2026 | V2.11.1 | V23 for tunnel contrast at depth. M4b and M4c for morale paid on the night bank rather than the turn's net; M5b and M5c for wallow coverage and the 100 ceiling. Tier 3 notes on the turn-zero wallow UNBOTHERED now needs, and where POOLS OPEN and the wallow bonus part company. Preflight examples point at `index.html`, which is now the build. Model change: Tier 2 in full, and the Tier 3 runs that turn on morale. |

| 1.7 | 23 Sep 2026 | V2.12.0 – V2.12.2 | *What has been surveyed* and *The opening, and replaying it*, neither of which existed. V24 and V24b for the fog as a covering and its four tones; V25 for digging lifting it and the surface never being covered. V26 and V26b for the opening animatic and its switches; V27 for the survey replay leaving a live colony alone, which V2.12.0 did not; V28 for LAND HERE AGAIN. F7 and F8 for frame rate with the glass fog, which blurs the canvas a second time — the pair of lows, glass on and off, is what decides whether it stays. First device evidence recorded against F7. `cine-check.js` added to CI beside `verify.js` and `survival.js`. |

| 1.8 | 23 Sep 2026 | V2.12.3 | V29 for the achievement card on glass — the last surface still on the opaque theme, and a new blurred surface that can arrive mid-pan. |

| 1.9 | 23 Sep 2026 | V2.12.4 | V30 for the star field: visible in daylight, the same stars all sol, seeded per site, and the pop at sundown gone. |

| 1.10 | 23 Sep 2026 | V2.12.5 | V26 extended: the sky ahead of the probe, no edge around the unsurveyed region, and no contact mark on ground that has not arrived. `cine-check.js` gained a pixel assertion for the first of those — it reads the frozen sweep frame and fails on V2.12.4. |

| 1.11 | 23 Sep 2026 | V2.12.6 | V31: nothing on the board may move independently of the map when it pans. `cine-check.js` measures it — pan by several widths, shift the previous frame back, count what still disagrees — and fails on V2.12.5. |

| 1.12 | 23 Sep 2026 | V2.12.7 | V32: a lit structure on an end column must not throw its glow past the map during the survey pass. `cine-check.js` measures it and fails on V2.12.6. Note against V26 on how it was found — a tinted diagnostic build, after a pixel-reading one returned nothing because `getImageData` throws on a `file://` canvas in WebKit. |

| 1.13 | 23 Sep 2026 | V2.12.8 | V27 extended: the survey replay must not revert birth tiles. Third fault out of `endCine()` — V2.12.1 was the turn, this is the board — so the note there now says to check both. `cine-check.js` rebuilds and strips birth tiles to catch it, and its glow-overhang check was made deterministic after it was found to be racy. |

| 1.14 | 23 Sep 2026 | V2.12.9 | V27 extended again: the replay fits the view before it plays and leaves it fitted. `cine-check.js` zooms to 2.4x and pans off first, then compares the view afterwards against a fresh fit. |

| 1.15 | 23 Sep 2026 | V2.12.10 | SISTER COLONY reworded to "two different sites" after it was read as two runs; the Tier 3 note now says the tally is keyed by seed and points at the `held` line in Copy diagnostics. Behaviour unchanged. |

| 1.16 | 23 Sep 2026 | V2.12.11 | V33: the unlock card must not be announced underneath an overlay. `achv-check.js` added — it reaches self-sufficiency on a reactor and watches `#achvslot` — and joins CI. Note that a check asserting "nothing appeared while an overlay was up" is the wrong assertion: the card legitimately appears just before the verdict opens. |

| 1.17 | 23 Sep 2026 | V2.12.11 | V23's automated half in `verify.js` now measures distance in RGB rather than difference in brightness, after it passed here at 20.8 and failed on the CI runner at 11.0 on the same row. No build change. Brightness is the wrong question for this palette: the tunnel is blue, dry regolith is brown and ice-bearing rock is blue-grey, so most of what separates them is hue. The old metric scored the warm fusion tunnel against blue-grey ice — two colours nobody could confuse — the same as the cold tunnel against that ice, which is the genuinely close pair. Threshold 18, against a floor of 23.3 on the runner and 32.6 here, and 12.7 for a tunnel repainted to within a shade of the rock. The manual check is unchanged: the phone, in daylight, is still what decides. |

| 1.18 | 23 Sep 2026 | V2.12.12 | V34 for the achievement clue text saying what the code tests. Reported from a real run: a colony came through the dark on sol 1 and the list read 0 of 11, which was correct — "held a night" means twelve dark turns on fusion, not reaching sunrise. Nine of eleven awards sit behind the self-sufficiency return and only four admitted it. The board now states the condition once above a group. P13 and P14 added to `verify.js`: P13 checks the grouping flag against which side of that return each `award()` is on, P14 that a short clue declares the long form the unlock card needs. Both fail on V2.12.11. |

| 1.19 | 23 Sep 2026 | V2.12.13 | V35 for a panel left open while you play. Reported at turn 239: nine of eleven earned, the store and the diagnostics both right, the BOARD pane still showing SKELETON CREW locked — `paintBoardPane()` had one caller, `showTab`. Older than the grouping; V2.12.12 only gave you a reason to sit on that tab. Three assertions added to `achv-check.js`, two of which fail on V2.12.12. Also the heading V2.12.12's case-sensitive sweep missed. |

When a build fixes something this plan did not catch, add the check here in the
same commit as the fix, and note the build it was first seen in.
