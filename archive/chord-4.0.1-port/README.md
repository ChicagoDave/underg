# Archived: the first Chord port of UNDERGROUND V1 (Chord 4.0.1)

Archived 2026-11-10 by owner decision. David judged this port very bad: it
compiles gate-clean and matches the 1979 program's output in its tests, but it
gets there by forcing the BASIC program's control flow through Chord with
workarounds, not by writing Chord as the language is meant to be written. It
is kept as a record of how a model misuses a language it does not know, not as
a base to build on. A new port waits on a new Chord version and a
code-generation primer.

**Do not copy from `story/` into a new port.**

## What is here

- `story/` - the port: `underg.story`, fourteen `.chord` files,
  `underg.config.json`, `world-map.json`. Written against Chord 4.0.1 on
  `@sharpee/devkit` 5.6.0.
- `scripts/` - `scaffold_world.py`, `world_parity.py`, `story_assembly.py`,
  `story_run.py`: tooling that only makes sense beside this `story/`.
- `tests/` - `test_world_parity.py`, `test_verbs_against_oracle.py`,
  `test_story_assembly.py`.

## Frozen, not runnable in place

The scripts and tests resolve `story/`, `extracted/` and `original/` from the
repository root, so they do not run from this folder. They last ran green (74
tests with `tests/test_extract_world.py`) at commit `6bf0cfa`; check that
commit out to run them.

## What a new port may still want from here

Knowledge of the 1979 program, not Chord:

- The command walks in `tests/test_verbs_against_oracle.py` (`LONG_WALK`,
  `SHORT_WALKS`, the 272-command winning walk in `StartToEnd`). They are
  inputs to the original as much as to the port.
- The plan's records, archived at
  `docs/work/archive/port-underground-v1-chord/`: `original-issues.md` (the O
  register and the owner's rulings on the eight corrected slips), `mapping.md`
  (the verb inventory and the decoded map), and the "Findings for the
  `sharpee` ratchet log" list in `deviation-ledger-draft.md`.

Still live at the repository root and untouched by this archive: `original/`
(the 1979 source and the bplus oracle), `extracted/world.json`,
`scripts/extract_world.py`, `scripts/oracle_run.py`, `scripts/oracle-smoke.sh`
and `tests/test_extract_world.py`.
