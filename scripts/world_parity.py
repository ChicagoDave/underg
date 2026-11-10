"""Hold the compiled Chord world to the decoded 1979 world.

Purpose: compare a Story IR (what `sharpee compose` makes of `story/`) with
`extracted/world.json`, room by room and object by object, and list every
difference in the terms of the original (room 16, object 31).

Public interface: `compare(world, names, ir) -> list[str]` (empty means parity),
`compile_story() -> dict` (runs the real compiler), and
`python3 scripts/world_parity.py` as a command, exit code 1 on any difference.

Owner context: Phase 3 acceptance instrument for the content port. It reads
world state only: rooms, exits, refusals, placements, names and text. Behaviour
is the oracle transcripts' business (Phases 6 and 7).
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WORLD_PATH = REPO / "extracted" / "world.json"
MAP_PATH = REPO / "story" / "world-map.json"
STORY_PATH = REPO / "story" / "underg.story"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scaffold_world import PASSAGE_COLUMNS, REFUSAL_KEYS  # noqa: E402

# The two exits whose destination is computed (mapping.md G3 and G4). They have
# no declarative form, so the world files leave them out until Phase 4, and
# this list is what "left out on purpose" means. Anything else missing is a
# defect.
UNAUTHORED_SPECIALS = {(54, "southeast"), (60, "west")}


def _direction_key(column: str) -> str:
    return f"passage:{column}" if column in PASSAGE_COLUMNS else column


def _text(phrases: dict, key: str | None) -> str | None:
    if key is None or key not in phrases:
        return None
    return phrases[key]["variants"][0]["text"]


def _joined(lines: list[str]) -> str | None:
    """A printed block as Chord stores it: lines trimmed, joined by hard breaks."""
    return "{br} ".join(line.strip() for line in lines) if lines else None


def compare(world: dict, names: dict, ir: dict) -> list[str]:
    """Return one line per difference between the decode and the compiled story.

    `world` is extracted/world.json, `names` is story/world-map.json, `ir` is
    the compiler's Story IR. Never raises on a mismatch; a missing entity is
    reported and its remaining checks skipped.
    """
    problems: list[str] = []
    by_name = {entity["name"]: entity for entity in ir["entities"]}
    phrases = ir["phrases"]["locales"][ir["phrases"]["defaultLocale"]]
    room_names = {int(k): v for k, v in names["rooms"].items()}
    object_names = {int(k): v for k, v in names["objects"].items()}
    room_ids = {number: by_name[name]["id"] for number, name in room_names.items() if name in by_name}

    def kinds(entity: dict) -> set[str]:
        return {kind["name"] for kind in entity["kinds"]}

    rooms_in_ir = [e for e in ir["entities"] if "room" in kinds(e)]
    if len(rooms_in_ir) != len(world["rooms"]):
        problems.append(f"the story has {len(rooms_in_ir)} rooms, the decode has {len(world['rooms'])}")

    seen_specials: set[tuple[int, str]] = set()
    for key, room in world["rooms"].items():
        number = int(key)
        entity = by_name.get(room_names[number])
        if entity is None or "room" not in kinds(entity):
            problems.append(f"room {number}: no room named '{room_names[number]}'")
            continue
        where = f"room {number} ({entity['name']})"

        want_name = room["name"].strip() if room["name"] else None
        got_name = _text(phrases, f"{entity['id']}.room-name")
        if got_name != want_name:
            problems.append(f"{where}: room name is {got_name!r}, the original prints {want_name!r}")

        want_text = _joined(room["description"])
        got_text = _text(phrases, entity["descriptionKey"])
        if got_text != want_text:
            problems.append(f"{where}: description is {got_text!r}, the original prints {want_text!r}")

        want_exits = {(_direction_key(d), room_ids.get(t)) for d, t in room["exits"].items()}
        want_blocked: dict[str, str] = {}
        want_deadly: dict[str, str] = {}
        for direction, refusal in room["refusals"].items():
            if refusal["kind"] == "special":
                seen_specials.add((number, direction))
                continue
            target = want_deadly if refusal["kind"] == "deadly" else want_blocked
            target[_direction_key(direction)] = REFUSAL_KEYS[refusal["code"]]
            if direction in PASSAGE_COLUMNS:
                # A refused passage names its own room as its destination.
                want_exits.add((_direction_key(direction), entity["id"]))

        got_exits = {(e["direction"], e["to"]["id"]) for e in entity["exits"]}
        for direction, target in sorted(want_exits - got_exits, key=str):
            problems.append(f"{where}: missing exit {direction} to {target}")
        for direction, target in sorted(got_exits - want_exits, key=str):
            problems.append(f"{where}: exit {direction} to {target} is not in the original")
        for exit_ in entity["exits"]:
            if "passage" not in exit_ and not exit_.get("oneWay"):
                problems.append(f"{where}: exit {exit_['direction']} is two-way; every 1979 exit is one-way")

        got_blocked = {b["direction"]: b["phraseKey"] for b in entity["blockedExits"]}
        got_deadly = {d["direction"]: d["phraseKey"] for d in entity["deadlyExits"]}
        if got_blocked != want_blocked:
            problems.append(f"{where}: blocked exits are {got_blocked}, the original has {want_blocked}")
        if got_deadly != want_deadly:
            problems.append(f"{where}: deadly exits are {got_deadly}, the original has {want_deadly}")
        for refusal in room["refusals"].values():
            if refusal["message"] and _text(phrases, REFUSAL_KEYS[refusal["code"]]) != refusal["message"]:
                problems.append(f"{where}: phrase {REFUSAL_KEYS[refusal['code']]} is not {refusal['message']!r}")

    if seen_specials != UNAUTHORED_SPECIALS:
        problems.append(f"computed exits are {sorted(seen_specials)}, expected {sorted(UNAUTHORED_SPECIALS)}")

    for key, obj in world["objects"].items():
        number = int(key)
        entity = by_name.get(object_names[number])
        if entity is None or "thing" not in kinds(entity):
            problems.append(f"object {number}: no thing named '{object_names[number]}'")
            continue
        where = f"object {number} ({entity['name']})"

        want_place = room_ids.get(obj["start_room"]) if obj["start_room"] > 0 else None
        got_place = entity["placement"]["place"] if entity["placement"] else None
        if got_place != want_place:
            problems.append(f"{where}: starts in {got_place}, the original starts it in {want_place}")

        fixture = number >= 33
        if fixture != any(trait["name"] == "scenery" for trait in entity["traits"]):
            problems.append(f"{where}: scenery is wrong; objects 33 to 45 are fixtures and no others")

        for word in obj["vocabulary"]:
            if word.lower() != entity["name"].lower() and word.lower() not in entity["aka"]:
                problems.append(f"{where}: does not answer to {word}")

        present = phrases.get(f"{entity['id']}.present")
        got_text = present["variants"][0]["text"] if present else None
        if obj["needs_review"]:
            allowed = {s for review in obj["needs_review"] for s in review["strings"]} | {None}
            if got_text not in allowed:
                problems.append(f"{where}: presence line {got_text!r} is none of the original's {sorted(a for a in allowed if a)}")
        else:
            want_text = obj["presence"][0] if obj["presence"] else None
            if got_text != want_text:
                problems.append(f"{where}: presence line is {got_text!r}, the original prints {want_text!r}")
        if present and fixture == ("condition" in present):
            problems.append(f"{where}: a carried thing's presence line must stop while it is held, a fixture's never does")

    return problems


def compile_story(story: Path = STORY_PATH) -> dict:
    """Compile the story with the installed Chord compiler and return its IR.

    Raises RuntimeError, carrying the compiler's diagnostics, if the story does
    not pass the load-time gates.
    """
    with tempfile.TemporaryDirectory() as scratch:
        out = Path(scratch) / "story.ir.json"
        result = subprocess.run(
            ["npx", "sharpee", "compose", str(story), "-o", str(out)],
            cwd=REPO, capture_output=True, text=True,
        )
        if result.returncode != 0 or not out.exists():
            raise RuntimeError(f"sharpee compose failed:\n{result.stdout}{result.stderr}")
        return json.loads(out.read_text())


def main() -> int:
    """Compile the story, compare, print each difference. Returns 1 on any."""
    problems = compare(json.loads(WORLD_PATH.read_text()), json.loads(MAP_PATH.read_text()), compile_story())
    for line in problems:
        print(line)
    print(f"world_parity: {len(problems)} difference(s)" if problems else "world_parity: OK - 87 rooms and 45 objects match the decode")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
