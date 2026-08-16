# Architecture — dispatch, not translation

What the router is for, why it is a dispatcher rather than a translator, and the shape of the traffic
that constrains it.

## The goal

A router that lets a coding harness reach several model backends at once. Concretely: Claude Code
should see Anthropic's own models (Haiku, Sonnet, Opus, Fable) **and** locally served LM Studio models
simultaneously, switchable by picking a model in LM Studio.

Planned later: other harnesses (OpenAI Codex, Google Antigravity, GitHub Copilot, JetBrains Junie; Pi,
Hermes, OpenCode, OpenClaw) and other cloud backends (OpenAI, Gemini, OpenRouter).

## Why it exists at all

**Claude Code accepts exactly one `ANTHROPIC_BASE_URL`.** Pointing it at LM Studio gives up the
Anthropic models; pointing it at Anthropic gives up the local ones. Something has to sit in front and
route per request to have both at once.

## No protocol translation is needed

LM Studio (0.4.1+) natively implements the Anthropic-compatible `POST /v1/messages`, including the
same SSE event sequence (`message_start` → `content_block_start` → `content_block_delta` →
`content_block_stop` → `message_delta` → `message_stop`), `tools` with `input_schema`, and
`tool_choice`. It accepts both `x-api-key` and `Authorization: Bearer`. Claude Code can already point
straight at it:

```
ANTHROPIC_BASE_URL=http://localhost:1234
ANTHROPIC_AUTH_TOKEN=lmstudio
CLAUDE_CODE_ATTRIBUTION_HEADER=0
claude --model <lmstudio-model-id>
```

So both sides of the router speak the *same* protocol, and the router is a **model-name dispatcher /
reverse proxy**, not a translator:

- `claude-*` model IDs → forward to `api.anthropic.com`
- everything else → forward to LM Studio at `localhost:1234`

Because the protocol matches on both sides, the request body is forwarded unmodified and the response
stream relayed as bytes, rather than parsed and re-emitted. That is a decision with consequences of
its own — see `design-decisions.md`.

The second real job is **credential handling**: forward for cloud, strip or inject for local. Each
backend declares which, in one field. The modes are in `design-decisions.md`; what each backend needs
is in its own file.

## Where this premise stops

**"Dispatch, not translation" is true because both sides speak `/v1/messages`, and that is a property
of LM Studio, not of local models in general.** It is worth stating plainly, because the goal above
names four more cloud backends and none of them shares the protocol:

| Backend | Surface | What it would take |
|---|---|---|
| Anthropic, LM Studio | `POST /v1/messages`, Anthropic SSE | dispatch — what exists today |
| OpenAI, OpenRouter | `POST /v1/chat/completions`, its own SSE shape | **translation**, both directions |
| Gemini | `generateContent` / `streamGenerateContent` | **translation**, both directions |
| Another local runner | whatever it implements | check first; several serve the OpenAI shape only |

The moment a backend needs translation, the properties this architecture is built on stop holding:
the request body must be parsed and rebuilt, which breaks prompt-cache prefix matching; the reply must
be re-emitted, which means the router owns a second protocol's correctness; and the usage scanner's
one rule for both backends becomes one rule per backend. **None of that is an argument against adding
such a backend** — it is an argument for expecting it to cost a great deal more than the second one
did, and for not treating "adding a backend" as a single kind of work.

## The four routes

| Route | Behaviour |
|---|---|
| `HEAD /` | Answered locally, 200. Claude Code probes here, from a separate client, before its first real call — a router that does not answer looks like a dead endpoint at startup |
| `GET /health` | Answered locally. Not proxied, and deliberately not recorded as a call |
| `POST /v1/messages` | The model name in the body picks the backend. No model is a 400, and that refusal still writes a row |
| everything else | Forwarded. Routed on the model if the body carries one, Anthropic otherwise |

The catch-all is registered **last**, because the first matching route wins and it would otherwise
shadow the three above it. It is not hypothetical: `POST /v1/messages/count_tokens` arrives through it
in ordinary traffic.

## Observed request shape

From one captured request (`../captures/log-the-whole-request.txt` — token and account/device/session
identifiers redacted; it is one 120 KB line, so read it with `jq`). Concrete facts that constrain the
proxy:

- **Claude Code probes with `HEAD /` first**, from a separate client (`User-Agent: Bun/1.4.0`), before
  any `/v1/messages` call. The router must answer it or it looks like a dead endpoint at startup.
- **The path carries a query string**: `POST /v1/messages?beta=true`. Forward path *and* query.
- **`Accept-Encoding: gzip, deflate, br, zstd`** comes in, so requesting an uncompressed response
  upstream must be a deliberate override — otherwise `usage` can't be read from the passing bytes.
- **Body fields beyond the base API**: `context_management`, `output_config` (`{"effort":"high"}`),
  `metadata.user_id`. None were anticipated when this was first written. This is the concrete case for
  byte-relay: a Pydantic full-body model would have silently dropped all three.
- **`cache_control: {"type":"ephemeral","ttl":"1h"}`** on the system blocks. Prompt caching matches on
  exact prefix bytes, so any reserialization — even key reordering that means the same thing — breaks
  cache hits and costs real money. Byte-relay is not just about forward-compatibility.
- **A `role: "system"` message inside `messages`** (the `mid-conversation-system-2026-04-07` beta).
  Predicted here to be unsupported by LM Studio; **measured 2026-08-06 as supported and obeyed** — see
  `backend-lmstudio.md`.
- `thinking` is `{"type":"adaptive","display":"omitted"}`, and no `temperature`/`top_p`/`top_k` is
  sent at all.

**The size is the constraint.** That bare `hi` turn arrived as 118 KB of JSON — 81 KB of tool schemas
(27 tools), 28 KB of system prompt, and 368 bytes of actual conversation, which LM Studio counts as
27924 tokens of preamble before the user types anything. Every turn re-sends all of it.
