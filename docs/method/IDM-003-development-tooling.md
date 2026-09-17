# IDM-003 — Development tooling: the formatter pin, and the type checker that was refused

**In force 2026-08-17.** Two decisions that already existed and had no home: the ruff pin's reasoning
lived only in `CLAUDE.md`, and `ty` was tried and refused with the refusal recorded nowhere at all.

---

## The formatter is pinned, and the pin has two halves

| Where | What |
|---|---|
| `pyproject.toml`, `[tool.ruff]` | `line-length = 100` |
| `Makefile` | `RUFF ?= ruff@0.16.1` |

`ruff` is fetched on demand by `uvx` rather than installed as a dependency — **but it is pinned
anyway**, and those two facts are not in tension. An unpinned formatter reformats the whole repository
the day it changes its mind, and the bump then arrives disguised as somebody's feature branch.

### Why both halves exist, and it is not tidiness

**It happened.** An unpinned ruff at its default 88 columns once rewrote every file it was pointed at.
The codebase is written at 100 columns and always has been, so the reformat touched everything, and it
buried the real change in progress. That made `make format` unsafe to run and meant any phase branch
touching it carried a pile of unrelated churn.

**And `make lint` did not object**, which is the part worth remembering. Line length is **`E501`**, and
`E501` is **not in ruff's default rule set** — so `ruff check` is silent about column width whatever
`line-length` says. The setting governs the *formatter* alone. A session that runs `make lint`, sees it
pass, and concludes the formatting is fine has learned nothing.

**100 is measured rather than chosen.** The widest lines here are 100 characters, and the dozen that
exceed it are comments and docstrings, which the formatter does not rewrap.

### How to try a version

```
make format RUFF=ruff@x.y.z
```

That tries a new version **without committing to it**, and **the diff it produces is the argument for or
against the bump** — not the changelog, and not the version number.

**An accepted bump goes in its own commit.** `d1def4f` (*"changed: reformatted the repository at 100
columns"*) is the precedent: 13 files, nothing else in the commit. And it is **checked by comparing each
file's AST before and after**, rather than by trusting that formatting only moves whitespace. That check
exists because the assumption is exactly the kind that holds until it does not, and a formatter diff is
too large to read line by line.

**Never bump the pin as a side effect.** That rule is restated in `CLAUDE.md` — it is a thing a session
does confidently and wrongly, and it has already happened here once — and this file is where its
reasoning lives.

### The pin is written in three places and enforced in none

Worth knowing before assuming the allowlist protects it. `.claude/settings.json` carries
`Bash(uvx ruff@0.16.1 format --check src tests)`, which looks like enforcement and is not:
`Bash(uvx ruff *)` in the local half already grants any version. See
`IDM-002-harness-configuration.md`, "The two files must not overlap" — a glob subsuming an exact entry
is the case a set intersection cannot see. **What stops a bump is the written rule and the review of the
diff.** Nothing mechanical does.

## `ty`: tried and refused

**`ty` was tried and rejected. It produced warnings without useful information.**

The evidence it left behind was `Bash(uvx ty@0.0.14 check src tests)` in the permission allowlist —
pinned like policy, absent from both the `Makefile` and `pyproject.toml` like a fossil, and actually
neither. The entry was removed in Phase 8's Task 10, and **the refusal is recorded here because deleting
it silently would leave a project with no type checker and no explanation.**

**A refusal is a first-class outcome.** `../README.md` says so of the review phase — *recording that
something was considered and refused is what stops it being re-proposed every milestone by the next
person reading the same surface signal* — and a repository with type hints throughout and no type
checker is a very strong surface signal. Without this section the next session adds one and re-runs the
same experiment.

**What the refusal does *not* establish** is that static analysis beyond ruff is worthless. `ty` was
version **0.0.14** at the time, which is early enough that the result may say more about the tool than
about the idea. That is why it is a refusal with a reason rather than a policy, and why
**`BKL-0031`** in `../backlog.md` insists the next attempt states what it expects to catch
**before** it runs.

## Provenance

- **The ruff pin** — `CLAUDE.md`'s "Style"/formatter paragraph held the rule *and* the reasoning until
  2026-08-17; the rule stays there and the reasoning moved here. The two comment blocks in `Makefile` and
  `pyproject.toml` are kept: they are where somebody editing those files will read them.
- **`ty`** — never documented anywhere before this file. Found in the allowlist during Phase 8's review,
  `../milestone-2-corpus/phase-8-method-and-guardrails/`.
