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
("yes those two as well"), then O-12 ("yes"), then O-13 ("again - infer the
correct response"), then O-15 ("B": correct room 51's exits in the port only,
from the paper).

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

**The other half, found 2026-11-10 (session b5d946), played in the oracle.**
"No test of anything" understated it. Once the rat is dead `X%(11%)-30%` is 1
(2 once the cat has eaten), and `1 AND (O%(31%)-X%(0%))` is true whenever the
rat's room number and yours differ by an odd number. With the rat dead in room
46 you may step into room 45 or 47 and are bitten on the way out of either;
carried, it bites on the way out of every even-numbered room, 46 included; and
after the death it lies in the building or the chasm and bites again from the
basement or the building. **Nothing after the rat's death can be played in
this listing as the oracle runs it**: not the cat, the vault, the golden key,
the door it opens, or the 381 points the road to the ending asks for (sixteen
treasures at 25 make 400; without the key, 375). The existing CORRECTED ruling
already gives the port its behaviour (only a hungry rat bites), so the port
plays through; what changes is verification. `PastTheRat` in
`tests/test_verbs_against_oracle.py` plays the port alone and holds each reply
to the listing line that prints it, and
`test_after_the_rat_dies_the_original_kills_you` shows both halves.

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

Played in the port 2026-11-10 (session b5d946, `PastTheRat`): a fed cat with
no leash in hand is refused with line 2150's words, and taken once the leash
is carried. The oracle side stays a reading of the listing, because a fed cat
cannot be reached in the oracle at all (O-11, the other half).

---

## O-13 — after the ice or the woman stops you, the next command loses its noun

**Disposition: CORRECTED** · `UNDERG.BAS` 1001, 2000, 2040, 2060 · found 2026-11-10

```
1001 INPUTLINE#1%,A$:...X%=INSTR(X%,A$," "):LSETA$(0%)=LEFT(A$,X%-1%):...
2000 X%=M%(X%(0%),Y%):IFX%<=0%THEN2870
2040 ifO%(40%)=x%(0%)then&"The ice is to slippery for you to move on.":goto1000
```

Line 1001 looks for the first space starting at whatever `X%` was left
holding. Lines 2040 and 2060 go back for input with `X%` still the number of
the room you tried to enter, so the search starts past the end of the next
line typed: the first word comes out empty and the verb lands where the noun
belongs. Seen in the oracle: in the Alaska room, N ("The ice is to
slippery..."), then DROP SUN answers "What?" and the sun stays in hand. A
second DROP SUN works, and a one-word command is unharmed.

The same thing happens after line 992's "I can't see a thing.", which also
returns for input with `X%` holding a room number: in the dark room (77), TAKE
PEARL typed straight after walking in answers "What?" (seen in the oracle).

Ruling of 2026-11-10 (David, asked whether the port should reproduce it:
"again - infer the correct response"). Inferred intent: the search for the
first space starts at the start of the line. In the port the command after a
refused move is read whole, and DROP SUN straight after the ice's refusal
drops the sun and melts the ice. Both halves are in `CorrectedSlips`
(`test_the_command_after_the_ice_keeps_its_noun`). No other oracle walk in
the tests types a two-word command straight after either refusal, and
Phases 6 and 7 must not generate one.

## O-14 — a bottle emptied by POUR is full again once dropped

**Disposition: REPRODUCE** · `UNDERG.BAS` 2240 · found 2026-11-10

```
2240 O%(T%)=X%(0%):O%(37%-T%)=X%(0%)ifT%=18%ORT%=19%:...
```

Dropping the bottle sets the water down with it whether or not the water was
being carried. POUR sends the water to room 0; DROP BOTTL brings it back, and
TAKE BOTTL then picks up both. "There is an empty bottle here." (LOOK.BAS
10180) can therefore hardly ever be seen. Carried over as coded and compared
(`SHORT_WALKS`, "the bottle is full again once dropped"). It makes the
corrected FILL (O-8) one of two ways to get the water back.

## O-15 — nothing leads back from the well

**Disposition: CORRECTED** (in the port only; `UNDERG.BAS` is left as transcribed) · `UNDERG.BAS` 510, 520 · found 2026-11-10

```
507 DATA51,,,,49,,,,,,,51,51,51
510 DATA52,52,,,,,,,,,,,,
520 DATA,,51,,,,,,,,,51,,
```

Room 51 ("you are in a short passage running E/W.") has two exits, north and
east, and both go to the well (52). The well leads only back to 51. All
fourteen directions were tried from each room in the oracle. So whoever walks
north through the dwarf's door can never return: the rare coins that the penny
buys at the well cannot be carried out, and a death there leaves any treasure
in hand behind (line 3051).

With the coins out of reach the most that can lie in the building is fifteen
treasures, 375 points, and the road to the ending wants more than 380 (line
3090). Together with O-11's other half this means this listing, as the oracle
runs it, cannot be won. The port carries the map as coded, so today it cannot
be won either.

That is a statement about the 14-Mar-79 printout as transcribed, not about the
game. David, 2026-11-10: "I 100% remember winning the game in high school",
and "I remember the well being a puzzle" (it is one here: the coal for the
dwarf, the penny for the well, the coins). The listing is one dated revision
among several (`original/README-reconstruction.md`), and its DATA block was
checked for count and range, not value by value against the scan.

**Ruling of 2026-11-10: check the paper first.** Offered a correction, David
chose to have line 510 read off the scans before ruling. To read: line 510
(and 507, 520) on `07192605` p1-2, with the second copies of the DATA block on
`07192603` and `07192606`; and, for O-11, line 2010 on `07192605` and on the
verb-handler sheets `07192600` to `07192602`. The scans are not in this
repository and were not found on this machine (searched by sheet name,
session b5d946). Until they are read the port keeps the listing's exits.

The room's own text suggests line 510 was meant to send east to the well and
west back to the door (`DATA,52,50`), where it sends north and east to the
well.

**The paper, read 2026-11-10 (session b5d946).** The scans are in
`gschmidl/interactive-fiction` on GitHub, under `Unfinished or Lost/Underground
(Scans)/reconstruction/V1`. Line 510 is not Gary's slip; it is a slip in the
transcription.

- `07192605` p1 (the 14-Mar-79 listing): line 510 is the last line on the page
  and the sheet break cuts it in half. The top half that survives begins
  `510DATA,5` - a leading comma, which the transcribed `510 DATA52,52,,,` does
  not have.
- `07192603` p2 (another listing pass) has the line whole and clear:
  `510DATA,50,52,,,,,,,,,50,,`. North nothing, east to the dwarf's door (50),
  west to the well (52), OUT to the door.

So on paper room 51 has its way back, and the coins can be carried out.

**Ruling of 2026-11-10 (David, offered a fix to the source, a fix in the port
only, or re-basing on `07192603`: "B").** The port takes room 51's exits from
the paper: east and OUT to the dwarf's door, west to the well, nothing north.
`original/UNDERG.BAS`, the oracle and `extracted/world.json` keep the
transcribed line, so here the oracle and the port differ on purpose, like the
other CORRECTED items, and Phases 6 and 7 must not generate oracle cards that
walk past room 51. In the code: `story/dwarf-city.chord` (room 51),
`CORRECTED_EXITS` in `scripts/world_parity.py`, and
`test_the_way_back_from_the_well` in `CorrectedSlips`, which shows both
halves. Sheet `07192603` is evidence for the corrections, not the port's
base.

**Sheet `07192603` is a different revision, and it already has four of the
corrections this register inferred.** Read off pages 3 and 5:

| Line | `07192603` | 14-Mar-79 as transcribed | Register |
|---|---|---|---|
| 2010 | `IFX%(11%)=30%ANDO%(31%)=X%(0%)THEN` | `-` for each `=` | O-11, as inferred |
| 1780 | `"LEASH"THENT%=16%` | `T%=31%` | O-1, as inferred |
| 2110 | `then2140` (and no line 2130) | `then2130`, `2130 GOTO2160` | O-12, as inferred |
| 1001 | `X%=INSTR(1%,A$," ")` | `INSTR(X%,...)` | O-13, as inferred |

It also differs where nothing was inferred (line 70 starts the lamp counter at
-50; line 180 sends OUT of the light room to 18, not 27; line 1960 goes to
1000; line 1270's arithmetic), so it is not simply the same listing. Its
header is torn off and its date is not known; the fixes suggest it is the
later one. Not checked: every other line of either sheet.

---

## How to add an entry

One heading per issue, numbered in discovery order. State the disposition, the
source lines, and the date. Quote the source where the defect is not obvious
from a description. If the disposition is BLOCKED, name the Chord construct
that is missing, and cross-reference the deviation-ledger entry in
`underg.story` once Phase 5 creates it.
