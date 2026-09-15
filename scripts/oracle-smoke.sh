#!/usr/bin/env bash
# oracle-smoke.sh — build the BASIC-PLUS interpreter and replay a fixed command
# sequence through the unmodified 1979 UNDERGROUND source, diffing the result
# against a recorded golden transcript.
#
# This is the REAL-PATH test for the oracle: it compiles bplus.c and runs the
# actual interpreter against the actual UNDERG.BAS/LOOK.BAS, with no stub or
# substitute anywhere in the path. Phases 6-7 generate branch-tester cards from
# this same binary, so a silent change here would silently corrupt the card
# corpus. Run it before trusting any generated assertions.
#
# Usage: scripts/oracle-smoke.sh [--accept]
#        --accept rewrites the golden from the current output (review the diff).
set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
src="$repo/original"
golden="$repo/tests/golden/oracle-smoke.txt"
actual="$(mktemp)"
trap 'rm -f "$actual"' EXIT

cc -O2 -o "$src/underg" "$src/bplus.c" -lm

# UNDER?.DAT are save files the game allocates at run time; a leftover one
# changes the password letter line 20 hands out, so the run is only
# reproducible from a clean slate.
rm -f "$src"/UNDER?.DAT

( cd "$src" && printf 'N\nW\nLOOK\nE\nN\nTAKE LAMP\nINVEN\nXYZZY\n' | ./underg ) > "$actual" 2>&1

rm -f "$src"/UNDER?.DAT

if [ "${1:-}" = "--accept" ]; then
  cp "$actual" "$golden"
  echo "oracle-smoke: golden updated"
  exit 0
fi

if diff -u "$golden" "$actual"; then
  echo "oracle-smoke: OK — oracle output matches golden"
else
  echo "oracle-smoke: FAIL — oracle output drifted from golden" >&2
  exit 1
fi
