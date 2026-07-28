# Handoff

Snapshot of where the work stands. Written 2026-07-27. This is a living file — update it in place
rather than adding new dated copies, and delete it once the project has enough code to speak for
itself.

It is deliberately thin. The design lives in `CLAUDE.md`, which is loaded automatically every
session; the phased plan lives in `implementation-plan.md`; the authentication procedure lives in
`anthropic-auth-check.md`. Read those for substance. This file only records session state — where we
stopped and what happens next.

## Where the project stands

**No code has been written.** The repository contains documentation only: `README.md`, `CLAUDE.md`,
and four files in `docs/`. There is no `pyproject.toml`, no source tree, and no tests. Phase 0 of
the plan has not started.

Most of what is decided came from reading vendor documentation and reasoning about the design. The
exception is the authentication question, which was settled empirically by capturing a real request
— see below.

## Git state

On branch `docs/add-claude-md`, five commits ahead of `origin/main`, nothing pushed:

- `5895359` initial CLAUDE.md
- `c9be81f` correction to CLAUDE.md
- `f7c71d4` design decisions and observability spec
- `1636024` implementation plan
- `93fda4f` authentication check procedure and handoff notes

The branch is documentation-only under a name that suggests docs, and is about to grow code.
Consider merging it to `main` and starting implementation on a fresh branch.

## What we were doing when we stopped

The authentication question is **answered**. Test A and Test B were run on 2026-07-28 and the
captured request is saved as `log-the-whole-request.txt`. Claude Code sends an OAuth subscription
token as a bearer credential, and Anthropic accepts it as forwarded — so the router holds no key of
its own and the rule is *forward for cloud, strip for local*. Test B's 429 was initially read as a
failure; it is not, because a 429 is only returned after authentication has succeeded.

The capture also produced several concrete facts that were previously guesses — a `HEAD /` startup
probe, a query string on the messages path, body fields outside the base API, and prompt-cache
markers that make byte-relay a correctness requirement rather than a preference. These are recorded
in `CLAUDE.md` under "Observed request shape" and folded into the plan.

**The next step is Phase 0** — the project skeleton. Nothing blocks it.

One loose end: re-run the Test B curl showing its response body, to confirm the 429 was an ordinary
subscription rate limit rather than something unexpected. The command is in `anthropic-auth-check.md`.
This does not block Phase 0.

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

**The documentation describes intentions, not observed behaviour** — with one exception. The
"Observed request shape" section of `CLAUDE.md` and the Result section of `anthropic-auth-check.md`
come from a real captured request and are facts. Everything else about how the router will behave is
still design intent, unvalidated until code exists to check it against.

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
