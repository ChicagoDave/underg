story
  title: Seen Unseen
  authors:
    David Cornelson
  id: seen-unseen
  ifid: F28F58CA-FA78-4EA7-9AC6-C62A026B3BCB
  story-version: 0.1.0
  description: Can a room print its long text once and only its short name after?

## UNDERGROUND V1 prints a room's long text (line room*100) the first time
## and only its short name (line room*100+50) on every later entry. Room 2
## and room 3 of the original, the long text in a `first time` block and no
## plain description.

create the Building
  a room
  room name:
    Inside building
  east to the Path

  first time
    You are in a one-room building. Stairs lead down.

create the Path
  a room
  room name:
    Outside building
  west to the Building

  first time
    You are on a path which winds through the forest. The path here bends
    from south to west.

create the Digger
  a person, playable
  in the Building

  You.

before the game starts
  change the player to the Digger
end before
