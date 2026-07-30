"""One CSV row per call, so models and backends can be compared in a spreadsheet.

Not implemented yet — this is Phase 2. Constraints established beforehand:

- Tee, do not parse and rebuild. Relay the response bytes downstream untouched while scanning a
  copy for `usage`. Observation must stay passive.
- Do not buffer the whole reply to do it. Keep a small working buffer and discard as you go.
- If `usage` cannot be found, write the row with empty token columns rather than failing the call.
  `request_bytes` is always available, so a row is never useless.
- A streamed response reports HTTP 200 before any content exists, so a backend failure can arrive
  as an SSE `error` event mid-stream. Watch the tee, not just the initial status code.
- Never let telemetry break a call. Any failure here is caught and dropped.
- Rotation is size-based. On rotation the CSV must re-emit its header row, or rotated segments
  cannot be parsed on their own.
- Several calls can finish at once; rows must not interleave into corrupted lines.
- `session_id` and `agent_id` are copied from the `x-claude-code-session-id` and
  `x-claude-code-agent-id` request headers, not from the body. `agent_id` arrives only on a
  subagent's call, so empty means the main conversation rather than a missing value.
- `stop_reason` comes off the same tee as `usage` and lives in the same two places — the final
  `message_delta` when streaming, the top level otherwise. Write both paths at once.
- Two clocks, both started when the request arrives: `ttfb_ms` stops at the first response byte,
  `duration_ms` at the last.
- `stream` is peeked from the body alongside `model`; `response_bytes` is counted on the tee. Both
  are nearly free, and both exist mainly so that a row with empty token columns still says which
  extraction path ran and whether anything came back at all.
- `error_status` is one of `ok`, `http_error`, `stream_error`, `transport_error`,
  `client_disconnect`. It says what kind of failure it was; `error_code` says which one. Both error
  columns are empty when the status is `ok`.
- Nothing derived and nothing body-shaped. Tokens per second belongs in the spreadsheet, not here,
  and prompts, message counts and tool names belong nowhere in this file at all.
- `router_version` is `__version__` from this package. Note it is currently written out twice, here
  and in pyproject.toml, so the two can drift and a row would then record a version that was never
  released. Reading it from installed metadata instead would remove the duplication.

Columns are listed in CLAUDE.md. Note `request_bytes` is dominated by the fixed ~110 KB preamble of
system prompt and tool schemas, so treat it as a fallback rather than a measure of conversation size.
"""

from __future__ import annotations
