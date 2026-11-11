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
    """O-1 and O-8 to O-11: five places where the port does what the 1979 line
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

    def test_leash_means_the_leash(self) -> None:
        """O-1. In the original TAKE LEASH is aimed at the rat ("Don't be
        stupid."); in the port the rat's room has no leash to take."""
        self.assertEqual(oracle_run.run([*self.TO_THE_RAT, "TAKE LEASH"]).splitlines()[-1], "Don't be stupid.")
        replies = story_run.run([*self.TO_THE_RAT, "TAKE LEASH", "TAKE RAT"])
        self.assertEqual(replies[-2][1], ["You can't see any such thing."])
        self.assertEqual(replies[-1][1], ["Don't be stupid."])


if __name__ == "__main__":
    unittest.main()
