# Anthropic as a backend

The cloud half. Everything a request needs to be accepted, and what comes back when it is not.

**Read this before naming an Anthropic model**, before changing anything about the outgoing
credential, and before assuming a failure is the router's.

## Model IDs

Use exact strings; **do not append date suffixes.**

| Tier | ID |
|---|---|
| Fable 5 | `claude-fable-5` |
| Opus 4.8 | `claude-opus-4-8` |
| Sonnet 5 | `claude-sonnet-5` |
| Haiku 4.5 | `claude-haiku-4-5` |

The `claude-` prefix is also the routing rule, so any correctly named Anthropic model routes here
without touching config, and a typo that loses the prefix goes to the local backend instead of failing.

## Two request shapes that are rejected

Both matter to a proxy that might be tempted to add fields:

- **`thinking` is `{"type": "adaptive"}`** on current models. `budget_tokens` is **rejected**. (LM
  Studio accepts the budget and ignores it, which is the opposite failure — see
  `backend-lmstudio.md`.)
- **`temperature`, `top_p` and `top_k` are rejected** on Opus 4.7+, Sonnet 5 and Fable 5. A naive
  passthrough that injects sampling parameters will 400.

Claude Code sends neither, so these bite a *router* that adds them, not the harness.

## Authentication: forward, and hold nothing

**`credential: forward`.** The arriving credential is the real one and Anthropic accepts it, so the
router holds no Anthropic key of its own. That is a property of this one backend rather than of the
architecture — the modes and the reasoning are in `design-decisions.md`.

Measured on 2026-07-28 by capturing what Claude Code actually sends and replaying it
(`../anthropic-auth-check.md`):

- **The credential is an OAuth subscription token** — `Authorization: Bearer sk-ant-oat01-…`. No
  `x-api-key` header is sent at all.
- It arrives with **`anthropic-version: 2023-06-01`** and **`anthropic-beta`, a ten-entry
  comma-separated list**.
- **The beta list must reach Anthropic verbatim.** One entry — `oauth-2025-04-20` — is what makes the
  bearer token acceptable, so trimming the list turns a working request into a 401.

The test that settled it returned **429**, and a 429 is the useful answer: a bad token returns 401 and
a token scoped away from the endpoint returns 403, so a rate-limit response means authentication had
already succeeded on `/v1/messages` with the headers sent exactly as Claude Code sends them.

One thing to be clear about: in this arrangement the client really is Claude Code, and the router only
relays its traffic unmodified. That is what `ANTHROPIC_BASE_URL` exists for.

## What a rate limit looks like

Ordinary and self-healing. The 2026-07-31 session produced **eight 429s, all retried successfully by
Claude Code**; the session never noticed. One was followed by a 200 five seconds later, which is
itself evidence the credential was fine — a rejected token does not recover in five seconds.

Their `error.type` is `rate_limit_error`, established by reconstruction rather than read directly,
because the recorder was discarding the symbolic type at the time. **It now keeps it**, so the next 429
through the router writes `rate_limit_error: Error` into the CSV by itself — measured rather than
inferred. Watch for it rather than going looking; reproducing one deliberately costs a real rate limit.

`error_message` reads the bare word `Error` because that is Anthropic's own wording. Alone it says
nothing, which is precisely why the symbolic type is kept beside it.

**Still unverified: the `anthropic-ratelimit-*` and `retry-after` headers.** The router tees response
*bodies* and never response headers, so no evidence here can carry them. Only a direct curl with the
token can settle it.

## Timeout

**`read_timeout: 600`.** Ten minutes of silence from a backend whose median time to first byte is
**1426 ms** already means something is wrong rather than slow.

**That median is over successful streamed `/v1/messages` calls** — 32 rows of the 2026-07-31 session.
The slice is not decoration: over every row in the same file the median is 1252 ms, because the file
also holds `count_tokens` calls answered in milliseconds. Both numbers are right and they answer
different questions. `measurements.md` carries the full recipe.

Note what `read` bounds: the longest permitted **silence between two reads**, restarted by every chunk
— not the duration of a call. See `backend-lmstudio.md`, where the difference is what mattered.

## What this backend is measured against

Far less than the local one, and deliberately so: Anthropic implements its own API, so parity is not a
question here. What has been measured is that a real session works end to end
(`../testing-against-claude-code.md`), that streamed replies scan exactly like LM Studio's, and the
failure shapes above. Anthropic was left alone during the review phase, so the claims resting on live
behaviour are consistent with their committed transcripts rather than re-measured.
