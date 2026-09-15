story
  title: Duplicate Names
  authors:
    David Cornelson
  id: duplicate-names
  ifid: C0317981-6E63-453F-9213-929BD7193A04
  story-version: 0.1.0
  description: Does Chord permit two rooms with the same name?

create the Mine
  a room
  north to the Mine

  You are in a mine.

create the Mine
  a room
  south to the Mine

  You are in a mine.

create the Digger
  a person, playable
  in the Mine

  You.

before the game starts
  change the player to the Digger
end before
