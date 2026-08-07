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

## Phase 0 — Project skeleton — **done**

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

## Phase 1 — The proxy itself (first milestone) — **done**

**Goal.** Claude Code can be pointed at this service and work normally against both a cloud model
and a local model. This is the milestone that proves the whole idea.

**Work.**

- Answer the startup probe. Before its first real call, Claude Code sends a bare `HEAD /` to the
  configured address to check something is there. Reply to it successfully. If this is missed, the
  router can look like a dead endpoint before it has handled a single request.
- Accept `POST /v1/messages` and read the raw request body. Note that the real path carries a query
  string, so forward the query along with the path rather than assuming a bare path.
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

**Met on 2026-07-29.** Claude Code ran through the router against both backends: `claude-sonnet-5`
behaved as a normal session, and `google/gemma-4-e4b` in LM Studio wrote and read files, ran bash
commands, and ran a Python script and read its stdout, with multi-turn conversation holding
together. Streaming was confirmed incrementally in a curl smoke test. The procedure and the full
results are in `testing-against-claude-code.md`.

Two things turned up on the way, both now recorded in `CLAUDE.md`: LM Studio has "Require
Authentication" switched on here, so local calls return 401 until its key is configured; and the
backend's `date` and `server` headers must not be relayed, since our own server writes them.

---

## Phase 2 — Logging and per-call statistics

**Goal.** Every call leaves two traces: a human-readable line in a log file, and a row in a CSV
file that can be opened in a spreadsheet and compared across models.

**Work.**

- Log each call with the time, the model, the chosen backend, the outcome and how long it took.
- Write one CSV row per call with the columns listed in `CLAUDE.md`: timestamp, session and agent
  identifiers, backend, model, request path, whether streaming was asked for, input tokens, output
  tokens, cached input tokens read and written, why the reply stopped, request and response sizes in
  bytes, time to first byte, total duration, how the call ended and — when it did not end well — the
  error code and a short description, and the router's own version.
- Copy the session and agent identifiers straight off the request headers. Both are free — a header
  lookup, no body parsing — and the agent one is the only thing that distinguishes a subagent's call
  from the main conversation's. That matters because the two are expected to run on *different*
  models, which is what `docs/epd/EPD-001-model-selection-and-mixed-model-sessions.md` is about; without the
  column such a session records as an indistinguishable pile of rows. Cheap to write while building
  the writer, tedious to retrofit into a working one.
- Get the token counts by watching the reply as it passes through, rather than by taking it apart.
  The reply carries a usage report; we read a copy of the bytes on their way past and pick the
  numbers out of it. The bytes going to Claude Code are untouched.
- If the usage numbers cannot be found, leave those columns empty and still write the row. The raw
  request and response sizes are always available, so a row is never useless — and recording whether
  streaming was asked for says which of the two extraction paths was the one that came up empty.
- Rotate both files when they grow past the size set in the configuration. When the CSV rotates,
  write the header row again at the top of the new file, otherwise the older files cannot be opened
  on their own.
- Wrap all of this so that any failure while logging is caught and discarded. A full disk must not
  break a conversation.

**Done when.** A short session produces a readable log and a CSV whose rows match what actually
happened, and both files roll over correctly when the configured size is exceeded.

---

## Phase 3 — Behaving well when things go wrong — **done**

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
  call as incomplete rather than silently losing it — `error_status: client_disconnect`, which is the
  case the old boolean could not express, since an abandoned call is neither a success nor a backend
  failure.
- Pass through backend error responses unchanged, so a real Anthropic error message reaches the user
  intact rather than being replaced by one of ours.

**Done when.** Stopping LM Studio mid-session produces a clear message in Claude Code and a correct
CSV row, and no failure mode leaves the service wedged.

**Met on 2026-07-31**, with a correction to the plan itself: **four of the five items above were
already written and tested**, because Phase 2 could not produce an `error_status` column without
them. Phase 3's real work was the four gaps that left, and the verification — a live server for a
dead backend, a stream cut off mid-answer and a caller that hung up, then a real Claude Code session
for what the user sees. Full write-up in `phase-3-notes.md`.

Two results not anticipated here. Claude Code **retries a 502 ten times with backoff**, so the
status the router chose to *describe* a failure also decides whether the session recovers from it.
And Claude Code **does not act on a mid-stream `error` event** — the one thing this phase added to
the response stream is not read by the only client it has.

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
- Test the specific things the captured request revealed, which are the likeliest places a local
  backend diverges:
  - a system-role message sitting *inside* the conversation rather than in the system field, which
    is a recent addition and almost certainly unsupported locally;
  - a long list of beta feature flags in the headers, none of which mean anything to LM Studio — the
    question is whether it ignores them quietly or objects;
  - body fields outside the base API, such as the context-management, output-effort and caching
    settings — again, ignored or rejected;
  - a system prompt and tool list far larger than a toy request, which is the realistic case rather
    than an edge case.
- Record the findings in `CLAUDE.md`, including anything that does not work.
- Only if something is genuinely broken, consider a small targeted fix for that specific gap. Do not
  build a general translation layer; that was ruled out for good reason.

**Done when.** There is an honest written list of what works locally and what does not.

**Met on 2026-08-06**, against `qwen/qwen3.5-9b` at 44544 tokens. The list is in `phase-4-notes.md`,
the instrument in `phase-4-probes/`, and the summary is that **nothing was rejected** — every awkward
shape this plan named was accepted, including the system-role message it expected to fail and the
whole captured request replayed unmodified. No targeted fix was needed, so none was made.

Three results the plan did not anticipate. **Prompt caching became a measurement** rather than a
rationale: the same request twice, `cache_read` 27904 of 27924, time to first byte cut four-fold.
**Silent truncation does not occur** — the boundary refuses cleanly — which retires a worry standing
since Phase 1, though the refusal arrives in the SSE `error` form Phase 3 found Claude Code ignoring.
And **the router's 600 s read timeout is reachable by an ordinary large request**, killing a healthy
call mid-prefill; recorded, deliberately not fixed here, and carried to the next phase.

A note on method, now true three phases running: **a third of this phase was already measured** by
Phase 2's frozen session, and reading it first deleted a step and a probe from the plan. Phase 3
found four of its five items already built. Check the committed artefacts before planning a run.

---

## Phase 5 — The credential shape and the read timeout

**Goal.** Close the two items that are unambiguously work rather than deliberation, both of which
touch configuration.

This phase is the mirror image of Phase 4: almost all of it is code, and none of it is a measurement
except the one that Phase 4 could not take. `outstanding-work.md` is the survey that picked these two
out of everything left; `phase-5-plan.md` is how they will be run.

**Work.**

- **Replace the two-knob credential configuration with one field and three modes** — `forward`,
  `strip`, `inject` — with `api_key_env` required by the last and forbidden by the others. Agreed
  2026-07-29 and never written. Today a configured key silently overrides whatever `credential` says,
  so `credential: forward` alongside a key does not forward. Contradictions become startup errors
  that name the fix and exit, matching the rest of config loading.
- **Exercise the `inject` path with a live request.** It has never carried one: LM Studio's
  authentication setting was switched off rather than configured around, so the mode that motivated
  this whole decision is covered by a unit test and nothing else.
- **Decide what to do about the 600-second read timeout**, which Phase 4 found reachable by ordinary
  traffic — a healthy local request killed mid-prefill, which means a local model's usable context is
  bounded by time rather than by its window. Start by measuring what httpx's `read` timeout actually
  applies to, because one of the three candidate fixes may already be the behaviour.
- **Verify the timeout change against the request that exposed it**, not against tests. Every one of
  the 147 tests passed with the broken number.
- Optionally, take the measurement this unblocks: whether context is trimmed *below* the boundary.
  The run meant to answer it in Phase 4 hit this timeout instead.

**Done when.** The credential shape cannot express a contradiction, `inject` has worked against a
real authenticated backend, and the timeout is either changed with its reasoning written down or
deliberately kept with the same. In both cases `CLAUDE.md` stops describing them as outstanding.

**Deliberately out of scope.** The per-backend authentication *header* name — `Authorization` versus
`x-api-key` versus `x-goog-api-key` — which is needed before the second cloud provider and not
before, and which this phase could easily settle by accident while editing the same function.

---

## Phase 6 — Reviewing the basement — **done 2026-08-07**

**Goal.** Read the whole thing at once, which nobody had done. Not a capability: the first phase
whose subject is the project itself.

Its reason was the shape of the three phases before it. Phase 3 found work already *built*, Phase 4
found work already *measured*, Phase 5 found work already *misdescribed* — a claim quoted forward
across four documents that had never been true. That last one is a failure only a re-reading catches.

**Work.** Read all of `src/` and `tests/`; audit every assertion of *built* / *fixed* / *verified* /
*measured* against the code, the frozen artefacts or the test suite; check for duplication, dead code
and bloat; run a type checker and an AST inventory; drive the router live against local stubs. The
EPDs were explicitly out of scope. Planned in `phase-6-plan.md`, findings and outcome in
`phase-6-notes.md`.

**What it found.** The documentation was almost entirely right — **fifteen of the sixteen quoted
measurements reproduce to the digit**, no dead code anywhere in `src/`, a type checker finding ten
diagnostics and none of them a defect. Seven items fixed, about forty lines: the 26× time-to-first-byte
gap quoted without the slice it means, an SSE scan cap that counted the arriving chunk rather than
one line, two undeclared direct dependencies, four identical copies of one test helper, one dead
line, a README with no instructions, and a double lookup.

**What it declined to do**, each measured first rather than argued: `ty` is not adopted, the 58%
comment density is kept (mean 2.8% wording overlap with `CLAUDE.md`, so it is not duplication),
`.gitignore` is not trimmed and no document is deleted.

**Its process lesson turns Phase 5's on the reviewer.** The plan asserted the comments were redundant
and a five-minute measurement refuted it; a finding overstated how many files carried the 26× claim,
written from memory of a grep rather than from the grep. Check the claim you are planning against,
including when it is your own.

---

## Things that are easy to get wrong

These cut across phases and are worth getting right the first time.

**Headers.** The credential arriving from Claude Code is the real one and works as-is against
Anthropic, so cloud-bound requests forward it unchanged. Local-bound requests have it removed, since
a real credential is of no use to LM Studio and should not be handed to something that might log it.
Forward for cloud, strip for local.

The `anthropic-beta` header must be forwarded verbatim to Anthropic. It is a long comma-separated
list, and one of its entries is what makes the bearer token acceptable — dropping or trimming it
turns a working request into an authentication failure.

Drop the headers that describe the old connection, such as the host and the content length, and let
the HTTP client set fresh ones. If these leak through, requests fail in confusing ways.

**Compression.** If we allow the backend to compress its reply, we cannot read the usage numbers out
of the passing bytes without decompressing first. Ask for an uncompressed reply. Claude Code asks for
several compression formats on the way in, so this has to be overridden deliberately rather than
merely not set. The traffic is local or already fast, so nothing is lost.

**Prompt caching.** The requests carry cache markers on the large, unchanging parts — the system
prompt and the tool list. Caching matches on the exact bytes of that prefix, so anything that
rewrites the body, even reordering keys while meaning the same thing, silently stops the cache from
matching and makes every call cost full price. This is the strongest practical reason to relay the
body untouched rather than parse and rebuild it.

**Do not buffer the whole reply.** Watching bytes go past must not mean collecting them all in
memory. Keep only a small working buffer, take the numbers out as they appear, and discard the rest.

**Measuring duration.** Time the call until the reply has finished arriving, not until the first byte.
Time to first byte is recorded as well, in its own column, and is arguably the more interesting number
when comparing a local model against a cloud one. Both clocks start when the request arrives, so the
two numbers read directly rather than needing subtraction. Until 2026-07-30 this paragraph asked for
time to first byte while the column list had nowhere to put it; that gap is now closed.

**Rotation and CSV headers.** Rotation renames files behind the writer's back. The new file starts
empty and needs its header row written before the first data row.

**Writing from many requests at once.** Several calls can finish at the same moment and try to write
a row together. Make sure rows cannot interleave into corrupted lines.

---

## Risks and open questions

**How Claude Code authenticates to Anthropic.** *Settled — this is no longer a risk.* It sends an
OAuth subscription token as a bearer credential, and that token is accepted by Anthropic when
forwarded the way Claude Code sends it. The router therefore holds no key of its own: it forwards the
credential on cloud-bound requests and strips it on local ones. Details and evidence in
`anthropic-auth-check.md`.

**Request fields we have not seen.** The one captured request already carried three body fields that
this plan did not anticipate, and a message role that is not part of the base API. More will appear
as Claude Code evolves. Nothing needs doing about it — that is precisely what relaying the body
untouched buys us — but it is worth remembering the next time parsing the body looks tempting.

**Whether LM Studio reports usage.** *Settled — it does.* Checked on 2026-07-29 ahead of Phase 2
rather than waiting for Phase 4, because the answer decided how much of the tee-and-scan machinery
was worth building. Usage arrives in Anthropic's exact shape in both streaming and non-streaming
replies, and survives the relay through the router. It reports `cache_read_input_tokens` as well,
which the CSV spec has no column for. Procedure and numbers in `lmstudio-usage-check.md`.

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
