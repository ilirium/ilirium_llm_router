# Checking how Claude Code authenticates

## Why this matters

The router forwards requests to two places: LM Studio locally, and Anthropic in the cloud. The local
side needs no real credential. The cloud side does, and the question is where that credential comes
from.

Claude Code can be signed in two different ways. With an API key, the key travels on every request
and can simply be passed along. With a subscription login (Pro or Max), what travels is an OAuth
token instead, which is a different kind of credential and may not be usable the same way.

This decides whether the router needs to hold an Anthropic API key of its own, or can stay out of the
credential business entirely. Answer it before building the proxy — it is cheap to check and it
changes the design.

Nothing here affects the local half, which works either way.

## Test A — look at what Claude Code actually sends

This is the decisive test: rather than reasoning about which login is configured, watch the request
go past.

In one terminal, start a listener that prints whatever arrives:

```
nc -l 1234
```

In a second terminal, point Claude Code at that listener and make one call against a cloud model:

```
ANTHROPIC_BASE_URL=http://localhost:1234 claude --model claude-sonnet-5 -p "hi"
```

`nc` prints the request headers and then hangs, because nothing answers. Claude Code will report an
error. That is expected; the headers are what we came for. Stop both with Ctrl-C.

Now read the headers. Treat the credential itself as a secret and do not paste it anywhere.

| What appears | What it is |
|---|---|
| `x-api-key: sk-ant-api03-…` | A plain API key |
| `authorization: Bearer sk-ant-oat01-…`, usually alongside `anthropic-beta: oauth-2025-04-20` | An OAuth subscription token |

## Test B — if it is an OAuth token, does it still work?

An OAuth token is not automatically unusable. It is accepted at the messages endpoint when sent as a
bearer token together with the OAuth beta header, both of which Claude Code is already sending. So
forwarding the request untouched may simply work, and that is worth confirming before concluding
otherwise.

Using the token from Test A:

```
curl -s -o /dev/null -w '%{http_code}\n' https://api.anthropic.com/v1/messages \
  -H "authorization: Bearer <token from Test A>" \
  -H "anthropic-beta: oauth-2025-04-20" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-sonnet-5","max_tokens":16,"messages":[{"role":"user","content":"hi"}]}'
```

A `200` means plain forwarding works. A `401` or `403` means the token is scoped in a way that rules
this out, and the cloud side will need its own API key, billed separately from the subscription.

## Quicker but less direct

`/status` inside Claude Code shows how the session is currently authenticated. If the `ant` CLI is
installed, `ant auth status` reports which credential source is active. Both are faster than Test A
but answer a slightly different question: they describe what is configured, not what is transmitted.
Use them for a quick orientation and Test A when it actually matters.

## What this changes in the design

The plan originally assumed the router would keep an Anthropic API key in `.env` and attach it to
cloud-bound requests. If Test A or Test B shows that the credential arriving from Claude Code is
usable as-is, that step is unnecessary and should be dropped.

The simpler arrangement: set Claude Code's `ANTHROPIC_AUTH_TOKEN` to the real Anthropic credential
and have the router forward whatever arrives on cloud-bound requests. This works for API keys and
OAuth tokens alike, keeps any secret out of the router's configuration, and means one less thing to
get wrong. LM Studio is unaffected, since it accepts any token and ignores it entirely unless
"Require Authentication" has been switched on.

One refinement either way: **strip the credential from requests heading to LM Studio.** A real
Anthropic credential is of no use to a local server and should not be handed to one that might write
it to a log. The rule becomes *forward for cloud, strip for local*, which is both simpler than
injecting a key and safer than passing it everywhere.

## Result

Both tests were run on 2026-07-28. The full captured request is in `log-the-whole-request.txt`, with
the token and the account, device and session identifiers replaced by `REDACTED-*` placeholders.

- **Credential type observed:** OAuth subscription token — `Authorization: Bearer sk-ant-oat01-…`,
  accompanied by `anthropic-beta: claude-code-20250219,oauth-2025-04-20,…` (ten beta flags in all)
  and `anthropic-version: 2023-06-01`. No `x-api-key` header is sent.
- **Test B status code:** `429`.
- **Decision:** forward the arriving credential; the router holds no Anthropic key of its own.

### Why a 429 settles the question

A 429 is not a rejection of the credential. A bad token returns 401, and a token scoped away from the
endpoint returns 403. A 429 is returned *after* authentication succeeds, on rate or usage grounds —
so the token was accepted at `/v1/messages` when sent exactly the way Claude Code sends it. That is
the fact Test B set out to establish.

The original curl in Test B discarded the response body (`-o /dev/null`), which is why the 429 was
ambiguous at first. To confirm the limit is an ordinary one rather than something unexpected, re-run
showing headers and body:

```
curl -sS -D- -o- https://api.anthropic.com/v1/messages \
  -H "authorization: Bearer <token>" \
  -H "anthropic-beta: claude-code-20250219,oauth-2025-04-20" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-sonnet-5","max_tokens":16,"messages":[{"role":"user","content":"hi"}]}'
```

An `error.type` of `rate_limit_error` alongside `anthropic-ratelimit-*` or `retry-after` headers means
the subscription's usage window was simply full at that moment.

### What this means in practice

Set Claude Code's `ANTHROPIC_AUTH_TOKEN` to the real credential, point `ANTHROPIC_BASE_URL` at the
router, and have the router pass the `Authorization` header through unchanged on cloud-bound
requests. The `anthropic-beta` header must be forwarded verbatim too — `oauth-2025-04-20` is what
makes the bearer token acceptable, and dropping it would turn a working request into a 401.

The credential is stripped from requests heading to LM Studio, as described above.

One thing to be clear about: in this arrangement the client really is Claude Code, and the router
only relays its traffic unmodified. That is what `ANTHROPIC_BASE_URL` exists for. Using a
subscription token from some *other* client is a different thing and is not what this design does.
