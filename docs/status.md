# Status

**State, not inventory.** Unscheduled work lives in `backlog.md`; this file says where the project
is and what is in flight. Three sections, most volatile first.

---

## Where we stopped

*Changes every session. If this section passes ~30 lines, or starts carrying anything that outlives
the session that wrote it, it has become a document and gets its own file.*

**2026-08-26 — Groups A and B are complete and Task 11 with them. Work resumes at Task 12, delta
reconstruction, which is the hard core of the phase.**

*Fourteen commits, from `fe37743`. **Derive it rather than relaying it** — `git log --oneline
fe37743..HEAD` — because a commit count written into a file is stale by the next commit, which is the
failure this section keeps recording about itself.*

**Tasks 1–11 done.** Group A closed the documentation debts and froze the evidence slice; Group B put
the CLI on subcommands; Task 11 built `transcript.py`. **355 tests, up from 310.**

**Four findings, in the order they cost:**

1. **Task 11's "66 buffered assistant replies" was the `count_tokens` count.** The task had already
   corrected that exact conflation once and then landed on 66 anyway. **The corpus holds ONE buffered
   reply in 979 rows.** Measured by decompressing every response blob. The path is built; *"both
   encodings are handled"* is now in "does not settle" so it is not read as coverage.
2. **Task 5 was recorded in `plan.md` as executed and half of it had not been done.** Its settings
   work ran on 2026-08-24; the `IDM-002` amendment its title names was never written, and was found
   only because Task 4 went to cite it. **The forward review read past it**, because a review checks
   what a document says and this one said something true about one half of a two-part task.
3. **The vendor documentation contradicts this branch's `git` finding, and it is unresolved on
   purpose.** Anthropic's built-in read-only set ends *"and read-only forms of `git`"*; seven
   measurements here on 2026-08-25 concluded every git command prompts. **In `IDM-002` with the
   one-observation check that settles it, and no allow rule removed.** *The hazard was written down as
   the reason for that section and then happened inside it, within 48 hours.*
4. **Three instrument errors, all caught because a number looked wrong and none by anything failing.**
   `awk` counting bytes not characters; a secrets scan reporting **1913** suspect cells that were all
   sha256 digests; `$?` after a pipe reporting `tail`'s exit code.

**The two strongest pieces of evidence are not tests.** `verify-archive` over the whole live corpus:
**1793 blobs, 0 failed.** And `reassemble` over every response blob, joined back to the index:
**979 rows, 0 unresolved, 0 contradictions** against an `error_status` column written at capture time
months earlier. *Two instruments built phases apart agreeing row for row.*

**One thing waits on the owner and nothing is blocked by it:** with auto mode off, does `git --version`
prompt? **A model cannot answer it** — a denial is a tool error and an approval is invisible.
→ `milestone-2-corpus/phase-11-corpus-tools/for-the-owner.md`, which is **new** and holds everything
addressed to a person rather than to a session.

*The earlier 2026-08-26 entries — ratification, the forward review, Group A's own findings — are in
that phase's `plan.md` and its **group notes**, task by task. **Fifth trim.***

**The phase's notes were split by group on 2026-08-26**, on the owner's instruction and per
`README.md`'s rule: `notes-group-a.md`, `-b.md`, `-c.md`, with `notes.md` going **963 → 403 lines** and
staying the entry point. **The split surfaced two required lines that were missing** — `notes.md` now
carries the **"Verified by"** table and says it was **written while measuring**, both of which
`README.md` asks of every phase note and neither of which existed.

**Baselines, all re-run 2026-08-26 at the close of this session, in this worktree.**

| Check | Figure |
|---|---|
| `make test` | **355 passed** — 310 at the session's start, +27 CLI and +18 reassembly |
| `make lint` / `make check` | clean at the pinned `0.16.1` / valid |
| `link-check.py` | **86 broken, 2 roundabout** — down one: the register's forward reference to `transcript.py` now resolves |
| `branch-index.py --check` | **current, 21 rows** |

**`make lint` cannot see column width and it bit inside this session** — a 101-character line went
into a commit and passed. `--select E501` reports **23 errors in 9 files**, all prose rewraps.
Deliberately not actioned: `method/IDM-003-development-tooling.md` owns tooling changes. **Check added
lines by hand until then.**

*The file count stays out of the `link-check` row: it moves when `.venv/` does, and broken is the
comparable figure.*

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

1. **Execute Phase 11, starting at Task 12.** ~~Ratify position 3~~, ~~the forward review~~,
   ~~Group A~~, ~~Group B~~ and ~~Task 11~~ — **all done 2026-08-26.** Task 12 is **delta
   reconstruction**: the two normalisations, ordering across day folders, and the error when a
   selected session has calls in a folder that was not passed. **It is the hard core of the phase**,
   and `notes.md`'s "The forward review" holds the seventeen findings it must not re-derive. Twenty settled positions, and the review returned **seventeen accepted
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

**`phase-11-corpus-tools/logs/` — still does not exist. `.venv/` does, and `evidence/` is now
committed.** *`logs/`'s continued absence is still evidence rather than trivia: `make test`, `make
lint` and `make check` have all run here and none of them created it.*

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
| `feat/phase-11-corpus-tools` | Phase 11 — the offline corpus tools: `extract` with selection over one or more day folders, `verify-archive`, and a converter to Claude Code session `JSONL`. **Dictionaries are documented, not extended** — position 3, ratified 2026-08-26 | forked at `f445d6f`; **`main` merged in 2026-08-25** so the branch carries `docs/bugs/`. **The plan was ratified and revised 2026-08-26** — 14 settled positions, `❓` column empty | **start work at Task 12**, delta reconstruction. **Groups A and B and Task 11 closed 2026-08-26**, 355 tests. `cli.py` is on subcommands and `transcript.py` reassembles both encodings. **Task 14 is struck on the owner's decision**: the tools are exercised by hand *after* the phase, so the phase's own evidence is tests and mutation testing — and task 23's mutation check is therefore the strongest thing it produces |

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
