story
  title: Room Name
  authors:
    David Cornelson
  id: room-name
  ifid: 0FC269EA-27A9-49F0-94A8-14979E02E71B
  story-version: 0.1.0
  description: Can rooms that print the same name coexist? The answer to gap G9.

## Two shapes from UNDERGROUND V1. The three mines (rooms 25 to 27) are
## separate create blocks that share a printed name. The maze (rooms 61 to
## 63 here, 61 to 71 in the original) is one group in a region.

create the Mine 25
  a room
  room name:
    Mine
  north to the Mine 26

  You are in a mine.

create the Mine 26
  a room
  room name:
    Mine
  south to the Mine 25
  north to the Mine 27

  You are in a mine.

create the Mine 27
  a room
  room name:
    Mine
  south to the Mine 26
  east to the Maze 61, one-way

  You are in a mine.

create the Maze
  a region

  rooms Maze 61 to 63
    room name:
      You are in a maze of twisty little passages, all alike.

    You are in a maze of twisty little passages, all alike.

  exits, one-way
    the Maze 61: east to the Maze 62, west to the Mine 27
    the Maze 62: east to the Maze 63, west to the Maze 61
    the Maze 63: west to the Maze 62

create the Digger
  a person, playable
  in the Mine 25

  You.

before the game starts
  change the player to the Digger
end before
