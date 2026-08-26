# Phase 11 — Group C: the converter

**Tasks 11–13.** Reassembly of both response encodings; delta reconstruction across a session's calls
and across day folders; `uuid`/`parentUuid` synthesis and the viewer's record shapes.

**In flight — task 11 is done, tasks 12 and 13 are not.** Tasks 14 and 15 are **struck in place** and
must not be resurrected or renumbered.

**The sharp end of the phase.** The store went to some trouble never to parse a body and this group
parses every one of them: *parsing lives in the tools, the store stays opaque.* Split out of `notes.md`
on 2026-08-26 per `../../README.md`'s group rule.

---

## Task 11 — reassembly, and two instruments that agree on all 979 rows, 2026-08-26

`transcript.py` reads a captured reply back into the message it was, or says which of six reasons it
was not one. **The store never parses a body and this module parses every one of them** — that is the
line the phase has to keep on the right side of, and nothing here is imported by the write path.

### The corpus was read before the code was written, and it moved three things

**Every response blob in the live corpus was decompressed and shaped**, 2026-08-26:

| Shape | Blobs |
|---|---|
| SSE | **808** |
| JSON `type=error` | **93** |
| JSON `{"input_tokens": N}` — `count_tokens` | **47** |
| zero-length | **4** |
| **JSON `type=message` — a buffered reply** | **1** |

**1 · The plan's "66 buffered replies" was the `count_tokens` count.** The task had already corrected
this exact conflation once — *"it conflated 'not streamed' with 'a buffered assistant reply'"* — and
then landed on **66**, which is the number of `count_tokens` rows. **The real figure is one call in
979.** The path is still built; what does not survive is the impression that it is a third of the
traffic, and *"both encodings are handled"* is now in "does not settle" so it is not read as coverage.

**2 · A content block has five types, not one.** `text`, `tool_use`, `thinking`, `server_tool_use`,
`web_search_tool_result`. **The last two were invisible in a two-day sample** and appeared only when
the count was re-run over all four days — 4 occurrences each. *A sample that covers 60% of a corpus
can still miss a category entirely, which is the argument for the full pass and not the fast one.*

**3 · A tool input arrives as JSON string fragments.** **64,260 `input_json_delta` against 2,071
`text_delta`** — the deltas are overwhelmingly *tool arguments*, not prose. They must be concatenated
and parsed **after** the block closes; parsing each fragment fails on all but the last. **All 654
tool inputs in the corpus parse to dicts, none left as a fallback string.**

*None of this is in the register's SSE list, which named the **events** and never what they carry.
Four rows added.*

### The strongest evidence this task produced is not a test

**`reassemble` was driven over every response blob in the live corpus and joined back to the index**,
which records `error_status` independently at capture time. **979 rows, 0 unresolved, 0
contradictions:**

| index `error_status` | reassembler says | rows |
|---|---|---|
| `ok` | **message** | **808** |
| `ok` | skip: `not-a-message` | 66 |
| `ok` | skip: `empty` | 9 |
| `http_error` | skip: `error` | 93 |
| `http_error` | skip: `empty` | 2 |
| `client_disconnect` | skip: `incomplete` | **1** |

**Two instruments, built years and phases apart, agreeing row for row.** `observe.py` wrote
`error_status` from HTTP status at capture time; `transcript.py` derives its verdict from the body's
own shape months later, knowing nothing about the column. **Nothing lines up like that by accident**,
and no green test could have said it.

*It also confirms the digest→path reconstruction — `FANOUT = 2`, `BLOB_SUFFIX = ".zst"` — on 979 rows
with **zero** unresolved, which is what the extractor will depend on.*

### The one `incomplete` stream was identified, not shrugged at

One SSE stream ends mid-`text_delta` at 912 bytes, with **no `error` event and no `message_stop`**.
Joined back to its index row: **it is the corpus's single `client_disconnect`** — *"The caller went
away before the reply finished."*

**That is why `stream-error` and `incomplete` are two reasons and not one.** An `error` event means
the router authored one because the upstream stream broke; a bare stop means **nothing went wrong
upstream at all** and the caller simply left. *`stream-error` has **zero** occurrences in the live
corpus and seven in Phase 9's gate corpus — so one of the six reasons is tested only synthetically,
and it is written down here rather than left to look like coverage.*

### What the tests carry that the corpus cannot

**18 tests, 337 → 355.** Two paths exist here or nowhere: **the buffered reply** (one real example)
and the **SSE `error` event** (none). The rest are the reverse — cheap to assert, and already proven
at scale by the pass above.

*The `data:`-split-over-several-lines test is for something Anthropic does not currently do. The SSE
spec allows it, and a reassembler that assumed otherwise would break on the day it changed, for a
reason no capture would ever explain.*
