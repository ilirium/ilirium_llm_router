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

## Documentation defects found and not fixed

**The whole of `milestone-1-core/documentation-review-2026-08-16.md`.** A fresh-context agent
reviewed the documentation Phase 7 produced — 23 files, ~5400 lines — and returned a work list:
**five findings verified independently**, roughly 25 more reported but not re-checked, and **six
questions for the owner (Q1–Q6)**. Its Part 5 orders the work by consequence and that order still
stands. **Nothing in it has been acted on.**

*Parked because* the owner parked it whole on 2026-08-17, in favour of opening Milestone 2 and
building router features. It is not blocked on anything and it is not scheduled; picking it up is a
decision to spend a session on documentation instead of on the router.

*Weaker than it looks?* **One item is not.** `reference/measurements.md:34` states a slice that
recomputes to **0.245×** rather than 26.6× — the sign reversed. It makes a future session act
confidently and wrongly, and it is cheap. Everything else in the file can wait.

> **The second of the two was fixed on 2026-08-17 by Phase 8, and is recorded here rather than
> dropped.** `README.md`'s closing worked example told a filer to create a **second Phase 7**,
> contradicting "Naming and numbering" in the same file. Phase 8's Task 4 was already rewriting that
> sentence for two unrelated reasons of its own, so leaving a known bug inside it would not have been
> scope discipline. See `milestone-2-corpus/phase-8-method-and-guardrails/notes.md`. *This paragraph
> said "two items" and named both until then; silently deleting one would leave the next reader unable
> to tell whether it was fixed or forgotten.*

**This entry points and does not restate, deliberately.** The findings, their evidence and the six
questions stay in that one file; copying any of it here would create the second copy this structure
exists to prevent, and the file is far too long to live in an inventory.

**Two consequences of it already landed and are not parked.** Phase 7 is **not** treated as
open — Q2 asked whether it was closed at all, and the owner closed it. And Q5 — where a finding goes
when it belongs to no phase — was answered **for that file only**, by filing it in the archive at the
milestone root; as a general rule for `README.md` it is still open, inside the file with the rest.

## Decisions waiting on a person

None of these is blocked on work. Each is blocked on somebody deciding, and each is argued in full in
`epd/`.

| | Blocked on | Why it may be weaker than it looks |
|---|---|---|
| `epd/EPD-001-model-selection-and-mixed-model-sessions.md` | **a decision only** | Its gate — that a local model can hold a real session — was discharged by Phase 4. Per-request dispatch already satisfies the subagent half with no code, and the `session_id`/`agent_id` columns were accepted separately |
| `epd/EPD-002-token-counting-for-local-backends.md` | **a decision, on a weakened case** | Phase 4 measured the harm it was organised around and found none: the context boundary refuses cleanly rather than trimming silently. Its addendum also records the proposal reading `max_context_length` where it needs the loaded `context_length` |
| ~~`epd/EPD-003-capturing-bodies-for-a-corpus.md`~~ | **no longer waiting on a person** | **Its decision was taken 2026-08-17: fine-tuning is dropped, analysis only.** What remains is its gate — whether a trained zstd dictionary recovers the cross-body compression ratio for per-file storage; if it does not, per-call files are the wrong unit and the sketch does not survive. That is **work, not a decision**, so this row no longer belongs in this section: Phase 9 is running it, and `status.md` carries it. The row is struck here rather than deleted so the next reader can tell it was resolved rather than dropped; it goes at the phase's close |

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

**Extract the portable methodology.** `EPD-004` decision 18 defers this **with a trigger rather than
a date**: when project #2 starts, extraction is a copy of `docs/README.md` with the backend rows
deleted, plus `CLAUDE.md`'s rule block, plus the whole of `method/` unfiltered — `IDM-000` settles that
the tier needs no such filter, because no IDM contains a fact about the router. *Parked because* a
methodology extracted from n=1 is a guess about what generalises. Do not create a global
`~/.claude/CLAUDE.md` before then.

> **Narrowed 2026-08-17. This item is now the extraction only.** The `docs/method/` tier itself was
> **built** in Phase 8 — `IDM-000` through `IDM-003`. Decision 18 declined the tier on a *structural*
> ground, that it would split `docs/README.md`'s acceptance test across two files, and that objection
> was answered rather than overruled: the manual answers *where does a document go* and the tier
> answers *how is the work done*. The n=1 reasoning above is untouched and is still the whole reason
> extraction waits — it was aimed at copying to project #2, which it always was, and never at the tier.
> *This item said "do not build a `docs/method/` tier" until then, which is why the change is recorded
> in place instead of edited away.*

## Instruments and housekeeping

**`procedures/link-check.py`'s exit code carries no information.** `link-check.py:222` is
`return 1 if check(...) else 0` and **there is no expected-failures mechanism in the code** — the
correct-and-permanent hits exist only as prose in the docstring. So the tool exits 1 permanently, can
never gate a commit or a hook despite its own docstring saying *"exits 1 … so it can gate a commit"*, and
reading its output requires a human holding a number from a comment.

**Four pieces of evidence, all from Phase 8, all new:**

- The docstring's counts are **hand-maintained state**, re-derived by Phase 8's Task 17 rather than by
  the tool. A number nobody re-derives is this repository's signature failure.
- **Five of seven "permanent" hits stopped being permanent in a single phase**, and ten further copies of
  the same two paths resolved inside the frozen archive at the same moment — which is why the docstring's
  71 became 61, under a sentence that had said "always".
- **Two independent attempts to predict the new count from the old prose were both wrong**, in the same
  direction, before anyone ran the tool. The prose partitions hits by *where they live*; what resolves
  them is *which path they name*.
- **Every phase plan legitimately cites files it will create.** Phase 8's added 23, all correct, all
  reported as breakage. That is a recurring false-positive class rather than drift.

**Two narrower gaps ride along**, and they are what this item used to be *about* rather than what it is
for. **Heading anchors** are stripped in `candidates()` although `README.md`'s naming table says findings
are "linked by anchor", and **`file.py:N` line citations** are skipped by `is_candidate` for containing
no `/`. Both were verified by hand and both passed — the 11 code citations in a fresh-context review, the
six section titles at commit 6 of the restructure — so they buy repeatability rather than fixing a known
defect. From `EPD-004` decision 21. **Two more were found in Phase 8:** the whole-repository run globs
`*.md`, so citations in `config.yaml`, the `Makefile`, `pyproject.toml`, `.env.example` and `src/` are
unchecked — one stale path was found that way — and a line containing `→` is skipped whole, which leaves
`CLAUDE.md`'s five `→` pointer lines unchecked.

*Parked because* the redesign should be argued from the measurement Task 17 produced, not from the
irritation of having done it once — `EPD-004` decision 12's reasoning, that an instrument which has never
been run should not be committed, applied to an instrument that has. **Decide at Milestone 2's close.**
The cost measured in `milestone-2-corpus/phase-8-method-and-guardrails/notes.md` is the input.

> **The roundabout gap this item once listed is closed.** A roundabout-path check was added on
> 2026-08-16, ahead of the rest, because commit 13 produced two live instances of the defect rather than
> a hypothetical one. See decision 21's second half.

**Static analysis beyond ruff.** Other type checkers, AST-level linters, a language server — over a CLI
or over MCP. `ruff` is all this project runs today; `method/IDM-003-development-tooling.md` records the
pin and what it does and does not catch. *Parked because* nothing depends on it: the code is small, typed
throughout, and covered by 158 tests. *Weaker than it looks?* **Yes, and it is worth saying why the
obvious argument runs the wrong way.** `ty` was tried and **refused** — warnings without useful
information — so the one data point this project has **weakens** the case rather than strengthening it.
The honest reading is that the useful signal may be scarce generally rather than absent from that one
tool, which was at version 0.0.14. **So the next attempt states what it expects to catch *before* it is
run**, and is judged against that rather than against whether it produced output.

**`status.md`'s shape — one row per milestone rather than per phase.** Proposed 2026-08-17 during
Phase 8 and deliberately not done there. *The proposal:* "Where the project is" currently carries a
per-phase table of merge commits, which duplicates what `README.md` assigns to the **phase note** —
branch, fork point, merge commit — and what each milestone's archive `README.md` already indexes.
Replace it with one row per milestone pointing at that archive. *Parked because* it is a filing
question rather than a branching one, and Phase 8 was scoped small on purpose. *Weaker than it looks?*
**Yes.** Only one of the file's four sections grows without bound: "Where we stopped" self-limits at
~30 lines by its own rule, and "In-flight branches" empties at every merge. So the file is not
actually accreting — the duplication is the whole of the complaint. **Carry the counter-argument:** a
separate `history.md` was considered in the same conversation and declined as a **third** copy of those
facts, with nothing forcing it to stay correct.

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
