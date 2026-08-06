# Handoff

Snapshot of where the work stands. Written 2026-07-27. This is a living file — update it in place
rather than adding new dated copies, and delete it once the project has enough code to speak for
itself.

It is deliberately thin. The design lives in `CLAUDE.md`, which is loaded automatically every
session; the phased plan lives in `implementation-plan.md`; the authentication procedure lives in
`anthropic-auth-check.md`; the decisions taken while writing the proxy live in `phase-1-notes.md`; the plan for Phase 2 and
the fourteen decisions taken building it live in `phase-2-notes.md`; what Phase 3 turned out to be —
mostly already built — lives in `phase-3-notes.md`, with the backend that fails on purpose, and the
commands that drive it, in `phase-3-verification/`; what LM Studio turned out to support lives in
`phase-4-notes.md`, planned in `phase-4-plan.md` and measured with the probes in `phase-4-probes/`,
which are committed and meant to be re-run;
the procedure for testing the router against a real session lives in `testing-against-claude-code.md`;
the token-usage check that unblocked Phase 2 lives in `lmstudio-usage-check.md`; proposals that are
written up but not decided live in `docs/epd/`, indexed by `EPD-000-about-these-documents.md`, which
also says what an EPD is and what the conventions are. Read those for substance. This file only
records session state — where we stopped and what happens next.

## Where the project stands

**Phase 0 is complete** — uv project, validated config loading, the routing rule, a CLI with a
`--check` mode.

**Phase 1 is complete and proven in a real session on 2026-07-29.** `proxy.py` and `app.py` forward:
the `HEAD /` probe is answered locally, `POST /v1/messages` is dispatched on the model named in the
body, and a catch-all carries anything else to Anthropic. Bodies go out byte for byte, replies stream
back untouched. Claude Code has run through the router against both backends — `claude-sonnet-5` as a
normal session, and `google/gemma-4-e4b` in LM Studio with working tool calls and multi-turn. Full
results in `testing-against-claude-code.md`.

**Phase 2 is complete and proven in a real session on 2026-07-31.** On `feat/phase-2-observability`,
139 tests. `logging_setup.py`, `stats.py` and `observe.py` are written; `proxy.py` tees the reply past
a scanner on its way downstream. Decisions taken while building are numbered 4–14 in
`phase-2-notes.md`. Step 6 ran, answered all four questions the phase existed to settle, and turned up
four recorder defects that have since been fixed. The session is frozen in `phase-2-step-6-session/`.

**The branch was merged into `main` on 2026-07-31** as `4d7d7f6`, `--no-ff` by convention so the
phase boundary stays visible in the history. Nothing from Phase 2 is outstanding.

**Phase 3 is complete and verified on 2026-07-31, merged to `main` as `cc65aed`.** 147 tests. Its central finding: **four of its five items were already built by Phase 2**,
which was specified as observability and delivered most of the error handling as a by-product of
needing an `error_status` column. The work was finding what that left — four gaps, all closed — and
measuring the phase's "Done when" against a live server and a real Claude Code session. Details in
`phase-3-notes.md`.

**Phase 4 is complete and measured on 2026-08-06, on `feat/phase-4-lmstudio-parity`, not yet
merged.** Against `qwen/qwen3.5-9b` at 44544 tokens. **Nothing was rejected** — every shape the plan
named was accepted, including the system-role message `CLAUDE.md` predicted was unsupported, and the
whole captured 118 KB request replays unmodified. Findings in `phase-4-notes.md`, instrument in
`phase-4-probes/`, which is committed and meant to be re-run.

## What we were doing when we stopped

**Phase 4, 2026-08-06.** The probes are written and run, the findings written up, `CLAUDE.md` and
`implementation-plan.md` updated, and both EPDs carry Phase 4 addenda. What remains is the `--no-ff`
merge.

Three results worth carrying beyond the parity table:

**Prompt caching stopped being an argument and became a number.** The captured request replayed
twice gave `cache_read_input_tokens` of **27904 out of 27924**, and time to first byte fell from
196789 ms to 49629 ms. `CLAUDE.md` has always called caching the strongest practical reason to relay
bytes untouched; that is now measured end to end rather than reasoned about.

**Silent truncation does not happen** — the worry standing since Phase 1 is retired. An over-window
request is refused in 908 ms with a message naming the cause and both fixes. But it arrives as an SSE
`error` event inside an HTTP 200, which is the shape Phase 3 measured Claude Code ignoring, so the
most useful message LM Studio produces may never be seen. That specific case is *not* measured: Phase
3's event followed partial content, this one is the sole event in the stream.

**The router's 600 s read timeout is reachable by ordinary traffic**, and this is the phase's one
real defect. A ~41000-token request against a 44544-token window was killed at exactly `read=600.0`
while LM Studio was still healthily prefilling — so **the usable context of a local model is bounded
by time, not by its window**. Deliberately not fixed: the same number is what makes a wedged backend
fail in bounded time and Phase 3 chose it on purpose. It belongs to the next phase, alongside the
credential work, with three options — a larger timeout, a configurable one, or one that resets on
progress rather than on first byte.

Two process notes. **A third of the phase was already measured** by Phase 2's frozen session, and
reading `phase-2-step-6-session/calls.csv` before running anything deleted a whole step and one probe
from the plan — the second phase running to find its work partly done. And **`lms load -c 8192` is
silently ignored**; LM Studio's saved per-model config beats the CLI, so a specific context length
needs a person in the GUI. The boundary was measured at the real 44544 instead.

### Earlier: Phase 3

**Phase 3, 2026-07-31, merged to `main` as `cc65aed`.** The
dead-backend path is measured in a real session: Claude Code shows the router's own wording and
**retries the 502 ten times with backoff**, so a session heals itself if LM Studio comes back — and
one turn becomes up to ten `transport_error` rows. The display truncates the message from the right,
which makes the order of that string a constraint rather than a preference.

The other failure — **a backend that dies while answering** — was measured too, and the answer is
the phase's most useful one: **Claude Code ignores the injected SSE `error` event.** It reports
`empty or malformed response (HTTP 200)`, its own wording, where on a 502 it prints the router's
message verbatim. So it never recognised the event; it is reporting the missing `message_stop`.

The event was **kept anyway**, decided 2026-07-31 — Anthropic's documented shape, fifteen lines, one
test, and other harnesses are planned. `CLAUDE.md` records it as a feature with **no measured
consumer**, so nobody later mistakes it for something that solved a visible problem. If a second
client also ignores it, delete it.

The phase's "Done when" is met in full, and the `--no-ff` merge landed as `cc65aed`.

**`make format` is now safe to run**, which it was not when this phase started. `pyproject.toml` set
no ruff line length, so the formatter used its default 88 columns against a codebase written at 100
and rewrote every file it was pointed at — while `make lint` passed either way, because line length
is `E501` and that is not in ruff's default rule set. Now `line-length = 100`, applied to the whole
repository in one commit of its own, verified by comparing every file's AST before and after: 18 of
19 identical, and the 19th a docstring that began with a quote character and gained a space. Details
in `phase-3-notes.md`.

**ruff is now pinned as well**, `RUFF ?= ruff@0.16.1` in the Makefile, which closes the other half:
an unpinned formatter reformats the repository the day it changes its mind, and the bump arrives
disguised as somebody's feature branch. It is still fetched on demand rather than made a project
dependency — the pin is what was missing, not the dependency. `make format RUFF=ruff@x.y.z` tries a
version without committing to it. Checked at the time: 0.16.0 and 0.16.1 both leave the repository
untouched, so the current formatting is not balanced on one patch release.

### Earlier: Phase 2 step 6

**Finishing 2026-07-31 with a clean tree.** The session was run, the CSV and log read,
`EPD-002` written out of what the `path` column exposed, the session frozen into `docs/` because
`logs/` is gitignored, the four recorder defects fixed, and the Phase 1 429 loose end answered from
rows the session already had. Six commits, then the `--no-ff` merge to `main`.

Two process notes from it. The analysis was worth more than the run: three of the four defects were
invisible in the passing tests and only showed up when reading 142 real rows next to each other.
And **committing the artefact needed checking, not trusting** — `git add` on the frozen directory
silently skipped `router.log` because `.gitignore` carries a blanket `*.log`, so the first version of
that commit shipped a document citing a file that was not in the repository.

### Earlier: Phase 2 steps 1 through 5

Finished 2026-07-30 with a clean tree. Step 1 was found already written
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

## What Phase 2 had to prove — all four answered

The step 6 session on 2026-07-31: long, switching models mid-conversation, subagents, an interrupted
response, tool use and file editing on a local model. 142 rows across eleven client sessions, frozen
in `phase-2-step-6-session/`.

- **Does `x-claude-code-agent-id` actually arrive?** **Yes.** Seven rows carry one agent ID, covering
  both the subagent's own background calls and its main call — so the column separates a subagent's
  whole footprint, not just its headline request. An empty `agent_id` can be read as "main
  conversation".
- **Does `client_disconnect` happen the way the unit test says?** **Yes.** Six rows, on both
  backends. Two shapes: some captured partial usage before the drop (`message_start` arrived,
  `message_delta` never did), some captured nothing.
- **Do Anthropic's streamed replies scan the way LM Studio's do?** **Yes.** Thirty-two streamed
  Anthropic rows with every token column populated. Their `input_tokens` of 2 alongside large
  `cache_read` values is the `message_start`-only rule earning itself — a scanner keyed on
  `message_delta` would have looked fine locally and been wrong here.
- **Does anything unexpected reach the catch-all?** **Yes** — `/v1/messages/count_tokens`, 33 rows.
  LM Studio does not implement it and answers HTTP 200 with an error body, so the rows read `ok`.
  That became `docs/epd/EPD-002-token-counting-for-local-backends.md`.

Four recorder defects surfaced alongside, all fixed: `stream` written blank where Claude Code omits
the field, the log and CSV timestamping on different clocks, the backend's symbolic `error.type`
being discarded, and completion-ordered rows going undocumented.

One finding that is not a defect and has no owner yet: **Claude Code's prompt-cache warmup probes
cost 44% of local wall-clock time** in that session — 40 calls returning zero content tokens, 20.0 of
45.5 minutes. Recorded under "No special case for background/auxiliary traffic" in `CLAUDE.md`,
because it is an argument against that decision rather than a bug in this one.

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

## Open proposals

All indexed in `docs/epd/EPD-000-about-these-documents.md`, which is also where "EPD" is expanded
(Enhancement Proposal Document) and where the conventions all three follow are written down. Read it
first if you have not seen one of these before.

**Written and deliberately not decided.**
`docs/epd/EPD-001-model-selection-and-mixed-model-sessions.md`, written 2026-07-30, covers two requirements
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

**Also written and deliberately not decided.**
`docs/epd/EPD-002-token-counting-for-local-backends.md`, written 2026-07-31 out of the Phase 2 step 6 session.
LM Studio does not implement `POST /v1/messages/count_tokens` and answers it with **HTTP 200 and an
error body**, so all 32 such rows in `calls.csv` are logged `ok`. Claude Code falls back to its own
estimator — `/context` still displays plausible numbers, labelled "Estimated" — but against an
assumed **200k** window rather than the model's real context length, which it has no way to learn.
On `qwen/qwen3.5-9b` at 262144 that is harmlessly conservative. On a sub-200k model it is not: a
34304-token `google/gemma-4-e4b` would show 41% for a conversation at 238% of its window, and
auto-compaction would fire far too late. That is the concrete mechanism behind the Phase 4 silent-
trimming worry. The document also settles that raw `request_bytes` cannot predict token counts
(6× ratio spread, 410% worst-case error) and leaves one hypothesis untested — that *content* bytes
can. Do not build anything from it: the fork between an honest count and a scaled one is open, and
question 3 in that file may make the fork moot.

Nothing there is blocking. The router forwards `count_tokens` correctly today and every session in
`calls.csv` completed.

**Newest, and the only one not waiting on Phase 4.**
`docs/epd/EPD-003-capturing-bodies-for-a-corpus.md`, written 2026-07-31 in answer to a requirement raised the
same day: store every request and response body for later analysis, and possibly as a fine-tuning
corpus. Two findings drive it. **The corpus is ~93% request bytes and those are almost entirely
repeats** — every turn re-sends the whole conversation, so storage is O(N²) in turns where the
transcript is O(N); the step 6 session would have produced 10.35 MB in 77 minutes. And **the storage
question is a compression-window question, not a database question**: measured on the real captured
request grown across twenty turns, gzip manages 2.4× where zstd manages 28.6×, while on a *single*
body the two are tied at 2.9× and 3.1×. The whole gap is gzip's 32 KB window failing to see the
previous request's copy of the same preamble.

What it waits on is not a phase but a decision: **Anthropic's terms prohibit using outputs as
training targets**, so the fine-tuning half of the requirement may not survive, while the analysis
half is untouched. That answer changes the design rather than its priority, which is why it is
question 1 in that file.

Note it also reverses one sentence of `CLAUDE.md` on purpose — the one ruling out anything
body-shaped — and says so explicitly. The narrow form it argues for is *store bytes, parse never*.
Nothing is implemented, and its own gate is a twenty-minute measurement: whether a trained zstd
dictionary recovers the cross-body ratio for per-file storage. If it does not, per-call files are the
wrong unit and the sketch in that document does not survive.

The loose end carried here since Phase 1 — whether Test B's 429 was an ordinary subscription rate
limit — is **mostly closed as of 2026-07-31**, and closing the rest needs no action.

The step 6 session produced eight more Anthropic 429s. Their `error.type` was `rate_limit_error`:
established by reconstruction rather than read directly, but pinned by the 429 status, a 114-byte
body that only a 16-character type name can produce, and a recorded `error_message` of the literal
word `Error`. A 429 at 08:34:32 followed by a 200 five seconds later corroborates it — a rejected
credential does not recover in five seconds. Claude Code retried all eight successfully.

Still unverified: the `anthropic-ratelimit-*` and `retry-after` headers, which the router never
records — it tees response bodies, not headers. Only the Test B curl can settle that, and it needs
the token.

**Do not go looking.** The recorder now keeps the body's symbolic type, so the next 429 through the
router writes `rate_limit_error: Error` into the CSV by itself — measured rather than reconstructed.
The reasoning and the numbers are in `anthropic-auth-check.md`.

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

**Phase 4 is now measured too, on 2026-08-06** — see `phase-4-notes.md` for what LM Studio supports
and, more usefully, the four things that remain open at the end of it. What is now fact: the
"Observed request shape" section of `CLAUDE.md`, the Result section of `anthropic-auth-check.md`, the
two Phase 1 findings above, the session results in `testing-against-claude-code.md`, and — for Phase
2 — the numbers checked against a live LM Studio on 2026-07-30, and the step 6 session that closed
all four of its open questions. For Phase 3, fact means the live-server run in `phase-3-notes.md`:
a dead backend, a stream cut off mid-answer and a caller that hung up, each producing the row it
should. What is *not* fact is the half that needs a person watching: whether Claude Code renders
either error usefully. LM Studio parity beyond tool calls and usage remains design intent that no
code has been checked against — that is Phase 4.

**LM Studio's parity is measured, and it is better than this file assumed for months.** Tool calls,
tool results, token usage, `thinking` blocks, images, a `role: "system"` message inside `messages`,
and the whole captured 118 KB request all work — **nothing sent in Phase 4 was rejected**. The
sentence this paragraph used to end with, warning not to assume passthrough is lossless, was right to
be cautious and turned out to be pessimistic.

Two caveats replace it. The gaps that exist are **quiet rather than loud** — `thinking.budget_tokens`
ignored, `output_config.effort` billing reasoning it never emits — and a quiet gap is harder to
notice than a rejection. And **all of it is one model**, `qwen/qwen3.5-9b`; `capabilities` varies per
model in `GET /api/v1/models`, so none of it transfers without re-running `phase-4-probes/`.

**One claim in this repository was already wrong once.** The first version of `CLAUDE.md` asserted
that a protocol translation layer between the Anthropic and OpenAI formats was needed and was the
hard part of the project. That was incorrect — LM Studio speaks the Anthropic format natively — and
was corrected in `c9be81f` after the repository owner checked the vendor documentation. The lesson
worth carrying: verify vendor capabilities against their current documentation rather than assuming,
and prefer correcting the record openly over quietly rewriting it.
