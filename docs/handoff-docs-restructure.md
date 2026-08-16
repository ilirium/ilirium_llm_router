# Temporary handoff — the documentation restructure

**This file is temporary and self-terminating.** It exists only while
`docs/milestone-boundary-restructure` is in flight. When the restructure lands, its content becomes
the "Where we stopped" section of `docs/status.md` and **this file is deleted** — it must not become
a second document answering "where are we", which is the exact failure the restructure is fixing.

Written 2026-08-15, extended 2026-08-16. Branch: `docs/milestone-boundary-restructure`. `main` is
untouched.

---

## Where this stands

Eight commits, tree clean, nothing moved yet. **All planning is done and decided; execution has not
started.**

| Commit | What |
|---|---|
| `51b857b` | `EPD-004` + `docs-restructure-plan.md`, written as a proposal |
| `9202106` | Repairs after a fresh-context review found six defects, plus the `CLAUDE.md` section measurement |
| `7da2f1b` | All six forks decided; the manual and the backlog file added |
| `de4e28a` | This handoff |
| `dff62a9` | The 2026-08-16 round — decisions 9–17, two of them revising decisions already taken |
| `c9f1152` | Decisions 18 and 19, and the reclassification that empties decision 16's machine-local category |
| `08280ed` | What a second fresh-context review found — a missing ninth memory, the withdrawal of "253 mentions", and eleven count and measurement corrections |
| *(this one)* | Decision 20, generalised from that withdrawal |

The two planning documents:

- **`docs/epd/EPD-004-documentation-structure.md`** — status **decided 2026-08-15**. The argument,
  the measurements, the decisions with the reasoning each one overrode or confirmed, and the original
  forks kept as written so the decisions stay checkable.
- **`docs/docs-restructure-plan.md`** — the migration. Scale, **eight** silent breakages, file-by-file
  mapping, **fifteen** commits, verification, rollback.

**The next action is commit 2 of the plan: write `docs/reference/backend-lmstudio.md`, extracting the
parity table out of `phase-4-notes.md`.** That is the gate — if the table cannot be lifted without
dragging half the phase narrative with it, the tier split is wrong and it is cheaper to learn that
from one file than from twenty-two.

---

## The decisions, in one place

**These use `EPD-004`'s numbering, corrected 2026-08-16.** This table previously renumbered the forks
— it had 2 as `outstanding-work.md` and 3 as `handoff.md`, where the EPD has the opposite, and it
shifted three others. Decision numbers are how these get cited, so two documents numbering them
differently is worse than either numbering.

| # | Question | Decision |
|---|---|---|
| Gate | Is the four-tier split right? | **Accepted** — reference / procedures / epd / milestone archive |
| 2 | `handoff.md` | **Freeze** as `milestone-1-core/closing-notes.md`; `status.md` takes over. No third file |
| 3 | `outstanding-work.md` | **Split**, with the backlog in its own `docs/backlog.md`, not in `status.md` |
| 4 | The capture | **`docs/captures/`** |
| 5 | `Design decisions` | **Moves out whole** into `reference/design-decisions.md`; a titles-only table of contents stays in `CLAUDE.md` |
| 6 | Size of `reference/` | ~~Six files~~ → **seven**, see #9 below. A 40-line growth rule for the rest |
| — | Numbering | **No prefixes** on reference docs; order lives in `reference/README.md`. Unnumbered in the EPD, which records it as a decision rather than a fork |
| 8 | A manual | **`docs/README.md`**, written before any file moves |

### The second round, 2026-08-16

From a discussion that started with *what is `CLAUDE.md` for* and ran into the memory store, the
permission allowlist, branch naming, and how a milestone is opened and closed. Full reasoning in
`EPD-004` under "Decisions taken, 2026-08-16".

| # | Question | Decision |
|---|---|---|
| 9 | A file per backend? | **Yes — `backend-anthropic.md`**, making the reference tier seven files. Revises fork 6. `request-shape.md` stays deferred, so `proxy.py:3` still needs no edit |
| 10 | `Anthropic model IDs` | **Leaves `CLAUDE.md`** into `backend-anthropic.md`. **Revises the triage table**, which said it must stay because it is silently used. The pointer must name the trigger |
| 11 | A review phase | **Yes, closing every milestone**, specified as *measurement, not removal*. Phase 6 was the first instance. Refusals count as outcomes; a new check asks whether each phase completed the task list it published |
| 12 | Playbooks | **Both in `docs/README.md`.** Opening written now from Milestone 1's archive; closing written **after this restructure lands**, from what it cost. `CLAUDE.md` points at both with an instruction, not an address |
| 13 | Phase template | `plan.md`, `notes.md`, `evidence/` + its README, a "Verified by" line, and whether the notes were written while measuring. **One implementation plan per milestone** — which closes the `EPD-000:31` gap |
| 14 | Branch naming | `feat/phase-N-<slug>`, `docs/`, `fix/`, `chore/`. **No planning suffix** — the plan opens the phase branch. `status.md` lists only in-flight branches; the phase note holds the permanent record |
| 15 | Phase slugs | **Folders follow branch names.** Three change: `phase-3-failure-handling`, `phase-5-config-and-timeouts`, `phase-6-review-and-cleanup` |
| 16 | The memory store | **All nine migrate into the repo**, shrinking to pointers — seven rules to `CLAUDE.md`, two conventions to `docs/README.md`. Three cite paths this restructure breaks; one is already stale. Was "six of nine", then "eight": the two harness rakes were reclassified as portable, and a fresh-context review then found `ask-before-touching-the-machine` missing from the table altogether — **the entry whose subject is this machine, omitted from the count that concluded the machine-local category was empty** |
| 17 | The permission allowlist | **Split** — a tracked `.claude/settings.json` policy, the untracked local file for machine accretions |
| 18 | A portable methodology artifact | **Deferred, deliberately.** No `docs/method/` tier, no global `~/.claude/CLAUDE.md`, no separate repo. Extraction is a copy of `docs/README.md` plus the `CLAUDE.md` rule block, done when project #2 starts — a methodology extracted from n=1 is a guess about what generalises |
| 19 | Enforcing the `$(...)` rule with a hook | **Rejected**, with the reasoning recorded so it is not re-proposed. The false positives are real here (the `Makefile` has six `$(VAR)`), quoting makes it undecidable without a shell parser, and it converts a recoverable prompt into a hard block on every Bash call |
| 20 | Meaningless numbers | **A number must have a job, and must be able to do it.** Generalised from withdrawing 253. Test: job, population, recipe, instrument. Enforced structurally by a fourth column in `measurements.md`, not by remembering. The sibling of the slice rule — 26× was unreadable, 253 was purposeless |

One behavioural change worth carrying: **commits no longer need a separate ask** (#16). The rest of
`propose-before-implementing` stands — a design answer is still not a build order.

---

## The last session message, kept verbatim

*Saved at the owner's request. This is the reasoning behind the decisions above, in the form it was
delivered.*

> Committed as `7da2f1b`. Tree clean, `main` untouched. EPD-004 is now **decided**, and `EPD-000`'s
> index reflects that.
>
> ## What your answers changed
>
> **Design decisions moves out whole** (#6). This overrode my recommendation, and your reason is
> better than my objection — I'd argued from the citation count that the section should stay, but "I
> want to read it as a document" is the stronger claim, and it's not satisfiable while the decisions
> are one section of a file nobody reads linearly. What stays in `CLAUDE.md` is a **titles-only table
> of contents**, deliberately not a summary: a one-line restatement of a decision is duplication and
> would drift, a list of titles is an index and can't. A session still sees which decisions exist and
> that reversing one means opening the file.
>
> This makes the `EPD-000` change mandatory — an accepted EPD now graduates into
> `reference/design-decisions.md`, and the graduation target is per-subject, since EPD-004 itself
> graduates into `docs/README.md`.
>
> **Backlog gets its own file** (#2). Your distinction is right and I've written it as *status is
> state, backlog is inventory*. One refinement: `outstanding-work.md` is unusually good at recording
> **why each item is parked** — several entries note the question is weaker than it looks.
> `backlog.md` keeps that column, or it degenerates into a to-do list. It also cites the three EPDs
> rather than restating them.
>
> **Fork 6 folded in at six files**, not four — my "four" named `design-decisions.md`, which my own
> fork 5 recommendation had deleted; your answer puts it back. `configuration.md`,
> `backend-anthropic.md` and `request-shape.md` are deferred with reasons, and the 40-line growth rule
> is recorded. One free win: `proxy.py:3` cites "Observed request shape" by *section title*, and that
> survives as a section of `architecture.md`, so it needs no edit at all.
>
> ## On your open question about the handoff
>
> You asked whether session state needs its own document. **My recommendation is no — one file with a
> bounded volatile section**, and here's the reasoning.
>
> `handoff.md` does three jobs today and only one is genuinely ephemeral: it indexes the documents
> (now `docs/README.md` + `CLAUDE.md`'s map), records what's complete (now `status.md`), and records
> where we stopped. Only the third changes every session.
>
> The case for a third file is that a volatile document churning against a stable one is unpleasant.
> The case against is stronger: **two documents that both answer "where are we" will drift**, and
> drift between documents that were supposed to agree is this repo's demonstrated failure mode —
> Phase 5 found exactly that across four files. One file can't disagree with itself.
>
> So `status.md` has three parts, most volatile first: *Where we stopped* (every session), *Where the
> project is* (every phase), *What is next* (two or three items drawn from `backlog.md` and cited to
> it). And I wrote down a falsifiable split condition rather than leaving it as taste: **if "Where we
> stopped" passes ~30 lines, or starts carrying material that outlives the session that wrote it, it
> has become a document and gets its own file.**
>
> ## On #8 — the manual
>
> This repairs a real gap I'd left. Every rule in EPD-004 would have ended up in `milestone-1-core/`,
> reachable only by someone already digging through history — which is how conventions get silently
> re-litigated. `docs/README.md` is now written as a manual, not a narrative, and it's commit 4,
> **before any file moves**, so every later commit is checkable against it.
>
> Its acceptance test: *somebody who has never read EPD-004 can file a new document correctly from
> this file alone.* The plan verifies that concretely — file three documents that don't exist yet (a
> Milestone 2 phase note, a new re-runnable check, a finding that contradicts an existing one) using
> only the manual. Needing the archive is a defect in the manual.
>
> One thing the decisions surfaced and did **not** close: `EPD-000:31` names `implementation-plan.md`
> as the home of the phases, and that file is archived with nothing named as Milestone 2's successor.
> `status.md` replaces the handoff, not the plan. I've flagged it as open and suggested the manual
> record the convention — one implementation plan per milestone, inside that milestone's folder — so
> the answer isn't invented twice.
>
> Plan is now 14 commits. Waiting for you.

---

## Things to know before touching this branch

**The `CLAUDE.md` section measurement, taken 2026-08-15.** Citations of each section across `docs/`,
`src/`, `tests/` and `README.md`: Design decisions **8**, Observability **4**, Observed request shape
**3**, Goal and the architecture section **1** each, and **zero** for Status, Layout and commands,
Anthropic model IDs, Open proposals, Stack decisions and Style.

**The caveat is the finding, and it must travel with the number.** A citation counts a section used
as an *authority*, not one used as a *lookup table*. Nobody cites "Layout and commands" before
running `make test`. Those zero-scoring sections split into genuinely inert (Status — 59 lines, never
cited in six phases) and silently-used (Layout and commands, Anthropic model IDs). The recipe is
recorded in EPD-004 so the number is never quoted without its slice.

**Two corrections, 2026-08-16.** This called Status "the largest in the file", which is true by bytes
and false by the lines it quotes — it is third, behind Observability at 62 and the architecture
section at 61. And "the second kind must stay in `CLAUDE.md`" now holds only for `Layout and
commands`: decision 10 sends `Anthropic model IDs` to `backend-anthropic.md`. Three counts in the
paragraph above were also re-derived — see EPD-004's citation table.

**The review found a class of defect worth remembering.** The plan originally listed the citations
pointing *out* of `CLAUDE.md` into `docs/`, found by grepping `docs/` — a grep that structurally
cannot find the three citations pointing *into* `CLAUDE.md` by section title. Searching for what
moves will not find what gets cut.

**Nothing is open and nothing is waiting on the owner.**

- ~~**Milestone 2's implementation plan has no home named.**~~ **Closed 2026-08-16 by decision 13:**
  one implementation plan per milestone, inside that milestone's folder, recorded in
  `docs/README.md`. `EPD-000:31` is edited in commit 13.
- **The original six forks from before the decisions are all answered** — this said "five
  questions" — **and so are the twelve from the second round**, decisions 9–20.

**One thing the second round added that has no home yet, and it is deliberate.** The *closing*
playbook cannot be written until this restructure lands, because it is written from what the
restructure actually cost. Until commit 15 exists, that procedure lives nowhere — which is correct,
and is not the same as being forgotten.

**Do not start executing from the numbers alone.** The plan's commit order exists because two of its
breakages have already fired once in this repository, and one of them silently un-tracks a committed
file. Read "The eight things that break silently" before commit 7.

## What has already been verified, 2026-08-16

Recorded so the executing session does not re-derive it. A second fresh-context review checked every
citable claim in both documents against the tree. **These reproduce exactly and can be trusted
without re-checking:**

- All **11** code and config citations, line for line — `config.py:62`, `proxy.py:3,238,321`,
  `stats.py:3,26`, `observe.py:12`, `tests/test_observe.py:9`, `config.yaml:24,30,44`. A repo-wide
  grep finds exactly these plus `README.md:44`, which Tier 6 handles.
- All **11 commit hashes**, each saying what the documents claim it says.
- Every `.gitignore`, `probe.py`, `router.yaml`, `EPD-000`, `EPD-001` and `EPD-002` line number.
- All ten `CLAUDE.md` section line ranges, and 158 tests.
- **The mapping is complete** — all 68 files under `docs/` were enumerated against the seven tiers
  and every one has a destination.

What did *not* reproduce was corrected in `08280ed`, and the withdrawn mention count is recorded in
both documents. **The eight silent breakages are the most reliable part of either document** and were
confirmed mechanically.

## Reading for commit 2, the gate

Done 2026-08-16 by reading `phase-4-notes.md` end to end. The gate's pass/fail criterion is in
`EPD-004` under "The cheapest next step, and the gate"; this is what the source actually looks like.

- **The parity table itself lifts cleanly.** Lines 27–37 are self-contained. The only phase-bound
  context they need is the model and window from lines 13–14 (`qwen/qwen3.5-9b`, 44544 tokens,
  authentication off) — and that is the *slice*, not narrative, so it travels with the table.
- **The three findings also lift** — the ignored thinking budget, `output_config` billing invisible
  reasoning, `cache_control` doing nothing at probe scale — but each carries a sentence of phase glue
  that has to be cut deliberately.
- **The real risk is not narrative drag, it is destination collision.** Several durable facts in that
  file belong to documents that do not exist until commit 3: the time-to-first-byte table and the
  cold/warm cache numbers are `measurements.md` rows; "a third of this phase was already done, again"
  is a `lessons.md` entry; the paragraph where byte-relay stops being an argument and becomes a
  measurement argues a `design-decisions.md` entry. **So writing this file is mostly deciding what it
  does not take.**
- The Phase 5 correction block at lines 239–252 and the timeout table are what `CLAUDE.md`'s LM
  Studio bullets duplicate. That overlap is where "one home per fact" gets its first real test.

## Loose ends that are not blockers

- **`main` is 12 commits ahead of `origin/main`.** Milestone 1's merges are unpushed. Unrelated to
  this branch, and this branch is unpushed too.
- **The tracked `.claude/settings.json`** (decision 17) is its own work on its own branch, listed
  under "What this plan does not cover".
