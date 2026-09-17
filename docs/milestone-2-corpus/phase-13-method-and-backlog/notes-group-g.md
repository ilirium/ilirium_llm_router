# Phase 13 — Group G, close

**Tasks 25–28.** *Written while working.*

---

## Task 25 — the register check, and it was vacuous on its first run

**`evidence/register-check.py` exists and exits 0.** It checks ten things against the artefacts
rather than against the register's prose: the `❓` column, every named document and path, the folder
slug, the `BKL` scheme read off both files, the one item shape, the metadata line carrying no id,
the five statuses and eight category tokens counted in the script that owns them, the `done`-only
lifecycle, the eight table columns, and `for-the-owner.md`'s kinds, levels, heading shape and
contiguous numbering.

***It passed on its first run and the pass was worthless.***

**The `❓` check skipped the rows it exists to find.** The register's header row is
`| Name | Value | ❓ |`, and the first version skipped any row ending `❓ |` as "the header" — which
is exactly what a row carrying a **live** `❓` looks like. A planted `❓` passed.

***This is the same failure class as the heading-count assertion the jobs-done review found in
`backlog-index.py`***: a check whose exclusion swallows its own subject. **Two instruments, written
eight days apart, both passing while testing nothing.** *Neither was found by reading. Both were
found by making the thing they check go wrong.*

**The header row is now identified by its cells** — `["Name", "Value", "❓"]` — and only by those.

## And the mutation harness was broken, which looked identical to a clean pass

**Seven mutations were run and all seven "survived".** One of them deleted an entire method
document; the check reported the register holding. **The check was right and the harness was
broken** — the shell function's here-document never executed the mutation, so every run scored an
unmutated tree.

***This repository had already written that trap down.*** `notes-group-e.md`, task 17: *"an eighth
attempt failed because the mutation script errored rather than the check passing — recorded because
'the mutation did not apply' and 'the test did not fail' are the same output at a glance."* **It was
recorded, and it still happened here eight days later.** *A warning in a notes file is not a
control.*

**The harness now asserts the mutation applied before trusting the result**, and reports the two
outcomes in separate columns. **Rewritten in Python rather than shell**, because the failure was a
quoting problem that produced no error anybody saw.

| Mutation | Killed by |
|---|---|
| an item cut out | the id count — 37 against the register's 38 |
| a heading demoted to prose | the id count |
| a `for-the-owner` number made 55 | the contiguity check |
| a category token dropped from the script | the eight-token comparison |
| the `See` column removed from the header | the column-order check |
| a `done` item left in `backlog.md` | the lifecycle check |
| a method document deleted | the existence check |
| a metadata line given back its id | the shape check |

**Eight mutations, eight kills, each verified as applied.** *That is what the first run's "pass" was
claiming and had not earned.*
