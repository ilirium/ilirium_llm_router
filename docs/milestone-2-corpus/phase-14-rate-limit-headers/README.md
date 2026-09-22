# Phase 14 — the rate-limit headers, and the bug that turned out to be ours

***This phase did not merge, and that was a decision rather than an accident.*** **Its branch,
`unmerged/phase-14-rate-limit-headers`, is kept unmerged as an archive** — *nothing on it is reverted,
every experiment still runs, and every measurement is still there.* **This file is what `main` keeps
of it: why it opened, what was done, what was concluded, and what crossed over.**

*Fork point `ac2976e`. The branch is not deleted and must not be —
`procedures/branch-index.py` refuses to render when a description names a branch that is gone.*

## Why it opened

**To record the Anthropic rate-limit response headers.** *A `429` writes `rate_limit_error: Error`
and nothing else; which bucket was exhausted and when it clears arrive in headers the router was
throwing away.* → **`BKL-0034`**.

## What it found instead, on its first day

***Claude Code's auto mode could not run through the router.*** **Its safety classifier sends a
non-streamed `POST /v1/messages`, and every one came back `429`** — *a status code that
misdescribes what was happening.* **That became the phase's subject**, and `BUG-001` is the document
it belongs to.

## What was done

| | |
|---|---|
| **Group A/B** | The header recorder — *an explicit allowlist of names, never a copy of the reply's headers* — plus a prefix catch that names an unlisted bucket without recording its value, and one sampled success per process as the control |
| **Group C** | Reproduce and measure. *Five driven sessions, frozen into `evidence/`* |
| **Group C2** | ***Thirteen hypotheses eliminated one at a time*** — quota, request size, the model, HTTP/2, `accept-encoding`, a non-browser TLS fingerprint, the router inventing the rejection, the first-party flag, and more. **None of them was it** |
| **Group C3** | The hosts route: `/etc/hosts` plus a TLS terminator, so the client believes it is talking to Anthropic directly while every byte still crosses the router |
| **Group C4** | The router putting the attribution block back itself. **Built, and measured working** |

***And two real defects were found along the way***, neither of which was the thing being chased:
**a gzipped request body was refused with a `400` blaming a `model` field that was present**, and an
experiment that relayed the caller's `accept-encoding` served brotli to a client that could not read
it.

## What it concluded

***`CLAUDE_CODE_ATTRIBUTION_HEADER=0`, in this repository's own `README.md` since 2026-08-07.***
**It suppresses an attribution block Claude Code sends in its request body; Anthropic refuses a
non-streamed `/v1/messages` that arrives without one.** *The operator had been setting it on every
run, because we told him to.*

**Proved twice, on 2026-09-21, and in both directions:**

- ***By intervention*** — the router supplying the block from its own side carried **12 / 12**
  non-streamed calls to `200` while the variable was still set.
- ***By isolation*** — **the same router process**, no restart, one environment variable: **33 × 429
  with it, zero without it.**

***So the router was never at fault, and the fix was deleting a line from five documents.***

## What crossed over to `main`, and what deliberately did not

| Crossed | |
|---|---|
| **The gzip `400` fix** | *A live defect in `peek`, which every request crosses — not experiment scaffolding.* **A client that gzips its body got a `400` about a field that was there** |
| **The header recorder** (Group A/B) | *What the phase was opened to build.* **It reaches `router.log` and nowhere else; the durable home is `BKL-0043`** |
| **The documentation fix** | *Five documents lost the line; Phase 1's evidence was **annotated instead**, because it records a session that actually ran* |
| **`BUG-001`** | Rewritten with the cause and the resolution |
| **`branch-index.py`, `backlog-index.py`, `IDM-011`** | *Tooling fixes the phase made in passing, and one of them — the per-section ordering rule — is why `main` can file a backlog item in its right section at all* |
| **`BKL-0039`–`0042`** | The backlog items the phase raised |

| Stayed on the branch | Why |
|---|---|
| **Group C4, the attribution injection** | ***Measured working, and unnecessary once the line is gone.*** *A router that needs no code to fix this is the better outcome — but the code is kept, because the behaviour it works around is somebody else's and could return* |
| **The three failed experiments** | *`relay_accept_encoding`, `http2_upstream`, `imitate_attribution_headers` — negative results, kept switchable so they stay reproducible* |
| **The hosts route and its TLS terminator** | *The fallback if the attribution behaviour ever changes, and the instrument for finding out what replaced it* |
| **The investigation record** | *`notes.md`, `plan.md`, twenty-four `for-the-owner.md` entries, and an `evidence/` folder of frozen runs* |

## Beside this file

**`git-refs-and-the-history-rewrite.md`** — *written from the owner's questions at the close-out.*
**How refs and namespaces actually work, why `git branch -a` does not show a tag or an invented
namespace, why a history rewrite copies commits rather than moving them, and every command the
sanitization used** — *with the two refs that still hold the pre-rewrite ids and what deleting them
would mean.*

## Two things a reader of that branch needs to know

***Every session id and request id on it is SYNTHETIC***, replaced 2026-09-22. **The real ids are in
`logs/`, which is gitignored and per-worktree**, and the mapping is deliberately outside git — *so an
id in a document there cannot be used to find a corpus folder without it.*

***There is still no BLOCKED verdict anywhere in the record.*** **Every classifier call measured
came back at stage 1**, so *the allow path is demonstrated and the block path is assumed.* **That is
`BUG-000`'s standing warning** — an absence of failures is not a result — *and it is the one
question the phase left open.*
