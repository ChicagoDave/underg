# Project Profile

**Generated**: 2026-11-10
**Repository**: underg

## Domains

- **Domain Modeling / Content Port** — `original/UNDERG.BAS`, `original/LOOK.BAS` (vendored 1979 RSTS/E BASIC-PLUS source) decoded by `scripts/extract_world.py` into `extracted/world.json` (87 rooms, 231 exits, 31 refusal-coded exits, 45 objects, 1263 DATA values); to be ported as Chord `.story` world data (`docs/work/port-underground-v1-chord/plan.md` Phases 3-5, verb mapping and gap list in `mapping.md`). Not a service or app — a declarative interactive-fiction content port.
- **CLI / Tooling — Interpreter Oracle** — `original/bplus.c` is a hand-written BASIC-PLUS interpreter (C), compiled locally (`cc -O2 -o original/underg original/bplus.c -lm`) and spawned as a subprocess by `scripts/oracle-smoke.sh` to produce ground-truth transcripts for parity checking. `original/check_data.py` validates the DATA block decodes to 1263 values.
- **CLI / Tooling — World Extractor** — `scripts/extract_world.py` (Python 3, stdlib only) decodes the world tables to JSON; held to the original by `tests/test_extract_world.py` (stdlib `unittest`, 12 tests, expectations anchored in the source or the oracle transcript).
- **CLI / Tooling — Chord Story Toolchain** — `@sharpee/devkit` 5.6.0 (provides the `sharpee` CLI), `@sharpee/platform-browser` and `@sharpee/sharpee` at ^5.6.0 (installed 5.6.0); Chord language **4.0.1** (`CHORD_LANGUAGE_VERSION` in `node_modules/@sharpee/chord/version.js`, versioned independently of the npm lockstep). Spikes under `spikes/` (`toolchain-smoke`, `room-name`, `seen-unseen`, `duplicate-names`) are throwaway `.story` files answering toolchain and gap questions.
- **API / Service**: not applicable — no server, no routes, no network boundary.

## Tech Stack

- **Language**: Chord (story DSL, language v4.0.1) for the port target; C (`original/bplus.c`, the oracle interpreter); Python 3 (local 3.14; `scripts/extract_world.py`, `original/check_data.py`, `tests/test_extract_world.py`); BASIC-PLUS (`original/*.BAS` — vendored 1979 source, read-only reference, not edited).
- **Runtime**: Node.js (local v25; hosts the `sharpee` CLI and branch-tester); native binary (compiled oracle `original/underg`, gitignored); Python 3 interpreter.
- **Framework**: Sharpee platform 5.6.0 — `@sharpee/devkit` (CLI: build/test), `@sharpee/chord` 5.6.0 (compiler, transitive via devkit), `@sharpee/platform-browser` (browser story runtime), `@sharpee/branch-tester` 5.6.0 (transitive; tree-document card runner).
- **Data layer**: none — no database, no ORM. World state is decoded to `extracted/world.json` and will be authored directly in `.story` source compiled to an IR (`dist/*.ir.json`, gitignored).
- **Messaging**: none detected.
- **Test framework**: `@sharpee/branch-tester` (card-based tree documents) for Chord stories; Python stdlib `unittest` for the extractor; a bespoke bash + diff harness (`scripts/oracle-smoke.sh`) for the C oracle, gating on `tests/golden/oracle-smoke.txt`.
- **Test command**: `bash scripts/oracle-smoke.sh && python3 -m unittest discover -s tests && npx sharpee test spikes/toolchain-smoke/toolchain-smoke.story`
  <!-- Verified green 2026-11-10. package.json's `npm test` (`sharpee build --test`) does not run the oracle regression or the Python suite. Retarget the third command from the spike to the real story once Phase 3+ lands real UNDERGROUND `.story` files and an oracle-derived card corpus. -->
- **Build tool**: `sharpee build` (Chord compiler, via devkit); `cc` (C99, for the oracle — invoked directly in `scripts/oracle-smoke.sh`, no Makefile).
- **Package manager**: npm (`package-lock.json` present); no Python dependency manifest (stdlib only).
- **CI/CD**: none detected — no `.github/workflows/`, `Jenkinsfile`, or `.gitlab-ci.yml`.
- **Monorepo**: No — single flat repo; Sharpee is a separate monorepo consumed here only as published npm packages.

## Conventions

- **Test location**: Chord story tests live beside their story as a `<story-name>.tests/` directory (`manifest.json` + card files, e.g. `spikes/toolchain-smoke/toolchain-smoke.tests/smoke001.json`) since the Chord 4.0.1 migration — the legacy `toolchain-smoke.tests.json` is still on disk alongside it; Python tests in top-level `tests/`; oracle golden output in `tests/golden/`.
- **Test naming**: `<story-name>.tests/` for branch-tester trees; `test_*.py` for unittest; `oracle-smoke.txt` for the golden transcript.
- **Source structure**: content-port shape — `original/` (vendored source, oracle interpreter, validation script, read-only reference), `scripts/` (extractor and regression tooling), `extracted/` (decoded world JSON), `spikes/` (one directory per toolchain/gap question, each with `<name>.story` + `<name>.config.json`), `tests/` (Python tests, golden transcripts). Real UNDERGROUND `.story` authoring (Phase 3+) will land in a new top-level directory not yet created.
- **TypeScript strict mode**: N/A — no TypeScript in this repo.
- **Import style**: N/A for Chord (fielded `story` header and `create the <X>` blocks, no imports); Python uses stdlib imports with `from __future__ import annotations`; C uses `#include`.

## Mutation Signatures

### Domain Modeling / Content Port (Chord world data)
- **Mutation calls**: `create the <Entity>` blocks (Chord 4.x: the kind leads every block — `a room`, `a thing`); `change the player to <character>` in a `before the game starts` block; `move <entity> to ...`, `make <actor> wear/take off <item>`, `raise`/`lower` counters; `states:` pairs for world flags; movement (`north to`) and inventory changes driven by stdlib actions or `define action` / `extend action` blocks.
- **Reporting without mutation**: room/object prose printed on `look`/`examine` (including `room name:` text) without any change to player location, inventory, or a named state — narration alone is not a mutation.
- **Test assertions — verify**: branch-tester `states` assertions on post-command world state (player location, inventory, named states), paired with `contains`/`notContains` on the narration that state change produces.
- **Test assertions — insufficient**: `contains`/`notContains` on printed text alone for a command that should mutate world state.

### CLI / Tooling — Interpreter Oracle (bplus.c / check_data.py)
- **Mutation calls**: `original/underg` writing `UNDER?.DAT` save files (cleaned before and after each run by `scripts/oracle-smoke.sh`); the interpreter's in-memory `M%`/`O%`/`X%` array mutations, observable only via the stdout transcript.
- **Reporting without mutation**: any change to `bplus.c` or the smoke command sequence not re-verified against `tests/golden/oracle-smoke.txt`.
- **Test assertions — verify**: `diff -u` between the golden transcript and a fresh run of the real compiled binary with a clean save-file slate (the rule 13a REAL-PATH test; no stub interpreter).
- **Test assertions — insufficient**: "compiled" or "exited zero" without the golden diff.

### CLI / Tooling — World Extractor (extract_world.py)
- **Mutation calls**: writing `extracted/world.json` (the extractor's only side effect).
- **Reporting without mutation**: reporting decode counts on stdout without the JSON on disk reflecting them.
- **Test assertions — verify**: assertions on decoded rooms/exits/objects against values anchored independently in `UNDERG.BAS`/`LOOK.BAS` or the oracle transcript.
- **Test assertions — insufficient**: asserting the extractor agrees with its own previous output (would pass on a transposed matrix decode).

## Notes

Content-port project gated on parity against a C-language oracle, not hand-written unit assertions for the story itself. Plan state (`docs/work/port-underground-v1-chord/plan.md`): Phases 1-2 DONE; Phase 3 (world authoring) PENDING and unblocked 2026-11-10 — gap G9 (identifier vs printed name) closed by Chord 4.0.1's `room name:` block, shown by `spikes/room-name/`. The port now targets Sharpee 5.6.0 / Chord 4.0.1 (was 5.4.1 / 3.6.0); the bump in `package.json`/`package-lock.json` and the new spikes were uncommitted at generation time. Brief mode (short name on revisit) is a recorded deviation, not a gap. `documentationStandard` in `.devarch/descriptor.json` is `always`.
