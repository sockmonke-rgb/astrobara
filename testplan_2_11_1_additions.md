TESTPLAN.md — additions for V2.11.1
Plan version 1.6. Apply as shown; nothing existing is removed.

────────────────────────────────────────────────────────────────────────
1. Header line

  **Plan version 1.5** · 20 September 2026 · covers Astrobara V2.11.0
→ **Plan version 1.6** · 21 September 2026 · covers Astrobara V2.11.1

────────────────────────────────────────────────────────────────────────
2. Tier 1 — view and text · new check

Add after the frame-rate block, under a new heading:

### Reading the ground

- **V23** — dig a shaft from the surface to the bottom of the map beside
  untouched rock. At every depth, open ground is obviously lighter than the
  rock next to it, in daylight and in the dark, with and without a reactor
  running. Check it on the phone in daylight, not on a monitor: the two old
  tones were 0.4 and 0.1 luma from the rock they sat against, which a monitor
  in a dim room will still let you tell apart. Guards V2.11.1.

────────────────────────────────────────────────────────────────────────
3. Tier 2 — model and loop · new checks

Add to *The ledger tells the truth*, after M5:

- **M4b** — go into a night with the bank covering it: the POWER `night` line
  is not red, and morale does **not** fall across the dark. Then spend the bank
  down mid-night until the line goes red: morale falls from that turn. Morale is
  paid for being able to hold the night, not for a positive net on the turn.
  Guards V2.11.1, where every dark turn cost 10 morale whatever the bank held.
- **M4c** — the ledger's `power secure` row agrees with the POWER `night` line:
  `yes` exactly when the bank covers the figure that line names. They are the
  same test, and if they ever disagree one of them is lying.
- **M5b** — with a crew of seven or more and one served wallow, the ledger
  reads `wallow cover · 1 of 2 served`. Build a second wallow beside a habitat:
  it reads `2 of 2` and morale climbs. Idle one: it drops back. One served
  wallow per six capybaras is full marks.
- **M5c** — a colony with a pool per six capybaras and a bank that covers the
  dark reaches morale 100, and the ledger's work multiplier reads 1.50×.

────────────────────────────────────────────────────────────────────────
4. Tier 3 — achievements · notes on two runs

- **UNBOTHERED** (morale never under 60) needs a served wallow standing on
  turn zero. A fresh colony's arrays are in shadow and its bank cannot hold a
  night, so the target is 50 on turn one and morale lands at 59.75 without one.
  Dig a tile beside the habitat and build the wallow before ending turn zero.
- **POOLS OPEN** wants three bathing in every wallow. Bathers are half the herd,
  three to a pool, so every pool is full only at a crew that divides by six.
  The wallow bonus wants one pool per six capybaras, which is the same
  configuration — but at crew 40, FULL CAPYCITY's threshold, full morale wants
  seven pools and POOLS OPEN allows six. Take POOLS OPEN as the herd passes
  through a multiple of six.

────────────────────────────────────────────────────────────────────────
5. Revision history · new row

| 1.6 | 21 Sep 2026 | V2.11.1 | V23 for tunnel contrast at depth. M4b and M4c
for morale paid on the night bank rather than the turn's net; M5b and M5c for
wallow coverage and the 100 ceiling. Tier 3 notes on the turn-zero wallow
UNBOTHERED now needs, and where POOLS OPEN and the wallow bonus part company.
Model change: Tier 2 in full, and the Tier 3 runs that turn on morale. |
