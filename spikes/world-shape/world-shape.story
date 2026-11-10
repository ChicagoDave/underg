story
  title: World Shape
  authors:
    David Cornelson
  id: world-shape
  ifid: 7C1B5C0E-5E0B-4D53-9C0A-6B1B1E2A9F01
  story-version: 0.1.0
  description: Which Chord 4.0.1 constructs carry UNDERGROUND's rooms, exits
    and objects? The Phase 3 authoring questions, asked of the compiler.

## Each block below is one question Phase 3 needs answered before 87 rooms
## are written. The texts are the 1979 program's own.

import "far-side"

## Q1: line breaks, a doubled space, a quoted line with leading spaces.
## Q2: a room name ending in a full stop.
## Q3: `in`/`out` exits, an exit to the room itself, all one-way on one line.
## Q4: blocked and deadly exits beside an `exits:` line.

create the Top of Ramp
  a room
  room name:
    Top of ramp.
  exits, one-way: north to the City, in to the Far Side, out to the Top of Ramp
  south is blocked: door-is-closed
  down is deadly: volcano

  You are in a dark mine corridor.  the corridor continues{br}
  up and down. The floor is a grating.

## Q5: the sign's two indented lines.
## Q6: DOOR and BARRIER as passages, one of them blocked.

create the City
  a room
  room name:
    City
  exits, one-way: south to the Top of Ramp

  passage to the Far Side
    grammar
      door
  end passage

  passage to the Top of Ramp
    grammar
      barrier
    blocked: barrel-spins
  end passage

  north, and a road goins NW, where it is written:{br}
          "You must have at least 380 points to travel{br}
             on this road."

## Q7: a room with no name and no description at all (room 85, O-7).

create the Room 85
  a room

## Q8: a carried thing with its own presence line.

create the platinum wire
  a thing
  aka wire, coil, plati
  in the Top of Ramp

  phrase present while not the player holds the platinum wire:
    There is a coil of platinum wire here!

## Q9: a fixture that announces itself and cannot be taken.

create the robot
  a thing, scenery
  in the Top of Ramp

  phrase present:
    There is a robot here.

## Q10: a thing that starts nowhere (O%(n) = 0).

create the ancient statue
  a thing
  aka statu

  phrase present while not the player holds the ancient statue:
    There is an ancient statue here!

create the Digger
  a person, playable
  in the Top of Ramp

  You.

before the game starts
  change the player to the Digger
end before

define phrases en-US
  door-is-closed:
    The door is closed.
  barrel-spins:
    The barrel's spinning motion prevents you from moving this way.
  volcano:
    You are INSIDE an active volcano. Lava flies about in all directions.
