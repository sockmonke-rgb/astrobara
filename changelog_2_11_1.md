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
