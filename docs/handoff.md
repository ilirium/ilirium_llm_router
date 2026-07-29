# Handoff

Snapshot of where the work stands. Written 2026-07-27. This is a living file — update it in place
rather than adding new dated copies, and delete it once the project has enough code to speak for
itself.

It is deliberately thin. The design lives in `CLAUDE.md`, which is loaded automatically every
session; the phased plan lives in `implementation-plan.md`; the authentication procedure lives in
`anthropic-auth-check.md`; the decisions taken while writing the proxy live in `phase-1-notes.md`;
the procedure for testing the router against a real session lives in `testing-against-claude-code.md`;
the token-usage check that unblocked Phase 2 lives in `lmstudio-usage-check.md`. Read those for
substance. This file only records session state — where we stopped and what happens next.

## Where the project stands

**Phase 0 is complete** — uv project, validated config loading, the routing rule, a CLI with a
`--check` mode.

**Phase 1 is complete and proven in a real session on 2026-07-29.** `proxy.py` and `app.py` forward:
the `HEAD /` probe is answered locally, `POST /v1/messages` is dispatched on the model named in the
body, and a catch-all carries anything else to Anthropic. Bodies go out byte for byte, replies stream
back untouched. 54 tests pass, and Claude Code has run through the router against both backends —
`claude-sonnet-5` as a normal session, and `google/gemma-4-e4b` in LM Studio with working tool calls
and multi-turn. Full results in `testing-against-claude-code.md`.

`stats.py` and `logging_setup.py` are still stubs whose docstrings carry the constraints they must
satisfy. That is Phase 2, and it is the next thing to build.

## What we were doing when we stopped

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

**Two pieces of work are agreed and not yet written.** Neither has been started; both are decisions
recorded in `CLAUDE.md`, and the code still reflects the state before them.

*The credential config shape.* One `credential` field with three modes — `forward`, `strip`,
`inject` — replacing today's two independent knobs, in which a configured key silently overrides
whatever `credential` says. Contradictions become startup errors that name the fix and exit.
Decided because auth is going back on for LM Studio and because more backends are planned, which
makes the current ambiguity a trap rather than a wart. Full rationale under "Design decisions".

*Phase 2* — the log and the per-call CSV. The columns and the constraints are
already specified in `CLAUDE.md` under "Observability"; the notable ones are teeing the response
rather than parsing it, re-emitting the CSV header on rotation, and never letting a telemetry
failure break a call. It also answers a question Phase 1 left uncomfortable: right now nothing
records which backend a request took, so testing means reading LM Studio's own server log.

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

**Phases 2 to 4 are still intentions, not observed behaviour.** What is now fact: the "Observed
request shape" section of `CLAUDE.md`, the Result section of `anthropic-auth-check.md`, the two
Phase 1 findings above, and the session results in `testing-against-claude-code.md`. Everything
written about logging, statistics, error handling and LM Studio parity remains design intent that no
code has been checked against.

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
