# Phase 6 — what the review found

Act 1, 2026-08-07. Nothing has been changed. The plan is `phase-6-plan.md`; this is the findings
half, and the "what was done" half will be appended after the gate.

**The short version.** The code is in better shape than the review expected, and the documents are
in better shape than the review expected — but for a reason worth stating precisely: *almost every
number quoted in them is exactly right*. Fifteen of the sixteen quoted measurements reproduce from
the committed artefacts to the digit. The problems that exist are three small defects, one claim
whose recipe is missing, and a shape question about comment density that the measurement argues
**against** acting on.

The single most useful outcome is negative: **the hypothesis this review was built on turned out to
be wrong.** The plan predicted that the source comments re-argue `CLAUDE.md` at length and could be
cut. Measured, they share a mean of **2.8%** of their wording with it. See B1.

---

## What holds

Verified rather than re-asserted. Each of these was recomputed or re-run, not read.

### The Phase 2 frozen session (`docs/phase-2-step-6-session/calls.csv`)

Every structural claim in `CLAUDE.md` reproduces exactly:

| Claim | Recomputed |
|---|---|
| 142 rows across eleven sessions | 142 rows, 11 distinct `session_id` |
| 7 rows under one agent ID | 7 rows with `agent_id`, 1 distinct value |
| 6 `client_disconnect` rows, both backends | 6 — 5 lmstudio, 1 anthropic |
| 32 streamed Anthropic rows fully populated | 33 streamed anthropic rows, 32 with both token counts |
| `/v1/messages/count_tokens`, 33 rows | 33 |
| 40 warmup probes, 20.0 of 45.5 minutes, 44% | 40 probes (all lmstudio), 20.0 of 45.6 min, **44%** |

### Phase 4 and Phase 5 numbers

Every quoted figure is present in a committed evidence file: `27924`, `27904`, `196789`, `49629`,
`600247`, `461712`, `30343`, `41595`, `44544`. One exception, D2 below.

### The code, driven live

The router was started for real against local stubs — a healthy backend, `dying_backend.py`, and a
header-echo backend — and taken through nine request shapes. All behaved as documented:

- `HEAD /` answered 200; uvicorn's own lines land in the router's log in the router's UTC format,
  character-identical to the CSV's `timestamp` — the Phase 2 claim about merging the two files.
- A healthy streamed reply: `input_tokens` from `message_start`, `output_tokens` and `stop_reason`
  from the final `message_delta`, `cache_read_input_tokens` carried through.
- A stream broken mid-answer: the caller receives everything that did arrive, then the injected
  Anthropic-shaped `error` event naming the backend. The row reads `transport_error` /
  `read_error` — **and still carries the usage captured before the break**.
- A buffered (non-SSE) reply broken mid-answer: no event injected, as designed.
- No `model` in the body, and a body that is not JSON: both 400, both recorded with `backend` empty.
- The catch-all forwarding `/v1/messages/count_tokens` to Anthropic, recorded with its real `path`.
- Backend unreachable: HTTP 502, `transport_error` / `connect_error`.
- `GET /health` answered locally and **not** recorded as a call.

The `stream` column's designed semantics held live: `true` where sent, `false` where omitted, and
**empty only for the body that did not parse** — the exact three-way distinction Phase 2 rebuilt it
for.

### Credential handling — the Phase 5 claim, re-exercised

Both modes checked against a backend that prints what it received:

| | `credential: forward` | `credential: inject` |
|---|---|---|
| caller's `authorization` | passed untouched | **removed** |
| caller's `x-api-key` | passed untouched | **removed** |
| key from the environment | not sent | `Authorization: Bearer …` |
| ten-entry `anthropic-beta` | intact, all ten | intact, all ten |
| `accept-encoding` | overridden to `identity` | overridden to `identity` |
| path and query | `?beta=true` forwarded | `?beta=true` forwarded |

`inject` with the environment variable unset is refused at startup with the message the design
called for. An older config carrying **no** `read_timeout` still loads and defaults to 600 s
(`docs/phase-3-verification/router.yaml`, checked directly) — the backward-compatibility claim.

### Everything else checked

- **157 tests**, exactly as `CLAUDE.md` says. The rough `def test` count of 127 was the stale
  number; parametrisation accounts for the difference.
- All four cited commit hashes resolve: `4d7d7f6`, `c8401e9`, `d1def4f`, `f9f6d83`.
- `ruff check` clean; the tree is already formatted at the pinned 0.16.1; `--check` validates.
- **No dead module-level names** anywhere in `src/` — an AST inventory of every name defined against
  every name referenced in `src/` and `tests/` found nothing unreferenced. `backend_name_for_model`,
  the review's leading suspect, is used by `backend_for_model` one line below it.
- `docs/log-the-whole-request.txt` is **still redacted** — no `sk-ant-` tokens, no UUID-shaped
  identifiers, 5 `REDACTED` markers — and is still referenced by eight documents. It earns its 119 KB.
- `.env.example` is accurate and current, including the `inject` instructions.

---

## Findings

Ranked by consequence. Three are real defects; the rest are judgement calls.

### C1 — the SSE scanner gives up on a large chunk of *short* lines, and its comment says it cannot

`src/ilirium_llm_router/observe.py:142-147`

```python
def _feed(self, chunk: bytes) -> None:
    self._pending += chunk
    # Only ever holds the tail after the last newline, so passing the cap means one line did.
    if len(self._pending) > MAX_SCAN_BYTES:
        self._give_up("a single SSE line grew past the scan limit")
```

The comment's invariant is true — but only *after* the split at the end of the method. At the moment
of the check, `_pending` holds the previous tail **plus the entire new chunk**, which may contain
thousands of complete lines. So the cap fires on total chunk size, not on line length, and the
message written to the log is wrong about why.

**Measured, not argued.** A 1,049,671-byte chunk whose longest single line is **101 bytes**:

```
gave_up      = True
input_tokens = None
output_tokens= None
stop_reason  = None
```

All five usage columns lost, and the row's own diagnostic (`stream: true`, non-zero
`response_bytes`) would point the next reader at the SSE scanner with a reason that is not the real
one.

**Honest reachability: low.** `httpx.aiter_raw()` yields what the transport produces, typically
≤64 KiB, so a >1 MiB single chunk is unlikely from either real backend. This is a latent defect and
a definitely-wrong comment, not a bug anyone has hit. It is ranked first because it is the exact
species Phase 5 named — *a note about the code that had drifted from the code* — found this time in
a comment rather than in a document.

**Fix:** move the cap check below the split so it measures the retained tail, which is what the
comment already claims it measures. Four lines, one test.

### C2 — `app.state.config` is written and never read

`src/ilirium_llm_router/app.py:56`. Set on every app; referenced nowhere in `src/` or `tests/`. The
one genuinely dead line in the codebase. **Fix:** delete it.

### C3 — `pydantic` and `starlette` are direct imports but undeclared dependencies

`pyproject.toml` declares five packages. `src/` imports **`pydantic`** (`config.py`) and
**`starlette`** (`proxy.py`, `app.py`, `observe.py`) directly, and neither is listed — both arrive
transitively through FastAPI, so the router's constraint on them is whatever FastAPI's happens to
be. A FastAPI release that widens or changes either is a silent break with nothing in this repo to
say what the router needs.

**Fix:** add both to `[project].dependencies` with the versions currently resolved in `uv.lock`.
This is the same discipline as pinning ruff, applied to a library instead of a tool.

### C4 — `_read_error` looks up each key twice and casts a value it has already narrowed

`src/ilirium_llm_router/observe.py:281-284`

```python
if isinstance(error.get("type"), str):
    observation.error_type = str(error["type"])
```

Two dictionary lookups and a `str()` on a value `isinstance` has just proved is a `str`. Harmless,
but it is the one place in the file that reads as generated rather than written, and it is half of
what `ty` complains about. **Fix:** narrow once into a local.

### T1 — 12 `ty` diagnostics, none of them bugs

Run with `uvx ty@0.0.14 check src tests`. All twelve are stub-precision artefacts, not defects:

- **7 in `observe.py`** — `dict[str, object]` narrowed by `isinstance`, which `ty` widens to
  `dict[Unknown, Unknown]`. C4 is a subset.
- **3 in `proxy.py:101-104`** — `httpx.Timeout`'s attributes are typed `object` in httpx's own
  stubs, so reading `TIMEOUT.connect` back to build a new `Timeout` cannot type-check.
- **2 in `tests/test_recording.py:380,436`** — `aclose()` on an `AsyncIterator`, which exists at
  runtime on an async generator but is not on the protocol.

**Recommendation: do not adopt `ty` and do not chase these.** Zero of twelve found a real problem,
and the project's stated non-negotiable is simple, human-readable code. The finding worth keeping is
the negative one: a type checker was pointed at this codebase and found nothing wrong with it.

---

## Documentation

### D1 — the 26× time-to-first-byte claim is right, and its recipe is missing

`CLAUDE.md:37` (and the same sentence in `handoff.md` and `implementation-plan.md`):

> median time to first byte was 1426 ms against Anthropic and 37136 ms against LM Studio, a 26× gap

Both numbers are **exactly reproducible** — but only under one slice, which no document names:

| Slice | anthropic | lmstudio | gap |
|---|---|---|---|
| all rows | 1252 | 4904 | 3.9× |
| `/v1/messages` only | 1254 | 16902 | 13.5× |
| `/v1/messages`, no warmup probes | 1254 | 33364 | 26.6× |
| **streamed + ok + `/v1/messages`** | **1426** | **37136** | **26.1×** |

So the claim is true and the arithmetic is sound. But the obvious recomputation — every row in the
file — gives **3.9×**, and a reader who tried it would conclude the documentation was wrong by a
factor of seven. This is the same defect as Phase 5's, one step earlier: not a claim that was never
measured, but a claim whose *measurement* is unreproducible from what is written down.

**Fix:** one clause — "across successful streamed `/v1/messages` calls" — in each of the three
places. Cheapest high-value change in the review.

### D2 — one figure is traceable to a note, not to an artefact

`CLAUDE.md:147` cites "9166 tokens → 115 s". Unlike every other Phase 4/5 number, `9166` appears in
no frozen evidence file — only in `phase-4-notes.md:223` and `phase-4-probes/make_needle.py:33`.
It is documented and consistent; it is just not independently checkable the way its neighbours are.
Grade: **holds, one level weaker than the numbers beside it.** No action needed beyond knowing it.

### D3 — `README.md` never says how to run the thing

Untouched since 2026-07-28, and still the original brief: goals, future plans, a stack list. It is
the repository's front door on GitHub and contains no install step, no run step, and no mention that
the router works. Nothing in it is false — it is 100% aspiration and 0% instruction.

**Recommendation:** add a short Quick start (`uv sync`, `make check`, `make run`, the three
`ANTHROPIC_BASE_URL` lines) and a sentence saying what works today. This does not require touching
the existing prose.

### D4 — the EPD index table in `CLAUDE.md` is accurate

Checked mechanically, without reading the proposals: no EPD is described as accepted, and each row's
"waiting on" wording is consistent with the index in `outstanding-work.md`. **No finding.**

---

## Duplication and bloat

### B1 — 58% of the source is prose, and the measurement argues against cutting it

| file | lines | code | comment | docstring | prose |
|---|---:|---:|---:|---:|---:|
| `observe.py` | 428 | 74 | 36 | 232 | 63% |
| `proxy.py` | 430 | 112 | 42 | 212 | 59% |
| `stats.py` | 231 | 25 | 5 | 156 | 70% |
| `config.py` | 218 | 57 | 0 | 108 | 50% |
| `app.py` | 104 | 16 | 0 | 66 | 63% |
| `logging_setup.py` | 116 | 3 | 17 | 70 | 75% |
| `routing.py` | 31 | ~2 | 0 | 24 | 77% |
| **total** | **1713** | **371** | **110** | **890** | **58%** |

371 lines of code carry 1,000 lines of prose. `stats.py` spends 156 docstring lines on 25 lines of
code; `routing.py` is 31 lines for a two-line rule. On the raw ratio this is the most extreme
comment density I would expect to see in a Python project, and it is the obvious thing to cut.

**The plan predicted these docstrings re-argue `CLAUDE.md` and could go. That prediction is wrong,
and it was tested rather than assumed.** Comparing every docstring of 25+ words against `CLAUDE.md`
by shared 5-word sequences:

- **mean overlap: 2.8%** across 49 docstrings
- highest single overlap: **19.7%** (`routing.py`'s module docstring)
- docstrings above 30% overlap at an 8-word window: **zero**

The prose is not duplicated. It restates the same *decisions* in different words, and most of it
carries specifics — dates, measured values, the failure that motivated the line — recorded nowhere
else. `describe_exception`'s docstring is the clearest example: it records that httpx raises
`ReadError("")`, that the naive f-string wrote a dangling colon into the CSV, and that every unit
test missed it because they all supplied a message. Deleting that deletes a finding.

**Recommendation: do not mass-delete, and do not set a ratio target.** The honest summary is that
this codebase is *documentation with code in it*, deliberately, and the measurement does not support
the reflex. Two bounded things are worth doing instead:

1. Fix the comment that is **wrong** (C1). One wrong comment costs more than a hundred verbose ones.
2. Accept that the density is a deliberate style, and record that it was measured and kept — so the
   next reviewer does not re-open it from the ratio alone.

If a target is wanted anyway, the defensible one is `logging_setup.py` (3 lines of code, 87 of
prose) and `routing.py` (77%), where the prose most exceeds what the code can surprise anyone with.

### B2 — one helper is defined four times, identically, and `conftest.py` already exists

`dies_after` — the async generator that yields one chunk and then raises `httpx.ReadError` — is
defined **four times with byte-identical bodies**:

- `tests/test_proxy.py:304` and `:336`
- `tests/test_recording.py:266` and `:467`

Found by comparing normalised ASTs, so this is exact duplication, not similarity. `tests/conftest.py`
already holds the shared `Upstream`, `make_config` and `running` helpers, which is where it belongs.
**Fix:** one definition in `conftest.py`, four call sites. The only real duplication in the repo.

*(A second pair — `test_recording.py:484`'s `write` and `test_stats.py:181`'s `explode` — is also
byte-identical, but they are two-line "raise on write" stubs with different names for different
reasons. Not worth merging.)*

### B3 — nothing else

No dead code, no unreachable branches, no unused imports, no speculative abstraction, no config knob
that nothing reads. Every scanner subclass has a real second implementation; every parameter varies
across call sites. The AST inventory and `ruff` agree.

---

## Hygiene

### H1 — `.gitignore` is 237 lines for a ten-file Python project

102 active rules and 92 comment lines — the standard GitHub Python template, carried whole. It
covers everything present (`.DS_Store`, `.idea/`, `.venv`, `logs/`, the caches; nothing untracked
is leaking). Harmless, and about 90 rules larger than this project can use.

**Recommendation: leave it.** It is doing its job, the cost is zero, and trimming a working
`.gitignore` is how something starts getting committed by accident later. Recorded so the next
reviewer does not re-open it either.

### H2 — one document is self-terminating by its own instruction

`docs/handoff.md` (28 KB) says in its first paragraph that it should be deleted once the project
speaks for itself. It does not yet — it still carries session state nothing else holds. Not a
finding, and **not recommended for deletion this phase**; noted because the review was asked whether
anything should be removed, and this is the only file that has ever nominated itself.

`docs/testing-against-claude-code--results.md` (3 KB) was the other deletion candidate. It holds the
Phase 1 verification results and is referenced by `testing-against-claude-code.md`. **Keep** — it is
small and it is the only record of that run.

**Nothing in `docs/` is recommended for deletion.**

---

## Recommended, ranked

| | Finding | Cost | Why |
|---|---|---|---|
| 1 | **D1** — add the slice to the 26× claim, 3 places | 3 lines | A reader recomputing gets 3.9× and concludes the docs lie |
| 2 | **C1** — move the SSE cap check below the split | 4 lines + test | The comment is definitively wrong; the behaviour is a latent defect |
| 3 | **C3** — declare `pydantic` and `starlette` | 2 lines | Undeclared direct dependency is a silent future break |
| 4 | **B2** — `dies_after` into `conftest.py` | −18 lines | The only exact duplication in the repo |
| 5 | **C2** — delete `app.state.config` | −1 line | The only dead line in the repo |
| 6 | **D3** — a Quick start in `README.md` | ~15 lines | The front door does not say how to open it |
| 7 | **C4** — narrow once in `_read_error` | 3 lines | Cosmetic; bundle with C1 or skip |

**Explicitly not recommended:** adopting `ty` (T1), cutting comment density (B1), trimming
`.gitignore` (H1), deleting any document (H2).

Items 1–7 total roughly forty lines. That is the honest size of what five phases of accumulation
left behind, and it is a smaller number than this review expected to write.

---

## What this review could not settle

It read code and committed artefacts and drove local stubs. It did not touch LM Studio or Anthropic.
So the claims resting on live third-party behaviour — Claude Code retrying a 502 ten times, Claude
Code ignoring a mid-stream `error` event, LM Studio's honoured/ignored feature table — are graded
**consistent with their committed transcripts** and not independently re-measured. None of them
showed any sign of being wrong; none of them was re-run.

One methodological note for whoever runs Phase 7. The most valuable thing in this review is B1, and
it is valuable because it **refuted the plan that produced it**. The plan asserted the comments were
redundant; five minutes of shingle comparison said they were not. That is the Phase 5 lesson
turned on the reviewer instead of the reviewed — check the claim you are planning against, including
when it is your own.
