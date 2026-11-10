#!/usr/bin/env python3
"""Behavioural tests for the world extractor.

Every assertion here traces to a line of `extract_world.py`'s Behavior
Statement, and every expected value is independently anchored - either in the
1979 source itself or in the oracle transcript at `tests/golden/oracle-smoke.txt`
- rather than in whatever the extractor happened to emit. A test that asserted
the decoder agrees with itself would pass just as happily on a decoder that
reads the matrix transposed.

Run: python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import extract_world  # noqa: E402


class WorldExtractionTests(unittest.TestCase):
    """The decode produces the world the 1979 source actually describes."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.world = extract_world.extract_world(
            REPO / "original" / "UNDERG.BAS",
            REPO / "original" / "LOOK.BAS",
        )

    def test_table_sizes_match_the_dim_statement(self) -> None:
        """DOES: 87 rooms and 45 objects, the sizes line 10's DIM declares."""
        self.assertEqual(len(self.world["rooms"]), 87)
        self.assertEqual(len(self.world["objects"]), 45)
        self.assertEqual(self.world["counts"]["data_values"], 1263)

    def test_start_room_matches_the_oracle_transcript(self) -> None:
        """DOES: room 8 is the start (line 70 sets X%(0%)=8%) and reads as the
        oracle's opening text, byte for byte off the golden transcript."""
        golden = (REPO / "tests" / "golden" / "oracle-smoke.txt").read_text().splitlines()
        room8 = self.world["rooms"][8]
        self.assertEqual(room8["name"], "Outside building")
        self.assertEqual(
            room8["description"],
            ["you are on a path which winds north into a dense forest.",
             "The west end of the path goes into a small building."],
        )
        # The same two lines are what the real interpreter printed at boot.
        self.assertEqual(room8["description"], golden[2:4])

    def test_exits_round_trip_the_walk_the_oracle_took(self) -> None:
        """DOES: exits are keyed by direction name and hold destination rooms.

        The golden transcript walks 8 -> west -> building -> east -> 8 -> north,
        so those three edges are checked against the walk rather than against
        the table that produced them."""
        self.assertEqual(self.world["rooms"][8]["exits"]["west"], 1)
        self.assertEqual(self.world["rooms"][1]["exits"]["east"], 8)
        self.assertEqual(self.world["rooms"][3]["name"], "Path")
        self.assertEqual(self.world["rooms"][8]["exits"]["north"], 3)

    def test_every_room_has_text_except_room_85(self) -> None:
        """DOES: resolves fall-through, so no room comes out blank by accident.

        Room 85 is the one real exception (O-7): `8500 !` falls through to
        `8550 goto10000`, which prints nothing and jumps to the object sweep.
        It is a bare room whose only content is the treasure standing in it.

        Asserting the exact exception set rather than "mostly fine" is what
        makes this test able to fail: an extractor that followed `goto10000`
        would give room 85 the object table's first line and pass a laxer
        check."""
        missing_name = [r for r, v in self.world["rooms"].items() if not v["name"]]
        missing_text = [r for r, v in self.world["rooms"].items() if not v["description"]]
        self.assertEqual(missing_name, [85])
        self.assertEqual(missing_text, [85])

    def test_the_object_table_is_not_mistaken_for_room_text(self) -> None:
        """REJECTS WHEN: a room line's `goto10000` is read as a delegation.

        10000 is where every room description jumps when it is finished, so
        following it hands the room the object sweep's first string. No room may
        carry it."""
        stray = "There is something extremely valuable here!"
        for room_id, room in self.world["rooms"].items():
            self.assertNotIn(stray, room["description"], f"room {room_id} picked up object text")
            self.assertNotEqual(room["name"], stray)

    def test_goto_delegation_is_followed(self) -> None:
        """DOES: room 6 is `600 goto700` / `650 goto750`, so it must read as
        room 7's text, not as an empty room."""
        self.assertEqual(self.world["rooms"][6]["description"], self.world["rooms"][7]["description"])
        self.assertEqual(self.world["rooms"][6]["name"], self.world["rooms"][7]["name"])
        self.assertTrue(self.world["rooms"][6]["description"])

    def test_refusal_codes_decode_to_their_messages_and_kinds(self) -> None:
        """DOES: negative exits become refusals carrying the original's text and
        a kind. Anchored on line 2870's jump table: -1 is the closed door, -6
        the cyanide atmosphere (fatal), -9 the computed random destination."""
        refusals = [
            (direction, data)
            for room in self.world["rooms"].values()
            for direction, data in room["refusals"].items()
        ]
        self.assertTrue(refusals, "the map has refusal-coded exits")

        by_code = {data["code"]: data for _, data in refusals}
        # All ten codes -1..-10 are reachable in the 14-Mar-79 map. Asserting
        # that unconditionally is the point: a decode regression that dropped a
        # code would otherwise slip past a guarded check.
        self.assertEqual(sorted(by_code), list(range(-10, 0)))

        self.assertEqual(by_code[-1]["message"], "The door is closed.")
        self.assertEqual(by_code[-1]["kind"], "refuse")
        self.assertEqual(by_code[-6]["kind"], "deadly")
        self.assertEqual(by_code[-8]["kind"], "deadly")
        self.assertEqual(by_code[-9]["kind"], "special")
        self.assertIsNone(by_code[-9]["message"])
        self.assertEqual(by_code[-10]["kind"], "special")

        for _, data in refusals:
            self.assertIn(data["kind"], {"refuse", "deadly", "special"})

    def test_objects_start_where_the_transcript_finds_them(self) -> None:
        """DOES: object entries carry a starting room.

        The oracle's walk into the building (room 1) reports the lamp, the
        bottle and the penny, which are objects 17, 18 and 30 by line 1244-1246's
        inventory ordering. So those three must start in room 1."""
        self.assertEqual(self.world["objects"][17]["start_room"], 1)
        self.assertEqual(self.world["objects"][18]["start_room"], 1)
        self.assertEqual(self.world["objects"][30]["start_room"], 1)

    def test_object_vocabulary_carries_the_leash_collision(self) -> None:
        """DOES: vocabulary is per object id, words spelled as the source spells
        them. O-1: LEASH and RAT both bind to object 31, so object 16 has no
        word of its own. Reproducing that is the point, so it is asserted."""
        self.assertEqual(sorted(self.world["objects"][31]["vocabulary"]), ["LEASH", "RAT"])
        self.assertEqual(self.world["objects"][16]["vocabulary"], [])
        # Truncated as the 1979 parser truncates: five characters, not English.
        self.assertIn("BOTTL", self.world["objects"][18]["vocabulary"])

    def test_branching_text_lines_are_flagged_not_guessed(self) -> None:
        """REJECTS WHEN: a line's prints are branch arms rather than postfix
        conditions.

        Regression for a real mis-pairing. LOOK.BAS 10180 is
        `ifo%(18%)=x%thenifo%(19%)=x%then&"bottle of water"else&"empty bottle"` -
        two ids and two strings, so positional zipping accepted it and handed
        the empty bottle to object 19 (the water). Both strings describe object
        18. The decoder must refuse to pair these, not guess."""
        objects = self.world["objects"]
        self.assertTrue(objects[18]["needs_review"])
        self.assertTrue(objects[19]["needs_review"])
        self.assertEqual(objects[19]["presence"], [])
        self.assertEqual(objects[18]["presence"], [])

        flagged = {int(i) for i, v in objects.items() if v["needs_review"]}
        self.assertEqual(flagged, {8, 17, 18, 19, 31, 32, 33, 34})

    def test_fixtures_have_no_carried_name(self) -> None:
        """DOES: the inventory table at 1241-1246 stops at object 32.

        Objects 33-45 are fixtures and creatures - the woman, the vault, the
        dwarf, the wall - and are never carried, so they have a presence line
        but no inventory name. A decoder inventing one would be wrong."""
        for object_id in range(33, 46):
            self.assertIsNone(
                self.world["objects"][object_id]["inventory_name"],
                f"object {object_id} is a fixture and has no carried name",
            )
        self.assertEqual(self.world["objects"][32]["inventory_name"], "Cat on leash.")

    def test_a_printing_line_runs_on_into_the_next_line(self) -> None:
        """DOES: follow a room's text across a line with no closing goto.

        LOOK.BAS 5400 prints four strings and has no goto; 5401 prints the
        fifth and then jumps. Likewise 5700 and 5701. Stopping at the first
        line left both signs open-quoted. The expected endings are read off
        lines 5401 and 5701 of the 1979 source."""
        city = self.world["rooms"][54]["description"]
        self.assertEqual(len(city), 5)
        self.assertEqual(city[-1], '           on this road."')
        vault = self.world["rooms"][57]["description"]
        self.assertEqual(len(vault), 4)
        self.assertEqual(
            vault[-1],
            '        anyone who attemps to open it will be immediately removed."',
        )
        # A line that does close with a goto must not run on: room 39's text
        # ends at its own third string, not at room 39's short name on 3950.
        self.assertEqual(self.world["rooms"][39]["description"][-1], '"GET ME OUT OF HERE!!!"')

    def test_a_short_data_block_is_rejected(self) -> None:
        """REJECTS WHEN: the DATA block is not exactly 1263 values.

        The failure mode this guards is silent, so the test drives the real
        check with a deliberately truncated source rather than trusting it."""
        import tempfile

        source = (REPO / "original" / "UNDERG.BAS").read_text(errors="replace")
        truncated = source.replace("880 DATA", "880 REMDATA", 1)
        with tempfile.NamedTemporaryFile("w", suffix=".BAS", delete=False) as handle:
            handle.write(truncated)
            path = Path(handle.name)
        try:
            with self.assertRaises(ValueError) as caught:
                extract_world.read_data_values(path)
            self.assertIn("expected 1263", str(caught.exception))
        finally:
            path.unlink()


if __name__ == "__main__":
    unittest.main()
