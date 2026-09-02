# Status

**State, not inventory.** Unscheduled work lives in `backlog.md`; this file says where the project
is and what is in flight. Three sections, most volatile first.

---

## Where we stopped

*Changes every session. If this section passes ~30 lines, or starts carrying anything that outlives
the session that wrote it, it has become a document and gets its own file.*

**2026-09-02 (later the same day) — Phase 12 is executed, all five groups, and waits only on the
merge.** `feat/phase-12-installer-and-readme`, **448 tests** from 438, `register-check.py` 28 of 28.
**The owner asked to be waited for before the merge runs.**

**The `README.md` is ten sections, 133 lines to 304**, the brief is a capture, and the count that
had gone stale in `status.md` is fixed. Phase 11's inherited commitment is discharged: its temporary
corpus-tools section is now "Commands", checked by a 38-element sweep of the old file rather than by
rereading it.

**Three instruments reported something untrue without failing, across two groups.** `uvx --from`
served a stale build that exited 0 for code that had not shipped; `$?` after a pipe reported the
wrong command's status; and **`uv tool upgrade` installs changed code while printing "Nothing to
upgrade"**, because its summary compares version numbers rather than builds. All three exited 0.
*Both Quick start lines nobody had driven turned out to be wrong — `--force` was unnecessary, and
`upgrade` was described as inert when it is merely quiet.*

**The register check found the `README.md` carrying five caveats where settled row 6 says four.**
The fifth was this session's own judgement and the fact was moved rather than dropped. **A plan's
settled table is not overridden by the plan being executed**, which is the rule that decided it.

**The router installs and runs without the repository.** `uv tool install <path>` yields a working
binary; `init` writes `config.yaml` and `.env.example` into the working directory; `check` accepts
them unmodified; `serve` creates `logs/telemetry/` there and shuts down reporting `0 arrived, 0
recorded, 0 lost`. All of it driven from directories that have never held this checkout.

**The forward review under `IDM-004` earned its cost before task 1 ran.** It found **three defects
in `src/`** that no test would have caught, two of which the author had stated to the owner as
fact.
The largest: **`load_dotenv()` never read the working directory** — it walks up from `cli.py`, which
in a checkout reaches the repository root by accident and in an installed tool reaches `$HOME`. A
`.env` beside the config was invisible while the error told the user to set the variable in it.

**Two instruments produced results that were wrong and did not fail.** `uvx --from <path>` served a
**stale build** — `--refresh` did not help — so a driven test exited 0 for a feature that had not
shipped; caught only because a printed message was wrong. And `$?` after a pipe reported 0 for a run
that had exited 1. **Both are recorded in `prompt.md`'s instruments list.**

**2026-09-02 — `fix-slop-docs/opening-playbook-not-run-table` merged. A new prefix pair, and five
documents corrected.** Four commits, **no `src/` or `tests/` change**, so the 438 below stands. The
branch exists because the owner named a defect class: documentation wrong *for a reason* — a
sentence summarising a table it has stopped matching, a count nobody re-ran, a directory described
in the present tense after deletion. **`fix-slop-docs/` and `fix-slop-code/` are now rows in
`IDM-001`'s prefix table and in `CLAUDE.md`**, and they name a *cause* rather than a kind of
artefact, which breaks that table's heading on purpose.

**Baselines re-run on the merged trunk.** `make test` **438 passed**; `make lint` clean at the
pinned `0.16.1`; `make check` valid; `branch-index.py --check` current at **23 rows**;
`link-check.py` **83 broken, 2 roundabout** — *unchanged by the merge, which is what the finding
above predicts*: the new citation of the untracked path resolves in `main` and would not in a clean
checkout.

**What it found while fixing what it was sent to fix — which is the argument for the prefix.**
`IDM-001`'s own accepted-duplication section said *"each of those five"* beside a list of six.
`to-run-server/logs/` is **153 MB**, not the 93 recorded on 2026-08-25. And **`link-check.py`'s
headline count is a property of the worktree, not of the repository** — 83 on `main`, 101 in a clean
checkout — so the baseline row below records *a tree*, and a session re-running it elsewhere will
read the difference as a regression it caused. That one is in `backlog.md`, under the existing
`link-check.py` item.

**2026-08-28 — Phase 11 is complete and merged. Milestone 2 is four phases in.** Merge `7e53f74`,
51 commits; branch index regenerated at `f97c4b6`, 22 rows. **438 tests**, from 310 when the phase
opened.

**`extract` and `verify-archive` read the archive back.** Selection is exact on session, model, path
and `--agent`; output is `bodies/` and `projects/` under one `--out`, and a session is rebuilt into a
transcript a history viewer opens. **No `❓` remains anywhere in the phase register**, and
`evidence/register-check.py` gates it at 89 checks.

**The one thing this phase deliberately did not do: nobody has driven the tools by hand.** Task 14
was struck on the owner's decision — a ground-truth diff was judged too early to be worth its cost —
so the evidence is mechanical throughout. **Do not read "Phase 11 is merged" as "the tools were
tried".** That step is the owner's, next.

**Four findings worth carrying out of the phase:**

1. **A `session_id` is not one conversation** — 36 across 9 sessions, including a 66-call subagent
   under its parent's id. And **a request's tail is provisional**: 100 messages were revised by a
   later call, 9 changing role.
2. **A systematic mutation sweep found 5 real logic defects that 23 targeted mutations could not**,
   because every targeted one had been chosen expecting it to fail. It also found **twelve tests
   comparing the code to itself**, which nothing else can find.
3. **The sweep nearly destroyed the module it measured.** `finally` does not run on `SIGTERM`:
   `transcript.py` was left comment-stripped, 256 of 670 lines gone, **suite passing 427/427**.
   `git status` caught it.
4. **A settled justification stopped being true while its requirement stayed right.** The missing-day
   error's stated failure mode cannot occur in the design that was built. The error was kept and the
   reason rewritten in place.

**Baselines, on the merged trunk.**

| Check | Figure |
|---|---|
| `make test` | **438 passed** |
| `make lint` / `make check` | clean at the pinned `0.16.1` / valid |
| `register-check.py` | 89 checks, 0 failed |
| `link-check.py` | **83 broken, 2 roundabout** |
| `branch-index.py --check` | current, **22 rows** |

*`make lint` still cannot see column width — `E501` is not in ruff's default set. Check added lines
by hand, in **characters**: `awk` counts bytes and reported 13 where there were 4.*

## Where the project is

*Changes every phase.*

**One row per milestone. Per-phase detail lives in the archive** — branch, fork point and merge commit
belong to the phase note, and each milestone's own index reads its phases in order.

| | Subject | Phases | State | Read it in |
|---|---|---|---|---|
| **1** | The core router — dispatch, byte-relay, observability, failure handling | 1–7 | **complete** 2026-08-07 | `milestone-1-core/README.md`, which carries every branch and merge hash with what each phase settled |
| **2** | The corpus — capturing bodies for analysis | 8– | **open**, four phases in — 8, 9, 10 and 11, the last merged 2026-08-28 | `milestone-2-corpus/implementation-plan.md` **until the milestone closes**; its `README.md` is a closing artefact and does not exist yet |

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

**Four phases done. The first two touched no `src/`** — Phase 8 built the method tier and the
guardrails, Phase 9 decided `EPD-003` and ran the gate that named the claim above — **and Phase 10 is
the first of this milestone that did**, merging 2026-08-21 as `32c26bb`; Phase 11 built the offline
tools over the store, merging 2026-08-28 as `7e53f74`.
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

**`phase-11-corpus-tools/` — the worktree is gone, removed after the merge. The finding it carried
is kept, because the tree was only ever the instrument.** *Rewritten 2026-09-02; it described a live
directory in the present tense, and had done since the tree was deleted.*

**`make test`, `make lint` and `make check` all ran there and none of them created `logs/`** — which
is `cli.py`'s documented promise that `--check` configures no logging, demonstrated rather than
asserted. That worktree's config also reported `Corpus: off`, so nothing done in it could reach the
corpus. Its `.venv/` was created **by the owner**, which is why `uv run python` worked there. *(This
file briefly recorded that a review subagent created it. It did not; that claim is retracted in
`milestone-2-corpus/phase-11-corpus-tools/notes.md`.)*

**A fresh worktree starts with neither, and `…/opening-playbook-not-run-table` has neither —
checked 2026-09-02.** So `uv run python` does **not** work in a new tree until a venv is made there,
and anything importing `zstandard` needs one.

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

**`feat/phase-12-installer-and-readme`, opened 2026-09-02 from `5cdc1c9`**, worktree at
`…/phase-12-installer-and-readme`. **The installer and the `README.md` rewrite** — seventeen tasks
in five groups, plan approved and forward-reviewed under `IDM-004` before its first task. Its
permanent record will be its phase note, per `IDM-001`.

**All seventeen tasks are executed and the branch waits on the merge**, which the owner asked to be
consulted before. *Closed out here **before** the merge message rather than after it — `IDM-001`
asks for that order, and Phase 11's merge is why it asks in those words.*

*`feat/`, because the phase touches `src/`: an `init` subcommand, a fix to the `.env` search, and a
`--version` flag. **The last two are defects the forward review found**, not planned work — and
without them the branch would have been `docs/`.*

*Entered here at the phase's task 1, which exists because the review found this section saying
"None" while the branch was already open. That is the defect this section's own closing paragraph
describes, and it had happened again.*

**`fix-slop-docs/opening-playbook-not-run-table` merged 2026-09-02**, and merged branches are
not listed here. It carried no phase number, so its permanent record is its **merge commit message**
and its row in `reference/branches.md` — `IDM-001`'s third and fourth homes, the pair
`docs/bugs-tier` used. *It was listed in flight here earlier the same day and closed out before the
merge message, which is what `IDM-001` asks for and what the previous merge did not do.*

**`feat/phase-11-corpus-tools` merged 2026-08-28** at `7e53f74` and is not listed here, because
merged branches are not. Its permanent record is its phase note and its row in
`reference/branches.md`. **Its worktree was removed after the merge**, which is harmless — the next
branch gets its own. **The branch must not be deleted**, for the reason two paragraphs down:
removing a worktree is safe and deleting a merged branch is not. *This paragraph said the worktree
"still exists and is spent" until 2026-09-02.*

*This section listed Phase 11 as in flight from 2026-08-24 until the merge. It read **"None. The
table is empty as of 2026-08-21"** before that, which was true when written and false the moment the
branch opened — the defect this file's own milestone-table entry describes, in the section that
exists to prevent it.*

**`docs/bugs-tier` merged 2026-08-25 and is not listed above**, because it is done. It carried no
phase number, so its permanent record is **its merge commit message** plus **its row in
`reference/branches.md`** — `IDM-001`'s third and fourth rows, both added the day they were needed.

**Everything is pushed as of 2026-08-28**, on the owner's word at the close of that session; this
was **not** verified against `origin` and is recorded as reported rather than as checked. *Before
that, on 2026-08-25, `git push --all` rejected `main` because `origin` held two commits from
2026-08-21 that this bare clone never received; both are merged in now. That paragraph read "`main`
is ahead of `origin/main` and nothing has been pushed" until then — true when written, and the reason
the divergence came as a surprise.*

**Merged branches are kept, not deleted, and the tooling enforces it.** `branch-index.py` refuses to
render when a description names a branch that no longer exists, so deleting one breaks the next
merge's regeneration. Found on 2026-08-25 by deleting `docs/bugs-tier` and restoring it.

*Trimmed 2026-08-25: four paragraphs of commentary on **merged** branches — `docs/phase-9-corpus-gate`,
`docs/phase-8-method-and-guardrails`, `docs/branch-index` and Phase 10's prefix — were cut. This
section's own opening rule says merged branches are not listed here, and it had accumulated 22 lines
of them. All of it is in `reference/branches.md` and the phase notes.*
