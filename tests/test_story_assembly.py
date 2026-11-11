"""Tests for the Phase 5 assembly: identity, ledger, and the imports.

Purpose: prove that the assembled story compiles carrying the IFID its config
owns, that its header ledger accounts for every recorded deviation, and that
the instrument saying so reports each kind of drift.

Public interface: run with `python3 -m unittest discover -s tests`.

Owner context: Phase 5 acceptance. `TheAssembledStory` drives the real Chord
compiler over the real story files (no stub). `AssemblyCheckBites` hands the
checker one known defect at a time and asserts it names the defect.
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import story_assembly  # noqa: E402
import world_parity  # noqa: E402

GOOD_IFID = "D44A0572-6535-4D0B-92C7-35BDCF1192C0"
GOOD_CONFIG = '{\n  "ifid": "%s",\n  "version": 1\n}\n' % GOOD_IFID
STORY = "## L-1. one\n## L-2. two\n##   O-1 corrected  O-2 restored\n\nstory\n  id: x\n  ifid: %s\n" % GOOD_IFID
DRAFT = "**L-1. One.** text\n\n**L-2. Two.** text\n"
ISSUES = (
    "## O-1 - a\n\n**Disposition: CORRECTED** (2026)\n\n"
    "## O-2 - b\n\n**Disposition: RESTORED-UPSTREAM**\n\n"
    "## O-3 - c\n\n**Disposition: REPRODUCE**\n"
)


class TheAssembledStory(unittest.TestCase):
    def test_the_repository_passes_its_own_check(self) -> None:
        self.assertEqual(story_assembly.check(), [])

    def test_the_compiled_story_carries_the_configs_ifid(self) -> None:
        """The compiler's own reading of the identity, not a reading of the header text."""
        compiled = world_parity.compile_story()["meta"]["fields"].get("ifid")
        self.assertRegex(compiled or "", r"^[0-9A-F]{8}(-[0-9A-F]{4}){3}-[0-9A-F]{12}$")
        self.assertEqual(story_assembly.identity_problems(compiled, story_assembly.CONFIG_PATH.read_text()), [])

    def test_every_story_file_is_imported_once_and_phrases_come_before_verbs(self) -> None:
        text = story_assembly.STORY_PATH.read_text()
        imported = re.findall(r'^import "([^"]+)"$', text, re.MULTILINE)
        on_disk = sorted(path.stem for path in story_assembly.STORY_PATH.parent.glob("*.chord"))
        self.assertEqual(sorted(imported), on_disk)
        self.assertLess(imported.index("phrases"), imported.index("verbs"))

    def test_the_player_is_assigned_before_the_game_starts(self) -> None:
        ir = world_parity.compile_story()
        adventurer = next(e for e in ir["identity"]["entities"] if e["id"] == "adventurer")
        self.assertEqual((adventurer["kind"], adventurer["startsIn"]), ("person", "outside-building"))
        self.assertIn("adventurer", str(ir["startBlock"]).lower())


class AssemblyCheckBites(unittest.TestCase):
    def test_a_clean_story_has_no_problems(self) -> None:
        self.assertEqual(story_assembly.identity_problems(GOOD_IFID, GOOD_CONFIG), [])
        self.assertEqual(story_assembly.ledger_problems(STORY, DRAFT, ISSUES), [])
        self.assertEqual(story_assembly.header_ifid(STORY), GOOD_IFID)

    def test_a_story_with_another_ifid_is_named(self) -> None:
        other = "00000000-0000-0000-0000-000000000000"
        self.assertEqual(
            story_assembly.identity_problems(other, GOOD_CONFIG),
            [f"the story's ifid {other} is not the config's {GOOD_IFID}"],
        )

    def test_a_story_with_no_ifid_is_named(self) -> None:
        self.assertIsNone(story_assembly.header_ifid("story\n  id: x\n"))
        self.assertEqual(story_assembly.identity_problems(None, GOOD_CONFIG), ["the story carries no ifid"])

    def test_a_broken_config_is_named(self) -> None:
        self.assertEqual(len(story_assembly.identity_problems(GOOD_IFID, "{")), 1)
        self.assertIn("not JSON", story_assembly.identity_problems(GOOD_IFID, "{")[0])
        self.assertEqual(story_assembly.identity_problems(GOOD_IFID, "[]"), ["the config is not a JSON object"])
        self.assertEqual(
            story_assembly.identity_problems(GOOD_IFID, GOOD_CONFIG.replace('"version": 1', '"version": 2')),
            ["the config's version is 2, not 1"],
        )

    def test_an_ifid_that_is_not_a_uuid_is_named(self) -> None:
        problems = story_assembly.identity_problems("not-an-ifid", '{"ifid": "not-an-ifid", "version": 1}')
        self.assertEqual(problems, ["the config's ifid 'not-an-ifid' is not an upper-case UUID"])

    def test_a_deviation_missing_from_the_header_is_named(self) -> None:
        self.assertEqual(
            story_assembly.ledger_problems(STORY, DRAFT + "\n**L-3. Three.** text\n", ISSUES),
            ["L-3 is in the draft and not in the story header"],
        )

    def test_a_deviation_missing_from_the_draft_is_named(self) -> None:
        self.assertEqual(
            story_assembly.ledger_problems(STORY, DRAFT.replace("**L-2. Two.** text\n", ""), ISSUES),
            ["L-2 is in the story header and not in the draft"],
        )

    def test_a_corrected_slip_missing_from_the_header_is_named(self) -> None:
        more = ISSUES + "\n## O-4 - d\n\n**Disposition: CORRECTED** (in the port only)\n"
        self.assertEqual(
            story_assembly.ledger_problems(STORY, DRAFT, more), ["O-4 is CORRECTED and not in the story header"]
        )

    def test_a_number_below_the_story_block_does_not_count(self) -> None:
        """Only the header comment is the ledger; a mention in a body comment is not an entry."""
        moved = STORY.replace("## L-2. two\n", "") + "## L-2 is mentioned down here\n"
        self.assertEqual(
            story_assembly.ledger_problems(moved, DRAFT, ISSUES), ["L-2 is in the draft and not in the story header"]
        )


if __name__ == "__main__":
    unittest.main()
