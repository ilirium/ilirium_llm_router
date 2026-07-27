# Implementation plan

## What we are building

A small web service that sits between Claude Code and two model backends. Claude Code is
configured to talk to this service instead of talking to Anthropic directly. For each request the
service looks at which model was asked for, decides whether that model lives at Anthropic or in
LM Studio on this machine, and forwards the request there. It records what happened for every call.

The reason it exists: Claude Code accepts only one server address. Without something in the middle
you must choose between the cloud models and the local ones. With it, both are available at the
same time, chosen per request just by naming a model.

The design decisions this plan builds on are in `CLAUDE.md`. The short version: forward requests
byte for byte rather than rebuilding them, decide routing with a simple name rule rather than a
config table, and never let the logging get in the way of a request.

---

## Phase 0 — Project skeleton

**Goal.** A project that starts up, reads its configuration, and does nothing else. No request
handling yet.

**Work.**

- Create the `uv` project and add the dependencies: FastAPI, an ASGI server, an async HTTP client,
  a YAML parser, and something to read `.env`.
- Decide the folder layout and create empty modules for the pieces we know we need: configuration,
  routing, the proxy itself, and the statistics recorder.
- Write the configuration file format and a loader for it. The loader validates the file at
  startup and stops the program with a readable message if something is missing or malformed.
  Failing loudly at startup is much better than failing on the first request.
- Read secrets from `.env` rather than the YAML file, so the config file stays safe to commit.
- Add `logs/` and `.env` to `.gitignore`.

**Done when.** The service starts, prints the configuration it loaded and which backends it knows
about, and exits cleanly with a clear error if the config file is wrong.

---

## Phase 1 — The proxy itself (first milestone)

**Goal.** Claude Code can be pointed at this service and work normally against both a cloud model
and a local model. This is the milestone that proves the whole idea.

**Work.**

- Accept `POST /v1/messages` and read the raw request body.
- Look inside the body just far enough to find the model name. Do not deserialize the whole thing.
  If there is no model name, reject with a clear error.
- Apply the routing rule: a model name beginning with `claude-` goes to Anthropic, anything else
  goes to LM Studio.
- Rebuild the outgoing headers. This is the fiddly part and is described below under "Things that
  are easy to get wrong".
- Send the request onward with the body unchanged, and stream the reply back to Claude Code as it
  arrives, without reassembling or re-encoding it.
- Handle both streaming and non-streaming requests, since Claude Code uses both.
- Add a catch-all route that forwards any other path we were not expecting to the same backend
  logic, so an unanticipated endpoint does not simply fail.

**Done when.** With the service running, `claude --model claude-sonnet-5` and
`claude --model <some-local-model>` both work in a real session: replies stream smoothly, tools
work, and a multi-turn conversation holds together.

---

## Phase 2 — Logging and per-call statistics

**Goal.** Every call leaves two traces: a human-readable line in a log file, and a row in a CSV
file that can be opened in a spreadsheet and compared across models.

**Work.**

- Log each call with the time, the model, the chosen backend, the outcome and how long it took.
- Write one CSV row per call with the columns listed in `CLAUDE.md`: timestamp, backend, model,
  input tokens, output tokens, request size in bytes, duration, whether it failed, and if so the
  error code and a short description.
- Get the token counts by watching the reply as it passes through, rather than by taking it apart.
  The reply carries a usage report; we read a copy of the bytes on their way past and pick the
  numbers out of it. The bytes going to Claude Code are untouched.
- If the usage numbers cannot be found, leave those columns empty and still write the row. The raw
  request size is always available, so a row is never useless.
- Rotate both files when they grow past the size set in the configuration. When the CSV rotates,
  write the header row again at the top of the new file, otherwise the older files cannot be opened
  on their own.
- Wrap all of this so that any failure while logging is caught and discarded. A full disk must not
  break a conversation.

**Done when.** A short session produces a readable log and a CSV whose rows match what actually
happened, and both files roll over correctly when the configured size is exceeded.

---

## Phase 3 — Behaving well when things go wrong

**Goal.** Failures are understandable from the client side and are recorded accurately.

**Work.**

- Handle LM Studio not running. This is the most common failure and today it would surface as an
  unhelpful crash. Catch the connection failure, record it with its own error code, and reply with
  an error in the shape Anthropic uses so Claude Code displays something sensible.
- Set sensible timeouts. Model replies can take minutes, so the normal short defaults would cut
  requests off. Keep the connection timeout short but allow reading to take a long time.
- Notice failures that arrive in the middle of a streamed reply. A streamed response reports success
  before any content exists, so an error can arrive afterwards. Watch the passing bytes for it
  instead of trusting the initial status.
- Handle Claude Code disconnecting halfway through. Close the upstream connection and record the
  call as incomplete rather than silently losing it.
- Pass through backend error responses unchanged, so a real Anthropic error message reaches the user
  intact rather than being replaced by one of ours.

**Done when.** Stopping LM Studio mid-session produces a clear message in Claude Code and a correct
CSV row, and no failure mode leaves the service wedged.

---

## Phase 4 — Checking what LM Studio actually supports

**Goal.** Find out where the local backend falls short, and write it down.

This phase is deliberately separate because it cannot be answered by reading documentation. LM Studio
publishes no compatibility table, so the only way to know is to send real traffic and observe.

**Work.**

- Run a real session against a local model that exercises the awkward parts: a system prompt, tool
  calls and their results, thinking blocks, and an image.
- Check whether the local backend reports usage numbers at all, since half the statistics depend on
  it.
- Record the findings in `CLAUDE.md`, including anything that does not work.
- Only if something is genuinely broken, consider a small targeted fix for that specific gap. Do not
  build a general translation layer; that was ruled out for good reason.

**Done when.** There is an honest written list of what works locally and what does not.

---

## Things that are easy to get wrong

These cut across phases and are worth getting right the first time.

**Headers.** The incoming request carries a placeholder credential meant for us, not for the real
backend. Replace it: the real key for Anthropic, whatever LM Studio expects locally. Also drop the
headers that describe the old connection, such as the host and the content length, and let the HTTP
client set fresh ones. If these leak through, requests fail in confusing ways.

**Compression.** If we allow the backend to compress its reply, we cannot read the usage numbers out
of the passing bytes without decompressing first. Ask for an uncompressed reply. The traffic is local
or already fast, so nothing is lost.

**Do not buffer the whole reply.** Watching bytes go past must not mean collecting them all in
memory. Keep only a small working buffer, take the numbers out as they appear, and discard the rest.

**Measuring duration.** Time the call until the reply has finished arriving, not until the first byte.
Recording time to first byte as well is cheap and is arguably the more interesting number when
comparing a local model against a cloud one.

**Rotation and CSV headers.** Rotation renames files behind the writer's back. The new file starts
empty and needs its header row written before the first data row.

**Writing from many requests at once.** Several calls can finish at the same moment and try to write
a row together. Make sure rows cannot interleave into corrupted lines.

---

## Risks and open questions

**How Claude Code authenticates to Anthropic.** This is the biggest unknown and should be settled
before Phase 1 rather than during it, because it decides whether the router needs to hold an API key
at all. A subscription login sends an OAuth token rather than an API key; that token may still be
usable as-is, in which case the router can forward whatever arrives and keep no secret of its own. If
it is not usable, the cloud side needs a separate, separately billed API key. Either way the local
side is unaffected. See `anthropic-auth-check.md` for how to test this and what each outcome implies.

**Whether LM Studio reports usage.** If it does not, the token columns will be empty for every local
call and comparisons will have to lean on request size and timing instead. Phase 4 answers this.

**Other endpoints.** Claude Code may call endpoints we have not anticipated. The catch-all route in
Phase 1 is there to stop that being fatal, but if the local backend does not implement one of them,
some feature may quietly not work.

**The name rule is a guess about the future.** Routing on a `claude-` prefix is simple and needs no
maintenance, but it assumes no local model will ever be named that way. That is a safe bet today and
easy to revisit later.

---

## Not doing yet

Deliberately out of scope until the above works: a combined model list endpoint, support for other
harnesses, other cloud providers, other local runtimes, retries or failover between backends, and any
kind of caching. Each is easy to add later and each would make the first working version harder to
get right.
