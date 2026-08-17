# Phase 8 — the method tier and the guardrails: plan

**Written 2026-08-17 on `docs/phase-8-method-and-guardrails`, forked from `main` at `6253cbc`.
Nothing in it has been executed.**

**Seventeen tasks in three groups.** They share a branch because each is small, each is about how the
work is done rather than about the router, and none depends on `EPD-003` or on Milestone 2's central
claim — which is not yet named, and `../implementation-plan.md` says why.

*It opened as two groups. Group C emerged from group B's review — reading the permission allowlist
turned up an entry that looked like a fossil and was a decided refusal. That is the phase's own
"re-derive the plan on contact" rule firing before execution rather than during it.*

**This is the first plan to number its units of work as tasks rather than commits**, per `EPD-004`
decision 22 and `../../README.md`. A task is a unit of work; a commit is a unit of review. Each task
is committed and a task may take several commits; the commit body names the task on its own line.

---

## Why this phase exists at all

**Task group A — the branching rules are in two documents and they disagree.** `CLAUDE.md`'s "Git
and branches" and `docs/README.md`'s "Branches" both claim to state the convention. Seven
differences, tabulated below. This is the exact failure the documentation restructure was run to
fix — *two documents that both answer a question will drift* — surviving inside the structure built
to prevent it, because the restructure split `docs/` and left `CLAUDE.md`'s relationship to it
stated only as a test rather than enforced.

**Task group B — half of the permission allowlist does not exist.** `EPD-004` decision 17 split it
into a tracked policy file and an untracked local one. Only the local file exists.
`docs/README.md:236` describes the split and names it as not yet built.

**Task group C — two tooling decisions have no home.** The ruff pin's reasoning lives only in
`CLAUDE.md`, and `ty` was tried and refused with the refusal recorded nowhere at all. Group C
emerged from group B's review rather than being planned: reading the allowlist turned up an entry
that looked like a fossil and was a decision.

---

## What is settled, and by whom

Decided by the owner on 2026-08-17 in the interview that opened this branch:

| | Decision |
|---|---|
| Location | `docs/method/`, a new tier |
| Naming | `IDM-NNN-kebab-slug.md` — **I**lirium **D**evelopment **M**ethod, mirroring EPD's scheme |
| The index | `IDM-000-about-these-documents.md` **is** the index. No `README.md` in the tier, matching `epd/` and unlike `reference/` and `procedures/` |
| `CLAUDE.md` keeps | the prefix table, `--no-ff`, and the `git merge -F -` gotcha, plus a trigger-naming pointer |
| `--no-ff` scope | **every branch, always.** `CLAUDE.md`'s wording wins over `README.md`'s narrower one |
| The parked `docs/method/` prohibition | narrowed, with a dated addendum in `EPD-004` |
| Scope | `IDM-000` + `IDM-001` + the citations. **No list of further split candidates** — the shape of the rest of the `docs/README.md` split stays undecided |
| The tracked allowlist | **project knowledge only, 14 entries** — `make` targets, the ruff pin, the pytest path, the two backend doc domains, plus four read-only entries derived from `config.yaml`. Arbitrary execution and network stay local |
| Deny rules | **yes, for `.env`**, exact-match. Not a reversal of decision 19 |
| The local file | **53 → 21.** Fifteen fossils and duplicates; `lms load`/`lms unload`, which had repealed a `CLAUDE.md` non-negotiable; `uvx ty@0.0.14`, a refusal rather than a fossil; and the fourteen that move to the tracked file, so each permission has one home |
| `ty` | **tried and refused** — warnings without useful information. Recorded in `IDM-003`, not deleted silently |
| Harness tooling | `settings.json` **hand-written**; `/permissions` verifies the merged result at Task 14; `/fewer-permission-prompts` named in `IDM-002` as writing into the wrong file |
| `README.md:381` | **all three errors fixed in Task 4.** Two are Phase 8's own doing; the second-Phase-7 half is borrowed from the parked review, and `backlog.md` is corrected in Task 5 so it stops listing a fixed finding |
| `~/.config/git/ignore` | **not touched.** Task 8 edits this repository's own `.gitignore` only |
| Harness rules | **`IDM-002`**, with `README.md:236` becoming a pointer — and the tier's second subject is its cheapest validation |
| A rejected plan | **merged and marked, not deleted** — reversing `EPD-004` decision 14. Status line in the plan, row in the milestone plan, no rename, no folder suffix. The phase number is spent |
| `status.md`'s shape | **to the backlog**, not to this phase. The proposal: one row per *milestone* rather than per phase, since the per-phase merge-commit table duplicates what phase notes and milestone READMEs already own |
| The phase number | **orthogonal to the prefix.** Any prefix may carry `phase-N-`; the prefix says what kind of work it is, the number says it is a phase |
| One branch, one merge | the claim **stays in `CLAUDE.md`**; only its `feat/`-only implication is wrong and goes out |
| This branch | `docs/phase-8-method-and-guardrails`; branch slug and folder slug match. **No rename** — the orthogonal rule sanctions the form it already uses |

---

## The seven disagreements, and how each is resolved

Read this before writing `IDM-001`. Every row is a real difference in the committed text, not a
wording preference.

| # | `CLAUDE.md` says | `docs/README.md` says | Resolution |
|---|---|---|---|
| 1 | `docs/<slug>` — "documentation work belonging to no phase" | same **+ "EPDs, a milestone's opening"** | **Neither, once row 7 is settled.** "Belonging to no phase" becomes false — this branch is a `docs/` branch belonging to Phase 8. The row becomes plain *"documentation work"*, keeping README's examples as examples rather than as the definition |
| 2 | Merge with `--no-ff`, **always** | every **phase and feature** branch; silent on `fix/`, `chore/` | **Always**, per the owner. No judgement call at merge time |
| 3 | *(silent)* | Planning that produces no code goes on a `docs/` branch | Keep; it is the rule that put this branch where it is |
| 4 | *(silent)* | A rejected plan's branch is **deleted, not renamed** | **Reversed** by the owner on 2026-08-17 — the branch is **merged and marked rejected**, not deleted. See "The rejected-plan rule is reversed" |
| 5 | *(silent)* | `status.md` in-flight only; **the phase note carries branch, fork point, merge commit** | Keep, and carry the warning: four of six Milestone 1 phase notes recorded intent and never outcome |
| 6 | `git merge` cannot read its message from stdin — `-F -` works for commit, fails for merge | *(silent)* | Keep. **Stays in `CLAUDE.md` too** — see "The one accepted duplication" |
| 7 | "one phase means one branch and one merge commit", with a table whose only numbered row is `feat/` | A phase is numbered work with a plan and a record, **whatever prefix its branch used** — but this sits in "The phase template", not in "Branches" | README is right and `CLAUDE.md` is misleading. `EPD-004` decision 14's own 2026-08-16 revision settles it: **the prefix rule answers *which prefix*, never *is this a phase*.** Resolved by the owner on 2026-08-17 as **orthogonality** — see below. State it inside the branching rules, where somebody choosing a prefix will read it |

**Row 7 is not academic — this phase is its second instance, and the first the table cannot
describe.** Phase 7 was a numbered phase on a `docs/` branch whose name carries no number, which is
precisely why its folder and branch slugs had to disagree. This branch is
`docs/phase-8-method-and-guardrails`: a `docs/` prefix *carrying* a phase number, a third form
neither document sanctions.

**Settled 2026-08-17: the phase number is orthogonal to the prefix.**

```
feat/<slug>    product work
docs/<slug>    documentation
fix/<slug>     a defect
chore/<slug>   tooling, dependencies, formatter bumps

any of them may carry a phase number:   <prefix>/phase-N-<slug>
```

The prefix says **what kind of work**; `phase-N-` says **it is numbered work with a plan and a
record**. `feat/phase-N-<slug>` stops being an atomic form and becomes the common instance of a
general one. Two consequences to carry into `IDM-001`:

- **Row 1 changes** — `docs/` can no longer be defined as work belonging to no phase.
- **Decision 15's one-way check generalises**: every `*/phase-N-*` branch has a folder with its
  slug, not merely every `feat/phase-N-*` one. The converse stays false in both directions —
  `feat/phase-0-skeleton` has no folder, and Phase 7's folder has no matching branch.

Phase 7 is the **old form**, not a violation of the new one; it stays the standing exception under
`EPD-004` decision 15 for the reason already recorded there.

### The rejected-plan rule is reversed

`EPD-004` decision 14 ends: *"if the plan is rejected the branch is **deleted, not renamed**."*
**Reversed 2026-08-17.** The branch is merged `--no-ff` like any other and the plan is marked
rejected in place.

**The reversal restores consistency rather than adding a rule.** Two documents already say the
opposite of decision 14:

- `EPD-000`'s status vocabulary: **withdrawn** — *"Superseded or shown wrong. Kept, with the reason,
  rather than deleted."*
- `docs/README.md`'s review phase: *"**Refusals are first-class outcomes.** Recording that a cut was
  considered and refused, with the measurement, is what stops the same cut being re-proposed every
  milestone by the next person reading the same surface signal."*

A deleted branch was the one place this project discarded a refusal. A rejected plan carries what
was proposed and why it was refused, which is precisely what stops it being re-proposed.

**The risk is not the one it looks like, and it must be designed against.** A rejected plan sitting
in the archive **reads exactly like an accepted-but-unexecuted plan**. That is this repository's
signature failure — a document recording intent that nobody closed out, four times over in Milestone
1's phase notes. So the rejection has to be legible *without opening the file*:

| Where | What |
|---|---|
| The plan's first lines | A status line: **`REJECTED <date>. Not executed.`** — mirroring `EPD-000`'s vocabulary, which already solved this |
| The milestone's `implementation-plan.md` | A row naming the phase, the date, and **why it was refused** |

**The phase number is spent.** Phase 9 rejected means the next phase is 10. Numbers are identities
that are never reused or renumbered, and the attempt did happen at that point in the sequence. The
cost is accepted and named: the archive gains folders holding no executed work, and their status
lines are what make that legible rather than confusing.

**No branch rename, and no folder suffix.** Rejection is not knowable when the branch is created, so
marking the slug means renaming at rejection time — and `EPD-004` decision 15 already established
that renaming a pushed branch costs more than slug agreement is worth. The status line and the
milestone-plan row do the same job with no new exception to the folder⇄branch rule.

### The one accepted duplication

The owner chose to keep the prefix table and both gotchas in `CLAUDE.md` **and** state them in
`IDM-001`. That is a fact with two homes, which is the thing this phase exists to stop.

It is accepted because the admission test demands it: a session writes `git merge -F -`
**confidently and wrongly** with no reason to look anything up first, and `CLAUDE.md` is the only
file auto-loaded. `EPD-004` decision 16 makes exactly this argument for exactly this fact.

**Mitigated by naming the direction of truth rather than by pretending there is one copy.**
`CLAUDE.md`'s block carries a line saying it is restated from `IDM-001`, which is canonical, and
that a change goes there first. Compare `CLAUDE.md`'s design-decisions index, which avoids the
problem by listing titles only — *"a one-line restatement would drift, a title cannot"*. Here a
title cannot carry the rule, so the restatement is accepted with its risk labelled.

---

## The objection `IDM-000` must answer

**`EPD-004` decision 18 declined a `docs/method/` tier, and not for the reason it is easy to
assume.** The n=1 argument — *a methodology extracted from n=1 is a guess about what generalises* —
was aimed at **extraction to project #2**, which stays parked. The tier itself was declined at
`EPD-004:984` on a structural ground:

> Declined: it splits the manual, and `docs/README.md`'s acceptance test — *file a new document
> correctly from this file alone* — would then span two files.

**That objection is answered, not overridden, and the answer is the reason the tier is safe:**

- `docs/README.md` stays the **filing** manual — *where does a document go?* Its acceptance test is
  about filing, and it survives intact **provided the "Where does it go?" table gains a `method/`
  row**. That row is not optional decoration; it is what keeps the test passing, and it is why
  Task 4 is a prerequisite rather than a tidy-up.
- `docs/method/` holds **rules about how the work is done** — *how do I name this branch?* A reader
  filing a document never needs to open it.

**If Task 4's table row is dropped, decision 18's objection becomes correct again.** Written here
so that a future session cutting Task 4 for time sees what it is cutting.

---

## Task list

Tasks are per-phase, numbered in order, and **never renumbered once published** — insert with a
letter (`9a`) rather than shifting the rest. Name the task in the commit body on its own line:
`Task N of phase-8-method-and-guardrails/plan.md`.

**A phase's first act is to re-derive its own plan against what is now known.** Four of Milestone
1's six phases found their own plan wrong on contact. Do that before Task 1.

### Task group A — the method tier and the branching rules

**Task 1 — write `docs/method/IDM-000-about-these-documents.md`.**
The tier's own rules, written before the document that obeys them. Mirrors `EPD-000`'s shape.
Must state:

- What IDM stands for, and what a method document is.
- **That an IDM is the opposite of an EPD in status.** `CLAUDE.md` says of EPDs *"Nothing in an EPD
  is implemented unless it names the date it was accepted. Do not build from one."* An IDM is **in
  force now and you are expected to act on it**. Two three-letter schemes sitting adjacent in
  `docs/` will otherwise be read with the same reflex, and a session that reads a method document as
  a proposal will ignore it. This is the single most important line in the file.
- **Numbering:** `IDM-NNN-kebab-slug.md`, allocated in order written, never reused, never
  renumbered. `IDM-000` is the index. The slug is for grepping and may drift; the number is what is
  cited. Numbers imply neither priority nor dependency.
- **A status vocabulary:** *in force* / *superseded by IDM-NNN* / *withdrawn*. A superseded or
  withdrawn document is kept with its reason, never deleted.
- **Whose method it is** — this repository's practice, or the owner's across projects. Settle it
  here rather than by accident later; it decides what `EPD-004` decision 18's extraction copies.
- **The answer to decision 18's objection**, per the section above.
- The index table. **Each later document's task adds its own row** — `IDM-001` at Task 2, `IDM-002`
  at Task 11, `IDM-003` at Task 15 — the way `EPD-000` grew. Writing all four rows now would leave
  the index describing files that do not exist for most of the phase.

**Task 2 — write `docs/method/IDM-001-git-branching.md`.**
The unified rules. Every row of the seven-disagreement table resolved as decided there, plus:

- The prefix table in its **new four-row shape** — `feat/`, `docs/`, `fix/`, `chore/` by kind of
  work, with `<prefix>/phase-N-<slug>` as an orthogonal form any of them may take. `--no-ff` stated
  as **always**.
- The prefix rule answers *which prefix*, never *is this a phase* — with Phase 7 (the old form,
  standing exception) and Phase 8 (the new form, this branch) as the two worked examples.
- Where a branch is recorded: `status.md` in-flight, the phase note permanently, with the
  intent-versus-outcome warning.
- **The rejected-plan rule in its reversed form**, with the status line, the milestone-plan row, and
  the spent phase number. State the reasoning — refusals are first-class, and `EPD-000` already
  keeps withdrawn documents rather than deleting them — because a rule that only says *what* invites
  the next owner to reverse it back.
- **The folder/branch slug rule, moved here** from `docs/README.md:153–157`: a phase folder takes
  its branch's slug; Phase 7 is the standing exception; **check folders against branches in that
  direction only** — generalised to `*/phase-N-*`. It is a branch rule and it was sitting in "Naming
  and numbering", which is half of how the two sections drifted apart.
- Its provenance: `EPD-004` decisions 14 and 15, and the sections it replaces.

**Task 3 — `CLAUDE.md`: "Git and branches" becomes table + gotchas + pointer.**
Keeps the four-row table **reshaped by kind of work, plus the `<prefix>/phase-N-<slug>` line**;
`--no-ff` (now "always", unchanged in wording); and the `git merge -F -` fact. Everything else
becomes a `→` pointer that **names when to open `IDM-001`** — not merely that it exists. Add the
line naming `IDM-001` as canonical for the restated block.

**Keep the claim, drop the inference.** *"The plan opens the phase branch — no separate planning
branch, so one phase means one branch and one merge commit"* **stays**: it is true, it was measured
(each Milestone 1 phase plan's creating commit sits on that phase's own branch and nothing earlier),
and it is acted on at the moment a session is least likely to look anything up. What goes is only
the implication that the branch is therefore a `feat/` one — which the reshaped table now removes by
itself.

**Task 4 — `docs/README.md`: the Branches section becomes a pointer, and the tier is admitted.**
Three edits, one commit:

1. "Branches" → a pointer to `IDM-001`.
2. The folder/branch slug rule leaves "Naming and numbering" → a pointer.
3. **The `method/` row in the "Where does it go?" table, plus a `method/` subsection under "The
   tiers".** This is the edit that keeps the acceptance test passing — see the section above.

4. **The worked example at `README.md:381`**, which is wrong in three ways:

```
- **A Milestone 2 phase note.** `milestone-2-<slug>/phase-7-<slug>/notes.md`, the slug identical to
- `feat/phase-7-<slug>`.
+ **A Milestone 2 phase note.** `milestone-2-corpus/phase-9-<slug>/notes.md`, the slug identical to
+ its branch's — whatever prefix that branch carries.
```

**Two of the three are Phase 8's own doing.** `feat/` is wrong as of Task 2's orthogonality
decision, and `milestone-2-<slug>` is now concretely `milestone-2-corpus`.

> **`feat/` appears at six lines in this file, not two.** An earlier draft of this plan said twice,
> and a fresh-context review counted them: `:156`, `:253`, `:264`, `:267`, `:326`, `:382`. **Five are
> already covered** — `:253`, `:264` and `:267` sit inside the "Branches" section that edit 1
> replaces wholesale, `:156` moves out at edit 2, and `:382` is this edit. **`:326` is left
> deliberately**: *"The usual case is a `feat/phase-N-<slug>` branch that changes `src/`"* is hedged
> and stays true under orthogonality — the usual case really is `feat/`. Verify that during Task 4
> rather than trusting this note.
>
> *This is the restructure's own lesson landing on the document that quotes it: a grep for a moving
> path cannot find a citation that names a section title, and counting by eye undercounted by four.*

**The third — `phase-7-<slug>`, a second Phase 7 contradicting `README.md:148`** — belongs to the
parked documentation review. Taken here anyway, because leaving a known bug inside a sentence this
task is already rewriting is not scope discipline. `notes.md` records where it came from.

*Phase 9 is used because it does not exist yet*, which keeps it a worked example rather than a
description of something real.

Also check "When two answers are defensible", rule 3: *"Is it a rule about how the work is done,
rather than about the router? Then it is this file, or `CLAUDE.md`…"* — that routing rule is now
wrong and must name `method/`.

**Task 5 — `docs/backlog.md`: narrow the park, record the `status.md` proposal, and close out
`README.md:381`.**
Three edits, one commit:

0. **The documentation-review item must stop claiming `README.md:381` is outstanding.** It currently
   reads *"**Two items are not** [weaker than they look]"* and names `measurements.md:34` and
   `README.md:381`. Task 4 fixes the second, so **one** remains. Rewrite the paragraph to say one,
   name which, and record that the other was taken by Phase 8 — **do not silently drop it**, or the
   next reader cannot tell whether it was fixed or forgotten.

   *This edit exists because of a cross-file dependency inside a single phase, which is the drift
   this whole phase is about.* Fixing a finding in one file while another file still lists it as
   open is how a work list stops being trustworthy.

1. "Extract the portable methodology" is rewritten so the park covers **the extraction only** —
   copying to project #2, a global `~/.claude/CLAUDE.md` — and records that the tier itself was
   built in Phase 8. The n=1 reasoning is preserved verbatim; it is still the reason extraction
   waits.
2. **A new item: `status.md`'s shape.** Proposed 2026-08-17 and deliberately not done here. *Why it
   is parked:* it is a filing question rather than a branching one, and Phase 8 was scoped small on
   purpose. *Why it may be weaker than it looks:* only one of the file's four sections grows without
   bound — "Where we stopped" self-limits at ~30 lines and "In-flight branches" empties at every
   merge. *The proposal:* one row per **milestone** pointing at its archive README, replacing the
   per-phase merge-commit table, which duplicates what `docs/README.md` already assigns to the phase
   note. Carry the counter-argument too: a separate `history.md` was considered and declined as a
   **third** copy of those facts, with nothing forcing it to stay correct.

**Task 6 — `docs/epd/EPD-004-documentation-structure.md`: addenda to decisions 14 and 18.**
Both dated 2026-08-17, in place, in the visible-in-place-correction style the document already uses
throughout. **Decision 18:** the tier is built; the acceptance-test objection was answered rather
than overruled, and how; the extraction decision is untouched. **Decision 14:** two changes — the
phase number is orthogonal to the prefix, and a rejected plan's branch is merged and marked rather
than deleted, with the `EPD-000`-withdrawn and refusals-are-first-class reasoning.

**Neither decision's original text is edited away** — both record what was believed then, and
decision 18's declined-mechanisms list is the part most likely to be tidied by mistake.

**Task 7 — verify group A.**
`procedures/link-check.py` before and after — its docstring names the hits that are correct and
permanent.

> **Expect this plan's own citations to be broken until the files exist.** A whole-repository run on
> this branch reports **98** broken against the docstring's **82**, and all **16** of the difference
> come from `milestone-2-corpus/` citing `docs/method/…` and `.claude/settings.json` — files Tasks 1,
> 2, 9, 11 and 15 create. They resolve as those tasks land. **This is not drift and must not be
> "fixed" by removing the citations.** Task 17 closes the accounting. `make test` must still report **158**; nothing here touches `src/`, so a change in that
number means something unintended moved. Then grep for citations of the two replaced sections by
**title** rather than by path: the restructure's own lesson is that *"a grep for moving paths
structurally cannot find a citation that names a section title"*, and six of those were stale last
time and found only by reading.

### Task group B — the guardrails

Interviewed and settled 2026-08-17. `EPD-004` decision 17 splits the allowlist into a tracked policy
file and an untracked local one; only the local half exists.

**Two findings from reading the file, both of which change the work:**

**The file has drifted since decision 17 measured it — 53 entries, not 51.** **Fourteen** are
provably dead: a literal PID (`ps -p 90607`), three `/tmp/lms*.json` curl lines, two curl lines
against port 8799, **four** one-off import checks — `PIL`, `starlette`, and `zstandard` **twice**
(`import zstandard` and `from compression import zstd`) — `Bash(echo "exit=$?")`,
`Bash(sort -t: -k2 -rn)`, `WebFetch(domain:www.letta.com)`, and `Bash(git -C /Users/ilirium/Library/…)` —
an absolute path to this machine duplicating `Bash(git -C . status --short)` two lines above it.

> *An earlier draft of this plan said thirteen. It counted **subjects** and reported **entries** —
> `zstandard` is one subject and two allowlist lines. Recounted mechanically on 2026-08-17.*

> **Two entries were misfiled as fossils on the first pass and are project knowledge.**
> `Bash(lsof -nP -iTCP:8787 -sTCP:LISTEN)` uses the router's own configured port, `config.yaml:10`,
> and `Bash(curl … http://localhost:1234/api/v1/models)` uses LM Studio's `base_url`,
> `config.yaml:40`. Both were called machine junk because they *look* like literals. **A literal that
> appears in `config.yaml` is a constant, not a fossil** — that is the test, and it is worth stating
> in `IDM-002` because the mistake is easy to repeat.

**The local file's protection is machine-local, which is the same defect as `EPD-004` decision 16.**
It is ignored by `~/.config/git/ignore:1`, the owner's **global** file, and **not** by this
repository's `.gitignore`. On another machine or for a contributor it is plain untracked — and
`Bash(git add *)` is in the allowlist. Decision 16's argument applies verbatim: a committed
convention depending on something that exists only outside the repository, which silently does not
apply if the repository is opened elsewhere. **Fixing this is the precondition for tracking its
sibling**, so it is Task 8 rather than a footnote.

**Task 8 — this repository's `.gitignore` ignores `.claude/settings.local.json`.**
One line, in the repo's own `.gitignore`. **`~/.config/git/ignore` is not touched** — it stays
exactly as it is, and this task neither reads nor edits it.

**The effect is to make the local file harder to commit, not easier.** Today the only thing keeping
it out of the repository is the owner's global ignore file, which does not travel: on another
machine, or for a contributor, the file is plain untracked and `Bash(git add *)` would take it —
along with whatever has accreted into it. A repo-level rule makes that impossible everywhere, for
everyone, permanently.

Do it **before** Task 9. The moment a tracked `.claude/settings.json` exists, the directory stops
being uniformly untracked, which is precisely when an accidental `git add .claude/` becomes
plausible.

**Task 9 — write the tracked `.claude/settings.json`.**

*Allow — **fourteen** entries, project knowledge only.* Ten that encode how the project is built and
tested: every `make` target, `Bash(uvx ruff@0.16.1 format --check src tests)` — which encodes the pin
`CLAUDE.md` calls non-negotiable — `Bash(.venv/bin/python -m pytest -q)`, and the two backend
documentation domains. Plus **four read-only entries derived from `config.yaml`**, promoted on
2026-08-17: `Bash(lsof -nP -iTCP:8787 -sTCP:LISTEN)`, `Bash(curl -s --max-time 5
http://localhost:1234/api/v1/models)`, `Bash(lms --version)` and `Bash(lms ps *)`. They answer *is
the thing even running?*, which is a contributor's first question on day one.

**Arbitrary execution and network stay in the local file.** `Bash(curl *)`, `Bash(python3 *)` and
`Bash(uv run *)` are how the project is actually worked on, but a file whose job is to state policy
should not bless them. Accepted cost: a fresh clone prompts for those until approved.

*Deny — `.env`.* It exists here with 500 bytes of real keys. `CLAUDE.md`'s "ask before touching the
machine" names it as a written rule; this makes it enforced.

> **The pattern must be exact-match, and this is a trap worth naming.** A glob like `Read(./.env.*)`
> also matches **`.env.example`** — which is committed, has no secrets, and is the file that
> documents which key each backend needs. **Deny beats allow in precedence**, so a glob cannot be
> re-allowed for the example. Deny `Read(./.env)` and the `cat` form; do not glob.

**This does not reopen `EPD-004` decision 19.** That refused a **hook** that would parse shell
quoting to block `$(...)`, on **six** grounds — real false positives in this repository,
undecidability without a shell parser, converting a recoverable prompt into a hard block, sitting in
the path of every Bash call, the written rule holding on its own, and enforcement being unable to
teach the alternative. **An exact-path deny has none of the first four, and the last two argue
against enforcing a *reflex*, not against denying a *path*.** Say so in `IDM-002`, or the
next reader will see enforcement and think the refusal was quietly overturned.

**Task 10 — prune the local file: thirty-two entries out, in four groups. 53 → 21.**

*Fifteen fossils and duplicates.* The fourteen listed above, plus
`Bash(curl -s --max-time 4 http://localhost:1234/api/v1/models)` — **not** a fossil, since the URL
is `config.yaml:40`, but a strict duplicate of the entry Task 9 promotes, differing only in
`--max-time 4` versus `5`. Six of them are specific `curl` lines that `Bash(curl *)` already
subsumes — which is exactly why they are dead weight rather than protection. `Bash(curl *)` itself
**stays**: it is how probes get written, and removing it buys a prompt on every one-off.

*Two that repeal a written rule.* **`Bash(lms load *)` and `Bash(lms unload *)` are removed so they
prompt again.** `CLAUDE.md`'s working agreement says *"Ask before touching the machine. GUI
settings, `.env`, long-running local servers: ask rather than detect-and-proceed."* Loading a model
evicts whatever is loaded and takes minutes. These were allowlisted by clicking *allow* during Phase
4 probe work, and **an allowlist entry silently repealed a non-negotiable** — which is the finding,
not the fix. `IDM-002` should name the class: *a permission granted to get through a task can
outlive the task and overrule a rule nobody re-read.*

`Bash(git checkout *)` **stays** — it is mostly branch switching, which this workflow does
constantly. `IDM-002` names the sharp edge instead: the destructive form is `git checkout -- <path>`.

*One that is a refusal, not a fossil.* **`Bash(uvx ty@0.0.14 check src tests)` is removed.** `ty` was
tried and rejected: it produced warnings without useful information. The entry looked like an
unresolved question on the first pass — pinned like policy, absent from the `Makefile` and
`pyproject.toml` like a fossil — and it is neither. **The deletion is only safe because Task 15
records the refusal first**; delete it without that and the next session sees a project with no type
checker and adds one.

*Fourteen that now live in the tracked file.* Every entry Task 9 writes into `settings.json` is
deleted from `settings.local.json`, so **each permission has exactly one home** — which is this
phase's whole subject, applied to itself. The four promoted entries matter most: calling them
project knowledge and then keeping a machine-local copy would be incoherent.

> *Decided 2026-08-17, reversing a narrower answer given earlier in the same interview. That answer
> was given when the tracked file was hypothetical and ten entries; it is now fourteen, four of them
> moved out of this very file. The cost of the reversal is named in the option it replaces: the local
> file no longer stands alone if `settings.json` is deleted. The cost of **not** reversing is worse —
> narrowing the tracked file later would appear to do nothing, because the local copy still grants it.*

**This task produces no commit** — the file is gitignored — and that is expected rather than
missing, per the rule that a task producing no commit is still a task. Record before and after
counts in `notes.md`; it is the only evidence it happened. **53 → 21.**

**Task 11 — write `docs/method/IDM-002-harness-configuration.md`.**
The second method document, which is also **the cheapest available validation that the tier works
for a second subject** — before more documents land in it and a structural mistake gets expensive.
It states: the split and its reasoning (durable project policy versus machine accretion), what earns
a place in the tracked half, the `.env` deny and why it is not a reversal of decision 19, the
exact-match trap, and that the local file is pruned periodically. Plus four things this review
produced, each of which exists because it was got wrong once:

- **The admission test for the tracked half:** *is this fact derivable from `config.yaml`, the
  `Makefile`, or `pyproject.toml`?* If yes it is project policy; if no it is machine accretion.
- **A literal that appears in `config.yaml` is a constant, not a fossil.** Ports `8787` and `1234`
  read as machine junk and are not.
- **A permission granted to get through a task can outlive the task and overrule a rule nobody
  re-read** — `lms load` versus "ask before touching the machine", found here.
- **The sharp edges that are staying:** `Bash(curl *)` is arbitrary outbound network and
  `Bash(git checkout -- <path>)` discards uncommitted work. Both kept deliberately; naming them is
  what makes that a decision rather than an oversight.
- **`/fewer-permission-prompts` writes into the wrong file.** It scans transcripts for common tool
  calls and writes an allowlist into the project's tracked `.claude/settings.json` — which is
  machine accretion, automated, landing in the file this split reserves for curated policy. Its
  output belongs in the local half. **Name it explicitly**, because the command's name makes it
  sound like precisely what this document is for, and a future session will reach for it.
- **`/permissions` is the tool for reading the *effective* rule set**, which is the thing neither
  file shows on its own.

**Task 12 — `docs/README.md`: the harness-configuration paragraph becomes a pointer.**
`README.md:236`'s "Where the harness configuration lives" currently describes the split and says the
tracked half is **not yet built**. That sentence is false the moment Task 9 lands. Replace the
paragraph with a pointer to `IDM-002`.

**Task 13 — `EPD-004` decision 17: addendum.**
Dated 2026-08-17. Records that the split is built, that the entry count had drifted to 53, that the
`.gitignore` gap was found and closed, and that the tracked half deliberately excludes the broad
execution entries decision 17 itself flagged. Separate commit from Task 6, which touches the same
file for different decisions.

**Task 14 — verify group B by driving it, not by reading it.**
`CLAUDE.md`: *green tests are not evidence.* Four checks:

1. `make test` still reports **158** and runs without a permission prompt.
2. **The deny actually fires** — attempt to read `.env` and confirm it is refused. *Attempting it is
   the test, not a violation of the rule; the attempt is blocked and no contents are exposed.*
3. **`.env.example` is still readable.** This is the check that catches a globbed deny pattern, and
   it is the one most likely to be skipped because the file feels unimportant.
4. **The two files together still cover the session's actual work** — no new prompts for anything
   that worked before Task 10, and **`lms load` does prompt**, which is the point of removing it.
   After deduplication this is no longer a formality: the fourteen entries deleted from the local
   file are covered *only* by `settings.json` now, so a mistake in Task 9 shows up here as a prompt
   for `make test`.
5. **`git check-ignore -v .claude/settings.local.json` resolves to this repository's `.gitignore`**,
   not to `~/.config/git/ignore`. That is the whole of Task 8's effect and it is one command to
   confirm.
6. **`/permissions` shows the effective merged rule set**, and it matches what was intended. This is
   the check that cannot be done by reading either file: tracked and local are merged by the
   harness, and the merge is the thing being designed. Hand-writing `settings.json` keeps the diff
   reviewable; `/permissions` is how the *result* is verified.

### Task group C — development tooling

**Task 15 — write `docs/method/IDM-003-development-tooling.md`, and its backlog item.**

The tier's **third** subject, which matters beyond its content: two documents can share a shape by
accident, three cannot. If the scheme is wrong, this is where it shows, and it is still cheap to
change.

Two entries, both of which already exist as decisions and neither of which has a home:

- **The ruff pin.** `line-length = 100` in `pyproject.toml`, `RUFF ?= ruff@0.16.1` in the
  `Makefile`, and why: an unpinned formatter at its default 88 columns once rewrote every file it
  touched, burying the change in progress, and **`make lint` did not object** — line length is
  `E501`, which is not in ruff's default rule set. How to try a version, and that an accepted bump
  goes in its own commit (`d1def4f`), checked by comparing each file's AST before and after.
- **`ty`: tried and refused.** It produced warnings without useful information. **Recorded as a
  refusal rather than deleted silently** — `docs/README.md` says refusals are first-class outcomes
  precisely so they are not re-proposed, and a project with no type checker and no explanation
  invites the next session to add one.

And a `backlog.md` item in the same commit, under "Instruments and housekeeping": **static analysis
beyond ruff** — other type checkers, AST parsers, language servers, over CLI or MCP. *Parked
because* nothing depends on it. *Weaker than it looks?* **Yes, and say so:** `ty`'s refusal weakens
the case rather than strengthening it. The useful signal may be scarce generally rather than absent
from that one tool, so the next attempt should say what it expects to catch **before** it is run.

**Task 16 — `CLAUDE.md`'s ruff paragraph becomes rule-plus-pointer.**

A direct consequence of Task 15, and the same pattern already accepted for branching at Task 3: once
`IDM-003` holds the pin and its reasoning, `CLAUDE.md`'s paragraph is a second copy. **The rule
stays** — *never bump the ruff pin as a side effect* is exactly a thing a session does confidently
and wrongly, and it has already happened once here. **The reasoning, the `E501` explanation and the
AST-comparison procedure go to `IDM-003`**, behind a pointer naming when to open it.

**Task 17 — close out `procedures/link-check.py`'s docstring, and re-derive its counts.**

**The finding this task exists for was missed by the plan and found by review.** `link-check.py`'s
docstring lists seven hits as *"correct and permanent"* — and **Phase 8 builds five of them**:

| Docstring line | Says | After Phase 8 |
|---|---|---|
| `:82` | `.claude/settings.json` ×3 — decision 17 *"defers"* the tracked file | **resolves** — Task 9 writes it |
| `:84` | `docs/method/` ×2 — *"decision 18 says do not build a methodology tier before project #2"* | **resolves** — Tasks 1, 2, 11, 15 build it |
| `:85`, `:86` | `.claude/agents/local-helper.md`, `docs/procedures/closing-a-milestone.md` | still permanent |

**So `link-check.py` is a *third* home for the decision-18 prohibition**, alongside
`backlog.md:106` and `EPD-004:984` — and the plan's Tasks 5 and 6 account for only two. It was
missed because it lives in an instrument rather than in prose, where no amount of reading `docs/`
would surface it. *That is the one-home-per-fact failure this phase exists to fix, found inside the
phase that fixes it.*

The work: rewrite the permanent-hits list from seven to two, drop the decision-18 justification at
`:84`, and re-derive the counts at `:62` and `:71`. **Expected end state: 77 broken and 2 roundabout**
— 82 minus the five that now resolve, with all 16 of this branch's own hits resolved too. **Derive it
by running the checker, and if it disagrees with 77, find out why before editing the number.** A
count written to match an expectation is exactly the defect `EPD-004` decision 20 was written about.

## Done when

- `docs/method/` exists with `IDM-000` and `IDM-001`, and no `README.md`.
- **The branching rules have exactly one canonical home**, with `CLAUDE.md`'s restatement labelled
  as one.
- **A rejected plan has a defined fate** that keeps its reasoning and cannot be mistaken for an
  unexecuted accepted plan.
- `docs/README.md` files a method document correctly **from itself alone**.
- `EPD-004` and `backlog.md` agree that the tier exists and that extraction is still parked.
- The tracked `.claude/settings.json` exists, holding project policy and an exact-match `.env` deny,
  with `.claude/settings.local.json` ignored by **this repository's** `.gitignore`.
- `IDM-002` and `IDM-003` exist, and **the tier has been shown to work for three subjects** — two
  can share a shape by accident, three cannot.
- **`ty`'s refusal is recorded before its allowlist entry is deleted**, so the next session does not
  read a missing type checker as an omission.
- **`link-check.py` reports 77 broken and 2 roundabout**, its docstring rewritten to match, with
  the permanent-hits list down from seven to two. *Not* "clean of new hits" — this phase deliberately
  resolves five long-standing ones.
- `make test` reports 158.
- **The deny was driven, not read** — `.env` refused, `.env.example` still readable.

## Record

| | |
|---|---|
| Branch | `docs/phase-8-method-and-guardrails` |
| Fork point | `6253cbc` |
| Merge commit | *not yet merged* |
