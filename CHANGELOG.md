# Changelog

**One entry per version, newest first.** *What a reader of a released artefact needs: what it can
do, what changed, and what is known not to work.* **The permanent record of how each change was
arrived at is elsewhere** — `docs/milestone-*/`, the phase notes, and `docs/bugs/`. *This file does
not repeat them; it says what shipped.*

**The version lives in exactly one place**, `pyproject.toml`, and reaches the running process
through `importlib.metadata`. *It is printed at startup, written into every `calls.csv` row as
`router_version`, and returned by `--version`.*

---

## 0.2.0 — 2026-09-22

***The corpus, the offline tools, the installer, and the rate-limit header recorder.***

**Added**

- ***The body store.*** **Every request and reply archived as opaque, content-addressed, per-call
  files, compressed against a shared dictionary** — *without parsing a payload and without special
  storage infrastructure.* Off by default. *Phase 10.*
- ***Offline tools over the store.*** **`extract` selects calls out of a corpus by session, model,
  agent or path and writes them where a person can read them** — bodies, or JSONL. *Dictionary
  training and retraining alongside. Phase 11.*
- ***Installable.*** **`ilirium-llm-router` as a console script, with `check` validating a config
  and printing it without starting a server.** *Phase 12.*
- ***The Anthropic rate-limit response headers, recorded.*** **A reply of `400` or worse is logged
  with `retry-after` and the `anthropic-ratelimit-*` family — an explicit allowlist of names, never
  a copy of the reply's headers**, *so the store's promise that no credential reaches disk still
  holds.* **One successful reply is sampled per process as the control**, *because without it "this
  rejection named no bucket" and "this credential is never sent buckets" are indistinguishable.*
  *Phase 14.*

**Fixed**

- ***A gzipped request body was refused with a `400` naming a field that was present.*** **The
  router reads `model` out of the body to choose a backend and was reading compressed bytes**, so a
  valid request was refused with *"carries no 'model' field"*. *The inflated copy is a throwaway —
  what arrived is what gets relayed and stored, byte for byte — capped at 4 MiB, and `br`/`zstd` are
  refused by name rather than guessed at.* **The error now says which of the two things went
  wrong.** *Phase 14.*

**Documentation, and it is the fix for `BUG-001`**

- ***`CLAUDE_CODE_ATTRIBUTION_HEADER=0` removed from five documents.*** **This repository told
  operators to set it from 2026-08-07, and it suppresses an attribution block Claude Code sends in
  its request body — which Anthropic requires on a non-streamed `POST /v1/messages`.** *The visible
  symptom was that Claude Code's auto mode could not run through the router.* **The router was never
  at fault.** *`docs/bugs/BUG-001-…`.*

**Known not to work**

- ***No run has produced a BLOCKED verdict from Claude Code's auto-mode classifier through the
  router.*** **Every classifier call measured came back at stage 1**, *so the allow path is
  demonstrated and the block path is assumed.* `docs/bugs/BUG-000-about-these-documents.md`.
- ***`content-length` is dropped from every reply, so every reply is chunked.*** *Correct for a
  streamed reply and a latent defect for a non-streamed one.* **`BKL-0040`.**
- ***Where the rate-limit headers durably live is unanswered.*** *They reach `router.log` and
  nowhere else.* **`BKL-0043`.**

*This version's number is the first that ever moved.* **`0.1.0` was set at Phase 0 and stayed there
through everything above**, so a wheel built during Milestone 2 reported `0.1.0` while carrying the
body store, the tools and the installer. *That is the defect this file exists to stop repeating.*

---

## 0.1.0 — 2026-08-07

***The core router.*** **Milestone 1, phases 0 through 7.**

- **Model-name dispatch and byte-relay.** *Anything starting with `claude-` goes to Anthropic;
  anything else to whatever LM Studio has loaded.* **No protocol translation is needed** — both
  sides speak the same API — *which the milestone measured rather than assumed.*
- **Streaming relayed untouched**, and a `HEAD /` probe answered for Claude Code's first call.
- **Three credential modes** — forward for cloud, strip for local, inject from a key.
- **A rotating log and a twenty-column `calls.csv`**, plus the failure taxonomy that classifies what
  went wrong rather than only that something did.

**What Milestone 1 settled, and both halves were measured:** *no protocol translation is needed, and
a local model can drive a real coding session through the router.*

*Set at Phase 0 and never bumped during its life — see the note under 0.2.0.*
