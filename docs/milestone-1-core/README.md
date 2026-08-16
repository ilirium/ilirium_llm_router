# Milestone 1 — the core router

**2026-07-27 to 2026-08-07.** Seven phases, from an empty repository to a router that Claude Code
uses as its only endpoint while reaching both Anthropic and a local model.

## What it set out to prove, and what happened

The central claim was falsifiable and could have come out false:

> **No protocol translation is needed, and a local model can drive a real coding session.**

Both halves held. LM Studio implements Anthropic's `/v1/messages` closely enough that the router is a
**model-name dispatcher**, not a translator — request bytes are relayed untouched and replies streamed
back as they arrive. And a local model ran a real session: reading and writing files, running bash
commands, running a Python script and reading its output, with multi-turn conversation holding
together.

Three things were established that the claim did not anticipate:

- **A single session reaches both backends at once**, measured rather than argued — two sessions in
  the frozen CSV have rows against each.
- **Prompt caching pays for the byte-relay decision**, end to end: the same request twice, 27904 of
  27924 tokens served from cache, time to first byte cut four-fold.
- **The expensive thing about a local backend is time, not money.** Warmup probes that return nothing
  cost 44% of local wall-clock time in one session, and the usable context of a local model is bounded
  by prefill time before it is bounded by the window.

## What is in this archive

Process and state: how the work was sequenced, and what was believed while it was happening. **A
phase note is never edited again** — corrections live in `../reference/`, which is what other
documents cite.

| | |
|---|---|
| `implementation-plan.md` | The phases and their "done when" — one plan per milestone |
| `closing-notes.md` | The running handoff, frozen at the boundary |
| `outstanding-work.md` | The survey that picked Phase 5's items; its live entries became `../backlog.md` |
| `docs-restructure-plan.md` | The migration that created this archive |
| `phase-N-<slug>/` | `notes.md`, `plan.md` where one exists, and `evidence/` |

**Where everything else went.** Durable facts were harvested into `../reference/`; instruments meant
to be re-run went to `../procedures/`; the raw captured request is in `../captures/`. The EPDs did
**not** move — they are the input to Milestone 2, not residue of Milestone 1.

## The phases

| Phase | Branch | Merged as | What it settled |
|---|---|---|---|
| 0 | `feat/phase-0-skeleton` | fast-forward, tip `fc65233` | The uv project, config loading, the CLI. No notes file — it is a section of `implementation-plan.md` |
| 1 | `feat/phase-1-proxy` | fast-forward, tip `8d335ab` | Dispatch working end to end: the `HEAD /` probe, `POST /v1/messages` by model name, a catch-all, byte relay and streaming. Verified in a real session on 2026-07-29 |
| 2 | `feat/phase-2-observability` | `4d7d7f6` | The rotating log and the twenty-column CSV. Its step 6 session — long, both backends, subagents, an interrupted response — is the evidence half the project still rests on |
| 3 | `feat/phase-3-failure-handling` | `cc65aed` | The failure taxonomy, and that **four of its five planned items were already built** by Phase 2. Measured what Claude Code actually does with an error: retries a 502 ten times, ignores a mid-stream `error` event |
| 4 | `feat/phase-4-lmstudio-parity` | `50444c5` | What LM Studio supports, measured instead of guessed. **Nothing was rejected**; the gaps are things accepted and not honoured. Found the router's read timeout reachable by ordinary traffic |
| 5 | `feat/phase-5-config-and-timeouts` | `c8401e9` | The three credential modes built and carried live against an authenticated LM Studio, and `read_timeout` made per backend — which unblocked ruling out silent trimming below the context boundary |
| 6 | `feat/phase-6-review-and-cleanup` | `532dc86` | The review. Fifteen of sixteen quoted measurements reproduced to the digit; seven items fixed in about forty lines; two proposed cuts refused with the measurement that refused them |

One documentation branch belongs to the milestone too: `docs/epd-index-and-corpus-proposal`, merged as
`acb399f`, which created `EPD-000` and `EPD-003`.

## Three irregularities, so nobody concludes something was lost

**Phases 0 and 1 were fast-forwarded.** They have no merge commit — their branch tips sit directly on
`main`'s first-parent line. The `--no-ff` convention that keeps a phase boundary visible in the log
starts at Phase 2 (`4d7d7f6`) and holds for every phase after it. The branches still exist and still
carry the work; what is missing is the boundary, and it is missing because the convention was adopted
later rather than because a merge was mishandled.

**Phases 1, 2 and 3 have no `plan.md`.** Their plans were sections of `implementation-plan.md`; only
phases 4, 5 and 6 wrote a separate one. The phase template in `../README.md` describes what Milestone
2 onward should produce — this archive records what Milestone 1 actually produced.

**Phase 6 has no `evidence/`.** Its findings were re-derivations of committed artefacts and live runs
against local stubs, and they are recorded in its notes rather than as new frozen files.

## What it cost, for whoever sizes the next one

Seven phases in twelve days. **1713 lines of source across seven modules — 371 of them code** — and
**158 tests**. The router does one thing: it forwards. Most of what the milestone produced is the
record of finding out what forwarding actually requires.

The pattern worth carrying into Milestone 2 is in `../reference/lessons.md`: **four of the six
numbered phases found their own premise wrong in the first hour** — work already built, already
measured, or already misdescribed. The habit that caught it every time was checking the frozen
artefacts before planning the run.

---

*Written 2026-08-16 at commit 5 of `docs-restructure-plan.md`, before the files it indexes arrived
here at commit 10.*
