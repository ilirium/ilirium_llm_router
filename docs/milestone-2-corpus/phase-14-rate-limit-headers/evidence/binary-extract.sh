#!/bin/sh
# Print readable context around a string in a Bun-compiled Claude Code binary.
#
# Claude Code ships as a single-file Bun executable with its JavaScript bundle
# embedded in plaintext, so `grep -a` finds source and `dd` lifts the context.
# No unpacking, no dependency, nothing installed.
#
#   ./binary-extract.sh <pattern> [bytes-before] [bytes-after] [max-hits] [binary]
#
# Byte offsets are a property of ONE build. They are recorded in
# claude-code-first-party-gate-2026-09-18.txt only so a reader can tell two hits
# apart; re-run this rather than trusting them against another version.

PAT="$1"; BEF="${2:-400}"; AFT="${3:-800}"; MAX="${4:-3}"
BIN="${5:-$(command -v claude)}"

[ -n "$PAT" ] || { echo "usage: $0 <pattern> [before] [after] [max-hits] [binary]" >&2; exit 2; }
[ -r "$BIN" ] || { echo "$0: cannot read binary: $BIN" >&2; exit 2; }

grep -a -b -o -F -- "$PAT" "$BIN" | head -n "$MAX" | while IFS=: read -r off _; do
  start=$(( off > BEF ? off - BEF : 0 ))
  echo "=== offset $off ==="
  dd if="$BIN" bs=1 skip="$start" count=$(( BEF + AFT )) 2>/dev/null \
    | tr -c '\11\12\15\40-\176' '.'
  echo
done
