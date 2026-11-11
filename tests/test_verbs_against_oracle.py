"""Tests for the Phase 4 verbs: the Chord port against the 1979 program.

Purpose: play the same commands through the oracle (`bplus.c` running the
unmodified source) and through `story/`, and hold the port to what the
original ends up with: what the player is carrying and what the score is.

Public interface: run with `python3 -m unittest discover -s tests`.

Owner context: Phase 4 verification. Both sides are the real thing: the
compiled interpreter and `sharpee play`. Nothing expected here is typed in by
hand; every expectation is read off the oracle's own output for that walk.
State is compared, not prose, because the port prints rooms differently by
platform decision (deviation ledger L-1 to L-4); the reply lines that can be
compared directly are compared directly.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import oracle_run  # noqa: E402
import story_run  # noqa: E402

# An unknown word makes the 1979 program print one fixed line, which marks
# where the closing INVEN begins in a transcript that does not echo commands.
MARK = "XYZZY"
MARK_REPLY = "I don't know what that means."


# Commands the port spells differently (deviation ledger L-10).
STORY_FORM = {"2-7-3": "two-seven-three"}


def oracle_end_state(commands: list[str]) -> tuple[list[str], str]:
    """Return (carried names, score line) the 1979 program ends the walk with."""
    lines = oracle_run.run([*commands, MARK, "INVEN", "SCORE"]).splitlines()
    start = len(lines) - 1 - lines[::-1].index(MARK_REPLY)
    score = next(i for i in range(start, len(lines)) if lines[i].startswith("You have scored"))
    # The mark is an input line, and line 1010 counts every input line as a
    # turn, understood or not. Take that one turn back out.
    head, turns, tail = lines[score].rpartition(" possible in")[2].strip().partition(" ")
    line = lines[score].rpartition(" possible in")[0] + f" possible in {int(head) - 1} {tail}"
    return [line_ for line_ in lines[start + 1:score] if line_.strip()], line


def story_end_state(commands: list[str]) -> tuple[list[str], str, list[tuple[str, list[str]]]]:
    """Return (carried names, score line, every reply) the port ends the walk with."""
    replies = story_run.run([*commands, "INVEN", "SCORE"])
    return replies[-2][1], replies[-1][1][0], replies


def normal(score_line: str) -> str:
    """The original prints a number with a leading space or a minus sign."""
    return " ".join(score_line.replace("scored-", "scored -").split())


class WalksEndWhereTheOriginalDoes(unittest.TestCase):
    def assert_same_end(self, commands: list[str], oracle_only: tuple[int, ...] = ()) -> list:
        """`oracle_only` are positions of answers to the original's own
        prompts ("Do you want to continue?"), which the port never asks."""
        for_story = [STORY_FORM.get(c, c) for i, c in enumerate(commands) if i not in oracle_only]
        want_carried, want_score = oracle_end_state(commands)
        got_carried, got_score, replies = story_end_state(for_story)
        self.assertEqual(got_carried, want_carried)
        self.assertEqual(normal(got_score), normal(want_score))
        return replies

    def test_taking_lighting_and_carrying_into_the_dark(self) -> None:
        """Take and light the lamp, take the bottle (the water comes with it),
        wear the sunglasses, shoot the robot with no target named, pour the
        water in the mine (the nuggets land at the bottom), take them."""
        walk = ["W", "TAKE LAMP", "LIGHT", "TAKE BOTTLE", "D", "TAKE SUNGL", "U", "E", "N", "W",
                "TAKE LASER", "IN", "N", "SHOOT", "E", "E", "D", "POUR", "D", "D", "D", "TAKE GOLD"]
        replies = self.assert_same_end(walk)
        said = {command: lines for command, lines in replies}
        self.assertEqual(said["take sungl"], ["You are now wearing them."])
        self.assertEqual(said["shoot"], ["The laser beam strikes it's target and disintegrates it."])
        self.assertEqual(said["pour"], ["There is a loud explosion below you."])

    def test_dying_at_the_robot_and_waking_in_the_basement(self) -> None:
        """The robot kills on the way out. The original asks whether to go on;
        answered yes, everything carried is back in the building, ten points
        are gone, and the player is in the basement with empty hands."""
        walk = ["W", "TAKE LAMP", "LIGHT", "TAKE PENNY", "E", "N", "TAKE ROCK", "W", "TAKE LASER",
                "IN", "N", "E", "Y"]
        replies = self.assert_same_end(walk, oracle_only=(12,))
        death = replies[12][1]
        self.assertEqual(death[0], "On your way out, the robot fires a laser blast which kills you.")
        self.assertEqual(death[1], "You are dead.")
        self.assertEqual(death[2], "Basement")

    def test_what_came_back_to_the_building_can_be_picked_up_again(self) -> None:
        """After the death above the lamp, rock, laser and penny lie in room 1."""
        walk = ["W", "TAKE LAMP", "TAKE PENNY", "E", "N", "TAKE ROCK", "W", "TAKE LASER", "LIGHT",
                "IN", "N", "E", "Y", "U", "TAKE LAMP", "TAKE ROCK", "TAKE LASER", "TAKE PENNY"]
        self.assert_same_end(walk, oracle_only=(12,))

    def test_a_treasure_in_the_building_scores_until_it_is_picked_up(self) -> None:
        """Lines 2160 and 2240: the nuggets are worth 25 points lying in room
        1 and nothing in the hand. Both ends are read off the oracle."""
        fetch = ["W", "TAKE LAMP", "LIGHT", "TAKE BOTTLE", "E", "N", "W", "TAKE LASER", "IN", "N",
                 "SHOOT", "E", "E", "D", "POUR", "D", "D", "D", "TAKE GOLD",
                 "U", "U", "U", "U", "NE", "W", "S", "S", "S", "S", "W", "DROP GOLD"]
        self.assert_same_end(fetch)
        self.assertIn("scored 25 points", oracle_end_state(fetch)[1])
        self.assert_same_end([*fetch, "TAKE GOLD"])

    def test_the_elevator_the_gnome_and_the_safe(self) -> None:
        """Up the elevator by its lever, the rock that knocks the Gnome off
        his cliff (and stays in the hand), the safe that opens once to the
        combination, the silver, and the elevator back down."""
        walk = ["W", "TAKE LAMP", "LIGHT", "E", "N", "TAKE ROCK", "W", "TAKE LASER", "IN", "N",
                "SHOOT", "N", "PUSH LEVER", "S", "IN", "THROW ROCK", "N", "READ MESSA", "E",
                "2-7-3", "2-7-3", "TAKE SILVE", "W", "S", "S", "S", "PUSH LEVER", "S"]
        replies = self.assert_same_end(walk)
        said = {command: lines for command, lines in replies}
        self.assertEqual(said["throw rock"], ["The rock hits the Gnome on the head, and he falls down the cliff."])
        self.assertEqual(replies[20][1], ["The Gnomes' safe slides open. There is silver inside!"])
        self.assertEqual(replies[21][1], ["Hut-Hut-Hike!"])
        self.assertEqual(replies[-3][1][0], "Junction of tunnels")

    def assert_replies_are_the_originals(self, walk: list[str], replies: list, commands: list[str]) -> None:
        """The first line the port printed for each of `commands` (the last
        time it was typed) is a line the original printed in the same walk.
        Only the first line: what follows a death or a move is the room, which
        the port lays out its own way (deviation ledger L-1 to L-4)."""
        oracle = {" ".join(line.split()) for line in oracle_run.run(walk).splitlines()}
        said = {command: lines for command, lines in replies}
        for command in commands:
            lines = said[STORY_FORM.get(command, command).lower()]
            self.assertTrue(lines, f"the port said nothing to {command}")
            self.assertIn(" ".join(lines[0].split()), oracle, f"reply to {command}")

    LONG_WALK = ["W", "TAKE LAMP", "LIGHT", "D", "TAKE SUNGL", "U", "E", "N", "TAKE ROCK", "W",
                 "TAKE LASER", "IN", "N", "SHOOT", "W", "W", "TAKE GLOVE", "TAKE CONTA", "NE", "SE",
                 "SW", "SW", "N", "TAKE SUN", "NE", "E", "NE", "N", "PUSH LEVER", "S",
                 "N", "W", "W", "N", "TAKE CHEES", "N", "TAKE BONE", "W", "E", "W", "S", "S",
                 "IN", "THROW ROCK", "N", "N", "DROP SUN", "TAKE DIAMO", "N", "DROP BONE", "NW",
                 "TAKE CAT", "DROP CHEES", "TAKE CHEES", "N", "TAKE DISH", "S", "NW", "W", "S", "S", "S",
                 "W", "S", "SE", "W", "N", "N", "W", "DROP CHEES"]

    def test_the_long_walk_to_the_rats_death(self) -> None:
        """Gloves and container for the sun, the cheese and the bone out of
        the maze, the Gnome, the sun that melts the ice (the diamonds appear),
        the bone that sends the dog away, the cat that will not be taken and
        sniffs at the cheese, the dish, and the cheese that kills the rat.
        The walk stops there: in the original nothing can be done after the
        rat is dead (see `test_after_the_rat_dies_the_original_kills_you`)."""
        replies = self.assert_same_end(self.LONG_WALK)
        self.assert_replies_are_the_originals(
            self.LONG_WALK, replies,
            ["TAKE GLOVE", "TAKE SUN", "DROP SUN", "TAKE DIAMO", "DROP BONE", "TAKE CAT", "TAKE DISH"])
        cheese = [lines[0] for command, lines in replies if command == "drop chees"]
        oracle = oracle_run.run(self.LONG_WALK).splitlines()
        self.assertEqual(len(cheese), 2)
        self.assertLess(oracle.index(cheese[0]), oracle.index(cheese[1]), "the cat sniffs first, the rat eats second")

    UP = ["W", "TAKE LAMP", "LIGHT", "E", "N", "TAKE ROCK", "W", "TAKE LASER", "IN", "N"]
    SPHERE = [*UP, "SHOOT", "N", "PUSH LEVER", "S"]
    FAR_SIDE = [*SPHERE, "W", "S", "SE", "W", "N", "N"]
    TO_THE_DOG = ["W", "TAKE LAMP", "LIGHT", "D", "TAKE SUNGL", "U", "E", "N", "TAKE ROCK", "W", "TAKE LASER",
                  "IN", "N", "SHOOT", "W", "W", "TAKE GLOVE", "TAKE CONTA", "NE", "SE", "SW", "SW", "N",
                  "TAKE SUN", "NE", "E", "NE", "N", "PUSH LEVER", "S", "IN", "THROW ROCK", "N", "N", "DROP SUN", "N"]
    WITH_COAL = ["W", "TAKE LAMP", "TAKE PENNY", "LIGHT", "E", "N", "W", "TAKE LASER", "IN", "N", "SHOOT",
                 "E", "E", "D", "D", "TAKE COAL", "U", "U", "NE", "W", "N", "PUSH LEVER", "S",
                 "W", "S", "SE", "W", "N", "N", "E", "W"]
    WITH_BOX = [*UP, "SHOOT", "W", "TAKE BOX"]
    PAST_THE_VAULT = [*FAR_SIDE, "E", "E", "NE", "S", "OPEN VAULT"]

    # Each: the walk, then the commands whose replies are checked against the
    # original's. A "Y" is the answer to "Do you want to continue?", which the
    # port never asks (L-7); it is left out of the port's walk.
    SHORT_WALKS = {
        "the robot": ([*UP, "THROW ROCK", "KILL ROBOT", "FEED ROBOT", "TAKE ROBOT", "DROP ROBOT", "RUB ROBOT",
                       "READ ROBOT", "EAT ROBOT", "SHOOT ROBOT", "THROW ROCK"],
                      ["KILL ROBOT", "FEED ROBOT", "TAKE ROBOT", "DROP ROBOT", "RUB ROBOT", "READ ROBOT",
                       "EAT ROBOT", "SHOOT ROBOT", "THROW ROCK"]),
        "the Gnome's alarm": ([*SPHERE, "IN", "KILL GNOME", "FEED GNOME", "RUB GNOME", "TAKE GNOME", "SHOOT GNOME", "Y"],
                              ["KILL GNOME", "FEED GNOME", "RUB GNOME", "TAKE GNOME", "SHOOT GNOME"]),
        "the Gnome's knife": ([*SPHERE, "IN", "N", "Y"], ["N"]),
        "the cliff at the gate": ([*SPHERE, "IN", "JUMP", "Y"], ["JUMP"]),
        "the ice": ([*SPHERE, "IN", "THROW ROCK", "N", "N", "N", "INVEN", "SHOOT ICE", "KILL ICE", "TAKE ICE", "S"],
                    ["SHOOT ICE", "KILL ICE", "TAKE ICE", "S"]),
        "the dog": ([*TO_THE_DOG, "THROW ROCK", "KILL DOG", "FEED DOG", "SHOOT DOG", "NW", "Y"],
                    ["THROW ROCK", "KILL DOG", "FEED DOG", "SHOOT DOG", "NW"]),
        "the dwarf's knife": ([*FAR_SIDE, "E", "W", "KILL DWARF", "FEED DWARF", "NE", "W", "N", "Y"],
                              ["KILL DWARF", "FEED DWARF", "N"]),
        "the dwarf and the rock": ([*FAR_SIDE, "E", "W", "THROW ROCK", "Y"], ["THROW ROCK"]),
        # (In the pearl's walk the INVEN is there for the oracle: a two-word
        # command typed straight after "I can't see a thing." loses its noun
        # in the original, which is O-13 again, line 992 this time.)
        # Both stop in the short passage: past it the port has the paper's
        # exits and the oracle the transcribed ones (O-15, `CorrectedSlips`).
        "coal fed, the dwarf's door": ([*WITH_COAL, "FEED DWARF", "N", "OPEN", "N"], ["FEED DWARF", "OPEN"]),
        "coal dropped": ([*WITH_COAL, "DROP COAL", "N", "N"], ["DROP COAL"]),
        "the cart": ([*UP, "SHOOT", "SW", "SW", "S", "PUSH CART", "TAKE STATU", "S"], ["PUSH CART", "TAKE STATU", "S"]),
        "the emerald": ([*SPHERE, "W", "S", "SE", "TAKE EMERA", "RUB EMERA", "DROP EMERA", "RUB EMERA", "RUB ROCK"],
                        ["TAKE EMERA", "DROP EMERA", "RUB ROCK"]),
        "the emerald kept": ([*SPHERE, "W", "S", "SE", "RUB EMERA", "W", "JUMP", "Y"], ["RUB EMERA", "JUMP"]),
        "the spaceship": ([*WITH_BOX, "PUSH COMPU", "TAKE WIRE", "W", "TAKE GLOVE", "TAKE CONTA", "PUSH BUTTO", "W",
                           "IN", "TAKE URANI", "OUT", "Y"], ["PUSH COMPU", "PUSH BUTTO", "TAKE URANI", "OUT"]),
        "uranium with bare hands": ([*WITH_BOX, "PUSH BUTTO", "W", "W", "IN", "TAKE URANI"], ["TAKE URANI"]),
        "crushed by the spaceship": ([*WITH_BOX, "W", "W", "PUSH BUTTO", "Y"], ["PUSH BUTTO"]),
        "the computer shot": ([*WITH_BOX, "SHOOT COMPU", "PUSH BUTTO", "W", "W", "E", "N", "TAKE TELES", "OUT"],
                              ["SHOOT COMPU", "PUSH BUTTO", "TAKE TELES"]),
        "locks": (["W", "TAKE LAMP", "LIGHT", "D", "OPEN", "N", "U", "OPEN", "E", "N", "W", "TAKE LASER", "IN", "N",
                   "SHOOT", "SW", "SW", "SE", "OPEN", "S", "OPEN LAMP"], ["OPEN", "S", "OPEN LAMP"]),
        "the vault": ([*FAR_SIDE, "E", "E", "NE", "NW", "TAKE STAMP", "S", "S", "READ VAULT", "KILL VAULT",
                       "SHOOT VAULT", "TAKE VAULT", "OPEN VAULT", "W", "E"],
                      ["READ VAULT", "KILL VAULT", "SHOOT VAULT", "TAKE VAULT", "E"]),
        "north of the square room": ([*PAST_THE_VAULT, "N", "NE", "N", "D", "U", "JUMP", "Y"], ["NE", "JUMP"]),
        "the volcano": ([*PAST_THE_VAULT, "S", "Y"], ["S"]),
        "room 85": ([*PAST_THE_VAULT, "E", "N", "DROP ROCK", "TAKE ROCK"], ["N", "TAKE ROCK"]),
        "the bottle is full again once dropped": (["W", "TAKE BOTTL", "POUR", "DROP BOTTL", "TAKE BOTTL", "POUR",
                                                   "THROW BOTTL", "TAKE WATER", "DRINK WATER", "EAT BOTTL"],
                                                  ["POUR", "DRINK WATER", "EAT BOTTL"]),
        "the pearl in the room that is always dark": ([*SPHERE, "N", "W", "W", "N", "N", "N", "INVEN", "TAKE PEARL",
                                                       "D", "BARRE", "DROP PEARL", "TAKE PEARL"], ["TAKE PEARL"]),
        "ME is the valuable thing": ([*SPHERE, "TAKE ME", "DROP ME", "E", "E", "N", "NW", "TAKE ME", "N", "TAKE RECOR",
                                      "S", "W", "BARRE", "DROP ME", "DROP ME", "TAKE ME", "TAKE ME", "ME"],
                                     ["TAKE ME", "DROP ME", "ME"]),
        "ME when it is not here": ([*UP, "TAKE ME", "DROP ME", "THROW ME"], ["TAKE ME", "DROP ME", "THROW ME"]),
        "feeding and throwing at the rat": ([*SPHERE, "N", "W", "W", "N", "TAKE CHEES", "E", "W", "S", "S", "W", "S",
                                             "SE", "W", "N", "N", "W", "KILL RAT", "THROW ROCK", "EAT RAT",
                                             "FEED RAT", "TAKE RAT"], ["KILL RAT", "EAT RAT", "FEED RAT", "TAKE RAT"]),
    }

    def test_each_short_walk_ends_where_the_original_does(self) -> None:
        """One guardian, fixture or special case per walk: same things in
        hand, same score and same number of turns at the end, and the verb's
        own answer is the original's."""
        for name, (walk, checked) in self.SHORT_WALKS.items():
            with self.subTest(name):
                answers = tuple(i for i, command in enumerate(walk) if command == "Y")
                replies = self.assert_same_end(walk, oracle_only=answers)
                self.assert_replies_are_the_originals(walk, replies, checked)

    def test_a_verb_with_no_noun(self) -> None:
        """Lines 2180, 2500, 2570, 2650: "What?"; PUSH alone falls to 2540.
        And the other way about, line 1980: a noun with no verb."""
        probes = ["EAT", "DRINK", "TAKE", "DROP", "FEED", "RUB", "READ", "KILL", "PUSH", "THROW", "FILL", "POUR",
                  "LAMP", "PENNY"]
        oracle = oracle_run.run(["W", MARK, *probes]).splitlines()
        want = oracle[len(oracle) - 1 - oracle[::-1].index(MARK_REPLY) + 1:]
        got = [line for _, lines in story_run.run(["W", *probes])[2:] for line in lines]
        self.assertEqual(got, want)

    def test_the_two_ways_the_original_removes_you(self) -> None:
        """SHOOT URANI (line 3110) and the road out of the City below 381
        points (line 3100) end the game. The port's last words are the
        original's last words, and it says nothing after them."""
        for walk in ([*self.WITH_BOX, "PUSH BUTTO", "W", "W", "IN", "SHOOT URANI"],
                     [*self.FAR_SIDE, "E", "E", "NE", "SE"]):
            with self.subTest(walk[-1]):
                oracle = [line for line in oracle_run.run(walk).splitlines() if line.strip()]
                last = story_run.run(walk)[-1][1]
                self.assertGreaterEqual(len(last), 2)
                self.assertEqual(last, oracle[-len(last):])

    def test_the_third_death_is_the_last(self) -> None:
        """Line 3054: killed by the robot three times, the game is over, and
        the port does not wake you in the basement a third time."""
        die = ["E", "N", "W", "IN", "N", "E"]
        oracle = [" ".join(l.split()) for l in oracle_run.run(["W", *die, "Y", "U", *die, "Y", "U", *die, "Y"]).splitlines()]
        last = story_run.run(["W", *die, "U", *die, "U", *die])[-1][1]
        self.assertEqual(last[-2:], [l for l in oracle if l][-2:])
        self.assertNotIn("Basement", last)

    def test_the_second_presence_lines(self) -> None:
        """L-5: the lit lamp, the silver in its safe and the dead rat are each
        announced by the original's own line for that state."""
        cases = {
            "lit lamp": ["W", "TAKE LAMP", "LIGHT", "DROP LAMP", "LOOK"],
            "silver in the safe": [*self.SPHERE, "IN", "THROW ROCK", "N", "E", "2-7-3", "LOOK"],
            "dead rat": [*self.SHORT_WALKS["feeding and throwing at the rat"][0][:-1], "LOOK"],
        }
        for name, walk in cases.items():
            with self.subTest(name):
                oracle = oracle_run.run(walk).splitlines()
                line = next(l for l in reversed(oracle) if name.split()[0] in l or name.split()[-1] in l)
                shown = " ".join(story_run.run([STORY_FORM.get(c, c) for c in walk])[-1][1])
                self.assertIn(line, shown)

    def test_default_replies_of_each_verb(self) -> None:
        """Every verb aimed at something it has no special case for says what
        the original says. The expected lines are the oracle's, in order."""
        setup = ["W", "TAKE LAMP", "TAKE BOTTLE"]
        probes = ["FEED LAMP", "KILL LAMP", "OPEN LAMP", "RUB LAMP", "EAT LAMP", "PUSH LAMP",
                  "DRINK WATER", "READ LAMP", "OPEN", "FUCK", "SHIT", "OFF", "SHOOT"]
        oracle = [l for l in oracle_run.run([*setup, MARK, *probes]).splitlines()]
        want = oracle[len(oracle) - 1 - oracle[::-1].index(MARK_REPLY) + 1:]
        got = [line for _, lines in story_run.run([*setup, *probes])[len(setup) + 1:] for line in lines]
        self.assertEqual(got, want)


class CorrectedSlips(unittest.TestCase):
    """O-1, O-8 to O-11, O-13 and O-15: places where the port does what the 1979 line
    evidently meant, by owner rulings of 2026-11-10. Each test shows both
    halves: the oracle still has the slip, and the port has the correction. If
    the oracle half ever fails, the source or the interpreter changed and the
    ruling needs looking at again."""

    def test_fill_at_the_lake_puts_the_water_back_in_hand(self) -> None:
        walk = ["W", "TAKE BOTTLE", "E", "N", "E", "POUR", "FILL"]
        oracle = oracle_run.run([*walk, "INVEN"]).splitlines()
        self.assertEqual(oracle[-1], "Nothing happens.", "the original stops dead at FILL")
        replies = story_run.run([*walk, "INVEN"])
        self.assertEqual(replies[-3][1], ["Nothing happens."])
        self.assertEqual(replies[-2][1], ["Done."])
        self.assertEqual(replies[-1][1], ["Glass bottle.", "Water in the bottle."])

    def test_fill_away_from_water_is_still_refused(self) -> None:
        walk = ["W", "TAKE BOTTLE", "FILL"]
        self.assertEqual(oracle_run.run(walk).splitlines()[-1], "With what? Saliva?")
        self.assertEqual(story_run.run(walk)[-1][1], ["With what? Saliva?"])

    def test_jump_in_an_ordinary_room_does_nothing(self) -> None:
        oracle = oracle_run.run(["JUMP", "LOOK"]).splitlines()
        self.assertEqual(oracle[-1], "The laser beam strikes it's target and disintegrates it.")
        replies = story_run.run(["JUMP", "LOOK"])
        self.assertEqual(replies[1][1], ["Nothing happens."])
        self.assertEqual(replies[2][1][0], "Outside building", "and the game goes on")

    def test_the_legend_is_on_the_penny_not_the_water(self) -> None:
        walk = ["W", "TAKE PENNY", "TAKE BOTTLE", "READ PENNY", "READ WATER"]
        oracle = oracle_run.run(walk).splitlines()
        self.assertEqual(oracle[-5:], ["There is nothing written on it.", "In god we trust", "Liberty", "1979", ""])
        replies = story_run.run(walk)
        self.assertEqual(replies[-2][1], ["In god we trust", "Liberty", "1979"])
        self.assertEqual(replies[-1][1], ["There is nothing written on it."])

    TO_THE_RAT = ["W", "TAKE LAMP", "LIGHT", "E", "N", "W", "TAKE LASER", "IN", "N", "SHOOT", "N",
                  "PUSH LEVER", "S", "W", "S", "SE", "W", "N", "N", "W"]

    def test_a_hungry_rat_bites_when_you_walk_away(self) -> None:
        """O-11. In the original you leave the rat's room unharmed; in the
        port the hungry rat bites, and you wake in the basement."""
        oracle = oracle_run.run([*self.TO_THE_RAT, "N"]).splitlines()
        self.assertIn("garbage dump", oracle[-3])
        replies = story_run.run([*self.TO_THE_RAT, "N", "INVEN"])
        self.assertEqual(replies[-2][1][:3],
                         ["As you walk away, the rat bites you and you die.", "You are dead.", "Basement"])
        self.assertEqual(replies[-1][1], [], "everything carried went back to the building")

    def test_after_the_rat_dies_the_original_kills_you(self) -> None:
        """O-11, the other half of line 2010. Once the rat is dead the line
        ANDs 1 with (the rat's room - yours) bit by bit, so leaving any room
        an odd number of rooms from the rat is "the rat bites you". With the
        rat lying dead in room 46 the original lets you into room 45 and
        kills you on the way out of it; nothing past the rat can be played.
        The port, where only a hungry rat bites, walks on."""
        walk = [*self.TO_THE_RAT[:11], "PUSH LEVER", "S", "N", "W", "W", "N", "TAKE CHEES", "E", "W", "S", "S",
                *self.TO_THE_RAT[13:], "DROP CHEES", "NE", "S"]
        oracle = oracle_run.run(walk).splitlines()
        self.assertEqual(oracle[-3:], ["As you walk away, the rat bites you and you die.", "You are dead.",
                                       "Do you want to continue?"])
        replies = story_run.run([*walk, "INVEN"])
        self.assertEqual(replies[-2][1][0], "You are on a bridge which spans the giant chasm.")
        self.assertEqual(replies[-1][1], ["Electric lamp.", "Laser pistol."], "alive, and still carrying")

    def test_the_command_after_the_ice_keeps_its_noun(self) -> None:
        """O-13. In the original the command typed after the ice stops you
        loses its noun ("What?") and the sun stays in hand; in the port it is
        read whole, the sun is dropped and the ice melts."""
        walk = [*WalksEndWhereTheOriginalDoes.TO_THE_DOG[:-2], "N", "DROP SUN"]
        oracle = oracle_run.run([*walk, "INVEN"]).splitlines()
        self.assertEqual(oracle[oracle.index("The ice is to slippery for you to move on.") + 1], "What?")
        self.assertIn("Minuature sun in container.", oracle)
        replies = story_run.run([*walk, "INVEN", "N"])
        self.assertEqual(replies[-4][1], ["The ice is to slippery for you to move on."])
        self.assertEqual(replies[-3][1][0], "The sun melts the ice.")
        self.assertNotIn("Minuature sun in container.", replies[-2][1])
        self.assertEqual(replies[-1][1][0], "You are in a room with exits S and SE.", "the way north is open")

    def test_the_way_back_from_the_well(self) -> None:
        """O-15. The transcribed line 510 sends north and east from the short
        passage to the well and nothing back, so in the oracle the coins the
        penny buys never leave. The paper sends west to the well and east or
        OUT back to the dwarf's door, and the port follows the paper: the
        coins come out in hand."""
        passage = [*WalksEndWhereTheOriginalDoes.WITH_COAL, "DROP COAL", "N", "N"]
        oracle = [l for l in oracle_run.run([*passage, "N", "DROP PENNY", "TAKE COINS", "OUT", MARK, "E", "OUT", "W", "INVEN"]).splitlines() if l.strip()]
        after = oracle[len(oracle) - 1 - oracle[::-1].index(MARK_REPLY) + 1:]
        self.assertEqual(after[0], "Well", "east is the well again")
        self.assertEqual(after[1], "you are in a short passage running E/W.", "and OUT of the well is the passage")
        self.assertEqual(after[2], "You can't move in that direction.", "and there is no way west")
        self.assertIn("Rare coins.", after)
        replies = story_run.run([*passage, "N", "W", "DROP PENNY", "TAKE COINS", "OUT", "E", "NE", "INVEN"])
        self.assertEqual(replies[-8][1], ["You can't move in that direction."], "north is not the well")
        self.assertEqual(replies[-7][1][0], "Well")
        self.assertEqual(replies[-3][1][0], "Dwarf door")
        self.assertEqual(replies[-2][1][0], "Dwarf city")
        self.assertIn("Rare coins.", replies[-1][1])

    def test_the_well_still_kills_a_jumper(self) -> None:
        """Line 2850, room 52: the same death in both, each reached its own way."""
        passage = [*WalksEndWhereTheOriginalDoes.WITH_COAL, "DROP COAL", "N", "N"]
        oracle = [" ".join(l.split()) for l in oracle_run.run([*passage, "N", "JUMP"]).splitlines()]
        died = story_run.run([*passage, "W", "JUMP"])[-1][1]
        self.assertIn(" ".join(died[0].split()), oracle)
        self.assertEqual(died[1:3], ["You are dead.", "Basement"])

    def test_leash_means_the_leash(self) -> None:
        """O-1. In the original TAKE LEASH is aimed at the rat ("Don't be
        stupid."); in the port the rat's room has no leash to take."""
        self.assertEqual(oracle_run.run([*self.TO_THE_RAT, "TAKE LEASH"]).splitlines()[-1], "Don't be stupid.")
        replies = story_run.run([*self.TO_THE_RAT, "TAKE LEASH", "TAKE RAT"])
        self.assertEqual(replies[-2][1], ["You can't see any such thing."])
        self.assertEqual(replies[-1][1], ["Don't be stupid."])


def listing(number: int) -> list[str]:
    """The strings the 1979 program prints on one line of UNDERG.BAS."""
    import re
    source = (REPO / "original" / "UNDERG.BAS").read_text(errors="replace").splitlines()
    line = next(l for l in source if l.split(" ", 1)[0] == str(number))
    return re.findall(r'&"([^"]*)"', line)


class PastTheRat(unittest.TestCase):
    """What comes after the rat's death cannot be played in the original (see
    `CorrectedSlips.test_after_the_rat_dies_the_original_kills_you`), so there
    is no oracle walk to hold these to. The port is played alone and each
    reply is held to the line of the listing that prints it: the cat that
    eats the rat (2700), the cat that needs its leash (2150, corrected O-12),
    the vault (2985) and the door the golden key opens (2370)."""

    WALK = [*WalksEndWhereTheOriginalDoes.LONG_WALK, "DROP ROCK", "DROP LASER", "TAKE RAT",
            "NE", "S", "NE", "NE", "E", "E", "SW", "IN", "N", "N", "N", "NW",
            "TAKE CAT", "DROP RAT", "TAKE CAT", "N", "TAKE LEASH", "S", "TAKE CAT", "INVEN",
            "NW", "W", "S", "S", "S", "W", "S", "SE", "W", "N", "N", "E", "E", "NE", "S",
            "DROP CAT", "LOOK", "TAKE KEY", "W", "OPEN", "INVEN"]

    @classmethod
    def setUpClass(cls) -> None:
        cls.replies = story_run.run(cls.WALK)[len(WalksEndWhereTheOriginalDoes.LONG_WALK) + 1:]

    def said(self, command: str, nth: int = 0) -> list[str]:
        return [lines for typed, lines in self.replies if typed == command.lower()][nth]

    def test_the_cat_wants_the_rat_then_its_leash(self) -> None:
        self.assertEqual(self.said("TAKE CAT", 0), ["Don't be stupid."], "a hungry cat is not taken")
        self.assertEqual(self.said("DROP RAT"), listing(2700))
        self.assertEqual(self.said("TAKE CAT", 1), listing(2150), "O-12: fed, but no leash in hand")
        self.assertEqual(self.said("TAKE CAT", 2), ["Done."])
        carried = self.said("INVEN", 0)
        self.assertIn("Cat on leash.", carried)
        self.assertIn("Cat's leash.", carried)
        self.assertNotIn("Dead rat.", carried, "the cat ate it")

    def test_the_cat_opens_the_vault_and_the_key_opens_the_door(self) -> None:
        self.assertEqual(self.said("DROP CAT"), listing(2985))
        vault = " ".join(self.said("LOOK"))
        self.assertIn("The vault is open.", vault)
        self.assertNotIn("The vault is closed.", vault)
        self.assertNotIn("cat", vault.replace("vault", ""), "the cat walked away")
        self.assertEqual(self.said("OPEN")[0], listing(2370)[0])
        self.assertEqual(self.said("OPEN")[1], "Basement", "pushed through the door")
        carried = self.said("INVEN", 1)
        self.assertIn("Golden key.", carried)
        self.assertNotIn("Cat on leash.", carried)


def walk(text: str) -> list[str]:
    return [command.strip() for command in text.split(",") if command.strip()]


class StartToEnd(unittest.TestCase):
    """The port played from the first move to the ending: sixteen treasures
    carried to the building in three trips (400 points), the road out of the
    City, the wall, the woman and the laser. No oracle walk can do this (O-11,
    O-15), so the port is played alone; the score lines are arithmetic on the
    original's 25 a treasure, and the ending is held to the listing."""

    FIRST_TRIP = walk("""W, TAKE LAMP, TAKE BOTTL, E, N, W, TAKE LASER, LIGHT, IN, N, SHOOT, DROP LASER,
        E, E, D, POUR, DROP BOTTL, D, TAKE COAL, D, D, TAKE GOLD, U, U, U, U, NE, W, DROP COAL,
        W, TAKE WIRE, TAKE BOX, W, TAKE GLOVE, TAKE CONTA, N, TAKE TELES, E,
        PUSH BUTTO, W, PUSH BUTTO, IN, TAKE URANI, IN, PUSH BUTTO, OUT, DROP BOX,
        NE, SE, SW, SW, S, PUSH CART, TAKE STATU, NE, N, TAKE SUN, NE, E, NE, S, S, OFF, S, S, W,
        DROP GOLD, DROP WIRE, DROP TELES, DROP URANI, DROP STATU, DROP GLOVE, SCORE""")
    SECOND_TRIP = walk("""TAKE PENNY, E, N, TAKE ROCK, W, LIGHT, IN, N, TAKE COAL, N, PUSH LEVER, S,
        IN, THROW ROCK, DROP ROCK, N, E, TWO-SEVEN-THREE, TAKE SILVE, W, N, DROP SUN, TAKE DIAMO, DROP CONTA,
        S, S, S, DROP SILVE, DROP DIAMO,
        N, W, W, N, TAKE CHEES, N, TAKE BONE, N, TAKE PEARL, D, BARRE, DROP PEARL, DROP BONE,
        E, E, N, NW, TAKE ME, N, TAKE RECOR, S, W, BARRE,
        W, S, SE, RUB EMERA, W, N, N, W, DROP CHEES, TAKE RAT, N, TAKE CAN, S, NE, E, W, DROP COAL,
        N, N, W, DROP PENNY, TAKE COINS, OUT, E, NE, NE, E, NE, NW, TAKE STAMP, S,
        N, N, S, S, NE, NE, E, E, SW,
        DROP ME, DROP RECOR, DROP CAN, DROP COINS, DROP STAMP, TAKE BONE,
        IN, N, N, N, DROP BONE, NW, DROP RAT, N, TAKE LEASH, TAKE DISH, S, TAKE CAT, NW, W, S, S, S,
        DROP CAT, DROP LEASH, TAKE SILVE, TAKE DIAMO, TAKE PEARL, TAKE ME, TAKE RECOR, TAKE CAN,
        S, PUSH LEVER, S, S, S, OFF, S, S, W,
        DROP SILVE, DROP DIAMO, DROP PEARL, DROP ME, DROP RECOR, DROP CAN, DROP DISH, RUB EMERA, SCORE""")
    THIRD_TRIP = walk("""E, N, W, LIGHT, IN, N, TAKE LASER, N, PUSH LEVER, S,
        TAKE LEASH, TAKE CAT, TAKE COINS, TAKE STAMP,
        W, S, SE, W, N, N, E, E, NE, S, DROP CAT, TAKE KEY, W, OPEN, OFF, U,
        DROP COINS, DROP STAMP, DROP KEY, DROP LEASH, SCORE, LOOK""")
    TO_THE_END = walk("""E, N, W, LIGHT, IN, N, N, PUSH LEVER, S, W, S, SE, W, N, N, E, E, NE, SE,
        SHOOT WALL, N, THROW LASER""")

    @classmethod
    def setUpClass(cls) -> None:
        cls.replies = story_run.run([*cls.FIRST_TRIP, *cls.SECOND_TRIP, *cls.THIRD_TRIP, *cls.TO_THE_END])[1:]

    def scores(self) -> list[str]:
        return [lines[0] for command, lines in self.replies if command == "score"]

    def test_each_trip_banks_its_treasures(self) -> None:
        """Five, then eight, then three treasures set down in the building."""
        points = [int(line.split()[3]) for line in self.scores()]
        self.assertEqual(points, [5 * 25, 13 * 25, 16 * 25])

    def test_no_command_on_the_way_is_refused_or_fatal(self) -> None:
        refusals = ("You are dead.", "You can't see any such thing.", "You can't move in that direction.",
                    "You can't carry so many things at once.", "It isn't here.", "You aren't carrying it.",
                    "Your lamp is running out of power.", "Which do you mean")
        stopped = [(command, line) for command, lines in self.replies for line in lines
                   if any(line.startswith(refusal) for refusal in refusals)]
        self.assertEqual(stopped, [])

    def test_all_sixteen_treasures_lie_in_the_building(self) -> None:
        building = " ".join([lines for command, lines in self.replies if command == "look"][0])
        for name in ("something extremely valuable", "platinum wire", "uranium", "statue", "gold nuggets",
                     "gold record", "garbage can", "pet's dish", "silver", "diamonds", "telescope", "emerald",
                     "rare coins", "rare stamps", "pearl", "golden key"):
            self.assertIn(name, building)

    def test_the_road_the_wall_and_the_woman(self) -> None:
        said = {command: lines for command, lines in self.replies}
        self.assertEqual(said["se"][0], "You are in a room which exits to the south.", "381 points open the road")
        self.assertEqual(said["shoot wall"], listing(2460))
        self.assertEqual(said["n"][-1], listing(2065)[0], "the last N of the walk is into room 87")
        ending = " ".join(" ".join(said["throw laser"]).split())
        self.assertTrue(ending.startswith(listing(2260)[0]))
        self.assertEqual(ending.count("The UNDERGROUND game is now yours."), 1, "said once")
        self.assertFalse(ending.endswith("Done."))
        for line in (*listing(3140), *listing(3141), *listing(3142), *listing(3143), *listing(3144)):
            self.assertIn(" ".join(line.replace("''", "'").split()), ending)


if __name__ == "__main__":
    unittest.main()
