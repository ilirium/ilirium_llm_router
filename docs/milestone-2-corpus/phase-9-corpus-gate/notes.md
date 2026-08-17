# Phase 9 — decide EPD-003, and run its gate: notes

Branch: `docs/phase-9-corpus-gate`, off `main` at `97f6563`, **not yet merged.** Per
`../../method/IDM-001-git-branching.md`, filling that hash in is the one edit this note takes after
being written — and leaving it reading "not yet merged" after the branch is gone is the defect four
Milestone 1 phase notes committed.

Written **while the work is happening**, task by task, rather than assembled afterwards.

**`evidence/` does not exist yet and may stay small.** The gate's input — captured bodies and the
dictionaries trained on them — **cannot be committed**, on `EPD-003`'s own rule: a body store is *"not
committable, not by redaction and not by placeholder mapping"*, and a `zstd --train` dictionary is a
concatenation of verbatim substrings of its samples, so it inherits that rule exactly. What can be
frozen is the derived table and the script. `../../README.md`'s phase template allows an absent
`evidence/`; this note says why in advance rather than after.

---

## Task 2 — the re-derivation, run **before** Task 1

`../../README.md`: *a phase's first act is to re-derive its own plan against what is now known.*
Five of Milestone 1's and 2's phases found their plan wrong on contact.

**This phase ran the re-derivation before publishing its plan rather than after**, which is a
departure from Phase 8's shape — that phase re-derived at "Task 0", against a plan already committed.
Here the plan did not exist yet: the phase opened with an interview, and five findings landed during
it. So the findings **shaped** the task list instead of correcting it, and no task numbers were spent
on work that turned out to be wrong.

The trade is worth naming, because it is not free. Phase 8's shape produces a visible record of a plan
being wrong, which is evidence about planning itself. This shape produces no such record — the wrong
version was never committed. **What is lost is the diff; what is gained is four fewer lettered
insertions.** The findings themselves are in `plan.md`, "What the re-derivation found, before Task 1".

### What was checked and passed

| Claim | Verified |
|---|---|
| `make test` reports **158** | ✅ 158 passed, 1 warning, 0.60s |
| `procedures/link-check.py` reports **68 broken, 2 roundabout** | ✅ **run, not predicted** |
| Working tree clean, `main` at `97f6563` | ✅ |
| `zstd` present, 1.5.x from Homebrew as `EPD-003`'s Evidence assumes | ✅ 1.5.7 |
| `logs/` is gitignored, so a capture directory under it needs **no new rule** | ✅ `.gitignore:228`; `git check-ignore -v` confirms it covers `logs/corpus-gate/*.dict` |
| `--maxdict` default | ✅ **112,640 bytes**, from `zstd --help` |
| `config.yaml` stats rotation | ✅ `max_bytes: 5242880`, `backup_count: 10` |

**The link-checker count was run rather than predicted.** `../../status.md` carries that as a standing
warning, and Phase 8 proved twice that reading the docstring gives the wrong answer. Predicting it
here would have been the third time.

### The five findings

Recorded in full in `plan.md` rather than duplicated here. In one line each:

1. **The capture is not discharged.** `../implementation-plan.md:103` hedged that step 3 *"may already
   be discharged"*; it is not. `../../captures/` holds **one** body, and one body cannot exercise a
   cross-body dictionary. The gate is a live capture plus twenty minutes of `zstd`, not twenty minutes
   of `zstd`.
2. **`EPD-003`'s gate, run as written, trains on its test set** — and the fix, a held-out split, turns
   out to measure the static-versus-session-local decomposition directly rather than merely adding
   rigour.
3. **`--maxdict` defaults to 112,640 bytes and the static preamble is ~110 KB** — so a single-point run
   could not tell "a dictionary cannot recover this" from "the dictionary was capped below the thing it
   needed to hold".
4. **`calls.csv` expires**, so `EPD-003`'s plan to use it as the corpus's join table would leave bodies
   outliving their own index. **Independent of the gate** — true whatever the compression numbers say.
5. **Concurrency dilutes a dictionary**, and the capture as first planned would have hidden it.

**Findings 3, 4 and 5 came out of the opening interview rather than out of any document**, and two of
them are about `EPD-003` being wrong in ways the gate would never have caught. Finding 4 in particular
is a storage-design defect surfaced by a compression question — recorded here because it is the kind
of thing that is expensive to rediscover.

---

## Task 3 — the decision, and the sweep it grew

`EPD-003` → **partly accepted**, `EPD-000`'s vocabulary for *"one named piece was accepted on a stated
date; the rest is still a proposal"*. Open question 1 decided; open question 7 struck as stale, since
it asks whether capture lands before or after Phase 3 and Phase 3 shipped as `cc65aed`.

**The task as published named three edits and took five.** `../../README.md`: *"When you record a
finding, sweep the other documents for claims it makes stale. That sweep is expected, not optional —
it is half of what filing a finding means."* So the sweep is part of the task rather than a new one,
and no task letter was spent.

| Swept | Was |
|---|---|
| `EPD-000`'s index row | `proposal`, waiting on *"a decision on the fine-tuning goal"* |
| `CLAUDE.md`'s EPD table | same, and `CLAUDE.md` is auto-loaded — a stale row there is the "acts confidently and wrongly" case its own admission test is about |
| `../../backlog.md`'s "Decisions waiting on a person" row | **struck, not deleted.** What remains of `EPD-003` is its gate, which is *work*, and that section's premise is *"None of these is blocked on work"* |

**Two findings were marked in place inside `EPD-003` rather than only in this phase folder** — the
gate training on its test set, and `calls.csv` being unable to serve as the join table. A finding
recorded only next to the phase that made it leaves the wrong document still saying the wrong thing to
whoever opens it next.

## Task 4 — the in-flight branch, and three stale claims

`../../status.md` gains the branch row. Two things worth recording about the edit:

**"Where we stopped" was already over its own limit.** The section's rule is that it gets its own file
past ~30 lines; it was at ~44 before this task. So Phase 8's and Phase 7's closed narrative was cut to
two sentences — their permanent records are their phase notes, and `status.md` is state. Adding Phase 9
on top without cutting would have pushed it to ~60.

**The task also took `../implementation-plan.md`,** which was stale in three places the moment Task 3
landed: `EPD-003` described as *"still a proposal"*; step 3 of the opening playbook described as *"may
already be discharged"*, which Finding 1 disproves; and Phase 9 marked *(outline)* when its plan is now
published in full. Corrected **in place with dated notes**, not rewritten — that file is a live
milestone plan rather than a frozen phase note, and Phase 8's Task 17a set the precedent for correcting
it in place.

**The central-claim blank survives the decision, and this is worth being explicit about.** `EPD-003`
being partly accepted might look like grounds to name the milestone's claim now. It is not: the half
that was decided is not the half a claim would rest on. The storage question is what the milestone is
*about*, and it is open until the gate runs.

---

## Paused here, deliberately

**Group A is complete and nothing has touched the machine.** No body captured, no `src/` patched, no
measurement run, no API call made. `git diff main -- src/` is empty.

Task 6 needs the owner's go-ahead in its own right: it patches `proxy.py`, runs the router, and makes
real API calls. `CLAUDE.md`'s working agreement — *"Ask before touching the machine … consent for one
is not consent for the next"* — is why that is a separate ask rather than covered by the go-ahead that
opened this branch.

### Verified by, Group A — run 2026-08-17, after Task 4's commit

| Check | Result |
|---|---|
| `make test` | **158 passed**, 1 warning, 0.68 s |
| `procedures/link-check.py` | **68 files, 68 broken, 2 roundabout** — the broken count **unchanged** from the fork |
| `git diff main --stat -- src/` | **empty** — the `docs/` prefix still holds |
| `git status --porcelain` | clean; no captured body or dictionary exists yet to leak |

**The link-checker's file count rose 66 → 68 while its broken count did not move**, and that is
checked rather than assumed: `link-check.py` reports **zero** hits from `phase-9-corpus-gate/`, and the
only `epd/` hits are the two that predate this branch. So the two new documents cite nothing that does
not exist, and nothing edited in Tasks 3–4 broke a path.

**That differs from Phase 8, whose plan contributed 23 forward citations** to files it intended to
create — a false-positive class `../../backlog.md` records as recurring. This plan has none, because
Group B's and C's outputs live under `logs/`, which is gitignored and therefore never cited as a
repository path. Not a virtue of this plan; a property of where its outputs go.
