# Project Profile

**Generated**: 2026-09-14
**Repository**: underg

## Domains

- Not yet established — repo contains only DevArch scaffolding (`.devarch/`, `CLAUDE.md`, `docs/`) and no source code, manifests, or config files.
- Stated intent (`docs/work/overview.md`): port a PDP-11/RSTS BASIC-PLUS interactive fiction game ("Underground") to "Chord." Source material referenced: https://github.com/gschmidl/interactive-fiction/tree/main/Underground%20(Scans)
- Once implementation begins, likely candidate domains include **Domain Modeling** (game world/entities: rooms, objects, parser state) and possibly **CLI / Tooling** or **API / Service** depending on how "Chord" surfaces the game, but neither is confirmed by any file in the repo today.

## Tech Stack

- **Language**: Not yet established — no source files or manifests present.
- **Runtime**: Not yet established.
- **Framework**: Not yet established. "Chord" is named as the port target in `docs/work/overview.md` but is not otherwise defined anywhere in this repo (no dependency, config, or doc clarifies whether it is a language, engine, or library).
- **Data layer**: Not yet established.
- **Messaging**: None detected.
- **Test framework**: Not yet established.
- **Test command**: NONE — repo has no code, no package manifest, and no toolchain of any kind yet; this is a pre-implementation scaffold, so there is nothing runnable to gate on.
- **Build tool**: Not yet established.
- **Package manager**: Not yet established.
- **CI/CD**: None detected — no `.github/workflows/`, `Jenkinsfile`, or `.gitlab-ci.yml`.
- **Monorepo**: No — single flat repo, no `packages/`/`apps/`/workspace config.

## Conventions

- **Test location**: N/A — no tests exist.
- **Test naming**: N/A.
- **Source structure**: N/A — no `src/`, `lib/`, or similar directories exist yet.
- **TypeScript strict mode**: N/A — no `tsconfig.json` present.
- **Import style**: N/A.

## Mutation Signatures

No domains are established yet, so no mutation signatures can be derived from evidence. Re-run `dev-context-detector` once source code, a package manifest, or a "Chord" toolchain definition lands in the repo — the domains and signatures below are placeholders to revisit at that point, not active guidance:

### Domain Modeling (anticipated, not yet evidenced)
- **Mutation calls**: game-state transitions (room changes, inventory updates, flag/variable sets) once a domain model exists.
- **Reporting without mutation**: narrator/output text printed without an underlying state change.
- **Test assertions — verify**: state after a command (player location, inventory contents, world flags), not just command output text.
- **Test assertions — insufficient**: asserting only that a parser "prints something" or "doesn't throw" without checking the resulting game state.

## Notes

This repository is a pre-implementation scaffold created by `devarch init`. The only substantive content is `docs/work/overview.md`, which records the intent to port the PDP-11/RSTS BASIC-PLUS interactive fiction game "Underground" to "Chord." No stack, language, or framework decision has been made in-repo yet — do not infer one. This profile should be regenerated as soon as a manifest, config file, or source directory appears, since every field above will change at that point.
