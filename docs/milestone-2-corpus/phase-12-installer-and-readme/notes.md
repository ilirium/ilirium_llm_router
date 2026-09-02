# Phase 12 — notes

**Branch:** `feat/phase-12-installer-and-readme`, forked from `main` at `5cdc1c9`.

*Entry point for the phase. Group notes split out as `notes-group-<letter>.md` once groups have work
in them, per `../../README.md`.*

**Where execution stopped: groups A, B and C are done. Group D is one task in — task 11 is done,
12 to 14 are not — and Group E has not started.** *This line replaced "Nothing has been executed
yet" on 2026-09-02, which was true when the file was created and false after task 1 — **in the
phase's entry point, the first thing the next session reads.** It was found by the owner asking
whether anything needed checking before the session closed, not by the sweep: the grep looks for
markers of work *not* done, and this was a claim that *nothing* was done.*

## Why this branch changes `backlog.md` and `IDM-001`

**2026-09-02, on the owner's instruction, and it is a rule change rather than phase work.**

The phase's planning produced a backlog item — that the group-notes rule is invisible at the moment
it applies. It was filed on a new `docs/` branch, on `IDM-001`'s authority that work not belonging
to a phase does not ride on that phase's branch.

**The owner reversed that, and the reasoning is now in `IDM-001`:** adding a backlog item is **how a
phase declines scope**, so it belongs on the branch that declined it. The rule being applied was
about *pre-empting a later phase's work*; a backlog item is the record that work is **not** being
done, which is the opposite thing.

`docs/group-notes-visibility` was deleted unmerged, its one commit's content moved here. It was
never described in `branch-index.py` and never reached `reference/branches.md`, which is the only
shape in which a branch here may be deleted at all.

*Recorded in this phase's notes because a reader will otherwise ask why a `feat/` branch amended the
method tier. The rule itself lives in `../../method/IDM-001-git-branching.md` and is not restated
here.*

---

## The group notes

**Each task group's notes go to `notes-group-<letter>.md`**, per `../../README.md`; this file keeps
what belongs to no group and stays the entry point. The plan has five groups — **A** open the phase,
**B** establish what already works, **C** the installer, **D** the documents, **E** close.

| File | Covers | Written |
|---|---|---|
| `notes-group-a.md` | Group A — open the phase | 2026-09-02 |
| `notes-group-b.md` | Group B — establish what already works | 2026-09-02 |
| `notes-group-c.md` | Group C — the installer | 2026-09-02 |
| `notes-group-d.md` | Group D — the documents | 2026-09-02 |

**Deliberately no placeholder rows, and this is not tidiness.** At Phase 11's merge this index
carried `| *(none yet)* | Groups D, E, F | not started |` **directly beneath two rows naming files
for two of those groups**, all marked complete. The owner found it; `IDM-001`'s sweep could not,
because its pattern required parentheses the row did not have. A row that exists before its file
does is a placeholder waiting to go stale — **so a row appears here when the file appears**, and the
groups are named in the sentence above instead, where nothing can rot.

---

## The forward review, 2026-09-02

**Run under `../../method/IDM-004-reviewing-unexecuted-work.md` before task 1**, on the owner's
instruction, against `plan.md` at commit `80914a0`. Charter: `review-charter.md` beside this file.
Two runs in parallel — the author, and a fresh-context agent given the charter and nothing else.
Neither fixed anything; this is the reconciliation.

**It paid for itself on one finding.** The plan asserted that an installed router reads `.env` from
the working directory. **It does not**, and the author had asserted it twice — once in the plan and
once to the owner — without reading python-dotenv.

### What the two runs found

| | Author | Cold |
|---|---|---|
| Task 8 says "eight sections" | ✓ | ✓ |
| `.env` is not read from cwd | — | **✓** |
| No `--version` flag exists | — | **✓** |
| `init` would fail before it runs | — | **✓** |
| `status.md` has no in-flight entry **now** | partial | **✓** |
| Branch index regeneration missing from task 11 | — | **✓** |
| `README.md`'s "158 tests" is stale | — | **✓** |
| `captures/README.md`'s index gains no row | — | **✓** |
| `cli.py:38–42` is off at both ends | — | **✓** |
| Register omits names that go on disk | 1 of 4 | **4 of 4** |
| Exit criteria need "a machine with no checkout" | **✓** | **disagreed** |
| `notes.md` and `evidence/README.md` uncreated | ✓ | ✓ (as "no artefact named") |
| B→C ordering rationale unwritten | ✓ | — |

**The cold run found more, and found the expensive ones.** That is the protocol working as
`IDM-004` says it should: the author holds the reasoning and can see contradictions with what was
decided; it cannot see its own blind spots, and the two largest findings here are blind spots rather
than inconsistencies.

### The finding that justified the review

**`load_dotenv()` does not search the working directory.** Verified independently by the author
after the cold run reported it, per `IDM-004`'s rule that a refutation is re-checked before it is
accepted.

`dotenv/main.py:418` calls `find_dotenv()` with no arguments. `find_dotenv` uses `os.getcwd()`
**only** when `usecwd or _is_interactive() or _is_debugger() or sys.frozen` — none of which holds
for an installed console script. Otherwise it walks `sys._getframe()` back to the **caller's** file,
takes that file's directory, and `_walk_to_root` climbs from there to `/`.

**In the repository this has always worked by accident.** The caller is
`<repo>/src/ilirium_llm_router/cli.py`, so the walk reaches `<repo>/.env` on the third step.
**Installed as a `uv` tool the walk starts inside uv's tool directory**, climbs through it and
`$HOME` to `/`, and never looks at the working directory at all — while a `~/.env`, if one existed,
would be picked up instead.

**Why it is quiet, which is what makes it worth the review rather than a test.** The shipped
`config.yaml` uses `forward` and `strip`, so no key is required and nothing fails. It bites only an
`inject` backend, through `config.py:260`, on a machine where nobody is watching.

### Two claims the author made and got wrong

Recorded rather than quietly corrected, because both were stated to the owner as fact.

1. **"`--version` already exists in `cli.py`"** — said while putting the install-mode options. It
   does not. `cli.py` has five occurrences of `version` and **none is an `add_argument`**; the only
   version output is `print()` inside `_report`, which runs *after* `load_config` succeeds. Driven:
   `ilirium-llm-router --version` exits **2** with `unrecognized arguments`. So on a fresh machine
   there is no invocation that prints the version and exits 0 — and "confirm the install worked" is
   the first line of any quick start.
2. **"`.env` is read from cwd"** — above.

**Both were single-source claims the author checked once**, which `IDM-004` names as the weakest
verification available. The charter listed nine claims to re-verify; the two that were wrong were
both on that list, which is the charter doing its job.

### A third the review exposed that neither had stated

**An `init` added as an ordinary subcommand fails before it runs.** `cli.py:40–43` has exactly two
early returns — `verify-archive` and `extract`. Every other branch reaches `load_config` at line 46
and `_report` at line 51. So `ilirium-llm-router init`, in the empty directory it exists to serve,
would print `error: Config file not found: config.yaml` and exit 1. **The command whose whole
purpose is to work without a config would have required one.** Task 3 establishes exactly this
pattern for the corpus tools and task 4 does not reference it.

### Where the runs disagreed

**One place, and it is about wording rather than correctness.** The author flagged two exit criteria
as unmeetable — *"on a machine with no checkout"*, *"with no repo on disk"* — because there is one
machine and it has three worktrees. The cold reader read task 5's criterion as *"unambiguous and
good"*.

**Both are right about different things, and that is the finding.** The intent is legible — the cold
reader had no trouble with it — and the literal criterion cannot be arranged without deleting the
repository. So it is a wording fix and not a design gap, which is a smaller finding than the author
filed and a real one the cold reader passed over.

### Resolved without asking, because they are facts rather than decisions

- **The `body_max_bytes` caveat has two readings and one is refuted by the source.** Bodies over the
  cap are **discarded, not truncated** — `corpus.py:130`: *"a prefix labelled as a whole body is
  worse than a hole"*. So the README must say that a long session's later calls go **unstored**,
  never that bodies are cut short. The cold reader filed this as a question and did not resolve it
  by inference, which was right; the source settles it. - **Milestone 2 is four phases in.**
  `status.md:35` says four, `status.md:87` and `:117` say three — the latter two written before
  Phase 11 merged. Four is correct: 8, 9, 10, 11. *The contradiction in `status.md` is executed work
  and out of this review's scope; it is raised for the owner separately.*

### Refused, with the reason

*Nothing yet. Every finding above was accepted.* **This section stays** — `IDM-004` says a refused
finding is recorded with its reason or it is re-raised by the next review.
