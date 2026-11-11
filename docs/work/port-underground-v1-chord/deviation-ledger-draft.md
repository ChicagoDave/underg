# Deviation ledger: running draft

Started in Phase 3 (2026-11-10), against Chord 4.0.1 on `@sharpee/devkit`
5.6.0. Phase 5 turns this into the ledger in the `underg.story` header.

Under the governing principle in `plan.md`, an entry here is one thing only: a
place where the port's output or world differs from the 1979 program because
Chord cannot say what the original does, or because a later phase has not said
it yet. Defects of the original that the port carries over are not here; they
are in `original-issues.md`.

"Spiked" means built and played in `spikes/world-shape/`. "Seen in play" means
seen in `sharpee play story`.

## Deviations Chord imposes

**L-1. Every room prints its heading and its description on every entry.**
The original prints the long text on a first entry and on LOOK, and only the
short name afterwards. Sharpee has no brief mode, by decision. One entry for
all 87 rooms. Reasoning in `mapping.md`, "Not a gap".

**L-2. Spaces at the start and end of a printed line are dropped.** The
original indents the two signs (room 54's `"You must have at least 380
points…"` by eight and eleven spaces, room 57's vault inscription by eight)
and ends one line of room 39 with a space. Chord trims every prose line.
Doubled spaces inside a line survive (rooms 25 to 27). Line breaks survive
through `{br}`. Spiked.

**L-3. An object's "There is … here" line joins the room's paragraph.** The
original prints each on a line of its own after the room text. Chord's
`phrase present:` feeds the description's own paragraph, joined by a space, and
a `{br}` at the start of the line is stripped. Spiked.

**L-4. A carryable object is announced twice.** After the original's own line
("There is a rock here.") the platform adds its contents list ("You can see a
rock here."). No construct was found that removes the list for a thing that is
still takeable: `scenery` removes it and also fixes the thing in place, and
`override message looking-contents-list` with `nothing` prints the word
"nothing". Spiked and seen in play. Fixtures (objects 33 to 45) are `scenery`
and are announced once.

**L-5. A thing has one presence line.** Seven objects print a different line
by state in the original (8 silver, 17 lamp, 18 bottle, 31 rat, 32 cat, 33
woman, 34 vault). A second `phrase present` block on one thing is
`analysis.duplicate-phrase`, even when the two carry different `while` gates.
Each of the seven has the line it shows when the game starts; the other line
is named in a comment on its block and is Phase 4's to deliver, by whatever
route Phase 4 finds. Spiked.

## Deviations Chord imposes on the verbs (Phase 4, 2026-11-10)

"Compared" means the same commands were played through the oracle and the port
by `tests/test_verbs_against_oracle.py` or by hand with `scripts/oracle_run.py`
and `scripts/story_run.py`.

**L-6. The parser's own two refusals are the platform's.** A word the 1979
program does not know gets "I don't know what that means."; a noun that is
neither here nor carried gets "It isn't here." The port prints "I don't
understand that." and "You can't see any such thing.", which are parser
texts outside the overridable message catalog. A line the parser rejects is
also not a turn, where line 1010 counts every input line. Compared.

**L-7. Nothing is asked.** The original asks "Do you want to continue?" after
a death, "Are you sure?" on QUIT and "Do you want the lamp?" from the woman.
Chord has no question a story can put to the player. After a death the port
goes on as if the answer were yes; the lamp offer is not made.

**L-8. SCORE says less.** The first line matches the original number for
number (compared). The second line's tail, "for the next rating you need N
more points", is arithmetic on the score and is left off; the class letter is
printed.

**L-9. LIGHT and OFF do not print the room again.** The original jumps to
line 980 after both. A body cannot ask for the room to be described.

**L-10. The safe's combination is typed `two-seven-three`.** A grammar
pattern cannot hold `2-7-3` (`parse.action-pattern`).

**L-11. A reply of several lines is several paragraphs.** Each `phrase` a
body speaks is its own paragraph, so INVEN's lines and SCORE's two lines have
blank lines between them.

**L-12. The noun comes second.** G1: `LAMP LIGHT` is not understood.

## Findings for the `sharpee` ratchet log (Phase 4)

Each was hit while authoring and is worked around in `story/verbs.chord`,
where a comment says how.

- An action's `must` and `refuse` lines are all tried before its body,
  whatever order they are written in; the analyzer accepts a `refuse` after a
  `change` in an action body and it then does not behave as written.
- `the item is a <story trait>` compiles and is always false.
- A room has one exit per direction even when each carries its own `while`
  (`analysis.duplicate-exit`); the same for two passages sharing a command.
- A name ending in a number cannot be the subject of a condition
  (`the Room 85 is entered`), and a name holding `can` ends at that word.
- The story header takes only `on every turn` clauses, and an entity's `on`
  clause may not change anything and then refuse, so "leaving this room is
  fatal while the Gnome is here" has no clause form.
- `kill the player` and `is deadly` end the game; nothing in Chord revives.
- A counter prints in a phrase only as `the player's <counter>`, each passed
  by its own `with`.
- An entity's `phrase taking-taken:` does not replace the stock message.

## Phase 4: done and not done

Done and compared against the oracle: TAKE (with its order of refusals, the
bottle and water pair, the worn things), DROP, INVEN, LIGHT and OFF, darkness
by line 980's rule, SHOOT with and without a target at the robot, POUR in the
mine, the death at the robot and waking in the basement, the 25 points of a
treasure in the building, and the default reply of every verb.

Also compared: the elevator and its lever both ways, the rock and the Gnome,
READ MESSAGE, the safe and its combination, the silver.

Corrected by owner ruling, so the port and the oracle differ on purpose (O-1
and O-8 to O-12 in `original-issues.md`): LEASH, FILL where there is water,
JUMP in an ordinary room, READ WATER and READ PENNY, the rat's bite.

Written from the listing but not yet compared: the cat needing its leash (O-12, not yet played in the port either), THROW's special cases, FEED,
the drop cases (cat and rat, dog and bone, dwarf and coal, the vault, the
well, the cheese, the sun on the ice, room 85), OPEN with the key, RUB, PUSH
(the spaceship, the cart, the lever), JUMP, the safe, the two fatal exits,
the guardians (Gnome, dog, dwarf, ice), room 58 sealing behind you, the
ending at room 87.

Not written:
- The two computed exits (G3, G4).
- The lamp running down past the warning: the woman's offer, the recharge.
- The one-in-three fatal accident of line 992 when a dark room is described.
- Object 0 in the decode (it is authored in `treasures.chord`, by hand).
- The second presence line of the seven stateful objects (L-5).
- "What about it?" for a noun typed alone.

## Not deviations, but worth knowing

- **Presence lines are gated on not being held.** A `phrase present:` line
  shows whenever its thing is anywhere in the player's room, including in the
  player's hands. The original prints the line only for a thing lying in the
  room, so every carryable's block reads `phrase present while not the player
  holds …`. With the gate the output matches. Spiked.
- **A refused DOOR or BARRIER names its own room.** A `passage` block must
  name a destination even when it only refuses. Rooms 2, 19 and 37 have such a
  passage, and each names itself. It is never taken, so nothing shows.
- **Room 85 has no heading and no description** (O-7, reproduced). The
  compiler warns `analysis.room-no-description`; that warning is expected.

## Still open from Phase 3

- **Words.** Each thing answers to the original's words and to the whole word
  each five-letter stub stands for (`plati` and `platinum`). The entity names
  also answer, which admits words the original does not have.
- **The water** (object 19) starts in room 1 beside the bottle, as the data
  has it, and so is listed as "a water".
- **Fixtures and creatures** are all `a thing, scenery`; none is `a person`.
  The verbs written so far did not need them to be.
- **Room 85's heading** has still not been looked at in play.
