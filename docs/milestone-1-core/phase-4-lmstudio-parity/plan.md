# Phase 4 plan — checking what LM Studio actually supports

Written 2026-08-06, before the phase starts. `implementation-plan.md` says what Phase 4 is for; this
says how it will be run and in what order. Findings go in `phase-4-notes.md` as they are measured.

**Completed the same day.** The boxes below are ticked as they were done, and two are not ticked
because they could not be: the 8192 reload is not reachable from the CLI, and the replay never failed
so there was nothing to bisect. Both are recorded rather than quietly dropped. **Read
`phase-4-notes.md` for the results** — this file is the plan, kept as written plus its outcomes.

Branch: `feat/phase-4-lmstudio-parity`, off `main` at `cc65aed`. Merge back with `--no-ff`.

This is a **measurement phase**. Almost nothing here is code. The output is an honest list of what a
local backend does and does not support, and the plan's own instruction is to fix nothing unless
something is genuinely broken — no general translation layer, which was ruled out for good reason.

## Setup

**Model: `qwen/qwen3.5-9b`**, decided 2026-08-06. It is the only one needed: `vision`,
`trained_for_tool_use` and `reasoning` are all supported, so one model exercises every unmeasured
item. Its `reasoning` default is **on**, which makes the thinking probe a real test rather than a
hypothetical.

**Context: 44544 tokens**, as currently loaded, and no reload needed for steps 1–3. It is ~14k above
the ~30k fixed preamble, so the captured request replays with room to answer — and it comfortably
clears the 41003 `input_tokens` the frozen session already reached on this model. The window is not
the subject until step 4, which moves it deliberately.

**One deliberate reload, at step 4 only:** down to **8192**. Reaching a 44544-token window costs
~180 KB of text and a multi-minute prefill per attempt — LM Studio's median time to first byte was
37 s in Phase 2, and one 31 KB body took 111 s. The behaviour at the edge is the same wherever the
edge is, so move the edge somewhere cheap to reach.

**Out of scope, deliberately:** the credential config shape. It is agreed and unbuilt, and it is a
config refactor in a phase where every other change is a measurement — mixing them makes a failing
probe and a config change hard to tell apart. Next phase.

## Already measured — not retesting

Checked 2026-08-06 against `phase-2-step-6-session/calls.csv`. That session ran **99 calls against
`qwen/qwen3.5-9b`** — this phase's model — from real Claude Code. It answers more of Phase 4 than the
plan it was written under expected, which is the same shape of finding as Phase 3.

| Question | Answer from the frozen rows |
|---|---|
| Does a real Claude Code request work against LM Studio? | **Yes.** 95 `ok`, 4 `client_disconnect` — those an interrupt, not a rejection |
| Do tool results round-trip? | **Yes.** Eight `tool_use` rows, each followed by a turn whose `request_bytes` grows — 154 → 157 → 159 → 161 → 162 → 164 KB — which is the result being fed back and accumulating |
| Does a realistic preamble work? | **Yes, and larger than planned.** `request_bytes` max 170 KB, `input_tokens` max 41003 — above the 118 KB captured request |
| Does prefix caching survive the relay? | **Yes.** 24 rows with non-zero `cache_read`, max 40879 tokens |
| Does multi-turn hold together? | **Yes** — a long conversation, model switching, subagents, and a local model asked about earlier messages |

**So there is no fresh Claude Code session in this phase.** It was step 5 of an earlier draft and has
been removed: it would re-answer questions that already have answers. Run one only if a probe below
turns up something whose consequence is visible to a user.

**The one limit of that evidence, and why step 2 survives anyway.** The router logs metadata, never
bodies. Those rows prove *real Claude Code requests succeeded*; they cannot prove *a request
containing `context_management` succeeded*, because nothing recorded what was in them. That gap is
the subject of `EPD-003`. `log-the-whole-request.txt` is the one body that can be read, so replaying
it tests known content rather than assumed content.

## TODO

### 1. The probe instrument

- [x] Branch, and fix the one stale line in `handoff.md` that still calls Phase 3 unmerged
- [x] `../../procedures/lmstudio-capability-probes/` with a runner that sends a body through the
      router and records status, headers, the stream and the CSV row. Committed, following
      `phase-3-verification/` rather than
      `phase-2-step-6-session/`: this is a tool to re-run, not frozen evidence, because every finding
      here expires the next time LM Studio ships a release

### 2. Replay the whole captured request

- [x] Send `log-the-whole-request.txt` through the router with the model swapped to the local id
- [x] Record what came back

One request carries four of the phase's questions at once — a `role: "system"` message inside
`messages`, the ten-entry `anthropic-beta` header, `context_management` / `output_config` /
`metadata.user_id`, and `cache_control` on the system blocks. Its realistic size no longer needs
testing; the frozen session already went 170 KB. What it adds over those rows is that its contents
are **known**, so a success names the fields that survived.

- [n/a] **If it fails:** bisect by removing one element at a time — the only form of the finding
      worth having. **It did not fail**, so there was nothing to bisect

### 3. The probes the replay cannot isolate

Small bodies, a few hundred bytes each — the question is whether LM Studio accepts the shape, not
whether it works at scale, and a small body answers it in seconds rather than minutes.

- [x] `thinking: {"type": "adaptive", "display": "omitted"}` — accepted or rejected, and whether
      qwen's reasoning surfaces as `thinking` content blocks in the stream at all. The CSV records no
      content, so the frozen session cannot answer this however many times it is read
- [x] An image content block, base64. A coding session sends none, so this is untouched by prior runs
- [x] Each unusual body field alone, so a rejection names the field rather than the request
- [x] A `role: "system"` message inside `messages`, alone, if step 2 did not settle it

`tool_result` was on this list and has been removed — the frozen session measured it, see above.

### 4. The truncation boundary

The one item with a consequence rather than a curiosity, and the mechanism behind `EPD-002`.

- [~] Reload at 8192 — **not possible from the CLI**; `lms load -c 8192` is silently ignored,
      LM Studio's saved per-model config wins. Measured at the real 44544 window instead
- [x] Put a distinctive needle near the start of a conversation, grow it past the window, ask for the
      needle back
- [x] Compare the `input_tokens` LM Studio reports against what was actually sent
- [x] Record which it is: silent trimming, or a loud error

Silent trimming degrades answers without ever failing, which is why this is worth the reload. A loud
error is the good outcome.

### 5. Write it up

- [x] `notes.md` — procedure and findings, including everything that did not work, and including
      that a third of this phase was already answered by a session run for another one.
      Phase 3 found four of its five items already built; this is the second instance, and a pattern
      worth naming rather than being surprised by a third time
- [x] The parity table into `CLAUDE.md`, replacing the "still unmeasured" list
- [x] `handoff.md`
- [x] Revisit `EPD-001` and `EPD-002`, both of which name Phase 4 as what they wait on. Revisit, not
      decide — an EPD is accepted deliberately or not at all

One fact for `EPD-002`, **corrected 2026-08-06 from an earlier draft of this line**, which claimed
the document was written without knowing the context length is machine-readable. It was not: EPD-002
already cites `GET /api/v1/models` and its `max_context_length`.

The real finding is narrower and worse. EPD-002's scaled option computes
`true_tokens × 200000 / real_context_length` and takes `real_context_length` from
**`max_context_length`** — 262144 for `qwen/qwen3.5-9b`. That is the model's *maximum*, not the
window it is *loaded* with, which is `loaded_instances[].config.context_length` and was 44544 here.
Scaling by the larger number would report a window roughly six times too big, which is the very error
the scaled option exists to fix. The two fields are one line apart in the same response and mean
different things.

## Done when

There is an honest written list of what works locally and what does not — including the things that
do not, stated plainly rather than left out.
