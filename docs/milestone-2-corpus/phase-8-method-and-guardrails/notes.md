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
