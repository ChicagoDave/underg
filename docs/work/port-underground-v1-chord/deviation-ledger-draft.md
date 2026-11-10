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
  What the platform prints as the heading of a room with no `room name` has
  not been looked at in play, because nothing leads to room 85 yet.

## Left for Phase 4, recorded so it is not mistaken for done

- **The two computed exits** (room 54 southeast, room 60 west; G4 and G3) are
  not authored. A comment marks each in `ancient-city.chord`.
- **Exits that change during play** (G2): the elevator, room 33, has no exits
  declared; room 58's sealing is not authored. The "door is closed" exits
  (rooms 2 and 19) are blocked unconditionally.
- **Darkness** (line 980) is not authored. No room is `dark`.
- **Words.** Each thing answers to the original's words and to the whole word
  each five-letter stub stands for (`plati` and `platinum`). The entity names
  also answer, which admits words the original does not have. The one that
  matters is the cat's leash: O-1 says LEASH must reach the rat and nothing
  else, and the leash's own name now competes for it.
- **Carried names.** INVEN prints "Platinum wire." in the original and
  "a platinum wire" here. Each carried name is in a comment on its block.
- **The water** (object 19) starts in room 1 beside the bottle, as the data
  has it, and so is listed as "a water". It belongs with POUR and FILL.
- **Fixtures and creatures** are all `a thing, scenery`. The woman, the dwarf,
  the Gnome, the dog, the rat and the cat are not `a person`; the verbs that
  act on them will decide.
