# Phase 2 step 6 — the frozen session

The evidence behind `docs/epd/EPD-002-token-counting-for-local-backends.md`, and behind the claim that Phase 2
step 6 passed. Captured 2026-07-31 on this machine, copied here because `logs/` is gitignored and
both files rotate — without this directory the numbers quoted in EPD-002 would have no source.

**Frozen. Do not regenerate.** A later session will produce different rows, and the row numbers cited
in EPD-002 point into `calls.csv` as it stands here.

## What the session was

A real Claude Code session run through the router, following the procedure in
`testing-against-claude-code.md`. It exercised: a long conversation, switching models mid-session,
subagents, interrupting a long response, tool use with local models reading and writing files, and
asking a local model about earlier messages.

142 calls. Two backends. Eleven client sessions, of which two carried both backends — which is the
project's central claim measured rather than argued.

## Redaction

`calls.csv` has been redacted; `router.log` has not, because it needed nothing.

| Column | Treatment |
|---|---|
| `session_id` | Replaced with `session-01` … `session-10`, in first-appearance order |
| `agent_id` | Replaced with `agent-01` (there was only one) |

The mapping was applied once and **the raw values were not recorded anywhere**, so this cannot be
reversed.

Placeholders rather than blanks, deliberately: the grouping *is* the evidence. Which rows share a
session is what shows a single session reaching both backends, and which rows share an agent ID is
what answered the open question about whether `x-claude-code-agent-id` arrives at all. Blanking the
column would have destroyed the finding while protecting nothing extra.

Two rows have a genuinely empty `session_id` — those are the curl smoke tests, which sent no header.
That emptiness is original, not redaction.

`router.log` was checked for UUIDs, bearer tokens, `sk-` strings and authorization headers, and
contains none. It carries loopback addresses and PIDs only.

## Reading the two files together

**The clocks differ.** `router.log` is naive **local** time; `calls.csv` is **UTC** with an explicit
offset. Local was UTC+3 on the day, so log `11:46:47` is CSV `08:46:47+00:00`. This is a known defect
in the recorder, listed as one of four open recorder fixes, and it is preserved here rather than
corrected — the artefact should show what the router actually wrote.

**The CSV is in completion order, not arrival order.** `timestamp` is when the request arrived, and
the row is appended when the response finishes, so a slow call lands after faster calls that started
later. Fourteen adjacent pairs are out of order. Sort before analysing.

## What is in here worth knowing

- **`agent_id` arrives.** Seven rows carry `agent-01`, covering both the subagent's own background
  calls and its main call. Closes an open question that had stood since EPD-001.
- **`client_disconnect` is reachable.** Six rows, on both backends. Closes the other one.
- **32 `count_tokens` rows are logged `ok` and are not.** LM Studio answers HTTP 200 with an error
  body. This is the whole subject of EPD-002.
- **40 rows returned zero content tokens** — `stop_reason: max_tokens`, `output_tokens: 0`. Claude
  Code's prompt-cache warmup probes, which cost 20.0 of the 45.5 minutes of local wall time.
- **`stream` is empty, never `false`.** Claude Code omits the field rather than sending `false`, and
  the recorder writes `None` as blank. Another of the four open recorder fixes; also preserved.
