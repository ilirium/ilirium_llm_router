# Handoff

Snapshot of where the work stands. Written 2026-07-27. This is a living file — update it in place
rather than adding new dated copies, and delete it once the project has enough code to speak for
itself.

It is deliberately thin. The design lives in `CLAUDE.md`, which is loaded automatically every
session; the phased plan lives in `implementation-plan.md`; the authentication procedure lives in
`anthropic-auth-check.md`; the decisions taken while writing the proxy live in `phase-1-notes.md`.
Read those for substance. This file only records session state — where we stopped and what happens
next.

## Where the project stands

**Phase 0 is complete** — uv project, validated config loading, the routing rule, a CLI with a
`--check` mode.

**Phase 1 is written and passes its tests, but its "done when" has not been met.** `proxy.py` and
`app.py` now forward: the `HEAD /` probe is answered locally, `POST /v1/messages` is dispatched on
the model named in the body, and a catch-all carries anything else to Anthropic. Bodies go out byte
for byte, replies stream back untouched. 54 tests pass.

What that does *not* include: a real `claude` session. The router has spoken to LM Studio but not to
Anthropic, and no conversation has been held through it. Until someone drives `claude` against it,
Phase 1 is unproven in the way that matters.

`stats.py` and `logging_setup.py` are still stubs whose docstrings carry the constraints they must
satisfy. That is Phase 2.

## What we were doing when we stopped

Phase 1 was implemented against the constraints already written in `proxy.py`'s docstring. Two
things came out of running it that were not known from documentation:

**LM Studio has "Require Authentication" switched on here.** A forwarded local request comes back
`401 authentication_error` from LM Studio itself. Local models will not work until that setting is
turned off or `lmstudio.api_key_env` is configured with the key in `.env`. This settles the Phase 0
question of whether `api_key_env` was speculative and should be removed — it is needed.

**The backend's `date` and `server` headers must not be relayed.** uvicorn writes its own, so
passing the backend's through gave the client two of each, which the HTTP spec forbids. Found by
reading the headers off a real reply, not by reasoning; the drop list in `proxy.py` now covers them.

**The next step is to verify Phase 1 for real:** point Claude Code at the router
(`ANTHROPIC_BASE_URL=http://127.0.0.1:8787`) and hold a conversation with a `claude-` model and with
a local one, checking that replies stream, tools work, and multi-turn holds together. Sort out the
LM Studio credential first or the local half cannot work at all. After that, Phase 2.

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

**Most of the documentation still describes intentions rather than observed behaviour.** The
exceptions — the parts that are facts — are the "Observed request shape" section of `CLAUDE.md`, the
Result section of `anthropic-auth-check.md`, and the two Phase 1 findings above. In particular, the
router has never sent a request to Anthropic. That the forwarded credential and beta header work
through the router is inference from the capture, not something anyone has watched happen.

**Claims about LM Studio come from its own documentation.** That it implements an Anthropic-compatible
`/v1/messages` is well supported. What is *not* known is how completely: LM Studio publishes no
compatibility table, so its handling of system prompts, tool results, thinking blocks, images, and
usage reporting is unverified. Phase 4 exists to find out. Do not assume passthrough is lossless
before then.

**One claim in this repository was already wrong once.** The first version of `CLAUDE.md` asserted
that a protocol translation layer between the Anthropic and OpenAI formats was needed and was the
hard part of the project. That was incorrect — LM Studio speaks the Anthropic format natively — and
was corrected in `c9be81f` after the repository owner checked the vendor documentation. The lesson
worth carrying: verify vendor capabilities against their current documentation rather than assuming,
and prefer correcting the record openly over quietly rewriting it.
