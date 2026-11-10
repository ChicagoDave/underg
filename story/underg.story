story
  title: Underground
  authors:
    Gary Kleppe
  id: underg
  story-version: 0.1.0
  description: UNDERGROUND V1, 14-Mar-79, RSTS/E BASIC-PLUS, ported to Chord.

## Phase 3 entry file: the world only. Rooms, exits, objects and their
## 1979 text load from the files below. The verbs, the player proper, the
## IFID and the deviation ledger are Phases 4 and 5.

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

create the Adventurer
  a person, playable
  in the Building

  You.

before the game starts
  change the player to the Adventurer
end before
