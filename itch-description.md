**A colony of capybaras on the rim of Shackleton crater. No rivals, no combat. The antagonist is the lunar night.**

*Version 14*

A lunar day is 29 turns. Fourteen of them are dark.

When the sun goes down your solar arrays make nothing, habitat heating triples, and the colony runs on whatever you banked. Every structure you add raises the load you have to carry through the next darkness. The colony grows until it can no longer afford itself.

Doing nothing kills you on turn 19, during the first night. A disciplined run reaches self-sufficiency around turn 58.

## Two resources, scarce in opposite ways

**Water ice** sits deep, in ground the sun never reaches. Finding it is a map puzzle. It feeds drinking water, life support and radiation shielding — and the best of it lies where there is no sun to run the extraction.

**Helium-3** is solar-wind implanted, richest in the top few metres where the sun does reach. Finding it is not the problem; throughput is, and throughput is gated by the power you already have. You spend energy to get energy, and it can stall out.

You cannot dig toward both at once.

## The geography does the work

The map is hand-authored rather than generated, because the shadow geometry has to be exact. Shackleton sits at the pole, so the sun never climbs more than 14° above the horizon. That single fact produces the whole map.

One stretch of crest is lit on all fifteen daylight turns — a peak of eternal light. The basin beside it is lit on none of them — a floor of permanent shadow. They are adjacent.

Your arrays want the crest. Your ice is in the dark right next to it. That is the real reason to go to the lunar pole, and it fell out of the shadow calculation rather than being designed in.

The lander sets down badly, with its arrays in shadow. Moving them is your first real decision.

## Playing

Tap a tile, pick a tool, then commit from the bar along the bottom. Tiles are small on a phone, so an arrow pad walks the selection one tile at a time instead of making you tap precisely.

Nine tools: dig, clear, solar array, battery, habitat, ice mine, processor, wallow, fusion reactor. Selecting one shows both its build cost and its per-turn upkeep — different numbers, and the distinction decides runs.

- **Everything must connect to a habitat by dug tunnel.** Orphaned structures go dead.
- **Habitats need three rows of regolith overhead.** Dig above one and the cover is gone, and the crew starts taking a dose. CLEAR backfills a tunnel to put it back.
- **Idle your machines before the dark.** Processors are your heaviest load at 22 power a turn each. Choosing what to carry through the night is the decision the whole game is built around.
- **Wallows are not decoration.** Capybaras are semi-aquatic and social. Standing water they can sit in is an extravagant use of your scarcest resource — and without one, morale tops out at 60, under the 70 the herd needs to grow.

## Controls

Landscape, phone or desktop. The game rotates itself, so it works with rotation lock switched on.

- **Tap** a tile to select it, then commit from the bottom bar
- **Arrow pad** nudges the selection one tile at a time
- **Pinch** to zoom; the corner bracket returns to the whole colony
- **Drag** the tools panel wherever suits you

On desktop: number keys pick tools, arrow keys nudge, Enter builds, Space ends the turn.

## Instruments

- **Ledger** — every generation and consumption line for the current turn, plus what the coming night will cost and whether your storage covers it.
- **Log** — every event, turn-stamped and filed under a snapshot of the numbers that produced it. "Why did I lose someone on sol 2" is answerable after the fact.
- **Survey** — shades every tile by ore grade, cyan for ice and amber for helium-3. Fog still applies: unsurveyed ground reads as unknown, not as barren.
- **Display options** — high-contrast ore, larger glyphs, grid lines on or off.

## Winning, losing, and afterwards

Carry one whole night on fusion and the colony is self-sufficient. The reward is visible on the map: from then on the tunnels light themselves, and the night stops being dark.

You can keep playing after that. If the colony dies instead, you can review the run — the map stays open, the log stays readable, and the end card diagnoses the failure: first brownout and when, peak power ever banked, turns spent running a deficit.

## Scope

A vertical slice, and some of what is missing is missing on purpose.

- **Autosaves every turn.** Close the tab, background the app, come back later — the run is where you left it.
- **Turn-based**, one turn to one lunar day.
- **One map**, one landing site.
- **No opponents.** Removing the fourth X is the decision the rest of it hangs on.

## Under the hood

One HTML file. No dependencies, no build step, no server, no analytics, no fonts, no CDN. It makes no network requests and stores nothing in your browser.

Source: [github.com/sockmonke-rgb/astrobara](https://github.com/sockmonke-rgb/astrobara) — MIT licensed.

Built by Mark Florentino LLC and Kittenmancer.
