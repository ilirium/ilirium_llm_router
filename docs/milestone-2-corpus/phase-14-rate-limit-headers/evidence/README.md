# Phase 14 — evidence

| | |
|---|---|
| **`mutation-check.py`** | Does Group B's test set test anything? Six deliberate defects, each with the test that has to die. **Reports "mutation applied" and "check failed" separately**, because Phase 13's harness silently never applied its mutations and that looks identical to a clean pass. Re-runnable: `python3 docs/milestone-2-corpus/phase-14-rate-limit-headers/evidence/mutation-check.py` from the worktree root |

**The measurement is not here yet.** Group C — one driven Claude Code session with auto mode on —
produces the response headers on a real `429`, and Task 8 freezes them into this directory,
redacted per `../../../README.md`.

***Until that lands this phase has an instrument and no finding.*** *A capture that exists only in
one worktree's gitignored `logs/` discharges nothing; this milestone has recorded that failure once
already, in `../../implementation-plan.md`'s step-2 row.*
