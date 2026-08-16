# Temporary handoff — the documentation restructure

**This file is temporary and self-terminating.** It exists only while
`docs/milestone-boundary-restructure` is in flight. When the restructure lands, its content becomes
the "Where we stopped" section of `docs/status.md` and **this file is deleted** — it must not become
a second document answering "where are we", which is the exact failure the restructure is fixing.

Written 2026-08-15, extended 2026-08-16. Branch: `docs/milestone-boundary-restructure`. `main` is
untouched.

---

## Where this stands

Seventeen commits, tree clean. **Commits 2 to 9a are done — the procedures and the capture have
moved, every live tier resolves, and the link checker is a committed instrument.** The gate
passed, all seven `reference/` files exist, the manual is written, and all three tier indexes are in
place. Four reference files still duplicate a `CLAUDE.md` section; that is deliberate and ends at
commit 11. **No citation has been repointed yet**, so a dozen documents and three code files name
paths that no longer exist — commits 8, 13 and 14.

| Commit | What |
|---|---|
| `51b857b` | `EPD-004` + `docs-restructure-plan.md`, written as a proposal |
| `9202106` | Repairs after a fresh-context review found six defects, plus the `CLAUDE.md` section measurement |
| `7da2f1b` | All six forks decided; the manual and the backlog file added |
| `de4e28a` | This handoff |
| `dff62a9` | The 2026-08-16 round — decisions 9–17, two of them revising decisions already taken |
| `c9f1152` | Decisions 18 and 19, and the reclassification that empties decision 16's machine-local category |
| `08280ed` | What a second fresh-context review found — a missing ninth memory, the withdrawal of "253 mentions", and eleven count and measurement corrections |
| `ad1d5ae` | Decision 20, generalised from that withdrawal |
| `f473277` | What the review verified, and the reading for commit 2 |
| `394d910` | **Commit 2 of the plan** — `reference/backend-lmstudio.md`, and the gate result written into `EPD-004` |
| `5924bcc` | **Commit 3** — `reference/measurements.md` and `reference/lessons.md`, and the two corrections the register found |
| `beddfaf` | **Commit 4** — `docs/README.md`, the manual, written before any file moves |
| `46c8321` | **Commit 5** — the three tier indexes, and two gaps found in the plan while writing them |
| `a3e88bc` | **Commit 6** — the last four `reference/` files, assembled from `CLAUDE.md` |
| `f729cbc` | **Commit 7** — the procedures moved, `.gitignore` repointed in the same commit |
| `f5b993c` | **Commit 8** — `probe.py` and the moved READMEs repaired; two plan corrections |
| `6535d7f` | **Commit 9** — the capture to `captures/`, with a README it turned out to need |
| *(this one)* | **Commit 9a** — the link checker filed as `procedures/link-check.py` |

The two planning documents:

- **`docs/epd/EPD-004-documentation-structure.md`** — status **decided 2026-08-15**. The argument,
  the measurements, the decisions with the reasoning each one overrode or confirmed, and the original
  forks kept as written so the decisions stay checkable.
- **`docs/docs-restructure-plan.md`** — the migration. Scale, **eight** silent breakages, file-by-file
  mapping, **fifteen** commits, verification, rollback.

~~**The next action is commit 2 of the plan**~~ **Done 2026-08-16, and the gate passed.** The parity
table lifted verbatim out of `phase-4-notes.md`; the file states its findings without referring to
Phase 4 as a phase, and the only phase names in it are paths. The result, what the extraction cost,
and the two things it exposed are in `EPD-004` under "The gate was run on 2026-08-16, and it passed".

~~**The next action is commit 3**~~ **Done 2026-08-16.** Both files exist; the four-column rule found
two defects and one rounding slip, all recorded under "What commit 3 found" below.

~~**The next action is commit 4**~~ **Done 2026-08-16.** `docs/README.md` is 365 lines and carries
everything decision 12 and the plan's Tier 6 row asked of it: the six-row filing table and a
tie-breaker for the ambiguous case, the four tiers, naming and numbering, one-home-per-fact with the
frozen-primary / canonical-for-quotation rule, the four-column rule for numbers, evidence and
redaction, the `CLAUDE.md` admission test, the permission-file split, branches, the phase template,
the review-phase spec, three worked examples, and the **opening** playbook. The closing playbook is a
placeholder naming why it is absent.

~~**The next action is commit 5**~~ **Done 2026-08-16.** `reference/README.md`, `procedures/README.md`
and `milestone-1-core/README.md` all exist. The reference index lists **all seven** files in their
finished reading order rather than the three that exist — an index listing part of its tier is worse
than one written slightly early, so nothing is owed at commit 6 beyond the files themselves.

~~**The next action is commit 6**~~ **Done 2026-08-16.** All four assembled; `CLAUDE.md` untouched, so
four sections are duplicated until commit 11. What the assembly decided is under "What commit 6
found" below — the short version is that three paragraphs a reader would expect in
`design-decisions.md` are deliberately in other files, and the file says so rather than leaving the
absence to be noticed.

~~**The next action is commit 7**~~ **Done 2026-08-16, and it is the first commit that moved
anything.** What it found is under "What commit 7 found" below, including one question the plan does
not answer.

~~**The next action is commit 8**~~ **Done 2026-08-16.** Breakage 1 is fixed and verified by
resolving `CAPTURE` rather than by trusting the edit. Both additions landed, and the plan gained two
corrections — see "What commit 8 found" below.

~~**The next action is commit 9**~~ **Done 2026-08-16.** Less isolated than the plan's row implied —
see "What commit 9 found" below.

~~**The next action was commit 10**~~ **Commit 9a came first, at the owner's call:** the link checker
is now `docs/procedures/link-check.py` rather than a file in `/tmp`. See "What commit 9a found".

**The next action is commit 10: `git mv` the milestone archive**, update `.gitignore:229` in the same
commit, copy the Milestone 1 run transcripts into phase evidence, and **write the three missing
`evidence/README.md` files** (phases 1, 3 and 5). This is the largest move and it carries breakage 2 —
the `!docs/phase-2-step-6-session/router.log` negation, the one trap in this plan that has already
fired once. Also due here, from the Tier 2 table: `testing-against-claude-code--results.md` →
`phase-1-proxy/evidence/session-results.md`, which was deliberately left out of commit 7 because its
destination is under the archive.

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

## Reading for commit 2, the gate — and how it turned out

Done 2026-08-16 by reading `phase-4-notes.md` end to end, then executed the same day. **Every
prediction below held**, including the last one: the destination collisions were the work, not the
narrative drag. Kept as written because it is the only record of what was expected before the
extraction, and the extraction agreeing with it is itself the evidence the tiers are readable in
advance.

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

## What commit 3 found

**The four-column rule works, and the verification step that was "expected to find something" found
three things.** All are in `reference/measurements.md` under "Corrections this register made"; this
is the part that becomes work for a later commit.

**`CLAUDE.md` carries one sentence that is false and must be fixed at commit 11.** It says a warmup
probe "took 111 seconds for a 31 KB body". Recomputed from the frozen CSV: the longest warmup probe
is **111559 ms with a 1960-byte body**, and the 31786-byte probe took **103395 ms**. Two true numbers
joined into a false one. **The correction strengthens the argument it was making** — a two-kilobyte
request costing 111 seconds says the cost of a probe is not proportional to what it carries. Why it
cost that is not established; a model load and contention are both plausible and neither was
recorded.

**`count_tokens` is 33 rows or 32 depending on the slice, and neither document said which.** 33 on
that path in the whole file, **32 LM Studio and 1 Anthropic**. `CLAUDE.md` quotes the first,
`handoff.md` the second, both correctly and neither readably. The split also records something nobody
had stated: the catch-all forwarded one `count_tokens` call to Anthropic.

**And the warmup probes cost 20.0 of 45.6 minutes, not 45.5.** 44% either way; already right in
Phase 6's notes and wrong in `CLAUDE.md`.

**A third failure mode for numbers, seen once**, is recorded in `lessons.md` as an instance rather
than a rule — two true numbers joined into a claim neither supports. One occurrence is exactly what
the 26×/253 pair says not to generalise from.

**`lessons.md` also gained nothing from the gate itself**, which is worth saying: the extraction found
no fifth "premise wrong" episode. It confirmed the one already recorded — a reference document is
mostly a decision about what it does *not* take.

### The inheritance as it was written before commit 3 ran

Kept because it is the list the register was checked against, and everything on it landed.

**Rows `measurements.md` must carry**, all of them now quoted in `reference/backend-lmstudio.md` and
therefore needing a canonical home with instrument and job: the 27924-token preamble; the 44544
window and the 63% it consumes; cold and warm time to first byte, 196789 → 49629 ms, with
`cache_read_input_tokens` 0 → 27904; the prefill profile 9166 → 115073 ms, 27924 → 196789 ms,
41595 → 461712 ms, ~41000 → killed at 600247 ms; the 908 ms over-window refusal; 41595 tokens at 93%
of the window; the `read_timeout: 30` reproduction at 30343 ms; the 4 / 127 / 216 output-token
`output_config` comparison; and the warmup-probe cost, 40 calls and 20.0 of 45.5 minutes. The two
medians — 1426 ms Anthropic and 37136 ms LM Studio — are already known to need their slice.

**The relationship to state, so it is not invented twice.** `backend-lmstudio.md` keeps the numbers
in prose because they *are* the backend's capability profile; `measurements.md` is the register that
says when each was taken, with what, over which slice, and what it is for. That is an index, not a
second copy, and a correction still lands in the register first.

**One row is a test of decision 20 rather than a transcription.** The LM Studio version was never
recorded on either measurement date. Every row above inherits that hole, and the fourth column is
where it becomes visible instead of implied.

## What commit 5 found

Writing an index means checking what it indexes, and two things did not survive that.

**The three `evidence/README.md` files had no commit.** Decision 13 requires one per phase, the Scale
row counts them, and no row of the commit table named them. They are now part of **commit 10**, where
the evidence they describe arrives.

**Decision 15's check said "six folders, six branches, no exceptions".** There are **seven**
`feat/phase-*` branches — `feat/phase-0-skeleton` exists and Phase 0 gets no folder — so the check runs
one way only, folders → branches. Corrected in the plan's verification section.

**And one fact about the history that nothing recorded: phases 0 and 1 were fast-forwarded.** Their
branch tips (`fc65233`, `8d335ab`) sit directly on `main`'s first-parent line; there is no merge
commit and no visible boundary. The `--no-ff` convention starts at Phase 2 (`4d7d7f6`) and holds for
every phase after it. This is *not* a defect to repair — rewriting history to add two merge commits
would cost far more than the boundary is worth — but a reader checking the convention against the log
finds two exceptions, so `milestone-1-core/README.md` now says why they are there.

## What commit 9a found

**Filing the checker made it find two things it had missed.** Tightening the filter from "looks like
a path" to **addressed rather than merely named** — first segment is `.`, `..`, or a directory that
exists at the repository root — cut the live-tier noise from 33 hits to 2, and both survivors were
real.

**One of them was a defect in the manual.** `docs/README.md` described `.claude/settings.json` as
though it exists. It does not: decision 17 records the split and defers building the tracked half.
The paragraph now says so.

**The other was a bug in the checker itself**, which is lesson 4 arriving on schedule. Its
"is this relative?" guard was `startswith(".")`, so `.claude/settings.local.json` — a *rooted* path
that happens to start with a dot — never got its repository-root fallback and was reported as missing
while sitting on disk. Fixed, with the reason in a comment.

**The whole-repository run is the commit 13 work list, available now: 97 hits across 55 files.**
Roughly: `CLAUDE.md` 8 (commit 11), forward references to `status.md` and `backlog.md` (commit 12),
the EPDs and the archive's prose (commit 13), and the two migration documents themselves, which name
old paths *as their subject* and are noise. That last class cannot be filtered — the `→` convention
covers a rename written as an arrow, not one written as a sentence.

## What commit 9 found

**The capture needed a README, which the plan did not budget for.** `captures/` was to hold one file
and no index — but the redaction scheme lived in `handoff.md`, which is being archived, and
`docs/README.md`'s own rule says the scheme belongs beside the data it describes. So
`captures/README.md` now records the file's structure, the five `REDACTED-*` markers, what was left in
deliberately, and one thing worth knowing before it causes alarm: **a grep for `sk-ant-` matches this
file**, because the placeholder is `sk-ant-oat01-XXX`.

**The body no longer matches its own `Content-Length`.** Line 29 says `118004`; the body is **117920
bytes**, 84 short. Almost certainly the redaction — real UUIDs and an email are longer than their
placeholders — but that is an **inference**, since the unredacted original was never committed. It
matters for exactly one use: replaying these bytes raw down a socket would hang or truncate. Nothing
in the repository does that.

**The link checker was written early, and it changed the plan.** Run over the live tiers it found six
real breaks from commits 7 and 9 — and **33 false positives** in four classes: template placeholders,
repository-root paths named in prose, globs, and paths named inside a sentence *about* a rename. That
filter is now recorded, because an unfiltered report at commit 13 is unusable.

It also settled a question the plan left implicit. **The live tiers are repaired in the same commit as
the move that breaks them**; only the archive waits for commit 13. A reference document that is wrong
for four commits is a reference document nobody can trust while the restructure runs, and commit 13 is
correspondingly smaller than the plan assumed.

## What commit 8 found

**`router.yaml:5` needed no edit, and the plan said it would.** Breakage 8 predicted the comment
asserting the runs are gitignored would be made false by the move. It was not — because the mapping
was later fixed so `runs/` follows the instrument rather than the archive, and the ignore rule moved
with it. The same rule already spared `probe.py`'s `RUNS` and `router.yaml:28,33`. **Three predicted
edits, none of them needed**, all for one reason, which is the strongest evidence so far that the
instrument rule is right.

**Two files the plan never listed carry the same stale usage examples `probe.py` does.**
`make_image.py:11` and `make_needle.py:13-14` print `python3 docs/phase-4-probes/…`. Breakage 6 names
this class — "cites sibling documents by relative path" — but the commit row enumerated one file of
three. Fixed, and the row now names all three.

**`make_image.py` was run after the move** and regenerated `bodies/image.json` byte-identically at the
new path, which is the cheap version of "exercise it": the script resolves its own directory, so it
was never at risk, and now that is measured rather than assumed.

## What commit 7 found — and one question the plan does not answer

**The move itself went exactly as written.** Twenty tracked files moved as renames, the three
gitignored paths moved with plain `mv`, and `.gitignore` was updated **before** the `mv` rather than
after — so there was never a moment when the scratch directories were uncovered. `git status
--ignored` afterwards shows the same four ignored paths at their new locations and **nothing newly
tracked**, which is the check breakages 3, 4 and 8 exist for. 158 tests, unchanged.

**Breakage 1 was demonstrated rather than assumed.** `probe.py`'s `ROOT = HERE.parent.parent` now
resolves to `docs/`, so it looks for the capture at `docs/docs/log-the-whole-request.txt`. And
`probe.py --list` still prints its probe names perfectly — confirming the plan's claim that `--list`
is not the check for this. Fixed at commit 8.

**The open question: commit 13 cannot repoint links inside the archive without contradicting the
manual.** A dozen archived files name the old procedure paths, and two rules collide — *a phase note
is never edited again*, and *no broken links*. The distinction that resolves it:

- **Prose in the archive gets its paths repointed.** A path is navigation, not a claim; updating it
  preserves what the document means. Phase notes, plans, and the evidence `README.md` files.
- **Captured output never does.** `phase-4-evidence/*.txt` and `phase-5-measurements/*.txt` are
  transcripts of what a command actually printed. Editing them would falsify the record, and a stale
  command line inside a transcript is *correct* — it is what was run that day.

This is not in the plan or the manual. **It goes into both at commit 8**, since two sessions would
otherwise answer it differently and one of them would rewrite the evidence.

## What commit 6 found

**Assembling the decisions file nearly created the duplication it exists to prevent.** A first draft
of `design-decisions.md` pulled in the per-backend `read_timeout`, two recorder constraints
("never let telemetry break a call", "don't store what a spreadsheet can derive") and the formatter
pin — all of which read like design decisions and all of which already have homes:
`backend-lmstudio.md`, `observability.md` and `CLAUDE.md`'s "Layout and commands", which stays.

They were cut, and the file now carries a short table naming where each one lives **and the trigger
that sends you there**. That table is worth more than the paragraphs would have been: the next person
to feel that gap gets an answer instead of adding a second copy.

**One decision was discharged rather than carried.** "First milestone is a minimal end-to-end proxy"
is done. It is recorded under a `Discharged` heading rather than dropped, because a decision that
disappears looks like one that was reversed.

**`architecture.md` states where the premise stops**, which nothing did before: *dispatch, not
translation* holds because both sides speak `/v1/messages`, and the four cloud backends named under
`Goal` do not. A table names what each would actually require, and the paragraph is explicit that this
is not an argument against adding them — it is an argument against treating "add a backend" as one
kind of work.

**The section-citation check passes for everything cut so far.** Each of the six `CLAUDE.md` section
titles due to leave now resolves to a heading in a `reference/` file, and "Observed request shape"
survives as a section heading inside `architecture.md`, which is what keeps `proxy.py:3` needing no
edit at commit 14.

## Loose ends that are not blockers

- **`main` is 12 commits ahead of `origin/main`.** Milestone 1's merges are unpushed. Unrelated to
  this branch, and this branch is unpushed too.
- **The tracked `.claude/settings.json`** (decision 17) is its own work on its own branch, listed
  under "What this plan does not cover".
