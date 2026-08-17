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

## Tasks 3 and 4

*(recorded as they complete)*
