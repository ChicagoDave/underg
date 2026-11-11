# Issues in the original — the O-register

Defects, typos, and oddities in UNDERGROUND V1 as written in 1979. The port
**reproduces** these (plan.md, "Governing principle — reproduce the story as
coded"), so this register exists to record that each one was seen and carried
over deliberately, not missed.

This is not the repo's issue store. The DevArch store holds **D-n** items —
problems with *this* project's tooling and process, things we intend to fix.
An **O-n** item is a property of the 1979 program, and the default disposition
is REPRODUCE. A future reader who notices the leash cannot be picked up should
find it here and stop, rather than "fixing" it.

## Dispositions

| Value | Meaning |
|---|---|
| REPRODUCE | Carried into the port exactly as the original behaves |
| RESTORED-UPSTREAM | Corrected in the recovered source before this repo received it; the port inherits the correction. Recorded so the divergence from the 14-Mar-79 listing stays visible |
| BLOCKED | Chord 3.6.0 cannot express it; the deviation ledger carries the entry and names the missing construct |
| CORRECTED | The port does what the line evidently meant, by owner ruling for that item. The oracle still does what the line says, so the two differ here on purpose |

Nothing is ever dispositioned CORRECTED without an explicit owner ruling that
overrides the governing principle for that item. David's rulings of 2026-11-10 cover O-8, O-9 and
O-10 ("let's infer the correct actions for the bugs"), then O-1 and O-11
("yes those two as well"), then O-12 ("yes").

---

## O-1 — `LEASH` addresses the rat; the leash has no word

**Disposition: CORRECTED** (2026-11-10; was REPRODUCE by the ruling of 2026-09-14) · `UNDERG.BAS` 1780, 1790 · found 2026-09-14

```
1780 IFA$="LEASH"THENT%=31%:GOTO1980
1790 IFA$="RAT"THENT%=31%:GOTO1980
```

Both words resolve to object 31. By the inventory ordering at line 1244, object
16 is "Cat's leash" and object 31 is "Dead rat" — so `LEASH` addresses the rat,
and object 16 cannot be named at all. The leash reaches the player only as part
of object 32, "Cat on leash".

Chord expresses this natively: give the rat an `aka leash`. No ledger entry
needed.

Ruling of 2026-11-10 (David, asked whether the correction should reach this
item: "yes those two as well"). Inferred intent: line 1780 should read
`T%=16%`. In the port `LEASH` names the cat's leash and only `RAT` names the
rat. The oracle still answers `TAKE LEASH` in the rat's room with "Don't be
stupid."; the port has no leash there to take.

Line 2140, which would make the cat need its leash, is the leash's only use
and cannot be reached in the source. That is O-12.

---

## O-2 — line 975 absent from the 14-Mar-79 listing

**Disposition: RESTORED-UPSTREAM** · `UNDERG.BAS` 20, 30, 975 · upstream finding

Line 20 arms `ON ERROR GOTO 30` to probe for a free `UNDER<letter>.DAT` and the
14-Mar-79 listing never disarms it, so any later error is caught by line 30,
fails its `erl-20%` test, and prints "Password not found." A failing `CHAIN` at
line 990 is therefore reported as a bogus password error.

The 01-Mar-79 listing carries `975 ON ERROR GOTO 0` in exactly that slot, and
the reconstruction restored it. The vendored source has it (verified at
`original/UNDERG.BAS` line 97). The oracle and the port read the same file, so
parity holds either way; the bug has no Chord analogue regardless, there being
no `CHAIN` to fail.

## O-3 — transcription bug at line 2000

**Disposition: RESTORED-UPSTREAM** · `UNDERG.BAS` 2000 · upstream finding

Recorded in `original/README-port.md`: with the bug present, `W` from inside
the building answered `?Statement not found` instead of "You can't move in that
direction." Corrected during reconstruction. Noted here so the difference from
the raw scan is not mistaken for a porting error.

## O-4 — misspellings in the game's own text

**Disposition: REPRODUCE** · multiple · found 2026-09-14

The port carries these letter for letter. They are the author's text.

| Spelling | Where |
|---|---|
| `enterance` (for entrance), 4 occurrences | `LOOK.BAS` 450, 2400, 2450, 5300, 5650 |
| `Minuature sun` (for miniature) | `UNDERG.BAS` 1245; also `LOOK.BAS` 10200 |
| `The ice is to slippery` (for too) | `UNDERG.BAS` 2040 |
| `all of it's treasures ... it's secrets` (for its) | `UNDERG.BAS` 3144 |

Any transcription tooling that normalises spelling is wrong for this project.

## O-5 — sentences run together without a space after the period

**Disposition: REPRODUCE** · `LOOK.BAS`, many rooms · found 2026-09-14

Room text frequently reads `...one-room building.Stairs lead down.` and
`You are in the forest.To the west is...`. This is in the source, not an
artifact of extraction — `extracted/world.json` preserves it and the oracle
prints it. Chord prose blocks carry it unchanged.

## O-6 — inconsistent capitalisation of the opening word

**Disposition: REPRODUCE** · `LOOK.BAS`, many rooms · found 2026-09-14

Some room descriptions begin lower case (`you are on a path which winds north`,
room 8 — the game's own start room) and others upper (`You are in the forest`,
room 5). The `README-port.md` verification notes call this out as expected
behaviour rather than a scanning artifact: the RSTS console shouted in capitals,
but the program's text is mixed case and is what a modern client renders.

## O-7 — room 85 has no description of its own

**Disposition: REPRODUCE** · `LOOK.BAS` 8500, 8550 · found 2026-09-14

```
8500 !
8550 goto10000
```

Every other room's line prints text and then jumps to 10000, the object sweep.
Room 85's long line is a bare `!` that falls through to a short line which
jumps straight to the sweep, printing nothing. So entering room 85 shows only
what is standing in it — and object 0, "There is something extremely valuable
here!", is what the map puts there.

Whether Gary meant the room to be wordless or the line was lost before the
scan, the program as written prints nothing, so the port prints nothing. In
Chord the room gets an empty description rather than an invented one.

This one bit during extraction: following `goto10000` as if it were a
delegation gave room 85 the object table's first line, which reads plausibly
enough to pass unnoticed. `tests/test_extract_world.py` now asserts no room
carries that string.

---

## O-8 — `FILL` where there is water ends the program

**Disposition: CORRECTED** · `UNDERG.BAS` 2560 · found 2026-11-10

```
2560 X%(19%)=-1%:goto2170
```

`X%` is dimensioned to 11 (13 in `LOOK.BAS`). Subscript 19 is an error, the
trap at line 1005 sends it to 3200, and the program ends without printing
anything. Seen in the oracle: at the lake shore, `FILL` produces no output and
no later command is answered. The line is transcribed, not reconstructed.

Inferred intent: `O%(19%)=-1%`, one letter away. Object 19 is the water and
-1 means carried, so FILL at the lake (room 9) or the bog (room 20) puts the
water back in hand and says "Done." The port does that and nothing more: it
does not add a check that the bottle is held, because the line has none.

## O-9 — `JUMP` in an ordinary room fires the laser and ends the program

**Disposition: CORRECTED** · `UNDERG.BAS` 2860 · found 2026-11-10

```
2850 IFX%(0%)=10%or ... then&"A A A A a a a a a . . .                    <splat>":GOTO3050
2860 goto2450
```

Away from the eight high places, line 2860 jumps to 2450, the middle of the
SHOOT handler, with no target. Seen in the oracle: "The laser beam strikes
it's target and disintegrates it." and then nothing more.

Inferred intent: `goto2540`, the same four digits with two swapped. Line 2540
is "Nothing happens." The port says that.

## O-10 — `READ WATER` prints a coin's legend

**Disposition: CORRECTED** · `UNDERG.BAS` 2610 · found 2026-11-10

```
2610 ifT%=19%then&"In god we trust":&"Liberty":&"1979":&:goto1000
```

Object 19 is the water; "In god we trust / Liberty / 1979" is what is written
on a penny, object 30. Seen in the oracle: `READ WATER` prints the legend and
`READ PENNY` prints "There is nothing written on it."

Inferred intent: `T%=30%`. In the port `READ PENNY` prints the legend and
`READ WATER` prints "There is nothing written on it."

## O-11 — the rat's bite cannot happen

**Disposition: CORRECTED** · `UNDERG.BAS` 2010 · found 2026-11-10

```
2010 IFX%(11%)-30%ANDO%(31%)-X%(0%)THEN&"As you walk away, the rat bites you and you die.":GOTO3050
```

`X%(11%)` is 30 while the rat is hungry, so the left side is zero and the
whole test is false exactly when the rat could bite. Seen in the oracle: you
walk into the hungry rat's room (46) and out again unharmed. Once the rat is
dead the two subtractions are ANDed bit by bit, which is no test of anything.

Inferred intent: `=` for each `-`, "the rat is hungry and the rat is here".
In the port, leaving room 46 by either of its exits while the hungry rat is
there prints the line and kills you. Feed it the cheese first.

## O-12 — the cat never needs its leash

**Disposition: CORRECTED** · `UNDERG.BAS` 2110 to 2150 · found 2026-11-10

```
2110 ift%<>24%andt%<>2%then2130elseifo%(26%)+1%then&"You can't touch that with bare hands.":goto1000
2120 IFO%(25%)+1%THEN2150
2130 GOTO2160
2140 IFT%-32%ORO%(16%)=-1%THEN2160
2150 &"You have nothing in which to carry that.":GOTO1000
```

Line 2140 says: take the thing unless it is the cat and the leash is not
carried. Nothing reaches it. Every thing but the sun and the uranium goes
from 2110 to 2130, and 2130 jumps over 2140 to the take at 2160. So the cat
is picked up bare-handed and the leash does nothing in the game.

Ruling of 2026-11-10 (David, asked whether the cat should require the leash as
the unreachable line intended: "yes"). Inferred intent: line 2110 should read
`then2140`. In the port, TAKE CAT without the leash in hand gets line 2150's
"You have nothing in which to carry that."; with it, the cat is taken.

Not yet compared with the oracle or played in the port: reaching a fed cat
takes the cheese, the rat, the sun and the ice first. The oracle side of the
claim is from the listing.

---

## How to add an entry

One heading per issue, numbered in discovery order. State the disposition, the
source lines, and the date. Quote the source where the defect is not obvious
from a description. If the disposition is BLOCKED, name the Chord construct
that is missing, and cross-reference the deviation-ledger entry in
`underg.story` once Phase 5 creates it.
