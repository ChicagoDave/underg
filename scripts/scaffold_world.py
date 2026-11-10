"""Write the first draft of UNDERGROUND's world as Chord source, from the decode.

Purpose: turn `extracted/world.json` (87 rooms, 45 objects) into the per-region
`.chord` files under `story/`, so no room, exit or placement is retyped by hand.

Public interface: `python3 scripts/scaffold_world.py [--force]`, and the pure
functions `room_block`, `maze_file`, `object_block` and `render_files`.

Owner context: Phase 3 tooling. This is a scaffold, not a build step. Once the
files exist they are edited by hand (Phase 4 adds behaviour to them), so the
script refuses to overwrite them without `--force`. What keeps the files honest
afterwards is `tests/test_world_parity.py`, which compiles the story and holds
the result to the decode.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WORLD_PATH = REPO / "extracted" / "world.json"
MAP_PATH = REPO / "story" / "world-map.json"
STORY_DIR = REPO / "story"

# Which file each room is written to. The grouping follows the map's own
# geography; it is a filing decision and compiles to nothing.
REGION_FILES: dict[str, tuple[str, list[int]]] = {
    "surface": ("The surface: the building, the forest paths and the lake.", [*range(1, 10)]),
    "tunnels": ("The tunnels under the cave mouth, down to the bog and the ramp.", [10, 11, *range(15, 24)]),
    "mine": ("The abandoned mine.", [*range(24, 29)]),
    "spaceport": ("The ancient spaceport, the spaceship and where it lands.", [13, 14, *range(29, 33)]),
    "barrel": ("The elevator, the sphere room and the spinning barrel.", [*range(33, 41), 77]),
    "chasm": ("The volcano path, the chasm and the rooms beyond it.", [12, *range(41, 49)]),
    "dwarf-city": ("The city of the dwarfs and the well.", [*range(49, 53)]),
    "ancient-city": ("The ancient city, its vault, and the rooms past the space warp.", [*range(53, 61), 85, 86, 87]),
    "gnome-city": ("The City of Gnome.", [*range(78, 85)]),
}
START_ROOM = 8
MAZE_ROOMS = range(61, 72)
DEAD_END_ROOMS = range(72, 77)

# Line 3051-3052 of UNDERG.BAS draws this split itself: treasures drop where you
# die, carryables go back to room 1, and the rest never move.
OBJECT_FILES: dict[str, tuple[str, range]] = {
    "treasures": ("Objects 1 to 15, the treasures.", range(1, 16)),
    "carryables": ("Objects 16 to 32, the things that can be carried.", range(16, 33)),
    "fixtures": ("Objects 33 to 45, the fixtures and creatures. None can be carried.", range(33, 46)),
}

# The two pseudo-directions are typed as nouns and routed like compass moves.
PASSAGE_COLUMNS = ("door", "barrier")

# One phrase key per refusal code (UNDERG.BAS line 2870's dispatch).
REFUSAL_KEYS = {
    -1: "door-is-closed",
    -2: "drown-yourself",
    -3: "cant-get-up-ramp",
    -4: "barrel-spins",
    -5: "cannot-reach-hole",
    -6: "cyanide-atmosphere",
    -7: "passage-blocked",
    -8: "inside-volcano",
}

# The 1979 parser keeps five characters of a noun, so `PLATI` is what PLATINUM
# became. These are the whole words a player would type for each clipped one.
WHOLE_WORDS = {
    "PLATI": ["platinum"], "URANI": ["uranium"], "STATU": ["statue"], "NUGGE": ["nuggets", "nugget"],
    "RECOR": ["record"], "SILVE": ["silver"], "DIAMO": ["diamonds", "diamond"], "TELES": ["telescope"],
    "EMERA": ["emerald"], "STAMP": ["stamps"], "SUNGL": ["sunglasses"], "GLASS": ["glasses"],
    "PISTO": ["pistol"], "CONTA": ["container"], "GLOVE": ["gloves"], "BUTTO": ["button"],
    "CHEES": ["cheese"], "BOTTL": ["bottle"], "PERSO": ["person"], "FEMAL": ["female"],
    "MESSA": ["message"], "SWITC": ["switch"], "COMPU": ["computer"],
}

# Seven objects print a different line by state. Chord allows a thing one
# `phrase present:` block, so each gets the line it shows when the game starts;
# the other line is Phase 4's, and is named in a comment on the block.
STARTING_PRESENCE = {
    8: ("There is silver here!", 'in room 80 it is "There is silver in the safe!"'),
    17: ("There is an electric lamp here.", 'lit, it is "There is a lit lamp here."'),
    18: ("There is a bottle of water here.", 'without the water it is "There is an empty bottle here."'),
    19: (None, "the bottle's line speaks for it; it has none of its own"),
    31: ("There is a hungry rat here.", 'once fed it is "There is a dead rat here."'),
    32: ("There is a cat here.", 'once the rat is dead it is "there is a hungry cat here."'),
    33: ("There is a woman standing here.", None),
    34: ("The vault is closed.", 'opened, it is "The vault is open."'),
}

EXTRA_TRAITS = {17: ["switchable", "light-source"]}


def _the(name: str) -> str:
    return f"the {name}"


def _prose(lines: list[str], indent: str) -> list[str]:
    """Join printed lines with hard breaks, one source line per printed line.

    Leading and trailing spaces on a printed line are dropped: Chord trims them,
    so writing them would only suggest they survive.
    """
    stripped = [line.strip() for line in lines]
    return [f"{indent}{line}{{br}}" if i < len(stripped) - 1 else f"{indent}{line}" for i, line in enumerate(stripped)]


def _exit_terms(room: dict, room_names: dict[int, str]) -> list[str]:
    return [
        f"{direction} to {_the(room_names[target])}"
        for direction, target in room["exits"].items()
        if direction not in PASSAGE_COLUMNS
    ]


def room_block(room: dict, room_names: dict[int, str]) -> list[str]:
    """Render one room as a `create` block.

    Raises KeyError if an exit or refusal names a room or code the tables do
    not hold, so a decode change cannot be scaffolded silently.
    """
    number = room["id"]
    name = room_names[number]
    out = [f"## Room {number}. LOOK.BAS {number * 100} and {number * 100 + 50}.", "", f"create {_the(name)}", "  a room"]
    if room["name"]:
        out += ["  room name:", f"    {room['name'].strip()}"]

    terms = _exit_terms(room, room_names)
    if terms:
        out.append("  exits, one-way: " + ", ".join(terms))

    specials = []
    for direction, refusal in room["refusals"].items():
        if refusal["kind"] == "special":
            specials.append((direction, refusal))
        elif direction not in PASSAGE_COLUMNS:
            word = "deadly" if refusal["kind"] == "deadly" else "blocked"
            out.append(f"  {direction} is {word}: {REFUSAL_KEYS[refusal['code']]}")

    for column in PASSAGE_COLUMNS:
        if column in room["exits"]:
            out += ["", f"  passage to {_the(room_names[room['exits'][column]])}", "    grammar", f"      {column}", "  end passage"]
        elif column in room["refusals"]:
            # A refused passage still has to name a destination, so it names
            # its own room; the `blocked` line means it is never taken.
            key = REFUSAL_KEYS[room["refusals"][column]["code"]]
            out += ["", f"  passage to {_the(name)}", "    grammar", f"      {column}", f"    blocked: {key}", "  end passage"]

    if room["description"]:
        out += ["", *_prose(room["description"], "  ")]

    for direction, refusal in specials:
        out += ["", f"## Room {number}, {direction}: code {refusal['code']}, not authored here. {refusal['note']}"]
    return out


def maze_file(world: dict, room_names: dict[int, str]) -> list[str]:
    """Render rooms 61 to 76 as two room groups and one exit table."""
    rooms = world["rooms"]
    out = [
        "## The maze, rooms 61 to 76: eleven rooms that print the same line and",
        "## five dead ends. Each kind is declared once; the 1979 exits are a one-way",
        "## table, because the matrix gives no exit a way back.",
        "",
        "create the Maze",
        "  a region",
    ]
    for stem, numbers in (("Maze", MAZE_ROOMS), ("Dead End", DEAD_END_ROOMS)):
        first = rooms[str(numbers[0])]
        for number in numbers:
            other = rooms[str(number)]
            if (other["name"], other["description"], other["refusals"]) != (first["name"], first["description"], {}):
                raise ValueError(f"room {number} does not match its group; it cannot be declared with it")
        out += ["", f"  rooms {stem} {numbers[0]} to {numbers[-1]}", "    room name:", f"      {first['name'].strip()}", "", *_prose(first["description"], "    ")]
    out += ["", "  exits, one-way"]
    for number in (*MAZE_ROOMS, *DEAD_END_ROOMS):
        room = rooms[str(number)]
        if set(room["exits"]) & set(PASSAGE_COLUMNS):
            raise ValueError(f"room {number} has a door or barrier exit; a table row cannot carry one")
        out.append(f"    {_the(room_names[number])}: " + ", ".join(_exit_terms(room, room_names)))
    return out


def _aliases(obj: dict, name: str) -> list[str]:
    words: list[str] = []
    for word in obj["vocabulary"]:
        for alias in (word.lower(), *WHOLE_WORDS.get(word, [])):
            if alias != name.lower() and alias not in words:
                words.append(alias)
    return words


def object_block(obj: dict, object_names: dict[int, str], room_names: dict[int, str]) -> list[str]:
    """Render one object as a `create` block.

    Raises ValueError if an object's presence text is undecided (the decoder
    flagged it) and this file has no starting line recorded for it.
    """
    number = obj["id"]
    name = object_names[number]
    fixture = number >= 33
    carried = f'Carried name: "{obj["inventory_name"]}"' if obj["inventory_name"] else "No carried name"
    words = ", ".join(obj["vocabulary"]) or "none"
    out = [f"## Object {number}. {carried}. Words: {words}."]

    if number in STARTING_PRESENCE:
        presence, other = STARTING_PRESENCE[number]
        if other:
            out.append(f"## Its line changes with state: {other}. Phase 4.")
    elif obj["needs_review"]:
        raise ValueError(f"object {number} has branching presence text and no starting line recorded")
    else:
        presence = obj["presence"][0] if obj["presence"] else None

    kind = ["a thing", *(["scenery"] if fixture else []), *EXTRA_TRAITS.get(number, [])]
    out += ["", f"create {_the(name)}", "  " + ", ".join(kind)]
    aliases = _aliases(obj, name)
    if aliases:
        out.append("  aka " + ", ".join(aliases))
    if obj["start_room"] > 0:
        out.append(f"  in {_the(room_names[obj['start_room']])}")

    if presence:
        gate = "" if fixture else f" while not the player holds {_the(name)}"
        out += ["", f"  phrase present{gate}:", f"    {presence}"]
    return out


def _phrases_file(world: dict) -> list[str]:
    messages: dict[int, str] = {}
    for room in world["rooms"].values():
        for refusal in room["refusals"].values():
            if refusal["message"]:
                messages[refusal["code"]] = refusal["message"]
    out = [
        "## What the game says when a way is refused or fatal. One key per code of",
        "## UNDERG.BAS line 2870; the texts are lines 2880 to 2950.",
        "",
        "define phrases en-US",
    ]
    for code in sorted(messages, reverse=True):
        out += [f"  {REFUSAL_KEYS[code]}:", f"    {messages[code]}"]
    return out


def _story_file(imports: list[str], start_room: str) -> list[str]:
    return [
        "story",
        "  title: Underground",
        "  authors:",
        "    Gary Kleppe",
        "  id: underg",
        "  story-version: 0.1.0",
        "  description: UNDERGROUND V1, 14-Mar-79, RSTS/E BASIC-PLUS, ported to Chord.",
        "",
        "## Phase 3 entry file: the world only. Rooms, exits, objects and their",
        "## 1979 text load from the files below. The verbs, the player proper, the",
        "## IFID and the deviation ledger are Phases 4 and 5.",
        "",
        *[f'import "{name}"' for name in imports],
        "",
        "create the Adventurer",
        "  a person, playable",
        f"  in {_the(start_room)}",
        "",
        "  You.",
        "",
        "before the game starts",
        "  change the player to the Adventurer",
        "end before",
    ]


def render_files(world: dict, names: dict) -> dict[str, str]:
    """Return {file name: content} for every file of the scaffold."""
    room_names = {int(k): v for k, v in names["rooms"].items()}
    object_names = {int(k): v for k, v in names["objects"].items()}
    files: dict[str, list[str]] = {}

    filed = set(MAZE_ROOMS) | set(DEAD_END_ROOMS)
    for stem, (summary, numbers) in REGION_FILES.items():
        body = [f"## {summary}"]
        for number in numbers:
            body += ["", *room_block(world["rooms"][str(number)], room_names)]
        files[f"{stem}.chord"] = body
        filed |= set(numbers)
    if filed != set(room_names):
        raise ValueError(f"rooms not filed exactly once: {sorted(filed ^ set(room_names))}")
    files["maze.chord"] = maze_file(world, room_names)

    for stem, (summary, numbers) in OBJECT_FILES.items():
        body = [f"## {summary}"]
        for number in numbers:
            body += ["", *object_block(world["objects"][str(number)], object_names, room_names)]
        files[f"{stem}.chord"] = body

    files["phrases.chord"] = _phrases_file(world)
    imports = [*REGION_FILES, "maze", *OBJECT_FILES, "phrases"]
    # UNDERG.BAS line 70: `X%(0%)=8%`. The game opens outside the building.
    files["underg.story"] = _story_file(imports, room_names[START_ROOM])
    return {name: "\n".join(lines) + "\n" for name, lines in files.items()}


def main(argv: list[str]) -> int:
    """Write the scaffold. Returns 1, writing nothing, if any file exists and
    `--force` was not given."""
    world = json.loads(WORLD_PATH.read_text())
    names = json.loads(MAP_PATH.read_text())
    files = render_files(world, names)
    existing = [name for name in files if (STORY_DIR / name).exists()]
    if existing and "--force" not in argv:
        print(f"scaffold_world: refusing to overwrite {', '.join(sorted(existing))} (pass --force)", file=sys.stderr)
        return 1
    for name, content in files.items():
        (STORY_DIR / name).write_text(content)
    print(f"scaffold_world: wrote {len(files)} files to {STORY_DIR.relative_to(REPO)}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
