"""Tests for the Phase 3 world: the Chord story against the 1979 decode.

Purpose: prove that `story/` compiles to the world `extracted/world.json`
describes, and that the instrument saying so reports each kind of drift.

Public interface: run with `python3 -m unittest discover -s tests`.

Owner context: Phase 3 acceptance. `StoryMatchesTheDecode` drives the real
Chord compiler over the real story files (no stub). `ParityCheckBites` hands
the checker a compiled story with one known defect at a time and asserts it
names the defect, so a checker that reports nothing cannot pass for one that
found nothing.
"""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import scaffold_world  # noqa: E402
import world_parity  # noqa: E402


class _Compiled(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.world = json.loads(world_parity.WORLD_PATH.read_text())
        cls.names = json.loads(world_parity.MAP_PATH.read_text())
        cls.ir = world_parity.compile_story()

    def entity(self, ir: dict, name: str) -> dict:
        return next(e for e in ir["entities"] if e["name"] == name)


class StoryMatchesTheDecode(_Compiled):
    def test_the_compiled_world_is_the_decoded_world(self) -> None:
        """DOES: 87 rooms and 45 objects, with every exit, refusal, placement,
        heading and line of text the decode holds."""
        self.assertEqual(world_parity.compare(self.world, self.names, self.ir), [])

    def test_the_maze_rooms_all_print_the_same_heading(self) -> None:
        """The point of gap G9: eleven rooms, one printed name. Read off
        LOOK.BAS, not off the checker."""
        phrases = self.ir["phrases"]["locales"]["en-US"]
        headings = {phrases[f"maze-{n}.room-name"]["variants"][0]["text"] for n in range(61, 72)}
        self.assertEqual(headings, {"You are in a maze of twisty little passages, all alike."})

    def test_the_player_starts_in_the_building(self) -> None:
        """Room 1, where the oracle's golden transcript opens."""
        player = next(e for e in self.ir["entities"] if e["isPlayable"])
        self.assertEqual(player["placement"]["place"], "building")

    def test_the_story_files_are_what_the_scaffold_writes(self) -> None:
        """Until Phase 4 edits them by hand, the files on disk are the
        scaffold's output. When that stops being true this test goes, and the
        parity test above is what remains."""
        for name, content in scaffold_world.render_files(self.world, self.names).items():
            self.assertEqual((REPO / "story" / name).read_text(), content, name)


class ParityCheckBites(_Compiled):
    """Each test breaks one thing in a copy of the compiled story and asserts
    the checker reports that thing."""

    def broken(self) -> dict:
        return copy.deepcopy(self.ir)

    def problems(self, ir: dict) -> list[str]:
        return world_parity.compare(self.world, self.names, ir)

    def test_a_redirected_exit_is_reported(self) -> None:
        ir = self.broken()
        self.entity(ir, "Building")["exits"][0]["to"]["id"] = "basement"
        found = self.problems(ir)
        self.assertTrue(any("room 1 " in p and "missing exit east to outside-building" in p for p in found), found)
        self.assertTrue(any("room 1 " in p and "exit east to basement is not in the original" in p for p in found), found)

    def test_a_two_way_exit_is_reported(self) -> None:
        ir = self.broken()
        self.entity(ir, "Path")["exits"][0]["oneWay"] = False
        self.assertTrue(any("room 3 " in p and "two-way" in p for p in self.problems(ir)))

    def test_a_dropped_refusal_is_reported(self) -> None:
        ir = self.broken()
        self.entity(ir, "Lake Shore")["blockedExits"].pop()
        self.assertTrue(any("room 9 " in p and "blocked exits" in p for p in self.problems(ir)))

    def test_a_deadly_exit_made_merely_blocked_is_reported(self) -> None:
        ir = self.broken()
        room = self.entity(ir, "Strange Planet")
        room["blockedExits"].append(room["deadlyExits"].pop())
        found = self.problems(ir)
        self.assertTrue(any("room 32 " in p and "deadly exits" in p for p in found), found)

    def test_an_authored_computed_exit_is_reported(self) -> None:
        """Room 60 west is code -9; a plain exit there would be an invention."""
        ir = self.broken()
        room = self.entity(ir, "One-Exit Passage 60")
        room["exits"].append({"direction": "west", "to": {"kind": "room", "id": "building"}, "via": None, "oneWay": True})
        self.assertTrue(any("room 60 " in p and "not in the original" in p for p in self.problems(ir)))

    def test_changed_room_text_is_reported(self) -> None:
        ir = self.broken()
        phrases = ir["phrases"]["locales"]["en-US"]
        phrases["cave-enterance.room-name"]["variants"][0]["text"] = "cave entrance"
        phrases["city.description"]["variants"][0]["text"] = phrases["city.description"]["variants"][0]["text"].replace("goins", "going")
        found = self.problems(ir)
        self.assertTrue(any("room 4 " in p and "room name" in p for p in found), found)
        self.assertTrue(any("room 54 " in p and "description" in p for p in found), found)

    def test_a_changed_refusal_message_is_reported(self) -> None:
        ir = self.broken()
        ir["phrases"]["locales"]["en-US"]["drown-yourself"]["variants"][0]["text"] = "You would drown."
        self.assertTrue(any("drown-yourself" in p for p in self.problems(ir)))

    def test_a_missing_room_is_reported(self) -> None:
        ir = self.broken()
        ir["entities"] = [e for e in ir["entities"] if e["name"] != "Room 85"]
        found = self.problems(ir)
        self.assertTrue(any("86 rooms" in p for p in found), found)
        self.assertTrue(any(p.startswith("room 85:") for p in found), found)

    def test_a_misplaced_object_is_reported(self) -> None:
        ir = self.broken()
        self.entity(ir, "electric lamp")["placement"]["place"] = "basement"
        self.entity(ir, "ancient statue")["placement"] = {"relation": "in", "place": "building"}
        found = self.problems(ir)
        self.assertTrue(any("object 17 " in p and "starts in basement" in p for p in found), found)
        self.assertTrue(any("object 3 " in p and "starts in building" in p for p in found), found)

    def test_a_takeable_fixture_and_a_fixed_treasure_are_reported(self) -> None:
        ir = self.broken()
        self.entity(ir, "robot")["traits"] = []
        self.entity(ir, "penny")["traits"].append({"name": "scenery"})
        found = self.problems(ir)
        self.assertTrue(any("object 41 " in p and "scenery" in p for p in found), found)
        self.assertTrue(any("object 30 " in p and "scenery" in p for p in found), found)

    def test_a_lost_word_is_reported(self) -> None:
        """LEASH names the rat in the 1979 source (O-1); losing it is a fix."""
        ir = self.broken()
        self.entity(ir, "rat")["aka"].remove("leash")
        self.assertTrue(any("object 31 " in p and "LEASH" in p for p in self.problems(ir)))

    def test_changed_and_ungated_presence_lines_are_reported(self) -> None:
        ir = self.broken()
        phrases = ir["phrases"]["locales"]["en-US"]
        phrases["minuature-sun.present"]["variants"][0]["text"] = "There is a miniature sun here."
        phrases["electric-lamp.present"]["variants"][0]["text"] = "A lamp sits here."
        del phrases["rock.present"]["condition"]
        found = self.problems(ir)
        self.assertTrue(any("object 24 " in p and "presence line" in p for p in found), found)
        self.assertTrue(any("object 17 " in p and "none of the original's" in p for p in found), found)
        self.assertTrue(any("object 21 " in p and "held" in p for p in found), found)


class ScaffoldRefuses(unittest.TestCase):
    def test_existing_files_are_not_overwritten_without_force(self) -> None:
        """REJECTS WHEN: story files exist and --force is absent. The file on
        disk must be untouched afterwards."""
        target = REPO / "story" / "surface.chord"
        before = target.read_bytes()
        self.assertEqual(scaffold_world.main([]), 1)
        self.assertEqual(target.read_bytes(), before)

    def test_a_room_filed_nowhere_is_rejected(self) -> None:
        world = json.loads(world_parity.WORLD_PATH.read_text())
        names = json.loads(world_parity.MAP_PATH.read_text())
        names["rooms"]["88"] = "Room 88"
        with self.assertRaises(ValueError) as caught:
            scaffold_world.render_files(world, names)
        self.assertIn("88", str(caught.exception))

    def test_a_maze_room_that_differs_cannot_join_the_group(self) -> None:
        world = json.loads(world_parity.WORLD_PATH.read_text())
        names = {int(k): v for k, v in json.loads(world_parity.MAP_PATH.read_text())["rooms"].items()}
        world["rooms"]["65"]["name"] = "A different passage"
        with self.assertRaises(ValueError) as caught:
            scaffold_world.maze_file(world, names)
        self.assertIn("room 65", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
