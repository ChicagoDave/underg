# Deviation ledger: running draft

Started in Phase 3 (2026-11-10), against Chord 4.0.1 on `@sharpee/devkit`
5.6.0. Since Phase 5 (2026-11-10) the ledger is the header of
`story/underg.story`, one short entry per L number; this file keeps the longer
note behind each number and what was spiked or compared. A new deviation gets
a number in both, and `tests/test_story_assembly.py` fails when the two lists
differ.

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
- `the item is scenery` in a `refuse` compiles and is never true, so every
  fixture could be picked up until each was named.
- `lose` does not stop the body: lines after it still speak.
- A `refuse` is tried before a `must`, so "you aren't carrying it" has to be
  written into each later refusal's condition.
- A grammar line with a slot does not match the bare verb, and `refuse without
  item` never fires for it; the bare verb needs an action of its own.
- A comment inside a `define action` block is a parse error.
- `win` does not stop the body either; the ending was spoken twice.
- `refuse when not …` is refused by the analyzer and `<thing> must be here` is
  not a form; "it is not here" needs a named condition.
- A grammar line of two plain words (`take pearl`) is taken ahead of the
  slotted pattern, which is what L-16 and L-17 rest on.

## Phase 4: done and not done

Done and compared against the oracle (every one a walk in
`tests/test_verbs_against_oracle.py`): TAKE with its order of refusals, the
bottle and water pair, the worn things and the thirteen fixtures ("Don't be
stupid."); DROP and THROW with their special cases (the sun on the ice, the
bone and the dog, the coal and the dwarf, the cheese with the cat and with the
rat, room 85, the emerald, the rock at the Gnome, the
robot, the dog and the dwarf); FEED; KILL; SHOOT with and without a target;
RUB; PUSH (lever, cart, the remote-control box, the computer shot first); OPEN
in each room that answers; READ; EAT and DRINK; POUR and FILL; LIGHT and OFF;
JUMP where it kills; every verb with no noun and a noun with no verb; INVEN
and SCORE; darkness by line 980's rule; the guardians (robot, Gnome, dog,
dwarf, ice); the spaceship, the planet and its two deaths; the vault's way
into room 58, room 58 sealing behind you, the volcano; the road out of the
City below 381 points; the death and waking in the basement, and the third death ending the game; the 25 points of
a treasure in the building; the second presence lines of the lamp, the silver
and the rat.

Corrected by owner ruling, so the port and the oracle differ on purpose (O-1
and O-8 to O-12 in `original-issues.md`): LEASH, FILL where there is water,
JUMP in an ordinary room, READ WATER and READ PENNY, the rat's bite, the cat
and its leash, (O-13) the command typed after the ice stops you, and (O-15)
the short passage's exits, which is what lets the coins out of the well.

Played in the port alone, each reply held to its line of the listing, because
the original cannot be played past the rat's death (O-11, the other half): the
cat eating the rat, the cat needing its leash, the cat opening the vault, the
golden key, the door in room 19, "The vault is open.", "there is a hungry cat
here.".

Played start to end in the port (`StartToEnd` in
`tests/test_verbs_against_oracle.py`): sixteen treasures carried to the
building in three trips for 400 points, the road out of the City above 380
points, the wall shot through in room 86, the woman asking for the laser in
room 87, and the ending, spoken once and held to lines 3140 to 3144. The walk
is 272 commands and none is refused. It cannot be played in the oracle (O-11,
O-15).

Written from the listing and neither compared nor played: the woman as a
target (THROW ROCK, KILL, SHOOT, PUSH) and "You are somehow paralyzed by the
woman."

**L-13. The penny in the well says nothing.** Line 2990 prints the room again
(where the coins now lie). A body cannot ask for the room to be described
(L-9), so DROP PENNY at the well prints nothing; LOOK shows the coins.

**L-14. The second presence lines come out of a carried thing.** A thing has
one presence line (L-5), so the other line of the lamp, the bottle, the
silver, the rat, the cat and the vault each belongs to a thing the player
always carries and never sees, gated on the state. The lines print in the
original's order in every walk compared.

**L-15. A noun the player cannot see is not "What about it?".** A noun typed
alone gets line 1980's reply when the thing is in the room or in hand;
otherwise the platform's "You can't see any such thing." (L-6), where the
original says "What about it?" for any word it knows.

**L-16. What cannot be seen cannot be named.** In a dark room the platform's
parser answers "You can't see any such thing." for a thing lying there, where
the original takes it. Room 77 is dark whatever is carried and holds the
pearl, so TAKE PEARL has its own words in that room and is compared with the
oracle. Nothing else is given this treatment: a thing dropped in a dark room
stays there until there is light.

**L-17. ME is spelled out.** ME is the original's one word for object 0. The
platform reads "me" as the player, so TAKE, GET, CARRY, WEAR, DROP, THROW,
TOSS and GIVE with ME, and ME alone, are their own actions with the original's
refusals. Compared. FEED, KILL, SHOOT, RUB, READ, EAT and PUSH with ME are
not.

**L-18. BARRE and BARRIER.** The original's word is BARRE; both are taken.

**L-19. Room 85 prints "Nameless Room".** The original prints nothing at all
in room 85 (O-7). A room with no `room name:` block shows the name it was
created under, so the port prints that one line on entry and on LOOK. Seen in
play, Phase 5 (the square room, E, LOOK), against the oracle's silence for the
same commands. An empty `room name:` block was not tried.

**L-20. The words a thing answers to.** The original reads the first five
letters of a noun (G5) and so takes any word beginning with them. Each thing
here answers to the original's stubs and to the whole word each stands for
(`plati` and `platinum`), not to every word with that beginning. The names the
things were created under also answer, which admits words the original does
not have.

Not written:
- The random exit west of room 60 (G3): nothing reads whether a room has been
  visited.
- The lamp running down past the warning: the woman's offer, the recharge
  (L-7).
- The one-in-three fatal accident of line 992 when a dark room is described.
  `one chance in 3` exists as a condition, but nothing fires when a room is
  described, only on every turn.
- Object 0 in the decode (it is authored in `treasures.chord`, by hand).

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

- **Words.** Now L-20.
- **The water** (object 19) starts in room 1 beside the bottle, as the data
  has it, and so is listed as "a water". Part of L-4.
- **Fixtures and creatures** are all `a thing, scenery`; none is `a person`.
  The verbs written so far did not need them to be.
- **Room 85's heading.** Looked at in Phase 5; now L-19.
