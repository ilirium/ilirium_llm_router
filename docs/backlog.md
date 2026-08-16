# Backlog — unscheduled work

**Inventory, not state.** What is in flight and where the project stopped are in `status.md`; nothing
here says when anything happens. An item lands in `status.md`'s "What is next" when it is picked up,
and is deleted from here when it is done.

**Every item names why it is parked, and several name why the question is weaker than it looks.**
That column is the point of this file. An item that has lost its reason has become a to-do, and a
to-do nobody has justified in six months cannot be told apart from one nobody wants.

Started 2026-08-16 from the live items of `milestone-1-core/outstanding-work.md`, which stays in the
archive as the survey it was. Where an item is fully argued elsewhere this file **points rather than
restates** — three of the heaviest are EPDs, and copying their substance here would create the second
copy the documentation structure exists to prevent.

---

## Decisions waiting on a person

None of these is blocked on work. Each is blocked on somebody deciding, and each is argued in full in
`epd/`.

| | Blocked on | Why it may be weaker than it looks |
|---|---|---|
| `epd/EPD-001-model-selection-and-mixed-model-sessions.md` | **a decision only** | Its gate — that a local model can hold a real session — was discharged by Phase 4. Per-request dispatch already satisfies the subagent half with no code, and the `session_id`/`agent_id` columns were accepted separately |
| `epd/EPD-002-token-counting-for-local-backends.md` | **a decision, on a weakened case** | Phase 4 measured the harm it was organised around and found none: the context boundary refuses cleanly rather than trimming silently. Its addendum also records the proposal reading `max_context_length` where it needs the loaded `context_length` |
| `epd/EPD-003-capturing-bodies-for-a-corpus.md` | **a decision, plus its own gate** | The decision is whether the fine-tuning half survives Anthropic's terms. The gate is a twenty-minute measurement — whether a trained zstd dictionary recovers the cross-body compression ratio for per-file storage. If it does not, per-call files are the wrong unit and the sketch does not survive |

## Measurements left open

Carried from Phase 4's own honest list. Phase 6 graded the live-behaviour claims among these
**consistent with their committed transcripts but not re-measured**, which is the label they should
keep.

**Whether Claude Code shows LM Studio's context error.** It arrives as an SSE `error` event inside an
HTTP 200 — the shape Phase 3 measured being ignored — but as the *sole* event, with no `message_start`
before it, where Phase 3's case followed partial content. *Parked because* nobody has needed it.
*Weaker than it looks?* No — this is the strongest item in the list. It decides whether the most
actionable message LM Studio produces is ever seen by anyone.

**Non-streaming replies.** Every Phase 4 probe ran streamed. `procedures/lmstudio-capability-probes/probe.py`
already has `--no-stream` and it has never been used; the recorder takes a different path for
buffered replies and LM Studio reports `usage` differently there. *Parked because* Claude Code always
streams, so this is about the router's second code path rather than about live traffic.

**Other local models.** All of Phase 4 is `qwen/qwen3.5-9b`. `capabilities` in `GET /api/v1/models`
varies per model — several have no `vision`, several no `reasoning` — so nothing in the
honoured/ignored table transfers without re-running the probes. *Parked because* it is re-running an
existing instrument rather than building one, and expires with each LM Studio release anyway.

**Before planning any of these, grep the frozen artefacts first.** Phases 3, 4 and 5 each found a
third or more of their work already done, measured, or misdescribed. The limit is worth knowing too:
the router logs metadata and never bodies, so old rows prove *a request succeeded* and can never
prove *a request carrying a particular field succeeded* — which is exactly the gap `EPD-003` proposes
to close.

## Work with an owner-shaped decision behind it

**Prompt-cache warmup probes cost 44% of local wall-clock time.** 40 calls returning zero content
tokens, 20.0 of 45.6 minutes in the frozen step 6 session. *Parked because* it has no owner and is
not a bug: `reference/design-decisions.md` records it under "No special case for background or
auxiliary traffic" as an argument *against* that decision rather than a defect in it. Fixing it buys
back nearly half the local wall clock at the price of the first special case in the dispatch rule.
*Weaker than it looks?* The opposite — this is the largest measured cost in the project, and the
reason it is parked is that nobody has been willing to take the trade.

**The per-backend authentication header name.** `inject` means `Authorization: Bearer` today, which
suits LM Studio and OpenAI; Anthropic's native key is `x-api-key` and Gemini's is `x-goog-api-key`.
*Parked deliberately:* it is needed before the second cloud provider, not before. Phase 5 was told
explicitly not to settle it while editing the same function.

**A tracked `.claude/settings.json`.** `EPD-004` decision 17 splits the permission allowlist — a
tracked policy file, with the untracked local file left for machine accretions. *Parked because* only
half of it exists: the local file works, and nobody has written the tracked half. It is its own
branch. `README.md` currently describes the split and names it as not yet built.

**Extract the portable methodology.** `EPD-004` decision 18 defers this **with a trigger rather than
a date**: when project #2 starts, extraction is a copy of `docs/README.md` with the backend rows
deleted, plus `CLAUDE.md`'s rule block. *Parked because* a methodology extracted from n=1 is a guess
about what generalises. Do not build a `docs/method/` tier or a global `~/.claude/CLAUDE.md` before
then.

## Instruments and housekeeping

**Teach `procedures/link-check.py` the two citation forms it cannot see.** It resolves paths and
ignores everything else, so two forms this repository depends on go unchecked: **heading anchors**,
stripped at `link-check.py:93` although `README.md`'s naming table says findings are "linked by
anchor"; and **`file.py:N` line citations**, skipped by `is_candidate` for containing no `/`.
*Parked because* both classes were verified by hand and both passed — the 11 code citations in a
fresh-context review, the six section titles at commit 6 of the restructure — so this buys
repeatability rather than fixing a known defect, and the population is small enough to check by hand
again. From `EPD-004` decision 21, where the gap surfaced while rejecting a larger proposal.

**Close out the four `Branch:` lines that record intent instead of outcome.** Five exist across four
of the six phases, in inconsistent places, and only `phase-4-notes.md:7` records the merge commit.
The other four say "Merge back with `--no-ff`" — written before the merge and never updated. *Parked
because* it is a review-phase checklist item under `EPD-004` decision 14, not standalone work. It is
this repository's signature failure in miniature: a document recording intent and never closed out.

---

## Not on this list, and why

**The Anthropic 429 rate-limit headers.** `anthropic-ratelimit-*` and `retry-after` are never
recorded, because the router tees bodies and not headers. Marked **do not go looking**: the recorder
keeps the error body's symbolic type, so the next 429 through the router writes `rate_limit_error:
Error` into the CSV by itself — measured rather than reconstructed. Listed here so it is not
rediscovered and filed as an omission.

**Everything struck through in `milestone-1-core/outstanding-work.md`.** The credential shape and the
read timeout were built in Phase 5; silent trimming below the context boundary was measured and
closed the same day. That file marks them in place rather than deleting them, because what a phase
found already answered is worth as much as what it found outstanding.
