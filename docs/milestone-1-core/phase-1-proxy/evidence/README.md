# Phase 1 evidence

| File | What it is |
|---|---|
| `session-results.md` | The transcript of running `../../../procedures/testing-against-claude-code.md` on 2026-07-29 — the run that first proved the router works end to end |

## What it proves

Phase 1's "done when" was *point Claude Code at the router and have a session behave normally*, which
no test can supply. This file is that run: the `HEAD /` probe answered, a streamed reply arriving
incrementally under `curl -N`, and then a real session on both backends.

Two results in it outlived the phase. **Streaming was confirmed incrementally by curl rather than
inferred from Claude Code's display** — the display would look the same either way. And a local model
(`google/gemma-4-e4b`, 34304-token window) ran a real coding session, writing and reading files,
running bash commands, and running a Python script and reading its stdout.

## How to read it, and what not to do with it

**It is captured output, so it is never edited** — not even to repair a path that has since moved. A
command line in here is what was actually run on the day, and rewriting it would falsify the record.
The procedure it came from is a live document and does get updated: `../../../procedures/testing-against-claude-code.md`.

**Regenerable, unlike the other phases' evidence.** Re-running the procedure produces a fresh
equivalent, because nothing here depends on a state that has passed. That is why it is one file rather
than a frozen directory, and why nothing in it is cited for a number — the numbers Milestone 1 quotes
come from the Phase 2 session and the Phase 4 and 5 runs, which are not reproducible.

**Nothing is redacted here**, because nothing needed it: the session used a local model, so no
credential and no account identifier appears. Contrast `../../phase-2-observability/evidence/step-6-session/`,
whose README records the placeholder mapping it required.
