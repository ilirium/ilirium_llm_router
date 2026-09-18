# Phase 14 — evidence

| | |
|---|---|
| **`mutation-check.py`** | Does Group B's test set test anything? Six deliberate defects, each with the test that has to die. **Reports "mutation applied" and "check failed" separately**, because Phase 13's harness silently never applied its mutations and that looks identical to a clean pass. Re-runnable: `python3 docs/milestone-2-corpus/phase-14-rate-limit-headers/evidence/mutation-check.py` from the worktree root |

## `rate-limit-headers-2026-09-18.txt`

**What produced it.** One driven Claude Code session through the router built from this branch, auto
mode on, 2026-09-18 11:02–11:05 UTC. **Claude Code 2.1.267, router 0.1.0**, backend `anthropic`,
`credential: forward` — an OAuth subscription token. Run by the owner; Group C is not a session's to
run.

**What it proves.** Twelve `429`s, and **every one carries `request-id` and nothing else.** No
`retry-after`. No `anthropic-ratelimit-*` header of any kind — not even an unlisted one, which would
have rendered as `<unlisted>`.

**What was redacted.** Nothing. The lines are verbatim. `request-id` values are Anthropic's own
correlation ids, carry no credential, and are **the thing an upstream report needs**.

**Regenerable?** No — it is a record of one session. The instrument that made it is re-runnable.

## `calls-2026-09-18-redacted.csv`

**What produced it.** `logs/telemetry/calls.csv` from the same session, complete: **22 rows**,
11:02:33 to 11:05:45 UTC.

**What it proves.** `BUG-001` reproduces on current versions: **12 non-streamed `/v1/messages`,
all 429; 8 streamed, all `ok`**, in the same three-minute window. The retry signature the bug
predicts is visible — five attempts at `claude-sonnet-5` and 128,250 bytes, then five at
`claude-opus-5` and **128,248** bytes, *a two-byte difference which is exactly the model-name length
difference*.

**What was redacted, and how.** `session_id` only — 2 distinct values, mapped to `session-01` and
`session-02` in order of first appearance. Nothing else altered. Verified after redaction: 22 rows
present, all 12 `429`s present.

**Regenerable?** No. Same session as above.

---

***What this evidence does not settle, said here so its silence is not misread.*** **Whether a
*successful* reply on this credential carries `anthropic-ratelimit-*` headers is unmeasured** — the
instrument fires only at `>= 400`, by design, and that design is what leaves the gap. Until it is
closed, *"the 429 names no bucket"* is a fact and *"Anthropic normally names one"* is an assumption.
**The control is one short run**; see `../notes.md`.
