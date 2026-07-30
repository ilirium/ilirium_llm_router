# Handoff

Snapshot of where the work stands. Written 2026-07-27. This is a living file — update it in place
rather than adding new dated copies, and delete it once the project has enough code to speak for
itself.

It is deliberately thin. The design lives in `CLAUDE.md`, which is loaded automatically every
session; the phased plan lives in `implementation-plan.md`; the authentication procedure lives in
`anthropic-auth-check.md`; the decisions taken while writing the proxy live in `phase-1-notes.md`; the plan for Phase 2 and
the fourteen decisions taken building it live in `phase-2-notes.md`;
the procedure for testing the router against a real session lives in `testing-against-claude-code.md`;
the token-usage check that unblocked Phase 2 lives in `lmstudio-usage-check.md`; proposals that are
written up but not decided live in `EPD-NNN-*.md`. Read those for substance. This file only records
session state — where we stopped and what happens next.

## Where the project stands

**Phase 0 is complete** — uv project, validated config loading, the routing rule, a CLI with a
`--check` mode.

**Phase 1 is complete and proven in a real session on 2026-07-29.** `proxy.py` and `app.py` forward:
the `HEAD /` probe is answered locally, `POST /v1/messages` is dispatched on the model named in the
body, and a catch-all carries anything else to Anthropic. Bodies go out byte for byte, replies stream
back untouched. Claude Code has run through the router against both backends — `claude-sonnet-5` as a
normal session, and `google/gemma-4-e4b` in LM Studio with working tool calls and multi-turn. Full
results in `testing-against-claude-code.md`.

**Phase 2 is built, steps 1–5 of six.** On `feat/phase-2-observability`, five commits, 137 tests.
`logging_setup.py`, `stats.py` and the new `observe.py` are written; `proxy.py` tees the reply past a
scanner on its way downstream. Decisions taken while building are numbered 4–14 in
`phase-2-notes.md`. **Step 6 — a real Claude Code session, then read the CSV — has not been run**,
and it is the next thing to do.

## What we were doing when we stopped

Phase 2 steps 1 through 5, finishing 2026-07-30 with a clean tree. Step 1 was found already written
from an earlier session that was closed accidentally, and its tests were written afterwards — which
promptly turned up two defects in it. Both are the kind that never raise: a `datefmt` was discarding
the milliseconds from the log's own timestamps, in the phase whose subject is `ttfb_ms` and
`duration_ms`; and an unusable log path crashed with a traceback instead of the readable
`ConfigError` every other startup problem produces.

The pattern repeated in every later step, and is worth carrying forward: **each step's real findings
came from writing its tests, not from writing its code.** Step 3's SSE scanner never read a final
`data:` line that arrived without a trailing newline — and the line held back is the last one, where
`output_tokens` and `stop_reason` live, so it would have looked like a healthy stream reporting its
two most interesting numbers as empty. Step 5 found that `proxy.py`'s *second* `httpx.HTTPError`
branch — the connection that breaks mid-relay, after the 200 has gone out — had no test at all.

Two traps were in the test scaffolding rather than the code. A streamed `httpx.Response` can only be
consumed once, so the shared stand-in backend works for every single-call test and fails on the
second. And a mock backend answers instantly, so the first version of the concurrency test passed
without ever putting two writes near each other; it now holds each reply open 20 ms between chunks.

**One piece of work remains agreed and not yet written.**

*The credential config shape.* One `credential` field with three modes — `forward`, `strip`,
`inject` — replacing today's two independent knobs, in which a configured key silently overrides
whatever `credential` says. Contradictions become startup errors that name the fix and exit.
Decided because auth is going back on for LM Studio and because more backends are planned, which
makes the current ambiguity a trap rather than a wart. Full rationale under "Design decisions".
Deliberately *not* part of Phase 2.

## What Phase 2 still has to prove

Everything below is implemented and unit-tested; none of it has met a real session.

- **Does `x-claude-code-agent-id` actually arrive?** The router demonstrably copies it — verified
  against a live server with the header set by hand — but no real subagent has been observed sending
  one. Until then an empty `agent_id` cannot be trusted to mean "main conversation".
- **Does `client_disconnect` happen the way the unit test says?** Its branch is proven by driving the
  generator and calling `aclose()`, because `TestClient` always reads a reply to the end and can
  never be the caller that stops listening. Whether starlette reliably lands there on a real dropped
  connection is unknown.
- **Do Anthropic's streamed replies scan the way LM Studio's do?** `lmstudio-usage-check.md` measured
  LM Studio directly; Anthropic's shape came from its documentation. The scanner takes
  `input_tokens` only from `message_start` precisely because the two backends differ there, so a
  cloud call is what confirms the rule rather than the assumption.
- **Does anything unexpected reach the catch-all?** The `path` column exists to turn that standing
  worry into a list of facts, and a real session is what populates it.

## Findings from Phase 1, kept for the record

Phase 1 was implemented against the constraints already written in `proxy.py`'s docstring. Two
things came out of running it that were not known from documentation:

**LM Studio has "Require Authentication" switched on here** — since turned off by hand, but intended
to go back on. A forwarded local request came back `401 authentication_error` from LM Studio itself.
This settles the Phase 0 question of whether `api_key_env` was speculative and should be removed: it
is needed, and backend authentication is now a design decision in `CLAUDE.md` rather than an
untested extra.

**The backend's `date` and `server` headers must not be relayed.** uvicorn writes its own, so
passing the backend's through gave the client two of each, which the HTTP spec forbids. Found by
reading the headers off a real reply, not by reasoning; the drop list in `proxy.py` now covers them.

Phase 1 was then verified end to end, which is where the project now stands. The one surprise from
that session: the local model ran at 34304 tokens of context — barely above the ~30k fixed preamble
measured from the captured request — and worked anyway. Either that estimate is pessimistic or
something trims context quietly; Phase 4 should find out, because silent truncation degrades answers
without failing.

## An open proposal

**Written and deliberately not decided.**
`EPD-001-model-selection-and-mixed-model-sessions.md`, written 2026-07-30, covers two requirements
that turned out to be absent from the specs: choosing a local model with `/model` mid-session, and
running subagents on local models alongside a Claude main conversation. Per-request dispatch already
satisfies the second with no code, and `/model <local-id>` should already work, so nothing here is
blocking. The decision waits until Phase 4, because a picker full of local models is worth nothing
until Phase 4 shows a local model can hold a real session. Do not treat that document as agreed
design; most of it is vendor documentation that has never been run against this router.

One piece of it *was* accepted the same day: the CSV gains `session_id` and `agent_id`, copied from
the `x-claude-code-*` request headers, and Phase 2 now writes them. The agent header is what
distinguishes a subagent's call from the main conversation's, and it is nearly free to include now.
Note the asymmetry in evidence — the session header appears in the captured request, the agent header
is documented only, so confirm it arrives rather than assuming an empty column means "main
conversation".

One loose end, carried over and still not blocking: re-run the Test B curl showing its response body,
to confirm the 429 was an ordinary subscription rate limit rather than something unexpected. The
command is in `anthropic-auth-check.md`.

## About `log-the-whole-request.txt`

A real captured request, kept as the evidence behind the "Observed request shape" notes. 120 KB,
nearly all of it a single line — read it with `jq` rather than opening it whole.

It has been redacted and is safe to commit. Replaced with `REDACTED-*` placeholders: the Anthropic
token, `account_uuid`, `device_id`, and `session_id` (which appeared both in the body and in an
`X-Claude-Code-Session-Id` header), plus the owner's email address where the system prompt carried it.
The JSON body still parses, including the nested `metadata.user_id` string.

Left in deliberately: `/Users/ilirium` paths, since the username is already throughout the repository
and git history, and stripping it would make the capture harder to read for no gain.

If a further capture is ever taken, redact the same set before committing it.

## Caveats worth carrying forward

**Phase 2 is written and unit-tested; Phases 3 and 4 remain intentions.** What is now fact: the
"Observed request shape" section of `CLAUDE.md`, the Result section of `anthropic-auth-check.md`, the
two Phase 1 findings above, the session results in `testing-against-claude-code.md`, and — for Phase
2 — the numbers checked against a live LM Studio on 2026-07-30. What is *not* yet fact is Phase 2
against a real session: see "What Phase 2 still has to prove" above, which is precisely the list step
6 exists to close. Everything written about error handling and LM Studio parity remains design intent
that no code has been checked against.

**LM Studio's parity is now partly measured rather than assumed, but only partly.** Tool calls
demonstrably survive the round trip — the 2026-07-29 session read and wrote files, ran bash commands
and ran a Python script — which was the biggest unknown. Token usage is reported too, in Anthropic's
exact shape, streaming and not (`lmstudio-usage-check.md`). LM Studio still publishes no
compatibility table, and these remain untested: a `role: "system"` message inside `messages`,
`thinking` blocks, and images. Do not assume passthrough is lossless before Phase 4.

**One claim in this repository was already wrong once.** The first version of `CLAUDE.md` asserted
that a protocol translation layer between the Anthropic and OpenAI formats was needed and was the
hard part of the project. That was incorrect — LM Studio speaks the Anthropic format natively — and
was corrected in `c9be81f` after the repository owner checked the vendor documentation. The lesson
worth carrying: verify vendor capabilities against their current documentation rather than assuming,
and prefer correcting the record openly over quietly rewriting it.
