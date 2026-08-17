# Does LM Studio report token usage?

Run on 2026-07-29. **Answer: yes, in both streaming and non-streaming replies, in the same shape
Anthropic uses.** The procedure is below so it can be re-run against a different model or a newer
LM Studio, since this is the kind of thing that changes without announcement.

## Why it matters

Phase 2 writes one CSV row per call, and four of its columns depend on this: `input_tokens`,
`output_tokens`, and by extension any comparison between a local model and a cloud one that is
denominated in tokens rather than wall time. `CLAUDE.md` records the fallback if the answer had been
no — write the row with empty token columns and lean on `request_bytes` — and notes that
`request_bytes` is a weak metric, because it is dominated by the ~110 KB fixed preamble. So a "no"
here would have meant local and cloud calls were not really comparable at all.

It also decides how much of the tee-and-scan machinery is worth building. If usage were absent
locally, scanning the passing stream would only ever pay off for Anthropic traffic.

## Procedure

Requires LM Studio running with a model loaded. If "Require Authentication" is on, add
`-H 'Authorization: Bearer <token>'` to every request below, or turn it off for the duration.

**1. Find the loaded model.** The Anthropic-compatible namespace has no `/v1/models`, so use the
native endpoint:

```bash
curl -s http://localhost:1234/api/v1/models | python3 -c "
import json,sys
for m in json.load(sys.stdin)['models']:
    if m.get('loaded_instances'):
        print(m['key'], m.get('max_context_length'), m.get('capabilities'))
"
```

**2. Non-streaming.** `usage` should appear as a top-level key of the reply:

```bash
curl -s -X POST http://localhost:1234/v1/messages \
  -H 'content-type: application/json' -H 'anthropic-version: 2023-06-01' \
  -d '{"model":"<key>","max_tokens":40,
       "messages":[{"role":"user","content":"Say hello in exactly five words."}]}' \
  | python3 -m json.tool
```

**3. Streaming.** This is the case that actually matters, because Claude Code streams and Phase 2
reads the numbers off the passing bytes rather than out of a parsed body:

```bash
curl -s -N -X POST http://localhost:1234/v1/messages \
  -H 'content-type: application/json' -H 'anthropic-version: 2023-06-01' \
  -d '{"model":"<key>","max_tokens":30,"stream":true,
       "messages":[{"role":"user","content":"Say hi."}]}' > sse.txt

grep '^event:' sse.txt | uniq -c    # the event sequence
grep -n 'usage' sse.txt             # where the numbers live
```

**4. Through the router.** Same request against `http://127.0.0.1:8787`, with
`-H 'accept-encoding: gzip, deflate, br, zstd'` to prove the identity override is doing its job. If
usage is readable here, Phase 2 can read it.

## Result

**Non-streaming** — `usage` is a top-level key, exactly as Anthropic sends it:

```json
"usage": { "input_tokens": 20, "output_tokens": 39, "cache_read_input_tokens": 0 }
```

**Streaming** — the event sequence is Anthropic's, and usage appears twice:

```
message_start → content_block_start → content_block_delta ×29 → content_block_stop
              → message_delta → message_stop
```

```
message_start:  "usage":{"input_tokens":15,"output_tokens":0,"cache_read_input_tokens":5}
message_delta:  "usage":{"input_tokens":15,"output_tokens":29,"cache_read_input_tokens":5}
```

**Through the router** — identical, with `accept-encoding: gzip, deflate, br, zstd` on the way in.
The identity override works and the numbers arrive readable in the relayed stream.

Model was `google/gemma-4-e4b`, the same one that drove the Phase 1 session.

## What this means for Phase 2

**Take `input_tokens` from `message_start` and `output_tokens` from the final `message_delta`.** That
rule works for both backends. Note the temptation to simplify it: LM Studio repeats `input_tokens`
in `message_delta`, so a scanner keyed only on that event would collect both numbers in one place
and appear to work — against LM Studio. Anthropic's `message_delta` carries only `output_tokens`, so
the same scanner would silently record empty input counts for every cloud call. Do not key on
`message_delta` alone. (Anthropic's streaming shape here is from its documentation; this check only
observed LM Studio, so confirm it against a real cloud stream when Phase 2 is built.)

**`cache_read_input_tokens` is reported too, and is now a CSV column.** LM Studio is doing real
prefix caching — the value rose from 5 to 15 between two runs of the same prompt, a full hit on the
second. This check is what put the column in the spec: prompt-cache behaviour is the reason the body
is relayed byte for byte, so a cache-hit rate that collapses is the signal that something has
started rewriting request bytes. Without the column that failure is invisible.

**Non-streaming needs its own path.** The number sits at a top-level `usage` key rather than inside
an SSE event, so a scanner written only for the streaming shape will find nothing. Both forms are in
use — Claude Code streams, but the catch-all route may carry anything.

## Not answered by this check

The rest of LM Studio's parity, which remains Phase 4's job: a `role: "system"` message inside
`messages`, `thinking` blocks, images. Tool calls are already known to work from the Phase 1 session
— see `testing-against-claude-code.md`.
