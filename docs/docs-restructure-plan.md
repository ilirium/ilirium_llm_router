# Documentation restructure — the migration plan

Written 2026-08-15 on `docs/milestone-boundary-restructure`, **extended 2026-08-16. The structure was
decided on the 15th and extended on the 16th; nothing here has been executed yet.**

The shape and the argument for it are in `docs/epd/EPD-004-documentation-structure.md`, whose six
forks are now answered — the tier split accepted, `Design decisions` moving out whole, the backlog
split into its own file, the capture at `docs/captures/`, no numeric prefixes, and the reference tier
starting at **seven** files. Two documents were added by those decisions and are built here:
**`docs/README.md`**, the manual, and **`docs/backlog.md`**.

**The 2026-08-16 round changed six things in this document**, all recorded in place below and all
traceable to `EPD-004` decisions 9–20: the reference tier gains `backend-anthropic.md`;
`Anthropic model IDs` leaves `CLAUDE.md`; three archive folder slugs change to match their branch
names; `docs/README.md` grows the phase template, the branch convention and the opening playbook;
the nine migrating memories become a step; and a **fifteenth commit** writes the closing playbook from
what this work actually cost.

This file is the mechanical half: what moves where, what breaks when it does, and in which order to
do it so that a mistake is recoverable.

Read the eight silent breakages first. **All eight** fail without an error message — the section is
named for that — and two have already fired once in this repository. *An earlier version said "six of
them", which never identified the other two and does not survive reading the list.*

## Scale

Measured 2026-08-15 on `docs/milestone-boundary-restructure` at commit `51b857b`.

| | |
|---|---|
| Files under `docs/` | **67 present, 52 tracked** at `51b857b` — of which this document and `EPD-004` are two of each. Before it: 65 / 50. **Today: 68 / 53**, after `de4e28a` added the handoff |
| Untracked-but-present | **15 files**: `phase-3-verification/runs/` (2), `phase-4-probes/runs/` (11), `phase-4-probes/bodies/needle.json`, `.DS_Store` — all gitignored local scratch |
| ~~Mentions of the 22 moving documents and directories~~ | **Withdrawn 2026-08-16.** It said **253**; it does not reproduce, no recipe was recorded, and it had no job. See below |
| Doc paths cited from code and config | **11**, in 7 files — 8 pointing *out* to `docs/`, 3 pointing *into* `CLAUDE.md` |
| `.gitignore` entries naming `docs/` paths | **4**, one of them a negation |
| Documents rewritten rather than moved | **4** — `CLAUDE.md`, `README.md`, `outstanding-work.md` (split), `EPD-000` |
| Documents created | **at least 16** — `docs/README.md` (the manual), `status.md`, `backlog.md`, **seven** `reference/` files, two tier `README.md` indexes, `milestone-1-core/README.md`, and an `evidence/README.md` for each of phases 1, 3 and 5, which have none today (decision 13). **Said 11, then 12, and both undercounted**: the milestone index was listed in Tier 5 but never counted, and the evidence READMEs were required by a decision taken after the row was written |

**The first row was wrong in this document's first version**, which said "68 files, 50 tracked". The
50 was right; the 68 was not, and it contradicted the untracked row two lines below it — 50 + 15 is
65, not 68. Recorded rather than silently corrected, because a document whose subject is this
repository's habit of quoting numbers forward has no business hiding one of its own.

**Why the mention count was withdrawn, 2026-08-16.** It was the sizing argument — "this is not a
forty-minute job" — and a fresh-context review could not reproduce it: counting over the stated scope
at `51b857b` gives 340 occurrences, 301 line-hits, ~261 excluding the two restructure documents, or
199 restricted to `docs/*.md`. No recipe was recorded to choose between them.

**Re-deriving it would have been the wrong fix, because the number had no job.** The sizing claim
stands without it — 68 files, 22 moving, 15 commits, eight breakages. And it was never the commit 13
work list: it **overcounts**, since a prose mention of "Phase 4" breaks nothing, and it
**undercounts**, since `phase-4-evidence/README.md:4` cites `../../CLAUDE.md` and needs `../../../../`
where the filename never changes. Breakage 5 and the Verification section below both say a name-based
grep cannot find that class — so this document already knew why its own headline number could not
size the job.

**What sizes it is the link checker**, run before commit 13, which is where the Verification section
always put it. If a magnitude is wanted, the unit is **files, not hits**: you edit files, and a file
count barely moves when the definition of "a mention" changes.

---

## The eight things that break silently

**1. `probe.py` computes the repository root from its own depth.** `probe.py:40` is
`ROOT = HERE.parent.parent`, used at `:43` for `docs/log-the-whole-request.txt` and at `:44` for
`logs/calls.csv`. Moving `docs/phase-4-probes/` to `docs/procedures/lmstudio-capability-probes/`
takes it from two levels below the root to three. It will not raise on import — it fails later, when
`replay` cannot find the capture.

**The minimum correct edit is `:40` alone.** `CALLS_CSV` at `:44` is derived from `ROOT` and is fixed
for free; `:43` needs a second edit only if the capture also moves to `docs/captures/`. (This
document's first version said "both lines need editing", which overstated the job.)

**2. The `.gitignore` negation for `router.log`.** `.gitignore:59` is a blanket `*.log`;
`.gitignore:229` is `!docs/phase-2-step-6-session/router.log`, the exception that lets the frozen
session's log be committed. Move the directory without updating line 229 and the negation silently
stops applying. **This trap has already fired once** — `handoff.md` records that the original
`git add` on that directory skipped `router.log` for exactly this reason, and shipped a document
citing a file that was not in the repository.

**The mechanism is narrower than "the file untracks itself", which this paragraph implied.**
`router.log` is already tracked, and `git mv` preserves tracking regardless of what `.gitignore`
says — so nothing becomes untracked at the moment of the move. What breaks is the **rule**: line 229
stops covering the path, and the file is unprotected the next time it would need re-adding (after a
`git rm --cached`, a fresh clone plus `git add -A`, or a rotation that replaces it). The trap that
already fired was a first `git add`, which the move does not reproduce. Still worth fixing in the
same commit, and the `git status --ignored` check below is what catches it.

**3. The two gitignored `runs/` directories.** `.gitignore:231` and `:233` ignore
`docs/phase-3-verification/runs/` and `docs/phase-4-probes/runs/`. If the directories move and those
lines do not, the next `git add -A` sweeps in a dozen local run transcripts that were deliberately
never committed. Fails in the wrong direction — nothing errors, the repository just grows.

**4. `docs/phase-4-probes/bodies/needle.json` is gitignored and regenerated.** `.gitignore:237`.
`handoff.md` records that it was regenerated to 41000 tokens for the Phase 5 runs and **put back** to
its committed 12000 default afterwards. It is local scratch; it moves with `mv`, not `git mv`, and
its ignore line moves with it.

**5. Docstring citations in `src/` are not tested.** Eleven of them, and nothing fails if they rot.

**Eight point outward, to a path under `docs/`:**

| File | Line | Cites |
|---|---|---|
| `src/ilirium_llm_router/config.py` | 62 | `docs/phase-5-measurements/` |
| `src/ilirium_llm_router/proxy.py` | 321 | `docs/phase-2-step-6-session/calls.csv` |
| `src/ilirium_llm_router/stats.py` | 26 | `docs/phase-2-step-6-session/calls.csv` |
| `src/ilirium_llm_router/observe.py` | 12 | `docs/lmstudio-usage-check.md` |
| `tests/test_observe.py` | 9 | `docs/lmstudio-usage-check.md` |
| `config.yaml` | 24 | `docs/phase-5-measurements/` |
| `config.yaml` | 30 | `docs/anthropic-auth-check.md` |
| `config.yaml` | 44 | `docs/phase-4-notes.md` |

**Three point inward, naming a `CLAUDE.md` section by its title** — and these are the ones the first
version of this document missed, because they were looked for by grepping `docs/`, which structurally
cannot find a citation that never mentions `docs/`:

| File:line | Names the section |
|---|---|
| `src/ilirium_llm_router/proxy.py:3` | "Observed request shape" — **Leaves** |
| `src/ilirium_llm_router/proxy.py:238` | the byte-relay exception, under "Design decisions" — **rationale leaves** |
| `src/ilirium_llm_router/stats.py:3` | "Observability: log + CSV stats" — **Leaves** |

Every one names a section that EPD-004's triage table marks as leaving `CLAUDE.md`. After the cut,
each points at a heading that no longer exists in the file it names, and nothing fails — which is
exactly the property this breakage is titled after.

These are also the harder edit. A path citation is replaced by a path; a section citation has to be
repointed at the `reference/` file that took the section. Two of the three become straightforward
once the destinations exist — `proxy.py:238` at `reference/design-decisions.md`, `stats.py:3` at
`reference/observability.md`. **`proxy.py:3` needs no edit at all**: it names "Observed request
shape" by section title, and that section survives as a section of `architecture.md`.

`proxy.py:238` is the one to get right: it is the only record in the code that the SSE `error` event
is a deliberate exception rather than an oversight, and the reasoning it points at is now a whole
file rather than a paragraph.

Phase 6 measured the source at 58% prose and kept it deliberately, on the grounds that the docstrings
carry measurements recorded nowhere else. That decision is what makes these citations load-bearing
rather than decorative — a dead path in `observe.py:12` breaks the chain from the scanner's rule back
to the run that established it.

**6. `probe.py`'s own header cites sibling documents by relative path.** `probe.py:6` names
`../log-the-whole-request.txt`, `:12` names `../epd/EPD-002-…`, `:26` names `../phase-4-notes.md`.
All three relative paths change. Its usage examples at `:20-23` print the old absolute path too.
The same applies to the `README.md` inside each evidence directory — several use `../` links.

**7. Rename detection degrades if a move and an edit share a commit.** `git log --follow` and
`git blame` track a rename through a pure `git mv`; a move plus a rewrite in one commit can drop
below git's similarity threshold and the file's history ends there. Given that the whole point of
this repository's documents is that they record when a thing was learned, **losing the history of
`phase-4-notes.md` would cost more than the restructure gains.** Hence the commit order below:
every move is its own commit, and no move commit changes a file's contents.

**8. `router.yaml` writes into `runs/` by a relative path, and the move un-ignores it.**
`docs/phase-3-verification/router.yaml:28` and `:33` are `file: runs/router.log` and
`file: runs/calls.csv`. `CLAUDE.md` records that relative log and stats paths resolve against **the
config file's directory**, not the working directory — so the destination follows the YAML file
wherever it goes.

The mapping below sends `router.yaml` to `docs/procedures/dying-backend/` and `runs/` to the phase
archive. The next run of the stub then writes to `docs/procedures/dying-backend/runs/`, a path
**nothing ignores**, and the next `git add -A` commits transcripts that `.gitignore:231` exists to
keep out. That is breakage 3's failure mode arriving through a door breakage 3 does not cover.
`router.yaml:5` also carries a comment asserting the runs are gitignored, which the move would make
false.

This one is embarrassing rather than subtle: the identical hazard in `probe.py` got a dedicated
paragraph below, and this one got nothing, because `RUNS` is Python and `file: runs/router.log` is
YAML. **It is resolved the same way** — see the mapping.

**And a trap that applies to breakages 3, 4 and 8 together:** `git mv olddir newdir` relocates the
directory's *ignored* contents along with it, and they arrive showing as untracked `??` rather than
ignored, because `.gitignore` still names the old path. So moving `phase-4-probes/` wholesale would
relocate `runs/` and `needle.json` **and un-ignore them in one stroke**. The "plain `mv`" instruction
in the mapping is only correct if the parent directory is never moved as a unit — move the tracked
contents, not the directory.

---

## File-by-file mapping

`git mv` throughout unless the row says otherwise.

### Tier 1 — reference (durable, assembled from existing text)

These are the only files whose *content* is composed rather than moved. Every fact is lifted
verbatim; the work is deciding which paragraph belongs to which file.

**Seven files, not ten** (EPD-004 fork 6, revised on 2026-08-16 from six). Deferred:
`configuration.md`, which has no source of its own, and `request-shape.md` at 12 lines, which starts
as a section of `architecture.md` — and stays there deliberately, since that is what keeps
`proxy.py:3` needing no edit.

| New file | Assembled from |
|---|---|
| `docs/reference/architecture.md` | `CLAUDE.md` "Goal" + the dispatch half of "The central architectural problem", long form. **Plus one section**: "Observed request shape" verbatim. The Anthropic surface moved out on 2026-08-16 into its own file. **Must newly state where the premise stops**: "dispatch, not translation" holds because both sides speak `/v1/messages`, which OpenAI and Gemini do not — written down nowhere today |
| `docs/reference/design-decisions.md` | `CLAUDE.md` "Design decisions" **entire, all 58 lines** — statements and reasoning together. `CLAUDE.md` keeps a titles-only table of contents |
| `docs/reference/observability.md` | `CLAUDE.md` "Observability: log + CSV stats" entire |
| `docs/reference/backend-lmstudio.md` | `CLAUDE.md` LM Studio bullets, including the timeout semantics; the parity table and context facts from `phase-4-notes.md` |
| `docs/reference/backend-anthropic.md` | **added 2026-08-16.** `CLAUDE.md` "Anthropic model IDs" **entire** — the ID table and both rejections — plus the *Result* of `anthropic-auth-check.md` (the OAuth bearer forwarded and accepted, the ten-entry `anthropic-beta` list and the `oauth-2025-04-20` entry that makes it work, and that trimming the list turns a working request into a 401), `credential: forward` and why this is the one backend holding no secret, the 429 shape from `handoff.md`, `read_timeout: 600` and why, and the median time to first byte **with its slice** |
| `docs/reference/measurements.md` | **new** — every quoted number, its date, its instrument, its slice, and **what it is for** (EPD-004 decision 20). Four columns, and a row that cannot be filled in is a number that should not be recorded |
| `docs/reference/lessons.md` | **new** — the four "phase found its premise wrong" episodes, from the six phase notes, **plus the two ways a number fails** — 26× quoted without its slice, 253 with no job it could do. The pair goes in together; either alone reads as a one-off |
| `docs/reference/README.md` | **new** — reading order and what each file answers |

**`request-shape.md` being folded in costs nothing at the citation.** `proxy.py:3` names "Observed
request shape" by **section title**, not by path, and that section survives as a section of
`architecture.md`. Only `stats.py:3` and `proxy.py:238` need repointing at a new file.

**And `Anthropic model IDs` leaving `CLAUDE.md` breaks no citation either**, because nothing in
`src/`, `tests/` or `config.yaml` names that section — it scored zero in the citation measurement,
which is exactly why EPD-004 originally ruled it must stay. What it needs instead is a pointer in
`CLAUDE.md` that names the **trigger**: *before naming an Anthropic model, read this file.* A pointer
saying only that the file exists does not replace a section nobody knew they were reading.

### Tier 2 — procedures (re-runnable instruments)

| From | To | Note |
|---|---|---|
| `docs/lmstudio-usage-check.md` | `docs/procedures/lmstudio-usage-check.md` | cited by `observe.py:12` and `tests/test_observe.py:9` |
| `docs/anthropic-auth-check.md` | `docs/procedures/anthropic-auth-check.md` | cited by `config.yaml:30`; its *Result* is also lifted into `reference/backend-anthropic.md`, which stopped being deferred on 2026-08-16 |
| `docs/testing-against-claude-code.md` | `docs/procedures/testing-against-claude-code.md` | the procedure is reusable for any milestone |
| `docs/testing-against-claude-code--results.md` | `docs/milestone-1-core/phase-1-proxy/evidence/session-results.md` | results are Phase 1 history, not a procedure |
| `docs/phase-4-probes/{probe,make_needle,make_image}.py`, `README.md`, `bodies/` | `docs/procedures/lmstudio-capability-probes/` | **edit `probe.py:40,43` after the move** |
| `docs/phase-4-probes/bodies/needle.json` | same directory | gitignored — plain `mv`, and update `.gitignore:237` |
| `docs/phase-4-probes/runs/` | **stays beside the probe** at `docs/procedures/lmstudio-capability-probes/runs/`; the Milestone 1 transcripts are *copied* to `docs/milestone-1-core/phase-4-lmstudio-parity/evidence/probe-runs/` | gitignored — repoint `.gitignore:233` at the new probe path, and add the archive copy as an exception if it is to be committed |
| `docs/phase-3-verification/{dying_backend.py,router.yaml,README.md}` | `docs/procedures/dying-backend/` | the stub is a tool. `router.yaml:5` comment and **`README.md:24` and `:25`** both need the new path — `:24` is the `python3 docs/phase-3-verification/dying_backend.py` invocation and `:25` the `make run CONFIG=…` example. This row named only `:25` |
| `docs/phase-3-verification/runs/` | **stays beside `router.yaml`** at `docs/procedures/dying-backend/runs/`; Milestone 1 transcripts *copied* to `docs/milestone-1-core/phase-3-failure-handling/evidence/runs/` | breakage 8. Repoint `.gitignore:231` at the new procedures path — **not** at the archive, or the stub writes to an unignored directory |
| `docs/phase-5-measurements/read_timeout_semantics.py` | `docs/procedures/read-timeout-semantics.py` | a twenty-minute measurement that settled two wrong claims; worth keeping runnable. **It splits from its own README**, which goes to phase evidence with the `.txt` files — so the archived README documents a script no longer beside it, and the script arrives in a tier whose index is meant to say when each check is worth re-running. Write its entry into `procedures/README.md` at commit 7, and leave a line in the archived README naming where the script went. `config.py:62` and `config.yaml:24` cite the *directory*: they repoint at the archive, which holds the evidence they mean, but no longer reaches the script |
| — | `docs/procedures/README.md` | **new** — the index, and when each check is worth re-running |

**The rule behind both `runs/` rows.** An instrument's output directory must follow the instrument,
never the archive. If it follows the archive, the tool writes into a milestone folder — wrong for
Milestone 2 — and the ignore rule that keeps disposable transcripts out of the repository stops
covering the path the tool actually writes to. So in both cases: **`runs/` stays beside the thing
that writes it, and only the Milestone 1 transcripts are copied into phase evidence.** `probe.py:42`
(`RUNS`) needs no edit under this rule, and neither does `router.yaml:28,33`.

### Tier 3 — captures

| From | To |
|---|---|
| `docs/log-the-whole-request.txt` | `docs/captures/log-the-whole-request.txt` |

18 mentions across 11 files, **two of which are `probe.py:6` and `probe.py:43`** — an earlier version
said "plus", double-counting them, since `probe.py` is one of the 11. See EPD-004 fork 4 — this is the
one path with a live alternative (`reference/captures/`).

### Tier 4 — EPDs

**No EPD moves**, and no EPD is renumbered. But "untouched" was wrong in this document's first
version — three kinds of edit are needed inside `docs/epd/`:

| What | Where |
|---|---|
| `EPD-000`'s index row for `EPD-004` | **already done** in `51b857b`. Listed as pending below by mistake |
| `EPD-000`'s closing "Related documents that are not EPDs" section | rewritten to point at the new tiers rather than the old flat `docs/` |
| `EPD-000:31` (`docs/implementation-plan.md`) and `EPD-000:55` (`docs/handoff.md`) | both targets move; both are outside the closing section |
| `EPD-000:28-30`, "An EPD graduates *into* `CLAUDE.md`" | a **convention change**, now mandatory: with "Design decisions" leaving whole, an accepted EPD graduates into `reference/design-decisions.md`. And the target is per-subject — `EPD-004` itself graduates into `docs/README.md` |
| `EPD-001:19`, `EPD-001:28`, `EPD-002:30` | relative links `../phase-4-notes.md` and `../phase-2-step-6-session/calls.csv`, all three targets moving into `milestone-1-core/` |

Relative links inside moved directories change by **depth**, not only by name:
`phase-4-evidence/README.md:4` cites `../../CLAUDE.md` and needs `../../../../` after the move. The
link-check script under Verification is what catches this class; reading for it does not.

### Tier 5 — the Milestone 1 archive

| From | To |
|---|---|
| `docs/handoff.md` | `docs/milestone-1-core/closing-notes.md` |
| `docs/implementation-plan.md` | `docs/milestone-1-core/implementation-plan.md` |
| `docs/outstanding-work.md` | `docs/milestone-1-core/outstanding-work.md` — moved in **commit 10**, then split in **commit 12**, its live items lifted into **`docs/backlog.md`** (EPD-004 fork 3). **Corrected 2026-08-16 on all three counts**: this row said commits 8 and 10, and said the live items go to `status.md` — which is the option fork 3 *rejected*, while citing fork 3 as its authority. Status is state, backlog is inventory |
| `docs/phase-1-notes.md` | `docs/milestone-1-core/phase-1-proxy/notes.md` |
| `docs/phase-2-notes.md` | `docs/milestone-1-core/phase-2-observability/notes.md` |
| `docs/phase-2-step-6-session/` | `docs/milestone-1-core/phase-2-observability/evidence/step-6-session/` — **update `.gitignore:229`** |
| `docs/phase-3-notes.md` | `docs/milestone-1-core/phase-3-failure-handling/notes.md` |
| `docs/phase-4-notes.md` | `docs/milestone-1-core/phase-4-lmstudio-parity/notes.md` |
| `docs/phase-4-plan.md` | `docs/milestone-1-core/phase-4-lmstudio-parity/plan.md` |
| `docs/phase-4-evidence/` | `docs/milestone-1-core/phase-4-lmstudio-parity/evidence/` |
| `docs/phase-5-notes.md` | `docs/milestone-1-core/phase-5-config-and-timeouts/notes.md` |
| `docs/phase-5-plan.md` | `docs/milestone-1-core/phase-5-config-and-timeouts/plan.md` |
| `docs/phase-5-measurements/*.txt`, `README.md` | `docs/milestone-1-core/phase-5-config-and-timeouts/evidence/` — cited by `config.py:62` and `config.yaml:24` |
| `docs/phase-6-notes.md` | `docs/milestone-1-core/phase-6-review-and-cleanup/notes.md` |
| `docs/phase-6-plan.md` | `docs/milestone-1-core/phase-6-review-and-cleanup/plan.md` |
| — | `docs/milestone-1-core/README.md` — **new**: what the milestone was, what it proved, the index |

**Three of these slugs changed on 2026-08-16** (EPD-004 decision 15) so that every folder matches its
branch exactly: `phase-3-error-handling` → `phase-3-failure-handling`, `phase-5-credentials-and-timeout`
→ `phase-5-config-and-timeouts`, `phase-6-review` → `phase-6-review-and-cleanup`. The other three
already agreed. **Verify this after commit 10** — every `milestone-1-core/phase-*` directory name must
appear verbatim after `feat/` in `git branch --list 'feat/*'`.

Phase 0 has no notes file; it exists only as a section of `implementation-plan.md` and needs no
directory. Its branch, `feat/phase-0-skeleton`, would give it `phase-0-skeleton/` under the same rule
if one is ever wanted.

**Phases 1, 2 and 3 have no `plan.md`** — their plans were sections of `implementation-plan.md`, and
only phases 4, 5 and 6 wrote a separate one. Decision 13 states the template as though it were
uniform, so three phase folders arrive missing a file the template names. **`milestone-1-core/README.md`
must say so**, or a later reader concludes the plans were lost in the move. The template describes
Milestone 2 onward; the archive records what Milestone 1 actually produced.


### Tier 6 — rewritten at the root

| File | What happens |
|---|---|
| `docs/README.md` | **new — the manual.** What each tier is for, what belongs in it, how to decide when a thing is ambiguous, the naming and numbering conventions, the 40-line growth rule, and how to open a new milestone. The entry point to `docs/`. Its acceptance test: **somebody who has never read `EPD-004` can file a new document correctly from this file alone**. **Widened 2026-08-16** — it also carries the phase template (`plan.md`, `notes.md`, `evidence/` with its README, the "Verified by" line), the branch convention, the two conventions migrating in from the memory store, the permission-file split, and both milestone playbooks. Playbooks go **last**, so a procedure used twice a year does not bury the filing rules read every week |
| `CLAUDE.md` | Cut per EPD-004's table — the length is a **result of the admission test, not a budget**. Sections leave; pointers naming their trigger replace them. "Design decisions" leaves whole, replaced by a **titles-only table of contents** — an index, not a summary, so there is nothing to drift. Surviving sections are rewritten **as rules rather than as history**. **Gains, 2026-08-16:** the branch convention, **seven** rules migrated from the memory store, and pointers at the two playbooks — the playbook pointer carrying an *instruction* (read it and work from it) rather than an address |
| `README.md` | "What it does today" gains the Milestone 1 result in two sentences; the pointer to `CLAUDE.md` becomes a pointer to `docs/README.md`. The "Description" brief stays verbatim |
| `docs/status.md` | **new** — three parts, most volatile first: "Where we stopped" (the handoff, every session), "Where the project is" (milestones → phases → tasks, every phase), "What is next" (two or three items drawn from `backlog.md` and cited to it). **No work items live here** |
| `docs/backlog.md` | **new** — the live items lifted out of `outstanding-work.md`: the three EPDs (**cited, never restated**), the open measurements, the loose ends. Every item keeps the column that makes the survey worth more than a to-do list: **why it is parked, and why the question may be weaker than it looks** |

### Tier 7 — these two documents

The first version of this plan placed every file under `docs/` except itself. Naming the destination:

| File | Destination |
|---|---|
| `docs/epd/EPD-004-documentation-structure.md` | **stays** in `docs/epd/`, per Tier 4. An EPD keeps its number and its home whatever is decided about it |
| `docs/docs-restructure-plan.md` | `docs/milestone-1-core/docs-restructure-plan.md`, as a step of **commit 15** (was commit 14) |
| `docs/handoff-docs-restructure.md` | **deleted** in **commit 15** (was commit 14). It is the temporary handoff for this branch; its content becomes the "Where we stopped" section of `docs/status.md` in commit 12. Leaving it would create the second "where are we" document that the fork 2 decision exists to prevent |

**Both moved from 14 to 15 on 2026-08-16, and the reason is the new commit's subject.** Commit 15
writes the closing playbook *from what this restructure actually cost*, and this plan and that handoff
are its two sources. They retire after it has been written, not before.

The plan is process material, and this restructure is Milestone 1's closing act rather than
Milestone 2's opening one — it exists because Milestone 1 ended, and its subject is Milestone 1's
output. Filing it in the archive it creates is the consistent choice.

It also brushes an EPD-000 convention worth naming: `EPD-000:31` says an EPD is "**not a plan**",
with plans living in `implementation-plan.md`. A migration plan for a *documentation* proposal fits
neither slot. Archiving it beside `implementation-plan.md` is the closest available answer.

---

## Commit order

**Fifteen commits**, raised from fourteen on 2026-08-16. The principle: **no commit both moves a file and edits it**, so rename detection
survives (breakage 7), and any single step can be reverted without unpicking the rest. Each of the
move commits below pairs its move with an edit to a *different* file — `.gitignore`, never the moved
file itself — which is what keeps the principle true rather than merely stated.

| # | Commit | Why here |
|---|---|---|
| 1 | `EPD-004` + this plan | Already on the branch. The decision record precedes the work |
| 2 | Write `reference/backend-lmstudio.md`, extracting the parity table out of `phase-4-notes.md` | **The gate**, and it is an *extraction* — see below |
| 3 | Write `reference/measurements.md` and `reference/lessons.md` | The highest-value output of the proposal, and worth having whatever is decided about the rest. **`measurements.md` carries four columns** including "what it's for" (decision 20), and **filling that column is the first test of the rule** — a number in these documents that cannot fill it is one to withdraw, as 253 was. **`lessons.md` takes the number-failure pair**, both episodes together |
| 4 | Write `docs/README.md`, the manual — including the phase template, the branch convention, the two migrated memory conventions, the permission-file split, and the **opening** playbook | **Before any file moves.** It states the rules the moves follow, so every later commit is checkable against it rather than against an argument in an EPD. The opening playbook can be written now because Milestone 1's opening already happened and is in the archive to be mined; the closing one cannot (commit 15) |
| 5 | Create the remaining tier directories with their `README.md` index files | Gives every later move a destination that already explains itself. **`reference/README.md` is written here but completed at commit 6**, since four of the seven files it must order do not exist yet — and its reading order is what substitutes for numeric prefixes, so an index listing four of seven is the wrong artifact to leave behind |
| 6 | Assemble `reference/architecture.md`, `design-decisions.md`, `observability.md` and `backend-anthropic.md` from `CLAUDE.md` | Content composition, no moves. `CLAUDE.md` is not yet cut — text is duplicated for one commit, deliberately. `backend-anthropic.md` joins here because it is assembled from `CLAUDE.md` sections like the other three, not extracted like commit 2 |
| 7 | Move the procedures — tracked contents by `git mv`, the gitignored `runs/` and `needle.json` by plain `mv`, **never the parent directory as a unit** — and update `.gitignore` in the same commit | The ignore rules must never be out of step with the paths, not even for one commit (breakages 3, 4, 8) |
| 8 | Fix `probe.py` (`ROOT` at `:40`, header paths at `:6,12,26`, usage examples at `:20-23`), `router.yaml:5`, and the moved `README.md` links | Separate from the move, so the move stays a clean rename. `RUNS` and `file: runs/…` need no edit under the instrument rule |
| 9 | `git mv` the capture to `docs/captures/`, fix `probe.py:43` | Decided: `docs/captures/`. Small and isolated |
| 10 | `git mv` the milestone archive; update `.gitignore:229` in the same commit; copy the Milestone 1 run transcripts into phase evidence | The `router.log` negation and its path move together (breakage 2) |
| 11 | Rewrite `CLAUDE.md` — cut the moved sections, rewrite the survivors as rules, insert the pointers, the decisions table of contents, the branch convention and the seven migrated memory rules. **And fix the two numeric errors commit 3 found**: the 111-second warmup probe carried 1960 bytes, not 31 KB, and the probes cost 20.0 of **45.6** minutes | Only now, once every destination exists. **Then shrink all nine migrated memories to pointers** — a step, not a commit, since those files are outside the repository (see below) |
| 12 | Write `docs/status.md` and `docs/backlog.md`; **split** `outstanding-work.md`, lifting its live items into `backlog.md` | EPD-004's fork 3 decision. Its own commit because it rewrites rather than moves. The *move* into the archive already happened at commit 10; this row used to say "archive", duplicating it |
| 13 | Rewrite the cross-references **the link checker reports**, `README.md`, and `EPD-000`'s graduation convention, two body citations and closing section | The bulk edit, in one reviewable commit. Said "the 253 cross-references"; that number is withdrawn above, and the checker's output is the actual work list. The `EPD-004` index row is **already done** in `51b857b` |
| 14 | Fix the **10** doc citations that need it in `src/`, `tests/` and `config.yaml`; run `make test` and `make lint` | Code last, so a test failure has one obvious cause. There are 11 citations but `proxy.py:3` needs no edit — this row said 11, conflating the count with the work |
| 15 | Write the **closing** playbook into `docs/README.md` from what this restructure actually cost — replacing the "not yet written, deliberately" placeholder commit 4 left there — and **delete the dated migration note at the top of that file**; move this plan into the archive; delete `handoff-docs-restructure.md`; **repoint the four references to both, then re-run the link check** | **New, 2026-08-16.** The playbook is mined from this plan and that handoff, so both retire only after it is written. Writing it earlier would commit an instrument that has never been run |

**Commit 15 breaks references that commit 13 repaired, and the link check must close after it, not
after 14.** Moving this plan and deleting the handoff leaves four citations dangling: `EPD-004`'s
opening and closing pointers at `docs-restructure-plan.md`, `EPD-000:76`'s index row naming it, and
`EPD-004`'s citation of `handoff-docs-restructure.md`. `EPD-000` is edited at commit 13 — two commits
before the move that invalidates one of its citations. Repointing them is part of commit 15 rather
than a fifth thing to remember.

**The memory step attached to commit 11 is the one part of this plan git cannot verify.** All
**nine** migrating memories live in `~/.claude/projects/<path-slug>/memory/`, outside the
repository, so nothing in the working tree changes when they shrink to pointers and the link checker
below cannot reach them. Three of them cite paths this restructure breaks and one is already stale.
They are listed in `EPD-004` decision 16 and must be checked by hand.

**Seven** rules land in `CLAUDE.md` and two conventions in `docs/README.md` (commit 4), so commit 11
is where the `CLAUDE.md` half arrives. The count was six until a fresh-context review found the table
in `EPD-004` decision 16 was itself short one memory — `ask-before-touching-the-machine`, which had
no destination anywhere.

**Why the gate changed.** The first version of this plan made commit 2 the writing of
`measurements.md` and `lessons.md`, on the grounds that it would discover whether the durable half
separates from the process half. It would not have. Those two files are **synthesis** — they harvest
asides scattered across six phase notes — and harvesting asides succeeds whether or not the tier
split is sound. The extraction that actually tests the proposition is the parity table coming out of
`phase-4-notes.md`, the one source most fused with its phase narrative. If that cannot be lifted
without dragging half the narrative along, the tiers are wrong, and it is cheaper to learn it from
one file than from twenty-two.

Commits 2 and 3 are both cheap and both reversible; the point of the reordering is only that the
*gate* is the one that can fail.

Merge `--no-ff` per repository convention, so the boundary stays visible.

## Verification

Green tests prove nothing about documents, so the checks are separate.

- **Link check.** A throwaway script over every `.md` in the repository: resolve each relative link
  and each backticked path that looks like a file, report the ones that do not exist. Run it before
  commit 13 to size the job and **after commit 15** to close it — not after 14, since commit 15 moves
  this plan and deletes the handoff and so breaks four references of its own. **Its output is the
  commit 13 work list**, which is why the withdrawn mention count is not needed: it is the only
  practical check for links that break by *depth* rather than by name
  (`../../CLAUDE.md` → `../../../../CLAUDE.md`), a class no name-based grep can reach.
- **A section-citation check, which the link checker will not do**, and **widened 2026-08-16 from
  three citations to every section.** Grep `src/` and `tests/` for `CLAUDE.md` and confirm the three
  section titles named there still resolve (breakage 5) — then confirm that **every section title in
  the pre-cut `CLAUDE.md` resolves to a heading in `CLAUDE.md` or in a `reference/` file.** The
  narrow version could not tell a section that *moved* from one that was *dropped*, and the pointer
  mechanism carries the whole certainty-for-size trade this restructure makes. The human read below
  judges whether a pointer names its trigger; this catches a section that got no pointer at all.
- **`git log --follow`** after commit 15, run against the **new** paths — `milestone-1-core/phase-4-lmstudio-parity/notes.md`,
  `milestone-1-core/closing-notes.md`, `procedures/lmstudio-capability-probes/probe.py`. Each must
  still reach its original commit. Add one file from inside each moved *directory* —
  `phase-2-step-6-session/calls.csv` and `phase-4-evidence/`'s README — since a directory move is
  where rename detection is most likely to have degraded and the three named files would not show it.
- **`git status --ignored`** after commits 7 and 10: the same four ignored paths as today, at their
  new locations, and nothing newly tracked. Specifically confirm that
  `procedures/dying-backend/runs/` and `procedures/lmstudio-capability-probes/runs/` are *ignored*
  and not merely absent — breakages 3 and 8 both fail by a path silently ceasing to be covered.
- **Run the instruments.** `python3 docs/procedures/lmstudio-capability-probes/probe.py --list`, and
  `probe.py baseline` if LM Studio is up. This is the only check that catches breakage 1, and
  `--list` alone will not — it has to be a run that reads the capture. Then run the dying-backend
  stub once and confirm its output lands in an ignored `runs/` beside `router.yaml` (breakage 8).
- **`make test` and `make lint`.** 158 tests, before and after. Any change in the count means this
  work touched behaviour, which it must not.
- **Read `CLAUDE.md` end to end** and ask of each removed section whether the pointer that replaced
  it names *when to open the file*. A pointer that only says the file exists is not a replacement.
- **Test the manual against its own acceptance criterion.** Take three documents that do not exist
  yet — a Milestone 2 phase note, a new re-runnable check, and a measured finding that contradicts
  an existing one — and file each using **only** `docs/README.md`. If any of the three needs
  `EPD-004` or this plan to place correctly, the manual is incomplete, and that is a defect in the
  manual rather than an argument for reading the archive.
- **Confirm `status.md` holds no work items** and `backlog.md` holds no state. The two files exist
  because mixing them is what made `handoff.md` and `outstanding-work.md` overlap; a backlog item
  that has migrated into the status file is the first sign of that recurring.

Added 2026-08-16, for the material the second round of decisions introduced:

- **Branch equals folder.** Every `milestone-1-core/phase-*` directory name must appear verbatim
  after `feat/` in `git branch --list 'feat/*'`. Six folders, six branches, no exceptions. This is
  the only check for decision 15, and reading for it will not catch a one-word slug difference.
- **The migrated memories.** By hand, since they are outside the repository: each of the **nine**
  holds a pointer and no duplicated rule, no memory names a path that no longer exists, and
  `propose-before-implementing` no longer claims commits are opt-in. **`document-decisions-in-separate-docs`
  was already stale before this work started** — it files EPDs at `docs/EPD-NNN-…` — so finding it
  correct afterwards is a real check, not a formality.
- **Every row of `measurements.md` fills all four columns**, including "what it's for" (decision 20).
  An empty cell is the check working: it means a number was carried forward that nobody can say the
  use of, and the answer is to withdraw it rather than invent a job for it. This is the one
  verification step that is *expected* to find something.
- **The `Anthropic model IDs` pointer names its trigger.** This is the one section leaving
  `CLAUDE.md` against the citation measurement's advice, so its pointer carries the whole risk. It
  must say *when* to open the file, not that the file exists.
- **The playbook pointers carry an instruction.** `CLAUDE.md` must tell a session opening or closing
  a milestone to work *from* the playbook, not merely that one exists — EPD-004 decision 12.
- **Both playbooks are present and distinguishable**, and the closing one is dated to when it was
  written rather than to when it was planned. A closing playbook that reads as though written in
  advance has lost the property it was delayed to gain.

## Rollback

Each commit is revertible in isolation except 7 and 10, which pair a move with its `.gitignore`
update by design. The branch is `docs/milestone-boundary-restructure`; `main` is untouched until the
merge.

The only changes under `src/` are **6 comment and docstring lines in commit 14** — 4 citing a
`docs/` path, 3 naming a `CLAUDE.md` section. The other 4 of the 11 citations are in `tests/` (1) and
`config.yaml` (3). The first version of this section said "eight comment lines under `src/`", which
both undercounted the citations and misattributed them to one directory.

## What this plan does not cover

- **Milestone 2's own contents.** `docs/status.md` gains a backlog section; what goes in it is a
  separate decision, informed by the three EPDs and by `outstanding-work.md`'s live items.
- **Whether `EPD-001`, `002` or `003` are accepted.** Untouched by this work. They keep their
  numbers, their status lines, and their place.
- **Any change to router behaviour.** If this branch changes what the router does, that is a defect
  in the branch.
- **Creating the tracked `.claude/settings.json`** (EPD-004 decision 17). The decision is recorded
  there and the manual names the split in one line at commit 4, but building the file is separate
  work on its own branch. Listed here because it otherwise has a decision and no home in either
  document.
- **Anything about `EPD-004` decision 19.** The `$(...)` rule is documented rather than enforced, so
  it needs no step; its text reaches `CLAUDE.md` at commit 11 as one of the migrating memories.
