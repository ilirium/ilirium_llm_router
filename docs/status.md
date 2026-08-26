# Status

**State, not inventory.** Unscheduled work lives in `backlog.md`; this file says where the project
is and what is in flight. Three sections, most volatile first.

---

## Where we stopped

*Changes every session. If this section passes ~30 lines, or starts carrying anything that outlives
the session that wrote it, it has become a document and gets its own file.*

**2026-08-26 — Phase 11's plan was ratified, reviewed and revised in one day. Work may begin at
Task 2. Still no phase task started.**

**Twenty settled positions, and the forward review is done** — charter, both runs in parallel,
reconciliation, **seventeen findings folded in**. → `milestone-2-corpus/phase-11-corpus-tools/`, whose
`review-charter.md` is new and whose `notes.md` holds both runs.

**The review's own summary is the thing to carry forward.** The plan's model of a captured session —
*cumulative calls, one user turn and one assistant turn each* — **is simpler than the traffic on
disk**: five interleaved request classes, three roles, two content serialisations, a migrating
`cache_control` annotation, 94 error responses, and **a 45-call tail with no request body at all**.
*"Every one of those is visible in an hour with `csv.DictReader`, and none of them is in the plan."*

**The phase was then deliberately narrowed to a baseline tool.** Errors, `count_tokens`, subagent
partitioning and the second-source check are **deferred**; **Task 14 is struck** — the owner exercises
the tools **by hand after the phase**, so the phase's own evidence is tests and mutation testing.
**That gap is named first in the plan's "does not settle"**, because `CLAUDE.md` says green tests are
not evidence and this phase now has only green tests.

**`observe.py:40` is confirmed by measurement for the first time in this project's history.** It says
`agent_id` *"arrives only on a subagent's call"* — a comment nothing had ever observed. The review's
cold run was a subagent through a capturing router, and **67 rows now carry an `agent_id`**, exactly as
`plan.md`'s finding 3 predicted before it ran. **All 67 carry the parent's `session_id`**, which makes
`agent_id` a partition key for the converter rather than a filter for the extractor — recorded, and
deliberately not acted on.

**Two claims were retracted the same day, one in each direction, and both are struck rather than
deleted.** The cold reader reported the `agent_id` prediction had resolved *before* the review; it was
reading **its own traffic**. And this session reported that the cold run created a `.venv` in this
worktree; **the owner created it**, and a governance lesson built on that inference was withdrawn. *A
plausible reading and the true one, one question apart — twice in one afternoon, once by the reviewer
and once by the author, in the document recording the reviewer.*

*2026-08-25's entry — permissions closed and committed, `BUG-001` measured, the corpus dicting itself,
this clone two commits stale — was cut here on 2026-08-26. **Homes checked rather than assumed:** the
permissions findings are in `milestone-2-corpus/phase-11-corpus-tools/notes.md`, the auto-mode
measurement is `bugs/BUG-001-non-streaming-messages-rejected-as-rate-limited.md`, the dictionary
figures are in that phase's `plan.md` register under two dated moments, and the stale-clone merge is in
its own merge commit message.*

**Still open and unchanged: `BUG-001` has not been reported to either upstream issue.** It remains the
only item in "What is next" not blocked on a decision.

*Trimmed on 2026-08-26 — the **third** trim. It stood at ~58 lines carrying 2026-08-25's four entries;
those are summarised in one italic paragraph above with each home checked rather than assumed. For the
record it kept: the second trim, on 2026-08-25, cut ~162 lines reaching back to 2026-08-21 and found
**three entries that had gone stale in place** — `CLAUDE.md` at 292 lines when it was 297, "eight of
nineteen" branches against a 21-row table, and the corpus called undicted after it had dicted itself.*

***This note claimed the trim "left the section inside its own rule" for most of 2026-08-26, and by the
end of the day that was false: the section is ~78 lines against ~30.** It was true when written, at
~35 lines, and then the same session added the forward review's outcome and re-measured the baselines
into it. **A self-describing note went stale the same way the entries it describes do, in the section
whose rule exists to stop exactly that** — the fourth recorded instance of prose about a count
outliving the count. Roughly a third of the 78 is the baselines block, which is state rather than
entries; **the honest reading is that this section needs a fourth trim and did not get one, rather than
that the rule has been met.***

**Baselines. Read the dates — these were run at two different moments and only one pair is current.**

| Check | Figure | When |
|---|---|---|
| `link-check.py` | **87 broken, 2 roundabout** (file count: see below) | re-run **2026-08-26** |
| `branch-index.py --check` | **current, 21 rows** | re-run **2026-08-26** |
| `make test` / `make lint` / `make check` | **310 passed in 2.5 s / clean / valid** | re-run **2026-08-26, in this worktree** |

***The file count is dropped from that row, and this is the evidence for dropping it.* It read 84 on
2026-08-25 and 97 then 98 during 2026-08-26 — moving by one *within a single session, with no document
added*, because `link-check.py` walks `.venv/` and this worktree acquired one. **The broken count is
the comparable figure and the file count never was.** Broken moved 86 → 87 the same day, and **the
whole delta is `review-charter.md` and its own forward citation** — not a regression.**

**The `make` row is measured in this worktree for the first time, and it moved nothing: 310 passed in
2.5 s, ruff clean at the pinned `0.16.1`, config valid.** Identical to the five-day-old figure, which
is the finding — **no test has been added or removed since 2026-08-21**, consistent with no phase task
having started. **One new `StarletteDeprecationWarning`** (`httpx` → `httpx2`) is recorded and
deliberately not actioned: `method/IDM-003-development-tooling.md` governs dependency bumps, and
nothing here bumps a pin as a side effect.*

## Where the project is

*Changes every phase.*

**One row per milestone. Per-phase detail lives in the archive** — branch, fork point and merge commit
belong to the phase note, and each milestone's own index reads its phases in order.

| | Subject | Phases | State | Read it in |
|---|---|---|---|---|
| **1** | The core router — dispatch, byte-relay, observability, failure handling | 1–7 | **complete** 2026-08-07 | `milestone-1-core/README.md`, which carries every branch and merge hash with what each phase settled |
| **2** | The corpus — capturing bodies for analysis | 8– | **open**, three phases in — 8, 9 and 10, the last merged 2026-08-21 | `milestone-2-corpus/implementation-plan.md` **until the milestone closes**; its `README.md` is a closing artefact and does not exist yet |

*Changed 2026-08-17 from a per-phase table of Milestone 1's merge commits, per the `backlog.md` item
that proposed it. **The hashes are not lost** — each one keeps two to six homes, the fewest being
`532dc86` and `9c30924` at two apiece, and `milestone-1-core/README.md`'s table is strictly richer than
the one removed. What this file kept is
the part that is **state**; a closed milestone's per-phase merge hashes are archive record, and
`status.md` says so at the top.*

Phases 0 and 1 were fast-forwarded before the `--no-ff` convention existed;
`milestone-1-core/README.md` says why they are left that way. **Milestone 2 starts at Phase 8**,
since 7 is taken.

**What Milestone 1 settles:** no protocol translation is needed, and a local model can drive a real
coding session through the router. Both halves were measured rather than argued — one session reached
both backends, and a local model handled tool use, file editing and multi-turn conversation.

**Milestone 2's subject is `EPD-003`** — capturing bodies for a corpus, **decided 2026-08-17**.

**Its central claim is now named**, at the end of Phase 9 and from what the gate returned:

> *The router can archive every body it carries — as opaque, content-addressed, per-call files
> compressed against a shared dictionary — without parsing a payload, without slowing a call, and
> without special storage infrastructure.*

**Two of its three failure modes are discharged**, and the third is not. Phase 9's measurement
settled the storage-infrastructure half; **Phase 10 settled that archiving cannot stay opaque** — tar
a day folder, unpack it elsewhere, and every blob opens and verifies against the digest in its own
filename. **Whether archiving slows a call is untested**, and is parked in `backlog.md`.

**Three phases done. The first two touched no `src/`** — Phase 8 built the method tier and the
guardrails, Phase 9 decided `EPD-003` and ran the gate that named the claim above — **and Phase 10 is
the first of this milestone that did**, merging 2026-08-21 as `32c26bb`.
*(Both sentences above were stale between Phase 10's close and this edit: they said two phases and
that Phase 10 had the opaque half still to test. **That is the paragraph below happening again, to
the paragraph that describes it** — prose that undercounts goes stale where a missing table row would
be visible. Recorded rather than quietly fixed, because it is now the second instance.)*
`milestone-2-corpus/implementation-plan.md` describes all three; **their merge
hashes are in their phase notes**, which is where `method/IDM-001-git-branching.md` puts the permanent
record. *(This sentence first said the plan indexes both hashes. It carries Phase 8's and not Phase 9's
— the plan's Record table records the branch **that file** was created on, which was Phase 8's.)*

*This paragraph carried both merge hashes and a note deferring to the `backlog.md` item above. **That
item is now decided and this is the evidence it asked for:** the prose version said "one phase of it is
done" after Phase 9 merged, and stayed wrong until the owner noticed — while the per-phase table beside
it never went stale, because a merged phase without a row is visibly missing and a sentence that
undercounts is not. **The conclusion is not "prefer tables"** — it is that the row-versus-prose choice
is about what goes stale invisibly, which is a different axis from the duplication the item was
arguing.*

## What is next

*Changes every phase. Two or three items lifted from `backlog.md` and cited to it — the file itself
is the full inventory.*

1. **Execute Phase 11, starting at Task 2.** ~~Ratify position 3~~ and ~~run the forward review~~ —
   **both done 2026-08-26.** Twenty settled positions, and the review returned **seventeen accepted
   findings**, all folded in. **The review's own summary is the thing to carry forward:** the plan's
   model of a captured session was simpler than the traffic on disk, and *"every one of those is
   visible in an hour with `csv.DictReader`, and none of them is in the plan."*
   **Three `❓` are live and deliberate**, all resolved at Task 13.
2. **Report `BUG-001` to the two upstream issues.** They are named in
   `bugs/BUG-001-non-streaming-messages-rejected-as-rate-limited.md`, and both stall on exactly the
   measurement it contains — a paired control showing a streamed request **2.8× larger** to the same
   model accepted **0.6 s** after a non-streamed one was rejected. **The document says this is an
   action, not a finished thing.** It is the only open item here that is not blocked on a decision.
   *(This item replaced **"settle whether a tracked permission change takes effect before it
   merges"**, answered 2026-08-25: settings are **session-cached**, inert until restart rather than
   until merge, and the worktree-resolution explanation is dead. Before that, items 1 and 2 replaced
   **"exercise the corpus by hand"** and **"plan Phase 11"**, both spent. The corpus figures that
   entry quoted — two day folders, 171 rows, **undicted** — are all superseded; see "Where we
   stopped".)*
3. **Decide `EPD-001` or `002`.** Both are blocked on a person rather than on work, and both are argued
   on a case Phase 4 measurably weakened — see `backlog.md`, "Decisions waiting on a person". Deciding
   one is cheaper than any measurement in the list, and neither decision waits on Phase 11.
   (`EPD-003` is no longer among them — decided 2026-08-17 by Phase 9.)

*The measurement items are both in `backlog.md` under "Measurements left open" and neither is listed
here as next, because Phase 11 is chosen and running and this file is not the inventory. Whether
Claude Code shows LM Studio's context error was already there. **Whether archiving slows a call was
added there on 2026-08-21** — until then it lived only in `prompt.md`, which is the one file allowed
to go stale, and in `milestone-2-corpus/implementation-plan.md`'s table. *(This sentence gave as its
reason that "the owner has not chosen Phase 11's subject" until 2026-08-25, which stopped being true
on 2026-08-24 — the conclusion held, the reason for it did not.)**

## What is on disk and not in git

*Harvested from `prompt.md` on 2026-08-21, which was the only place it was written down and which
expires by design. **Re-verified by looking on 2026-08-25**, not relayed — and it had gone stale in
three ways, which is what this section warns about happening to itself. This is working-copy state.
Re-check before trusting a line of it.*

**`logs/` is gitignored whole (`.gitignore:228`), so none of this can be committed by accident.**
**And it is now per-worktree** — there are three checkouts of this repository and the layout below
differs in each. That is new since this section was written.

**`to-run-server/logs/` — the live one, 93 MB**

| Path | What it is |
|---|---|
| `logs/corpus/2026-08-21/`, `2026-08-24/`, `2026-08-25/` | **Three** day folders. Every document that says "two" was written on 2026-08-24 and has not been re-counted |
| `logs/corpus/dicts/req-2026-08-25T103250Z-9dd33823.dict` | **The corpus is no longer undicted.** Installed 2026-08-25T10:32:50Z, 262,144 bytes. All 320 rows in that day's index reference it |
| `logs/corpus/retrain.log` | Three verdicts: `no-complete-day`, then `too-few-samples`, then **`installed`** |
| `logs/telemetry/calls.csv`, `router.log` | **Exists.** This section said *"does not exist yet"* until 2026-08-25; the router created it on 2026-08-21 |

**`main/logs/` — historical, 260 KB of corpus plus Phase 9's**

| Path | What it is |
|---|---|
| `logs/corpus/dicts/req-2026-08-20T110338Z-0e4d84d1.dict` | **The first real dictionary**, 262,144 bytes exactly. **Do not delete it.** `reference/measurements.md` cites the `0e4d84d1` ID as evidence that the same parameters reproduce the same dictionary byte for byte |
| `logs/corpus-gate/` | Phase 9's corpus, **8.8 MB** — re-measured 2026-08-25, unchanged. `measurements.md` names it as the slice behind four rows. It stays |
| `logs/calls.csv`, `logs/router.log` | The router's history to 2026-08-20. **Deliberately left** where they are when the config moved to `logs/telemetry/` — owner's decision, in `milestone-2-corpus/phase-10-body-store/plan.md`'s settled table |

**`phase-11-corpus-tools/logs/` — still does not exist. `.venv/` now does.**

*Both halves changed meaning on 2026-08-26 and the entry is rewritten rather than patched.* The venv
was created **by the owner**, so `uv run python` works here and anything importing `zstandard` can be
run in this worktree. *(This file briefly recorded that a review subagent created it. It did not; that
claim is retracted in `milestone-2-corpus/phase-11-corpus-tools/notes.md`.)*

**`logs/`'s absence has stopped being trivial and become evidence.** It used to be correct because
nothing had ever run here. **Three `make` targets have now run — `test`, `lint` and `check` — and the
folder still does not exist**, which is `cli.py`'s documented promise that `--check` configures no
logging demonstrated rather than asserted. **This worktree's config also reports `Corpus: off`**, so
nothing done here can write to the corpus.

**One warning was dropped rather than carried across, and it stays dropped.** `prompt.md` said
*"stage with explicit paths, never `git add -A`."* The stated reason was that `logs/` holds
uncommittable things — and `logs/` is gitignored, so `git add -A` cannot stage any of it. **The advice
survives on other grounds** — there is now a deny rule that fires — **but the reason originally given
was not a real hazard**, and repeating it would preserve a rule whose justification does not hold.

## In-flight branches

*Merged branches are not listed here — this section holds live state. **They are indexed in
`reference/branches.md`, generated from git**, which is the 2026-08-21 amendment to
`method/IDM-001-git-branching.md`: a hand-maintained list would drift and a derived one cannot. The
permanent record of a phase's branch, fork point and merge commit is still its phase note.*

| Branch | Purpose | Tree | Next action |
|---|---|---|---|
| `feat/phase-11-corpus-tools` | Phase 11 — the offline corpus tools: `extract` with selection over one or more day folders, `verify-archive`, and a converter to Claude Code session `JSONL`. **Dictionaries are documented, not extended** — position 3, ratified 2026-08-26 | forked at `f445d6f`; **`main` merged in 2026-08-25** so the branch carries `docs/bugs/`. **The plan was ratified and revised 2026-08-26** — 14 settled positions, `❓` column empty | **start work at Task 2.** The forward review ran 2026-08-26 — charter, both runs, reconciliation, and seventeen findings folded into `plan.md`. **Task 14 is struck on the owner's decision**: the tools are exercised by hand *after* the phase, so the phase's own evidence is tests and mutation testing |

**Opened 2026-08-24, and it is the first branch worked in a git worktree** —
`/Users/ilirium/Projects/local/ilirium_llm_router/phase-11-corpus-tools`, beside `main` and
`to-run-server` under a bare clone. Recording the practice is Task 3 on the branch itself.

*This section read **"None. The table is empty as of 2026-08-21"** until 2026-08-24, which was true
when written and false the moment the branch opened. It is the defect this file's own milestone-table
entry describes, in the section that exists to prevent it.*

**`docs/bugs-tier` merged 2026-08-25 and is not listed above**, because it is done. It carried no
phase number, so its permanent record is **its merge commit message** plus **its row in
`reference/branches.md`** — `IDM-001`'s third and fourth rows, both added the day they were needed.

**Everything is pushed as of 2026-08-25, and `main` diverged before it was.** `git push --all`
rejected `main` because `origin` held two commits from 2026-08-21 that this bare clone never
received; both are merged in now. *(This paragraph read "`main` is ahead of `origin/main` and nothing
has been pushed" until then — true when written, and the reason the divergence came as a surprise.)*

**Merged branches are kept, not deleted, and the tooling enforces it.** `branch-index.py` refuses to
render when a description names a branch that no longer exists, so deleting one breaks the next
merge's regeneration. Found on 2026-08-25 by deleting `docs/bugs-tier` and restoring it.

*Trimmed 2026-08-25: four paragraphs of commentary on **merged** branches — `docs/phase-9-corpus-gate`,
`docs/phase-8-method-and-guardrails`, `docs/branch-index` and Phase 10's prefix — were cut. This
section's own opening rule says merged branches are not listed here, and it had accumulated 22 lines
of them. All of it is in `reference/branches.md` and the phase notes.*
