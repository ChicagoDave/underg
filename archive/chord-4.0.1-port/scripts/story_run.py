"""Run a list of commands through the Chord port and return what it says.

Purpose: the port's side of an oracle comparison. `scripts/oracle_run.py` asks
the 1979 program; this asks `story/`, through the real `sharpee play`.

Public interface: `run(commands) -> list[tuple[str, list[str]]]` (each command
with the non-blank lines printed in reply, the opening text under the command
""), and `python3 scripts/story_run.py CMD [CMD ...]`.

Owner context: Phase 4 verification tooling, beside `scripts/oracle_run.py`.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def run(commands: list[str], timeout: float = 120.0) -> list[tuple[str, list[str]]]:
    """Play the story with these input lines and split the transcript by command.

    Commands are lower-cased, as the 1979 program upper-cases its own input.
    Raises RuntimeError if the story does not load.
    """
    typed = [command.lower() for command in commands]
    result = subprocess.run(
        ["npx", "sharpee", "play", "story"], cwd=REPO, input="\n".join(typed) + "\n",
        capture_output=True, text=True, timeout=timeout,
    )
    if "--- Play Mode ---" not in result.stdout:
        raise RuntimeError(f"the story did not load:\n{result.stdout}{result.stderr}")
    body = result.stdout.split("--- Play Mode ---", 1)[1].splitlines()[1:]
    replies: list[tuple[str, list[str]]] = [("", [])]
    for line in body:
        if line.startswith("> "):
            replies.append((line[2:], []))
        elif line.strip():
            replies[-1][1].append(line)
    return replies


if __name__ == "__main__":
    for command, lines in run(sys.argv[1:]):
        print(f"> {command}" if command else "(opening)")
        for line in lines:
            print(f"  {line}")
