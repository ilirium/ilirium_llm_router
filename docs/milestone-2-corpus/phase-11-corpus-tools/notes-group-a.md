# Phase 11 — Group A: open the phase

**Tasks 1–7.** Branch, worktree and folder; the `CLAUDE.md` and `reference/corpus.md` corrections; the
worktree practice in `IDM-001`; the Shell rule and `IDM-002`'s read-only set; the
`implementation-plan.md` entry; and the frozen evidence slice.

**Split out of `notes.md` on 2026-08-26**, per `../../README.md`'s rule that a phase's notes divide by
group once it has groups. **`notes.md` stays the entry point** and keeps what belongs to no group —
the re-derivation before Task 1, the session boundaries, the forward review, and what was open at the
end of this group.

*The first three sections here predate the group structure being used. They are Task 5's working
record — the permission probes and what the settings files hold — written on 2026-08-24 and 2026-08-25,
before any section carried a task number in its heading.*

---

## The deny rules work — and the allow list beside them was the actual hazard

**Opened 2026-08-24, settled 2026-08-25 in a fresh session by driving it.**

**What was open.** `Bash(git add -A)` was added to `.claude/settings.json`'s `deny` list, committed as
`3d8ae54`, and **was not blocked** when run immediately afterwards. Two explanations were left
standing: **a**, tracked settings resolve through the worktree to the main checkout, so a phase
branch's permission change does nothing until it merges; **b**, settings are read once at session
start and not reloaded.

**It is `b`. Settings are session-cached.** In a fresh session `git add -A` was **blocked** on a clean
tree, and so was `git stash`. Both deny rules fire. **Explanation `a` is dead** — a tracked permission
change on a phase branch is inert until **restart**, not until merge, which is ordinary and costs the
phase nothing.

**The wrong order is still the lesson.** `../../../CLAUDE.md` says *exercise it before committing*;
`3d8ae54` committed first and checked second. Had the next session inherited *"two deny rules added"*
with nothing saying they were ever seen to work, the phase record would have carried a defect.

### What the check found on the way past, which is larger than what it was for

**Chasing why `git status` prompted the owner produced seven measurements**, all 2026-08-25, in
**accept-edits** mode, in this worktree:

| driven | result |
|---|---|
| `ls` | silent |
| `git status` · `git status && echo ok` · `git --version` · `git --no-optional-locks status` | **all prompted** |
| `git add -A` · `git stash` | **denied** |
| `git add -A .` | **ran, unprompted** |

**Git is not in Claude Code's built-in read-only set.** `git --version` touches no repository and
still prompted, so it is neither the worktree layout nor `git status`'s index refresh — **both were
proposed here, both were persuasive, and both were wrong.** Git prompts unless an allow rule matches
it; `ls` confirms the non-git half of the built-in set is real.

**`../../prompt.md`'s claim that *"read-only `git` … runs without a prompt in every mode"* is false as
written, and the way it entered the record is the finding.** It was asserted by a session that had no
instrument to observe it: a model sees a denial as a tool error and **cannot see an approval at all**,
so a silent run and an approved-after-prompt run are identical from the inside. The owner was the only
instrument, and was never asked. `../../method/IDM-002-harness-configuration.md` is where the corrected
fact belongs — that is Task 5.

**A deny entry matches exactly; an allow entry with `*` does not.** `git add -A` was denied and
`git add -A .` — one character longer, identical effect — ran, because it fell through to
`Bash(git add *)`. **A deny list of spellings is not a guard**: the set of dangerous spellings is open
and cannot be enumerated.

**The allow list was permissive exactly where git destroys work and absent exactly where git is
safe.** `Bash(git checkout *)` permitted `git checkout -- .`; `Bash(git stash *)` permitted
`git stash clear` and `git stash drop`. The denies beside them stopped `git stash` and `git stash pop`
— neither of which loses data. Meanwhile `git status` and `git log`, which cannot harm anything, cost
a prompt every time.

*Why this belongs in the notes: it is the third and fourth time in two days that a plausible reading
and the true one differed by one check. The empty `dicts/` was the first, the deny rule the second,
and here two mechanisms were reasoned out in sequence and both were wrong while the simple
explanation sat available the whole time.*

## What `.claude/settings.json` now says, and what is unverified about it

**Rewritten 2026-08-25 on one principle: allow what cannot destroy work, and let everything else
prompt.** The blocklist approach was abandoned for the reason above.

- **Removed the three wildcard allows that carried an irreversible spelling** — `Bash(git add *)`,
  `Bash(git checkout *)`, `Bash(git stash *)`.
- **Added read-only git** — `status`, `log`, `diff`, `show`, `rev-parse`, `branch`/`branch --list`,
  `stash list`, `worktree list`, `remote -v`; bare **and** `*` forms, since matching is literal.
- **`git checkout` was replaced by `Bash(git switch *)` rather than narrowed.** `switch` changes
  branches and cannot touch working-tree files; `checkout` conflates that with `restore`. Choosing a
  different verb removes the destructive spelling without having to name it. **`git checkout` now
  prompts every time**, deliberately — it is a working-practice change, not an oversight.
- **Staging is explicit paths only** — `docs/*`, `src/*`, `tests/*`, `.claude/*` and six tracked root
  files. This is the project's own rule expressed *as* the permission instead of as a blocklist of its
  violations. **Matching is by prefix, so a two-path `git add` passes on the strength of its first
  path alone** — much better than `git add *`, and not airtight.
- **Five denies added** for the genuinely irreversible spellings — `git stash clear`, `git stash drop`,
  `git reset --hard`, `git checkout -- .`, `git clean -fd`. They are belt-and-braces. **They are not
  the guard, and no document should describe them as one.**

**`settings.local.json` was merged in and emptied by the owner on 2026-08-25** — it exists, holds an
empty `permissions` block, and grants nothing. Every rule is now tracked and reaches `main` and
`to-run-server` when this branch merges. Four entries went as subsumed duplicates; `python3 *` and
`curl *` were narrowed by the owner back to the two `docs/procedures/` scripts and the LM Studio probe.

**Removing the local file broke 13 documentation links; recreating it empty restored all 13.**
`link-check.py` ran **86 → 99 → 86** across the two moves, which has the side effect of confirming the
baseline by measurement rather than by arithmetic. Ten of the thirteen sit in **frozen historical
records** — Phase 7, 8 and 9 notes, `EPD-004`, the 2026-08-16 documentation review — and three in live
documents, including `../../method/IDM-002-harness-configuration.md`.

**The lesson is not about this file.** A path in backticks *is* a link here, so removing any referenced
file breaks documents that had no defect — and the ten historical ones could not have been repaired
without rewriting frozen records. **Check `link-check.py` before deleting a file the documentation
names**, not after.

**The local file now exists with an empty `permissions` block, by decision.** The split `IDM-002`
describes is structurally intact — tracked policy, untracked local, gitignored, no overlap — but its
*practice* changed on 2026-08-25: **the local half is deliberately empty and every rule is tracked.**
`IDM-002` still calls that half *"machine accretion: whatever this laptop clicked allow on"*, which now
describes a policy the owner has stopped following. **That is Task 5's to record**, and it was left
alone here because Task 5 sits in an unapproved plan.

**One conflict with `../../../CLAUDE.md` was raised and left standing:** `Bash(uvx ruff *)` permits an
**unpinned** ruff — `uvx ruff format` with no version fetches the latest — and `CLAUDE.md` says never
bump the ruff pin as a side effect. The rule authorises the thing the project documents against. Left
as the owner's call, recorded here so it is not rediscovered as a surprise.

**Verified 2026-08-25 by the following session, and only then committed.** Settings are
session-cached, so the file could not be exercised by the session that wrote it — and committing
first is exactly what `3d8ae54` did wrong. All three probes in `../../prompt.md` returned what the
rewrite predicted: `git status` **silent**, `git add -A .` **prompting**, `git stash clear`
**denied**. Nothing needed fixing because nothing surprised.

**Only one of the three probes reports itself to a session, and that is the durable lesson.** A
denial arrives as a tool error, so `git stash clear` was self-evident. The other two *completed* —
which rules out denial and nothing else, because a silent run and an approved-after-prompt run are
the same observation from inside the model. **The owner was the instrument for probes 1 and 2 and was
asked directly.** This is the same correction recorded above against the previous handoff's
*"runs without a prompt in every mode"*: the claim was not wrong so much as unobservable by whoever
made it. **A probe whose two outcomes are indistinguishable to the reader is not a probe until
someone who can tell them apart is asked.**

Two incidental findings the probe table does not cover. **There were no stashes** — checked before
probe 3 rather than trusting the deny to hold, so the destructive case cost nothing either way; that
check is the cheap half of the same habit the probes exist to enforce. And **`git restore --staged`
with explicit paths ran without a denial**, which no rule in the list names in either direction — it
was needed because probe 2, once approved, really does stage everything.

## The git allows are, for now, only on this branch — and that is a self-inflicted gap

**`main` and `to-run-server` currently have no `git add`, `git commit`, `git checkout` or `git stash`
approval at all.** Measured 2026-08-24: `grep -c git` returns **0** against both of `main`'s settings
files.

**How it happened, plainly:** the four mutating git rules were removed from the local half and added
to the tracked half in the same pass. The tracked half is a **branch commit**, so the removal took
effect everywhere and the replacement took effect nowhere except here.

**Left as it is, deliberately.** Restoring them to the local files of the other two worktrees would
put the same permission in both halves, which `../../method/IDM-002-harness-configuration.md` refuses
in as many words — *"narrowing the tracked file later appears to do nothing, because the local copy
still grants it."* Trading a permanent landmine for a temporary prompt is the wrong way round. The
cost is one approval when committing in `main`, and it clears when this branch merges.

**It was also the open question in miniature, and 2026-08-25 answered it.** Tracked settings do *not*
resolve through the worktree to the main checkout — they are read from this worktree, once, at session
start. So the rules on this branch are live **here** after a restart and nowhere else until the merge,
which is exactly the shape described above: a temporary prompt in the other two worktrees, not a
permanent landmine.

**The gap widened on 2026-08-25 and closes the same way.** `settings.local.json` was merged into the
tracked file and emptied, so *every* rule this worktree has — not just the git ones — now reaches the
other two only at the merge. That is the intended direction: one tracked file, an empty local half that
cannot contradict it, per `../../method/IDM-002-harness-configuration.md`.

## Task 2 — the inode note, and a justification with eight homes in seven files, 2026-08-26

**Both halves the task names are done, and both were wrong in a larger way than the task expected.**

### The inode note was not stale — it was inverted

`CLAUDE.md` said `~/Projects/code-2026/ilirium_llm_router` and the OneDrive path were the **same
directory** (identical inode), *"editing either edits both"*. The task predicted this had become false
because *"with this clone there are now genuinely two checkouts"*. **Checked rather than assumed, and
the truth is one step further on:**

| Claim | What is on disk, 2026-08-26 |
|---|---|
| the two paths are one directory | **`~/Projects/code-2026` is still a symlink** into `~/Storage/OneDrive/software-engineering/code-2026`, itself a symlink to `~/Library/CloudStorage/OneDrive-Personal`. The **inode half was never wrong** |
| …and the project is at the end of it | **It is not.** `code-2026/` holds `ilirium_llm_router.zip`, 26 MB, **2026-08-25 18:01**. The working tree was archived, not moved |
| not two checkouts | **Three**, and none of them there — a bare clone at `~/Projects/local/ilirium_llm_router/` with `main`, `to-run-server` and this phase as worktrees, created **2026-08-25 18:25**, twenty-four minutes after the zip |

**So the note told a session that two paths were one directory at the exact moment the project
acquired three that genuinely are not** — the most expensive shape a stale note can take, because the
sentence it replaces is the one a session would have needed.

*`docs/epd/EPD-004-documentation-structure.md:998` carries the same fact in the present tense, and is
**left alone deliberately**: it is the record of a 2026-08-16 decision and cites `CLAUDE.md` as it
stood that day. Correcting an archived deliberation to match today would destroy what it records.*

### The mtime justification is dead, and it has eight live homes in seven files

`reference/corpus.md` said *"newest is by filename, never by mtime"* because *"`logs/` sits inside a
cloud-synced folder on the machine this was built for, and a sync rewrites mtimes."*

**Verified before acting on it, per the instrument lesson:** `~/Projects/local/` is a real directory
under `~/Projects/`, not a symlink and not under `~/Library/CloudStorage/`. The live corpus at
`to-run-server/logs/` is outside every sync root. **The reason is false about this machine as of
2026-08-25.**

**The rule is not in question — the argument for it was simply local when a durable one was four lines
above it.** `reference/corpus.md:55` already promises a day folder can be `tar`'d and unpacked on
another machine; unpacking rewrites every mtime, so mtime ordering cannot survive the move the store
guarantees. That is now the stated reason.

**What the task did not know is how many places repeat the dead one.** **Eight live homes across seven
files** — `corpus.py` carries it twice — of which the task named **one**, `reference/corpus.md`. **Seven
sit outside the task, and two of those are in `src/`.** Two families, and they cannot be fixed the same
way:

| | Where | Which claim |
|---|---|---|
| **A** | `reference/corpus.md:76` **← fixed** | newest-by-filename |
| **A** | `corpus.py:604`, `corpus.py:928` | newest-by-filename — **in `src/`, verbatim** |
| **A** | `dictionary.py:766` | the retrain lock's age comes from inside the file, *"the same reason"* |
| **A** | `tests/test_corpus.py:220`, `tests/test_dictionary.py:676` | the same reason, as a test's docstring |
| **B** | `docs/procedures/corpus-benchmark/README.md:86`, `benchmark.py:55` | **a different claim** — that the fsync figure *measures* a cloud-synced filesystem, so it is the number the router would really pay |

**Family B is not a stale reason, it is a stale caveat on a measurement**, and it cannot be fixed the
same way: the figures it qualifies were taken when the premise held. It needs a dated note, not a
rewrite — and **`phase-10-body-store/evidence/benchmark.py` is a frozen copy of the same file and must
not be touched at all.**

**The question was put to the owner rather than answered here** — position 20 is *"step by step, not
leaps by leaps"*, and a task that quietly grows from two files to eight is the thing that position
rejects. **The owner's answer, 2026-08-26: fix all seven of the homes outside the task.** It is committed separately from Task 2 so the
task's own boundary stays visible in the history.

**The two families are fixed differently, and that is the point of separating them.**

- **Family A is rewritten.** All five now say an mtime is filesystem metadata that anything outside
  this program can rewrite — a copy, a backup restore, the unpack of a tarred day folder. For
  `dictionary.py`'s lock the durable form is narrower and truer: *`since=` is a fact the trainer
  wrote*, and an mtime is not. Only `corpus.py`'s shared `newest_dictionary` carries the dated
  correction note; four repetitions of it would be the defect again in a new costume.
- **Family B is dated, not rewritten.** The recorded fsync figures **are** measurements of a
  cloud-synced filesystem, because that is what was under them when they were taken. Rewriting the
  caveat would falsify the record; deleting it would let somebody re-run the procedure today and read
  the result as the same series. Both files now say when the premise held and when it stopped.

**Verified after:** `make test` **310 passed**, ruff clean at the pinned `0.16.1`, `link-check.py`
**87 broken / 2 roundabout** — all three unmoved. **Line width checked by hand**, because `CLAUDE.md`
says `make lint` cannot see it: **zero added lines over 100 characters.** *(A first pass with `awk`
reported eleven. It was counting **bytes**, and every one of the false positives was a line containing
an em-dash. The instrument, again — and it was checked because the count looked wrong, not because
anything failed.)*

## Task 3 — the worktree practice, and the branch that is not work, 2026-08-26

**`IDM-001` gains one section**, "Worktrees are the standing practice, and one branch is not work",
and `CLAUDE.md`'s existing `IDM-001` pointer gains one clause naming it. Nothing else moved.

**The mechanical fact the task was missing, and it is the one that explains everything else:** git
**refuses to check out a branch that another worktree already holds.** So "run the router against a
stable tree while a phase branch holds the editable one" cannot be solved by checking `main` out
twice — a branch had to be **created to be pinned**, and that is the entire reason `temp/to-run-server`
exists. Written into the amendment, because without it `temp/` looks like a naming preference rather
than a forced move.

**`temp/` is deliberately not a fifth row of the prefix table**, and the amendment says so in as many
words. That table answers *what kind of work this is*; this branch is not work. It carries no commits
of its own, it never merges, its fork point is lost and that is acceptable, and it will never have a
phase folder. A row in the prefix table would invite the next one.

**`branch-index.py` tabling it as *merged* is not a defect and must not be fixed there.** Confirmed by
running it: `--check` reports `branches.md is current: 21 rows` and names only
`feat/phase-11-corpus-tools` as in flight — `temp/to-run-server` is absent from that report because
its tip **is** an ancestor of `main` (`f445d6f`, verified with `git merge-base --is-ancestor`). The
script asks git a factual question and git's answer is right. **What it means is that a branch which is
not work still needs a row**, because the row's last column is the only place that can say so — which
is the argument `IDM-001` already makes in "A derived index is not the hand-maintained list this
document refused", arriving at a case it was not written for.

*It already has that row.* `reference/branches.md:44` carries it, describing itself as **"not a piece
of work, and the only row here that is not."** Checked before writing rather than assumed; the
amendment records the rule, it does not create the record.

**Three consequences of the layout, and only the third needed measuring.** `logs/` is per-worktree, so
a document naming "the corpus" must say which tree's. A session started in `main` sees none of an open
phase. And **tracked settings are read from the worktree the session started in, once, at session
start** — so a permission added on a phase branch is live here after a restart and reaches the other
two only at the merge.

**The dead explanation is named in the amendment so it cannot be re-proposed.** For one day it was
believed that tracked settings resolve *through* a worktree to the main checkout, which would have made
a permission inert until it **merged**. They do not: settings are **session-cached**, inert until the
session **restarts**. *The two predictions differ by days, and by what you would do about it. Only
measurement separated them — and the plan's Task 3 was written around the wrong one, which is why it
carries an instruction not to hedge it.*

## Tasks 4 and 5 — the Shell rule, and the task that was recorded as done, 2026-08-26

**Task 4 was one clause. It took three because the clause needed a source, the source contradicted a
settled finding, and the document Task 4 points at did not exist.**

### The plan's figure was right, and it was worth not taking on trust

Task 4 asserted the general rule *"as documented"* and gave a 10,000-character limit. **Nothing in this
repository recorded either**, so neither belonged in the auto-loaded file unsourced. Fetched from
[`code.claude.com/docs/en/permissions`](https://code.claude.com/docs/en/permissions), 2026-08-26,
against Claude Code **2.1.231**, and **all four claims hold verbatim**:

> *"When Claude Code can't fully parse a command, it asks for approval instead of treating the command
> as read-only. Commands longer than 10,000 characters always prompt because they exceed what the
> analysis parses."*

**And the plan's self-correction was right too** — compound-ness is not the trigger, and
`cd packages/api && ls` is the doc's own example. *The claim it corrected came from a user-filed issue
and was repeated on 2026-08-24 without checking. This is the one place a check confirmed the document
rather than moving it, which is worth recording: the re-derivation habit is not only for finding
errors.* One exception is now in `CLAUDE.md` because git is constant here — **`cd` into a different
directory followed by `git` does prompt**, since that directory's hooks could run.

### Task 5 was recorded as executed and half of it had not been done

**`IDM-002` had no read-only-set section at all.** Found by Task 4 going to point at it. The plan's
"Placeholders" item said *three* tasks were already executed; the note under Task 5 described only the
**settings** work, which is real and did run on 2026-08-24. **The half the task's title names — record
the built-in set, dated, with the source link — was never written.**

*The shape: a two-part task, one part executed, the whole marked done, and the record describing the
part that ran. It survived the forward review because a review checks what a document **says**, and
this document said something true about one half of a task.* **Both plan.md sites are corrected rather
than quietly filled in.**

### And the section contradicted this branch's own measurement within minutes of being written

**The documented set ends: `du`, `cd`, *"and read-only forms of `git`"*.**

**This branch measured the opposite on 2026-08-25** — seven probes, the decisive one being that
**`git --version` prompted**, a command touching no repository. `prompt.md`, `plan.md` and this file
all carry *"every git command prompts unless an allow rule matches."*

**Checked before treating it as a conflict:** the tracked file has **no blanket `ask` or `deny` on
`git`** — the thirteen deny rules are specific (`git add -A`, `git stash`, `git reset --hard`), so the
doc's stated way of forcing a prompt on a built-in read-only command is not what happened here.

**Two readings survive and reading cannot separate them:** the clause postdates 2026-08-25, or
`git --version` is not a *read-only form* to the classifier. **Recorded unresolved in `IDM-002`, with
the check named and its positive result stated first** — with auto mode off, run `git --version` and
have the owner say whether a prompt appeared. **A model cannot run it alone**: a denial is a tool
error, an approval is invisible, so silence and approved-after-prompt are the same observation from
the inside. **Auto mode removes the prompt entirely**, so a probe taken today measures nothing.

***The hazard was written down as the reason for the section and then happened inside it.*** Task 5's
own rationale said a vendor fact recorded here is **"a second home for a fact Anthropic owns and can
change, which would then disagree with reality silently."* It disagreed within 48 hours. **No git
allow rule was removed** — deleting twenty entries on an unverified reading is the expensive direction.

### One more disagreement, found while checking the first

**Anthropic documents that an auto-saved approval lands at the git repository root, *"resolved through
worktrees to the main checkout"*, from v2.1.211. At v2.1.231 here, it does not.** All three worktrees
hold their own `settings.local.json` with **different contents** — this branch's written 2026-08-26,
`main`'s unchanged since 2026-08-24.

**Hypothesis, marked as one: a bare clone has no main checkout to resolve to.** It matters because the
local half is supposed to stay empty, and per-worktree accumulation means it refills three times over.
`IDM-001`'s worktree section was **amended after it was written** to distinguish this from the dead
tracked-settings claim beside it — *the two are one word apart and the doc's phrasing is the same one
this branch declared dead.*

## Task 7 — the frozen slice, and the instrument that cried wolf 1913 times, 2026-08-26

**979 rows, four day folders, 26 columns, taken 2026-08-26T15:16:22Z.** Index only, redacted, no
blobs — ever. → `evidence/`, with `freeze.py` committed beside it so the redaction is auditable.

**Group A is now complete.** Tasks 1–7, of which 1, 5 and 6 ran ahead of the plan and 2, 3, 4, the
missing half of 5, and 7 ran here.

### Why the script is committed and the result still is not reproducible

**Re-running `freeze.py` tomorrow produces a larger slice with a different mapping.** The corpus read
**770 rows** during this plan's ratification and **979** here, the same day. `../../README.md` asks
every evidence artefact to say whether it can be regenerated, and the answer is **no** — the CSVs are
the record, the script is the audit trail. *The plan's own `evidence/README.md` predicted this would be
the column the phase struggled with, and it was right.*

### The instrument reported 1913 secrets and every one was a sha256

The secrets pass is a **separate problem from identifiers**, per `../../README.md`, so it is a separate
pass. Its first version matched `[A-Za-z0-9+/]{60,}` as "a long base64-ish blob" and reported **1913
suspect cells**. **Every one was a digest**: sixty-four hex characters satisfy that rule perfectly.

**`CLAUDE.md`: when a check comes back negative, fix the instrument before believing the result.** Two
things changed, and the second matters more than the first:

1. The pattern now excludes pure hex, with the reason in a comment so nobody removes the exclusion.
2. **The scan moved to run on the *redacted* row, and nothing is written until it is clean.** The
   question worth asking is whether the **committed** file carries a secret — which also covers any
   column the script does not redact. The first version asked a different question and wrote the files
   anyway before reporting.

*A rule that fires on everything is indistinguishable from a rule that fires on nothing. The clean
result is only worth having because the pattern was made capable of returning a dirty one.*

### Two families were redacted beyond the one that was asked for

`session_id` (9 distinct) and `agent_id` (1) were the obvious ones. **The two `*_ref` digest columns
were taken as well.** A sha256 does not reveal a body but it **confirms a guess about one**, and
placeholders preserve every property this phase needs — dedup counts, cross-day identity, which rows
share a blob. **`request_dict_id` was deliberately left alone**: it names a dictionary, not a person,
and `9dd33823` is already committed in `../../status.md`.

**The five sentinels pass through unchanged, and that is load-bearing rather than tidy.** A sentinel
run through a digest redactor becomes a **fake identifier** — and the extractor's entire reason for
knowing the sentinels is to read *"no blob here"* instead of trying a filename.

### What the slice settles, and the one thing it adds

**Every data finding from the forward review reproduces**, at four to five times the sample it was
found on — the 45-row `too_large` tail all inside the 292-call session, the cross-day session now at
**276 calls**, **67 agent rows all carrying the parent's session id**, both response encodings, 96
error rows, 66 `count_tokens`. The review read the disk correctly.

**One thing no earlier reading had: `absent` never appears.** Not even on the **9** router-authored
`/api/hello` rows, which carry real digests. **Four of the five sentinels have never been observed in
this corpus** — `dropped`, `absent`, `error`, and `none` as a *response* ref. The extractor must still
handle all five; the register already says a sentinel used as a filename fails at the filesystem, and
now the register can say how little of that path has ever been exercised by real data.

*`evidence/README.md` itself said **"Empty until Task 5"** and named Task 5 twice. Task 5 is the
`IDM-002` amendment; **Task 7** freezes the slice. **This is the third instance of that exact
off-by-two in this phase** — register §8 carried it, and a session reading only the README would have
gone looking for the freeze in the settings work.*
