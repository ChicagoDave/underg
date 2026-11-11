## UNDERGROUND V1 (Gary Kleppe, 14-Mar-79, RSTS/E BASIC-PLUS) - Chord port
##
## PURPOSE. The entry file of the port: the story block, the turn counter, the
## lamp timer, the death-and-waking loop, the imports, and the player.
## PUBLIC INTERFACE. `sharpee build story/underg.story` and `sharpee play
## story`; the identity is in `underg.config.json`, which owns the `ifid:`
## line below.
## OWNER CONTEXT. The port as a whole; plan and registers are under
## docs/work/port-underground-v1-chord/.
##
## AUTHORITY. Every line the game prints is Gary Kleppe's 1979 text, carried
## letter for letter with its misspellings and run-together sentences (O-4 to
## O-6), or is the platform's own text where the ledger below says so.
## Nothing is drafted for this port. This is a FAITHFUL PORT, not a retarget:
## the program is reproduced as coded, bugs included, and checked against the
## original running in the bplus interpreter (the oracle).
##
## WHERE THE PORT DEPARTS FROM THE 1979 PROGRAM - the first-pass ledger,
## Phases 3 and 4. An L entry is a place where Chord 4.0.1 cannot say what the
## original does. The longer notes, and what was spiked or compared for each,
## are in deviation-ledger-draft.md under the same numbers.
##
##  What is printed
##   L-1. Every room prints its short name and then its long text on every
##        entry. The original prints the long text on a first entry and on
##        LOOK, and the short name alone afterwards. Sharpee has no brief
##        mode. One entry for all 87 rooms.
##   L-2. Spaces at the start and end of a printed line are dropped: the
##        indents of the two signs (rooms 54 and 57) and one trailing space
##        (room 39). Chord trims every prose line.
##   L-3. An object's "There is ... here" line joins the room's paragraph,
##        where the original prints each on a line of its own.
##   L-4. A carryable thing is announced twice: the original's line, then the
##        platform's list ("You can see a rock here."). Nothing was found
##        that removes the list for a thing that can still be taken. The
##        list is also where the words "a water" come from.
##   L-9. LIGHT and OFF do not print the room again (line 980). A body
##        cannot ask for the room to be described.
##  L-11. A reply of several lines is several paragraphs: INVEN's lines and
##        SCORE's two lines have blank lines between them.
##  L-13. DROP PENNY at the well prints nothing, where line 2990 prints the
##        room again with the coins in it. Same cause as L-9.
##  L-19. Room 85 prints "Nameless Room" and nothing else. The original
##        prints nothing at all there (O-7). A room with no `room name:`
##        shows the name it was created under.
##
##  What is said back
##   L-6. An unknown word gets "I don't understand that." for "I don't know
##        what that means."; a noun not here gets "You can't see any such
##        thing." for "It isn't here." Both are parser texts outside the
##        message catalog. A line the parser rejects is also not a turn,
##        where line 1010 counts every line typed.
##   L-7. Nothing is asked. "Do you want to continue?" after a death, "Are
##        you sure?" on QUIT and the woman's "Do you want the lamp?" have no
##        Chord form. After a death the port goes on as if the answer were
##        yes.
##   L-8. SCORE's second line gives the class letter and leaves off "for the
##        next rating you need N more points".
##  L-15. A noun typed alone gets "What about it?" only when the thing is
##        here or carried; otherwise the parser's text of L-6. The original
##        says it for any word it knows.
##
##  What can be typed
##  L-10. The safe's combination is typed `two-seven-three`; a grammar
##        pattern cannot hold `2-7-3`.
##  L-12. The noun comes second. The original takes verb and noun in either
##        order (G1); `LAMP LIGHT` is not understood here.
##  L-16. What cannot be seen cannot be named. A thing dropped in a dark room
##        stays there until there is light, where the original takes it.
##        TAKE PEARL in room 77, always dark, has its own words and works.
##  L-17. ME, the original's word for object 0, is spelled out verb by verb
##        (TAKE, GET, CARRY, WEAR, DROP, THROW, TOSS, GIVE, and ME alone),
##        because the platform reads "me" as the player. FEED, KILL, SHOOT,
##        RUB, READ, EAT and PUSH with ME are not written.
##  L-18. BARRE, the original's word, and BARRIER are both taken.
##  L-20. The original reads the first five letters of a noun (G5), so it
##        takes any word that starts with them. The port takes the stub and
##        the whole word (`plati`, `platinum`), and also the name each thing
##        was created under, which admits words the original does not have.
##
##  How it is built (nothing shows in play)
##   L-5, L-14. A thing has one presence line. The second line of the lamp,
##        the bottle, the silver, the rat, the cat and the vault belongs to a
##        thing the player always carries and never sees.
##
##  Not written
##    G3. The random exit west of room 60 (line 2960): nothing reads whether
##        a room has been visited. The exit is absent.
##   992. The one-in-three fatal accident when a dark room is described:
##        nothing fires when a room is described.
##   L-7. The lamp past its warning: the woman's offer and the recharge.
##
## CORRECTED BY OWNER RULING, 2026-11-10. Here the port does what the line
## evidently meant and the oracle does what it says, so the two differ on
## purpose. Each is in original-issues.md with the line and the ruling.
##    O-1  LEASH names the cat's leash, not the rat (line 1780).
##    O-8  FILL where there is water gives the water back (2560).
##    O-9  JUMP in an ordinary room says "Nothing happens." (2860).
##   O-10  READ PENNY prints the legend; READ WATER does not (2610).
##   O-11  A hungry rat bites as you leave; a dead one does not (2010).
##   O-12  The cat needs its leash (2110 to 2150).
##   O-13  The command after the ice or the dark keeps its noun (1001).
##   O-15  Room 51 has its way back from the well, as the paper has it (510).
##
## RESTORED UPSTREAM, before this repository received the source. Not a
## deviation of the port: the oracle and the port read the same file.
##    O-2  Line 975, `ON ERROR GOTO 0`, absent from the 14-Mar-79 listing and
##         restored from the 01-Mar-79 one. Kept (Phase 1). It changes only
##         how a failed CHAIN is reported and has no Chord form.
##    O-3  The transcription bug at line 2000.
##
## What the port is checked against:
##   original/UNDERG.BAS, original/LOOK.BAS      the 1979 source, as transcribed
##   scripts/oracle_run.py                       the original, run by bplus
##   scripts/world_parity.py                     87 rooms and 45 objects
##   tests/test_verbs_against_oracle.py          the walks, port against oracle
##   docs/work/port-underground-v1-chord/original-issues.md   the O register
##   docs/work/port-underground-v1-chord/deviation-ledger-draft.md
## Written from the listing and neither compared nor played: the woman as a
## target (THROW ROCK, KILL, SHOOT, PUSH) and "You are somehow paralyzed by
## the woman."

story
  title: Underground
  authors:
    Gary Kleppe
  id: underg
  ifid: D44A0572-6535-4D0B-92C7-35BDCF1192C0
  story-version: 0.1.0
  description: UNDERGROUND V1, 14-Mar-79, RSTS/E BASIC-PLUS, ported to Chord.
  states, reversible: alive, dying

  on every turn
    raise the player's turns by 1
  end on

  on every turn while the electric lamp is shining
    raise the player's lamp-life by 1
    phrase lamp-running-out when the player's lamp-life is 250
    phrase lamp-out-of-power when the player's lamp-life is 300
    change the electric lamp to dormant when the player's lamp-life is 300
  end on

  on every turn while dying
    phrase you-are-dead
    move the something valuable here when the player holds the something valuable
    move the platinum wire here when the player holds the platinum wire
    move the uranium here when the player holds the uranium
    move the ancient statue here when the player holds the ancient statue
    move the gold nuggets here when the player holds the gold nuggets
    move the gold record here when the player holds the gold record
    move the gold garbage can here when the player holds the gold garbage can
    move the gold pet's dish here when the player holds the gold pet's dish
    move the Gnomes' silver here when the player holds the Gnomes' silver
    move the large diamonds here when the player holds the large diamonds
    move the gold telescope here when the player holds the gold telescope
    move the large emerald here when the player holds the large emerald
    move the rare coins here when the player holds the rare coins
    move the rare stamps here when the player holds the rare stamps
    move the black pearl here when the player holds the black pearl
    move the golden key here when the player holds the golden key
    move the cat's leash to the Building when the player holds the cat's leash
    move the electric lamp to the Building when the player holds the electric lamp
    move the glass bottle to the Building when the player holds the glass bottle
    move the water to the Building when the player holds the water
    move the sunglasses to the Building when the player holds the sunglasses
    move the rock to the Building when the player holds the rock
    move the laser pistol to the Building when the player holds the laser pistol
    move the lump of coal to the Building when the player holds the lump of coal
    move the minuature sun to the Building when the player holds the minuature sun
    move the radiation-proof container to the Building when the player holds the radiation-proof container
    move the space gloves to the Building when the player holds the space gloves
    move the remote-control box to the Building when the player holds the remote-control box
    move the bone to the Building when the player holds the bone
    move the piece of cheese to the Building when the player holds the piece of cheese
    move the penny to the Building when the player holds the penny
    move the rat to the Building when the player holds the rat
    move the cat to the Building when the player holds the cat
    set the player's burden to 0
    lower the player's score by 10
    raise the player's deaths by 1
    change the story to alive
    lose three-deaths when the player's deaths > 2
    move the player to the Basement when the player's deaths < 3
  end on

## ---------------------------------------------------------------------------
## THE IMPORTS
##
## An import is a paste at its own line, so this sequence is arbitration
## order. The places come first, one file per region of the 1979 map, from
## the surface down (the regions' room numbers overlap, so this is geography,
## not numbering), then the things that stand in them (objects 0 to 15, 16 to
## 32, 33 to 45), then the two layers that speak:
## `phrases` before `verbs`. Those two each hold a phrasebook, and
## phrasebooks arbitrate by position, so the exit refusals of line 2870 are
## read ahead of the handlers' replies. No key is in both today. A `create`
## is order-independent, and `verbs` defines the conditions the places gate
## on (`lit-up`, `sun-lights`), which resolve from anywhere in the paste.
## ---------------------------------------------------------------------------

import "surface"
import "tunnels"
import "mine"
import "spaceport"
import "barrel"
import "chasm"
import "dwarf-city"
import "ancient-city"
import "gnome-city"
import "maze"
import "treasures"
import "carryables"
import "fixtures"
import "phrases"
import "verbs"

create the Adventurer
  a person, playable
  in the Outside Building
  counter score
  counter turns
  counter deaths
  counter burden
  counter lamp-life
  counter shots

  You.

before the game starts
  change the player to the Adventurer
end before
