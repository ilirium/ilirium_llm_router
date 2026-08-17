# Phase 8 — the method tier and the guardrails: notes

Branch: `docs/phase-8-method-and-guardrails`, off `main` at `6253cbc`. **Merge commit: not yet
merged.** That sentence is deliberate rather than lazy — `../../backlog.md` carries the defect of four
Milestone 1 phase notes that said "merge back with `--no-ff`" and never recorded what happened, and
`IDM-001` now states the rule this line has to obey.

Written **while the work was happening**, task by task, rather than assembled afterwards. That matters
for the re-derivation section below: it records the plan being wrong at the moment it was found wrong,
not reconstructed from the diff.

**Phase 8 has no `evidence/`.** Nothing here is a measurement over the router — the outputs are
documents, a tracked settings file, and two counts (the allowlist prune and the link-checker
re-derivation) which are recorded in this file because that is the only place they can be. Task 10
produces no commit at all. An absent `evidence/` is correct rather than missing, per
`../../README.md`'s phase template.

---

## Task 0 — re-deriving the plan, before Task 1

`plan.md`'s own instruction, and `../../README.md`'s: *a phase's first act is to re-derive its own
plan against what is now known.* Four of Milestone 1's six phases found their plan wrong on contact.

**This one is wrong in four places, and right everywhere else that was checked.** What was checked,
and passed:

| Claim in `plan.md` | Verified |
|---|---|
| Nothing has been executed | ✅ all 14 branch commits are the plan, `implementation-plan.md`, or `status.md`. No task-numbered commit exists |
| `.claude/settings.local.json` holds **53** entries | ✅ counted mechanically |
| The fourteen fossils, one by one | ✅ every one present, at the shape quoted |
| `lms load *` / `lms unload *` present; `uvx ty@0.0.14 check src tests` present | ✅ |
| The prune arithmetic 15 + 2 + 1 + 14 = 32, and 53 − 32 = **21** | ✅ enumerated the surviving 21 by hand |
| Ports `8787` and `1234` are `config.yaml:10` and `config.yaml:40` | ✅ both exact |
| This repository's `.gitignore` does **not** mention `.claude/` | ✅ Task 8 has real work to do |
| `feat/` appears at six lines of `../../README.md` — `:156`, `:253`, `:264`, `:267`, `:326`, `:382` | ✅ all six, and `:326`'s hedge does survive orthogonality |
| `../../README.md:236` still says the tracked half is not built; `:153–157` holds the slug rule; `:381` holds the worked example | ✅ |
| `backlog.md:106` and `EPD-004:984` are the other two homes of the decision-18 park | ✅ |
| `link-check.py:222` is `return 1 if check(...) else 0`, with no expected-failures mechanism | ✅ |
| `make test` reports **158** | ✅ 158 passed |

### Finding 1 — the plan's own "98 broken" is stale. It is **105**

`plan.md`'s Task 7 warning says a whole-repository run on this branch reports 98 broken, 16 of them
this branch's own forward citations. Run today: **105 broken, 2 roundabout.**

The extra seven are not drift and not a defect. Four commits landed *after* that warning was written
and each added citations of files Phase 8 will create: `782a3dd` and `c431dab` grew `plan.md`'s own
hit count to 18, and `3dfeb81` and `9628846` gave `status.md` two (`.claude/settings.json` and
`docs/method/` on the same line). The branch's own forward citations are now **23**, not 16:
`plan.md` 18, `implementation-plan.md` 3, `status.md` 2. 82 + 23 = 105.

**This is the plan's own warning proving itself.** It says *"expect this plan's own citations to be
broken until the files exist … this is not drift and must not be 'fixed' by removing the citations"* —
and then quotes a count that a plan still being edited could not hold still. A number written into a
document that is itself still growing is the same class of defect as a number nobody re-derives.

### Finding 2 — Task 17's expected end state is wrong. It is **76**, not 77

`plan.md` predicts 77 broken and 2 roundabout, as 82 minus the five permanent hits Phase 8 resolves.
It also says: *"derive it by running the checker, and if it disagrees with 77, find out why before
editing the number."* Done — and it disagrees.

The docstring's 82 decomposes exactly:

| Group | Count |
|---|---|
| `phase-7-docs-restructure/` plan and notes | 71 |
| The seven "correct and permanent" hits **outside the archive** | 7 |
| `documentation-review-2026-08-16.md` | 4 |

Task 17's table walks the middle group and finds five of the seven resolve — `.claude/settings.json`
×3 and `docs/method/` ×2. It is right about those. **It misses a sixth.**
`documentation-review-2026-08-16.md:732` also cites `.claude/settings.json`, and it resolves the
moment Task 9 lands. It was missed because it sits *inside* the archive, so the docstring counted it
in the group of four rather than among the seven — and the docstring's own sentence says "outside the
archive there are seven", which is true and is exactly what made the fourth copy invisible to a reader
working from that list.

So: **82 − 6 = 76 broken, 2 roundabout**, provided nothing this phase writes adds a hit. Task 17
verifies rather than assumes that.

*The shape of this finding is the phase's subject again. A fact with four homes was corrected in three
of them because the list that enumerated them was scoped "outside the archive", and nobody re-read the
scope.*

### Finding 3 — three stale claims the task list does not cover

Task 5's edit 0 exists for precisely this class: *"fixing a finding in one file while another file
still lists it as open is how a work list stops being trustworthy."* The plan applies that reasoning
to `README.md:381` and misses three siblings.

1. **`backlog.md:98`, "A tracked `.claude/settings.json`".** An open work item that Task 9 completes.
   `backlog.md`'s own header says an item *"is deleted from here when it is done"*. The plan's Task 5
   rewrites two backlog items and adds one, and does not touch this one. **Taken as Task 12a**, beside
   Task 12, which closes out the same fact in `../../README.md`.
2. **`../implementation-plan.md:47`** says of the tracked settings file: *"**Not yet specified — the
   owner has not been interviewed on it**, and the plan's task list says so in place."* False since the
   2026-08-17 interview that produced task group B. Two more in the same section: `:39` calls Phase 8
   *"two small pieces of housekeeping"* when it is three groups, and `:49`'s "done when" says *"both
   documents exist"* when the tier gets four. **Taken as Task 17a.**
3. **`status.md`** carries Phase 8 as "Plan only. No task executed" in its in-flight table and as item
   1 of "What is next". Both are true today and false at the end. **Taken as Task 17a**, in the same
   commit — it is one fact (Phase 8 is executed) with two homes plus a third in `implementation-plan.md`.

**No task is renumbered**, per `plan.md`'s own rule. Two are inserted with letters: **12a** and
**17a**.

### Finding 4 — "every `make` target" and "fourteen entries" disagree

Task 9 says the tracked file holds *"ten that encode how the project is built and tested: every `make`
target, [the ruff pin], [the pytest path], and the two backend documentation domains."* Ten requires
**six** `make` entries. The `Makefile` has **eight** targets — `help`, `sync`, `run`, `check`, `test`,
`lint`, `format`, `clean` — and `settings.local.json` happens to hold exactly six `make` entries
(`test`, `lint`, `format`, `run`, `check`, and bare `make`). So "every `make` target" is really *every
`make` entry that had already accreted locally*.

**Resolved in favour of the decided number.** The owner's settled table says "14 entries" and the
count is load-bearing — Task 10 deletes exactly those fourteen from the local file so each permission
has one home. Fourteen it is, with the six proven-working patterns.

**The gap is named rather than silently accepted:** `make sync` and `make clean` are absent, so a
fresh clone prompts for them. `make sync` is a contributor's *first* command, which sits oddly against
Task 9's own reason for promoting the four `config.yaml` probes ("*is the thing even running?*, which
is a contributor's first question on day one"). Adding `Bash(make sync *)` and `Bash(make clean *)` is
a two-line change and a decision for the owner, not for this phase.

### What the re-derivation did *not* change

The plan's structure, its three groups, and every one of the owner's settled decisions survive
contact. **Task 8 before Task 9** is right for the reason given.

**One ordering hazard, resolved without reordering.** Task 10 deletes `Bash(uvx ty@0.0.14 check src
tests)` and says the deletion *"is only safe because Task 15 records the refusal first"* — but Task 15
is five tasks later, and the deleted file is gitignored, so an interrupted session would lose the
refusal with nothing committed anywhere. Rather than execute out of order, **Task 10 records the `ty`
refusal in this file**, which is committed, and Task 15 gives it its permanent home in `IDM-003`. The
constraint is met at the moment the entry disappears rather than at the end of the phase.

*Written before Task 1. Verified by: `python3 docs/procedures/link-check.py` (105 broken, 2
roundabout), `make test` (158 passed), and a hand enumeration of all 53 allowlist entries.*

---

## Task group A — the method tier and the branching rules

### Task 1 — `IDM-000`

**The plan left one thing to the writer and it turned out to be the load-bearing one: whose method it
is.** The plan says only *"settle it here rather than by accident later; it decides what `EPD-004`
decision 18's extraction copies."* Settled as **the owner's method, evidenced from this repository**,
and the reason to prefer that over "this repository's practice" is that it yields a usable admission
test in one step: **no IDM contains a fact about the router.** Which in turn answers the extraction
question concretely — extraction copies the whole tier **unfiltered**, where `docs/README.md` has to be
copied *and* have its backend rows deleted. A tier that needs no filter is worth more than one that
does, and that is an argument for the test rather than a consequence of it.

### Task 2 — `IDM-001`

Nothing found. Every row of the seven-disagreement table resolved as written, and the two consequences
the plan predicted for row 1 both landed: `docs/` loses its "belonging to no phase" definition, and
decision 15's one-way check generalises to `*/phase-N-*`.

### Task 3 — `CLAUDE.md`

**The plan was right that the reshaped table removes the `feat/`-only inference by itself.** No wording
change to "one phase means one branch and one merge commit" was needed; once the table is organised by
kind of work and the `<prefix>/phase-N-<slug>` line sits under it, the sentence reads as it was
measured to be true.

### Task 4 — `docs/README.md`

**`feat/` went from six lines to two, exactly as the plan's fresh-context review predicted, and `:326`
survives for the reason it gave.** Verified rather than trusted: *"The usual case is a
`feat/phase-N-<slug>` branch that changes `src/`"* is hedged, and under orthogonality the usual case
really is `feat/`. It stays.

**One thing the plan did not anticipate.** Edit 3 changes the sentence introducing the "Where does it
go?" table from *"one of these six rows"* to *seven*. A count in prose immediately above the table it
counts — the cheapest possible instance of a number nobody re-derives, and it would have been missed by
a diff that only read the table.

### Task 5 — `docs/backlog.md`

Nothing found beyond what Task 0 already recorded as Finding 3.1, which becomes Task 12a.

### Task 6 — `EPD-004`

**Writing decision 14's addendum showed the orthogonality change is smaller than the plan makes it
sound.** Decision 14 had *already* been revised on 2026-08-16 to separate *which prefix* from *is this
a phase* — and then left its own table stating the conflation. So the addendum finishes an existing
revision rather than reversing a decision. Only the rejected-plan half is an actual reversal.

### Task 7 — verifying group A

| Check | Result |
|---|---|
| `link-check.py`, whole repository | **105 → 93 broken**, 2 roundabout |
| `make test` | **158 passed** |
| Citations of the two replaced sections, by **title** rather than by path | none stale outside the archive |

The remaining 93 are accounted for: 71 in `phase-7-docs-restructure/`, 4 in
`documentation-review-2026-08-16.md`, 2 permanent deliberate absences, and 16 forward citations of
`.claude/settings.json`, `IDM-002` and `IDM-003` — which Tasks 9, 11 and 15 create. Every
`docs/method/` hit outside those two resolved.

**The title-grep found two stale claims and both are correctly left alone.**
`documentation-review-2026-08-16.md:281` says the "Where does it go?" table *"has six rows"* and `:328`
cites "Naming and numbering" as lines 136–157. Both are now false. Both are **claims in archived
prose**, which `../../README.md`'s editable-paths-yes-claims-no table says are not edited — they record
what was believed then, and a review document's findings are the last thing that should be quietly
updated to match the thing it was reviewing. Recorded here so the next reader knows they were seen
rather than missed.

---

## Task group B — the guardrails

### Task 8 — the `.gitignore` line

`git check-ignore -v .claude/settings.local.json` resolved to `~/.config/git/ignore:1` before and to
`.gitignore:253` after. That one command is the whole of the task's effect, and it is the only way to
see it — the file's *status* is identical either way, which is exactly why the gap survived.

### Task 9 — the tracked `.claude/settings.json`

Written as specified: **14 allow, 3 deny.** The deny is three entries rather than two because "the
`cat` form" has two spellings a session would actually type, `cat .env` and `cat ./.env`, and an
exact-match rule has to name both. See Finding 4 in Task 0 for the `make sync` gap.

**What the exact-match deny is and is not.** It stops the reflex, not a determined path — `sed`, `head`,
`python3` and `env` all still read the file. That is not a weakness in the rule, it is the point of
decision 19's argument: enforcement that tries to cover every route needs a shell parser and produces
false positives, and the written rule is what does the real work. Named in `IDM-002`.

### Task 10 — the prune. **53 → 21, and it produced no commit**

The file is gitignored, so this record is the only evidence the task happened. `git status` was clean
after the edit, which is the expected outcome rather than a missing one.

| | Count |
|---|---|
| `settings.local.json` before | **53** |
| Removed | **32** |
| `settings.local.json` after | **21** |
| Tracked `settings.json` | 14 |
| **Effective merged allow set** | **35** |
| Overlap between the two files | **0** — verified by set intersection, not by eye |

The 32, in the plan's four groups: **15** fossils and duplicates, **2** that repealed a written rule
(`lms load *`, `lms unload *`), **1** that was a refusal (`uvx ty@0.0.14 check src tests`), and **14**
that moved to the tracked file. Every one was present at the shape the plan quoted; the arithmetic held.

**Zero overlap is the invariant worth naming**, because it is what "each permission has exactly one
home" means operationally, and it is checkable in one line. It also means a mistake in Task 9 cannot
hide: the fourteen promoted entries are now covered *only* by `settings.json`, so Task 14's check 1
either passes or produces a prompt for `make test`.

**The `ty` refusal, recorded here at the moment its allowlist entry was deleted.** `ty` was tried and
rejected: it produced warnings without useful information. The entry was pinned like policy
(`uvx ty@0.0.14`) and absent from both the `Makefile` and `pyproject.toml` like a fossil, which is why a
first pass read it as an unresolved question — it is neither. This paragraph exists because the deleted
file is gitignored and Task 15 is five tasks away; `IDM-003` is its permanent home, and this is the
committed record that closes the window in between.

### Tasks 11, 12, 12a, 13

`IDM-002` gained one thing the plan did not specify, found by Task 14 and folded back in — see check 6
below. Nothing else found. *(The plan says Task 14 is "four checks" and then lists six. Harmless, and
noted because a count nobody re-derives is this repository's subject.)*

### Task 14 — driving group B. **Four pass, one passes differently, one is not testable here**

| # | Check | Result |
|---|---|---|
| 1 | `make test` reports 158, no prompt | ✅ **158 passed** |
| 2 | The `.env` deny fires | ✅ **refused** — *"File is in a directory that is denied by your permission settings"*, no contents exposed |
| 3 | `.env.example` still readable | ✅ **readable**, all 11 lines |
| 4 | No new prompts, and **`lms load` prompts** | ⚠️ **half testable** — see below |
| 5 | `git check-ignore -v` resolves to this repository's `.gitignore` | ✅ `.gitignore:253` |
| 6 | `/permissions` shows the effective merged set | ⚠️ **substituted** — see below |

**Checks 2 and 3 are the pair that matters and they pass together.** The trap the plan named is real:
a globbed deny would have taken `.env.example` with it, and `.env.example` is the file that documents
which key each backend needs. Driving both is what distinguishes "the deny works" from "the deny works
and did not overreach". The plan predicted check 3 was the one most likely to be skipped because the
file feels unimportant; it is the one that carries the information.

**Check 4 is not testable in this session, and saying so is the honest result.** `lms load --help` — the
help form, which loads nothing — ran **without a prompt**. The reason is not a mistake in Task 10: the
merged allow set was enumerated and contains no rule matching `lms load`, `lms unload` or `uvx ty`.
**This session is not enforcing the allowlist for Bash at all** — demonstrated by `mkdir -p docs/method`,
which appears in neither file and ran silently. Allowlist *absence* therefore cannot be observed from
inside it. **The deny half was observable**, because a deny is enforced regardless of mode, which is
why check 2 is real evidence and check 4's second clause is not. The verifiable part — that no allow
rule matches — was verified mechanically:

```
'Bash(lms load *)'                     present in merged set: False
'Bash(lms unload *)'                   present in merged set: False
'Bash(uvx ty@0.0.14 check src tests)'  present in merged set: False
```

**Check 6 could not be run as written, and the substitute found something.** `/permissions` is an
interactive slash command; a session cannot invoke it and read the result back, so the merge was
computed from the two files instead: **14 tracked + 21 local, overlap 0, effective allow 35**, plus 3
deny. *That is a defect in the plan rather than in the work* — it specifies a verification step that only
a human at the terminal can perform, and says nothing about what to do when the executor is not one.
`/permissions` remains the right tool and `IDM-002` still names it; the owner should open it once.

**What the substitute found, and it is worth more than the check was.** A set intersection of zero is
**not** the same as no overlap. `Bash(uvx ruff *)` sits in the local file and
`Bash(uvx ruff@0.16.1 format --check src tests)` in the tracked one; they intersect in nothing, and the
glob already grants any ruff version — so the tracked entry, whose whole purpose is to encode the pin
`CLAUDE.md` calls non-negotiable, **grants nothing that was not granted anyway.** It is documentation of
policy, not enforcement of it. Both are kept, and the distinction is now stated in `IDM-002` where
"the two files must not overlap" is defined, because the one-line check I used to verify that rule would
have missed the one case that matters.

**One defect found in passing and fixed.** `.env.example:5` cited `docs/anthropic-auth-check.md`, which
moved into `docs/procedures/` during the restructure. **A whole-repository `link-check.py` run cannot
see it**: `check()` globs `*.md`, so every citation in `.env.example`, `config.yaml`, the `Makefile`,
`pyproject.toml` and `src/` is unchecked unless the file is named on the command line. Repointed — it is
a path, not a claim. The rest were swept at the same time and are clean, which is why this is one line
rather than a work list.
