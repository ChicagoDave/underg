# Chord gap: an entity's identifier and its printed name cannot differ

**Found:** 2026-09-14, porting UNDERGROUND V1 (1979) to Chord 3.6.0.
**Status:** CLOSED 2026-11-10. Chord 4.0.1 (`@sharpee/devkit` 5.6.0) carries a `room name:` block, the shape of candidate 2 below: the `create` head stays the identifier and the block supplies the printed name. `spikes/room-name/room-name.story` builds gate-clean on the published 5.6.0 and plays: three rooms heading `Mine` and a three-room group heading `You are in a maze of twisty little passages, all alike.`, each walked with `sharpee play`. The original spike, `spikes/duplicate-names/`, still fails with `analysis.duplicate-entity`, as it should. Was: blocking Phase 3 of `docs/work/port-underground-v1-chord/plan.md`.
**Written for:** the `sharpee` repo. This file is the evidence; the decision and
any ratchet-log entry belong there.

## The gap

Chord derives an entity's identifier from its name and offers no way to set the
two independently. Two entities that should print the same name therefore cannot
coexist.

```
create the Mine
  a room
  ...

create the Mine          ## error [analysis.duplicate-entity]
  a room                 ## An entity named `mine` is already declared at line 10.
```

Reproduced at `spikes/duplicate-names/` in the `underg` repo.

## Why this is a surface gap, not a model gap

The platform already draws the distinction the language cannot express.
`packages/chord/src/ir.ts`:

```ts
export interface IREntity {
  /** Canonical slug (lowercased name words joined with `-`). Unique. */
  id: string;
  /** Display name without article. */
  name: string;
```

Two fields, two concerns. The uniqueness gate is keyed on the name only because
the id is *derived* from it — `packages/chord/src/analyzer.ts:3897`:

```ts
// Keyed on the LOWERCASED name, matching the `id` derivation this gate
// used to test directly (`nameWords.join('-').toLowerCase()`) ...
this.registerUnique('entity', nameWords.join(' ').toLowerCase(), ...)
```

So nothing downstream needs to change. The IR, the loader, and the world model
are already shaped for an id that is not the name. What is missing is one line of
author-facing syntax and the consequent unkeying of that gate from the display
form.

## Why the workaround is not acceptable here

Suffixing the duplicates — `Mine 1`, `Mine 2`, `Mine 3` — changes visible text,
because a room's short name is what the original prints when the player
re-enters a room they have seen (`UNDERG.BAS` line 990 selects `room*100+50`).

In UNDERGROUND that affects **27 of 87 rooms**:

| Count | Name | Rooms |
|---|---|---|
| 11 | `You are in a maze of twisty little passages, all alike.` | 61-71 |
| 5 | `Dead end.` | 72-76 |
| 3 | `Mine` | 25-27 |
| 2 | `Forest.` | 6, 7 |
| 2 | `E/W tunnel` | 21, 22 |
| 2 | `You are in a passage with only one exit.` | 59, 60 |
| 2 | `Closet` | 80, 81 |

For the mines and the closets the deviation is cosmetic. For the maze it is not.
Eleven rooms that announce themselves identically **are** the puzzle — it is the
Colossal Cave maze, the most-copied structure in the form. Numbering them
`Maze 61`..`Maze 71` hands the player the map, turning a wording deviation into a
gameplay one. No ledger entry makes that acceptable.

The same shape will recur in any port of a period game, and in any new story with
a maze, a row of identical cells, a corridor of unmarked doors, or a set of
interchangeable NPCs ("a guard").

## Candidate shapes

Not a proposal — the language's owner picks. Recorded so the decision has
something concrete to react to.

1. **An `id` line inside the create block.** The name stays the display form; the
   id is authored when it must differ.
   ```
   create the Maze 61
     a room
     id maze-61
   ```
   Wrong way round for this case: the *name* is what needs to repeat.

2. **A `named` line.** The `create` head becomes the identifier, and `named`
   supplies the printed form.
   ```
   create the Maze 61
     a room
     named You are in a maze of twisty little passages, all alike.
   ```
   Reads naturally, keeps `create the X` as the thing every other construct
   already refers to by, and leaves existing stories untouched — additive, a
   minor by ADR-257 D2's ordinary rule.

3. **Allow duplicate names, disambiguate references.** Rejected on sight: every
   cross-reference in the language (`in the Mine`, `north to the Mine`) resolves
   by name, so this trades one gap for an ambiguity in every reference.

Shape 2 is the one that fits the existing grammar with the least disturbance.

## What it costs

A grammar change, so: owner approval, an entry in
`docs/architecture/chord-grammar-changes.md`, a `CHORD_LANGUAGE_VERSION` bump
(additive → minor → 3.7.0), the `chord.ebnf` surface pin re-recorded, and a
publish of `@sharpee/*` before the `underg` repo can consume it — this port takes
Chord from npm, by the placement decision recorded in `plan.md`.

## Until it is decided

Phase 3 is blocked on the naming scheme, because it determines how all 87
`create` blocks are written. The rest of Phase 2's output — the decoded world,
the verb mapping, the O-register — is unaffected and complete.
