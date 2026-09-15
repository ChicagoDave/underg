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

Nothing is ever dispositioned FIX without an explicit owner ruling that
overrides the governing principle for that item.

---

## O-1 — `LEASH` addresses the rat; the leash has no word

**Disposition: REPRODUCE** · `UNDERG.BAS` 1780, 1790 · found 2026-09-14

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

## How to add an entry

One heading per issue, numbered in discovery order. State the disposition, the
source lines, and the date. Quote the source where the defect is not obvious
from a description. If the disposition is BLOCKED, name the Chord construct
that is missing, and cross-reference the deviation-ledger entry in
`underg.story` once Phase 5 creates it.
