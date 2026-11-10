story
  title: Verb Shape
  authors:
    David Cornelson
  id: verb-shape
  ifid: 7C1B5C0E-5E0B-4D53-9C0A-6B1B1E2A9F02
  story-version: 0.1.0
  description: Which Chord 4.0.1 constructs carry UNDERGROUND's verbs? The
    Phase 4 authoring questions, asked of the compiler.
  states, reversible: alive, dying

  on every turn while dying
    phrase you-are-dead
    move the rock to the Adventurer's location when the player holds the rock
    move the piece of cheese to the Building when the player holds the piece of cheese
    move the player to the Tunnel
    lower score by 10
    change the story to alive
    lose third-death when the player's deaths is 2
    raise the player's deaths by 1
  end on

create the Building
  a room
  room name:
    Building
  exits, one-way: down to the Tunnel

  You are in a one-room building.Stairs lead down.

create the Tunnel
  a room, dark while not lamp-shines
  room name:
    Tunnel
  exits, one-way: up to the Building

  You are in a dark north-south tunnel.

define condition lamp-shines: the electric lamp is shining and (the player holds the electric lamp or the electric lamp is here)

create the electric lamp
  a thing
  aka lamp
  in the Building
  states, reversible: dormant, shining

create the large emerald
  a thing
  aka emera, emerald
  in the Building

  on the player taking
    refuse emerald-falls
  end on

create the rock
  a thing, gem
  in the Building

  on the player taking
    refuse when the player's burden > 0: too-many
    raise the player's burden by 1
  end on

  after the player dropping
    lower the player's burden by 1
    kill the player rock-death when the rat is hungry
  end after

create the rat
  a thing
  aka leash
  in the Building
  states: hungry, dead

create the piece of cheese
  a thing
  aka chees, cheese
  in the Building

create the Adventurer
  a person, playable
  aka me
  in the Building
  counter deaths
  counter burden

  You.

before the game starts
  change the player to the Adventurer
end before

define action lighting
  grammar
    light
    light the thing
    on
    on the thing
  the player must hold the electric lamp: no-lamp
  refuse when the electric lamp is shining: already-on
  change the electric lamp to shining
  phrase lamp-is-lit

define action feeding
  grammar
    feed the animal
  refuse without animal: what
  refuse when the animal is not the rat: not-alive
  the player must hold the piece of cheese: no-food
  phrase rat-eats
  change the rat to dead
  remove the piece of cheese

define action hurling
  grammar
    throw the item
    toss the item
    give the item
  refuse without item: what
  refuse when the item is the rock and the rat is here: spca
  phrase done

define trait gem
  phrases en-US
    gem-note:
      A gem.
end trait

define action appraising
  grammar
    appraise the item
  phrase is-gem when the item is a gem
  phrase not-gem when the item is not a gem

define counter score
define counter turns

define action tallying
  grammar
    score
  lower score by 10
  raise turns by 3
  phrase score-line with points = the player's deaths and moves = turns
  phrase class-f when score < 100

define action grabbing
  grammar
    grab
  refuse when score > 8: too-many
  move the piece of cheese to the Adventurer
  move the rat to the player
  phrase done

define action dying
  grammar
    die
  phrase rat-bites
  change the story to dying

define action swearing
  grammar
    damn
    hell
  phrase headache

override message taking-taken
  Done.
end override

override message dropping-dropped
  Done.
end override

override message looking-room-dark
  I can't see a thing.
end override

define phrases en-US
  too-many:
    You can't carry so many things at once.
  rock-death:
    You are dead.
  spca:
    S.P.C.A. and humane society regulations clearly prohibit you from doing that.
  done:
    Done.
  headache:
    Not now-- I've got a headache.
  score-line:
    You have scored {verbatim:points} points out of 500 possible.
  class-f:
    This puts you in class F.
  you-are-dead:
    You are dead.
  rat-bites:
    As you walk away, the rat bites you and you die.
  third-death:
    Sorry, but people who are incompetent enough to die three times in the same game don't deserve the chance to make it four.
  is-gem:
    It is a gem.
  not-gem:
    It is no gem.
  emerald-falls:
    The emerald falls out of your hand.
  no-lamp:
    You don't have a lamp.
  already-on:
    It's already on.
  lamp-is-lit:
    The lamp is lit.
  what:
    What?
  not-alive:
    It isn't alive.
  no-food:
    There is nothing here you can use for food.
  rat-eats:
    The rat eats the cheese and immediately dies.
