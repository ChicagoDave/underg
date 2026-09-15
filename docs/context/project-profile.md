# Project Profile

**Generated**: 2026-09-14
**Repository**: underg

## Domains

- **Domain Modeling / Content Port** — `original/UNDERG.BAS`, `original/LOOK.BAS` (vendored 1979 RSTS/E BASIC-PLUS source) decoded into an 87-room x 14-column exit/attribute matrix and 45 object placements; ported as Chord `.story`/`.chord` world data (`docs/work/port-underground-v1-chord/plan.md` Phases 2-5). Not a service or app — a declarative interactive-fiction content port.
- **CLI / Tooling — Interpreter Oracle** — `original/bplus.c` is a hand-written BASIC-PLUS interpreter (C), compiled locally (`cc -O2 -o original/underg original/bplus.c -lm`) and spawned as a subprocess to produce ground-truth transcripts for parity checking. `original/check_data.py` is a Python extraction/validation script that checks the vendored DATA block decodes to the expected 1263 values.
- **CLI / Tooling — Chord Story Toolchain** — `@sharpee/devkit` (provides the `sharpee` CLI, in `node_modules/.bin/sharpee`), `@sharpee/platform-browser`, `@sharpee/sharpee` at 5.4.1; Chord is the declarative story-authoring DSL (language version 3.6.0, versioned independently of the npm package lockstep) compiled/tested via `npx sharpee build` / `npx sharpee test`. `spikes/toolchain-smoke/` is a stub two-room `.story` proving the toolchain builds and its `branch-tester` runs `.tests.json` cards.
- **API / Service**: not applicable — no server, no routes, no network boundary.

## Tech Stack

- **Language**: Chord (story DSL, language v3.6.0) for the port target; C (original/bplus.c, the oracle interpreter); Python 3 (original/check_data.py, DATA-block validation); BASIC-PLUS (original/UNDERG.BAS, original/LOOK.BAS — vendored 1979 source, read-only reference material, not edited).
- **Runtime**: Node.js (hosts the `sharpee` CLI and branch-tester); native binary (compiled oracle, `original/underg`, gitignored build artifact).
- **Framework**: Sharpee platform — `@sharpee/devkit` (CLI: build/test), `@sharpee/chord` (compiler, transitive via devkit), `@sharpee/platform-browser` (browser story runtime), `@sharpee/branch-tester` (transitive; tree-document `.tests.json` card runner).
- **Data layer**: none — no database, no ORM. World state is authored directly in `.chord`/`.story` source and compiled to an IR (`spikes/toolchain-smoke/dist/toolchain-smoke.ir.json`).
- **Messaging**: none detected.
- **Test framework**: `@sharpee/branch-tester` (card-based: `opening`/`boot`/`turn` cards with `contains`/`notContains`/`states` assertions) for Chord stories; a bespoke bash + diff harness (`scripts/oracle-smoke.sh`) for the C oracle, gating on a golden transcript (`tests/golden/oracle-smoke.txt`).
- **Test command**: `bash scripts/oracle-smoke.sh && npx sharpee test spikes/toolchain-smoke/toolchain-smoke.story`
  <!-- package.json's own `npm test` (`sharpee build --test`) only builds the still-stub toolchain-smoke spike and does not run the oracle regression; the two commands above are what actually gates this repo today per docs/work/port-underground-v1-chord/plan.md Phase 1's exit state. Re-check this field once real UNDERGROUND `.story`/`.chord` files exist (Phase 3+) and a `underg.tests.json` card corpus is generated from the oracle — the command will likely retarget from the spike path to the real story. -->
- **Build tool**: `sharpee build` (Chord compiler, via devkit); `cc` (C99, for the oracle — invoked directly in `scripts/oracle-smoke.sh`, no Makefile).
- **Package manager**: npm (`package-lock.json` present).
- **CI/CD**: none detected — no `.github/workflows/`, `Jenkinsfile`, or `.gitlab-ci.yml`.
- **Monorepo**: No — single flat repo; Sharpee itself is a separate monorepo consumed here only as published npm packages (per plan Phase 1 Open Question 1 resolution — no submodule, no workspace link).

## Conventions

- **Test location**: Chord story tests live beside their story as `<story-name>.tests.json` (e.g., `spikes/toolchain-smoke/toolchain-smoke.tests.json`); oracle regression golden output lives under `tests/golden/`.
- **Test naming**: `<story-name>.tests.json` for branch-tester cards; `oracle-smoke.txt` for the golden transcript.
- **Source structure**: content-port shape, not layer- or feature-based application code — `original/` (vendored 1979 source + oracle interpreter + validation script, read-only reference), `spikes/` (toolchain proof-of-concept stories), `scripts/` (regression tooling), `tests/golden/` (recorded transcripts). Real UNDERGROUND `.story`/`.chord` authoring (Phases 3+) will land in a new top-level directory not yet created.
- **TypeScript strict mode**: N/A — no TypeScript in this repo (Chord stories are the authored artifact; the compiler that processes them is a consumed npm dependency).
- **Import style**: N/A for Chord (declarative blocks, no import statements observed in `.story` files); C oracle uses standard `#include`.

## Mutation Signatures

### Domain Modeling / Content Port (Chord world data)
- **Mutation calls**: `create the <Entity>` blocks establishing rooms/objects/actors; `change the player to <Entity>`; state transitions expressed as Chord `states:` pairs (per the plan's D9 note — boolean world flags must be real `states:` pairs, not bare true/false); movement (`north to`, `south to`) and inventory changes (`take`, `drop`) driven by stdlib actions or `define action` blocks.
- **Reporting without mutation**: room/object prose text printed on `look`/`examine` without any change to `player.location`, `player.inventory`, or a named `states:` value — narration alone is not a mutation.
- **Test assertions — verify**: branch-tester `states` assertions (e.g., `"player.inventory contains Lamp"`, `"player.location = Clearing"`) that check actual post-command world state, matched against `contains`/`notContains` checks on the narration produced by that same state change.
- **Test assertions — insufficient**: asserting only `contains`/`notContains` on printed text without a corresponding `states` assertion for a command that is supposed to mutate world state (e.g., checking that "You take the lamp." was printed but never checking `player.inventory`).

### CLI / Tooling — Interpreter Oracle (bplus.c / check_data.py)
- **Mutation calls**: `original/underg` writing `UNDER?.DAT` save files at run time (side effect the harness explicitly cleans up before and after each run, per `scripts/oracle-smoke.sh`); the C interpreter's in-memory BASIC-PLUS variable/array mutations (`M%`, `O%`, `X%`) which are not directly observable — only surfaced via stdout transcript.
- **Reporting without mutation**: any change to `scripts/oracle-smoke.sh`'s command sequence or to `bplus.c` itself that is not re-verified against `tests/golden/oracle-smoke.txt` — the golden diff is the only gate; a passing build with no diff run is not verification.
- **Test assertions — verify**: `diff -u` between the golden transcript and a fresh run's captured stdout, executed against the actual compiled binary spawned as a subprocess with a clean save-file slate (`scripts/oracle-smoke.sh` — the plan's designated REAL-PATH test, per rule 13a; no stub interpreter is used anywhere in this path).
- **Test assertions — insufficient**: asserting the C program "compiled" or "exited zero" without diffing output against the golden; asserting `check_data.py`'s value count without also confirming the oracle itself still boots and accepts input identically.

## Notes

This is a content-port project, not an application: the deliverable is declarative Chord (`.story`/`.chord`) source describing a ported 1979 text-adventure world, gated on parity against a C-language oracle rather than on hand-written unit assertions (plan's stated principle: "Acceptance is gated on `@sharpee/branch-tester` running a card corpus generated from `bplus.c`, not on hand-written assertions"). The repo currently has no real UNDERGROUND `.chord` authoring yet — `spikes/toolchain-smoke/` is a deliberately trivial two-room stub proving the toolchain round-trips; Phase 2 (world/verb extraction and mapping) is CURRENT per `docs/work/port-underground-v1-chord/plan.md`, with Phases 3-7 (world authoring, verb layer, assembly, deviation ledger, oracle-derived card generation) still PENDING. `documentationStandard` in `.devarch/descriptor.json` is `always`. Re-run this detector once Phase 3+ lands real `.chord` files and a `underg.tests.json` card corpus exists — the Test command field will very likely need to retarget from the toolchain-smoke spike path to the real story.
