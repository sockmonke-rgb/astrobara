# Astrobara

A 3X lunar survival colony builder. One HTML file, no dependencies, no network, no build step.

You are running a colony of capybaras on the rim of Shackleton crater. There are no rivals and no combat. The antagonist is the lunar night.

**[Play it](https://sockmonke-rgb.github.io/astrobara/)** — landscape, phone or desktop.

---

## The premise

A lunar day is 29 turns. Fourteen of them are dark.

When the sun goes down your solar arrays make nothing, habitat heating triples, and the colony runs on whatever you banked. Every structure you add raises the load you have to carry through the next darkness. The colony grows until it can no longer afford itself.

Doing nothing kills you on turn 19, during the first night. A disciplined run reaches self-sufficiency around turn 58.

## The two resources

They are scarce in opposite ways, and they pull you in opposite directions.

| | Water ice | Helium-3 |
|---|---|---|
| **Where** | Deep, in ground the sun never reaches | The top few metres, where the sun does reach |
| **Verb** | Prospect — finding it is a map puzzle | Process — throughput gated by the power you already have |
| **Feeds** | Drinking, life support, radiation shielding | Fusion, once you can bank 25 of it |
| **Trap** | The best ice sits where there is no sun to run the extraction | You spend energy to get energy, and it can stall out |

You cannot dig toward both at once.

## Geography

The map is hand-authored rather than generated, because the shadow geometry has to be exact. Shackleton sits at the pole, so the sun never rises more than 14° above the horizon. That single fact produces the whole map:

- **Columns 13–16** are lit on all fifteen daylight turns — a peak of eternal light.
- **Columns 4–11** are lit on none of them — a floor of permanent shadow.

They are adjacent. Your arrays want the crest; your ice is in the dark right beside it. This is the real reason to go to the lunar pole, and it fell out of the shadow maths rather than being designed in.

The lander sets down badly, with its arrays in shadow. Moving them is your first real decision.

## Playing

Tap a tile to select it, pick a tool, then commit with the button in the bottom bar. Tiles are small on a phone, so the arrow pad walks the selection one tile at a time rather than making you tap precisely.

**Nine tools.** Dig, clear, solar array, battery, habitat, ice mine, processor, wallow, fusion reactor. Selecting one expands it to show both its build cost and its per-turn upkeep — those are different numbers and the distinction decides runs.

**Everything must connect to a habitat by dug tunnel.** Orphaned structures go dead.

**Habitats need three rows of regolith overhead.** Dig above one and its cover is gone, and the crew starts taking a dose. `CLEAR` backfills a tunnel to put the cover back.

**Idle your machines before the dark.** Processors are your heaviest load at 22 power a turn each. Deciding what to carry through the night is the decision the whole game is built around. `IDLE ALL` does the lot in one tap. There is an automatic safety net underneath: if a turn would drive power below zero, industry goes dark on its own before anyone gets hurt.

**Wallows are not decoration.** Capybaras are semi-aquatic and social. Standing water they can sit in is an extravagant use of your scarcest resource, and without one morale tops out at 60 — under the 70 the herd needs to grow.

### Instruments

- **The ledger** — tap the day counter. Every generation and consumption line for the current turn, plus what the coming night will cost and whether your storage can cover it.
- **The log** — the same panel, second tab. Every event, turn-stamped and filed under a snapshot of the numbers that produced it. "Why did I lose someone on sol 2" is answerable after the fact.
- **Survey mode** — shades every tile by ore grade, cyan for ice and amber for helium-3, intensity by concentration. Fog still applies: unsurveyed ground reads as unknown, not as barren.
- **Display options** — high-contrast ore, larger glyphs, grid lines on or off.

### Winning, losing, and afterwards

Carry one whole night on fusion and the colony is self-sufficient. The reward is visible on the map: from then on the tunnels light themselves, and the night stops being dark.

You can keep playing after that. If the colony dies instead, you can review the run — the map stays open, the log stays readable, and the end card diagnoses the failure: first brownout and when, peak power ever banked, turns spent running a deficit.

## Running it

Open `astrobara.html`. That is the whole thing.

No server, no build, no package manager, no analytics, no fonts, no CDN. It makes no network requests and stores nothing in your browser. Deploying is copying one file.

## Scope

This is a vertical slice, and some of what is missing is missing on purpose.

- **No saving.** A run is a sitting.
- **Turn-based**, one turn to one lunar day.
- **One map**, one landing site.
- **No opponents.** Removing the fourth X was the design decision the rest of it hangs on.

All tuning lives in a single `CFG` object at the top of the file.

## Credits

Built by **Mark Florentino LLC** and **Kittenmancer**.

Released under the [MIT License](LICENSE).
