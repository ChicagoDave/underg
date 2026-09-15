#!/usr/bin/env python3
"""Decode UNDERGROUND V1's world out of the 1979 BASIC-PLUS source into JSON.

The 1979 game keeps its entire world in two tables rather than in code, which is
what makes this port tractable. `UNDERG.BAS` line 70 does `MAT READ M%,O%` over
`DIM M%(87,14), O%(45)`, so the DATA block is 87 rooms x 14 exit columns
followed by 45 object start locations - 1263 values, no more and no less.
`LOOK.BAS` is a second table keyed by line number: `room*100` holds a room's
long description and `room*100+50` its short name, which is how line 990's
`R%=100%*X%(0%) : R%=R%+50% IF M%(X%(0%),0%)` picks between them.

This module reads both and emits one JSON document describing the world, so
Phases 3-4 author Chord against decoded data rather than against BASIC.

Public interface: `extract_world(underg_path, look_path)` returns the world as a
dict; `main()` writes it to disk. Everything else is internal.

Owner context: the port's extraction tooling - it reads the vendored 1979
sources under `original/` and never writes to them.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# UNDERG.BAS lines 1020-1150 define exactly fourteen movement words, setting
# Y%=1..14, and M%(room, Y%) is that direction's destination. So the matrix's
# fourteen columns ARE these directions, in this order. DOOR and BARRE (barrier)
# are pseudo-directions the player types as nouns.
DIRECTIONS = [
    "north", "east", "west", "south",
    "northeast", "northwest", "southeast", "southwest",
    "up", "down", "in", "out",
    "door", "barrier",
]

ROOM_COUNT = 87
EXIT_COLUMNS = 14
OBJECT_COUNT = 45
EXPECTED_VALUES = ROOM_COUNT * EXIT_COLUMNS + OBJECT_COUNT  # 1263

# A non-positive exit value is dispatched by line 2870's
# `ON 1%-X% goto 2880,2890,2900,2905,2910,2920,2930,2940,2950,2960,3090`,
# so the code is an index into that jump list, not a room. Three kinds live in
# here and they need different Chord treatments, which is why `kind` is decoded
# rather than left for Phase 3 to infer from the message:
#   refuse   - print and stay put (Chord: `<dir> is blocked: <phrase>`)
#   deadly   - print and die (Chord: a deadly exit)
#   special  - neither; the destination is computed. No declarative form exists.
EXIT_CODES = {
    0:   ("refuse",  "You can't move in that direction.",
          "No exit. The default arm of line 2870."),
    -1:  ("refuse",  "The door is closed.", None),
    -2:  ("refuse",  "I wouldn't advise you to drown yourself.", None),
    -3:  ("refuse",  "You can't get up the ramp.", None),
    -4:  ("refuse",  "The barrel's spinning motion prevents you from moving this way.", None),
    -5:  ("refuse",  "You cannot reach the hole.", None),
    -6:  ("deadly",  "You are on the surface on the planet, which has an atmosphere of cyanide gas.", None),
    -7:  ("refuse",  "This passage has been somehow blocked.",
          "Also written at run time: line 2070 sets this code on the exit you just used when leaving room 58."),
    -8:  ("deadly",  "You are INSIDE an active volcano. Lava flies about in all directions.", None),
    -9:  ("special", None,
          "Line 2960 draws a random room 1-85 that the player has already visited and moves them there."),
    -10: ("special", None,
          "Line 3090 gates on score: above 380 points the destination is room 86, otherwise the woman "
          "ends the game outright."),
}

# A numbered BASIC line: `880 DATA,8,,,` or `850 &"Outside building":goto10000`.
LINE_RE = re.compile(r"^(\d+)\s*(.*)$")
DATA_RE = re.compile(r"^DATA(.*)$", re.IGNORECASE)
# `&"text"` and `&'text'` both occur - line 10201 uses single quotes because its
# text contains a quoted phrase.
PRINT_RE = re.compile(r"&\s*(\"([^\"]*)\"|'([^']*)')")
GOTO_ONLY_RE = re.compile(r"^goto\s*(\d+)$", re.IGNORECASE)
# LOOK.BAS room lines run 100..8750; 10000 upward is the object sweep every
# room description jumps to when it is done. So `goto10000` TERMINATES a room
# line, and following it would give that room the object table's first line.
# Room 85 is exactly this shape - `8500 !` falling through to `8550 goto10000` -
# and has no description of its own in the source (see O-7).
OBJECT_TABLE_START = 10000


def _numbered_lines(path: Path) -> dict[int, str]:
    """Read a BASIC source file into {line number: statement text}.

    Unnumbered lines (the reconstruction notes' `!` comment banners) are
    skipped; they are annotation, not program text. Returns an empty dict for an
    empty file rather than raising, so a caller can report the gap itself.
    """
    out: dict[int, str] = {}
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("!"):
            continue
        match = LINE_RE.match(stripped)
        if match:
            out[int(match.group(1))] = match.group(2).strip()
    return out


def read_data_values(underg_path: Path) -> list[int]:
    """Flatten UNDERG.BAS's DATA block into the value stream MAT READ consumes.

    Empty fields are real data meaning zero - `DATA,8,,,,` supplies a 0, an 8,
    then three more 0s - so they are preserved, not skipped. Raises ValueError if
    the stream is not exactly 1263 values, because a miscount silently shifts
    every room after the error (the defect check_data.py was written to catch).
    """
    values: list[int] = []
    for number, text in sorted(_numbered_lines(underg_path).items()):
        match = DATA_RE.match(text)
        if not match:
            continue
        for field in match.group(1).split(","):
            field = field.strip()
            values.append(int(field) if field else 0)

    if len(values) != EXPECTED_VALUES:
        raise ValueError(
            f"DATA block holds {len(values)} values, expected {EXPECTED_VALUES} "
            f"({ROOM_COUNT}x{EXIT_COLUMNS} rooms + {OBJECT_COUNT} objects)"
        )
    return values


def _resolve_text(lines: dict[int, str], number: int, seen: frozenset[int] = frozenset()) -> list[str]:
    """Return the printed strings at a LOOK.BAS line, following fall-through.

    Two forms of sharing exist in the original and both must be followed or
    rooms come out blank. A line that is only `goto NNN` delegates wholesale -
    room 6 is `600 goto700`, borrowing room 7's text. A line with no print at
    all falls through to the next numbered line, which is the author's trick
    that makes the 61-71 maze share one description.

    `seen` guards against a cycle in a malformed source rather than recursing
    until the stack dies.
    """
    if number in seen or number not in lines:
        return []

    text = lines[number]
    delegate = GOTO_ONLY_RE.match(text)
    if delegate:
        target = int(delegate.group(1))
        if target >= OBJECT_TABLE_START:
            return []
        return _resolve_text(lines, target, seen | {number})

    printed = [m.group(2) if m.group(2) is not None else m.group(3) for m in PRINT_RE.finditer(text)]
    if printed:
        return printed

    following = [n for n in sorted(lines) if n > number]
    if following:
        return _resolve_text(lines, following[0], seen | {number})
    return []


# `IFA$="WIRE"ORA$="COIL"ORA$="PLATI"THENT%=1%` - one vocabulary line may give an
# object several words. `THENT%=` is what marks the line as a noun binding;
# lines 1940-1970 quote words with no T% assignment (the swearing replies) and
# are deliberately not vocabulary.
VOCAB_ID_RE = re.compile(r"THENT%\s*=\s*(-?\d+)%", re.IGNORECASE)
VOCAB_WORD_RE = re.compile(r"A\$\s*=\s*\"([^\"]*)\"", re.IGNORECASE)
# `O%(17%)` in a condition names an object. `O%(45)` without the inner `%` is
# the DIM statement's bound, not a reference, so the trailing `%` is required.
OBJECT_REF_RE = re.compile(r"O%\((\d+)%\)", re.IGNORECASE)
# A `then` on the line means its prints are branch arms, not postfix conditions.
BRANCHING_RE = re.compile(r"\bthen\b", re.IGNORECASE)


def read_vocabulary(underg_path: Path) -> dict[int, list[str]]:
    """Map each object id to the words the 1979 parser accepts for it.

    Words are returned exactly as the source spells them, truncated to five
    characters as the original truncates them (`PLATI`, `BOTTL`, `SUNGL`) -
    lengthening them to real English would change what the parser accepts.
    Object 0 (ME) is included. Two different ids may share a word, and one id
    may appear on two lines; both are preserved rather than deduplicated away,
    because a collision is a finding (see O-1 in original-issues.md), not noise.
    """
    vocabulary: dict[int, list[str]] = {}
    for _, text in sorted(_numbered_lines(underg_path).items()):
        id_match = VOCAB_ID_RE.search(text)
        if not id_match:
            continue
        object_id = int(id_match.group(1))
        words = VOCAB_WORD_RE.findall(text)
        vocabulary.setdefault(object_id, []).extend(words)
    return vocabulary


def _paired_strings(text: str) -> tuple[list[tuple[int, str]], list[str], bool]:
    """Pair the printed strings on a line with the object ids they test.

    The ordinary form interleaves them - `&"a"ifO%(1%)=x%:&"b"ifO%(2%)=x%` - so
    equal counts can be zipped positionally. Lines that branch on state break
    that shape (`ifO%(17%)=x%thenifx%(5%)then&"lit"else&"unlit"` is one id and
    two strings), so those are returned unpaired with a review flag rather than
    guessed at. Returns (pairs, unpaired strings, needs_review).
    """
    ids = [int(n) for n in OBJECT_REF_RE.findall(text)]
    strings = [m.group(2) if m.group(2) is not None else m.group(3) for m in PRINT_RE.finditer(text)]
    # Equal counts are NOT sufficient. Line 10180 is
    # `ifo%(18%)=x%thenifo%(19%)=x%then&"bottle of water"else&"empty bottle"`:
    # two ids, two strings, and positional zipping silently hands the empty
    # bottle to object 19 (the water) when both strings describe object 18. A
    # `then` anywhere on the line means the prints are branch arms rather than
    # postfix conditions, so the shape does not hold.
    if BRANCHING_RE.search(text):
        return [], strings, bool(ids)
    if ids and len(ids) == len(strings):
        return list(zip(ids, strings)), [], False
    return [], strings, bool(ids)


def read_object_text(underg_path: Path, look_path: Path) -> dict[int, dict]:
    """Collect each object's inventory name and its on-the-floor presence line.

    Two tables hold these and neither is addressable by object id directly.
    `UNDERG.BAS` 1241-1246 prints the carried name (`&"Electric lamp."`) and
    `LOOK.BAS` 10000-10500 prints the in-room line (`&"There is an electric lamp
    here."`), both as postfix-conditional prints keyed on `O%(n%)`.

    An entry whose `needs_review` is true sits on a line that branches on world
    state - the lamp's lit/unlit pair, the bottle's full/empty pair - and its
    strings are returned unassigned, with the source line, for a human to split.
    """
    entries: dict[int, dict] = {}

    def slot(object_id: int) -> dict:
        return entries.setdefault(object_id, {
            "id": object_id, "inventory_name": None, "presence": [],
            "needs_review": [], "vocabulary": [],
        })

    for number, text in sorted(_numbered_lines(underg_path).items()):
        if not 1240 <= number <= 1250:
            continue
        pairs, loose, review = _paired_strings(text)
        for object_id, string in pairs:
            slot(object_id)["inventory_name"] = string
        if review:
            for object_id in {int(n) for n in OBJECT_REF_RE.findall(text)}:
                slot(object_id)["needs_review"].append({"line": number, "source": text, "strings": loose})

    for number, text in sorted(_numbered_lines(look_path).items()):
        if number < 10000:
            continue
        pairs, loose, review = _paired_strings(text)
        for object_id, string in pairs:
            slot(object_id)["presence"].append(string)
        if review:
            for object_id in {int(n) for n in OBJECT_REF_RE.findall(text)}:
                slot(object_id)["needs_review"].append({"line": number, "source": text, "strings": loose})

    for object_id, words in read_vocabulary(underg_path).items():
        slot(object_id)["vocabulary"] = words

    return entries


def extract_world(underg_path: Path, look_path: Path) -> dict:
    """Decode both source files into one world document.

    Returns a dict with `rooms` (87 entries, each carrying its exits by
    direction name plus its long and short text) and `objects` (45 entries,
    each carrying its starting room). An exit value of 0 means no exit; a
    negative value is decoded through EXIT_CODES into a `refusals` entry
    carrying the message the original prints and whether it refuses, kills, or
    computes a destination.
    """
    values = read_data_values(underg_path)
    look = _numbered_lines(look_path)

    rooms = {}
    for room in range(1, ROOM_COUNT + 1):
        base = (room - 1) * EXIT_COLUMNS
        row = values[base:base + EXIT_COLUMNS]
        exits = {}
        refusals = {}
        for direction, target in zip(DIRECTIONS, row):
            if target > 0:
                exits[direction] = target
            elif target < 0:
                kind, message, note = EXIT_CODES[target]
                refusals[direction] = {
                    "code": target, "kind": kind, "message": message, "note": note,
                }
        long_text = _resolve_text(look, room * 100)
        short_text = _resolve_text(look, room * 100 + 50)
        rooms[room] = {
            "id": room,
            "name": short_text[0] if short_text else None,
            "description": long_text,
            "exits": exits,
            "refusals": refusals,
        }

    text_by_object = read_object_text(underg_path, look_path)
    objects = {}
    object_base = ROOM_COUNT * EXIT_COLUMNS
    for index in range(1, OBJECT_COUNT + 1):
        entry = dict(text_by_object.get(index, {"id": index}))
        entry["start_room"] = values[object_base + index - 1]
        entry.setdefault("inventory_name", None)
        entry.setdefault("presence", [])
        entry.setdefault("vocabulary", [])
        entry.setdefault("needs_review", [])
        objects[index] = entry

    return {
        "source": {"underg": underg_path.name, "look": look_path.name},
        "counts": {"rooms": len(rooms), "objects": len(objects), "data_values": len(values)},
        "directions": DIRECTIONS,
        "rooms": rooms,
        "objects": objects,
    }


def main() -> int:
    """Write the decoded world to extracted/world.json and report a summary.

    Overwrites the output file. Returns 0 on success, 1 if either source file is
    missing or the DATA block fails its size check.
    """
    repo = Path(__file__).resolve().parent.parent
    underg_path = repo / "original" / "UNDERG.BAS"
    look_path = repo / "original" / "LOOK.BAS"
    out_path = repo / "extracted" / "world.json"

    for path in (underg_path, look_path):
        if not path.exists():
            print(f"extract_world: missing source {path}", file=sys.stderr)
            return 1

    try:
        world = extract_world(underg_path, look_path)
    except ValueError as exc:
        print(f"extract_world: {exc}", file=sys.stderr)
        return 1

    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps(world, indent=2) + "\n", encoding="utf-8")

    unnamed = [r for r, v in world["rooms"].items() if not v["name"]]
    undescribed = [r for r, v in world["rooms"].items() if not v["description"]]
    print(f"extract_world: wrote {out_path.relative_to(repo)}")
    print(f"  rooms {world['counts']['rooms']}, objects {world['counts']['objects']}, "
          f"data values {world['counts']['data_values']}")
    print(f"  rooms without a short name: {unnamed or 'none'}")
    print(f"  rooms without a description: {undescribed or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
