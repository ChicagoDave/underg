story
  title: Underground
  authors:
    Gary Kleppe
  id: underg
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
    move the player to the Basement
  end on

## Rooms, exits, objects and their 1979 text load from the region and object
## files; the verbs from verbs.chord. The IFID and the deviation ledger are
## Phase 5.

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
