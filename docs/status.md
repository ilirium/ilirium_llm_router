# Status

**State, not inventory.** Unscheduled work lives in `backlog.md`; this file says where the project
is and what is in flight. Three sections, most volatile first.

---

## Where we stopped

*Changes every session. If this section passes ~30 lines, or starts carrying anything that outlives
the session that wrote it, it has become a document and gets its own file.*

**2026-09-04 — Phase 13 is open. Groups A–D are complete; Group E is part-done and **stopped at a
checkpoint that is the owner's**.** `docs/phase-13-method-and-backlog`, forked at `dec7c4a`.
*`git log main..HEAD` is the commit count; it is not written here, because a number written at a
handoff is stale at the next commit and this file has four recorded instances of exactly that.*

**All three method documents are written and in force.**

| | |
|---|---|
| **`IDM-009`** | reviewing **executed** work — the third review protocol, and it draws the line between all three |
| **`IDM-010`** | the per-phase `for-the-owner.md` |
| **`IDM-011`** | the backlog — **and one of its rules is in force now**: a session asks before filing an item |

**Where Group E is.** Task 13 compiled the item inventory, task 17 wrote and drove
`procedures/backlog-index.py`, and **task 14a — the cold review — is done.** **`docs/backlog.md` is
still untouched.** *Tasks 15, 16, 18, 19 and 20 all take the ratified inventory as input and none
has run; **they are no longer blocked.***

**The inventory is ratified and it holds 38 items, not the 36 task 13 proposed.** The cold run found
**two missing items** — `backlog.md:716` and `:735`, struck-through `done` entries that open `~~**`
where the pass's enumeration matched bold-or-`###` at the line start. *Both struck entries that open
`**~~` were caught; two bytes in the wrong order made two items invisible.* **The author run had
cleared this exact claim** and named it as the one an author is least entitled to be believed on.

**The owner ratified on 2026-09-04**: the two get ids in file order as `BKL-0032` and `BKL-0033`, so
old `BKL-0032`–`0036` became `BKL-0034`–`0038` and **`BKL-0025`–`0031` did not move**; `BKL-0038` is
`done` rather than `refused`; `BKL-0004` is `partly-done` until task 15 lands. **Two questions are
open and neither blocks** — `BKL-0007`'s status, and whether `BKL-0020` splits, which is the one
that would renumber.

| Commit | |
|---|---|
| `9976873` · `6345eb8` | the plan, then the re-derivation that found it wrong twice |
| `2ffb5e7` · `1d8872b` · `601c041` | the forward review: charter, **18 findings at 17% overlap**, the owner's four answers as rows 21–24 |
| `740eea6` | this file cut from 373 lines to 253, and `prompt.md` replaced whole |
| `05f74ad` · `1a1fbb9` · `50d801c` | `IDM-009`, `IDM-010`, `IDM-011` |
| `809a422` | this file, `prompt.md`, `README.md` and `CLAUDE.md` brought true after the three landed |
| `a9b0c6b` · `e1f6e5f` · `00d3ed3` | the inventory; the frozen copy and the review charter; the script |
| `8374245` · `0ffeb00` | the handoff, and a one-column fix recorded rather than folded in |
| `d315a16` · `d36cc27` · `16c9e6a` | the session close-out, why raw reports are not kept, and the author run |

**`IDM-001` is amended for the second time in three days, and the two amendments differ.**
2026-09-02 changed **where** the record of a declined scope goes — never its own branch. 2026-09-04
changes **whose act it is**: declining scope is still the phase's, **filing is the owner's word**,
and a declined item's decline goes in the phase's `notes.md`.

**`CLAUDE.md` no longer states Milestone 2's phase count.** *It carried that count and was wrong
about it during the phase chartered to fix the count — found by a review, not by a check. The number
lives here now, and only here.*

**Baselines.** This branch changes no `src/` and no `tests/`, so the trunk's **448** stands; *not
re-run in this worktree, which has no venv.* `make lint` clean at the pinned `0.16.1` — **and it
does not reach `docs/procedures/`**, so the new script was linted explicitly and passes.
`link-check.py` reports **117 broken** here against 91 on `main`; the delta is files Group E will
create. **`backlog-index.py --check` exits 1 and that is correct** — this phase's documents already
cite ids `backlog.md` does not carry yet, and it flips to 0 when task 15 lands.

**This section was 154 lines and is now short again — the four older entries were removed, not
moved.** *Every fact in them was checked and found to have a durable home already: Phase 11's and
Phase 12's in their phase notes, and `fix-slop-docs/opening-playbook-not-run-table`'s entire content
in its row in `reference/branches.md`, which is richer than the prose was. **A new file would have
been a fifth home for facts that already had four.** This discharges the open item `prompt.md`
carried.*

## Where the project is

*Changes every phase.*

**One row per milestone. Per-phase detail lives in the archive** — branch, fork point and merge commit
belong to the phase note, and each milestone's own index reads its phases in order.

| | Subject | Phases | State | Read it in |
|---|---|---|---|---|
| **1** | The core router — dispatch, byte-relay, observability, failure handling | 1–7 | **complete** 2026-08-07 | `milestone-1-core/README.md`, which carries every branch and merge hash with what each phase settled |
| **2** | The corpus — capturing bodies for analysis | 8– | **open**, five phases merged — 8 through 12, the last 2026-09-02 — and **Phase 13 in flight** | `milestone-2-corpus/implementation-plan.md` **until the milestone closes**; its `README.md` is a closing artefact and does not exist yet |

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

**Five phases done. The first two touched no `src/`** — Phase 8 built the method tier and the
guardrails, Phase 9 decided `EPD-003` and ran the gate that named the claim above — **and Phase 10 is
the first of this milestone that did**, merging 2026-08-21 as `32c26bb`; Phase 11 built the offline
tools over the store, merging 2026-08-28 as `7e53f74`; Phase 12 made it installable, merging
2026-09-02 as `6c75997`.

**And the merge that closed Phase 12 made this paragraph stale for a fourth time, within minutes of
the phase that existed to fix it.** *Written down rather than quietly corrected, because it is the
strongest evidence the `backlog.md` item has: the count went stale **because a phase landed**, which
is the one moment nobody is reading prose. A derived count would not have moved.*
*(Both sentences above were stale between Phase 10's close and the 2026-08-21 edit: they said two
phases and that Phase 10 had the opaque half still to test. **That is the paragraph below happening
again, to the paragraph that describes it** — prose that undercounts goes stale where a missing
table row would be visible. Recorded rather than quietly fixed, because it was the second instance.*
**And it happened a third time.** *This paragraph and the milestone row above both said **three**
from Phase 11's merge on 2026-08-28 until Phase 12's task 12 fixed them on 2026-09-02, while
"Where we stopped" said four on the day of that merge — so the file disagreed with itself for five
days. Three instances of one defect in one file is no longer evidence about prose; it is the
argument for the count living in exactly one place. **Filed in `backlog.md` rather than fixed
here**, because choosing that place is a change to what this file is.)*
`milestone-2-corpus/implementation-plan.md` describes all four; **their merge
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

1. **Exercise the corpus tools by hand.** *The owner's, and the phase was shaped around it: task 14
   was struck so this would happen after the merge rather than inside it.* Nothing has driven
   `extract` against the real corpus except the author's own scripts.

   ```sh
   ilirium-llm-router extract logs/corpus/2026-*/ --out ./dump --format jsonl --format bodies
   ```

   Then point a history viewer's Custom Claude Directory at `./dump` — **never at
   `~/.claude/projects/`**, which position 12 forbids and which is not a reversible mistake. **What
   to look at first:** whether the fidelity note renders at all, whether a session's several files
   read as separate conversations, and whether the 45 gaps in the largest session look like gaps.

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
**And it is now per-worktree** — the layout below differs in each, and **`git worktree list` is the
count** rather than a number written here. That is new since this section was written. *This
sentence said "there are three checkouts" until 2026-09-02, when it was two: the phase-11 worktree
had been removed and nothing that said three was re-run. It is three again today, for a different
reason, which is exactly why the number does not belong in prose.*

**`to-run-server/logs/` — the live one, 153 MB** *(re-measured 2026-09-02; it read 93 MB, taken
2026-08-25)*

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

**Worktrees that have been removed are not described here.** `phase-11-corpus-tools/` and
`…/opening-playbook-not-run-table` are both gone; `git worktree list` is the answer to what exists,
and today it is `main`, `to-run-server` and `phase-13-method-and-backlog`. *The findings those trees
carried are kept in their branches' records — the tree was only ever the instrument.*

**`make test`, `make lint` and `make check` all ran there and none of them created `logs/`** — which
is `cli.py`'s documented promise that `--check` configures no logging, demonstrated rather than
asserted. That worktree's config also reported `Corpus: off`, so nothing done in it could reach the
corpus. Its `.venv/` was created **by the owner**, which is why `uv run python` worked there. *(This
file briefly recorded that a review subagent created it. It did not; that claim is retracted in
`milestone-2-corpus/phase-11-corpus-tools/notes.md`.)*

**A fresh worktree starts with neither.** So `uv run python` does **not** work in a new tree until a
venv is made there, and anything importing `zstandard` needs one. *Confirmed again 2026-09-04 in
`phase-13-method-and-backlog/`, which has neither. This sentence named
`…/opening-playbook-not-run-table` as the live example until that worktree was removed — **a fresh
example goes stale exactly as fast as the last one**, which is why the rule is stated and the tree
is only cited as evidence for it.*

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

**`docs/phase-13-method-and-backlog`, opened 2026-09-04**, forked from `main` at `dec7c4a`. A
documentation phase — three method documents and the backlog refactor — carrying **no `src/`
change**, which is why the prefix is `docs/`. **Entered here at task 1**, which is where `IDM-001`
puts it.

**Nothing else is in flight.**

**Merged branches are kept, not deleted, and the tooling enforces it.** `branch-index.py` refuses to
render when a description names a branch that no longer exists, so deleting one breaks the next
merge's regeneration. Found on 2026-08-25 by deleting `docs/bugs-tier` and restoring it.

**Push state cannot be checked from here.** `origin` is configured, but this clone holds **no
remote-tracking refs at all** — `git branch -r` is empty — so no local command can tell whether
anything has been pushed without a fetch. *The last word on it is the owner's, 2026-08-28, and
`status.md` has always recorded that as reported rather than checked. What is new on 2026-09-04 is
knowing it is **unverifiable locally**, not merely unverified — so a session must ask rather than
look.*

*Trimmed twice for the same reason, and the second time is the interesting one. On 2026-08-25 four
paragraphs of commentary on **merged** branches were cut, because this section's opening rule says
merged branches are not listed and it had accumulated 22 lines of them. **By 2026-09-04 it had
re-accumulated four more** — Phase 12, `fix-slop-docs/opening-playbook-not-run-table`, Phase 11 and
`docs/bugs-tier` — each a paragraph explaining that the branch is merged and therefore not listed
here. **Each of the four was verified to have a row in `reference/branches.md` before it was cut.**
The rule did not fail; what fails is closing a branch out by writing a sentence here instead of
deleting one, and the second instance is the argument for that being the thing to notice.*
