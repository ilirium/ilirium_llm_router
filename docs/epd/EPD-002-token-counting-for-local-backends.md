# EPD-002 — Token counting for local backends

**Status: proposal. Written 2026-07-31. No decision is taken here.** Like EPD-001, this waits for
Phase 4. Nothing in it is implemented and nothing in it is blocking: the router forwards
`count_tokens` correctly today, and every session in `logs/calls.csv` completed.

What is *not* deferred is the finding, which is measured and reproducible: **Claude Code's context
accounting for local models is an estimate against an assumed 200k window.** On a large-context
model that is harmlessly conservative. On a small-context model it is the silent-truncation failure
`CLAUDE.md` has been worried about since Phase 1, with a mechanism attached at last.

## How this surfaced

Phase 2 step 6 — the real Claude Code session of 2026-07-31, recorded in `logs/calls.csv`. The `path`
column did exactly the job it was specified for: it turned the standing "other endpoints" worry into
a fact. 33 of 142 rows are not `/v1/messages` at all:

| Backend | `count_tokens` rows | Response |
|---|---|---|
| lmstudio | 32 | 85 bytes, HTTP 200, **no token count** |
| anthropic | 1 | 22 bytes, HTTP 200, a real count |

Without that column those rows would have been indistinguishable from ordinary traffic and the gap
would still be invisible.

## What LM Studio actually does

`POST /v1/messages/count_tokens` is **not implemented**. It answers with a body that names the
endpoint it does not have:

```
$ curl -s -o /dev/null -w '%{http_code}\n' -X POST \
    http://localhost:1234/v1/messages/count_tokens \
    -H 'content-type: application/json' \
    -d '{"model":"qwen/qwen3.5-9b","messages":[{"role":"user","content":"hi"}]}'
200

$ # …and the body:
{"error":"Unexpected endpoint or method. (POST /v1/messages/count_tokens)"}
```

**The status is 200, not 404.** That is why all 32 rows are logged `error_status: ok`. The router is
being honest — it cannot call a 200 a failure without parsing bodies it exists to relay — but it
means the failure is invisible in the CSV except by reading `response_bytes`.

There is no tokenizer endpoint to fall back on either. Both candidates return the same
200-with-an-error-body:

```
POST /v1/tokenize        →  {"error":"Unexpected endpoint or method. (POST /v1/tokenize)"}
POST /api/v0/tokenize    →  {"error":"Unexpected endpoint or method. (POST /api/v0/tokenize)"}
```

So the only way to obtain a true local token count is to send the prompt and read `usage` off the
reply — a full prefill. Measured cost of exactly that, from this session: **70–110 seconds for a
30–50 KB body.** Not viable as a synchronous answer to `count_tokens`.

A small confirmation that fell out of this, worth recording because it verifies a Phase 1 promise:
the curl above returns **75 bytes**, but the CSV rows are **85**. The difference is exactly the ten
characters of `?beta=true`, which LM Studio echoes back inside the error string. Path *and* query
reach the backend, byte for byte, as designed.

## What Claude Code does with the non-answer

It falls back to its own estimator, and it says so. `/context`, run against a short local session on
2026-07-31 (a different session from `calls.csv`):

```
⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁   qwen/qwen3.5-9b
⛁ ⛁ ⛀ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁   81.8k/200k tokens (41%)

                      Estimated usage by category
                      ⛁ System prompt:  2.7k tokens  (1.3%)
                      ⛁ System tools:  23.1k tokens (11.6%)
                      ⛁ MCP tools:      7.7k tokens  (3.9%)
                      ⛁ Skills:         2.2k tokens  (1.1%)
                      ⛁ Messages:      46.2k tokens (23.1%)
                      ⛶ Free space:   118.1k        (59.1%)
```

The word **Estimated** is the tell. The display is not blank and not zeroed; the earlier suspicion
that it would be is withdrawn. The categories are internally consistent (they sum to 81.9k, and
81.9 + 118.1 = 200.0), so this is a coherent local calculation, not garbage.

Corroborating evidence that these numbers come from `count_tokens` and not from something else: the
32 local calls arrive in **two bursts of 14 within a single millisecond**, with near-identical size
profiles —

```
08:46  n=14  sizes=[174, 357, 363, 441, 508, 715, 910, 1211, 1246, 1719, 2276, 4214, 30839, 31545]
09:35  n=14  sizes=[174, 357, 363, 441, 508, 715, 828, 1125, 1304, 1719, 2276, 4214, 30839, 35573]
```

— a component-by-component breakdown, exactly the shape `/context` draws. Note the 30839-byte member
(the tool schemas) and the ~31–35 KB member (system prompt and conversation). It happened **twice in
the whole session against 109 message turns**, which rules out per-turn background accounting: these
are two `/context` invocations. The lone larger calls at 08:48 and 09:36 (52671 and 48643 bytes) are
a different question — one whole-conversation measurement mid-session, which is the shape of an
auto-compaction threshold check.

## The two errors, and which one matters

### The numerator is in the wrong tokenizer

The estimate tokenizes with Claude's tokenizer; the truth is qwen's. From `calls.csv`, qwen3.5-9b
runs about **4.08 bytes per token** on real payloads (see the table below). Claude's tokenizer is
denser on this kind of JSON, so the estimate reads high — perhaps 10–15%, which is **not measured**
and is inference from the ratio alone.

Direction: conservative. It thinks the context is fuller than it is.

### The denominator is a guess

`81.8k/200k`. The model is loaded at **262144**. 200k is Claude's window, and Claude Code has no way
to learn the real one: LM Studio publishes `max_context_length` at its native `GET /api/v1/models`,
but the Anthropic-compat namespace exposes **only `/v1/messages`** — nothing in the request path ever
carries the local model's context length.

Here that is also conservative (200k < 256k), so the true usage is **31%, displayed as 41%**.

### Why both being safe here is an accident

Both margins exist only because this model happens to be loaded above 200k. Load a model **below**
200k and they invert together, with nothing left to catch the error.

This is not hypothetical for this machine. Phase 1 ran `google/gemma-4-e4b` at **34304** tokens of
context. A conversation of the size shown above — 81.8k — is **238% of that model's window**, and
`/context` would report 41%. No warning, no early compaction, and the model silently truncates.

That is the concrete mechanism behind the Phase 4 worry recorded in `CLAUDE.md`: *"either the ~30k
figure is pessimistic for this tokenizer, or context is being silently trimmed somewhere."* It is the
second one, and the trimming is invisible because the meter is measuring against the wrong ruler.

It also revises the auto-compaction concern raised while analysing this session. Compaction **will**
fire — Claude Code has a number to work with. It will fire against the wrong ceiling, so on a
small-context model it fires far too late.

## Can the router emulate `count_tokens`?

Partly. The question was asked directly, so here is what the data says.

### Raw `request_bytes` → tokens does not work

Fitted over the 65 local rows in `calls.csv` that carry an `input_tokens` value:

```
bytes/token by payload size
     0-500    n=11  median= 24.08   range  8.57-24.08
   500-2000   n=20  median=  6.46   range  3.31- 8.36
  2000-10000  n=4   median=  4.97   range  4.91- 5.02
 10000-40000  n=6   median=  4.08   range  3.79- 4.19
40000-200000  n=24  median=  4.08   range  3.93- 4.22

least squares:  tokens = 0.2454 × bytes − 11
                median |error| = 18.4%      worst = 410%
```

A **6× spread** in the ratio, and the worst errors land on small bodies — which is precisely what
`/context` asks about (174, 357, 363, 441, 508 bytes…). The cause is plain once seen:
`request_bytes` counts the JSON envelope, and a 313-byte body is almost entirely envelope and
metadata that never reaches the tokenizer at all. **The ratio is not a tokenizer property. It is a
"what fraction of this JSON is content" property**, and it varies with body shape.

The stable 4.08 figure for large payloads is a coincidence of self-similarity — every big body
carries the same ~110 KB fixed preamble. It is not a law and must not be used as one.

### Content bytes would work much better — and parsing is permitted here

Extract only what actually gets tokenized (system blocks, message content, tool schemas) and estimate
on *that*. The envelope overhead disappears and the ratio should tighten sharply.

The byte-fidelity rule does **not** forbid this. That rule protects bodies the router *relays*,
because reserialization breaks the prompt-cache prefix and costs real money. A `count_tokens` request
the router answers itself is never forwarded — there is no cache prefix to preserve and no fidelity
to lose. This is a real distinction, not a loophole, and it applies to this one endpoint only.

**Unmeasured.** `calls.csv` deliberately stores nothing body-shaped, so the content-byte ratio has
never been computed here. Proving it needs fresh measurement (see the next-step note below).

### The router holds a calibration signal nothing else has

Every real `/v1/messages` call already yields a `(body, true input_tokens)` pair — LM Studio's own
tokenizer, ground truth, arriving free on the tee Phase 2 already built. So the router need not
*guess* a ratio; it can **learn one per model and keep it current**. That is a strictly better
position than Claude Code's bundled estimator, which can never see the local tokenizer at all.

### Why "correctly" stays out of reach

LM Studio applies the model's **chat template** before tokenizing. Those wrapper tokens are in the
count and invisible from outside. They are roughly constant per model per turn, so they absorb into
an intercept — but the ceiling is "usefully close", never exact.

The exact path exists and is not recommended: load the model's real tokenizer via HuggingFace
`tokenizers`. It requires resolving an arbitrary LM Studio model ID to a tokenizer, a download, and
*still* replicating LM Studio's chat template to match. That is a heavy dependency for a project
whose stated non-negotiable is simple, human-readable code.

## The fork, stated and not decided

**Emulating `count_tokens` does not by itself fix the dangerous failure.** A perfect numerator over a
200k denominator still shows 41% for a 34k model that has already overflowed. So there are two
different goals here and they want different answers:

| | Returns | `/context` percentage | Auto-compaction | Cost |
|---|---|---|---|---|
| **Honest** | best estimate of true tokens | still wrong on small models | still fires too late | none beyond the estimator |
| **Scaled** | `true_tokens × 200000 / real_context_length` | **correct** | **correct** | the absolute number becomes a deliberate lie |

The scaled option needs `real_context_length`, which is available: LM Studio's native
`GET /api/v1/models` reports `max_context_length` per model, and reading that list is already the
mechanism EPD-001 identifies for advertising a merged model list. Verified present on this machine —
`qwen/qwen3.5-9b` reports 262144.

Only the scaled option solves silent truncation. It also means the router starts telling the harness
something untrue on purpose, which is a different kind of project from *"dispatch, not translation"*
— and it carries an unquantified risk: if Claude Code uses absolute token counts anywhere else (to
cap `max_tokens`, say), the lie breaks something not visible from here.

**This is a decision for the repository owner, and it belongs in `CLAUDE.md` under "Design
decisions" once taken, not in code before then.**

## Documented versus measured

Everything in the right-hand column is stated at the confidence it was actually established.

| Claim | Status |
|---|---|
| LM Studio does not implement `/v1/messages/count_tokens` | **Measured** — reproduced by curl, 2026-07-31 |
| It answers HTTP **200** with an error body, so the router logs `ok` | **Measured** — 32 rows in `calls.csv`, confirmed by curl |
| LM Studio exposes no tokenizer endpoint either | **Measured** — `/v1/tokenize` and `/api/v0/tokenize` both refuse |
| The router forwards path *and* query byte-for-byte | **Measured** — the 10-byte `?beta=true` echo |
| Claude Code falls back to a local estimator rather than failing | **Measured** — the `/context` paste, labelled "Estimated" |
| The two 14-request bursts are `/context` invocations | **Inferred**, strongly — size profile, and 2 bursts against 109 turns |
| The lone 48–52 KB calls are auto-compaction threshold checks | **Inferred**, weakly — shape only |
| The displayed denominator is 200k while the model is loaded at 262144 | **Measured** — the paste, and `GET /api/v1/models` |
| Claude Code cannot learn the local context length | **Measured** in the negative — no `/v1/models` under the Anthropic-compat namespace |
| qwen3.5-9b runs ~4.08 bytes/token on large payloads | **Measured** — n=30, `calls.csv` |
| Claude's estimator reads 10–15% high for this model | **Inferred** from the ratio; never measured against a paired count |
| Raw `request_bytes` cannot predict tokens | **Measured** — 6× ratio spread, 410% worst-case fit error |
| Content bytes predict much better | **Unmeasured hypothesis.** The whole proposal rests on it |
| A sub-200k local model silently truncates while showing a low percentage | **Inferred** from the two measured errors; never observed end to end |

The last row is the one worth proving before anything is built, and the second-to-last is the one
worth proving before anything is designed.

## The cheapest next step, whenever this is picked up

Roughly fifteen minutes of measurement, no code:

1. Load a **small-context** local model (`google/gemma-4-e4b` at 34304 is the known case) and run a
   session until `/context` reports around 30%. If replies degrade or the model starts losing the
   early conversation while the meter still reads comfortable, the last row of the table above is
   measured and this stops being a proposal.
2. In parallel, capture one `count_tokens` request body and one matching `/v1/messages` body, and
   compare *content* bytes against the `input_tokens` the reply reports. One pair is enough to say
   whether the content-byte ratio is tight or whether this whole approach is dead.

Step 2 is the gate. If content bytes do not predict, nothing else here is worth building.

## Open questions

1. Honest number or scaled number — the fork above. Nothing else can be designed until this is
   settled.
2. If the router answers `count_tokens` for local backends, does it answer for *unknown* backends
   too, or forward and let them fail? A future local runner may implement the endpoint properly.
3. Does the estimator live in the router at all, or is the right answer to advertise
   `max_context_length` through a merged `/v1/models` and let Claude Code size its own window? That
   would fix the denominator without any lying, and it ties this document to EPD-001's question 3.
   **It is the option that should be ruled in or out first**, because it may make the fork moot.
4. Should `stats.py` gain a way to mark a 200-with-an-error-body? The 32 `ok` rows are technically
   correct and practically misleading. This would mean inspecting bodies the router relays, so it
   probably should not — but the alternative is that the CSV keeps recording a broken endpoint as
   healthy.
5. Does any of this change if LM Studio implements `count_tokens` in a later release? Worth
   re-checking before building, since the entire document is downstream of one missing endpoint.

## Evidence

All local, all 2026-07-31, all reproducible from this repository. **The session itself is frozen in
`docs/phase-2-step-6-session/`** — `logs/` is gitignored and rotates, so that directory rather than
`logs/` is the citable source for everything below.

- `docs/phase-2-step-6-session/calls.csv` — 142 rows, the Phase 2 step 6 session. Rows 24–37 and 112–125
  are the two `/context` bursts; row 69 is the one Anthropic `count_tokens`. Session and agent
  identifiers are replaced with stable placeholders (`session-01`, `agent-01`), which preserves the
  grouping the arguments here depend on; see that directory's `README.md`.
- `docs/phase-2-step-6-session/router.log` — the same calls with uvicorn's own lines interleaved,
  unredacted because it needed nothing. Note the log is naive **local** time and the CSV is **UTC**;
  the offset was +3 on the day.
- `docs/testing-against-claude-code--results.md` — the smoke test that preceded the session.
- LM Studio as installed on this machine (`lms` CLI commit `71bd99c`), serving `qwen/qwen3.5-9b` at
  262144 context. `CLAUDE.md` records 0.4.1+ as the release that added the Anthropic-compat surface.
- Claude Code `/context` output, pasted above, from a short local session not present in
  `calls.csv`.

Related: `EPD-001-model-selection-and-mixed-model-sessions.md` for the `/v1/models` and model
discovery questions this touches; `docs/lmstudio-usage-check.md` for the `usage` shape the router reads;
`CLAUDE.md` "Observability" for why the `path` column exists, which is the only reason any of this
was noticed.
