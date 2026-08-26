# Phase 11 — evidence

**Frozen 2026-08-26 by Task 7.** *(This file read "Empty until Task 5" until then, and named the wrong
task twice. Task 5 is the `IDM-002` amendment; **Task 7** is "Freeze the evidence slice" — the same
stale task number the plan's register §8 already had to correct once.)*

`../../../README.md`'s rule: evidence is cited to something **committed**, because `logs/` is
gitignored and rotates. The source is the owner's live corpus at `to-run-server/logs/corpus/`, which
**grows while it is read** — so nothing here cites it by path, and every figure carries its moment.

## What is here

| File | What it is |
|---|---|
| `freeze.py` | What produced the rest. Standard library only, so it does **not** need the project venv |
| `index-2026-08-21.csv` | 10 rows |
| `index-2026-08-24.csv` | 317 rows |
| `index-2026-08-25.csv` | 413 rows |
| `index-2026-08-26.csv` | 239 rows |

**979 rows, 26 columns, taken 2026-08-26T15:16:22Z.** The index only. **No blobs, and there never
will be** — captured request bodies are real prompts and real source code, response bodies are real
model output about them, and neither is redactable to placeholders in any meaningful sense.

## What was redacted, and how

**To stable placeholders in first-appearance order, never by blanking.** `../../../README.md` is
explicit that blanking destroys the finding while protecting nothing: *which rows share a
`session_id`* is the basis of every per-session claim this phase makes. **Equality is preserved
exactly and the raw values are recorded nowhere.**

| Family | Distinct | Becomes |
|---|---|---|
| `session_id` | **9** non-empty | `session-01` … `session-09` |
| `agent_id` | **1** non-empty | `agent-01` |
| `request_ref` | **821** digests | `req-1` … `req-821` |
| `response_ref` | **934** digests | `resp-1` … `resp-934` |

**Two families were taken beyond the one that was asked for**, per README.md's first practical rule:
the two `*_ref` digest columns. A sha256 does not reveal a body, but it **confirms a guess about one**,
and placeholders preserve every analytical property that matters here — dedup counts, cross-day
identity, and which rows share a blob.

**`request_dict_id` is deliberately *not* redacted.** It names a dictionary, not a person, and
`9dd33823` is already committed in `../../../status.md`.

**The five sentinels pass through unchanged** — `dropped`, `too_large`, `absent`, `error`, `none`. A
sentinel run through a digest redactor becomes a **fake identifier**, and the extractor's whole reason
for knowing them is to read "no blob here" rather than a filename.

## The secrets pass, which is a separate problem

**Run separately from identifiers**, per README.md's second practical rule, and **on the redacted rows
that actually get committed** — which also covers any column this script does not redact. Nothing is
written unless it comes back clean. **It came back clean.**

***The first run of it reported 1913 suspect cells and every one was a sha256 digest.*** Sixty-four hex
characters satisfy any "long base64-ish blob" rule. `CLAUDE.md`: **when a check comes back negative,
fix the instrument before believing the result.** The pattern now excludes pure hex, and the comment in
`freeze.py` says why so nobody removes the exclusion as noise.

**The index carries no header and therefore no credential by construction** — `../../../reference/corpus.md`
says the store is attached to a tee of body bytes and never sees a header at all. That is an argument;
the pass is the check, and both are wanted.

## Can it be regenerated? No, and that is the honest answer

**Re-running `freeze.py` on any later day produces a larger slice with a different mapping.** The
corpus is live: it read **770 rows** during this plan's ratification earlier the same day and **979**
here. The committed CSVs *are* the record; `freeze.py` is committed so the redaction is **auditable**,
not so the result is reproducible.

## What the slice establishes

**Every one of the forward review's data findings reproduces on it**, at four to five times the sample
they were found on:

| | Confirmed |
|---|---|
| **The `too_large` tail is structural** | **45 rows, all in `session-07`** — the corpus's largest session at 292 calls. The **only** sentinel present anywhere, and **no response is ever `too_large`**: requests are cumulative and grow, responses do not |
| **A session spans day folders** | `session-08`, **276 calls across 2026-08-25 and 2026-08-26**. It was 39 + 19 when finding 5 was written |
| **`agent_id` is a partition key, not a filter** | **67 rows, one agent, every one of them inside `session-08`** — the parent's session. Confirmed exactly as the review reported |
| **Both response encodings are live** | **807** streamed ok, **67** buffered ok. "Reassemble the SSE stream" is half the job |
| **Error responses are not rare** | **93** `http_error` at `stream=false`, **2** more with `stream` empty, **1** `client_disconnect`. All 93 are `429` |
| **`count_tokens` is in the same sessions** | **66 rows**, against 902 `/v1/messages` |
| **A row can have no `session_id`** | **11 rows** — 9 × `/api/hello`, 1 × `/`, 1 × `/favicon.ico`. `<out>/bodies//00001-request.json` is not a path |
| **Bodies dedup** | request **934 rows → 821 distinct**; response **979 → 934**. `<seq>` cannot be derived from a digest |
| **LM Studio traffic exists** | **1 row**, `google/gemma-4-e4b`, in `2026-08-21` |

**One thing the slice adds that no earlier reading had:** `absent` **never appears**, not even on the
9 router-authored `/api/hello` rows, which carry real digests. Four of the five sentinels have never
been observed in this corpus.
