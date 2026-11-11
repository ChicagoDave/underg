# Session Plan: Port UNDERGROUND V1 (1979 BASIC-PLUS) to Chord, gated on branch-tester parity

**Created**: 2026-09-14
**Plan Status**: ACTIVE
**Overall scope**: Port Gary Kleppe's UNDERGROUND V1 (RSTS/E BASIC-PLUS, 14-Mar-79) — 87 rooms x 14-column exit/attribute matrix, 45 object placements, ~20 parser verbs, all text — to Chord (Sharpee monorepo; **language version 3.6.0**, which is versioned separately from the `@sharpee/*` package lockstep — `packages/chord` v5.4.1 is the compiler's package version, not the language's), producing the branch-stories deliverable shape (`.story` entry, per-region `.chord` files, `.config.json` with IFID, `.tests.json` cards) with a deviation ledger recording every place Chord cannot reproduce the original's wording. Acceptance is gated on `@sharpee/branch-tester` running a card corpus generated from `bplus.c` (the verified BASIC-PLUS interpreter oracle), not on hand-written assertions.
**Bounded contexts touched**: N/A — this is a content/language port (world data + parser-verb semantics into a story-authoring DSL), not domain-driven service work. Framed in plain technical terms per the "DDD does not apply" checklist (infrastructure/content-port shape, no bounded-context model in play).
**Key domain language**: N/A (plain technical framing chosen; IF/Chord terms — room, exit, object, verb, deviation ledger, card, oracle — are used because they are what the source material and target language call these things, not as DDD artifacts).

## References consulted
- `docs/context/project-profile.md` — stack is explicitly "not yet established, pending the placement decision"; this plan's Phase 1 is that decision, so nothing here is assumed ahead of it.
- `/Users/david/repos/sharpee/docs/architecture/chord-grammar-changes.md` (ratchet log, 117 entries) — the grammar is a closed set (Given 7); relevant constraints for this port: prose-block-only phrase text (no quoted one-liners) governs how LOOK-V1's room text becomes Chord prose; "conditional blocked exits" (`<dir> is blocked while <cond>: <key>`) is the direct target for V1's directional refusal messages; D9's three-ring boolean-state gate forbids modeling any yes/no world flag as a bare true/false — V1's lantern-lit/door-locked/etc. style state must become real `states:` pairs; ADR-327's player-is-a-role removal of `create the player` (entries 105-106) governs how the PC is declared; Z1 `first time` room blocks are the built-in mechanism for LOOK-V1's seen/unseen (room*100 vs +50) text split.
- `/Users/david/repos/sharpee/docs/architecture/adrs/adr-327-explicit-references.md` — clause heads are actor-explicit (`on|after <actor> <gerund>`); `it`/`its` are removed from the language. Any verb/room authoring in this plan must be written in the current form, not the `it`-based form seen in older docs.
- `/Users/david/repos/sharpee/docs/architecture/adrs/adr-328-actors-are-a-platform-concept.md` — actors (player and any addressed NPC-like entities) are symmetric at the platform level; relevant if V1's world has any non-player character logic to model, however thin.
- `/Users/david/repos/sharpee/docs/architecture/adrs/adr-329-chord-acting-statement.md` — if any V1 verb effect requires scripting another entity's action, the acting statement (not `move`-as-teleport) is the current mechanism.
- `/Users/david/repos/sharpee/docs/architecture/adrs/adr-074-ifid-requirements.md` — every story declares an IFID; for Chord stories the hard fail is at publish time (a missing IFID is a compile warning), so `underg.config.json` must carry a freshly minted IFID from the start.
- `/Users/david/repos/sharpee/docs/architecture/adrs/adr-056-story-testing-framework.md`, `adr-073-transcript-story-testing.md` — origin ADRs for Sharpee's testing-first convention; superseded in file format (see below) but establish that a story ships with a behavioral test corpus, not prose-only.
- `/Users/david/repos/sharpee/docs/architecture/adrs/adr-294-golden-transcripts-tester-rebuild.md`, `adr-300-addressable-channels-and-canonical-transcript.md`, `adr-307-testing-tree-model-v2.md`, `adr-340-testing-assertion-core.md` — the current branch-tester model: `.tests.json` tree-document cards (`opening`/`boot`/`turn`, with `branches`), a single shared assertion-core (`checkAssertion`/`checkStateAssertion`) used by both testers, and the Chord-spelled `[the] <name> is <state>` / `story.state = <value>` claim forms this port's cards must use for state assertions.
- `/Users/david/repos/sharpee/docs/work/chord/dungeo-conversion.md` — the prior conversion-assessment method (bucket the source into converts-today / converts-under-design / stays-TS-hatch / out-of-scope / genuine-language-gaps, smallest-gap-first) that Phase 2 of this plan applies to Underground before any `.chord` authoring begins.
- `/Users/david/repos/sharpee/docs/work/chord/grammar.md` (Phase A snapshot) and `/Users/david/repos/sharpee/docs/unofficial/reference/chord-grammar.md` (living reference) — structural reference for `create`/`define action`/`define trait`/statements/conditions used throughout Phases 3-4; the living reference is authoritative where the two disagree (Phase A snapshot predates most of the ratchet log).
- `/Users/david/repos/sharpee/branch-stories/secret-letter/secret-letter.story` — the deviation-ledger convention this port's header must follow (a numbered list of every wording departure and why), and the "RETARGET vs. faithful port" framing question this plan answers as "faithful port, gated on the oracle" rather than a retarget.
- `/Users/david/repos/sharpee/branch-stories/{secret-letter,fernhill,ides-of-march}/*.tests.json` — the concrete `opening`/`boot`/`turn` card shape (`contains`/`notContains`/`states`, `branches`) this port's `underg.tests.json` must match byte-for-shape.
- `/Users/david/repos/sharpee/packages/branch-tester/README.md` — PARTIALLY STALE: documents the retired `.transcript` file format. The package's own source (`tree-document.ts`, `auto-assertion.ts`) and the goal's own statement ("there are no `.transcript` files in branch-stories") confirm the JSON card model is current; this plan follows the card model, not the README's examples.

## Governing principle — reproduce the story as coded

**Owner's direction, 2026-09-14: the port reproduces UNDERGROUND as the 1979
program is written, not as it was meant to work.** Where the code and the
apparent intent disagree, the code wins. Bugs in the original are behaviour to
be carried over, not defects to be fixed.

This is the standing answer to the whole gap list in `mapping.md`, not a ruling
on one item. It settles, without needing to be re-asked:

- **G8** — `LEASH` addresses the rat (both map to `T%=31`) and the leash is
  unaddressable. Reproduced.
- **G1** — the parser accepts verb and noun in either position. Reproduced.
- **G5** — five-character noun truncation over-accepts. Reproduced.
- **The five verb conflations** (WEAR=TAKE, GIVE=THROW, EAT=DRINK,
  UNLOCK=OPEN, PULL=PUSH). Reproduced, at the cost of the corresponding stdlib
  actions never firing.
- **G6/G7** — the death-resurrection loop and the lamp-timer interruption are
  behaviour, and are ported as behaviour.

**What this does to the deviation ledger.** It is no longer a record of choices
this port made. Every entry is now one thing only: a place where Chord 3.6.0
*cannot* express what the original does, with the construct that is missing.
That makes the ledger reviewable against the language rather than against
taste, and makes each entry a candidate ratchet-log item in `sharpee` rather
than an apology.

**Every defect carried over is registered.** `original-issues.md` is the
O-register: one entry per defect, typo, or oddity in the 1979 program, each
with a disposition (REPRODUCE / RESTORED-UPSTREAM / BLOCKED), so a future reader
who notices that the leash cannot be picked up finds the record and stops rather
than "fixing" it. It is deliberately separate from the repo's own DevArch issue
store, which holds D-n items we intend to fix.

**Exception, by owner ruling 2026-11-10: eight slips are corrected, not
reproduced.** Asked whether FILL ending the program, JUMP firing
the laser and READ WATER printing a coin's legend should stay as coded, David
answered "not this time - let's infer the correct actions for the bugs". They
are O-8, O-9 and O-10 in `original-issues.md`, disposition CORRECTED, each with
the line as written and the reading inferred. The principle stands for
everything else; a further correction needs its own ruling. A second ruling
the same day ("yes those two as well") added O-1, LEASH naming the rat, which
reverses the 2026-09-14 answer on G8 above, and O-11, the rat's bite that can
never happen. A third added O-12: the cat needs its leash, as the unreachable
line 2140 says. A fourth ("again - infer the correct response") added O-13:
the command typed after the ice or the woman stops you keeps its noun. A fifth
("B") added O-15: room 51's exits come from the scanned sheets, where the
transcribed line 510 leaves no way back from the well; `UNDERG.BAS` is left as
transcribed. Where the port is
CORRECTED the oracle and the port differ on purpose, so Phases 6 and 7 must
not generate cards from the oracle for those commands.

The one thing this principle does not license is inventing behaviour where the
source is absent rather than wrong. `LOOK.BAS` 10370-10500 and a handful of
`UNDERG.BAS` lines are reconstructed rather than transcribed (see
`original/README-reconstruction.md`); those stay flagged as reconstruction, and
the line-975 restoration stays recorded as upstream, separate from both.

## Open questions this plan surfaces (not assumed)

1. **Placement — RESOLVED 2026-09-14 by the owner: this work is self-contained in this repo (`~/repos/underg`).** The port is not a branch-story in `~/repos/sharpee`. The Chord toolchain is consumed as published npm packages — `@sharpee/devkit` (the `sharpee` CLI), `@sharpee/chord`, and `@sharpee/branch-tester` are all published at **5.4.1**, carrying Chord language **3.6.0**, so no submodule, no monorepo dependency, and no publish wait blocks Phases 2-7. Consequence carried forward: a language gap this port finds is a change in `sharpee` that must be published before this repo can consume it, so Phase 2's mapping table records gaps against the **published** 3.6.0 surface, not against the monorepo working tree. Phases 2-7 happen here; no re-plan in another repo, and rule 18b does not apply.

2. **Verb mapping**: which of the ~20 verbs map onto existing Sharpee stdlib actions (taking, dropping, going, examining, etc. — likely aliases via grammar) versus need a Chord `define action` versus need a TS hatch. Phase 2 produces this mapping as a table before any verb is authored — not assumed here.
3. **The line-975 bug — RESOLVED 2026-09-14 (Phase 1): keep the restoration; it is not a port deviation.** The vendored `original/UNDERG.BAS` already carries `975 ON ERROR GOTO 0` (verified at line 97 of the file), restored upstream on the evidence of the 01-Mar-79 listing. Three reasons it stands: the oracle and the port read the *same* source, so parity is preserved by construction rather than by choosing sides; the bug is unobservable in normal play, affecting only how a failed `CHAIN` at line 990 is reported (line 30's `erl-20%` test falls to `resume60`, printing a bogus "Password not found."); and it has no Chord analogue at all, because there is no `CHAIN` to fail. Recorded in the deviation ledger under upstream restorations, separate from deviations this port introduces.

## Phases

### Phase 1: Source acquisition, oracle verification, and placement decision
- **Tier**: Medium
- **Budget**: 250
- **Domain focus**: establishing the executable oracle (`bplus.c` running the unmodified 1979 source) and resolving where this work happens before any Chord authoring starts.
- **Entry state**: this repo has only DevArch scaffolding and no commits; no Sharpee toolchain is installed; none of the source material (`UNDERG-V1.BAS`, `LOOK-V1.BAS`, `check_data.py`, `V1-FINDINGS.md`, `README.md`, `bplus.c`) is vendored anywhere yet.
- **Deliverable**:
  - The V1 source tree from `github.com/gschmidl/interactive-fiction`, directory `Underground (Scans)/V1/`, vendored (or fetched via a committed script) into the chosen working location.
  - `bplus.c` built and confirmed to run `UNDERG-V1.BAS` interactively; a captured smoke-test session (boot text plus a handful of commands) proving the oracle executes, verified line-for-line against the RSTS/E SIMH baseline claim in the source material.
  - `check_data.py` run against the DATA block, confirming the 1263 values decode to the claimed 87x14 room/exit matrix and 45 object locations.
  - `V1-FINDINGS.md` and `README.md` read; the line-975 bug and any revision-mixing/transcription-vs-reconstruction caveats summarized, with an explicit recorded decision on whether the bug is replicated (oracle parity) or fixed (and ledgered).
  - Placement: already decided (Open Question 1) — self-contained in this repo, consuming `@sharpee/devkit` 5.4.1 from npm. Phase 1's remaining placement work is to *stand it up*: `npm install -g @sharpee/devkit` (or a local devDependency), `sharpee init`-style project scaffolding for `underg`, and a confirmed `sharpee build` + `sharpee build --test` round trip on a trivial stub story, proving the published toolchain works here before any real authoring begins.
- **Exit state**: the oracle runs and is trusted; the world-data volume is confirmed; the line-975 bug decision is recorded; the published Chord toolchain is installed here and a stub story builds and tests green.
- **Status**: DONE (2026-09-14) — oracle built and replaying green via `scripts/oracle-smoke.sh` against `tests/golden/oracle-smoke.txt`; DATA block validates at 1263 values (87x14 + 45); line-975 decision recorded (Open Question 3); placement stood up — devkit 5.4.1 / Chord 3.6.0 installed locally, stub story at `spikes/toolchain-smoke/` gate-clean, 4 cards / 7 assertions passing, browser build emitted.

### Phase 2: World and verb extraction — mapping design
- **Tier**: Medium
- **Budget**: 250
- **Domain focus**: turning the 1263 DATA values and the LOOK-V1 text table into a structured intermediate model, and the ~20-verb parser into a per-verb Chord mapping — all before any `.chord` file is written.
- **Entry state**: Phase 1 done — oracle trusted, placement fixed.
- **Deliverable**:
  - A structured world-model document decoding the DATA block: 87 rooms with their 14-column exit/attribute rows as UNDERG-V1.BAS's own parsing logic reads them, and the 45 object-to-room placements.
  - LOOK-V1.BAS's `room*100` (unseen) / `room*100+50` (seen) text table extracted verbatim into first-visit vs. subsequent-visit prose per room — quoted exactly, no paraphrase; this is the raw material Phase 3 turns into Chord prose blocks and Z1 `first time` blocks.
  - A verb inventory (~20 entries) resolving Open Question 2: for each verb, its BASIC-PLUS parser handling (synonyms, special-cased nouns, quirks) and its proposed Chord target — stdlib grammar alias, `define action`, or TS hatch — using the dungeo-conversion.md bucket method (converts today / needs a hatch / genuine language gap), smallest-gap-first.
  - Explicit call-outs for anything that doesn't fit Chord's current closed grammar (a candidate future ratchet-log entry) versus what today's grammar already covers (D1 state adjectives, conditional blocked exits, `must`, `refuse when`, Z1 first-time blocks).
- **Exit state**: every room, exit, object, and verb has a named Chord target construct or a flagged, explicit gap — nothing is authored ad hoc in Phase 3/4 without having appeared here first.
- **Status**: DONE (2026-09-14) — world decoded by `scripts/extract_world.py` into `extracted/world.json` (87 rooms, 231 exits, 31 refusal-coded exits, 45 objects, 1263 DATA values) and held to the original by `tests/test_extract_world.py` (8 tests green, every expectation anchored in the source or the oracle transcript, not in the extractor's output). Verb mapping table and the enumerated gap list at `docs/work/port-underground-v1-chord/mapping.md`. Headline counts: 15 verbs, not ~20 — 8 alias onto stdlib, 5 need `define action`, 0 need a TS hatch; 8 gaps (G1-G8) have no declarative target, of which G8 is a vocabulary collision in the 1979 source that needs David's call.

### Phase 3: World authoring in Chord — rooms, exits, objects, prose
- **Tier**: Large
- **Budget**: 400
- **Domain focus**: the 87-room/14-exit matrix and 45 objects as Chord `create` blocks, one `.chord` file per region (branch-stories convention).
- **Entry state**: Phase 2's world-model document and verb mapping exist.
- **Deliverable**: per-region `.chord` files covering all 87 rooms (grouped by V1's own geography — entrance/tunnels/vault or whatever the extracted map shows), every exit (including one-way and conditionally-blocked forms where V1 has directional refusals, via the ratchet's `<dir> is blocked while <cond>: <key>` form), the 45 objects placed with Identity plus the standard traits Phase 2 assigned them, and room prose using Z1 `first time` blocks for the seen/unseen split — verbatim from LOOK-V1 wherever Chord's prose-block form can carry it, with every place it cannot recorded immediately in a running deviation-ledger draft (not deferred to Phase 5).
- **Exit state**: the full room/exit/object graph loads clean under the Chord loader (no load/analysis errors) and matches Phase 2's map one-to-one.
- **Delivered** (2026-11-10): the world is in `story/` — nine region files, `maze.chord` (rooms 61 to 76 as two room groups and a one-way exit table), three object files, `phrases.chord` and a world-only `underg.story`. It was written by `scripts/scaffold_world.py` from `extracted/world.json` and `story/world-map.json` (the 1979 numbers against the Chord names), so nothing was retyped; the files are hand-edited from here on. `scripts/world_parity.py` holds the compiled story to the decode. The decode itself gained two lines: the extractor stopped at LOOK.BAS 5400 and 5700 and cut the city sign and the vault inscription short (fixed, with a regression test). Deviations are in `deviation-ledger-draft.md` (L-1 to L-5, plus what is left for Phase 4). Not done here, by design: the two computed exits (G3, G4), exits that change in play (G2), darkness, and the second presence line of seven stateful objects.
- **Demonstrated**: 2026-11-10 — `npx sharpee compose story/underg.story --check` reports gate-clean on Chord 4.0.1 (134 entities; one warning, `analysis.room-no-description` on room 85, which is O-7 reproduced). `python3 scripts/world_parity.py` reports "OK - 87 rooms and 45 objects match the decode". `python3 -m unittest discover -s tests` runs 32 tests, all passing, 12 of which break the compiled story one way each and assert the parity check names the break. `sharpee play story` was walked from the Building through the Basement, the forest path and the cave mouth to the Elevator, with the 1979 text, the "door is closed" refusals and the presence lines printing. [verified: work-summary-writer rerun 2026-11-10T22:42:20Z — compose --check gate-clean (one warning, room 85), world_parity OK 87 rooms / 45 objects, unittest Ran 32 tests OK] [play walk: reported by session, unverified]
- **Status**: DONE

### Phase 4: Verb and action layer
- **Tier**: Large
- **Budget**: 400
- **Domain focus**: the ~20-verb parser as Chord grammar aliases, `define action` blocks, and `on`/`after` clause bodies.
- **Entry state**: Phase 2's verb mapping exists; Phase 3's world is loadable (verbs need rooms/objects to test against, but see the note below on ordering).
- **Deliverable**: every verb from Phase 2's inventory implemented per its assigned target — stdlib reuse via grammar aliases where the mapping said so, `define action` for the rest, refusals via `must`/`refuse when`, reactions via actor-explicit `on the player <gerund>` / `after the player <gerund>` clauses (ADR-327 — no bare `it`), and a documented, per-verb decision on the line-975 bug and any other V1-FINDINGS.md parser idiosyncrasy that verb touches.
- **Exit state**: every verb the original parser accepted has a Chord equivalent or a documented, ledger-recorded gap; the story is playable by hand start-to-end.
- **Demonstrated**: 2026-11-10 (session b5d946) — `python3 -m unittest discover -s tests` runs 61 tests, all passing. `StartToEnd` plays the port from the first move to the ending in 272 commands with no refusal: 125, 325 and 400 points after the three trips, all sixteen treasures listed in the building, the road at 381 points, the wall, the woman and the closing text held to `UNDERG.BAS` 3140 to 3144. `WalksEndWhereTheOriginalDoes` plays 34 walks through both the oracle and the port and compares what is carried, the score and the turn count; `CorrectedSlips` shows both halves of each owner-ruled difference (O-1, O-8 to O-13, O-15); `PastTheRat` holds the cat, vault and key to the listing. Gaps are ledgered in `deviation-ledger-draft.md` (L-6 to L-18 and "Not written": the random exit west of room 60, the woman's lamp offer, the dark-room accident). `npx sharpee compose story/underg.story --check` gate-clean on Chord 4.0.1 (one warning, room 85); `scripts/world_parity.py` OK; `scripts/oracle-smoke.sh` OK (run 2026-11-11T02:24:01Z, before the ledger edits that followed). [verified: work-summary-writer rerun 2026-11-11T02:26:08Z — unittest Ran 61 tests OK, world_parity OK 87 rooms / 45 objects, compose --check gate-clean (one warning, room 85), oracle-smoke OK] [StartToEnd/walk details: reported by session, carried by the passing suite]
- **Corrections to earlier phases found here** (2026-11-10): Phase 3 started the player in room 1; line 70 and the oracle's transcript say room 8, and the scaffold, the story and its test now do. Phase 2's decode cut the volcano's text (line 2950) at its first sentence; the extractor now carries both printed lines. Three room identifiers changed in `story/world-map.json` (59, 60, 85), because a name ending in a number cannot be the subject of a Chord condition.
- **Progress** (2026-11-10, not complete): `story/verbs.chord` holds one action per 1979 handler, with the death-and-continue loop, the lamp timer, darkness and the moving exits; `tests/test_verbs_against_oracle.py` plays the same walks through the oracle and the port and compares what is carried and the score. What is compared, what is written but not yet compared, and what is not written are listed in `deviation-ledger-draft.md` under "Phase 4: done and not done". The phase stays CURRENT until that last list is empty or ledgered.
- **Status**: DONE
- **Note on ordering**: Phases 3 and 4 both depend only on Phase 2's output, not on each other — they are listed sequentially for narrative simplicity, not because rooms must exist before verbs. A session could interleave them per-region (author a region's rooms, then its region-specific verb behavior) if that proves more tractable once Phase 2's map is in hand.

### Phase 5: Story assembly and initial deviation ledger
- **Tier**: Medium
- **Budget**: 200
- **Domain focus**: the `.story` entry file, config, and the player-as-role declaration.
- **Entry state**: Phases 3 and 4 complete — world and verbs both load and run.
- **Deliverable**: `underg.story` wiring the region imports in arbitration order (ADR-251; imports are a paste at their own position, so order is semantic — per the secret-letter precedent), `underg.config.json` with a freshly minted IFID (ADR-074), the player declared `playable` and assigned via a `before the game starts … end before` block (ADR-327 D9/D10 — `create the player` is removed), and a complete first-pass deviation ledger in the `.story` header (secret-letter convention) enumerating every wording departure introduced in Phases 3-4 and why, plus the line-975 bug decision from Phase 1.
- **Exit state**: `underg.story` builds clean end-to-end with no analysis errors; the ledger accounts for every deviation introduced so far.
- **Status**: PENDING

### Phase 6: Oracle-driven card generation tooling
- **Tier**: Large
- **Budget**: 400
- **Domain focus**: generating `underg.tests.json` cards from `bplus.c`'s real output, per the acceptance-gate requirement that the original's real text is the assertion source.
- **Entry state**: `underg.story` builds; the oracle (Phase 1) is trusted and scriptable.
- **Deliverable**: a script/tool that drives `bplus.c` with scripted command sequences, captures its real output, and converts that output into `opening`/`boot`/`turn` cards (`contains`/`notContains`/`states` assertions, `branches` where V1's paths diverge) — never hand-written prose. An initial corpus covering the main walkthrough plus the highest-value branches, scaled against the existing worked examples (fernhill 84 turns, ides-of-march 37, secret-letter 564) — Underground's 87-room scale suggests a corpus toward the secret-letter end of that range.
- **Exit state**: the generation tooling exists and is reusable; a first run of `underg.tests.json` against the Chord port produces a baseline pass/fail report (not required to be green yet).
- **Status**: PENDING

### Phase 7: Parity closure
- **Tier**: Large
- **Budget**: 400
- **Domain focus**: closing the gap between the Chord port and the oracle-derived assertions until `@sharpee/branch-tester` is green.
- **Entry state**: Phase 6's baseline report exists, naming every current mismatch.
- **Deliverable**: iterate the `.chord` files and/or the card corpus (expanding coverage where the baseline found gaps) until the full `underg.tests.json` card set passes under branch-tester; every remaining, unavoidable difference from the original recorded as a final deviation-ledger entry with its reason; a closing note comparing this port's scale (rooms, verbs, cards) against the worked examples it followed.
- **Exit state**: the branch-tester parity gate passes; the deviation ledger is complete and closed; the port meets the acceptance gate stated in the goal.
- **Status**: PENDING
