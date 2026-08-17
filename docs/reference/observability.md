# Observability — the log and the CSV

Every call is logged **and** appended as one row to a CSV, so model/backend comparisons are analysable
without parsing free-text logs. This file is the specification of what is recorded and why; read it
before touching the recorder.

## CSV columns

Twenty, in this order.

| Column | Source |
|---|---|
| `timestamp` | ISO 8601, when the request arrived |
| `session_id` | `x-claude-code-session-id`, copied from the request headers. Groups a session's calls without parsing bodies. Empty when the header is absent, since a non-Claude-Code caller has no reason to send it |
| `agent_id` | `x-claude-code-agent-id`. **Present only on requests from a subagent**, so an empty value means the main conversation — that emptiness is the signal, not missing data. Without this column a mixed-model session collapses into an indistinguishable pile of rows. See `../epd/EPD-001-model-selection-and-mixed-model-sessions.md` for why mixed-model sessions are expected at all |
| `backend` | `anthropic` or `lmstudio` |
| `model` | peeked from the request body |
| `path` | the request path, without the query string. Almost always `/v1/messages`, and that is the point: the catch-all route forwards endpoints we did not anticipate, and without this column those rows are indistinguishable from ordinary ones. Turns a standing "other endpoints" worry into a list of facts |
| `stream` | boolean, peeked from the request body alongside `model` — it is already a routing-relevant field, so it costs nothing extra. Its real value is diagnosing the recorder rather than the call: empty token columns with `stream` true means the SSE scanner failed, empty with `stream` false means the non-streaming path failed. Two different bugs that are otherwise indistinguishable in the file. **An absent `stream` field is written as `false`**, because the API defaults it so and Claude Code omits it rather than sending it — reading absence as unknown left 83 of 142 rows blank on 2026-07-31 and made the diagnosis above impossible. An empty cell now means only that the body did not parse, or said something non-boolean |
| `input_tokens` | `usage.input_tokens`, tee'd from the response |
| `output_tokens` | `usage.output_tokens` (free alongside the above) |
| `cache_read_input_tokens` | `usage.cache_read_input_tokens`. Reported by both backends and free alongside the other two. It is here because prompt-cache behaviour is *why* the body is relayed byte for byte: without this column the project's most expensive constraint stays an assumption instead of a measurement. Empty when a backend omits it |
| `cache_creation_input_tokens` | `usage.cache_creation_input_tokens`, free alongside the read count. It is what makes the read count interpretable: without it a low `cache_read` cannot be told apart from a legitimate first write on a new prefix, which is the difference between "nothing is wrong" and "something upstream is rewriting our bytes". Empty when a backend omits it |
| `stop_reason` | from the final `message_delta`, or the top level of a non-streaming reply. `max_tokens` where `end_turn` was expected is truncation made visible, which otherwise degrades answers without ever failing loudly |
| `request_bytes` | raw body length — always available, even when `usage` is not. Note it is dominated by the fixed preamble of roughly 110 KB, so it is a weak proxy for conversation size; keep it as the fallback it is, not the comparison metric |
| `response_bytes` | bytes relayed downstream, counted on the tee that is there anyway. Unlike `request_bytes` it carries no fixed preamble, so it is a fair measure of how much came back — but it counts SSE framing as well as content, so treat it as a volume signal rather than a token proxy. Its steadiest use is the case `usage` doesn't cover: a reply that arrived empty or stopped early still leaves a number here |
| `ttfb_ms` | time to first byte of the response. The only column that captures the *felt* difference between backends: a local model that stalls for seconds and then streams quickly is a different experience from a cloud model that starts at once, and `duration_ms` averages that distinction away |
| `duration_ms` | wall time until the response *completes* (stream fully drained), not time to first byte |
| `error_status` | how the call ended: `ok`, `http_error`, `stream_error`, `transport_error`, `client_disconnect`. Replaces an earlier `is_error` boolean, which could not express a client that disconnected mid-stream — neither a success nor a backend failure. Same width, and it makes the common failure modes countable with a spreadsheet filter instead of a judgement call |
| `error_code` | HTTP status, or a symbolic code for transport failures. `error_status` says what *kind* of failure it was, this says *which* one; both are empty when `error_status` is `ok` |
| `error_message` | short description, single line, no embedded newlines. Written as `type: message` when the backend's error body carried both — on an HTTP error `error_code` holds the status, so this column is the only place the symbolic type survives, and it is the countable half. Anthropic answers a rate-limited call with the bare word `Error`, which alone says nothing; the same call now reads `rate_limit_error: Error` |
| `router_version` | the router's own version. Measurements taken weeks apart across a changing router are otherwise hard to compare, and the cost is one short string per row |

**A note on the cache columns, since they are the ones that needed justifying:** LM Studio does real
prefix caching, first observed rising from 5 to 15 tokens across two runs of the same prompt and later
measured at 27904 tokens on a real request. A cache-hit rate that collapses is the signal that
something upstream has started rewriting request bytes — exactly the failure byte-relay exists to
prevent, and otherwise invisible.

## Constraints on the recorder

These are the ones a plausible-looking implementation quietly violates.

- **The two identifier columns come from headers, not the body.** Copying `x-claude-code-session-id`
  and `x-claude-code-agent-id` costs a dictionary lookup and needs no parsing, which is the whole
  reason they are affordable. Neither is a user identifier: an agent ID identifies a spawn, and
  subagent IDs are generated fresh each time. Both are now measured as arriving — the agent header was
  documented only until the 2026-07-31 session produced seven rows carrying one.
- **Tee, don't parse-and-rebuild.** Relay response bytes downstream untouched while scanning a copy
  for `usage`. Byte-relay fidelity is preserved; observation is passive. If `usage` can't be found,
  write empty token columns rather than failing the request.
- **Take `input_tokens` from `message_start` and `output_tokens` from the final `message_delta`.**
  Verified against LM Studio on 2026-07-29 (`../procedures/lmstudio-usage-check.md`); both backends
  carry usage in Anthropic's shape, so one rule covers both. Resist the obvious simplification:
  LM Studio repeats `input_tokens` in `message_delta`, so a scanner keyed on that event alone would
  look correct locally and silently record empty input counts for every Anthropic call. Non-streaming
  replies put `usage` at the top level instead, so that form needs its own path.
- **`stop_reason` shares the scanner with `usage`, and shares its trap.** It rides the final
  `message_delta` streaming and the top level otherwise, so it is nearly free once the usage scanner
  exists — but only if that scanner already handles both forms. Build them together rather than
  bolting one on afterwards.
- **Which path runs is decided by the response `content-type`, not by the request's `stream` flag.**
  The content-type describes what the bytes *are*; the request flag describes what was *asked for*.
  Keeping them separate is what makes a `stream: true` row scanned by the buffered path a visible
  disagreement rather than an invisible one.
- **`stream` and `response_bytes` are the recorder's own instruments.** Both are nearly free — `stream`
  is peeked for routing already, `response_bytes` is a counter on an existing tee — and both earn
  their place mainly by making a *failed* row interpretable. A row with no tokens is a dead end on its
  own; the same row saying which code path ran and how many bytes went past is a bug report.
- **Two clocks, not one.** `ttfb_ms` stops at the first response byte and `duration_ms` at the last.
  Both start when the request arrives, so the pair reads as "how long until it began" and "how long in
  total" rather than needing subtraction. Time to first byte is the more interesting of the two when
  comparing a local model against a cloud one, and it is measured at the first byte of the *body*, not
  at the headers — headers arrive as soon as the backend accepts the request, which for a streamed
  reply says nothing about when the model started producing.
- **Streaming hides errors behind a 200.** A streamed response returns HTTP 200 before content exists,
  so a backend failure can arrive as an SSE `error` event mid-stream. Error detection must watch the
  tee'd stream, not just the initial status code — that case is `error_status: stream_error`, and it
  is exactly why a boolean was not enough.
- **Transport errors matter most here.** LM Studio simply not running is the common failure. That is a
  connection error with no HTTP status — `error_status: transport_error` with a symbolic `error_code`
  derived from the exception class, rather than leaving both blank.
- **Never let telemetry break a call.** Any failure in logging or CSV writing is caught and dropped;
  the proxied request always wins, including when the disk is full.
- **The body is never logged.** It carries the whole conversation, and on the cloud side it arrives
  alongside a real credential.
- **Don't store what a spreadsheet can derive.** Tokens per second is the headline comparison, and
  precisely for that reason it stays out of the file: a stored derivation can drift out of agreement
  with the columns it came from. Same for anything body-shaped — no prompts, no message counts, no
  tool names. Those are steps toward parsing what the router promised only to relay.
- **The CSV is in completion order; sort before analysing.** A row is appended when its call finishes,
  while `timestamp` records when it *arrived*, so a slow call lands after quicker ones that started
  later — 14 adjacent pairs are out of order in the 2026-07-31 session. Deliberately not fixed:
  ordering the file would mean holding finished rows until the calls that started before them came
  back, which trades a spreadsheet sort for losing every buffered row when the process stops.
- **Both files timestamp in UTC, in the same format.** The log writes
  `2026-07-31T08:46:47.339+00:00`, character-for-character what the CSV's `timestamp` column holds, so
  a log line and its row merge-sort together. The log used to write naive local time, which meant
  correlating the two files — the whole reason uvicorn's lines share the router's log — required
  remembering an offset that appeared in neither.
- **Rotation is size-based for both files**, with sizes set in YAML. On rotation the CSV must
  **re-emit its header row** in the new file, or rotated segments won't parse standalone.

**Non-streaming replies are buffered to a 1 MiB cap**, then parsed once. `usage` in a buffered reply
sits inside one JSON object and an object's contents are unknown until its closing brace, so "never
buffer the whole reply" cannot hold literally for that path. The cap exists because of the *catch-all
route*: the reply to an endpoint nobody has enumerated could be anything, and the cap turns "memory
decided by an unknown endpoint" into a known ceiling. At the cap, the row is written with empty token
columns; the relay is never affected, so the cap can cost observation and never fidelity.

## Config shape

```yaml
logging:
  level: INFO
  file: logs/router.log
  max_bytes: 10485760   # 10 MiB
  backup_count: 5

stats:
  file: logs/calls.csv
  max_bytes: 5242880    # 5 MiB
  backup_count: 10
```

Relative paths resolve against the config file's directory, not the working directory. **Uvicorn's own
loggers are pointed at the same file**, so "did the request arrive" and "was the server up" sit next
to the router's own line for the same call — which is the whole reason the two files share a clock and
a format.
