# Phase 4 notes — what LM Studio actually supports

Written 2026-08-06 **while measuring**, like `phase-3-notes.md` and unlike `phase-2-notes.md`. The
plan is `phase-4-plan.md`; the instrument is `phase-4-probes/`, which is committed and meant to be
re-run, because every finding below expires the next time LM Studio ships a release.

Branch: `feat/phase-4-lmstudio-parity`, off `main` at `cc65aed`. Merged with `--no-ff` as `50444c5`.

**The sources for the numbers that cannot be measured again are frozen in `phase-4-evidence/`** — the
cold and warm cache replays, the over-window refusal, and the read timeout. Everything else in
`phase-4-probes/runs/` is disposable and gitignored, because re-running reproduces it.

Model throughout: **`qwen/qwen3.5-9b`**, MLX 4-bit, loaded at **44544** tokens of context out of a
262144 maximum. LM Studio's "Require Authentication" is off, so no credential was configured.

## The headline: nothing was rejected

Every probe came back **HTTP 200 with no error body**, including the ones the project expected to
fail. That is the finding, and it is worth stating before the detail, because the detail is all about
things that were accepted *and then not honoured* — which is a different and quieter kind of gap than
the rejection this phase was looking for.

The check matters because a status code is not a verdict here: LM Studio answers `count_tokens` with
HTTP 200 and an error body (`epd/EPD-002-token-counting-for-local-backends.md`), so `probe.py` looks
for an error shape regardless of status. None of the probes below tripped it.

| Shape sent | Accepted | Honoured | Note |
|---|---|---|---|
| `role: "system"` message inside `messages` | **yes** | **yes** | Answered in French as the system message instructed. `CLAUDE.md` predicted this was "almost certainly unsupported" |
| Image content block, base64 PNG | **yes** | **yes** | Named four quadrant colours in the order asked |
| `thinking: {"type": "adaptive"}` | **yes** | **yes** | Real `thinking` content blocks, Anthropic's shape |
| `thinking: {"type": "enabled", "budget_tokens": 1024}` | **yes** | **no** | The budget is ignored — see below |
| `output_config: {"effort": "high"}` | **yes** | **yes, invisibly** | Turns reasoning on and bills it without showing it — see below |
| `context_management` (`clear_thinking_20251015`) | **yes** | not observable | No effect a probe can see; nothing broke |
| `metadata.user_id` | **yes** | not observable | Ignored quietly, which is all that was asked of it |
| `cache_control: ephemeral, 1h` | **yes** | **not on a small prefix** | Two identical 117-token runs, `cache_read` 0 both times |
| The ten-entry `anthropic-beta` header | **yes** | n/a | Sent on every probe above, never objected to |

## The three findings that are more than a yes

### 1. `thinking` works properly, and its budget does not

LM Studio emits real `thinking` content blocks with `thinking_delta`s, in Anthropic's shape, followed
by a `text` block. This was listed as unmeasured and it is now measured as **working**:

```
blocks         thinking, text
stop_reason    end_turn
usage          {"input_tokens": 31, "output_tokens": 3376}
```

**But nothing bounds the thinking.** `budget_tokens: 1024` with `max_tokens: 2048` produced 2047
tokens of thinking, no text at all, and `stop_reason: max_tokens`. `{"type": "adaptive"}` with
`max_tokens: 1024` did the same at 1023. The model thinks until it runs out of the *overall* budget,
and only what is left over becomes an answer.

**The consequence, which is the part that matters:** a request that asks for thinking with a small
`max_tokens` returns **an empty reply** — HTTP 200, zero content blocks, no text, `max_tokens`. Not
an error, not a warning; a well-formed message containing nothing. Claude Code sends
`max_tokens: 64000`, so it has room and this does not bite in practice. Anything more frugal does.

### 2. `output_config: {"effort": "high"}` buys reasoning that is billed but never shown

This one was expected to be ignored. It is not. Controlled against a baseline that differs only by
this field, same prompt and same `max_tokens`:

| | `output_tokens` | blocks returned | text |
|---|---|---|---|
| baseline, twice | **4** | `text` | `PROBE OK` |
| `output_config.effort: high`, `max_tokens: 128` | **127** | **none** | *(empty)* |
| `output_config.effort: high`, `max_tokens: 2048` | **216** | `text` | `\n\nPROBE OK` |

So the field switches reasoning **on** — the baseline plainly does none — and because `thinking` was
not also set, the reasoning is **not emitted as a content block**. It is still counted: 216 output
tokens for a four-token answer, ~98% of them invisible. The leading `\n\n` on the text is the residue
where the stripped reasoning used to be.

Two things follow. **Silent cost:** every Claude Code request carries `output_config`, so every local
call pays for hidden reasoning it never displays. **A misleading row:** the middle line of that table
is a `max_tokens` stop with `output_tokens: 127` and nothing to show for it — the same signature as
the 40 prompt-cache warmup rows in `phase-2-step-6-session/calls.csv`, which were read as "returned
zero content tokens". Some of those may be this instead. The two are indistinguishable in the CSV.

### 3. `cache_control` is accepted but does nothing at probe scale

Two identical runs of a request with an `ephemeral`/`1h` marked system block, 117 input tokens:
`cache_read_input_tokens` was **0** both times. The marker is accepted and has no effect this small.

This is not a contradiction of the frozen session, which showed 24 rows with non-zero `cache_read`
and a maximum of 40879 — LM Studio's prefix cache is real and works on real traffic. It simply has a
floor that a probe-sized request sits under. Worth knowing before anyone tries to measure caching
with a small request and concludes it is broken.

## What the replay showed

The real captured Claude Code request — `log-the-whole-request.txt`, with only the model name
changed — **worked against a local model, unmodified**:

```
status         200
request        119797 bytes, max_tokens 64000
blocks         thinking, text
stop_reason    end_turn
usage          {"input_tokens": 27924, "output_tokens": 36}
text           '\n\nHi! How can I help you today?'
```

That is every unusual element at once — a `role: "system"` message inside `messages`, 27 tool
schemas, two `cache_control` markers, `context_management`, `output_config`, `metadata.user_id`,
`thinking`, and the ten-entry `anthropic-beta` header — accepted together, with a correct answer to
the `hi` the conversation actually contained. There was nothing to bisect.

**The preamble is now measured, not estimated.** `CLAUDE.md` puts it at "~30k tokens of fixed
preamble" inferred from 118 KB of JSON. It is **27924 tokens**, which makes the estimate good and
slightly pessimistic. Against the 44544-token window that model was loaded with, **63% of the context
is gone before the user types anything.**

**And it took 196789 ms to the first byte** — three minutes and seventeen seconds of prefill for a
one-word turn. `duration_ms` was 198000, so essentially all of it was prefill: the answer itself took
1.2 seconds. This is the `ttfb_ms` column earning its place more starkly than anything in Phase 2,
where the median local time to first byte was 37 s.

### Run it twice, and the project's central design decision becomes a measurement

The same replay, sent a second time:

| | first run | second run |
|---|---|---|
| `input_tokens` | 27924 | 27924 |
| `cache_read_input_tokens` | 0 | **27904** |
| time to first byte | 196789 ms | **49629 ms** |

**99.93% of the prefix was served from cache, and time to first byte fell four-fold** — 3m17s to
50s, on a real Claude Code request through the router.

This is the argument for byte-relay stopping being an argument. `CLAUDE.md` calls prompt caching "the
strongest practical reason to relay the body untouched rather than parse and rebuild it", reasoning
that any reserialization — "even key reordering that means the same thing" — silently breaks the
match. A cache hit of 27904 tokens is that claim measured end to end: the bytes the router forwarded
on the second call matched the first closely enough for LM Studio's prefix cache, which is only true
because the router changed none of them.

It also puts a number on what the decision is worth locally: **147 seconds of prefill per turn**, on
a one-word conversation. It would be larger on a real one.

Worth noting even so: a 99.93% hit still cost 50 seconds. Cache reads are much cheaper than prefill
here, not free.

### One caveat about the instrument

`probe.py` parses the captured body and re-serializes it, so the bytes on the wire are not identical
to the ones captured — 119797 against the original 118004, the difference being JSON separator
spacing. The replay therefore proves **the shape is accepted**, which is what this phase asked, and
the cache comparison above is still sound because both runs were serialized the same way by the same
code. What it does not do is prove that Claude Code's own bytes survive, which is a different claim —
and one the 24 cache-hit rows in `phase-2-step-6-session/calls.csv` already carry, from real traffic.

## The truncation boundary: it fails loudly, and that is the good news

This was the phase's one item with a consequence rather than a curiosity — the mechanism behind
`epd/EPD-002-token-counting-for-local-backends.md`, which worries that a conversation outgrowing a
small local window would be **silently trimmed**, degrading answers without ever failing.

**It is not trimmed. LM Studio refuses.** A request whose input exceeds the loaded window comes back:

```
{"type": "error", "error": {"type": "api_error", "message":
 "The number of tokens to keep from the initial prompt is greater than the context length.
  Try to load the model with a larger context length, or provide a shorter input"}}
```

Recorded by the router as `error_status: stream_error`, `error_code: api_error`, and — worth
noting — **rejected in 908 ms**, without paying for the prefill it could not fit.

The method: a codeword at the very front of a long conversation, filler in the middle, and a question
at the end asking for the codeword back. A model that had been quietly trimmed would answer without
it. The control run, comfortably inside the window at 9166 input tokens, returned
`ZARDOZ-QUILL-7734` exactly — so the needle works and a failure to produce it would have meant
something.

### But the message arrives in the one form Claude Code is known not to read

The refusal is an **SSE `error` event inside an HTTP 200** — the same shape, in the same position,
that Phase 3 measured Claude Code ignoring. There, the client printed its own generic
`API returned an empty or malformed response (HTTP 200)` instead of the router's wording.

So LM Studio's single most actionable error message — one that names the cause *and* the two fixes —
is very likely invisible to the harness it is talking to. That elevates Phase 3's "feature with no
measured consumer" from a curiosity about our injected event to a gap with a real message behind it.

**Not measured, and the difference could matter.** Phase 3's case was an error event arriving *after*
partial content; this one is the *only* event in the stream, with no `message_start` before it.
Whether Claude Code treats those two identically is unknown. If it does not, this message may reach
the user after all. That is the one question this phase leaves open, and it needs a real session at a
context small enough to trip — which the CLI cannot arrange, see below.

### The check below the boundary did not answer its question — it found a defect instead

The over-window case says LM Studio refuses. The obvious companion test is a request *just under* the
window, to rule out a zone where it quietly trims rather than refusing. That run was a needle of
about 41000 tokens against the 44544-token window, and it came back:

```
error          {"type": "api_error", "message":
                "The lmstudio backend's reply broke off mid-stream: ReadTimeout"}
csv row        error_status=transport_error, error_code=read_timeout
ttfb           600247 ms
```

**600247 ms is the router's own read timeout.** `proxy.py` sets `httpx.Timeout(connect=5.0,
read=600.0, …)`, chosen in Phase 3 so that "a model may think for ten minutes but a dead port fails
fast". LM Studio was not failing: `lms ps` showed `PROCESSINGPROMPT` throughout. The router hung up
on a healthy request that simply had not finished prefilling.

So the question that run was meant to answer — is there silent trimming below the limit — **remains
open**. What it found instead is more useful:

**The usable context of a local model is bounded by time, not by the window.** Three measurements
from this session, all on the same model and machine:

| input tokens | time to first byte |
|---|---|
| 9166 | 115073 ms |
| 27924 | 196789 ms (49629 ms on a cache hit) |
| ~41000 | **never — killed at 600000 ms** |

A model loaded at 44544 cannot be driven to the top of its own window through this router, because
the ten-minute ceiling arrives first. Two points do not establish a curve and this does not claim
one — the middle row is faster per token than the first, which warmup alone may explain — but the
endpoint is not in doubt.

**Not fixed here, deliberately.** Raising `read` is a one-line change and a design decision that is
not Phase 4's to take: the same number is what makes a wedged backend fail in bounded time, and
Phase 3 picked it on purpose. What this phase contributes is that the number is *reachable by
ordinary traffic*, which is not what it was chosen against. It belongs in the next phase alongside the
credential work, with the options being a larger read timeout, a configurable one, or one that resets
on progress rather than on first byte.

> **Corrected by Phase 5 on 2026-08-07.** Two claims in the paragraph above are wrong, both measured
> in `phase-5-measurements/read_timeout_semantics.py`.
>
> **The third option does not exist.** `read` already resets on progress — a backend dripping a
> chunk every second ran for three times the timeout and completed, because every chunk restarts the
> clock. What `read` measures is the longest permitted *silence between two reads*, which is why a
> silent prefill hits it and a slow stream does not.
>
> **And "fails in bounded time" was never true of duration.** Since the clock restarts per chunk, a
> backend dribbling one byte every 599 s would have run forever under the old setting too. The
> property Phase 3 actually bought was "fails if it goes quiet", which is narrower — so raising the
> number gave up less than this paragraph implies.
>
> Phase 5 made `read_timeout` per backend: 600 s for Anthropic, 1800 s for LM Studio.

It is also the third instance of this project's most reliable lesson, after Phase 2 step 6 and Phase
3's `ReadError("")`: **the tests confirm the code does what it was written to do; only real traffic
shows what it was written to do being wrong.** Every one of the 147 tests passes with this timeout.

### An instrument note: the context length could not be changed from the CLI

The plan called for reloading at 8192 so the boundary would be cheap to reach. **`lms load -c 8192`
and `--context-length 8192` are both silently ignored** — the model reloads at 44544 regardless,
because LM Studio's saved per-model configuration wins over the flag. `lms ps` and the REST API agree
on 44544 afterwards; only the GUI can change it.

So the boundary was measured at the real 44544 window instead, with a proportionally larger needle.
That is arguably the better test — it is the size actually in use — and it cost one 165 KB request
rather than a reload. But the plan's assumption that the window is scriptable was wrong, and anything
later that wants a specific context length needs a person in the GUI.

## A third of this phase was already done, again

Phase 3's central finding was that four of its five work items had been built by Phase 2 as a
by-product. Phase 4 repeats it in a different form: **a third of its plan was already measured**, by
the same Phase 2 step 6 session, and reading `phase-2-step-6-session/calls.csv` before running
anything removed a whole step and one probe.

Those 99 rows against this same model already showed real Claude Code requests succeeding (95 `ok`,
zero rejections), tool results round-tripping (eight `tool_use` turns with `request_bytes` growing
154 → 164 KB as each result accumulated), a 170 KB request — larger than the replay this phase
planned for realism — and prefix caching working at scale. The planned "run a real Claude Code
session" step would have re-answered all of it.

**The pattern is now three phases old and worth naming rather than rediscovering.** Artefacts
committed for one phase keep answering the next one, because a real session exercises far more than
the question it was run for. The cheap habit: before planning a run, grep the frozen CSVs for the
same model and the same question.

**Its limit is equally worth knowing.** The router logs metadata and never bodies, so those rows
prove *a real request succeeded* and can never prove *a request containing `context_management`
succeeded* — nothing recorded what was in them. That is exactly the gap `epd/EPD-003-capturing-bodies-for-a-corpus.md`
proposes to close, and it is why the replay of a *known* body survived the cut.

## What is still open

Stated plainly, because an honest list is this phase's deliverable and a short one would be dishonest.

- **Whether trimming happens below the boundary.** The run meant to check it hit the router's read
  timeout. The boundary itself refuses cleanly; the region just under it is uncharacterised.
- **Whether Claude Code shows LM Studio's context error.** It arrives as an SSE `error` event inside
  an HTTP 200 — the shape Phase 3 measured being ignored — but as the *sole* event, with no
  `message_start` before it, where Phase 3's case followed partial content. Whether the client treats
  those alike is unknown, and it decides whether the most useful message LM Studio produces is seen
  at all.
- **Non-streaming replies.** Every probe here ran streamed. `probe.py --no-stream` exists and was not
  used; the recorder takes a different path for buffered replies and LM Studio reports `usage`
  differently.
- **Other local models.** Everything here is `qwen/qwen3.5-9b`. `capabilities` in
  `GET /api/v1/models` varies per model — several have no `vision`, several no `reasoning` — so none
  of the honoured/ignored column transfers without re-running the probes.

## Corrections this phase owes to `CLAUDE.md`

- The claim that a `role: "system"` message inside `messages` is "almost certainly unsupported by
  LM Studio" is **wrong**, and was wrong when written. It is supported and obeyed.
- "Still unmeasured: a `role: "system"` message inside `messages`, `thinking` blocks, images" — all
  three are now measured, and all three work.
- "~30k tokens of fixed preamble" is now **27924**, measured by replaying the request the estimate
  was derived from.
- The standing worry that "context is being silently trimmed somewhere" is answered: **it is not**,
  at the boundary. The 34304-token `gemma-4-e4b` session of 2026-07-29 worked because it fit.

And one this phase owes to its own plan: `phase-4-plan.md` asserted that `EPD-002` was written
without knowing the loaded context length is machine-readable. **That was wrong** — the document
already cites `GET /api/v1/models`. The real defect is narrower: it reads `max_context_length` where
it needs `loaded_instances[].config.context_length`, which on this machine differ by 262144 against
44544. The plan file has been corrected in place and `EPD-002` carries an addendum.
