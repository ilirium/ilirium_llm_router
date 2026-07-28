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

Columns are listed in CLAUDE.md. Note `request_bytes` is dominated by the fixed ~110 KB preamble of
system prompt and tool schemas, so treat it as a fallback rather than a measure of conversation size.
"""

from __future__ import annotations
