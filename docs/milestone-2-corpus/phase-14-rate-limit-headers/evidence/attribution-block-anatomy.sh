#!/usr/bin/env bash
# What is actually in Claude Code's attribution block, measured over the corpus.
#
# PHASE 14, 2026-09-20. Reproduces every number in `wiki/claude-code-first-party-gate.md`'s
# "The anatomy, measured over 99 blocks", and the notes section of the same date.
#
# It exists because four documents in this phase once rested on a measurement taken in a heredoc
# that nobody saved -- see commit c54f45c. This one is saved.
#
# The block is a TEXT ELEMENT INSIDE THE JSON BODY, not an HTTP header, so the corpus can answer
# this and a header capture cannot. Bodies only; the store never holds headers.
#
# Run from the worktree root, with a corpus on disk:
#     bash docs/milestone-2-corpus/phase-14-rate-limit-headers/evidence/attribution-block-anatomy.sh
#
# 2026-09-18 is the day `ANTHROPIC_BASE_URL` was set and the client withheld the block from
# everything except its two `-p` probes; 2026-09-19 is the day the hosts route made it first-party
# and every request carried one. Both are needed: the contrast IS the measurement.

set -euo pipefail

OUT="${OUT:-$(mktemp -d)}"
echo "extracting to $OUT"

for day in 2026-09-18 2026-09-19; do
    uv run ilirium-llm-router extract "logs/corpus/$day" --out "$OUT/$day" --format bodies >/dev/null
done

blocks() { grep -roh 'x-anthropic-billing-header: [^"]*' "$1" 2>/dev/null || true; }

for day in 2026-09-18 2026-09-19; do
    d="$OUT/$day"
    echo
    echo "=== $day ==="
    echo -n "requests carrying a block: "; { grep -rl "x-anthropic-billing-header" "$d" 2>/dev/null || true; } | wc -l
    echo "field names, with how many blocks carry each:"
    blocks "$d" | tr ';' '\n' | sed 's/^ *//; s/=.*//' | grep -v '^$' | sort | uniq -c
    echo -n "distinct cch values: "; { grep -roh 'cch=[0-9a-f]*' "$d" 2>/dev/null || true; } | sort -u | grep -c . || true
    echo "cc_entrypoint:"; { grep -roh 'cc_entrypoint=[^;]*' "$d" 2>/dev/null || true; } | sort | uniq -c
    echo "cc_version:";    { grep -roh 'cc_version=[^;]*'    "$d" 2>/dev/null || true; } | sort | uniq -c
done

# The suffix maps to the CALL SITE rather than to the build, which is the claim that makes
# `cc_version` underivable from the user-agent. `classifier=1` marks the auto-mode safety
# classifier, identified by its own system prompt rather than by a model name or a header.
echo
echo "=== 2026-09-19: which requests carry which cc_version suffix ==="
for s in 0a3 608 682 d18 daa; do
    echo "--- cc_version=2.1.267.$s ---"
    for f in $(grep -rl "cc_version=2.1.267.$s" "$OUT/2026-09-19" 2>/dev/null || true); do
        printf '%s classifier=%s\n' \
            "$(grep -o '"model":"[^"]*"' "$f" | head -1)" \
            "$(grep -c 'security monitor for autonomous' "$f" || true)"
    done | sort | uniq -c
done

# The two-stage pair sharing one cch is what shows cch is per TURN, not per request: same session,
# adjacent request numbers, different models, both stage 1, one value.
echo
echo "=== a cch shared by two requests, if this corpus holds one ==="
for h in $({ grep -roh 'cch=[0-9a-f]*' "$OUT/2026-09-19" 2>/dev/null || true; } | sort | uniq -d | head -2); do
    echo "--- $h ---"
    { grep -rl "$h" "$OUT/2026-09-19" 2>/dev/null || true; } | while read -r f; do
        printf '%s  %s  stage1=%s\n' \
            "$f" \
            "$(grep -o '"model":"[^"]*"' "$f" | head -1)" \
            "$(grep -c '<severity>N</severity>' "$f" || true)"
    done
done
