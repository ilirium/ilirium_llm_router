# 3. Smoke-test with curl before involving `claude`

```bash
% curl -i -X HEAD http://127.0.0.1:8787/
Warning: Setting custom HTTP method to HEAD with -X/--request may not work the
Warning: way you want. Consider using -I/--head instead.
HTTP/1.1 200 OK
date: Fri, 31 Jul 2026 08:21:00 GMT
server: uvicorn
content-length: 0
```

```bash
ilirium@ilirium-mbp ilirium_llm_router % curl -N -X POST http://127.0.0.1:8787/v1/messages \
  -H 'content-type: application/json' \
  -d '{"model":"qwen/qwen3.5-9b","max_tokens":64,"stream":true,
       "messages":[{"role":"user","content":"count to five"}]}'
event: message_start
data: {"type":"message_start","message":{"id":"msg_bqo3du1eehlp7o40clml9g","type":"message","role":"assistant","content":[],"model":"qwen/qwen3.5-9b","stop_reason":null,"stop_sequence":null,"usage":{"input_tokens":14,"output_tokens":0,"cache_read_input_tokens":0}}}

event: content_block_start
data: {"type":"content_block_start","index":0,"content_block":{"type":"text","text":""}}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"1"}}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":","}}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":" 2"}}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":","}}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":" 3"}}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":","}}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":" 4"}}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":","}}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":" 5"}}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"."}}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":""}}

event: content_block_stop
data: {"type":"content_block_stop","index":0}

event: message_delta
data: {"type":"message_delta","delta":{"stop_reason":"end_turn","stop_sequence":null},"usage":{"input_tokens":14,"output_tokens":15,"cache_read_input_tokens":0}}

event: message_stop
data: {"type":"message_stop"}
```

# 4. Point Claude Code at it

> ***ANNOTATED 2026-09-22, and the commands below are deliberately NOT edited.*** **They carry
> `CLAUDE_CODE_ATTRIBUTION_HEADER=0`, which this repository now tells you not to set** — *it
> suppresses an attribution block Claude Code sends in its request body, and Anthropic rejects a
> non-streamed `/v1/messages` that arrives without one.* **That is `BUG-001`, and it cost Phase 14
> three days.**
>
> ***This file records what was actually run on 2026-08-04.*** *Editing the command to remove an
> inconvenient line would make the record say something that did not happen* — **the measurements
> below stand, and the sessions that produced them were streamed, which is the half the variable
> does not break.** *`docs/bugs/BUG-001-…` and `milestone-2-corpus/phase-14-rate-limit-headers/`.*


```bash
ANTHROPIC_BASE_URL=http://127.0.0.1:8787 CLAUDE_CODE_ATTRIBUTION_HEADER=0 \
  claude --model claude-sonnet-5
```

```
Anthropic base URL:  http://127.0.0.1:8787
Model:               claude-sonnet-5
```

```bash
ANTHROPIC_BASE_URL=http://127.0.0.1:8787 CLAUDE_CODE_ATTRIBUTION_HEADER=0 \
  claude --model qwen/qwen3.5-9b
```

```
Anthropic base URL:  http://127.0.0.1:8787
Model:               qwen/qwen3.5-9b
```