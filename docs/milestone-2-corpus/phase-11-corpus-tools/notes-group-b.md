# Phase 11 — Group B: the CLI restructure

**Tasks 8–10, all on 2026-08-26.** The subcommand skeleton with bare invocation still serving; the
move of `check`, `train-dict`, `tune-dict` and `extract` across with `verify-archive` split out; and
the CLI's first test file.

**This is the first group in Phase 11 to change `src/`.** Split out of `notes.md` on 2026-08-26, per
`../../README.md`'s group rule; `notes.md` remains the entry point.

---

## Tasks 8 and 9 — the CLI becomes subcommands, 2026-08-26

**The first `src/` change in this phase.** `serve`, `check`, `train-dict`, `tune-dict`, `extract` and
`verify-archive`; bare invocation still serves; every old flag deleted rather than aliased.

### The defect that would have shipped silently, and how it was caught

**A subparser's `--config` with an ordinary default overwrites the top-level value after parsing.**
`ilirium-llm-router -c other.yaml serve` would have loaded `config.yaml` — **the flag accepted, the
flag ignored, and no error anywhere.** `argparse.SUPPRESS` fixes it: the attribute is set only when
the option actually appears.

**Measured in both directions rather than asserted in a docstring**, because a claim about argparse is
exactly the kind that reads as obviously true and is not:

```
SUPPRESS (what cli.py uses)    -c other.yaml serve -> other.yaml
ordinary default (the trap)    -c other.yaml serve -> config.yaml
```

*The instrument lesson applied to a docstring. Writing "SUPPRESS is not a style choice" costs nothing
and proves nothing; the counterfactual is what makes it a fact, and it took four lines.*

### `verify-archive` over the whole live corpus — 1793 blobs, 0 failed

**Driven, not tested.** `CLAUDE.md` says green tests are not evidence, and the tests here are all
`tmp_path` fixtures. → register §8 for the table.

**Every blob in the live corpus opens and verifies against the digest in its own filename.** That is
Phase 10's promise driven at scale for the first time — it had been driven on one day folder, at 280
blobs, and now on four at 1793.

**It also discharges task 19 ahead of its group**, and the task is left visible rather than struck so
the ordering stays legible.

***And it caught a ratio going stale, which no note in this repository had recorded before.***
`2026-08-24` read **2.815×** at 280 blobs mid-day and reads **2.553×** at 580 blobs complete. Same
folder, same command, same absence of a dictionary. **Every earlier warning here is about counts
moving under a measurement; a count that has gone stale is at least visible as a count. A ratio never
looks stale.**

### Four decisions inside task 9 worth naming

1. **Every day is attempted even after one fails.** A run that stopped at the first bad folder would
   report the first problem and hide the rest — and the question `verify-archive` answers is *"does
   all of it open?"*, not *"is there a problem?"*.
2. **The grand-total block prints only when more than one day was given**, so a single-day run prints
   exactly what `--extract` always did and the two forms need not be read differently.
3. **`--project-name` without `--format jsonl` is a parse error**, reported through the *subparser* so
   the usage line is `extract`'s rather than the program's. `--project-name` defaults to `None` rather
   than to `corpus`, because *"was it given?"* has to stay answerable for that check to exist at all.
4. **`extract` parses fully and refuses to run**, returning 2 and naming the tasks that will build it.
   A command that parsed and then quietly did nothing is the same failure this phase exists to avoid
   one level up.

### One measurement here was the instrument's fault, again

Checking exit codes, `echo "exit=$?"` after a pipe into `tail` reported **0** for a run that had
failed. **`$?` was `tail`'s.** Re-run without the pipeline: missing folder **1**, good folder **0**,
`extract` stub **2**, deleted flag **2** — all correct.

*Third instrument error in one session — the `awk` byte-count, the `1913` sha256 "secrets", and now
this. All three were caught because the number looked wrong, and none by anything that failed.*

## Task 10 — the CLI's first test file, and three mutations to prove it can fail, 2026-08-26

**`tests/test_cli.py` is new, and the point worth recording is that it had to be.** The CLI had **no
test file at all**. It was reached only sideways — two tests in `test_dictionary.py` import
`_with_overrides`, one in `test_corpus.py` shells out — so **the surface this phase restructured had
never been described anywhere that a change would break.** 310 → **337**.

### The tests were mutated, because a test that cannot fail is this phase's own recorded defect

Task 22's `❓` check *"could not fail"* and the forward review found it. **Writing 27 green tests and
reporting the number would be the same thing one level down**, so three mutations were applied to
`cli.py` and reverted:

| Mutation | Result |
|---|---|
| `argparse.SUPPRESS` → an ordinary default | **1 failed**, `test_the_config_flag_wins_from_either_side_of_the_subcommand` |
| the `--project-name` guard deleted | **1 failed**, `test_project_name_without_jsonl_is_an_error_not_a_silent_no_op` |
| `--out` no longer `required` | **1 failed**, `test_out_and_format_are_both_required` |

**Each killed by exactly one test, and `cli.py` restored byte-identically afterwards** — confirmed with
`git diff --stat`, which came back empty. *This is not task 23: that one is mutation testing on the
**converter**, and it is still owed.*

**One test is deliberately two assertions where one would look sufficient.** The config-flag test
checks `-c other.yaml serve` **and** `serve -c other.yaml`. **Only the first fails without
`SUPPRESS`** — a test written with the second alone would have passed against the defect, which is the
whole failure mode being guarded.

### A 101-character line was committed in task 8 and `make lint` passed it

**`CLAUDE.md` warns that `make lint` cannot see column width** — `E501` is not in ruff's default set
while `pyproject.toml` sets `line-length = 100`. **The warning stopped being theoretical inside this
session.** Six over-width lines across `cli.py` and `test_cli.py`, one of them already committed.

*Task 2 checked added-line width on purpose and reported zero; task 8 did not, and task 8 is the one
that leaked.* **Fixed here, and the underlying gap is in `for-the-owner.md`** with the measurement that
makes it actionable: `--select E501` reports **23 errors in 9 files**, all prose rewraps, so the fix is
bounded — but it is a tooling change and `IDM-003` owns those.

### Two rewraps in a row pushed a *different* line over

Fixing six over-width lines by rewrapping produced two new ones, because rewrapping moves words onto the
following line. **Caught only by re-running the check after the fix.** *A fix that is not re-measured
is a hypothesis, and this one was wrong twice before it was right.*
