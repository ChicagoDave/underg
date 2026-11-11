"""Check that the assembled story carries its identity and its whole ledger.

Purpose: hold `story/underg.story` to the two things Phase 5 gave it - the
IFID that `story/underg.config.json` owns, and a header ledger that names
every deviation the working notes and the O-register record.

Public interface: `identity_problems(header_ifid, config_text)`,
`ledger_problems(story_text, draft_text, issues_text)`, `header_ifid(story_text)`,
`check() -> list[str]` over the real files, and `python3
scripts/story_assembly.py` (exit 0 and "OK", or exit 1 and one line per
problem).

Owner context: Phase 5 acceptance tooling, beside `scripts/world_parity.py`.
Reads files only; changes nothing.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
STORY_PATH = REPO / "story" / "underg.story"
CONFIG_PATH = REPO / "story" / "underg.config.json"
WORK = REPO / "docs" / "work" / "port-underground-v1-chord"
DRAFT_PATH = WORK / "deviation-ledger-draft.md"
ISSUES_PATH = WORK / "original-issues.md"

_UUID = re.compile(r"^[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}$")
# Dispositions under which the port and the 14-Mar-79 listing differ, so the
# header must say so.
_LEDGERED_DISPOSITIONS = ("CORRECTED", "RESTORED-UPSTREAM")


def header_ifid(story_text: str) -> str | None:
    """Return the `ifid:` value of the story block, or None when it has none."""
    found = re.search(r"^  ifid:[ \t]*(\S+)[ \t]*$", story_text, re.MULTILINE)
    return found.group(1) if found else None


def identity_problems(story_ifid: str | None, config_text: str) -> list[str]:
    """Name every way the story's identity fails to be one well-formed IFID.

    `story_ifid` is what the story carries (its header line, or the compiled
    IR's `meta.fields.ifid`); `config_text` is the config file's contents.
    Returns an empty list when the config is valid JSON at version 1, its
    `ifid` is an upper-case UUID, and the story carries the same value.
    """
    try:
        config = json.loads(config_text)
    except json.JSONDecodeError as error:
        return [f"the config is not JSON: {error.msg}"]
    if not isinstance(config, dict):
        return ["the config is not a JSON object"]
    problems = []
    if config.get("version") != 1:
        problems.append(f"the config's version is {config.get('version')!r}, not 1")
    ifid = config.get("ifid")
    if not isinstance(ifid, str) or not _UUID.match(ifid):
        problems.append(f"the config's ifid {ifid!r} is not an upper-case UUID")
    if story_ifid is None:
        problems.append("the story carries no ifid")
    elif story_ifid != ifid:
        problems.append(f"the story's ifid {story_ifid} is not the config's {ifid}")
    return problems


def _header(story_text: str) -> str:
    """The comment lines above the `story` block, where the ledger lives."""
    lines = []
    for line in story_text.splitlines():
        if not line.startswith("##"):
            break
        lines.append(line)
    return "\n".join(lines)


def ledger_problems(story_text: str, draft_text: str, issues_text: str) -> list[str]:
    """Name every deviation recorded in one place and missing from the other.

    Compares the L numbers in the story's header comment with the `**L-n.`
    entries of the draft, both ways, and requires the header to name every
    O-register entry whose disposition is CORRECTED or RESTORED-UPSTREAM.
    Returns an empty list when the header accounts for all of them.
    """
    header = _header(story_text)
    in_header = {int(n) for n in re.findall(r"\bL-(\d+)\b", header)}
    in_draft = {int(n) for n in re.findall(r"^\*\*L-(\d+)\.", draft_text, re.MULTILINE)}
    problems = [f"L-{n} is in the draft and not in the story header" for n in sorted(in_draft - in_header)]
    problems += [f"L-{n} is in the story header and not in the draft" for n in sorted(in_header - in_draft)]
    named = {int(n) for n in re.findall(r"\bO-(\d+)\b", header)}
    for number, disposition in re.findall(
        r"^## O-(\d+)\b[^\n]*\n+\*\*Disposition: ([A-Z-]+)", issues_text, re.MULTILINE
    ):
        if disposition in _LEDGERED_DISPOSITIONS and int(number) not in named:
            problems.append(f"O-{number} is {disposition} and not in the story header")
    return problems


def check() -> list[str]:
    """Run both checks over the repository's own files and return the problems."""
    story_text = STORY_PATH.read_text()
    if not CONFIG_PATH.exists():
        return [f"{CONFIG_PATH.name} does not exist"]
    return identity_problems(header_ifid(story_text), CONFIG_PATH.read_text()) + ledger_problems(
        story_text, DRAFT_PATH.read_text(), ISSUES_PATH.read_text()
    )


if __name__ == "__main__":
    found = check()
    for problem in found:
        print(f"story_assembly: {problem}")
    if not found:
        print("story_assembly: OK - one IFID in config and story; the header ledger matches the draft and the O-register")
    sys.exit(1 if found else 0)
