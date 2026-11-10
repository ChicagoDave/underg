"""Run a list of commands through the 1979 program and print what it says.

Purpose: ask the oracle (the compiled `bplus.c` running the unmodified
UNDERG.BAS and LOOK.BAS) what the original does, one question at a time.

Public interface: `run(commands) -> str`, and the command line
`python3 scripts/oracle_run.py CMD [CMD ...]` (each argument one input line;
the opening "Are you recalling a saved game?" is answered N for you).

Owner context: oracle tooling, beside `scripts/oracle-smoke.sh`. Every run
happens in a fresh temporary directory, so the UNDER?.DAT save file one run
writes cannot change the next (issue D-3).
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ORIGINAL = REPO / "original"
BINARY = ORIGINAL / "underg"
SOURCES = ("UNDERG.BAS", "LOOK.BAS")


def run(commands: list[str], timeout: float = 20.0) -> str:
    """Return everything the 1979 program prints for these input lines.

    The first prompt is answered "N" before `commands`. Builds the interpreter
    if it has not been built. Raises RuntimeError if the build fails and
    subprocess.TimeoutExpired if the program does not finish.
    """
    if not BINARY.exists():
        build = subprocess.run(
            ["cc", "-O2", "-o", str(BINARY), str(ORIGINAL / "bplus.c"), "-lm"],
            capture_output=True, text=True,
        )
        if build.returncode != 0:
            raise RuntimeError(f"could not build the oracle:\n{build.stderr}")
    with tempfile.TemporaryDirectory() as scratch:
        for name in SOURCES:
            shutil.copy(ORIGINAL / name, Path(scratch) / name)
        result = subprocess.run(
            [str(BINARY)], cwd=scratch, input="\n".join(["N", *commands]) + "\n",
            capture_output=True, text=True, timeout=timeout,
        )
        return result.stdout + result.stderr


if __name__ == "__main__":
    sys.stdout.write(run(sys.argv[1:]))
