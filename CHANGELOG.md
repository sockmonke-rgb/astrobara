## V2.12.13

**The BOARD tab never repainted itself.** Reported from a colony at turn 239
with five structures standing: SKELETON CREW was in the store, Copy diagnostics
listed it, and the pane on screen still read `[LOCKED] under 20 structures
standing` and `UNLOCKED · 0 of 11`.

`paintBoardPane()` had exactly one caller — `showTab('board')`. Open the tab,
keep playing, and the list is frozen at whatever it said the moment you opened
it. The other two panes were already handled: `paintDisplayPane()` repaints on a
system text-size change and `paintRunPane()` from half a dozen places. The board
was the one that only ever painted on the way in, which is also the one whose
contents change while you are not touching it.

The fault is older than the grouping — it has been there since the pane existed.
V2.12.12 only made it visible, by giving you a reason to sit on that tab.

### Fixed

- `refreshBoardPane()` repaints from two events, and only those: `award()`, and
  `recordScore()` writing a row. Nothing on the turn loop — a repaint every
  recompute would rebuild the list sixty turns a sol to no purpose.
- It returns immediately when the tab is not showing, and **restores
  `scrollTop`** when it is. The pane scrolls; earning an award is not a reason
  to lose your place in the list.

### Also

- `COLONIES THAT HELD A NIGHT`, the heading over the board rows, becomes
  `COLONIES THAT CARRIED A NIGHT`. V2.12.12 swept for the old wording
  case-sensitively and this one is upper case, so it shipped. The check that
  let it through is now case-insensitive — it is the heading directly above the
  rows, so it was the most visible one left.

### Verified

- Three new assertions in `achv-check.js`: the open pane's count goes up on an
  award, the row it belongs to stops reading `[LOCKED]`, and the scroll position
  survives the repaint. **The first two fail on V2.12.12** (`5/11 -> 5/11`,
  `[LOCKED] rows 6 -> 6`). 8/8 on V2.12.13.
- Tier 0 clean, `cine-check.js` 27/27, survival bot identical to the V2.11.1
  baseline. No markup, no CSS, no model.

## V2.12.12

**The clue text promised something the code does not test.** A colony came
through the dark on sol 1 and the list still read `0 of 11`. That is the code
behaving correctly and the copy saying otherwise.

In the build, *"held a night"* is a term of art: `fusionNightTurns >= 12` —
twelve consecutive dark turns on a live reactor, the same test as the win.
Reaching sunrise on stored power is not it. Nine of the eleven awards sit
behind

```
if(!G.selfSufficient) return;
```

including the line that writes the per-site ratings tally, which is why the
diagnostics also read `held none` after a night that plainly happened. Only
FULL CAPYCITY and POOLS OPEN! are reachable before that return, and they were
the only two whose clues were already honest about it.

Three vocabularies were in the table for one condition — *a night held*, *a
night carried*, *self-sufficient* — and two clues named no condition at all.
NOSE ABOVE WATER was the worst of them: "never blacked out" reads as something
you either did or did not do, with no hint that it only counts once you have
won.

### Changed

- The board states the condition once, above a group, instead of nine times
  inside it:

  ```
  UNLOCKED · 0 of 11
  A NIGHT CARRIED ON FUSION
    · [LOCKED]  at every rating
    · [LOCKED]  on a 5-star site
    · [LOCKED]  two different sites, same rating
    ...
  ANY TIME
    · [LOCKED]  40 capybaras at once
    · [LOCKED]  three bathing in every wallow
  ```

  The clues get shorter rather than longer, which is what the docked 268px
  panel needs. The grouping reads a new `w` flag on each award.
- **Two clue strings where one surface is not enough.** The board has the
  heading above it and takes the short form; the unlock card floats over the
  map with nothing above it and takes `cf`, the long form — *"a night carried
  at every rating"*. A card reading "at every rating" would only have moved the
  bug one surface across.
- SISTER COLONY keeps *"two different sites, same rating"* in full: it was
  reworded in V2.12.10 for exactly this reason and shortening it would undo
  that. TWIN SUNS keeps *"a night carried on one reactor"* — it is the award
  most often seen, so the verb is worth repeating there.
- Every remaining user-facing string moves to the same verb: the empty board
  now reads *"No colony has carried a night yet."* and the exported board is
  headed *"colonies that carried a night"*.
- One CSS rule, `#pane-board .ghead`. No new markup, no new ids, no logic in
  the turn loop. The model is untouched.

### Verified

- Tier 0 clean at V2.12.12. `cine-check.js` 27/27, `achv-check.js` 5/5,
  survival bot identical to the V2.11.1 baseline — nothing here can move it.
- **New: P13 in `verify.js`.** The gold heading is a promise about the code, so
  the flag is checked against the code: `checkAchv()` is split on the
  self-sufficiency return and the awards on each side are compared with the `w`
  flags. A flag on the wrong side of that line is the same bug printed in gold.
  **Fails on V2.12.11 with all nine listed as "gated but unflagged".**
- **New: P14 in `verify.js`.** A clue under four words, or one that opens with
  a preposition, must declare `cf` — otherwise it is a card that says "after
  stripping" and nothing else. Concatenated clues are skipped, since the
  literal in the source is a fragment rather than the clue. **Fails on V2.12.11
  on three rows.**

### Not changed

The gate itself. Twelve dark turns on fusion is the win condition and the unit
the whole ladder is built on; the fault was never that the rule is wrong, only
that nothing said it.

## V2.12.11

**The unlock card was being shown where nobody could see it.** Reaching
self-sufficiency awards several achievements and raises the verdict in the same
breath:

```
G.selfSufficient = true;
checkAchv();          // queues the cards, the first starts its 3.6s timer
finish(true);         // .overlay at z-index 30, over #achvslot at z-index 21
```

The card slid in, the verdict covered it, the timer ran out behind it and the
card removed itself. The board showed the awards because `award()` had written
them — only the announcement was lost, and it was lost at the biggest moment in
a run.

### Fixed

- `pumpAchv()` holds while any overlay owns the screen — the verdict, the
  splash, the portrait gate — and while the animatic is playing, since the HUD
  is out for that too.
- A card already on screen when an overlay opens is taken down and put back at
  the **front** of the queue. The gate alone would not have caught this one:
  `checkAchv()` runs before `finish()`, so at the instant the card appears
  there is no overlay up yet.
- The queue is pumped again when the verdict closes, when a restart clears it,
  and when the animatic ends.

### Verified

- Tier 0 clean at V2.12.11: P1–P12, unchanged counts. No DOM, no CSS.
  `cine-check.js` 27/27. Survival bot identical to the V2.11.1 baseline.
- **New: `achv-check.js`.** It holds a night on a reactor to reach
  self-sufficiency for real — `fusionNightTurns` is reset on every dark turn
  fusion is not carrying, so the win cannot be poked in from outside — then
  watches `#achvslot` with a MutationObserver and records what was announced
  before the verdict closed and what after. **V2.12.10 loses MOISTURIZED:
  announced once, underneath the verdict, never again. V2.12.11 announces it
  again when the verdict closes.** Added to CI.
  - The first version of the check asserted "no card was inserted while an
    overlay was up", which failed on the fixed build too — the card legitimately
    appears a moment *before* the verdict opens. What matters is not the instant
    of insertion but whether the player ever saw it with nothing on top, so the
    check now compares what was announced before the verdict closed against
    what was announced after.

---

## V2.12.10

### Changed

- **SISTER COLONY now reads "two different sites, same rating."** It said "two
  sites at the same rating", and two people running the same site twice read
  that as two runs. The behaviour was always right — the tally is a map of seed
  to rating, so replaying a site overwrites its own entry and can never count
  twice — but the sentence was not saying so. Text only: the id, the name and
  the award logic are untouched, so awards already held carry as normal.
  - Worth knowing when this comes up again: the held tally is already in **Copy
    diagnostics** as `held 3★×1`, and that line is the progress meter for both
    SISTER COLONY and THE LONG SURVEY. It is not on the BOARD tab, where a
    locked entry shows the description and nothing else.

### Verified

- Tier 0 clean at V2.12.10: P1–P12. P10 still reads 11 achievements and 11
  awarded, because only the description string moved. `cine-check.js` 27/27.
  Survival bot identical to the V2.11.1 baseline.
- `buildMajor()` takes the major only, so a two-digit patch number changes
  nothing about whether achievements carry.

---

## V2.12.9

### Fixed

- **The survey replay now plays on the view the game opens with.** The probe
  crosses the whole map and the reveal is column by column, so the animatic is
  composed for the whole site — and it was playing on whatever view the colony
  happened to be sitting on. Zoomed in and panned into a corner, the sweep runs
  off the edges of the frame and the pass hands the colony back wherever you
  were, which is not where the opening leaves it.
  - `startCine()` calls `fitView()` first, which is exactly what `newGame()`
    does. A replay is framed the way the opening is framed and ends there.
  - The opening itself is unchanged: it runs on a view that was just fitted, so
    the call is a no-op on that path.
  - Before the `.cine` class goes on, because `fitView()` measures the panes
    through `glassInset()` and they should be measured sitting normally.

### Verified

- Tier 0 clean at V2.12.9: P1–P12, unchanged counts. No new block — one call.
  Survival bot identical to the V2.11.1 baseline. Tunnel contrast unmoved.
- **`cine-check.js`, 27 assertions.** The test colony is now zoomed to 2.4×
  and panned off before the replay, and the view afterwards is compared against
  a fresh `fitView()` of the same board. V2.12.8 comes back at zoom 2.4, pan
  140,−64 where a fresh fit is zoom 1, pan −80,3, and fails. V2.12.9 lands on
  the fit exactly. Three consecutive clean runs.

---

## V2.12.8

**Replaying the survey was overwriting structures.** A processor standing on a
tile `newGame()` had put an array on came back as an array. Every tap of
`Replay the survey` did it, on every colony, since V2.12.1.

### Fixed

- `startCine()` calls `endCine()` first, to clear anything already running. On
  that call nothing is playing: `cineTurn` is null and `cineSurvey` is false,
  because the previous run cleared it. The turn restore was guarded on
  `cineTurn`. The board restore was not:

  ```
  if(cineTurn !== null){ G.turn = cineTurn; cineTurn = null; }
  if(!cineSurvey) cineSet((G.birth||[]).length);      // runs anyway
  ```

  `cineSet()` winds `G.birth` back and lays it again. On a fresh colony that is
  a no-op, which is why it never showed in the opening it was written for. On a
  colony that has been played it reverts every birth tile to what `newGame()`
  put there — a structure built over one is replaced, a birth structure
  stripped from one is restored — and it ran before a single frame was drawn,
  which is why it looked like the replay doing it.
- Both restores now sit inside the same guard. `endCine()` touches the board
  only when a cinematic was actually running. No new block: the guard was
  already there and the call was outside it.
- **This is the third fault from the same two lines** — V2.12.1 was the turn
  reset, this is the board. The survey replay shares an exit path with an
  opening that runs once on a colony with no history, and every assumption that
  exit path makes about the board is wrong on a colony that has one.

### Verified

- Tier 0 clean at V2.12.8: P1–P12, unchanged counts. Survival bot identical to
  the V2.11.1 baseline. Tunnel contrast unmoved.
- **`cine-check.js`, 26 assertions.** Two new ones, and a fix to the harness
  that mattered more than either: the test colony now rebuilds one tile
  `newGame()` laid as a different structure, and strips another. Structures on
  tiles birth never touched cannot catch this — `cineSet()` only reverts birth
  tiles — which is exactly why the existing "every structure still standing"
  check passed on every build that had the bug. Against **V2.12.7 it now fails
  four assertions**, against V2.12.6 five.
- The glow-overhang check from V2.12.7 was flaky: three runs failed and five
  passed on the same build, because it polled for the dark beat and froze the
  clock from outside, racing the animation. It now freezes in the same tick the
  cinematic starts, so the frame under test is always the first one. Six
  consecutive clean runs, and it still reports 336 warm pixels on V2.12.6.

---

## V2.12.7

### Fixed

- **A lit structure at either end of the map threw its glow out past the map,
  into ground the survey had not reached.** `cineDrawFog()` builds its clip
  from one rect per unsurveyed column, so the clip stopped dead at the first
  and last column boundary. Anything drawn wider than the map came through the
  sky repaint untouched — and `structureGlow()` reaches 1.2 cells past its tile
  on every side. Build a reactor on the edge column and the survey pass runs
  with a warm square hanging in the dark beside it.
  - The first and last unsurveyed columns now extend their rect to the edge of
    the stage. `Math.min`/`Math.max` against the map bounds, so a map wider
    than the stage keeps exactly the rect it had. Same columns covered, no
    longer cut off at the map boundary.

### Verified

- Tier 0 clean at V2.12.7: P1–P12, unchanged counts. No new block, no new
  brace — two ternaries and a rect.
- **`cine-check.js`, 24 assertions now.** A drift out to both edges with a
  reactor on each end, zoomed out so there is margin off the ends, frozen on
  the dark beat, counting warm pixels outside the map: **V2.12.6 → 336, peak
  R 45. V2.12.7 → 0.**
  - Two false passes had to be worked through first, both worth recording. The
    reactors were placed unconnected, so `conn.has()` made them unlit and
    `structureGlow()` returned before drawing anything — a check that passes
    because the thing it tests never happened. Then the warmth threshold was
    set at R > 26, and the overhang is at about 5% alpha, so it peaks around
    R 45 and most of it sits under 26. A check that reports zero is only worth
    something if it has been made to report non-zero on a build that has the
    fault.
- Survival bot identical to the V2.11.1 baseline. Tunnel contrast unmoved.

### Worth watching

- This was found with a diagnostic build that tinted the three regions —
  surveyed, repainted, off the end of the map — and asked for one screenshot.
  The build before it tried to read the canvas with `getImageData` and reported
  nothing at all, because WebKit treats a canvas on a `file://` page as tainted
  and the call throws. **Pixel-reading diagnostics do not work on the device
  this game is tested on.** Draw the diagnosis instead.

---

## V2.12.6

### Fixed

- **The sky is pinned to the ground now, not to the screen.** Reported as
  movement in the fog while panning, and the fog was innocent: `drawSky()` laid
  the star field out in screen space, so the terrain slid out from under a sky
  that stayed exactly where it was. Earth never had this problem — it is placed
  at `offX + cell*28.5`, in map space, two lines below the star loop. On a
  board where everything else moves together, one thing that does not reads as
  crawl, and it reads worst through the fog, because the sheet travels with the
  ground while the blur under it keeps collecting stars that do not.
  - The stars are offset by the pan and wrapped, so they travel with the
    terrain and the field never runs out at an edge. Not scaled by zoom: a star
    has no size to magnify, and wrapping keeps the count constant however far
    you pan.
  - V2.12.4 is where this became visible, because that is where the daylight
    star field went from 28 nearly-invisible specks to 92 legible ones. The
    fault was older than that; it just had nothing to show with.

### Changed

- **Fogged tiles are no longer given detail nobody can see.** The stratum seam,
  the material patches, the dust specks and the grid line were all drawn and
  then covered by the sheet. A grid line marks a tile boundary, and unsurveyed
  ground has no tile boundaries to show yet. The depth shade stays — depth is
  geometry, not a finding, and the basin is visibly lower than the crest from
  turn one.
  - **Be clear about what this bought: nothing you can see.** Rendered at the
    cell size the phone plays at, the before and after differ by at most 1 in
    255 and by more than 2 on zero pixels. It went in because it is the right
    thing to draw and because it is less work per frame, not because it fixed
    the report — the stars did that.

### Verified

- Tier 0 clean at V2.12.6: P1–P12, unchanged counts. Canvas only.
- **New in `cine-check.js`, 23 assertions now: the pan residual.** It pans the
  map by 1, 2, 3, 5 and 7 pixels, shifts the previous frame back by the same
  amount, and counts pixels that still disagree — anything moving against the
  map. V2.12.6: **0.000%**. V2.12.5: **0.129%**, and the check fails.
  - The measurement took four wrong turns worth recording, because each one
    produced a confident number that meant nothing: sampling above the map
    rectangle (which the old fog never covered), sampling at a fitted cell of
    11.7 rather than the 20.8 a phone plays at, sampling from behind the
    portrait gate, and — the worst — setting `panX` without calling `layout()`,
    so nothing panned and the residual was an image compared against a shifted
    copy of itself. Any pan measurement in this file calls `layout()`.
- Survival bot identical to the V2.11.1 baseline. Tunnel contrast unmoved.

---

## V2.12.5

Two faults in the survey pass, one cause, both reported off a phone in
portrait.

### Fixed

- **The sky went out ahead of the probe.** `cineDrawFog()` painted the unseen
  columns with flat `C.vacuum`, which took the stars and Earth with them — so
  the pass ran across a black void and the sky only arrived behind the beam,
  when the sky is the one thing on that site that was never in question. The
  unseen columns are now repainted with the sky itself: one more `drawSky()` on
  the sweep frames, clipped to those columns. It cannot mismatch, because it is
  the same gradient, the same seeded stars in the same places and the same
  Earth. The site arrives out of a sky that was there all along.
- **A line drawn ahead of the probe.** The same rectangle. It covered the map
  rows only, so its bottom edge sat against the background below the map and
  read as a line being ruled across the dark — which in portrait is exactly
  where the eye is. Its right edge did the same down the last column. The
  clip is now the full stage height and there is nothing to have an edge:
  sky against sky.
- **The beam touched ground that had not arrived.** The footprint rounds up by
  one column past the reveal, and the contact bar was drawn on all of them — a
  bright mark on terrain nobody could see yet, giving away the skyline one
  column early. It now skips any column the survey has not reached.

### Verified

- Tier 0 clean at V2.12.5: P1–P12, unchanged counts. The patch asserts no div,
  no id, no CSS rule and no font size moved — this is canvas drawing only —
  and that `drawSky` has exactly two call sites.
- **New in `cine-check.js`, 22 assertions now.** It freezes a real sweep frame
  at 35%, finds the last revealed column, and counts lit pixels in the band
  three columns ahead of it, inside the map and above the terrain — the exact
  rectangle that used to be filled black. V2.12.5: 127 lit pixels, peak luma
  156. V2.12.4: **0 lit pixels, peak luma 8**, and the check fails.
- Survival bot identical to the V2.11.1 baseline. Tunnel contrast 19.6 / 16.8 /
  16.8.

---

## V2.12.4

### Changed

- **The stars stay up in daylight.** They were never removed — `drawSky()` drew
  92 at night and 28 by day at roughly a seventh of the brightness, which on a
  phone is an empty sky. The opening animatic runs on a night turn, so it
  showed the full field and then handed over to a game that appeared to take it
  away.
  - There is no atmosphere here to scatter sunlight across the sky, and the
    sky is already drawn near-black at noon for exactly that reason. What dims
    stars on a lit surface is the exposure an eye is holding for sunlit
    regolith, and the sun's own halo — which is drawn over them a few lines
    later and still washes out the ones near the disc. So the day sky keeps all
    92 and only loses brightness: alpha `.13–.43` against the night's
    `.20–.75`, radius `.45–.90` against `.55–1.30`.
  - **Sundown no longer pops.** The old day and night fields were different
    sizes, so 64 stars came into existence the turn the sun went down. Now they
    are the same stars in the same places all sol and dusk only brings them up.
  - Night is byte-identical. Positions are still seeded off `G.seed`, so a
    site's sky is the same sky every time it is played.

### Verified

- Tier 0 clean at V2.12.4: P1–P12, unchanged counts — the patch asserts no div,
  no id, no CSS rule and no font size moved, because this is eight characters
  of canvas drawing.
- `cine-check.js` 21/21. Survival bot identical to the V2.11.1 baseline.
  Tunnel contrast 19.6 / 16.8 / 16.8.

### Worth watching

- 92 arcs a frame in daylight instead of 28. They are sub-pixel fills with no
  blur and no filter, so this should not register next to the fog, but F3 is
  the pan test and the star field is now drawn on every frame of it.

---

## V2.12.3

### Changed

- **The achievement card is glass.** It is the one surface that floats over the
  map without belonging to a lane, and it was the last thing in the file still
  wearing the opaque theme — flat panel, square corners, no specular — while
  everything around it had moved on. It now takes the same recipe as every
  other pane: `blur(16px) saturate(1.25)`, a `rgba(214,218,220,.14)` hairline,
  the 14px corner and the top specular. The glyph box becomes a small pane of
  its own, the way the portrait gate's options are.
  - **The gold edge moved from a border to an inset shadow.** A 3px straight
    border on a 14px corner tapers into a crescent; `inset 3px 0 0` follows the
    curve instead. The card is the only rounded thing in the file with a rule
    down one side, so it is the only place that needs the trick.
  - A held card still goes gold all the way round. The glass rule outranks
    `.achvcard.held`, so that is restated rather than left to luck.
  - Both ways back are wired the same as the panes: `prefers-reduced-
    transparency` and a browser without `backdrop-filter` each get the flat
    card, and the gold edge survives both.
  - The opaque theme is untouched. Glass off is the card exactly as it was.

### Verified

- Tier 0 clean at V2.12.3: P1–P12. **346 CSS braces**, up six — the six new
  rules and nothing else. The patch asserts no div, no id, no font size and no
  `touch-action` was added, so P3, P4, P8 and P9 could not have moved, and P3
  and P4 read 70 and 56 exactly as in V2.12.2.
- `cine-check.js` 21/21. Survival bot identical to the V2.11.1 baseline:
  93.9 / 96.3 / 91.3 / 86.6 / 85.5, 90.8 overall.

### Not verified

- The card on a device, and in Safari. It is a new `backdrop-filter` surface
  that can appear while the map is being panned, which is the case F3 exists
  for — if there is a cost, that is where it shows.

---

## V2.12.2

### Added

- **LAND HERE AGAIN**, on the RUN tab, under THIS SITE. Re-lands on the seed you
  are already on without reading its code off the line above and typing it back
  in. Two taps to fire, the same as the other two, because it throws the colony
  away like they do — and because it goes through `restart()` it comes back to
  the splash, so BEGIN plays the full opening with the landing in it. The
  plumbing already existed: `restart()` has always defaulted to the current
  seed, and the end card's AGAIN button has always used it. It was only ever
  missing from the panel you reach mid-run.

### Changed

- **`Replay the opening` is now `Replay the survey`.** It stopped being the
  opening in V2.12.1 and the label did not follow. The two are different films
  and there are now two ways to ask for them: the survey pass over the colony
  you are on, from DISPLAY; and the whole opening on a fresh colony, from LAND
  HERE AGAIN. The row's wording is also the quickest way to tell which build is
  loaded — if it still says *the opening*, the page is V2.12.0 or older.

### Verified

- Tier 0 clean at V2.12.2: P1–P12. **70 ids and 56 `getElementById` targets**,
  up one each, both of them the new button; the patch asserts exactly one div
  and exactly one id were added and that no font size, `touch-action` or CSS
  rule moved, so P8, P9 and P10 cannot have.
- `cine-check.js` now runs 21 assertions, five of them new: the button is
  there, it arms before it fires, it lands on the same seed, the colony it
  lands is fresh, and the splash comes back so the opening plays.
- Survival bot identical to the V2.11.1 baseline: 93.9 / 96.3 / 91.3 / 86.6 /
  85.5, 90.8 overall. Tunnel contrast 19.6 / 16.8 / 16.8.

### Worth watching

- **A report that the replay still builds structures could not be reproduced.**
  In V2.12.1 there is one call site (`startCine(true, true)`), the survey order
  has no `land`, `build` or `settle` beat, and `cineSet()` is never reached on
  that path; a frame-by-frame capture holds 7 dug and 4 built from the first
  frame to the last, and the same check fails on V2.12.0. The likeliest
  explanation is a page served from cache. **The label is the tell:** DISPLAY
  reading *Replay the survey* means V2.12.2, *Replay the opening* means an
  older file. The build stamp is on the splash watermark, in the ledger header
  and in Copy diagnostics.

---

## V2.12.1

A replay is a different film from an opening, and V2.12.0 shipped one function
for both. Two defects, one of them a save-corrupting one.

### Fixed

- **Replaying the opening on a live colony reset it to sol 1.** `endCine()`
  ended with a bare `G.turn = 0`, correct for the only case it was written for
  — the opening, where the turn is 0 anyway — and wrong for the button added
  in the same build. Worse, it took effect the instant `Replay the opening`
  was tapped, because `startCine()` calls `endCine()` first, and the next
  `saveRun()` (a pane action, or the page going to the background) wrote sol 1
  down over a colony on sol 25. The turn the animatic borrows is now saved and
  handed back, in both modes; `cineTurn` is null when nothing is playing, so
  the restore cannot fire on a turn it never took.
- **A replay re-enacted the landing on top of a standing colony.** The build
  beats wind `G.birth` back to bare rock and lay it again, so the original
  shaft, habitat and arrays vanished and were re-placed underneath a colony
  that had grown well past them. Reported as "weird", which undersells it.

### Changed

- **`Replay the opening` is now a survey pass, not a landing.** It keeps the
  beats that are about looking at the site — dark, the probe and its frustum,
  then a hold — and drops the three that are about building it. The ground is
  never wound back: what the beam uncovers is the colony as it stands today,
  and past the sweep the turn goes back to the colony's own, so the light and
  the shadows are the ones it is living in. The warm and cold survey caps still
  come with the beam and fade out as the panels come in. About 5.9 seconds
  against the opening's 9.4.
  - The opening itself is untouched: all eight beats, the lander, the build
    replay, ending on turn 0 with the birth colony exactly as `newGame()` left
    it.

### Verified

- Tier 0 clean: P1–P12, stamps at V2.12.1, 69 ids, 55 targets, 340 braces
  balanced, no page errors, 10/10 seed codes.
- Survival bot identical to the V2.11.1 baseline again — 93.9 / 96.3 / 91.3 /
  86.6 / 85.5, 90.8 overall. This is a view change; nothing in a turn moved.
- Tunnel contrast unmoved: 19.6 / 16.8 / 16.8.
- **New: `cine-check.js`.** Sixteen assertions on a colony set to turn 706 with
  ground `newGame()` never laid. Mid-sweep and after: every dug tile, every
  structure, the turn, crew, power, water, he-3 and morale are the values that
  went in; `cineTurn` is released and the survey flag cleared; and the full
  opening still runs eight beats and ends on turn 0 with the birth colony
  intact. Run against V2.12.0 it fails on the first assertion, which is the
  point of having it.
- **Frame rate, on device.** iPhone 16 Pro, dpr 3, glass and fog both on, ASH:
  `now 60 · low 29 · avg 54` over 34 seconds, one dip under 30, at three
  seconds, on a glass toggle. The 14ms headless figure did not survive contact
  with the hardware — it holds.

### Not verified

- The replay on a device. Tier 1 F1–F6 again if the opening is going to be
  watched more than once.

---

## V2.12.0

Two things arrive together, and they turned out to be one thing: the site is
unknown until something looks at it. Nothing in a turn resolves differently, so
this is not a model change by the test plan's definition — but it changes what
the player can see, which is not nothing. Tier 1 in full, and a playtest.

### Added

- **An opening animatic, after BEGIN.** `dark → probe sweep → hold → lander →
  build → settle → rest → HUD`, about nine seconds, and a touch skips it — one
  speeds it up four times, a second ends it. The same grammar as the end card,
  so a run opens and closes the same way.
  - **No media of any kind.** The same canvas, the same terrain and the same
    sun the game already computes. A few paths and a gradient.
  - **The probe surveys in the dark.** A craft crosses the sky with a frustum
    of scan light spreading to the ground, and its footprint is what reveals
    the site — unsurveyed columns are painted out to vacuum, skyline included,
    so the crest arrives as the beam reaches it. The sweep runs on a night
    turn, so nothing on the surface is lit by anything but the beam.
  - **What the probe leaves behind is the survey, not the light.** Each column
    it crosses takes a warm cap if `maxAnnualSun()` ever reaches it and a cold
    one if it never does — the same function that decides where helium can be
    implanted and where ice survives. Sunlit rim, sunk basin, wordlessly, in
    three seconds. The splash has been saying it in prose since V1.
  - **The build replays `G.birth`**, the list `newGame()` writes as it digs the
    shaft, drifts, sets the habitat and puts the arrays up on the dimmest
    columns. The animatic cannot disagree with the colony it produces, because
    it is that colony being produced — including the lander making the mistake
    that the whole opening is about.
  - Dawn arrives on the hold beat, on a site already mapped.
  - `TOOLS · DISPLAY · Opening animatic` switches it off; `Replay the opening`
    plays it again on the current site. A resumed colony has already landed and
    never sees it, and `prefers-reduced-motion` goes straight to the finished
    state.

- **Fog of war under the skyline.** The probe mapped the surface on the way in,
  so the skyline, the crest and the basin are always yours — the opening
  decision is unchanged. What is under them is not: no strata, no seams, no
  specks and no ore until something has been opened within `scanRadius`. Half
  of this already existed, since `known()` has gated ore since V1; now it gates
  the ground as well, and SURVEY is an instrument rather than a shading toggle.
  - **Drawn as a covering, not a hole.** One path, one fill, laid over the
    ground after the tiles — so the alpha cannot double where tiles meet — and
    the corners round *only* where the region ends. Interior corners stay
    square. On a board made of squares, that outline is the only curved thing
    on screen, which is what separates a sheet from a dark tile.
  - **Liquid glass, by hand.** Canvas has no `backdrop-filter`, so the backdrop
    is made: the frame so far is blurred into a quarter-scale buffer and drawn
    back under the sheet, with the tint over it, a hairline on every boundary
    edge and a specular on the top edges only — the same
    `inset 0 1px 0 rgba(255,255,255,.22)` the panes carry. It samples outside
    the clip as well, so ground beyond the edge smears in underneath the way a
    pane picks up what it overlaps.
  - It follows `Glass panels`. Glass off in DISPLAY means glass off everywhere,
    and `prefers-reduced-transparency` or a browser without `ctx.filter` gets
    the flat sheet without having to find a setting.
  - `TOOLS · DISPLAY · Subsurface fog` switches it; `Fog tone` cycles SLATE,
    **ASH** (default), STONE and SMOKE. Each carries two alphas — one for the
    flat sheet, a lighter one for when the glass is doing the covering.

### Changed

- **`known()` is dilated once and cached.** It used to be asked only about
  tiles that might show ore; the fog asks it about every rock tile on every
  frame, which is 374 tiles against an 81-tile scan each. It is now computed
  from the handful of tiles actually open and invalidated on `recompute()`.

### Verified

- Tier 0 clean: P1–P12. 69 unique ids, 55 `getElementById` targets present, 139
  divs in `#app` — unchanged from V2.11.1 — three storage keys, no network, 85
  scaled font sizes, 9 justified `touch-action` declarations, 11 achievement
  ids matching the awarded set, 340 CSS braces balanced. P1 and P11 in the
  page: no errors, and all ten published codes still regenerate their site and
  rating.
- **The survival bot, in the shipped build, is identical to the V2.11.1
  baseline across all five bands** — 93.9 / 96.3 / 91.3 / 86.6 / 85.5 survived,
  90.8 overall. Nothing in a turn resolves differently.
- Tunnel contrast, read off the rendered canvas, unmoved: 19.6 by day, 16.8 at
  night, 17.9 with a reactor lit.
- The animatic leaves the board exactly as `newGame()` left it: same dug tiles,
  same structures, turn 0, `#app` back to its own classes and the splash gone.
- The patch asserts structurally that no DOM, no ids, no font sizes and no
  `touch-action` were added, so P3, P4, P5, P8 and P9 cannot have moved. The
  quarter-scale blur buffer is created but never appended to the document.

### Not verified

- Tiers 1–3 on a device, and Safari. **Frame rate above all** — see below.

### Worth watching

- **The glass fog costs about 14ms a frame against 1.5ms for the flat sheet**,
  measured in headless Chromium at dpr 3 on a 1740×796 backing store. That is a
  65fps ceiling on a desktop; a phone will be slower, and the bar here is a
  steady 30. The expense is not the blur and not the clip — both are under
  0.2ms — it is the GPU round trip of sampling the canvas back into a buffer,
  and a masked-buffer variant that removes the clip entirely measured *slower*.
  Run F1–F6 with the FPS meter on and read the low. If it will not hold, `Glass
  panels` off keeps the fog and drops the blur.
- **Every fog tone is lighter than the terrain**, so unexplored ground is now
  the brightest mass on the board. STONE and SMOKE pull the eye hard toward the
  part of the map you are not working in. ASH is the default for that reason.
- **The survival bot can see through the fog.** It reads `t.ice` directly and
  never looks at the screen, which is exactly why "identical to baseline"
  proves the model is untouched — and exactly why it says nothing about whether
  the fog makes the game harder to play. Measuring that needs a bot that picks
  targets only from known ground and digs toward the dark basin on the strength
  of the skyline alone.

---

## V2.11.1

A model change: morale moves. Per the test plan that means Tier 2 in full and
the Tier 3 runs it could affect — UNBOTHERED and POOLS OPEN, which turn on the
morale floor and on how many wallows a colony keeps.

### Fixed

- **Morale fell on a night the colony was carrying comfortably.** The +10 was
  paid for a positive power net *on the turn*, and at night the net is negative
  by design — so every dark turn lost it. A colony that banked 4,880 of 4,880
  and then spent it exactly as planned was scored the same as one in trouble,
  and sank toward 75 over six turns.
  - The +10 is now paid for being **power secure**: the bank covers the rest of
    the dark at the idled draw. That is the same figure the readout already
    prints as `night N`, and the same test the sundown line runs — so the rule
    the colony is scored against is one already on screen.
  - Brownouts (−35) and load shedding (−12) are untouched. Actually running out
    still costs exactly what it cost.
  - The 75 was never a floor anyone set. It was 50 + 25, the target with the
    +10 removed.
- **A tunnel was the same colour as the rock around it.** Reported at depth 8
  with a reactor running, and it is worse than that: measured against the
  shading the renderer actually applies — `clamp(.18 + band*.165 + noise*.05)`
  mixed from `#4A423A` toward `#191614`, giving bands from luma 59.0 down to
  24.5 — both old tunnel tones sat *inside* the rock range.

    | tone | luma | nearest band | separation |
    |---|---|---|---|
    | `#1B2430` unlit | 35.0 | depth 6–7 | 0.4 |
    | `#211d18` reactor lit | 29.5 | depth 8–9 | 0.1 |

  - Open ground is now `#3E5472`, and `#66502E` while a reactor is carrying the
    colony through the dark. Those clear the brightest band by 22.5 and 23.2 in
    source, and by 16.8 and 17.9 once the renderer's vignette has been over
    them — the number that matters, and the one measured.
  - There is no separate daytime tunnel colour. Light on this surface only ever
    means fusion, and a day/night tunnel tone would be a distinction the
    renderer has never made.
  - A hairline, `rgba(216,210,198,.30)`, is drawn on each face where open
    ground meets solid rock. Tone separates them in a swatch; at tile size on a
    phone in daylight, the edge is what actually does it. Drawn only above
    6px cell.

### Changed

- **The morale ceiling is 100, not 85.** 85 was not a cap anyone chose — it was
  50 + 25 + 10, everything the three terms could add up to. A second wallow, a
  bigger herd and more housing all added nothing.
  - The wallow term scales with coverage: 25 for the first served wallow, and
    up to 15 more as the rest of the herd gets pools of its own, at one served
    wallow per six capybaras. `CFG.wallowPerCrew` and `CFG.wallowScaleMax`.
  - Full marks is 50 + 25 + 15 + 10 = 100, and it takes a pool per six
    capybaras *and* a bank that covers the dark.
  - The work multiplier is `0.5 + morale/100`, so its ceiling moves from 1.35×
    to 1.5×.
  - One pool per six capybaras is also exactly what POOLS OPEN asks for —
    bathers are half the herd, three to a pool. The configuration that maxes
    morale is the one that fills every wallow, wherever the crew divides by six.
- **The ledger says why morale is where it is.** `wallow served · yes/no` is
  replaced by `wallow cover · n of m served` and `power secure · yes/no`.
- The wallow's build hint no longer promises a flat +25.

### Verified

- Tier 0 clean: P1–P12. 69 unique ids, 55 `getElementById` targets all present,
  139 divs in `#app` opened and closed — the same count as V2.11.0 — three
  storage keys, no network, 85 scaled font sizes and no bare ones, 9
  `touch-action` declarations all justified, 11 achievement ids matching the
  awarded set, 334 CSS braces balanced. P1 and P11 were run in the page: the
  build loads in Chromium with no errors, and all ten published codes
  regenerate the site and the rating `SEEDS.txt` claims.
- Tier 2, the morale arithmetic, against the shipped file rather than a model
  of it — six states, each held still except for morale, each landing exactly
  on its target:

    | state | morale |
    |---|---|
    | night, bank covers it, no pool | 60 |
    | night, bank will not cover it, 1 of 1 pools | 90 |
    | night, bank covers it, 1 of 2 pools | 92.5 |
    | night, bank covers it, 1 of 1 pools | 100 |
    | night, bank covers it, 2 of 2 pools | 100 |
    | day, bank covers the coming night, 1 of 1 pools | 100 |
- 1,200 generated sites played to turn 290 under both rule sets, same seeds and
  the same bot:

    | | V2.11.0 | V2.11.1 |
    |---|---|---|
    | survived | 91.7% | 91.9% |
    | self-sufficient | 86.0% | 91.3% |
    | mean morale | 68.9 | 81.0 |
    | mean morale, dark turns | 64.8 | 80.3 |
    | turns at or above the growth gate of 70 | 53.8% | 65.4% |
    | work multiplier | 1.189 | 1.310 |
    | peak crew | 16.2 | 18.1 |
    | ever browned out | 9.8% | 10.8% |

- Survival holds its shape across the ladder: 97.2% → 81.8% becomes 95.7% →
  84.7%. Brownouts move by one point, so the incentive not to run the bank flat
  survives the change.
- Morale 100 is reached in 93% of a 120-site sample, and holds on 26% of all
  turns across the 1,200, so the new ceiling is a target rather than a default.
- `SLOW-PEAK-538`, 4★, holding 398 of 440 into a night that wanted 252 to
  finish: V2.11.0 drifts 79 → 75 over six dark turns with the bank never in
  doubt. V2.11.1 holds.
- Tier 3, the two runs this could affect:
  - **POOLS OPEN** fires in 88% of runs under both rule sets — 104 of 120
    before, 106 of 120 after.
  - **UNBOTHERED** needs a wallow standing on turn zero under *both* rule sets:
    a fresh colony's arrays are in shadow, so the old +10 is not available on
    turn one either, and a target of 50 puts morale at 59.75 after one turn.
    With that opening it goes from unreached in 60 sites to held in 5.
- Tunnel and rock luma read back off the rendered canvas in headless Chromium,
  a shaft cut from the surface to the floor beside untouched rock, sampled at
  every depth — not computed from hex values, which is how the old pair passed
  inspection for as long as they did. Worst case is the shallowest band, where
  the rock is lightest: 19.6 by day, 16.8 at night, 17.9 with a reactor lit.
  The same probe on V2.11.0 returns 0.4 and 0.1.
- The first sol is slightly leaner: mean morale over turns 1–15 goes from 70.9
  to 68.6, because a colony cannot hold a night until it has banked for one. It
  becomes power secure at turn 14.6 on average, which is sundown — the +10
  arrives exactly when it has been earned. The first pup is unmoved, turn 44.4
  against 44.6.

### Not verified

- Tiers 1–3 on a device, and Safari. Tier 1's new V23 in particular: the tunnel
  tones are measured, but whether they read on an iPhone in daylight is the
  thing a measurement cannot settle.
- **The 1,200-site A/B ran on a re-extracted model, not on the shipped file.**
  The morale arithmetic it predicted has since been checked against the real
  build, case by case, and matches exactly — but the survival and
  self-sufficiency rates come from a rebuilt model with a bot of its own. The
  model was validated against what is already known: all ten published seeds
  reproduce exactly, Shackleton rates 3 stars, and the star cuts land on the
  12th, 32nd, 68th and 88th percentiles over 20,000 seeds. The *player* is not
  the usual harness — its curve runs 97% → 82% where the published one runs
  93% → 53%, so it is flatter and more cautious on hard sites. The deltas are
  like-for-like; the absolute levels are not comparable with earlier runs.

### Worth watching

- **The ladder compresses.** Self-sufficiency gains most where the game is
  hardest — 5★ +10.0 points, 4★ +7.1, 1★ +2.8 — so the spread from 1★ to 5★
  narrows from 19.4 points to 12.2. That is arguably the right shape, since the
  old rule punished exactly the lean colonies that bank carefully and then spend
  the bank. If the ratings should keep their present bite, the lever is the star
  cuts, not the morale rule.
- The work multiplier's new ceiling of 1.5× speeds up extraction on a
  well-run colony by about 11% over the old maximum. Nothing in the yields was
  retuned to match.
- At crew 40 — the FULL CAPYCITY threshold — full morale wants seven pools and
  POOLS OPEN allows at most six. The two achievements pull apart at any crew
  size that does not divide by six.

---

## V2.11.0

A model change: site ratings move. Per the test plan that means Tier 2 in full
and the Tier 3 runs it could affect — B and D, which turn on what a site is
rated — before this goes near a release candidate.

### Changed

- **A thin crest floors the rating at 3 stars.** The rating averages six
  factors, and ice carries 44% of it, so a site could be generous with ice,
  hand you a heavy lander, and still be brutal to power — because the crest it
  gives you for arrays is four columns wide, and the average votes that away.
  - Measured on the site that prompted this, VAST-GATE-900: crest 4, ice close
    and plentiful, score 0.240 against a 2-star cut of 0.235. It rated 2 stars.
  - A site with fewer than five columns in permanent sun is now never rated
    below 3 stars, whatever the score says. Arrays only go on sunlit ground, so
    below that there is no amount of ice that makes the nights easy.
  - VAST-GATE-900 now reads **3★ LEAN · thin crest, deep ice** — the reason line
    names the crest, because the flooring makes it the loud factor.
- **High-contrast ore and larger glyphs are on by default.** Both were
  switchable because they were guesses. Neither has a downside on a phone in
  daylight, which is where this is played. Anyone who turns them off keeps them
  off: a saved run carries its own settings.

### Verified

- Tier 0 clean: P1–P12, including P11 against the real `SEEDS.txt` — all ten
  published codes still regenerate the site and the rating the file claims.
  None of them has a crest under five, so the floor does not touch them.
- 4,000 generated sites, before and after: 1★ 12% → 12%, 2★ 20% → 17%,
  3★ 35% → 39%, 4★ and 5★ unchanged. 137 sites move, all from 2 stars to 3.
  After the change, no 1★ or 2★ site anywhere in the sample has a crest of
  four or fewer, where before 22% of 2★ sites did.
- The hand-authored Shackleton site still rates 3 stars, which is what anchors
  the scale.
- A fresh colony starts with contrast and large glyphs on; a run saved with
  them switched off resumes with them off, and the DISPLAY rows agree.
- No page errors.

### Not verified

- Tiers 1–3, and Safari.

### Worth watching

- The band proportions have shifted: 3 stars is now 39% of sites. If that
  reads as too broad, the fix is to re-derive the cuts against the floored
  distribution rather than to weaken the floor.

---

## V2.10.7

### Fixed

- **A run that ended while the app was away came back unplayable.** END TURN
  refused every tap and nothing said why. `finish()` did two jobs — mark the run
  over, and draw the card that asks what to do next — and only the first
  survived a reload: `G.won` and `G.dead` are saved, the card is not. Coming
  back to a won or lost colony therefore meant `endTurn()` returning at its
  first line, for good.
  - Drawing the card is now its own function, called on the way out and on the
    way back in. It records nothing, so a resumed card cannot re-count a loss
    or re-add a board row.
  - A tap on END TURN in a state that outlived its card brings the card back
    rather than being swallowed.
  - Review mode is untouched: a lost run being reviewed stays open on the map.

### Verified

- Tier 0 clean: P1–P12.
- Headless Chromium, reloading mid-state as the viewer does when the app is
  left and returned to:
  - win, reload → the card is back, KEEP PLAYING works, END TURN then advances
    the turn. V2.10.6 through the same sequence: two taps on END TURN, still
    turn 0, no card.
  - loss, reload → the loss card is back, the lost-colony count stays at 1 and
    the board stays at one row.
  - REVIEW THE RUN, reload → no card, still in review on the map.
- No page errors.

### Not verified

- Tiers 1–3, and Safari.

---

## V2.10.6

### Fixed

- **The portrait gate under-read the reader's text size.** Two causes:
  - Its heading and the rotate arrow used `--tsb`, the damped scale. That
    damping exists to protect the map — the HUD's height is the map's height
    subtracted — and the gate has no map. At a system setting of 145% the
    heading had grown 14%, which left it *smaller* than the line beneath it.
  - The gate was also held to the same 145% ceiling as the HUD, which exists so
    the top readout still fits across the screen. The gate is a card of words
    with nothing to fit.
- **The gate now has its own scale, `--tsg`**, which follows the reader's
  setting whole, up to 220%, and moves every line of the card together. The
  gate also starts a step larger: heading 15px, subtitle 12px, the switch 11.5px
  and the notes 10px, before scaling. It scrolls rather than clipping if it
  ever outgrows the screen.
  - A fixed size — S to XXL — drives the gate the same way, so XXL enlarges it
    too.
  - The HUD is untouched: AUTO still caps at 145% there, and a tile is still
    the same size at every setting.

### Verified

- Tier 0 clean: P1–P12, with P8 now recognising `--tsg` as a scaled size.
- Headless Chromium, portrait 395×750, driving the system probe and touching
  nothing else:
  - at 100%: heading 15px, notes 10px.
  - at 145%: heading 21.8px, notes 14.5px — every line grown by the same
    proportion, and the heading larger than the subtitle again.
  - at 310%: `--tsg` 2.2, heading 33px, notes 22px; the card is 343×579 and
    still fits the screen, with nothing cut off at either width.
  - at 304×750, the narrowest fixture, the same 310% card is 286×680 and fits.
  - the change lands without a tap, a rotation or leaving the app.
- Landscape at the same 310% system setting: `--ts` stays 1.45, the top row
  stays 63px, and the map cell stays 21.9 — the cap still does its job.
- Manual XXL drives the gate too: heading 26.3px.
- No page errors.

### Not verified

- Tiers 1–3, and Safari.

---

## V2.10.5

### Added

- **Two larger text steps, XL (150%) and XXL (175%).** Text size now cycles
  AUTO / S / M / L / XL / XXL. Page zoom is not always available — an embedded
  viewer can refuse the pinch outright — so the app's own text has to go far
  enough to read the panels without it.
  - AUTO still tops out at 145%, because past that the top readout no longer
    fits across the screen. XL and XXL are a deliberate choice, not something
    the system setting can impose.

### Changed

- **The portrait gate names rotation lock.** With the phone locked in portrait,
  turning it does nothing and *TURN YOUR PHONE* is advice that cannot be
  followed. The gate now reads *Rotation locked? Unlock it in Control Centre*,
  above the line naming the DISPLAY switch. The switch on the gate is still the
  other way out.
  - A page cannot force or unlock an orientation on iOS: `screen.orientation
    .lock()` exists only where the Fullscreen API does, and iOS Safari has no
    element fullscreen. Saying so is the whole fix available.

### Verified

- Tier 0 clean: P1–P12.
- Headless Chromium, 750×304, tools open on DISPLAY at every step from S to
  XXL: no row in the panel clips, the panel stays inside the map area, no build
  row clips, and the map cell stays 21.9 — check V12 — at all six settings. The
  panel grows from 278px wide to 461px and scrolls, as it already did.
- The gate at 395×750 and 304×750, AUTO, L and XXL: the card fits the screen at
  all of them, and both notes read in full.
- No page errors.

### Not verified

- Tiers 1–3, and Safari.

### Worth watching

- Whether the pinch works at all is the host's decision, not the game's: the
  panel asks for `pinch-zoom` and the viewport allows it. In an embedded viewer
  that refuses page zoom, XL and XXL are the way to read the panels; opening the
  same build in Safari gets the pinch back.

---

## V2.10.4

### Fixed

- **AUTO text size did not follow the system setting while the game was open.**
  Changing Dynamic Type from Control Centre left the game at the old size until
  something else re-laid it out — leaving the app and coming back, rotating, or
  cycling the Text size row by hand.
  - The cause: the probe that measures the setting, a hidden element rendered
    at `-apple-system-body`, was built and thrown away on each measurement, and
    a measurement only ever happened as part of a layout.
  - The probe now stays in the document, and a `ResizeObserver` watches it.
    Changing Dynamic Type re-renders the probe at the new size, which resizes
    it, which is the event. No polling and no waiting for the app to be
    revisited. A two-second timer is the fallback where there is no observer,
    and it does not run while the app is off screen.
  - The DISPLAY row repaints with the new percentage if it is open at the time.
  - A fixed size — S, M or L — still ignores the system entirely.

### Verified

- Tier 0 clean: P1–P12.
- Headless Chromium, the tools panel open on DISPLAY, driving the probe and
  touching nothing else — no focus, no resize, no tap:
  - probe at 140% → the app is at 140% within 250ms, and the row reads
    `AUTO · 140%`.
  - back to 100% → 100%.
  - 160% → 145%, the cap.
  - switched to fixed M, probe moved again → stays at 115%.
  - the map cell stays 21.9 throughout, which is check V12.
- V2.10.3 through the same sequence never leaves 100%.
- No page errors.

### Not verified

- Tiers 1–3, and Safari. Chromium has no `-apple-system-body`, so the test
  drives the probe with a stylesheet instead: what is proven is that the app
  follows the probe, not that iOS resizes it. That part is the playtest.

### Worth watching

- AUTO is capped at 145%, which is why a phone set to 310% reads `AUTO · 145%`.
  Past that the top readout scrolls sideways rather than fitting. The cap is one
  number if a bigger ceiling is wanted.

---

## V2.10.3

### Fixed

- **RESTART and STRIP were squeezed and cut off.** With CLEAR held on a machine,
  the action cell splits into two buttons. It stayed 108px wide, but at 135%
  text the two words need 137px, so they clipped to `ESTART` and `STRI`. They
  were also only 24px tall.
  - The cell now takes the width its two halves need, about 145px at 135%, from
    the objective line beside it. It goes back to 108px when it holds one
    action.
  - Each half is glyph over word, like every other action in the lane: the
    machine's own glyph over IDLE or RESTART, `×` over STRIP.
  - Each half is the full lane height, about 43px, and is a rounded glass
    button with glass on.

### Verified

- Tier 0 clean: P1–P12.
- Headless Chromium, 750×304, an idled mine selected with CLEAR held. Glass on
  at text 100%, 135% and 150%, glass off at 135%, and LEFT and RIGHT at 135%:
  - Neither half clips, and each takes a tap at its centre.
  - The cell stays inside the lane.
  - The objective line keeps 311px or more.
- V2.10.2 on the same setup: halves 76 + 57px inside a 108px cell, 24px tall.
- No page errors.

### Not verified

- Tiers 1–3, and Safari.

---

## V2.10.2

### Changed

- **The site field stops previewing codes while you type.** Every keystroke of
  half-typed text was worked out into a fresh, unrelated site code (`WTF` showed
  `→ NOON-DAY-699`), which was noise. The line under the field now only talks
  about what you are typing:
  - **Not a code yet:** `WORD-WORD-###`, the shape a code takes. The empty field
    shows the same as its placeholder.
  - **A real code:** a tick, `✓ SCARP-REGOLITH-192`, plus *you are already here*
    when it is the site you are on. Spaces count as dashes.
  - **A code with a slip in it:** the red *did you mean …? Tap to use it*, as in
    V2.10.1. The *as typed, it lands on …* line under it is gone.

  Any words still land somewhere — LAND THERE takes them as before, and THIS
  SITE shows the code you arrived at.

### Verified

- Tier 0 clean: P1–P12.
- Headless Chromium, typing into the real field: `SCARP-REGOLITH-192` letter
  by letter shows `WORD-WORD-###` until it is a code, then ticks. `hello moon`
  and `XYZZY-REGOLITH-192` show `WORD-WORD-###` and no code. The typo, swap
  and dropped-letter cases still offer the fix, tapping it fills the field, and
  LAND THERE lands on SCARP-REGOLITH-192. No page errors.

### Not verified

- Tiers 1–3, and Safari.

---

## V2.10.1

### Fixed

- **Typing in the site field could end turns.** The keyboard shortcuts listened
  everywhere, text fields included, and the phone's keyboard sends the same
  keys. So typing *any words at all* into LAND SOMEWHERE ELSE did this:
  - **Space** ended a turn and never reached the field.
  - **Digits** armed build tools.
  - **V** toggled SURVEY, and three site words have a V in them.

  Typing `a b c 1` ended three turns and armed DIG. The shortcuts now stand down
  while a text field has the focus. Space still ends a turn everywhere else.
- **A mistyped site code landed somewhere else, and went on landing there.**
  `SCRAP-REGOLITH-192` is not a code — SCRAP is not a site word — so it was
  hashed like any other phrase, to FLAT-PEAK-296. Typing it again landed on
  FLAT-PEAK-296 again, which looked like the field ignoring you. The only sign
  was a small `→ FLAT-PEAK-296`, below the fold of the panel.
  - Text shaped like a code with a word off its list now reads, in red: *SCRAP
    is not a site word — did you mean SCARP-REGOLITH-192? Tap to use it.* Below
    that is where it lands as typed. One slip is caught in a short word, two in
    a long one: swapped letters, dropped letters, extra letters, and the two
    words the wrong way round.
  - Anything the field would land you on reads *· you are already here* when
    that is where you are.
  - While you type, the panel scrolls so the echo and LAND THERE sit under
    the field.
  - Free text still lands where it hashes to. Only code-shaped slips are
    questioned.

### Verified

- Tier 0 clean: P1–P12.
- Headless Chromium, 750×304, typing into the real field from FLAT-PEAK-296:
  - `SCRAP-REGOLITH-192` is flagged, offers SCARP-REGOLITH-192, and says you
    are already where it lands. Tapping the suggestion fills the field, and
    LAND THERE twice lands on SCARP-REGOLITH-192.
  - `regolith-scarp-192` is flagged as the wrong way round. `scarp regolth
    192`, with spaces, keeps its spaces and is flagged.
  - `XYZZY-REGOLITH-192` and `hello moon` hash without complaint.
    `SHACKLETON` and exact codes read ✓.
  - Typing `vast vein 1` ends no turn, arms no tool and leaves SURVEY off. Space
    outside the field still ends a turn.
- No page errors.

### Not verified

- Tiers 1–3 and Safari, including how the phone's keyboard sits over the
  panel while it is open.

---

## V2.10.0

Glass is the main line. The `-GLASS` suffix is gone, and V2.9.4 — the last
build of the boxed layout — is retired as a line of its own. Its layout is
still in the game: turn **Glass panels** off in TOOLS · DISPLAY.

Nothing to merge: nothing shipped on the old line after the branch point, and
V2.9.4's own change (idled machines draw grey) was already here.

### Changed

- **Achievements belong to a major version.** They carry across every build
  inside one — dev builds and release candidates alike — and are cleared once
  when the major version changes. V2.9.15 cleared them on every build; that is
  withdrawn. A record written before the build stamp existed is treated as V2's
  and kept.
- **Versioning.** V2.x is development and anything may change. V3.0-RC*n* are
  release candidates: presentation only, never how a turn resolves. The README
  and the test plan carry the rule.
- Code comments no longer call glass a branch.

### Coming from V2.9.4

Everything on the glass line was layout, input, copy or the end card. None of
it changed how a turn resolves.

- The map runs full-bleed with the panels floating on it; glass off restores
  the boxed layout.
- The bottom lane carries the arrows, FIT, the objective line and the action,
  ordered by handedness (BALANCED, LEFT, RIGHT).
- A drag that starts on or beside the build column scrolls the column, never
  the map.
- The top row fits without scrolling at 135% text. The night line reads
  *night 224*.
- The splash, the end card and the portrait gate are glass cards. The end
  card lays the run out in two columns and reads itself out; a tap speeds it
  up.
- The ledger counts structures standing, for SKELETON CREW.
- MAXIMUM OCCUPANCY is FULL CAPYCITY; its id is unchanged.
- Copy diagnostics adds frame-rate dips with context and the last eight
  touches.

### Verified

- Tier 0 clean: P1–P12. P2 now reads a suffix with digits, so `V3.0-RC1`
  checks the same way `V2.10.0` does.
- Headless Chromium, through real reloads at V2.10.0: a record that is
  unstamped, stamped V2.9.15-GLASS or stamped V2.10.3 is kept; one stamped
  V1.4.0 or V3.0-RC1 is cleared; the board survives every case; an award from
  this build survives a reload.
- The same build restamped as V3.0-RC1: a V2.10.0 record is cleared, a
  V3.0-RC2 record is kept.
- Glass on, off, and on again: stage 746×300, then 594×199, then 746×300;
  the build column's last row, FUSION, takes a tap in both; the grip exists
  only with glass on.
- The stamp reads V2.10.0 on the splash, in the ledger header and at the top
  of Copy diagnostics. No page errors.

### Not verified

- Tiers 1–3, and Safari. Test plan 1.3 lists what the playtest should cover.

---

## V2.9.15-GLASS

### Changed

- **Achievements are cleared by a version bump.** The record is stamped with
  the build that wrote it, and a build that finds another build's stamp — or
  the old unstamped shape — clears it before anything reads it. An award says
  this build can be beaten that way, so it is worth what that build is worth.
  Saved runs already behaved this way. The board still carries, and each row
  still names the build it was set on.
- **The storage footnote is gone from TOOLS · BOARD.** The line naming the
  storage key went with it, along with its now-dead style rule. COPY AS TEXT
  follows the achievement list directly.

### Verified

- Tier 0 clean: P1–P12.
- Headless Chromium, 750×304, four states through real reloads:
  - a record left in the old unstamped shape, with two awards, a held rating
    and a loss count: cleared, board untouched.
  - an award written by this build: survives an ordinary reload, stamped
    `V2.9.15-GLASS`.
  - that same record restamped as `V2.9.14-GLASS`: cleared, board untouched.
  - the BOARD pane: no footnote, board rows and COPY AS TEXT still there,
    `UNLOCKED · 0 of 11` after the clear.
- No page errors on any of them.

### Not verified

- Tiers 1–3, and Safari.

### Worth watching

- This is now the fastest-moving thing in the game: every build shipped in a
  session wipes the sheet. If it turns out to be wanted only during
  development, the gate is one comparison — matching the leading version
  instead of the whole string would keep awards across a -GLASS patch level
  and clear them on a minor bump.

---

## V2.9.14-GLASS

### Added

- **`structures standing` in the ledger.** SKELETON CREW asks for fewer than 20
  structures and there was no way to count what you had. The ledger now shows
  the number, taken from the same count the award is judged on — one function,
  so the two can never drift apart.

### Changed

- **The top row fits without scrolling at 135% text.** Four trims, no readout
  removed:
  - The night line under POWER and WATER reads *night 224* rather than *night
    needs 224*. It was the widest thing in the water cell, and the row is about
    the night already.
  - The sun bar in the day cell is a step smaller, and LEDGER's letter-spacing
    is tighter.
  - Cell padding is 6px rather than 7–8px, and the labels are set a little
    tighter.

### Verified

- Tier 0 clean: P1–P12.
- Headless Chromium, 750×304, with a mid-game readout (573/1640, night 224,
  6/8 crew, 6/6 labour): the row needs 723px against 724px of space at 135%
  text, where V2.9.13 needed 795px and clipped LABOR. It still fits at 100%
  and 115%.
- The ledger reports the same count `builtCount()` returns; no page errors.

### Not verified

- Tiers 1–3, and Safari.

### Worth watching

- At 150% text the row is still about 56px too wide and scrolls. The next
  candidates are the POWER cell — it is the widest now, at *573/1640 +114* —
  and dropping the word LEDGER for its arrow alone.

---

## V2.9.13-GLASS

### Changed

- **The portrait gate's note is shorter**: *Switch lives in [≡] TOOLS ·
  DISPLAY, toggle to turn off.* The 280px cap on it was narrower than the card
  it sits in, so the note now uses the width it has, and where it does wrap the
  two lines are balanced rather than ragged. The footnote is a half-step
  smaller.

### Verified

- Tier 0 clean: P1–P12.
- Headless Chromium, portrait 395×750: one line at text AUTO; two balanced,
  centred lines at M and L. At L the sentence wants about 410px and the card
  gives about 300, so no text size in normal use fits it on one line in
  portrait — see below.
- No page errors.

### Not verified

- Tiers 1–3, and Safari.

### Worth watching

- One line in portrait at 135% needs either about 35 characters — *[≡] TOOLS ·
  DISPLAY toggles it off.* — or a footnote about a third smaller than it is
  now. The wording is the cheaper of the two.

---

## V2.9.12-GLASS

### Changed

- **The portrait gate names the tools panel with its glyph** too: *The same
  switch lives in [≡] TOOLS · DISPLAY, to turn back off.* The style rule for
  the glyph moved off the hints box, since it should look the same wherever
  the panel is named.

### Verified

- Tier 0 clean: P1–P12.
- Headless Chromium: the gate renders with the glyph and the note still sits on
  two centred lines; the end-card hints line is still one line at AUTO, M and
  L; no page errors on either screen.

### Not verified

- Tiers 1–3, and Safari.

---

## V2.9.11-GLASS

### Fixed

- **The tools button read as a square inside a rounded shadow.** The bar kept
  its own square-cornered background from the opaque theme, and with no
  clipping on the panel it sat proud of the panel's 14px corners — most
  visible when the panel is shut and the bar is all there is. On glass the bar
  is now transparent, so the panel is the only surface and the button is as
  round as the panel it opens. Shut, it is a rounded pill with a little more
  room around the glyph. Glass off is untouched.
- **The hints line on the end card wrapped to two lines.** It is shorter now —
  *Objective hints are off — [≡] TOOLS · DISPLAY turns them on.* — and the box
  is a half-step smaller with tighter padding.

### Verified

- Tier 0 clean: P1–P12.
- Headless Chromium, 750×304: the hints line is one line at text AUTO, M and L
  (--ts up to 1.32); the phone was at 1.35 when it wrapped, and the line is now
  about a third shorter than the space it has.
- The tools button, shut and open, on glass and with glass off; no page errors.

### Not verified

- Tiers 1–3, and Safari.

---

## V2.9.10-GLASS

### Changed

- **The end card reads at a third of the pace.** Every constant behind it is
  three times what it was: the verdict fills over 2.7s, each character takes
  33ms, the beat between lines is 270ms, and the board, hints box and
  attribution fade over 1.26s. The gap between the verdict and the first typed
  line is now its own constant, `OVER_LEAD`.

### Verified

- Tier 0 clean: P1–P12.
- Headless Chromium, 750×304, a forced loss with the full seven-line
  post-mortem: the buttons come live at 12.2s, where V2.9.9 took 3.5s. One tap
  at 3s brings that to 5.4s; a second tap at 3.6s ends it at 4.2s.
- No page errors.

### Not verified

- Tiers 1–3, and Safari.

### Worth watching

- Twelve seconds is a long time for a card with nothing to press on it. If a
  player who does not know about the tap reads it as a freeze, the fix is
  either a faint line saying the screen can be tapped, or letting the buttons
  appear before the fade-ins finish.

---

## V2.9.9-GLASS

### Changed

- **The end card is laid out in reading order.** The run was one column with the
  build line buried in the middle of it, which read as though the attribution
  were a statistic.
  - The run is one block in **two columns**, filled down the left and then the
    right: turns survived, nights endured, peak crew, fusion on the left; the
    post-mortem — first brownout, peak power banked, turns in deficit — on the
    right.
  - Then the board, then the hints box, then the attribution, then the buttons.
- **The hints box names the tools panel with its glyph**, `[≡] TOOLS ·
  DISPLAY · Objective hints`, since TOOLS is a button on screen and a reader
  who has not opened it has no way to know that.

### Added

- **The card reads itself out.**
  - **COLONY LOST fills from the top down**, out of the dark into red — a
    gradient three times the height of the line, sliding up through it, with
    the text as its mask. SELF-SUFFICIENT does the same in amber.
  - **The obituary fades in**, then the run **types line by line**, left column
    first. Each line's full text is held in place invisibly underneath, so
    nothing on the card moves while it types.
  - **The board, the hints box and the attribution fade in last.**
  - **The buttons are not there until it is done** — invisible and untappable,
    so nothing can be pressed by accident mid-sentence.
  - **A tap anywhere speeds it up** four times over, and a tap after that ends
    it immediately. With the buttons inert until the end, a tap can only mean
    get on with it.
  - `prefers-reduced-motion` goes straight to the finished card.
  - The intro stops if the card is dismissed while it is still running.

### Verified

- Tier 0 clean: P1–P12.
- Headless Chromium, 750×304, a forced loss: at 0.4s the verdict is a third
  filled with nothing else on the card and the buttons at opacity 0; at 1.6s
  the verdict is full and two lines have typed; at the end every line is
  complete and the buttons are live.
- Tapping at 1.6s finishes the remaining five lines inside 0.8s; the second tap
  ends it; the buttons then take taps.
- `prefers-reduced-motion: reduce` renders the finished card in the first frame.
- A win renders SELF-SUFFICIENT, four stats in two columns, the board, and
  KEEP PLAYING / FIND A NEW SITE.
- No page errors on either path.

### Not verified

- Tiers 1–3, and Safari. `background-clip: text` carries the verdict; where it
  is unsupported the word is drawn in flat colour with no wipe, which is the
  `@supports` fallback rather than a guess.

### Worth watching

- The typing takes about 3.5 seconds at full length on a loss. If that is long
  on the second or third colony lost in a row, the per-character step is one
  constant, `OVER_CHAR`.

---

## V2.9.8-GLASS

### Fixed

- **Scrolling the build list at the screen edge moved the map.** With the
  panels floating, the build column is ringed by 10px of map on every side,
  including the strip between it and the screen edge where a thumb rests. A
  touch that began in that strip belonged to the canvas, so the drag panned the
  map instead of scrolling the list. Reproduced headlessly: three drags started
  just outside the column all panned.
  - A transparent grip now sits under the column and over the map, covering the
    ring out to the screen edge. A touch that starts on it scrolls the build
    list and nothing else until the finger lifts. It follows LEFT, works in the
    rotated portrait view, and is absent with glass off, where the column meets
    the screen edge directly.
  - The canvas gestures count `targetTouches` rather than `touches`, so a
    finger that went down on a panel can never become part of a pan or a pinch.

### Changed

- **The splash, the verdict and the portrait gate are glass.** The scrim behind
  them blurs whatever is underneath; the card on it is a tinted, ruled sheet
  with the same top-edge specular as the panes in play, rounded 18px. BEGIN,
  KEEP PLAYING and RUN IT AGAIN are rounded amber-tinted buttons. There is
  little behind the splash to bend, so the tint does most of the work. Glass
  off, and `prefers-reduced-transparency`, keep the opaque versions.
  - The portrait gate's contents sit in a card, which is one wrapper `div` in
    the markup and changes nothing with glass off.
- **MAXIMUM OCCUPANCY is FULL CAPYCITY.** The id stays `big_herd`, so anyone who
  already holds it keeps it.
- **A dip is now a second under 30 fps, not 50.** Nothing in a turn-based game
  needs more than a steady 30.

### Added

- **Copy diagnostics · `touch`.** Where each of the last eight touches began —
  the element it landed on and the screen point — and whether it became a pan
  or a list scroll. Capture-phase and passive: it watches and changes nothing.

### Verified

- Tier 0 clean: P1–P12.
- Headless Chromium, 750×304, glass on, RIGHT and LEFT: drags starting in the
  outer edge strip, the strip on the map side and the gap above the column
  scroll the list, with the map's pan unchanged. A drag on open map still pans.
  V2.9.7 on the same drags: all three panned the map.
- Rotated portrait view: a drag on the grip scrolls the list by 80px; no pan.
- Scrolled to the end, FUSION hit-tests to its own row in glass RIGHT, glass
  LEFT and glass off.
- The portrait gate's switch still turns rotation on through the tap.
- A glass-off save still resumes as glass off.

### Not verified

- Tiers 1–3, and Safari. The grip was confirmed against the cause found in
  Chromium; whether that is the cause on the phone is what the `touch` line in
  Copy diagnostics will say.

### Worth watching

- The grip also covers the 10px of map on the inner side of the column, so a
  tile there can no longer be tapped without panning it clear first. If that
  gets in the way, the inner strip can go and the outer edge stay.
- If the splash still reads as flat, the next step is a faint image of the
  site behind it rather than more tint.

---

## V2.9.7-GLASS

### Fixed

- **FUSION could not be tapped.** The direction pad floated at the bottom-right
  corner, over the last rows of the build column. Scrolled to the end, a tap on
  FUSION landed on the pad. The pad now lives in the lane in both modes, and the
  lane runs the full width, so the build column ends above it with nothing on
  top of it.
- **Turning glass off left the glass layout in place with the backs removed.**
  Only a few glass rules were undone for glass off, and one of those lost on
  specificity: `#side{background:transparent}` beat `.noglass .glasspane`, so
  the build column floated over the map with no back at all.
  - Every glass rule is now scoped to `#app.glass`. Glass off removes the class
    and the V2.9.4 layout is the layout.
  - **The stage kept its glass height after the switch.** The canvas was in
    flow, so a 300px canvas sized the grid row to 300px, which `resize()` then
    measured and kept. The canvas is out of flow and the row is
    `minmax(0,1fr)`: glass off now measures 199px, as V2.9.4 does.
  - The same specificity problem made `prefers-reduced-transparency` and the
    no-blur fallback draw clear panes with no blur. Both now win.
- **The FPS meter drew over the tools panel.** It sat at z-index 22 against the
  panel's 17. It now sits under the panel and the ledger.
- **A dragged tools panel stretched.** Once moved, its inline `left` was set
  while the glass anchor still set `right`, so the panel spanned between them.
  The anchor lets go once the panel is moved.
- **The tools panel ran under the lane.** Its height and drag range now stop
  above it.
- Duplicated `applyGlass()` / `applyFps()` calls left by an earlier patch in the
  handedness row and the resume path are gone.

### Changed

- **BALANCED splits the thumbs: arrows · FIT · description · action.** The left
  thumb moves the view; the right thumb builds, with the action cell under the
  build column. It used to differ from RIGHT only in where the action cell sat,
  which on a phone reads as the same layout.

  | | lane | build column |
  |---|---|---|
  | LEFT | arrows · action · description · FIT | left |
  | RIGHT | FIT · description · action · arrows | right |
  | BALANCED | arrows · FIT · description · action | right |

  - FIT goes with whichever thumb is not building. With glass off it is the chip
    over the map, as before, and `#lanefit` takes no room.
  - `#bact` no longer carries its own right rule; the mode says which edge.
- **The tools panel has no blur of its own** with glass on. It was a second
  pane over the map at .92 opacity, costing a blur for almost nothing visible.
- The FPS meter follows the build column's side in LEFT; the full-screen button
  (not offered on iOS) sits beside the tools button rather than on the lane.

### Added

- **FPS meter, second pass.**
  - The first two windows after the meter starts, or after glass is toggled,
    are warm-up and not counted. A saved `fps=true` starts the meter during page
    load, which is the likely source of the turn-0 low of 25.
  - A window longer than 1.6s (tab hidden, rAF paused) is dropped rather than
    counted as a stutter.
  - Toggling glass restarts the meter, so each half of the comparison is
    measured on its own.
  - Every window under 50 is a **dip**, counted on the meter and logged in Copy
    diagnostics with the turn, glass state, and whether tools, the ledger, zoom
    or night were in play. The low is tagged the same way.

### Verified

- Tier 0 clean: P1–P12.
- Headless Chromium at 750×304, glass on and off, all three hands, text S and L:
  - Scrolled to the end, FUSION, WALLOW and PROCESSOR each hit-test to their own
    row in every glass mode. In V2.9.6 the same test put FUSION on `#nudge`.
  - Tapping `Glass panels` off through the real row: stage 199px, canvas
    backing store 398px, tools panel bottom 248 inside a stage ending at 254.
    V2.9.6 on the same path: stage 300, tools past the stage.
  - Glass off, a resumed save restores `noglass`, the pad in the lane and FIT
    over the map.
  - Handedness row cycles LEFT → RIGHT → BALANCED; the pad stays in the lane
    throughout.
  - A forced 450ms main-thread block registers as one dip with its context; a
    glass toggle then resets the meter to warm-up.
- No simulation, cost, site-generation, turn-resolution, persistence or
  hit-testing code was touched.

### Not verified

- Tiers 1–3, and anything on the phone. Chromium is not Safari, and the blur
  cost the meter is there to find is Safari's.

### Worth watching

- At text L the build column shows about two and a half rows before it scrolls.
  If that is too few, the alternative is the lane stopping short of the column
  and the column running to the bottom edge, at the cost of about 160px of lane
  text.
- The glass panes are drawn clear, as they were in V2.9.6: the `.55` tint in
  `.glasspane` was always overridden. Kept as seen rather than changed quietly.

---

## V2.9.6-GLASS

### Fixed

- **The ledger could take the top bar off screen and refuse to come back.**
  `#probe` is sized as a share of `#stage`, and on this branch the stage is the
  whole screen rather than the old boxed area — so 70% wide and 88% tall could
  exceed the room between the floating panes and push the HUD out with it. It is
  now anchored under the top pane, bounded by the other two, and never wider than
  the clear area.
- **END TURN and the gutters were opaque.** Both were panels of their own inside
  a sheet that is meant to be one pane: glass on glass, with a black bar across
  it. END TURN is now a tinted pane with its own rule, and the gutters are
  transparent.

### Changed

- **A colony opens on its crest**, upper left, where the sun is and where the
  first decision is. Centring showed the middle of a map twice the height of the
  screen, most of it ground nobody has dug.
- **The tools panel sits over the map in the top corner**, clear of the build
  column, and keeps a solid back rather than stacking a second pane.
- **FIT and the direction pad swap.** The pad floats at the bottom-right corner
  where a thumb rests; FIT takes its slot in the lane. The elements move rather
  than being duplicated, so each keeps one handler and one live state, and they
  swap back when glass is turned off.

### Added

- **TOOLS · DISPLAY · FPS meter.** `now · low · avg`, sampled over one-second
  windows. Off by default and the loop does not run when off, so it costs nothing
  unless it is being read. The numbers also go into Copy diagnostics.
  - The **low** is the number that matters. An average hides exactly the stutter
    worth finding, which on this branch is a blur re-sampling a live canvas.
  - Glass panels can be toggled off in the same pane, so both halves of the
    comparison are in one build.

### Verified

- Tier 0 clean: P1–P12.

### Not verified

- Tiers 1–3. Test plan 1.2 adds F1–F5 for exactly this branch.

---

## V2.9.4

### Changed

- **Idled machines draw grey.** An idled machine carried the same colour as a
  running one with a small slash over it. Idling is the most-used decision in
  the game and the thing you scan the map for, so it should read at a glance
  rather than on inspection. Idled is now `--dim` whatever the structure, 130
  luminance below the brightest running state. Unpowered still draws alarm red,
  which outranks both.

---

## V2.9.4-GLASS · branch

Not a successor to V2.9.4 — a branch from it, identical in every other respect,
so both can be played and one thrown away. The version string carries `-GLASS`
so a screenshot says which you are looking at.

### Changed

- **The map is the screen.** It runs full-bleed behind everything; the HUD, the
  build column and the status lane float on it as translucent sheets with rounded
  corners and a 10px inset. Glass needs something behind it to bend — over the
  black margin of the old layout it would have read as tinted film, which is why
  full-bleed had to come first.
- **Tiles grow.** The reference cell is measured against the whole screen rather
  than the space left between panels, so the map is drawn at roughly twice the
  area.
- **You can pan any tile out from under a panel.** The pan range is extended by
  the measured panel extents, and the resting position after FIT centres the map
  on the clear area between them rather than on the screen.
- **One sheet per surface, never glass on glass**, per Apple's guidance. The
  tools panel and the ledger already float over the map, so they keep their solid
  backgrounds rather than stacking a second pane.
- **Three ways back to opaque**: `prefers-reduced-transparency`, a DISPLAY toggle
  (`Glass panels`), and an `@supports` fallback for anything that cannot blur.

### Verified

- Tier 0 clean on both builds: P1–P12. `preflight.py` updated to accept a branch
  suffix in the version string.

### Not verified

- Tiers 1–3, and the thing that actually matters here: whether `backdrop-filter`
  over a live canvas holds frame rate on the phone. That is the reason this is a
  branch rather than a release.

---

## V2.9.3

### Changed

- **Objective hints are off by default.** Working out that the night needs
  batteries, and that arrays belong on the crest, is the game; a line saying so
  on turn one is a walkthrough. TOOLS · DISPLAY · Objective hints turns them on.
  - Self-sufficiency still reports either way. It says what the colony *is*, not
    what to do next, so it is a state rather than a hint.
- **The hint is offered once, after a colony is lost.** A player who has not yet
  failed has no reason to want the answers; a player who has may not know they
  exist. The loss overlay names the setting, and only while hints are off.
  - Losses are counted in the achievement store, so the offer survives a version
    bump the same way the board does.

### Verified

- Tier 0 clean: P1–P12.

---

## V2.9.2

### Fixed

- **`Your arrays sit in shadow` kept saying that when it was not true.** The
  test is "solar income under 36"; shadow is only one of the ways that test
  fails, and arrays in full sun but too few of them made the line a lie. The
  objective now reads the ledger: `Your arrays sit in shadow` at zero income,
  `Solar makes 11 of 36` above it. Objective text functions receive the ledger.
- **DIG said BUILD.** It opens ground rather than building anything, and the
  button should say what the tool does rather than what most tools do.

### Changed

- **Air between the glyph and the word** in the action cell: 3px scaling with
  the text, and the wrapper's leading up from 1.2 to 1.45.

### Verified

- Tier 0 clean: P1–P12.
- The objective at solar 0, 11, 26, 35 and 36: the shadow line only at zero, the
  count in between, and the next objective at 36.

---

## V2.9.1

### Changed

- **The action-button toggle becomes a handedness setting: LEFT · RIGHT ·
  BALANCED**, and it moves every control rather than one button.

  | | lane | build column | FIT |
  |---|---|---|---|
  | LEFT | arrows · action · description | left of the map | bottom-left |
  | RIGHT | description · action · arrows | right | bottom-right |
  | BALANCED | action · description · arrows | right | bottom-right |

  - LEFT puts the action 0px from the left edge; RIGHT puts it 176px from the
    right, just past the arrows; BALANCED splits them.
  - Still flex `order`, so nothing in the markup moves and the file reads the
    same whichever mode is set.
  - Each mode names which edges carry a divider. A rule drawn from the DOM order
    lands on the wrong side of a reordered row, which is the kind of thing that
    looks fine in one mode and wrong in the other two.
  - In LEFT the build column swaps sides with the map and its border swaps with
    it, and the FIT chip follows to the bottom-left.
  - Defaults to BALANCED, which is the arrangement as it stood.

### Verified

- Tier 0 clean: P1–P12.

### Not verified

- Tiers 1–3 need a device. LEFT in particular moves the build column for the
  first time; worth a look that the map and the panel have not swapped borders.

---

## V2.9.0

### Added

- **TOOLS · DISPLAY · Action button — LEFT or MIDDLE.** Middle puts it between
  the description and the direction pad, 176px from the right edge instead of
  638px, so a right thumb reaches it without leaving the arrows. Which hand the
  phone is in decides where that button should be, and only the person holding
  it knows.
  - Defaults to MIDDLE.
  - Implemented with flex `order`, so the reading order of the file stays the
    reading order of the lane and nothing has to move to change a preference.
  - The divider follows the button to whichever side needs it.
  - Saved with the run, applied on load and on restore.

### Verified

- Tier 0 clean: P1–P12.

### Not verified

- Tiers 1–3 need a device. Whether MIDDLE actually reaches better than LEFT is a
  thumb question, not an arithmetic one.

---

## V2.8.9

### Fixed

- **The glyph and the verb were rendering on one line** — `~BUILD`, `∩BUILD` —
  in both V2.8.7 and V2.8.8. `#bact` is a flex container, so every element child
  becomes a flex *item* and sits in a row, and a `<br>` between flex items does
  nothing at all.
  - Plain text with `<br>` had worked because the text collapses into one
    anonymous flex item, where the break still applies. The moment the glyph got
    its own `<span>` in V2.8.7, the two became two items side by side, and adding
    an explicit `<br>` in V2.8.8 changed nothing because it was a third item.
  - Everything the cell writes now goes inside a single wrapper, so there is one
    flex item and ordinary block layout inside it.

### Verified

- Tier 0 clean: P1–P12.

### Note

- I said in V2.8.8 that an explicit break "can't fail that way". It failed in
  exactly that way, and I asserted it without being able to render the page. The
  screenshots were the only thing that could have told either of us.

---

## V2.8.8

### Changed

- **An explicit `<br>` between the glyph and the verb**, and the two spans go
  inline so the break is what stacks them. They were block-level spans stacking
  by their own display, which gives the same result until something changes the
  display and it silently doesn't.

### Verified

- Tier 0 clean: P1–P12.

---

## V2.8.7

### Changed

- **The action button is a glyph over a verb.** It had been carrying the name of
  the thing as well as the verb, which is what forced three lines of five-letter
  fragments. The glyph says which thing in one character, the description line
  beside it says which one in full, and the button keeps the one word that
  matters: what tapping it does.
  - `◫ / BUILD`, `∩ / STRIP`, `× / BACKFILL`, `≋ / IDLE`, `(6) / IDLE ALL`.
  - Every actionable state is now exactly two lines, whatever the structure.
- **Refusals are two words at most.** Thirteen of them were three lines of
  fragments; none is now. `not enough power` → `no power`; `dig it out first` →
  `dig first`; `must sit beside a habitat` → `needs a hab`; `too deep — He-3 is
  near the surface` → `too deep`.

### Verified

- Tier 0 clean: P1–P12.
- Fifteen actionable states: all exactly two lines.
- Thirteen refusals: all were three lines, none is now — seven at two, six at one.

### Worth watching

- The refusals lost their explanations along with their length. `too deep` no
  longer says helium sits near the surface, and `needs a hab` no longer says
  beside. If a new player stalls on one of those, the sentence belongs in the
  description line, not back in the button.

### Not verified

- Tiers 1–3 need a device.

---

## V2.8.6

### Changed

- **The action cell wraps by width rather than by word.** One word per line was
  breaking phrases that fit together — `arrays / go / on` for something eight
  characters long. It now fills each line to the width the cell actually has,
  about eight characters, and stops at three lines, keeping any remainder on the
  last line rather than dropping it.
  - `arrays / go on`, `last / habitat`, `IDLE ALL / (6)`, `BUILD / BATTERY`.
- **`the last habitat must stand` becomes `last habitat`.** A refusal in a 108px
  cell is a label, not a sentence.
- **The objective breaks at the sentence.** The first says what is wrong, the
  second what to do about it, and they are easier to take in apart than run
  together.
- **Less prose in the objectives.** `Build ARRAYS on the bright crest` →
  `on the crest`; `Build BATTERIES to bank power` → `Build BATTERIES`;
  `Ice sits 3+ rows below the basin floor` → `Ice sits deep in the basin`;
  `Free play — grow the herd as far as the ice will carry it` → `Grow the herd
  as far as the ice allows`.

### Verified

- Tier 0 clean: P1–P12.
- Every action label through the wrapper: fifteen cases, longest three lines,
  none truncated.
- Every objective at one sentence per line against a 462px description: worst
  case two lines, and the lane shows three before it scrolls.

### Not verified

- Tiers 1–3 need a device.

---

## V2.8.5

### Changed

- **The lane is a fixed 48px and its text scrolls.** It was a minimum height, so
  a three-line label grew it; now it holds three lines of the objective at
  12px/1.2 — 43px against 48 with padding — and anything longer scrolls rather
  than pushing the map up.
- **The action cell narrows from 152px to 108px**, and its padding and leading
  come in. The description gains that width: 462px of the 746px lane.
- **`IDLE ALL (6)` rather than `IDLE ALL ·6`.** Brackets read as a count of what
  the button acts on. The long form goes in the line beside it — `· 6 running`,
  `· 13 idled` — so the detail is there whether or not the button has room.
- **The map clips the sky rather than the ground.** At a fixed tile size the map
  can be taller than the stage, and centring it took the overflow off the top
  *and the bottom* — the bottom being the deep regolith where the ice is. FIT now
  anchors to the bottom, so the rows that go are the vacuum above the crest.

### Verified

- Tier 0 clean: P1–P12.
- Against the viewport in your diagnostics (874×327): the 14px the lane gives
  back is more than the map was overflowing by, so at that size nothing is
  clipped at all now. The anchor is there for the viewports where it still is.
- Lane arithmetic: action 108 + arrows 176 + description 462 = 746.

### Not verified

- Tiers 1–3 need a device.

---

## V2.8.4

### Changed

- **The bottom lane runs the full width of the app**, 594px to 746px. V2.6.1 had
  put it under the map only so the build column could run full height; now that
  the lane carries the action and the direction pad as well as the text, it needs
  the width more than the column needs the height. The column scrolls, so what it
  gives up it can still reach.
  - The description gets 418px, up from 266.
- **Action labels are capped at three words.** `no labor left this turn` becomes
  `no labor left`; `STRIP WALLOW · +9p +35w` becomes `STRIP WALLOW`, with the
  salvage numbers moved to the detail line beside the button, where the rest of
  the tile's detail already is.
  - The bulk labels keep their count by attaching it to the third word —
    `IDLE ALL ·6` rather than `IDLE ALL · 6`, which the cap would have cut.

### Verified

- Tier 0 clean: P1–P12. Divs balance, lane is a sibling of `#main` rather than a
  child of `#left`.
- Every action label at three words or fewer, so the cap never truncates one.

### Not verified

- Tiers 1–3 need a device.

---

## V2.8.3

### Changed

- **The bottom lane reads ACTION · DESCRIPTION · NAVIGATION.** The thing you are
  about to do belongs at the start of the line, not wedged between the tile
  description and the direction pad.
- **The lane is 23% shorter**, 62px to 48px at S. The 62px was set before the
  arrows lived there; the arrows now set the floor, so the reservation above
  them was empty space. 14px back to the map.
- Arrows 46px square to 44px — still exactly the 44pt touch minimum at S, and
  larger above it.

### Verified

- Tier 0 clean: P1–P12.
- Lane arithmetic at every text size: height 48–53px, action 152px, description
  249–266px, arrows square and never under 44pt.

### Not verified

- Tiers 1–3 need a device.

---

## V2.8.2

### Fixed

- **The status detail truncated before the scroll box ever saw it.** V2.8.1 made
  `#binfo` scrollable, but `#detail` still carried `white-space:nowrap` with
  `text-overflow:ellipsis` — the characters were discarded at the line, so there
  was nothing overflowing to scroll to. It wraps now. A scroll container around a
  line that truncates itself is not a fix.
- **The arrows were not square.** `aspect-ratio:1` was being overridden by the
  row's stretch. Both dimensions are now set outright, so square is square
  however the app is turned.

### Changed

- **Action labels go one word per line.** The cell is 152px however the app is
  rotated, and a label is two to five words; `pick a tool` becomes `pick / a /
  tool`. Applied to every label rather than the placeholder alone — `BUILD
  BATTERY` had the same problem — and routed through one function, so nothing
  writes to that cell without stacking.
- Action cell type down from 12.5px to 11.5px, placeholder from 10px to 9.5px.

### Verified

- Tier 0 clean: P1–P12.
- Every action label at one word per line: longest single word is 7 characters,
  about 48px at S, against a 152px cell. Nothing overflows.

### Not verified

- Tiers 1–3 need a device. The rotated view in particular.

---

## V2.8.1

### Fixed

- **Taps were landing on the wrong tile, by the width of the safe area.**
  `canvasOrigin()` measures from `#app`; `appPoint()` returned raw client
  coordinates. Those agreed until V2.5.1 moved `#app` inside the safe area with
  a 2px gutter — so every tap has been off by that inset since. On an iPhone in
  landscape with the notch on the left that is 49px, or three columns. In
  portrait it is 61px, four rows. Even with no inset at all it was off by the
  2px gutter. `appPoint()` now subtracts `#app`'s own rect first.
- **FIT floated over the splash.** It is z-index 24 so the tools panel cannot
  bury it; the overlays were 20. Overlays are now 30 — above the chip, below the
  portrait gate.
- **The status line could not be panned.** It clipped with `overflow:hidden` and
  a fixed max-height on the objective. Both replaced with a scrollable box that
  accepts pan and pinch on both axes.
- **The splash could not be scrolled or zoomed.** `overflow:hidden` meant
  anything past the fold was unreachable at a large text size. Now scrolls and
  takes the system pinch, as the other panels do.

### Changed

- **The arrows move into the status bar and become square.** They were the last
  thing in the build column that does not build anything, and a direction pad
  reads as a pad when its targets are as wide as they are tall. 46px square at
  S, rising with the text; the 44pt touch target holds at every size. The status
  line keeps 258px at S, and pans now, so nothing is lost.
- **RUN rows report that they ran.** Reset map view and Fix touch alignment both
  work instantly and invisibly, which reads as a dead button. They now say DONE
  in green and fade back.

### Verified

- Tier 0 clean: P1–P12. 63 unique ids, 46 targets present, divs balanced, three
  storage keys, no network, 81 scaled font sizes, every `touch-action` naming
  `pinch-zoom`, 11 achievement ids matching the awarded set, 10 of 10 seeds
  correct, 237 braces balanced.
- Bottom row arithmetic at every text size: arrows 46–51px square, action 152px,
  status line 239–258px.

### Not verified

- Tiers 1–3 need a device. The tap fix in particular wants V15 and a few taps at
  the edges of the map, in both orientations.

---

## V2.8.0

### Added

- **TOOLS · DISPLAY · Copy diagnostics.** One block on the clipboard, about 700
  characters: build stamp, site code and seed with its rating, turn and colony
  state, the view numbers, the text scale requested against the scale applied,
  page and visual viewport with the current page zoom, every display option, the
  unlocked achievement ids, the ratings tally, board size, **which storage keys
  actually exist on this host**, and the last ten log lines.
  - The storage line answers the question no amount of reasoning from outside the
    device can: whether this host shares local storage between build files.
- **`preflight.py` + `seedcheck.js`** — Tier 0 of the test plan, automated.
  `python3 preflight.py <build.html> SEEDS.txt`, exits non-zero on failure and
  prints the evidence for every check rather than a bare verdict.

### Verified

- Tier 0 clean on this build: P1–P12 all pass. 63 unique ids, 46 getElementById
  targets all present, divs balanced in `#app`, three storage keys, no network,
  81 scaled font sizes and zero bare ones, every `touch-action` pan list also
  naming `pinch-zoom`, 11 achievement ids matching the awarded set, 10 of 10
  seed codes regenerating their claimed site and rating, 235 CSS braces balanced.

### Not verified

- Tiers 1, 2 and 3 need a device with a browser and a person playing. They were
  not run.

---

## Test plan 1.0

Not a build. `TESTPLAN.md` replaced with a versioned plan covering V2.7.3,
modelled on the Ink Strike plan: four tiers, each check naming the build whose
regression it guards.

- **Tier 0** — twelve static checks that need no device. P8 (every font size
  scaled) would have caught the V2.6.2 sky label; P9 (every `touch-action`
  justified) would have caught V2.7.1; P10 (achievement table integrity) catches
  an achievement renamed out from under its check.
- **Tier 1** — the view. Zoom stability tested in both directions separately,
  since V2.7.2 fixed pinching in and V2.7.3 had to fix pinching out. Constant
  cell size across text settings is checked by reading `cell` in DISPLAY.
- **Tier 2** — the model, the herd tiles, the board, the platform.
- **Tier 3** — proof that all eleven achievements are obtainable, as four runs
  with named seeds from `SEEDS.txt`. SOL SURVIVOR was unreachable for three
  builds without anything anywhere reporting an error, which is the case this
  tier exists for. SKELETON CREW's threshold of 20 structures is flagged as
  never having been tested against a real colony.

The plan verifies against the build: eleven declared ids, all awarded in
`checkAchv`, all eleven names cited, every seed it names present in `SEEDS.txt`,
and the three storage keys it lists matching the three in the file.

On the probe question: a full one is not needed, because the ledger, the log tab
and the DISPLAY view numbers already say what a probe would print. What is
missing is portability — a tester can see all of it and send none of it. The plan
recommends one COPY DIAGNOSTICS button instead.

---

## V2.7.3

### Fixed

- **Pinch-zooming out crashed the tab.** Two faults, both mine, both from the
  last two builds:
  - **The V2.7.2 guard was one-sided.** `pageScale() > 1.01` is true when zoomed
    in and false when zoomed out, so a zoom-out ran `resetScroll()` on every
    scroll event — and `resetScroll()` calls `scrollTo`, which dispatches scroll.
    The test is now `|scale - 1| > 0.01`: any scale that is not 1 is a zoom, in
    either direction.
  - **`resetScroll()` could re-enter itself.** It now holds a flag while running,
    and only writes an offset that is actually non-zero, since writing the same
    value still counts as a write and a write is an event.
- **Zoom-out below 100% is clamped again.** V2.7.1 removed `maximum-scale=1` to
  allow accessibility zoom, which removed the whole clamp rather than its upper
  half. `minimum-scale=1` restores the floor: there is nothing to see below 100%
  in a full-bleed app, so the gesture that crashed was also the gesture with no
  purpose.

### Verified

- The guard across the scale range 0.25 to 3.0: the old one ran the scroll reset
  at every scale below 1, the new one only at exactly 1.
- Re-entrancy replayed: without the flag, 201 nested calls and a stack runaway;
  with it, one call.

### Changed

- `TESTPLAN.md` §1.1 now tests zoom out as its own case in every panel, with a
  note that it is not the same test backwards — it was only possible from V2.7.1
  and the V2.7.2 guard covered zooming in only.

---

## V2.7.2

### Fixed

- **Pinch-zooming the tools panel crashed the tab.** Four things compounded into
  an unbounded loop, each harmless alone:
  1. `viewport()` read `visualViewport.width`, which is the *visual* viewport and
     shrinks as the reader zooms in. The app was laid out against it, so zooming
     resized the app, which resized the visual viewport, which fired resize.
     It now multiplies by `scale` to recover the layout viewport, which a pinch
     does not change.
  2. `visualViewport` **scroll** fires every frame of a pinch and was wired
     straight to a full layout pass. Panning a zoomed page changes no layout, so
     it now only does the standalone scroll reset.
  3. `resetScroll()` called `scrollTo(0,0)` mid-gesture, undoing the reader's pan
     and firing another scroll event back. It is a no-op while zoomed.
  4. Every pass reallocated the canvas backing store — assigning to
     `canvas.width` reallocates even when the value is unchanged — and forced two
     synchronous reflows. Both are now skipped when nothing has changed, and the
     reference cell size is cached against the app size and text scale.

### Verified

- A thirty-frame pinch replayed through both code paths: **before**, 400 layout
  passes, 400 canvas reallocations and 800 forced reflows before the guard
  tripped — a runaway loop. **After**, 30 layout passes, 1 canvas reallocation,
  2 forced reflows, stable.

### Added

- `TESTPLAN.md`. Section 1 is zoom: the three separate mechanisms that get
  confused with each other, a stability pass that has to be held for five
  seconds rather than flicked, and a check that the three do not interfere.
  Each section names the build whose regression it guards.

---

## V2.7.1

### Fixed

- **The tools panel and the ledger accept the system pinch zoom.** `touch-action`
  is a whitelist, not a list of things to add: naming `pan-x pan-y` told the
  browser those are the only gestures the element answers, so the pinch was being
  refused on exactly the two panels carrying the most text. Both now read
  `pan-x pan-y pinch-zoom`.
  - Everywhere zoom already worked — the top readout, the build column, the
    status bar — has no `touch-action` at all, which is why those behaved and
    these did not.
  - The tools title bar keeps `touch-action:none`; it is the drag grip, and a
    pinch there would fight the drag.
  - The map keeps its own pinch zoom, unchanged.
- **`maximum-scale=1` removed from the viewport.** It is a request not to let the
  reader zoom. iOS has ignored it since iOS 10, which is why zoom worked
  elsewhere on the phone, but Android and desktop Chrome still honour it.

---

## V2.7.0

### Fixed

- **The tools panel and the ledger pan in both directions.** Both scrolled
  vertically and clipped horizontally, so at a large text size a line ran off the
  right edge with no way to reach it — the same failure the top readout had
  before V2.6.0. `touch-action` allows both axes and `overscroll-behavior:
  contain` keeps the gesture inside the panel.
- **The status line was being squeezed by FIT.** The bar sits under the map only
  since V2.6.1, so it is narrower than it was, and a 62px cell in it cost the
  objective about nine characters a line.

### Changed

- **FIT goes back over the map**, bottom right. It was moved into the status bar
  in V2.1.3 because the floating chip kept disappearing — but the position was
  never the cause. It was `display:none` until zoomed, at a z-index the tools
  panel sat above. Both were fixed long ago, so the chip can come back and the
  62px goes to the objective.
  - z-index 24, above the tools panel at 17, the ledger at 18 and the achievement
    banner at 21. Nothing the stage can draw goes in front of it.
  - Always visible, dim until the view is actually zoomed or panned.
- **The objective gets a third line** before it clips, 30px to 46px.

### Verified

- Objective width 380→442px at S, 370→435 at M, 359→427 at L — about 52 to 61
  characters a line, against a longest objective of 60.
- FIT is inside `#stage`, gone from the status bar, handler and live-state
  toggle both intact.

---

## V2.6.4

### Changed

- **The arrows, properly this time.** V2.6.3 raised the cell 13% and the glyph
  from 16px to 19px, which is below the threshold of noticing — the change was
  real and invisible. The glyph is what the eye measures, so the glyph is what
  moved: 27px now, in a 52px cell. Against V2.6.1 that is +41% cell and +69%
  glyph.
- `line-height:1` on the cell, so the glyph centres on its box rather than on its
  font metrics.

---

## V2.6.3

### Changed

- **The arrow row is sized like the rows above it.** It was 9px of padding
  around one glyph, so the column ended in a strip shorter than everything in
  it — and the arrows are the control most often used repeatedly with a thumb.
  Now a 42px minimum that scales with the text, centred rather than padded, with
  a larger glyph.
- **The portrait gate offers the setting, in the setting's own words.** It read
  `Can't turn it? Rotate the view instead`, which is a different sentence for the
  same switch that DISPLAY calls `Rotate view in portrait`. It is now presented
  as that row — label left, state right — flips to ON when tapped, and says where
  to find it again to turn it back off.

### Verified

- Arrow cell height against a two-line build row: 37→42px at S, 38→44 at M,
  39→46 at L. Apple's minimum touch target is 44pt; these were under 30 before
  V2.6.1 made the rows two lines.

---

## V2.6.2

### Removed

- **The sky label.** `POLAR DAY // LOW-ELEVATION SUN` was drawn at 8px and 16%
  opacity, unscaled by the text setting, over a dark sky — unreadable at any size
  and saying nothing the HUD does not already say.

---

## V2.6.1

### Changed

- **The build column runs the full height of the app.** The status bar used to
  span the whole width beneath both the map and the column, which capped the
  column at the map's height. The bar now sits under the map alone, inside a new
  left column, and the build list gets that height back — 183px to 245px, or
  three visible rows to five before scrolling.
- **The wallow says what the 70 is for again.** `+25 morale beside a habitat, and
  the herd needs 70 to grow`. The number alone was the efficient version; the
  clause is the one that teaches.

### Fixed

- **Achievement cards fit their text.** They were 232px with `text-overflow:
  ellipsis`, so a name or condition longer than the card was simply cut —
  `a night carried on one rea…`. The card now sizes up to 300px, capped against
  the viewport, and both lines wrap instead of truncating.
- **Tapping a card holds it.** A card that slides away while you are still
  reading it is a card you did not get to read. A tap cancels the dismissal and
  adds TAP TO DISMISS; a second tap lets it go and releases the queue behind it.

### Verified

- The restructured shell nests correctly: div balance in `#app` matches V2.6.0
  exactly, with `#main > #left > #stage, #bottom` and `#side` in the right order.

---

## V2.6.1

### Fixed

- **The unlock banner truncated the achievement it was announcing.** `a night
  carried on one rea…` — the one moment the game tells you what you just did,
  cut off mid-word. The card sizes to its contents now, capped at 300px or the
  room available, and both lines wrap rather than ending in an ellipsis. Every
  one of the eleven fits without wrapping the name.
- **Tapping the banner holds it open.** The four-second dismissal is a guess
  about how fast someone reads; tapping the card cancels it and adds `TAP TO
  DISMISS`, so the guess never has to be right. The queue waits while a card is
  held.

### Changed

- **The wallow line says what it costs you again**: `4 water/turn, no power ·
  +25 morale beside a habitat, and the herd needs 70 to grow`. The 70 was doing
  the teaching, not the 25 — without it a new player has no reason to care about
  morale at all.

---

## V2.6.0

### Fixed

- **The top readout pans instead of clipping.** At the extremes of the system
  text setting the row is simply wider than the glass, and clipping loses
  figures with no way to get them back. The row scrolls horizontally now, so
  every number is reachable at any size.
  - The step-down clamp from V2.5.1 is gone with it. It existed only to avoid
    the clipping, and it made the setting quietly do less than it was asked.
  - The cells stop shrinking, since shrinking was the other half of the same
    compromise.

### Changed

- **Every build row is two lines**, name above cost, whether or not it would
  have fitted on one. A row that changes height when it happens to fit makes the
  column jump as the colony's resources change.
- **Tool copy moved to the status bar.** Selecting a tool used to expand a
  paragraph inside the build column, pushing every row below it down. The
  description now appears in the bar that already carries the running
  commentary, and the column holds still.
- **The copy is 41% shorter** — 709 characters across the nine tools down to
  417, longest line from 144 to 61. `upkeep 3/turn by day, 9/turn at night.
  Houses 4 — the herd cannot grow past its housing. Each crew costs a further 3
  power and 2 water per turn.` became `houses 4 · 3/turn by day, 9 at night ·
  3p 2w per capybara`.

---

## V2.5.3

### Changed

- **A tile is the same size at every text setting.** `baseCell` was derived from
  whatever room the HUD left over, so any change to the chrome changed the scale
  of the map. It is now measured once against the stage the app would have at
  text size S — the scale variables are briefly set to 1, the stage is read, and
  they are put back — and the map keeps that scale regardless of what the chrome
  is doing.
  - Where the stage is shorter, the map overflows and the view pans rather than
    shrinking. That is what a zoom control is for.
  - FIT now means "back to reference scale, centred" rather than "fit the whole
    map into whatever is left". At the larger sizes the whole colony no longer
    fits on screen at once, by design.
  - The FIT indicator lights on an actual zoom or pan, not merely on the map
    being larger than the stage, which is now the normal state above S.

### Verified

- Against the stage sizes the tools panel reported: cell size is 16.64px at S, M,
  L and AUTO 135% alike, where it previously fell from 16.64 to 15.36. At L, 10.2
  of 11 rows are on screen and the remaining 13px pans.

---

## V2.5.2

### Changed

- **Larger text no longer costs the map much.** Text at 12px and above now grows
  at 30% of the requested rate, while everything at 11px and below takes the full
  increase. The readouts that were hard to read are the 8 and 9px labels — CREW,
  MORALE, `night needs` — and the 15px numbers beside them were never the
  problem. But it is the large text that sets the height of the HUD and the
  status bar, and that height is the map's height, subtracted.
  - 61 rules take the full scale, 18 are damped.
  - The side column stops growing at all. Its rows are large text, so they no
    longer need the width, and the map keeps those pixels.

### Verified

- Against the stage size the tools panel reports (594×181 at 100%): at L the map
  area is 22% larger than V2.5.1 gave, and cell size goes from 13.1px back to
  15.5px. At AUTO 135%, 24% larger.
- The 9px labels still reach 11.9px at L, unchanged. The 15px readouts grow to
  16.4px instead of 19.8px.

---

## V2.5.1

Larger text stopped fitting the screen. It fits now, and the edges have room.

### Fixed

- **The app overflowed sideways at larger text sizes.** The top readout is a row
  of nowrap cells, so at 124% its natural width exceeded the screen and pushed
  the whole layout past both edges, clipping the sol counter on the left and the
  tile detail on the right.
  - The requested size is now treated as a request rather than an instruction.
    After applying it the game measures the readout against the screen and
    shrinks in 4% steps until it fits, floor 0.84. A clipped number is worth less
    than a slightly smaller legible one.
  - The control reports what actually happened: `AUTO · 124% → 118%` when the
    screen forced a reduction, rather than claiming a size it did not get.
  - Re-measured on every layout, so rotating or resizing re-fits.
  - Guarded against running before first layout, when the row has no width and
    every comparison would read as an overflow.
- **The status bar cropped its own text.** Its height scaled with the text, but
  the objective line wraps to more lines at a larger size, so it lost the last
  line. The fixed height is now a minimum.

### Added

- **Safe-area insets.** The app is inset by `env(safe-area-inset-*)` plus a 2px
  gutter, with `viewport-fit=cover` in the viewport meta so those values are
  reported. Nothing sits against the glass edge or under a rounded corner.

### Verified

- Backoff arithmetic: a request of 1.45 on a row that fits at 1.20 settles at
  1.18 in five steps; a request that cannot fit at all stops at the 0.84 floor
  rather than shrinking without bound.

---

## V2.5.1

### Fixed

- **Text scaling could push the layout wider than the screen.** The HUD is one
  row of nowrap cells, and `#clock` was `flex:0 0 auto`, so its intrinsic width
  set a floor for the whole row: at a larger text size the row simply grew past
  the glass and the readout ran off both edges.
  - `#clock` can now shrink and clip like every other cell, and `#top` clips
    rather than growing.
  - **The requested size is a request, not a promise.** After applying a scale
    the game measures the row and steps back 3% at a time until it fits, down to
    1.00. A readout whose left edge is off-screen is worse than a small one.
  - The DISPLAY row reports what was actually applied, with `MAX` when the
    request was cut short, so a setting that silently does less than asked says
    so.
  - Re-fitted on every layout pass, since rotation and the tools panel change
    the room available.
- **The status bar cropped its own text.** Fixed height and a fixed 30px cap on
  the objective line meant a wrapped sentence lost its second line at any size
  above S. The bar now grows with its contents and the cap scales with the text.

### Added

- **A margin at the edges.** The shell sits inside the safe area with a 2px
  gutter, and the viewport meta carries `viewport-fit=cover` so `env()` returns
  real numbers, so nothing runs to the physical edge of the glass.

### Verified

- Clamp convergence at twelve combinations of natural HUD width and requested
  scale: every case that can fit does, in at most a handful of steps.

### Known limit

- If a HUD is wider than the viewport at 1.00 — a very narrow phone in landscape
  — the clamp bottoms out and it still clips. Fixing that needs the HUD to drop
  or stack cells, not smaller text.

---

## V2.5.0

Text size is adjustable, and one achievement turned out to be unearnable.

### Added

- **DISPLAY · Text size**, cycling AUTO / S / M / L.
  - AUTO reads the system setting. iOS does not hand a page its Dynamic Type
    value, but it will render `-apple-system-body` at the size the reader chose,
    so the game measures a hidden probe in that font against the 17px default.
    The row shows the percentage it found. Re-read on window focus, so changing
    it in Settings and coming back takes effect.
  - S, M and L are 1.00, 1.15 and 1.32, for overriding a system setting that
    makes the game unplayable in either direction.
  - All 79 font sizes in the stylesheet now derive from one variable, `--ts`.
  - Fixed-width furniture — the side column, the status bar, the FIT cell —
    grows at 40% of the text's rate through a second variable, `--tsw`. It has to
    grow or labels clip, but growing proportionally would hand a third of the map
    to the panel.
  - The setting is saved with the run.

### Removed

- **SOL SURVIVOR.** A reachability audit found no path to it. At one capybara the
  morale target is 50 + 25 wallow + 10 net − 20 lone = 65, and growth needs 70,
  so the target never clears the gate; the only route is to still be coasting
  down from higher morale for the three consecutive turns growth requires, which
  needs 83.21 at the moment of the loss against a maximum of 85.
  - That 1.79-point window is then closed by the thing that causes the loss.
    All three death causes cut the target on the same turn: brownout to 30,
    thirst to 40, radiation to 55. Radiation is the gentlest and needs three
    turns of exposure first, which has already pulled morale to about 79.
  - The lone-capybara penalty is right and stays. A herd animal alone should be
    in trouble; the achievement was asking for a recovery the model does not
    allow. Eleven remain.
  - `crewLow` removed with it, since nothing else read it.

### Verified

- Zero unscaled font-size rules remain; all 79 route through `--ts`.
- Cost to the map on a 16 Pro in landscape: cell size falls from 21.2px at S to
  20.4px at AUTO's ceiling, so the wallow bather (17px floor) still draws at
  every text size.
- The smallest text in the UI, the 7.5px banner label, reaches 9.9px at L.

---

## V2.4.2

### Changed

- **No dash between an achievement's name and its condition.** Two spaces do the
  separating; the dash was punctuation doing work the layout already did.

---

## V2.4.1

### Changed

- **Achievement rows read as one sentence.** The name sat hard left and the
  condition hard right, so the two halves of a single line ended up as far apart
  as the pane would allow, with a wall of blank between them. Name and condition
  now run together, left aligned, wrapping rather than truncating.
- **Locked rows say `[LOCKED] — condition`** instead of an em dash standing in
  for the hidden name. A row that reads `— · under 20 structures standing` looks
  like a rendering fault; one that says it is locked looks like a target.
- Hairline between rows, and the glyph column keeps its place whether or not the
  row is earned, so the list does not shift as things unlock.

---

## V2.4.0

Twelve achievements, latched, with a banner that gets out of the way.

### Added

- **Achievements.** Twelve, listed under BOARD with the ones still locked shown
  as their condition only, so there is something to aim at rather than a row of
  question marks.

  | id | name | condition |
  |---|---|---|
  | `all_ratings` | THE LONG SURVEY | a night held at every rating |
  | `brutal` | THE DARK SIDE | a night held on a 5-star site |
  | `twice_rated` | SISTER COLONY | two sites at the same rating |
  | `no_losses` | MOISTURIZED | self-sufficient, nobody lost |
  | `no_brownout` | NOSE ABOVE WATER | never blacked out |
  | `salvager` | SECOND HELPING | self-sufficient after stripping |
  | `lean` | SKELETON CREW | under 20 structures standing |
  | `morale_floor` | UNBOTHERED | morale never under 60 |
  | `recovery` | SOL SURVIVOR | down to one, back to eight |
  | `big_herd` | MAXIMUM OCCUPANCY | 40 capybaras at once |
  | `full_wallows` | POOLS OPEN! | three bathing in every wallow |
  | `single_reactor` | TWIN SUNS | a night carried on one reactor |

- **The id is the contract.** It is what goes into storage and, if a Steam build
  ever happens, into the API call — so ids never change while names stay free to
  be rewritten.
- **Latched, not derived.** Earning something is permanent, written into its own
  record under `astrobara.achv` rather than recomputed from the board. The board
  keeps ten rows and rolls the eleventh off, which would otherwise silently
  revoke a trophy that had genuinely been earned.
- **A slide-in banner** in the lower left, above the log and clear of the build
  column. Queued, because reaching self-sufficiency often trips four at once.
- **Per-run tracking**: `crewLow`, `moraleFloor`, `everLost`, `everBrownout`,
  `everStripped`. Each reads state the turn loop already keeps, so an achievement
  cannot disagree with the colony it describes.
- The site tally is a map of seed to rating, so replaying one site can never earn
  SISTER COLONY, and a self-sufficient colony playing on for fifty more turns
  re-awards nothing.

### Verified

- Twenty turns on one 3-star site award nothing; a second, different 3-star site
  awards SISTER COLONY. Replaying earned sites adds nothing.
- Four run shapes against the per-run gates: win-gated awards stay locked before
  self-sufficiency, while the free ones (herd size, recovery, full wallows) fire
  during play.

### Needs play, not code

- `lean` is set at under 20 structures and `big_herd` at 40. Both are guesses.
  The first colony to hold a night will say whether 20 is generous or impossible.

---

## V2.3.4

### Fixed

- **A machine could not be idled while CLEAR was selected.** The tile action
  offered IDLE only when the held tool could *not* be placed there — and CLEAR is
  legal on every building, so it never failed, so the idle branch was never
  reached. Selecting CLEAR once meant no machine could be switched off again for
  the rest of the session, with scrapping as the only offer on every mine,
  processor, wallow and reactor.
  - The two are not alternatives, so the action cell now carries both: IDLE
    first, since switching something off is far commoner than dismantling it,
    and STRIP with its salvage beside it.
  - Every other tool already reached IDLE, because placing a structure on an
    occupied tile errors out and falls through to it. CLEAR was the only tool
    that shadowed it.

### Verified

- All ten tool states against a running machine: only the CLEAR case changes,
  and IDLE is now reachable from every one of them rather than nine of ten.

---

## V2.3.3

### Added

- **A BOARD tab in the tools panel.** The board was reachable only from the
  end-of-run overlay, which meant the only way to read it was to lose a colony.
  It now sits beside SURVEY, IDLE, DISPLAY and RUN, readable at any time. A row
  for the site you are currently on is highlighted, and rows written by an older
  build carry that build's number.
- **COPY AS TEXT.** These builds are loaded as separate files, and whether a host
  shares local storage between two files is not something the game can determine
  about itself. Export is the only thing that survives a host that scopes storage
  per file, so the board offers itself as one block of text.
- The pane says where the rows are kept — `astrobara.board`, separate from the
  save, never cleared by a version bump — so the storage question has an answer
  in the product rather than only in this file.
- With an empty board the pane explains what qualifies: a whole night carried on
  fusion, the same test as the win. Nothing else.

### Verified

- Tabs, panes and the switcher all agree on the same five names.

---

## V2.3.2

### Changed

- **CLEAR costs nothing but the labour.** Charging power for the action that
  recovers resources was the one charge that could close a game out entirely: a
  colony at zero power with no sunlit array had no legal move at all. Labour
  still applies, so stripping remains a turn decision rather than a free action.
- Cost lines read `free` instead of `0p`, and the build hint reads "no power"
  rather than "0 power".

### Verified

- Every build-then-strip cycle is a net loss in every resource, so free
  stripping is not a loop: an array costs 11 power to put up and take down, a
  wallow 9 power and 35 water.
- From zero power with the opening lander standing, stripping both arrays and
  the battery returns 32 power — enough for the 30-power ice mine.

---

## V2.3.1

You can dismantle your way out of a corner.

### Added

- **CLEAR returns half of what a structure cost**, rounded down, in power, water
  and helium alike. Half rather than all, because a colony that can rebuild
  freely never has to live with a decision; half rather than nothing, because a
  site that starves you before you can reach the ice is not a hard site, it is a
  dead one.
  - A wallow holds 70 water and an ice mine costs 8, so stripping the pool is
    always a route back to the ice. That is the corner this rule exists for.
  - The action button states the return before you commit — `STRIP WALLOW ·
    +9p +35w` — rather than leaving you to work it out.
  - Recovered power is capped at the battery bank. Nothing returns more than it
    cost.
  - "Remove" became "strip" throughout, since the verb now has a payout attached.

### Verified

- Salvage table for all seven structures: nothing is a net gain in any resource.
- The reported dead end — 306 power, 0 water, a wallow standing, an ice mine out
  of reach — reopens: stripping the wallow leaves 309 power and 35 water against
  a mine costing 30 and 8.

### Known edge

- CLEAR itself costs 6 power, so a colony at zero power with no array in sunlight
  still cannot strip anything. Water is recoverable; a total power-out is not.

---

## V2.3.0

The herd is in one place or the other, water gets the warning power has, and a
colony that held a night goes on the board.

### Added

- **The board.** A colony that carried a whole night on fusion is recorded with
  its site code, sol reached, peak crew and peak power, and the board appears on
  the overlay when a run ends. The bar is `G.selfSufficient` — the same test as
  the win condition — because surviving a long time on solar is something the
  sun grants you, while a night on fusion is something you built.
  - One row per site. A better run on the same seed replaces the old row instead
    of filling the board with the same colony.
  - Ranked by turns survived, then peak crew, then peak power. Turns come first
    because the night is what this game is about.
  - Recorded on a loss as well as a win: a colony that reached self-sufficiency
    and later died of thirst still held a night.
  - Every row is reproducible. Sites are seeded, so the code is the point of the
    entry — a run on the board can be handed to someone else.
- **Up to three capybaras in a wallow**, two of them behind the first and drawn
  in the recessive tone, from 24px up.
- **Water reports what a night costs**, under the water figure, the same shape
  as the power line, red when the tank will not cover it. Water draw does not
  change when the sun goes — crew drink and wallows evaporate at the same rate —
  but idled mines stop replacing it, so a night costs the full outflow with
  nothing coming back. Also added to the ledger.
- `G.peakPower`, tracked per turn, for the board.

### Fixed

- **A capybara in the wallow is one fewer in the habitat.** Bathers are drawn
  from the same crew the habitats house, so the two tiles can never add up to
  more capybaras than the colony has. Never more than half the herd at once:
  someone is keeping the lights on, and an empty habitat would read as a dead
  one.
- **Depth is drawn with an opaque tone instead of transparency.** Two
  overlapping capybaras at 58% alpha composite twice, so the overlap went darker
  and the seam between them became the most visible edge on the tile. An opaque
  recessive tone cannot produce that seam at any amount of overlap.
- **The back tier sits wider**, .28 and .72 rather than .38 and .70. At the old
  spacing the two behind cleared each other by .008 of a cell, which is a fifth
  of a pixel on a phone.

### Verified

- Crew split across every combination of 1–24 crew, 0–4 wallows and 1–5
  habitats: the herd is always conserved, never more than three bathe per
  wallow, never more than half bathe at once.
- Board: one row per site, correct tie-break order, capped at ten, a worse rerun
  on the same seed rejected and a better one promoted.

---

## V2.2.1

### Changed

- **No mouths on the capybaras, on either sprite.** At the sizes these are drawn
  a mouth is two or three dark pixels below the eye, which reads as a smudge on
  the face rather than as a mouth. Eyes alone carry it.
- The V2.2.0 detail budget line about "eyes and mouth from 18px" now reads eyes
  only. Ears at 22, leaf and floating citrus at 26 are unchanged.

---

## V2.2.0

A wallow in use shows who is using it.

### Added

- **The wallow bather.** A wallow only earns its +25 morale when it sits beside
  a habitat, and that is the single largest term in the morale model — but a
  wallow built out of reach looked identical to one doing its job. When a wallow
  is running and adjacent to a connected habitat, a capybara sits in it wearing a
  citrus on its head. The tile now reports the same test the ledger runs.
  - Drawn front on rather than in profile, which is what makes it read as
    sitting in the water rather than walking past it.
  - Detail by cell size, as everywhere else: citrus from 17px, eyes from 18,
    ears from 22, leaf and a second floating citrus from 26. Below 17px a wallow
    is a blue ellipse and nothing more.
  - The citrus is the whole message at phone scale. Nothing else on the map is
    that orange.
  - The reference is the yuzu bath — capybaras sitting in an onsen with citrus
    floating around them, as at Izu Shaboten Zoo. It is a real tradition and it
    is what a wallow is for. No existing character design was used.

### Fixed

- **The herd was painted front to back.** The spots list runs the front tier
  first, so capybaras standing behind were drawn *over* the ones in front — two
  identical silhouettes at identical weight, overlapping the wrong way round,
  which reads as one animal. Now sorted by depth and painted farthest first.
- **The back tier is dimmed to 58%.** Depth, not detail, is what separates two
  silhouettes that are the same shape.

### Verified

- Paint order: back tier first at both the four-capybara and two-capybara
  layouts, front tier at full strength.
- The bather stays inside the foundation plate and never exceeds the pool at
  every cell size from 17px to 110px.

### Not done

- The rounded sprite was declined; the herd keeps its existing silhouette.

---

## V2.1.6

### Removed

- **The "NASA-STYLE VISUAL SYSTEM" line on the splash.** It claimed an
  association the game does not have, and the splash already says what this is.

---

## V2.1.5

### Changed

- **The view diagnostics moved from the ledger to Tools · Display.** The ledger
  is the turn's arithmetic, and how the map happens to be drawn is not part of
  the turn — it was the only block there that said nothing about the colony. It
  now sits under the display options, with the toggles and the reset it belongs
  with. It refreshes from `layout()`, so the numbers stay live while the panel is
  open and the map is being pinched.

---

## V2.1.4

One FIT, in the bar, in the bar's own colour.

### Changed

- **The floating chip is gone.** It sat over the bottom-right of the map, which
  is playable ground, and it was the element that kept vanishing under the tools
  panel in the first place. The status bar cell replaces it entirely.
- **FIT is bone, like the toolbar**, rather than amber. Amber is the game's
  colour for sunlight and for things that need attention; a view control is
  neither. It still dims when the whole colony is already in view and comes to
  full strength when it is not — same colour, different weight.

### Verified

- No orphan references to the removed element remain. `#fsbtn` keeps its own
  rule, which it previously shared with the chip.

---

## V2.1.3

FIT moves to the status bar.

### Changed

- **FIT is now a cell in the bottom status bar**, between the objective line and
  the tap-a-tile panel, rather than the fifth arrow. The arrow row is a
  directional control and a jump-to-fit sitting in it read as a fifth direction.
  It stays dim while the whole colony is already in view and lights up when it
  is not, so it reports the state of the view rather than nagging about it.
- The arrow row is back to four columns.
- The floating chip on the map stays. It is useful when it works; it is simply
  no longer the only way out.

### Verified

- The status bar keeps 453px for the objective line on the narrowest landscape
  viewport (iPhone SE), 660px on a 16 Pro.

---

## V2.1.2

The way out of a zoomed view stops being something that can go missing.

### Fixed

- **FIT moved out of the map corner and into the panel.** A chip floating over
  the stage is reachable only if nothing covers it and the stage is exactly as
  tall as it believes; neither has held up across iOS standalone, rotation and
  third-party file viewers. FIT is now the fifth cell of the arrow row, laid out
  by the same grid as END TURN. It cannot be occluded, clipped or scrolled away.
  The floating chip stays as well — it is useful when it works.
- **The arrow keys keep the selection on screen.** They moved the cursor without
  moving the view, so at zoom the selection walked off the edge and the arrows
  appeared to do nothing. `keepSelInView()` pans the minimum distance to bring
  the selected tile back inside the stage, and is a no-op at zoom 1.

### Added

- **The ledger reports the view.** Zoom, whether panning is enabled, cell against
  base cell, and stage size against map size. The zoom failure is intermittent
  and a screenshot of a black rectangle carries no information; these three lines
  make the next report diagnosable in one look, the way the version watermark
  did for builds.

### Changed

- **Strata got their grain back.** V2.1.1 cut micro-variation to .03, which is
  about one and a half levels of red — tiles inside a band came out identical
  and a zoomed view read as a flat wash with no tile edges at all. Now .05,
  still far under the .165 band step, so depth continues to win.

### Verified

- Every corner selection is brought into view at zoom 1, 2, 3 and 5, and pan is
  untouched at zoom 1.

---

## V2.1.1

Depth reads as depth, and the herd is the brightest thing on a habitat.

### Changed

- **Regolith is banded strata rather than a per-row fade.** Depth now steps
  every two rows, with a faint seam at each boundary, so the column reads as
  geology you could point at.
- **The palette had no room in it.** `regolithDeep` was `#2A2622`, which left
  32 levels of red between the surface and the crater floor — no gradient can be
  distinct inside that. It is now `#191614`.
- **Micro-variation no longer outweighs depth.** The noise term spanned .13
  while one row of depth was worth .048, nearly three rows of noise, so a
  shallow tile could sit darker than one well beneath it. Variation is now .03
  against a band step of .165, and depth always wins.
- **Tunnels moved out of the way of the new deep rock.** Open ground went from
  `#11151b` to `#1B2430` — cooler and lighter, ten points of luminance clear of
  the deepest regolith. Rock is warm, a tunnel is not. This matters precisely
  where the ice is and the digging happens.
- **Lit tunnels follow the same rule as everything else.** They warmed on
  `G.selfSufficient`, a flag that needs twelve consecutive dark turns; they now
  warm when a reactor is actually running, like the structure glow.

### Fixed

- **The habitat arch was competing with its own occupants.** A live arch is now
  drawn at 30% as a recessive shell behind the herd. An unpowered one keeps the
  full alarm colour, because a dead habitat has to shout.
- **The herd is back to two staggered tiers.** V2.1.0 put four capybaras in one
  row .19 apart while each was .26 wide, so they fused into a single animal with
  eight legs. Body scale is .30 rather than the old .35, which is what it takes
  to leave clear air once the heads are counted.

### Verified

- Band boundaries never invert across the noise range: a deeper tile is never
  lighter than a shallower one.
- Deepest rock and tunnel separated by 10.5 luminance and opposite in hue.
- Closest same-tier capybara gap is positive with heads included.

---

## V2.1.0

The visual language settles. One vocabulary for the toolbar and the map, no
letters in it, and light on the surface now means something specific.

### Changed

- **The map speaks the toolbar's language.** Drawn silhouettes were a second
  vocabulary that existed only on the map: a player learned `H` in the build
  menu and a cylinder with portholes on the ground, and had to hold both. They
  also blurred at the cell sizes a whole crater rim is played at. Every
  structure now draws the same glyph the toolbar shows.
- **No glyph is alphanumeric.** `B`, `H` and `R` were mnemonics for English
  words — battery, habitat, refinery — and read as noise in any other language.
  The set is now nine shapes:

  | | | |
  |---|---|---|
  | `▒` DIG | `×` CLEAR | `◫` ARRAY |
  | `▮` BATTERY | `∩` HABITAT | `≋` ICE MINE |
  | `▤` PROCESSOR | `~` WALLOW | `*` FUSION |

  `◫` is the two-panel wing reduced. `∩` is the pressure vessel in section.
  `▤` shares a family with `▒` and `▮` so the set reads as one hand. `≋` and
  `~` are deliberate siblings: the mine is buried ice and the wallow is standing
  water, and both are why this colony survives.
- **Two exceptions kept.** The wallow keeps its basin — a pool of standing water
  reads as itself at any size and no glyph carries *somewhere to wallow*. The
  herd keeps its capybaras, now in one row along the floor of the tile so they
  stand under the habitat arch rather than through it.
- **`Larger glyphs` does something now.** The toggle has been in the display
  options since V2.0.2 and was wired to nothing. It scales the map glyph from
  .58 to .74 of a cell.

### Fixed

- **Light on the surface meant almost nothing.** Arrays glowed whenever the sun
  hit them, which is backwards — a lit array is *receiving* light, not casting
  it — and every other structure glowed only after `G.selfSufficient`, which
  needs twelve consecutive dark turns carried by fusion and so arrives long
  after the reactor is built.
  - A glow now means fusion is running and this structure is one of the loads it
    is carrying: the reactor, habitats, mines and processors. Arrays, batteries
    and wallows draw no power and never glow.
  - Daylight produces no glow at all. Nothing on this surface makes its own
    light.
  - Because the check is on the live building, an idled processor goes dark the
    turn you shed it. The lit tiles at night are exactly the ones spending your
    helium-3.

### Verified

- Glyph set audited from the source: nine entries, all distinct, none
  alphanumeric, codepoints U+2592 U+00D7 U+25EB U+25AE U+2229 U+224B U+25A4
  U+007E U+002A.
- Glow eligibility audited: FUSION, HAB, MINE and PROC can glow; SOLAR, BATTERY
  and WALLOW never do, in any light.
- No simulation, cost, site-generation, turn-resolution or persistence code was
  touched. This release is presentation only.

### Worth watching

- `≋` U+224B and `◫` U+25EB are the two least common codepoints in the set. They
  render in the system mono stack on iOS and macOS; if a device falls back to
  tofu, `≈` and `=` are the safe substitutions.
- The habitat arch is drawn at .42 of the cell and the herd at .70. At small
  `cell` on a crowded hab the two may crowd; if so, drop the arch to .38.

---

## V2.0.4

Two escapes: one from a view you could get stuck in, one from a line that
described the terrain wrongly.

### Fixed

- **A zoomed map could leave you with no way back to the colony.** The FIT chip
  was the only exit, and it was hidden two ways at once. It only appeared when
  `zoom > 1.02`, and it sat at `z-index: 16` — beneath the tools panel, which
  docks in the same bottom-right corner. Worse, if `baseCell` is ever computed
  from a bad stage measurement (rotation, a standalone relaunch, a mid-layout
  resize), the map overflows the stage while `zoom` still reads 1: no chip, no
  panning, and pinching out clamps at a zoom you are already on.
  - `fitView()` now re-measures the stage and rebuilds `baseCell` rather than
    trusting the last measurement.
  - `layout()` tracks whether the drawn map is larger than the stage, and the
    chip shows on that, not on zoom alone.
  - Three further ways out: the chip, now labelled **FIT** and stacked above the
    tools panel; **DISPLAY · Reset map view**; and a double tap on the map,
    which only fits when there is something to escape from.
- **Panning was gated on zoom** rather than on whether the map actually
  overflowed, which made the stuck state immovable as well as inescapable.
- **A pinch that dropped to one finger left the gesture stuck**, swallowing the
  taps and drags that followed.

### Changed

- **The crest line follows the tiles.** Built from one point per column and
  joined left edge to left edge, it drew a diagonal across tiles that are not
  surface tiles — lit ground above the line, shadowed ground below, on the same
  tile. Now stepped: one horizontal cap per column, a vertical face at each
  height change, run out to the far edge of the last column.
- **The warm crest is rim light, so it only falls where the sun does.** Each
  column is tested with the same `litAt()` the tile highlight and the power
  model use. Shadowed ground keeps a dim neutral edge so the basin still reads
  as terrain.

---
