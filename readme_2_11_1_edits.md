README.md — edits for V2.11.1
Five replacements. Nothing else in the file changes.

────────────────────────────────────────────────────────────────────────
1. Version line

  **V2.11.0** · MIT · Mark Florentino LLC and Kittenmancer
→ **V2.11.1** · MIT · Mark Florentino LLC and Kittenmancer

────────────────────────────────────────────────────────────────────────
2. The glyph table, WALLOW row

  | `~` | WALLOW | 18 power, 70 water, 1 labour | 4 water/turn, no power · +25 morale beside a habitat |
→ | `~` | WALLOW | 18 power, 70 water, 1 labour | 4 water/turn, no power · +25 morale beside a habitat, more as the herd gets pools of its own |

────────────────────────────────────────────────────────────────────────
3. The morale paragraph, under *Everything is deterministic*

OLD:

  Morale, for instance, is a target computed fresh each turn from a base of 50:
  a wallow beside a habitat is +25, positive power net +10, load shedding −12, a
  brownout −35, running dry −25, a habitat under thin cover −10, and being down to
  one capybara −20, because herd animals do badly alone. Morale then closes 35% of
  the gap to that target each turn. It never snaps, it chases — which is why it
  appears to drift when nothing obvious has changed.

  Morale is not cosmetic: `work = 0.5 + morale/100` scales extraction, so a shed
  turn costs you output for several turns afterwards.

NEW:

  Morale, for instance, is a target computed fresh each turn from a base of 50:
  a wallow beside a habitat is +25, with up to 15 more as the rest of the herd
  gets pools of its own — one served wallow per six capybaras is full marks — and
  a bank that covers the rest of the dark is +10. Against that, load shedding
  −12, a brownout −35, running dry −25, a habitat under thin cover −10, and being
  down to one capybara −20, because herd animals do badly alone. Everything at
  once is 100. Morale then closes 35% of the gap to that target each turn. It
  never snaps, it chases — which is why it appears to drift when nothing obvious
  has changed.

  The +10 is paid for being able to **hold** the night, not for a positive net on
  the turn. A colony spending a bank it deliberately filled is the plan working,
  and the figure it is judged against is the one already on screen under POWER —
  `night N`, the same test the sundown line runs. Actually running out still
  costs what it cost.

  Morale is not cosmetic: `work = 0.5 + morale/100` scales extraction, from 0.5×
  at nothing to 1.5× at 100, so a shed turn costs you output for several turns
  afterwards.

────────────────────────────────────────────────────────────────────────
4. The ledger line, under *Playing*

  - The **ledger** (tap the day counter) lists the turn's power and water flows,
    what the night will cost, and how many structures are standing.
→ - The **ledger** (tap the day counter) lists the turn's power and water flows,
    what the night will cost, how many structures are standing, and why morale
    is where it is — wallow cover, and whether the bank is secure for the night.

────────────────────────────────────────────────────────────────────────
5. The preflight example

      python3 preflight.py astrobara-v2_11_0.html SEEDS.txt
→     python3 preflight.py astrobara-v2_11_1.html SEEDS.txt
