# What is on the plate

Written 2026-08-07, with all four phases merged and the tree clean. An audit of what is actually
outstanding, read off `handoff.md`, `phase-4-notes.md`, `docs/epd/`, and the code itself.

It exists because "the phases are done" and "there is nothing left" are different statements, and
after four phases the difference has spread across six files. This is the one place that lists it.

**This is a survey, not a plan.** What to do about the first two items is `phase-5-plan.md`.
Everything else here is deliberately left where it is, with its reason.

**The distinction that organises the list:** most of what remains is *not work*. It is decisions
waiting on a person, and measurements waiting on a reason. Two items are unambiguously work, and
they are the only two that go into Phase 5.

## Agreed work, not yet written — this is Phase 5

**1. The credential config shape.** Decided 2026-07-29, still unbuilt. `config.py:41-42` carries the
old two-knob shape — `credential: Literal["forward", "strip"]` and an independent `api_key_env` — in
which the key silently wins at `proxy.py:348`, so `credential: forward` alongside a configured key
reads as "forward the caller's token" and does not do that. The agreed replacement is one field with
three modes (`forward` / `strip` / `inject`), `api_key_env` required by `inject` and forbidden by the
others, contradictions refused at startup with a message naming the fix. Full rationale under
"Design decisions" in `CLAUDE.md`.

With one backend needing authentication this was a wart. With the several that are planned it is a
trap, which is why it was promoted from "untested extra to consider deleting" to a design decision.

Worth flagging alongside it: **the key path has never carried a live request.** LM Studio's "Require
Authentication" was switched *off* rather than configured around, so `inject` is covered by a unit
test and nothing more. Switching that setting back on is the cheap way to actually exercise it.

**2. The 600-second read timeout.** `proxy.py:81`. Phase 4's one real defect, found 2026-08-06 and
deliberately left. A ~41000-token request against a 44544-token window was killed at exactly
`read=600.0` while LM Studio was healthily prefilling, so **the usable context of a local model is
bounded by time rather than by its window**. Three candidate fixes named, no decision taken.

It is not a one-line bump: the same number is what makes a wedged backend fail in bounded time, and
Phase 3 chose it on purpose. What Phase 4 contributes is that the number is reachable by *ordinary*
traffic, which is not what it was chosen against.

**These two belong together.** Both are small, both touch configuration, neither is a measurement —
and mixing a config change into a measurement phase is exactly what Phase 4 refused to do.

## Decisions waiting on a person — the three EPDs

None of these is blocked on work. Each is blocked on somebody deciding.

| | Blocked on | Note |
|---|---|---|
| `EPD-001` — model selection and mixed-model sessions | **a decision only** | Its gate was "Phase 4 shows a local model can hold a real session". Phase 4 did, so the reason for waiting is discharged. Per-request dispatch already satisfies half of it with no code |
| `EPD-002` — token counting for local backends | **a decision on a weakened case** | Phase 4 measured the harm it was organised around and found none — the context boundary refuses cleanly rather than trimming silently. Its addendum also records that the proposal reads `max_context_length` where it needs the loaded `context_length` |
| `EPD-003` — capturing bodies for a corpus | **a decision, plus its own gate** | The decision is whether the fine-tuning half survives Anthropic's terms. The gate is a twenty-minute measurement: whether a trained zstd dictionary recovers the cross-body compression ratio for per-file storage. If it does not, per-call files are the wrong unit and the sketch in that document does not survive |

## Measurements Phase 4 left open

Its own honest list, carried here so it is not lost in a phase document.

- **Whether trimming happens below the context boundary.** The run meant to check it hit the read
  timeout instead. The boundary itself refuses cleanly; the region just under it is uncharacterised.
  **This one is blocked by item 2 above**, which is the useful sequencing fact in this whole file.
- **Whether Claude Code shows LM Studio's context error.** It arrives as an SSE `error` event inside
  an HTTP 200 — the shape Phase 3 measured being ignored — but as the *sole* event, with no
  `message_start` before it, where Phase 3's case followed partial content. Whether the client treats
  those alike is unknown, and it decides whether the most useful message LM Studio produces is ever
  seen.
- **Non-streaming replies.** Every Phase 4 probe ran streamed. `docs/phase-4-probes/probe.py:297`
  already has `--no-stream` and it was never used; the recorder takes a different path for buffered
  replies and LM Studio reports `usage` differently there.
- **Other local models.** All of Phase 4 is `qwen/qwen3.5-9b`. `capabilities` in
  `GET /api/v1/models` varies per model — several have no `vision`, several no `reasoning` — so
  nothing in the honoured/ignored table transfers without re-running the probes.

## Smaller loose ends, each with its reason for staying put

- **Prompt-cache warmup probes cost 44% of local wall-clock time** — 40 calls returning zero content
  tokens, 20.0 of 45.5 minutes, in the frozen step 6 session. Recorded in `CLAUDE.md` under "No
  special case for background/auxiliary traffic" as an argument *against* that decision rather than a
  bug in it. It has no owner. Fixing it would mean the first special case in the dispatch rule, in
  exchange for nearly half the local wall clock — a real trade, and nobody has taken it.
- **The per-backend authentication header name.** `inject` means `Authorization: Bearer` today, which
  suits LM Studio and OpenAI; Anthropic's native key is `x-api-key` and Gemini's is
  `x-goog-api-key`. Deliberately unanswered: it is needed before the second cloud provider, not
  before. Phase 5 must not accidentally settle it — see the plan's "Out of scope".
- **The Anthropic 429 rate-limit headers** — `anthropic-ratelimit-*` and `retry-after`, which the
  router never records because it tees bodies and not headers. Marked **do not go looking** in
  `handoff.md`: the recorder now keeps the body's symbolic type, so the next 429 through the router
  writes `rate_limit_error: Error` into the CSV by itself, measured instead of reconstructed.
- **`handoff.md` is self-terminating by design.** Its own first paragraph says to delete it once the
  project has enough code to speak for itself. Not yet — it still carries session state nothing else
  holds — but it is worth knowing that is the intended end.

## The pattern that keeps repeating, and what it implies for this list

Phase 3 found four of its five work items already built by Phase 2. Phase 4 found a third of its plan
already measured by Phase 2's frozen session — reading `phase-2-step-6-session/calls.csv` before
running anything deleted a whole step and one probe.

**So the honest reading of the measurement list above is that some of it may already be answered**,
in artefacts committed for another purpose. The cheap habit, now three phases old: before planning a
run, grep the frozen CSVs for the same model and the same question.

Its limit is equally worth knowing. The router logs metadata and never bodies, so those rows can
prove *a real request succeeded* and can never prove *a request containing a particular field
succeeded*. That gap is exactly what `EPD-003` proposes to close.
