# Phase 11 — corpus tools: notes

**Not yet merged.** *(Closed out at the merge, per `plan.md`'s "Placeholders in this file".)*

**Branch `feat/phase-11-corpus-tools`, forked from `main` at `f445d6f`, opened 2026-08-24.** The
first phase of this project worked in a **git worktree** rather than in the trunk checkout —
`../../../../phase-11-corpus-tools`, beside `main` and `to-run-server` under a bare clone.

## Index of the group files

*In the order they were written, which is the chronology the letter-sorted split otherwise breaks.*

| | |
|---|---|
| *(none yet)* | Group A is partly done — Tasks 1, 5 and 6 ran ahead of the plan and are recorded in the sections below rather than in a group file. **No group file exists yet**, and the first will be Group B's |

## The re-derivation before Task 1

**Held 2026-08-24, before the plan was written, and it moved three things.** The findings are in
`plan.md`'s section of that name rather than duplicated here; what belongs in the notes is *how* they
were found, because two of them were found by accident and that is worth not repeating by accident.

**The corpus was read twice by chance.** The first read counted 114 request blobs; a later
re-count, run only because a blob total and an index row count disagreed by four, returned **123**.
The router in `to-run-server` was still up. **The disagreement was the signal, and it was nearly
explained away** — the plausible story was that `wc -l` miscounts a CSV whose free-text
`error_message` column can hold newlines, which is *also true* and would have accounted for a small
gap. Two mechanisms, one of them real, and the wrong one was the more sophisticated.

*This is `../phase-10-body-store/`'s "interrogating a passing check" arriving unprompted: **what
would make this discrepancy innocent anyway?** The answer existed, and it was not the explanation.*

**The empty `dicts/` looked like the invariant failing and was not.** `reference/corpus.md` warns
that a day folder holding a blob whose dictID names an absent dictionary is a real corruption that
**nothing reports until somebody reads it back** — so an empty `dicts/` in both day folders read as
exactly that. Reading it back is the check, `--extract` is the instrument, and it returned **280
blobs, 0 failed**. `request_dict_id` is `none`, not a dictID: the blobs name no dictionary, so there
is none to be missing. **The alarming reading and the true one differ by one column of the index.**

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

## Where the opening session stopped — 2026-08-24

**The project-level handoff is `../../prompt.md`, rewritten for this phase on 2026-08-24, and
`../../status.md` carries the in-flight row.** This section is the *phase's* record of its opening
session and does not repeat them.

*It briefly claimed both files were stale "until Task 6 fixes them", which was wrong twice over:
Task 6 is about `../implementation-plan.md`, and `status.md`'s in-flight table is **live state** that
`../../method/IDM-001-git-branching.md` requires a branch to appear in the moment it opens — not
phase work to be scheduled. Both were updated the same day.*

**Start in the `phase-11-corpus-tools` worktree.** The plan, these notes and the settings change are
on the branch; a session started in `main` sees none of them.

**Four commits, tree clean:** `052ea3e` opened the phase, `12ada32` fixed a dead WebFetch domain,
`3d8ae54` added the deny rules and folded the git allows, `9e0b59d` recorded that the denies did not
fire. *(Said "three" over a list of four until 2026-08-26, when the forward review's cold run counted
them. A prose count beside the thing it counts, again.)*

### The first thing to do, and it costs nothing — *run 2026-08-25, and it is done*

**Was:** run `git add -A` on a clean tree; blocked → settings are session-cached and the rules work;
not blocked → a tracked permission change on a phase branch has no effect until it merges.

**It was blocked.** Settings are session-cached, the rules work, and the merge-scope constraint Task 3
was going to have to record does not exist. The full result, and the larger finding the check ran into,
are two sections above.

### Two things waiting on the owner

1. **Position 3** in `plan.md`'s settled table — whether *"document the dictionary tooling"* also
   means build something. One word, and it changes whether Group D has another section.
2. **Every `❓` in the register**, listed in "Placeholders in this file".

### What is deliberately not in the plan

**The auto-mode classifier diagnosis.** A day of telemetry was spent establishing that Claude Code's
auto-mode classifier gets HTTP 429 from Anthropic — 66 of 232 calls, **every one of them
non-streaming**, against 138 of 145 streaming calls succeeding. It is **not a router defect**: the
router relays the upstream status with its headers, `retry-after` and `anthropic-ratelimit-*` are not
in `DROPPED_FROM_RESPONSE`, and a streaming call to the same model succeeded five seconds after five
consecutive 429s on it.

**It is not Phase 11's subject and no task covers it.** What it left behind that *is* the project's:
a `backlog.md` item to overturn, since `backlog.md`'s *"do not go looking"* note on the rate-limit
headers rests on the recorder keeping the error body's symbolic type — and 66 rows of
`rate_limit_error: Error` do not say **which** limit. That reasoning failed its first real test.
**Two open upstream issues stall on exactly the measurement this router could take:**
[`anthropics/claude-code#82653`](https://github.com/anthropics/claude-code/issues/82653) and
[`BerriAI/litellm#30365`](https://github.com/BerriAI/litellm/issues/30365).

## Where the second session stopped — 2026-08-25

**No phase task was started, and no corpus tool was written.** The session opened on the one check the
handoff put first, and the check turned into the whole session. What it produced is in the two
sections above; this is the state it leaves.

**Still five commits, and the tree is deliberately dirty.** One modified file — `.claude/settings.json`
— **uncommitted on purpose**, because it cannot be exercised until a restart and `3d8ae54` already
demonstrated what committing first costs. `settings.local.json` was deleted by the owner; it was
untracked, so git records nothing of it.

**Nothing moved on Group A, the register, or the plan's approval.** The two items waiting on the owner
are unchanged and still waiting: **position 3** in `plan.md`'s settled table, and **every `❓` in the
register**.

**Task 5 gained its material.** `IDM-002` now has a measured account to record rather than an
inherited claim — that git is outside the built-in read-only set, that deny is exact-match while allow
is a wildcard, and that a model cannot observe its own approvals. The third of those is the reason the
first was wrong in `../../prompt.md` for a day.

**Task 3 lost a constraint.** The worktree practice it records does not need to say anything about
tracked permissions being inert until merge, because they are not — they are inert until restart.

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

## Where the third session stopped — 2026-08-25

**No phase task ran. Everything below is either the settings work closing out, or work that belongs to
other branches and was kept off this one.**

**The three probes ran and the settings file was committed** — `b70769a`, in that order, which was the
whole point. Recorded in full above under "What `.claude/settings.json` now says".

**Then the owner turned auto mode on to test whether Anthropic's rate-limiter had been fixed, and it
failed inside two minutes.** The result is `../../bugs/BUG-001-non-streaming-messages-rejected-as-rate-limited.md`,
on `main` — **not on this branch**, because the classifier diagnosis is not this phase's work and
`../../method/IDM-001-git-branching.md` gives documentation its own prefix. It went to
`docs/bugs-tier`, forked from `main`, merged `--no-ff`, and the tier it introduced is new.

**What this branch kept**, because both correct text this branch's own commits added:

- **Phase 13 allocated** in `../implementation-plan.md` for the rate-limit response headers, with its
  two gates written into the entry rather than left to be rediscovered — `calls.csv` takes no new
  columns under Milestone 2's non-goals, and the store's bodies-only-never-headers promise means a
  **named allowlist** rather than a copy. Phases 11 and 12 were added at the same time; the list ran
  8, 9, 10, "closing review".
- **The capture step marked discharged in fact, evidence pending Task 7.** It had read "NOT
  discharged" since 2026-08-17 on a ground that stopped being true on 2026-08-24.
- **A correction to this branch's own text, the same day it was written**: *no LM Studio traffic has
  **ever** been captured* overreached. The 171 rows are the corpus; `calls.csv` holds 15 LM Studio
  calls on 2026-08-21. One population is a subset of the other and they are easy to conflate.

**Two things a session picking this branch up should not get wrong.**

**`main` was merged into this branch to bring `docs/bugs/` onto it**, which is a shape this project
had not used before — the trunk into a phase branch, rather than the reverse. The reason is specific:
the handoff documents cite `BUG-001`, **a path in backticks is a link here**, and the branch could not
resolve them. `link-check.py` reported **seven** broken links repairable only from the other side.
Un-backticking them would have silenced the instrument without fixing anything, which is the one
option that was refused. Baseline restored to **86**.

**A fresh worktree reports 13 more broken links than this one, and it is not a regression.**
`.claude/settings.local.json` is gitignored, so `git worktree add` does not create it, and a path in
backticks is a link here. That is the same 13 measured on 2026-08-25 when the file was briefly
removed.

**A merged branch is kept here, and `../../procedures/branch-index.py` enforces it. Found by breaking
it.** `docs/bugs-tier` was deleted straight after its merge as tidying the owner had not asked for.
**Nothing was lost** — `git branch -d` refuses an unmerged branch, and `c889207` is the second parent
of the merge commit on `main`, so it stays permanently reachable. **What broke was the index.** The
script's `stale` check reports a description naming a branch that no longer exists and **refuses to
render at all**, on the stated ground that a half-written table spliced into the file is worse than
none. So the next merge's regeneration would have failed before doing anything, with
`../../reference/branches.md` correct on disk but unverifiable.

**Two things were already available and were not consulted.** Every one of the twenty other branches
survives — `docs/add-claude-md` and `feat/phase-0-skeleton` among them, merged weeks earlier — so
`git branch -a` answers this in one line. And `../../method/IDM-001-git-branching.md` has **already
reversed a branch-deletion rule once**: `EPD-004` decision 14 said a rejected plan's branch is
deleted, and 2026-08-17 changed it to merged-and-marked, because *"a deleted branch was the one place
this project discarded a refusal."* That section is about **rejected plans, not merged ones**, so this
deletion did not violate its letter — but it ran against the grain of the only statement the method
tier makes on the subject, and the tool enforces the general case that the rule does not state.

Restored with `git branch docs/bugs-tier c889207`; `--check` then reported **"branches.md is current:
21 rows"**, which also establishes that the generated table had been right the whole time and only the
ref was missing.

**One instrument lesson, and it generalises past permissions.** The probe table in the handoff assumed
its three outcomes were readable by whoever ran them. Only one was: a denial arrives as a tool error,
while a silent run and an approved-after-prompt run are the same observation from inside the model.
**A probe whose outcomes are indistinguishable to its reader is not a probe until someone who can tell
them apart is asked.** The same shape produced `BUG-000`'s founding rule hours later — *an absence is
not a fix* — arrived at independently, from counting 429s rather than from watching prompts.

## What is open at the end of Group A

*(**Corrected 2026-08-26**, on the forward review's finding 15. This read "Group A has not started"
while `plan.md` recorded three of its seven tasks done — **Tasks 1, 5 and 6**, all executed ahead of
the plan on the owner's instruction. The two statements sat in two files for two days. A cold reader
opening the notes first would have re-done the `IDM-002` amendment and the implementation-plan edit,
which is exactly the cost the review priced.)*

---

## The forward review — both runs and the reconciliation, 2026-08-26

**Protocol: `../../method/IDM-004-reviewing-unexecuted-work.md`. Charter: `review-charter.md`, written
first and committed at `8bb501c` before either run started**, because `IDM-004`'s first rule is that
the charter decides what the review finds.

**Subject:** `plan.md` at `2d04840` — the ratification revision, not the version any earlier session
saw. Tasks 2, 3, 4, 7 and Groups B–F. Tasks 1, 5 and 6 out of scope as executed.

| | |
|---|---|
| Runs | the author (this session) and one fresh-context agent, **in parallel**, read-only |
| Cold run's cost | ~157k tokens, 42 tool calls, ~23 minutes |
| Findings | **~18 distinct.** 11 by the cold reader alone, 3 by the author alone, ~4 by both |
| Overlap | **~22%** — and see "What this says about `IDM-004`" below, because it is **not** comparable with Phase 10's 18% |

### The departure from `IDM-004` that was declared in advance

**`IDM-004` assumes the author run is performed by the session that *wrote* the document.** That
session was gone. This one is its successor by handoff: it ratified and revised the plan on 2026-08-26
but did not hold the 2026-08-24 interviews behind positions 1–6. **The charter said so before the runs
rather than after**, which is why the overlap figure above is recorded with a warning attached instead
of being compared.

---

### One refutation was checked and did not survive

**`IDM-004`: *verify a refutation before accepting it. A reviewer can be confidently wrong.*** This is
the run where that rule earned its place.

**The cold reader reported that finding 3's `agent_id` prediction had already resolved *before* the
review began**, from "a subagent spawned earlier today" — 20 rows, timestamps 12:51:08–12:56:21.

**Checked, and the causation is backwards.** Across all four day folders there is **exactly one
distinct `agent_id`**, on **67 rows**, running 12:51:08 → 13:10:53. One value, not two. Those rows are
**the cold reader's own calls**: it read the index partway through its own run, saw 20 of them, and
attributed them to somebody else. The count reached 67 by the time it finished.

**So the prediction resolved positively, and it resolved *because of* this review run — exactly as
`plan.md`'s finding 3 said it would.** The outcome the reviewer reported is right; the mechanism it
gave is not. **`observe.py:40` is confirmed by measurement for the first time in this project's
history**, and task 18's defect-filing contingency is dead.

*This is the repository's own recurring shape landing on the reviewer rather than on a session: a
plausible reading and the true one, one query apart. It is the sixth recorded instance.*

---

### Accepted, ranked by what it costs to find later

**Verified against the disk by the author before acceptance, not taken from the report.**

| # | Finding | Evidence re-checked | Lands on |
|---|---|---|---|
| **1** | **45 consecutive calls have no stored request body.** `request_ref = too_large`, all in session `ad9392ae` — the corpus's largest at 292 calls, the one a reader would pick to demo. Structural, not a fluke: request bodies grow monotonically, so every long session eventually crosses the cap and **the tail is always what is lost** | **45 rows, the only sentinel present in the whole corpus** | task 12, `JSONL_SCHEMA_NOTE` |
| **2** | **"Requests are cumulative" is false on raw bytes.** True only after two normalisations the plan never names: `cache_control` markers migrate between calls, and the same message is serialised as a bare string in one call and as content blocks in the next. Raw: 9 prefix / 84 not. Normalised: 85 / 8. Plus a filter: 75 / 0 | accepted on the reviewer's evidence; the author's own corpus-gate check confirmed the premise holds *with* retries as the visible artefact | tasks 11, 12, 13 |
| **3** | **Interleaved request classes share one `session_id`** — recap, suggestion-mode, two-message classifiers, and `count_tokens`. **Four kinds, not the five reported** — see the correction below | `count_tokens`: **65 rows** — 0/21/43/1 across the four days. The plan says "**No `count_tokens` at all**" | task 12 |

***One of the reviewer's five classes was a real user message and is struck.*** It listed
`"Ping to you to keep cache warm: I still reading and thinking"` ×2 as a synthetic probe. **The owner
typed it, twice, and confirmed so on 2026-08-26 when asked.** The author flagged it as suspect before
the owner was asked, on the grounds that it appears verbatim in this session's own dialogue — *a class
of error only available to a reviewer that cannot see the conversation it is reading about.* **Had
"drop the probe classes" been implemented from the reviewer's list unchecked, it would have deleted
genuine turns** — the exact failure this phase names as refuting it.
| **4** | **`agent_id` is a partition key, not a filter.** A subagent's calls carry the **parent's** `session_id`, so a converter keyed on session alone splices a separate conversation into the parent transcript | **all 67 agent rows carry this session's id** | task 12 |
| **5** | **`messages` carries a third role, `system`; the plan's model has two.** On 14 calls the *last* message — the one delta reconstruction emits as the new turn — is `system` | author confirmed independently in `corpus-gate/run-01/requests/00012.bin`: roles user, **system**, assistant, user | tasks 12, 13 |
| **5b** | **…and it collides with the fidelity marker.** `JSONL_SCHEMA_NOTE` was settled as "a `system` record at the head of each file". **If real `system` turns exist in reconstructions, the marker announcing "this is not a real record" is indistinguishable from one** | author-only finding | register §5, task 13 |
| **6** | **94 calls have an error response and no task says what the converter emits.** 92 `http_error` + 1 `client_disconnect` on `/v1/messages`. An error body is `{"type":"error",…}` — not a message | author's cross-tab: **693 stream=true ok; 92 stream=false http_error; 66 stream=false ok** | task 11 |
| **7** | **Task 19 names a command that cannot produce the number it exists to produce.** The ratio is printed inside the verify loop at `cli.py:176`, which register §2 assigns to **`verify-archive`**, not `extract` | verified by reading the register against `cli.py` | task 19 |
| **8** | **There is no `❓` column, so task 22's check cannot fail.** `❓` was always a marker inside cells. Two §5 rows defer their value to task 13 and under `IDM-008` should carry `❓`: `JSONL_SCHEMA_NOTE` and `SYNTHETIC_UUID_NAMESPACE` | verified against the register's own tables | register, task 22 |
| **9** | **The register carries no record shape and no index shape**, both of which `IDM-008` requires by name. The JSONL record shape — **this phase's entire output** — appears nowhere; nor do the index's 26 columns; nor the five `request_ref` sentinels | `IDM-008` re-read; `stats.COLUMNS` (20) + `corpus.INDEX_EXTRA_COLUMNS` (6) = the 26 every day's `manifest` reports | register §§1–8 |
| **10** | **`<seq>` is never defined** — per-session or per-day, width, timestamp or index order (the index is in **completion** order), and what it means for a session spanning days. 10 rows have an empty `session_id`, rendering `<out>/bodies//…` | accepted; dedup makes it load-bearing — 849 digest rows resolve to 737 distinct digests | register §7, task 17 |
| **11** | **`corpus-gate` is misdescribed.** No root `manifest.csv` — one per run, no header row. "Responses as **raw SSE**" is wrong for 22 of run-01's 49, which are error JSON | author confirmed: `run-01/`, `run-02/`, `run-03/` each hold their own manifest; `00006.bin` is an `overloaded_error` body | finding 4, task 15 |
| **12** | **"No LM Studio traffic exists in the captured corpus" is false in both places it is asserted** | **1 `backend=lmstudio` row** in `2026-08-21`, plus 3 calls in `corpus-gate/run-02-lmstudio/` | finding 3, "does not settle" |
| **13** | **Task 14 has nothing to run.** It is "drive it and diff it", but `--format jsonl`'s writer is **task 17, in Group D, after it**. Group C is placed first deliberately and the dependency runs the other way | verified by reading the task order | Groups C/D ordering |
| **14** | **Task 9 breaks an existing test and the plan does not mention it.** `tests/test_corpus.py:453` shells out to `python -m ilirium_llm_router --extract <day>` | accepted on the reviewer's citation | task 9 |
| **15** | **`notes.md` said Group A had not started** while `plan.md` recorded three of its tasks done; and "Three commits" sat above a list of four | **fixed in this file, above**, at the two cited places | — |
| **16** | **The register's SSE event list is incomplete — `event: ping` is absent** | author-only; observed in `corpus-gate/run-01/responses/00012.bin` | register §5, task 11 |
| **17** | **Retries produce byte-identical consecutive requests** and delta reconstruction has no defined behaviour for a zero delta | author-only; `00003.bin`≡`00004.bin`, `00006.bin`≡`00008.bin` | task 12 |

### Refused, downgraded, or already true

**Recorded with reasons, per `IDM-004` — a refused finding with no reason is re-raised by the next review.**

- **The `agent_id` causation.** Refuted above. **The finding's *conclusion* is accepted and its
  *mechanism* is not**, and register §8's "0 of 770" needs replacing with a real number rather than
  merely being corrected.
- **`.sse`/`.json` extension rule.** The reviewer checked every stored response in all four folders
  and found **zero mismatches** — the rule is sound. Downgraded to finding 10's edge case: 10 rows with
  empty `stream` and zero-byte bodies. *Kept because the reviewer also noticed `observe.py` decides by
  **content-type**, not by the request's `stream` flag, and the design deliberately allows them to
  disagree.*
- **The four superseded spellings** — `--to-jsonl`, `--verify-only`, `--day`-as-option,
  `corpus-<day>`, the two-modules proposal, finding 2's old heading. The reviewer checked each against
  the charter's test ("still presented as current") and **filed none.** The false-positive list did its
  job; this is what naming them in advance buys.
- **`link-check.py` at 87 broken / 97 files**, not 86/96. **Not a regression — the delta is entirely
  `review-charter.md` itself** and its own forward citation. The baseline is confirmed rather than
  moved.
- **`Bash(uvx ruff *)`** remains a raised concern with no home. Not a plan defect; still nobody's.

### Questions this review hands to the owner

**None of these is a defect, and none can be settled by reading. They block the plan revision.**

1. **The probe-class calls — emit, drop, or refuse the session?** Dropping them makes the transcript
   match ground truth. Emitting them is the more honest record of *what crossed the wire*, which is
   this milestone's stated subject. **They cannot both be right**, and the choice decides whether task
   14's *"anything else in the diff is a converter defect"* survives as written or becomes a growing
   list of expected differences.
2. **A session whose request bodies stop being captured** — refuse it, emit up to the gap with the gap
   named in-band, or emit assistant-only turns? Not recoverable by any tool: the bytes were never
   written.
3. **Where does the viewer's record schema come from?** It is not published. Two sources: the viewer's
   Rust source, or a real `~/.claude/projects/*.jsonl`. **The plan forbids the second as *input* —
   "oracle, never input" — but task 13 is schema discovery, not conversion, and the plan does not draw
   that distinction.**
4. **Is `PROJECT_NAME_DEFAULT = corpus` compatible with the viewer?** Every real project folder is
   path-mangled. The plan asserts a plain name works, with no evidence.
5. **Matching semantics for `--path`, `--session`, `--model`** — exact or prefix, and how repeated
   filters of different kinds combine. `--path /v1/messages` under prefix matching now sweeps in 65
   `count_tokens` rows.

### What this says about `IDM-004` itself

**Its predicted split did not hold, and that is evidence rather than noise.** `IDM-004` says the
author finds defects about *the record* and the cold reader finds what the author *could not un-know*.
Here the **cold reader found the record defects too** — the missing `❓` column, and this file
contradicting `plan.md` about Group A. The author's three unique findings were all **data** findings:
`ping`, retries, and the `system`-record collision.

**`IDM-004` says its numbers are n=1 and not a rule.** This is n=2, and n=2 disagrees with n=1 about
where the value comes from. *The overlap figure is not evidence either way, for the reason declared
above.*

### ~~One side effect~~ — **retracted 2026-08-26. This section was wrong, and it was the author's error, not the reviewer's**

**This read: *"The cold run created a `.venv` in this worktree"*, and built a governance lesson on it —
that a constraint the parent honours does not reach a delegate unless the prompt carries it, therefore
the charter template needs an environment clause.**

**The owner created the `.venv`.** Told plainly when asked. **There was no side effect, no delegate
exceeded its brief, and the lesson has no evidence under it.** It is struck rather than deleted,
because a retracted claim that vanishes cannot show that the mechanism caught it.

**How it happened is the part worth keeping.** The author observed a `.venv` that had not been there
an hour earlier, knew a delegate had just run and had needed `zstandard`, and **inferred a cause that
fit perfectly**. It was never checked against the one person who could confirm it. *That is the same
shape as the reviewer's `agent_id` error two sections above — a plausible reading, a true one, and one
question between them — except this time it is the author's, in the document that records the
reviewer's.*

**The charter's environment clause is not adopted**, having been argued from a fiction. If a future
delegate does exceed its brief, that will be the evidence, and this paragraph is the reason to wait
for it.

## Task 2 — the inode note, and a justification with seven homes, 2026-08-26

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

### The mtime justification is dead, and it has seven live homes

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

**What the task did not know is how many places repeat the dead one.** Two families, seven live homes,
and the two named in the task are two of them:

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
leaps by leaps"*, and a task that quietly grows from two files to nine is the thing that position
rejects. **The owner's answer, 2026-08-26: all seven.** It is committed separately from Task 2 so the
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
