# UNDERGROUND V1 → Chord: the mapping

**Phase 2 deliverable.** Produced 2026-09-14 against the vendored 14-Mar-79
source in `original/`, Chord language 3.6.0, Sharpee 5.4.1. Method follows
`sharpee/docs/work/chord/dungeo-conversion.md`: sort every unit of the original
into what converts declaratively today, what needs a `define action`, what needs
a TypeScript hatch, and what has no target at all — so the gap list is
enumerable rather than open-ended.

Nothing here is authored yet. This document is the input to Phases 3 and 4.

## What the decode produced

`scripts/extract_world.py` reads both 1979 sources and writes
`extracted/world.json`; `tests/test_extract_world.py` holds it to the original
(8 tests, green). Every expected value in those tests is anchored either in the
source or in the oracle transcript, never in the extractor's own output.

| Table | Size | Where it lives in the original |
|---|---|---|
| Rooms | 87 | `M%(1..87, 1..14)`, read by `MAT READ` at line 70 |
| Exits | 231 real, 31 refusal-coded | the same matrix; columns are directions |
| Objects | 45 | `O%(1..45)`, the tail of the same DATA stream |
| Room text | 87 long + 87 short | `LOOK.BAS` lines `room*100` and `room*100+50` |

The fourteen columns are the fourteen movement words of lines 1020–1150, in
order: north, east, west, south, northeast, northwest, southeast, southwest,
up, down, in, out, **door**, **barrier**. The last two are pseudo-directions —
the player types them as nouns and the parser routes them like compass moves.
Column 0 is the room-seen flag, not an exit, which is why line 70 zeroes it
separately.

## Exit semantics

A non-positive value is not a room. Line 2870 dispatches it:
`ON 1%-X% goto 2880,2890,2900,2905,2910,2920,2930,2940,2950,2960,3090`. All ten
negative codes are reachable in this map.

| Code | Uses | Kind | Chord target |
|---|---|---|---|
| 0 | — | refuse | absence of an exit; stdlib's own refusal |
| −1 | 8 | refuse | `<dir> is blocked: <phrase>` |
| −2 | 8 | refuse | same |
| −3 | 3 | refuse | same |
| −4 | 4 | refuse | same |
| −5 | 2 | refuse | same |
| −6 | 1 | **deadly** | deadly exit (cyanide atmosphere) |
| −7 | 2 | refuse | `<dir> is blocked:` — but see G2, it is also written at run time |
| −8 | 1 | **deadly** | deadly exit (volcano) |
| −9 | 1 | **special** | no declarative target — see G3 |
| −10 | 1 | **special** | no declarative target — see G4 |

Twenty-nine of the thirty-one are ordinary blocked exits or deadly exits, both of
which Chord expresses directly. Two are computed destinations and have no
declarative form.

## Verbs

Fifteen verbs, `V%=1..15`, each with its synonym list. Not "~20" as the plan
estimated — the count came down once the noun table was separated out.

| `V%` | Words | Chord target | Note |
|---|---|---|---|
| 1 | GET, TAKE, CARRY, **WEAR** | stdlib `taking` | WEAR is a synonym for TAKE here, not `wearing`. Deviation D-4. |
| 2 | DROP | stdlib `dropping` | clean |
| 3 | THROW, TOSS, **GIVE** | stdlib `throwing` | GIVE is a synonym for THROW. Deviation D-5. |
| 4 | DRINK, **EAT** | stdlib `drinking` | one action for both. Deviation D-6. |
| 5 | OPEN, **UNLOC** | stdlib `opening` | one action for both. Deviation D-7. |
| 6 | KILL, HIT, FIGHT, ATTAC | stdlib `attacking` | clean |
| 7 | SHOOT, FIRE | `define action` | no stdlib equivalent |
| 8 | RUB | `define action` | `touching` exists but is not the same verb |
| 9 | POUR | `define action` | no stdlib equivalent |
| 10 | FILL | `define action` | no stdlib equivalent |
| 11 | READ | stdlib `reading` | clean |
| 12 | FEED | `define action` | no stdlib equivalent |
| 13 | LIGHT, ON | stdlib `switching_on` | clean |
| 14 | EXTIN, OFF | stdlib `switching_off` | clean |
| 15 | PUSH, PRESS, **PULL** | stdlib `pushing` | PULL is a synonym for PUSH. Deviation D-8. |

**Eight map to stdlib as aliases. Five need `define action`. Two of those five
(POUR, FILL) are a pair that share the bottle's state and should be authored
together.** Nothing in the verb layer needs a TypeScript hatch.

The five conflations marked Deviation are the interesting half. The original
gives one action two English names that Sharpee's stdlib treats as distinct
actions with distinct refusals. Under the reproduce-as-coded principle these
are settled: alias each pair the way the original does, so `WEAR LAMP` behaves
as it did in 1979, at the cost of `wearing`, `giving`, `eating`, `unlocking`
and `pulling` never firing. Each gets a ledger entry recording the stdlib
action the port gives up; none needs a language change.

## Meta commands

Outside the `V%`/`T%` tables entirely, handled inline before the verb sweep.

| Words | Chord target |
|---|---|
| N/E/W/S/NE/NW/SE/SW/U/D/IN/OUT/DOOR/BARRE and long forms | stdlib `going` (DOOR and BARRIER need custom direction vocabulary) |
| LOOK | stdlib `looking` |
| QUIT | stdlib `quitting` |
| SCORE | stdlib `scoring` — but the original's rating prose is its own (line 1270–1271) |
| INVEN | stdlib `inventory` |
| JUMP, LEAP, HOP, DIVE | `define action` |
| `2-7-3` | `define action` — the Gnomes' safe combination, a bare literal command |
| FUCK, SHIT, HELL, DAMN | `define action` or phrases — each has its own authored reply |

## Objects

Forty-five, addressed by `T%=1..45`, plus `T%=0` for ME. `O%(n)` holds a room
number; `-1` means carried. Line 3051–3052 shows the split the original itself
draws: objects 0–15 are treasures (they drop where you died), 16–32 are
carryables (they return to room 1), 33–45 are fixtures and creatures.

Four objects are stateful rather than static, and these are the first candidates
for Chord `states:` pairs rather than prose:

| Object | State | Read from |
|---|---|---|
| 17 lamp | lit / unlit | `X%(5)` |
| 18 bottle | full / empty | whether `O%(19)` is co-located |
| 31 rat | hungry / dead | `X%(11) = 30` |
| 32 cat | hungry / fed | `X%(11) = 31` |

## Gaps — things with no declarative target

The enumerable list. None of these blocks Phase 3.

**All of them are already decided**, by the governing principle recorded in
`plan.md`: the port reproduces the story as coded. So the open question on each
gap below is never *whether* to reproduce it — only *how*, and whether Chord
3.6.0 can. A gap that Chord cannot express becomes a deviation-ledger entry
naming the missing construct, and a candidate ratchet-log item in `sharpee`.
Defects in the original that the port carries over are registered separately, in
`original-issues.md`.

**G1 — the parser is positionally symmetric.** Line 1001 builds a 6-character
verb field and a 5-character noun field with `LSET`, then line 1015 loops
`for x%=0% to 1%` comparing *both* fields against *every* vocabulary word. So
`LAMP LIGHT` parses identically to `LIGHT LAMP`. Chord's grammar shapes are
positional. Either accept the deviation or author reversed patterns for every
verb.

**G2 — the map mutates at run time.** Line 2070: entering room 33 rewrites
`M%(33,4)` to wherever you came from, so that room's south exit leads back to
the room you entered from; and leaving room 58 writes `−7` into the exit you
just used, sealing it behind you. Chord's exits are declarations. This is the
same "dynamic exits" gap the Dungeo assessment logged.

**G3 — a random-destination exit.** Code −9, line 2960: draw a random room
1–85, retry until it is one the player has already visited, then go there.
Chord 3.6.0 has `move <entity> to a random adjacent room` (ADR-326), which is a
different predicate — adjacency, not visitedness.

**G4 — a score-gated exit.** Code −10, line 3090: above 380 points the exit
leads to room 86; below it, the woman ends the game.

**G5 — five-character noun truncation.** `PLATI` matches PLATINUM, and equally
matches any word beginning PLATI. Reproducing the original's over-acceptance
faithfully means authoring prefixes, not words.

**G6 — death is a loop, not an ending.** Line 3050–3054: you are asked whether
to continue, your treasures scatter to where you died, your carryables return
to room 1, you lose 10 points and restart in room 2 — and the third death ends
the game with an insult. ADR-347 made endings an explicit concept in Chord;
this is a resurrection cycle *with* an ending attached at the third iteration.

**G7 — the lamp timer drives an interruption.** Lines 1010 and 3175–3195: at 250
turns of lamp use you get a warning; at 297 a woman appears and offers to
recharge the lamp for 50 points, teleporting you to the lamp if you are not
holding it; at 300 the lamp dies, and if you are in room 87 the game ends
instead.

**G8 — a vocabulary collision in the original. RESOLVED: reproduce it.**
Line 1780 maps LEASH to `T%=31` and line 1790 maps RAT to `T%=31`. The leash is
object 16 by the inventory ordering at line 1244, so `LEASH` addresses the rat
and the leash has no word of its own. Owner's direction 2026-09-14 is to
reproduce the story as coded, so the port carries the collision: `LEASH` and
`RAT` both resolve to the rat, and the leash is takeable only as part of the
cat (object 32, "Cat on leash"). No ledger entry is needed — Chord can express
this natively with `aka`. Registered as **O-1** in `original-issues.md`.

**G9 — CLOSED 2026-11-10 by Chord 4.0.1's `room name:` block (see the re-read
below). Was BLOCKING: Chord cannot give two rooms the same printed name.**
`analysis.duplicate-entity` refuses a second `create` of an existing name
(verified: `spikes/duplicate-names/`), and Chord has no construct separating an
entity's identifier from the name it prints — the grammar has no `printed name`,
`called`, or equivalent. But **27 of the original's 87 rooms share a short name
with another room**:

| Count | Name | Rooms |
|---|---|---|
| 11 | `You are in a maze of twisty little passages, all alike.` | 61-71 |
| 5 | `Dead end.` | 72-76 |
| 3 | `Mine` | 25-27 |
| 2 | `Forest.` | 6, 7 |
| 2 | `E/W tunnel` | 21, 22 |
| 2 | `You are in a passage with only one exit.` | 59, 60 |
| 2 | `Closet` | 80, 81 |

The short name is what the original prints on re-entering a seen room (line 990's
`room*100+50`), so this is visible text, not an internal label.

For most of these the deviation would be cosmetic. For the maze it is not: eleven
rooms that announce themselves identically ARE the puzzle. Numbering them
`Maze 61`, `Maze 62`, … solves it for the player by naming the solution, which is
a gameplay change, not a wording change.

This is the first BLOCKED item and it blocks Phase 3 authoring, because the
naming scheme has to be settled before 87 `create` blocks are written. Written up
with the supporting evidence in `chord-gap-g9.md`, for the `sharpee` repo. The
natural fix is a language one — a display-name construct in Chord, which would
be a ratchet-log entry in `sharpee` — and the owner of that language is also the
owner of this port.

## Re-read against Chord 4.0.1 (2026-11-10)

Everything above was written against Chord 3.6.0 (Sharpee 5.4.1). The port now
consumes `@sharpee/devkit` 5.6.0, which carries Chord 4.0.1. This section
records what that changes. Grammar references are to
`sharpee/packages/chord/chord.ebnf` on `main` at `ad4094967`; "spiked" means
built and played here on the published 5.6.0, and anything not spiked says so.

**Closed**

- **G9, same printed name.** Closed by the `room name:` block (ebnf line 1354).
  Spiked: `spikes/room-name/` (three rooms heading `Mine`, a three-room group
  heading the maze line). Detail in `chord-gap-g9.md`.
- **IN and OUT as exits.** The meta-command table above sends IN and OUT to
  `going`, but 3.6.0 had no `in`/`out` exit directions, which this document
  missed. 4.0 added them (sharpee GH #568). Not spiked here.
- **DOOR and BARRIER.** The two pseudo-direction columns have a direct target
  now: a `passage … end passage` block (ebnf line 1419), an exit the player
  takes by typing its command, with its own `while`, `blocked` and `deadly`
  lines. This replaces "custom direction vocabulary" in the meta-command table.
  Not spiked here.
- **JUMP, LEAP, HOP, DIVE.** `jumping` is a stock verb in 4.0 that a room or
  thing answers with a clause, so it no longer needs a `define action`. The
  synonyms still need grammar. Not spiked here.

**New in 4.0 that changes how Phase 3 is written**

- **Room groups and exit tables.** `rooms <stem> <first> to <last>` in a region
  (ebnf line 1368) declares the maze (61 to 71) and the dead ends (72 to 76)
  once each, with their exits in an `exits, one-way` table (line 1397).
  `sharpee/packages/chord/tests/fixtures/maze-sixteen.story` is this game's
  rooms 61 to 76 written that way. A table row cannot carry a blocked or deadly
  exit (`parse.exit-row-blocked`), so refusal-coded exits stay on the room.
- **Every thing names its kind.** `create the Lamp` with no kind noun is
  `analysis.missing-kind-noun`; all 45 objects need `a thing` or another kind.
  Found by `spikes/toolchain-smoke/`, which is migrated and green again (4
  cards passing, 7 assertions passing).
- **Test trees are a directory.** `<id>.tests/` with a `manifest.json` and one
  file per run of cards replaces the single `<id>.tests.json`. Phase 6's card
  generator writes that shape. The old `toolchain-smoke.tests.json` is still
  on disk and is read by nothing.

**Unchanged: still no declarative target**

- **G1, positional symmetry.** Patterns are still positional. Reversed
  patterns per verb remain the route.
- **G2, the map mutates at run time.** `exit` is still `DIRECTION to <name>`
  (ebnf line 1453): a fixed destination. A blocked exit can be conditional
  (`<dir> is blocked while <cond>`, line 940), which may cover room 58's
  sealing; room 33's "south leads back where you came from" has no form.
- **G3, the random visited room.** The only random place is still `a random
  adjacent room` (line 2261), and no condition reads whether a room has been
  visited.
- **G4, the score-gated exit.** No conditional destination. Whether a
  condition can read the score was not checked.
- **G5, five-character truncation.** Unchanged; prefixes through `aka`.
- **G6, the death loop** and **G7, the lamp timer.** Not re-examined beyond
  the grammar: `kill the player`, `define timer` and `when … expires` are all
  present, as they were in 3.6.0.

**Not a gap: the original's short-name-on-revisit is brief mode, which Sharpee
does not have by decision.** The original prints a room's long text on the
first entry and on LOOK, and only its short name on a later entry (line 990).
That is the teletype brief mode. Sharpee prints the heading and the description
on every entry and every LOOK: `verbose` is always true
(`sharpee/packages/stdlib/src/actions/standard/looking/looking-data.ts:143`,
"the teletype-era brief/verbose modes are not a Sharpee feature", David,
2026-10-12; `going.ts:662` the same), and the heading is one authored name
printed wherever a room description is (sharpee ADR-349 D3). So each room is
authored the plain way: the short name (line `room*100+50`) as its `room name`,
the long text (line `room*100`) as its description. The port's output differs
from the original on every first entry (a heading the original does not print)
and every later entry (a description the original does not print); that is one
deviation-ledger entry covering all 87 rooms, decided by the platform, not a
choice this port makes. `spikes/seen-unseen/` tried the other route, the long
text in a `first time` block with no description: a later entry then matches
the original, but LOOK prints only the name and the compiler warns
`analysis.room-no-description` on every room, so it is not the way to write it.
An earlier draft of this section called this G10 and asked for a decision; the
platform had already made it.

## Phase 3 entry state

Rooms, exits, room text, and object placements are decoded and verified.
Phase 3 can author the world from `extracted/world.json` without reading
BASIC. The four stateful objects (17, 18, 31, 32) and the two computed exits
(G3, G4) are the only world-layer items that need a decision first.
