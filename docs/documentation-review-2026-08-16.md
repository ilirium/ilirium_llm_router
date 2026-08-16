# Documentation review — 2026-08-16

**Temporary, and it names its own problem.** This file has no home under `README.md`'s filing rules,
and that gap is one of its own findings — see **Q5** below: *where does a finding go when there is
no phase?* Every worked example in the manual routes a finding through "the phase note that made
it", and this review belongs to no phase. It sits at the root of `docs/` until that question is
answered, then moves.

Written at the end of the session that finished the documentation restructure (Phase 7). Nothing
here is fixed. **The whole file is a work list**, and none of it has been acted on.

*`procedures/link-check.py` reports about six broken paths inside this file. They are correct: this
document quotes broken paths **as its subject**, which is the one class the checker documents as
unfilterable. Do not "fix" them — fix the files they are reported against.*

---

## Part 0 — how this came about, and what state things are in

Phase 7 landed in full: fifteen tasks, `docs/` in its finished shape, `CLAUDE.md` cut 337 → 188,
every citation repointed. The branch `docs/milestone-boundary-restructure` is **complete, unmerged,
tree clean**, at `32bf409`.

A fresh-context agent was then asked to review the **current** documentation — not the Milestone 1
archive, not the captures. Scope: `CLAUDE.md`, `README.md`, `docs/README.md`, `status.md`,
`backlog.md`, all of `reference/`, `procedures/` and `epd/`. 23 files, ~5400 lines. It ran
`make test`, the link checker, and recomputed 14 numbers from the frozen 2026-07-31 CSV.

**The reason a fresh context was used:** the whole restructure was done by one agent in one session,
which is the condition under which blind spots survive. That was the right call — three of the five
findings verified below are that agent's own errors, and two of them are in the load-bearing
evidence for decisions taken the same day.

---

## Part 1 — the five findings verified independently

These were re-checked against the tree rather than relayed on trust. **All five confirmed.**

### V1 — `measurements.md:34` states a slice that recomputes to 0.245×

The severest finding. The row exists to show the 26× latency gap is robust across filters, and
states one of its slices as **"26.6× (no warmup probes)"**. Recomputed from
`milestone-1-core/phase-2-observability/evidence/step-6-session/calls.csv`:

| Slice | Anthropic | LM Studio | Ratio |
|---|---|---|---|
| All rows | 1251.5 ms (n=42) | 4904.0 ms (n=97) | 3.918× |
| `/v1/messages` only | 1254.0 ms (n=41) | 16902.0 ms (n=65) | 13.478× |
| **no warmup probes — as the cell literally reads** | 1251.5 ms (n=42) | **307.0 ms (n=57)** | **0.245×** |
| `/v1/messages` **and** no warmup probes | 1254.0 ms (n=41) | 33364.0 ms (n=25) | 26.606× |

The cell silently inherits the previous row's `/v1/messages` filter. Read as written it says LM
Studio is **four times faster** than Anthropic.

**Why this is worse than the failure it descends from.** The original 26×/3.9× episode was a number
correct over an unstated slice, wrong by a factor of seven. This is the same failure *inside the
register built to prevent it*, in the row whose job is to prove the gap survives re-slicing, wrong
by two orders of magnitude with the sign reversed.

### V2 — `README.md:20` says six phases

> "**Milestone 1 is complete** — six phases, 158 tests…"

Against seven in `CLAUDE.md:12`, `status.md:37`, `milestone-1-core/README.md:3`. The repository
front page is the outlier, and it was rewritten during this restructure.

### V3 — the manual's worked example tells you to create a second Phase 7

`README.md:148` — "**Milestone 2 starts at Phase 8**", with the parenthetical explaining that the
restructure took 7.

`README.md:381`, 233 lines later, in the section whose entire purpose is to be copied:

> "**A Milestone 2 phase note.** `milestone-2-<slug>/phase-7-<slug>/notes.md`, the slug identical to
> `feat/phase-7-<slug>`."

The correction was applied to the rule and not to the example.

### V4 — `.env.example:5` is a twelfth code citation, and it is broken

```
# LM Studio. See docs/anthropic-auth-check.md for why.
```

That path does not exist; it is `docs/procedures/anthropic-auth-check.md`. `link-check.py` walks
`*.md` only, so nothing has ever scanned it — and `status.md:20` claims *"every citation in the
repository resolves, including the eleven in `src/`, `tests/` and `config.yaml`."* Eleven is right
for the enumerated set; the sentence claims the repository.

### V5 — decision 22's evidence does not survive re-running

`EPD-004` decision 22 argues the forward-only exception with:

> "**Twenty-one** commit messages in the history say 'Commit N of …' and cannot be rewritten"

Measured: `git log --all` finds **12**. And the companion figure, "21 commits from 15 units", was
true when measured at `eae1489` and is now **24** over `f473277..HEAD`, the range `status.md:83`
itself names as where execution began.

**The decision stands; its evidence does not.** And this is `lessons.md` lesson 6 — *a count that
sizes work is a measurement, not an estimate* — landing inside the decision that cites lesson 6's
own three instances, written the same day.

---

## Part 2 — the triage as delivered, in full

*Saved verbatim at the owner's request. This is what was reported at the end of the session, before
anything was acted on.*

> Report's in. I verified its five most consequential claims myself rather than relaying them on
> trust — **all five confirmed, and three of them are my errors.**
>
> ## The worst one, confirmed by recomputation
>
> `measurements.md:34` — the row that exists to show the 26× gap is robust — states a slice of
> **"26.6× (no warmup probes)"**. Read literally, that slice gives:
>
> | Slice as written | Result |
> |---|---|
> | no warmup probes | **0.245×** — LM Studio four times *faster* |
> | `/v1/messages` **and** no warmup probes | 26.606× ✓ |
>
> The cell silently inherits the previous row's `/v1/messages` filter. This is the file's signature
> failure — a number whose slice doesn't say what it means — **reproduced inside the register built to
> prevent it**, and worse than the original: the 26×/3.9× episode was wrong by a factor of seven, this
> is two orders of magnitude with the sign flipped.
>
> ## Three more I confirmed
>
> **`README.md:20` says "six phases"** — against seven in `CLAUDE.md`, `status.md` and the milestone
> README. The front page is the outlier, and I rewrote it on this branch.
>
> **`docs/README.md:381` tells you to file a Milestone 2 phase note as `phase-7-<slug>`** — 233 lines
> after line 148 says "Milestone 2 starts at Phase 8". I applied that correction to the rule and not to
> the worked example, which is the part meant to be copied.
>
> **`.env.example:5` cites `docs/anthropic-auth-check.md`**, which doesn't exist — it's
> `docs/procedures/`. The link checker only walks `*.md`, so nothing has ever seen it. It's a
> **twelfth** code citation, and `status.md:20` claims "every citation in the repository resolves."
>
> ## And decision 22's evidence doesn't hold
>
> I wrote in `EPD-004` that **"twenty-one commit messages say 'Commit N of …' and cannot be
> rewritten"** — that sentence is the entire argument for the forward-only exception you approved.
> Actual count: **12**. The "21 commits from 15 units" figure was true when I measured it at `eae1489`
> and is now 24 over the range `status.md` itself names.
>
> So the decision is fine, its evidence is not — and it's **lesson 6 landing inside the decision that
> cites lesson 6's own three instances.**
>
> ## The gap I'd rank highest
>
> **The closing playbook is a log of this restructure, not a closing procedure.** `CLAUDE.md:171`
> singles it out as "the one pointer whose omission costs a whole milestone's worth of harvest" — but
> six of its nine steps are one-time work that cannot happen again ("write this file's rules first",
> "then cut `CLAUDE.md`", "split state from inventory"). Decision 12 specified seven steps; **five are
> absent**, including the whole harvest into `lessons.md` and `measurements.md`. I mined it faithfully
> from what the restructure cost, as step 9 asked — and replaced the generic procedure instead of
> adding to it.
>
> Also: **`CLAUDE.md` contains the words "task", "plan.md" and "task list" zero times**, so decision
> 22's mandatory commit-body line is unreachable from a cold start — a session mid-phase would get it
> confidently wrong.
>
> ## What I haven't verified
>
> Everything else — roughly 25 findings, including 10 stale citations the checker structurally can't
> see, `EPD-004:3` still saying "Nothing has been moved yet", `EPD-001`'s confidence table
> contradicting its own addendum, and a procedure that teaches the `max_context_length` field the
> reference tier calls wrong. The reviewer showed its work on most, but I'd rather check before acting
> than relay on trust.
>
> It was also honest about its own coverage: it did **not** verify `backend-lmstudio.md` (the largest
> in-scope file), any live-traffic number, or the three undecided EPDs in full.
>
> ## Six questions it wants from you
>
> 1. Which file owns the branch convention — `CLAUDE.md` or the manual? They already differ.
> 2. **Is Phase 7 complete?** Four commits landed after the one that closed it, none naming a task, one
>    changing a convention the plan is written in.
> 3. Are EPD addenda frozen like phase notes, or live like reference files? Two currently carry claims
>    Phase 5 retired.
> 4. Growth rule or symmetry for the next backend — does `reference/backend-ollama.md` exist on day
>    one?
> 5. Where does a finding go when there's no phase — like this review, or anything on a `fix/` branch?
> 6. `measurements.md` was decided to be cited by anchor, and nothing cites it by anchor. Grow anchors,
>    or re-minute decision 1?
>
> I've changed nothing. My suggested order: the `measurements.md` slice and the `phase-7` worked
> example first (both make a future session act wrongly), then the four confirmed factual errors, then
> verify the remaining ~25 before touching them. The playbook rewrite is bigger and probably wants its
> own task. Say which you want and I'll start — or answer any of the six and I'll fold them in.

---

## Part 3 — the reviewer's report, in full

*Reproduced verbatim. It existed only in session context and on no disk this repository controls;
this is the only copy.*

**What it did:** read all of `CLAUDE.md`, `README.md`, `docs/README.md`, `docs/status.md`,
`docs/backlog.md`, all 8 `docs/reference/`, all of `docs/procedures/` (including the two
sub-directory READMEs), `EPD-000` and `EPD-004` in full, `EPD-001`/`002`/`003` in part. Ran
`make test` (**158 passed** — confirms `CLAUDE.md:12` and `status.md:29`), the link checker on both
scopes (**78 broken / 71 archive / 7 permanent** — matches the docstring exactly), and recomputed 14
numbers from the frozen step-6 CSV and from `git log`.

**Headline:** the numeric register is in excellent shape — nearly everything recomputed matched to
the digit. The defects cluster somewhere else: **in the counts about the restructure itself**, and
in **the paths the manual leaves a filer standing on**. Three findings would cause a future session
to do the wrong thing, not merely be slower.

### 1. Gaps

**G1 — The closing playbook is a migration log, not a closing procedure** *(highest consequence)*

`CLAUDE.md:171-173` singles this out above every other pointer:

> "**Both playbooks are in `docs/README.md`. Read the relevant one and work from it rather than
> improvising** — this is the one pointer whose omission costs a whole milestone's worth of harvest".

Now read what a Milestone 2 closer would find at `README.md:432-458`. Steps 1, 2, 3, 4, 6 and 7 are
**one-time work that has already happened and cannot happen again**: "Write this file's rules first,
before anything moves"; "Run one extraction as a gate before planning the rest"; "Write the tier
indexes for the finished shape"; "Assemble the reference tier"; "**Then cut `CLAUDE.md`**"; "Split
state from inventory — `status.md` and `backlog.md`". Only step 5 (move files, repair links) and
step 8 (repoint) generalise, and step 9 is "write this playbook", already done.

Compare `EPD-004:722-724`, decision 12, which is what the playbook was *decided* to be:

> "**Closing:** freeze the plan and phase notes → write `milestone-N/README.md` → harvest durable
> facts into `reference/` → **process lessons into `lessons.md`** → **numbers into `measurements.md`**
> → live items into `backlog.md` → reset `status.md`."

**Five of those seven steps are absent from the manual.** The harvest — the thing `CLAUDE.md` says
the pointer exists to protect — is not in the playbook at all. The playbook that landed is the
narrative of *this* restructure, mined faithfully from what it cost, which is exactly what step 9
asked for; but it replaced the generic procedure rather than being added to it.

**G2 — Cold start: the task convention is unreachable**

`README.md:282-323` adopts *Milestone → phase → task* today (decision 22), including a mandatory
commit-body line:

> "**Name the task in the commit body**, on its own line before the prose … That line is what makes
> the review phase's check — *did every phase complete the task list it published?* — answerable from
> `git log`".

`CLAUDE.md` contains the words "task", "plan.md" and "task list" **zero times**. Its "Git and
branches" section (146-161) covers prefixes and `--no-ff` and stops. So a session committing
mid-phase writes a commit body with no task line, confidently and wrongly, and the review-phase
check silently loses its input.

No pointer routes there either. `CLAUDE.md:7-8` sends you to the manual "before adding a document or
moving one"; `CLAUDE.md:171` sends you there for opening or closing a milestone. Committing code
during a phase is neither. This is a fresh rule (last commit on the branch, `32bf409`) that has not
yet been given a trigger.

**G3 — Nothing on the prescribed path tells you to run the link checker**

`CLAUDE.md:7` — "Read it before adding a document or moving one" — is the correct trigger, and
`README.md` is the correct destination. But the manual **never instructs you to run the checker**.
Its only two mentions are `:189` (how to *interpret* a report) and `:456` (step 8 of the
milestone-closing playbook). The instruction exists in `procedures/README.md:19` ("**After any
commit that moves a document**") and `status.md:28`, and `CLAUDE.md` points at neither with a
trigger. Given that this repository's own worst-documented failure class is links breaking by depth,
the one instrument that catches it is off the marked path.

**G4 — The manual never names `lessons.md` as a destination**

All three worked documents were filed. Two went smoothly. A **process lesson** does not.

`README.md`'s "Where does it go?" table (17-24) has six rows, none of which fits. The tie-break list
then says at `:46-48`:

> "3. **Is it a rule about how the work is done, rather than about the router?** Then it is this file,
> or `CLAUDE.md` if a session would act on it wrongly without being told."

That is the wrong answer. `reference/lessons.md` is exactly the home for a rule about how the work
is done, and the manual mentions it **once**, at `:200`, in passing, as a place where two numeric
episodes happen to be recorded — never as a destination. A filer working from the manual alone puts
a process lesson in `README.md`, which is how the manual grows into the thing it warns against.

**G5 — The manual's acceptance test fails on the second worked example**

The second test document — a probe for a second local backend — files correctly right up to the last
clause of `README.md:391`: "If it establishes durable facts about a backend, those go to
`reference/backend-<name>.md`". A new backend file starts thin. The manual's growth rule (`:70-73`)
then says:

> "A section becomes its own file when its trigger is nameable **and** it passes roughly 40 lines.
> Until then it lives as a section in the nearest file that already has a trigger."

So the manual says put it in `backend-lmstudio.md` or `architecture.md`. The decided convention says
the opposite — `EPD-004:551-558`:

> "**Revised again on 2026-08-16 to seven, adding `backend-anthropic.md`.** The two tests below did
> not decide it — at 13 lines it fails the size test exactly as this section says. **Symmetry decided
> it** … a tier holding `backend-lmstudio.md` and *not* `backend-anthropic.md` creates precisely such
> an ambiguity for the next backend".

**EPD-004 had to be opened to file this correctly.** By `README.md:7-9`'s own words, that is a
defect in the manual. `reference/README.md:39-47` doesn't carry the override either.

**G6 — `CLAUDE.md` advertises a rule the manual does not have**

`CLAUDE.md:7`: "`docs/README.md` is the manual: how documents are filed, named, **corrected and
retired**." Grepping the manual for `retire|delete|supersede|withdraw|obsolete` returns three hits,
none about retiring a document: `:202` is about withdrawn *numbers*, `:268` about deleting a
*branch*, `:340` about deleting a plan *step*. EPDs have a `withdrawn` status (`EPD-000:62`);
documents have nothing. A superseded procedure has no rule.

**G7 — Decision 21's convention graduated into the wrong file**

`EPD-004:1153-1155`: "**The convention this decision states, graduating into `docs/README.md`:** a
path is written in backticks, and a rename is written with `→`. The second half is not a style
preference — the checker depends on it."

It is in `CLAUDE.md:187-188`. `docs/README.md` contains **zero** occurrences of "backtick" and zero
of the arrow. The manual's "Naming and numbering" section (136-157) — where a person about to write
a rename is standing — does not carry it. Since `link-check.py:128` silently skips any line
containing the arrow, a rename written without it becomes a permanent false positive nobody can
explain.

**G8 — A twelfth code citation exists, is broken, and is invisible**

`.env.example:5`:

```
# LM Studio. See docs/anthropic-auth-check.md for why.
```

That file does not exist; it is `docs/procedures/anthropic-auth-check.md`. `link-check.py:184` only
walks `*.md`, so this was never scanned. And `status.md:20-21` states:

> "`docs/` has its finished shape and **every citation in the repository resolves**, including the
> eleven in `src/`, `tests/` and `config.yaml`."

Eleven is the correct count for `src/`+`tests/`+`config.yaml` — all eleven verified to resolve. But
the sentence claims the repository, and `.env.example` is a twelfth citation outside the enumerated
set. This is `lessons.md:157`'s own third instance ("I measured the live tiers, wrote the number
down as though it covered the repository") recurring in the status file.

**G9 — `observability.md` omits half of the scan cap**

`observability.md:104-109` presents the 1 MiB cap as a property of the buffered path only:
"**Non-streaming replies are buffered to a 1 MiB cap**, then parsed once." The code says otherwise —
`observe.py:44-51`:

```
# A ceiling on what a scanner will hold in memory, for the buffered body and for a single unbroken
# SSE line alike.
```

`MAX_SCAN_BYTES` is used at both `observe.py:157` (SSE) and `:237` (buffered). The SSE half is where
Phase 6's real defect lived, and it has a `measurements.md:102` row — but the file that calls itself
"the specification of what is recorded and why; read it before touching the recorder" does not
mention it.

### 2. Contradictions

**C1 — `README.md` says six phases; everything else says seven**

`README.md:20`: "**Milestone 1 is complete** — six phases, 158 tests". Against `CLAUDE.md:12`
("seven phases, 158 tests"), `status.md:37` ("Seven phases, 158 tests"),
`milestone-1-core/README.md:3` ("Seven phases"). The repository front page is the outlier, and it
was rewritten on this branch.

**C2 — The manual's worked example collides with the manual's numbering rule**

`README.md:148-151`:

> "**Phase numbers are globally sequential, not per-milestone.** **Milestone 2 starts at Phase 8**, so
> … *(This said Phase 7 until 2026-08-16, when the documentation restructure took that number…)*"

`README.md:381-382`, 233 lines later, in the section whose entire purpose is to be copied:

> "**A Milestone 2 phase note.** `milestone-2-<slug>/**phase-7**-<slug>/notes.md`, the slug identical
> to `feat/**phase-7**-<slug>`."

The parenthetical correction at `:150` was applied to the rule and not to the example. Anyone filing
Milestone 2's first phase from the worked example creates a second Phase 7.

**C3 — "21 commits from 15 units" does not survive `git log`**

The claim appears twice, and it is the evidentiary basis for decision 22 — `README.md:289-292`:

> "Phase 7's plan numbered its work 'commit 1' to 'commit 15'. Executing it produced **21 commits from
> 15 units** … **Six of fifteen were not one-to-one in the naming scheme's own first use.**"

and `EPD-004:1219-1222`. Measured:

| Claim | Actual |
|---|---|
| 21 commits | **24** (`git rev-list f473277..HEAD`, the point `status.md:83` names as where execution began) |
| "**Twenty-one** commit messages in the history say 'Commit N of …'" (`EPD-004:1237`) | **12** repository-wide (`git log --all`); 16 on the loosest reading of "Commit ⟨n⟩" anywhere in a body |

Twelve of the 24 commits carry no unit attribution at all, and the last four (`7f3eecd`, `ea00856`,
`5758a55`, `32bf409`) sit outside the plan's numbering entirely. The 21 was presumably true at
`eae1489` and was not re-run afterwards. That the "Twenty-one commit messages … cannot be rewritten"
sentence is the load-bearing argument for the forward-only exception makes this worth fixing rather
than shrugging at — and it is **lesson 6 arriving inside the decision that cites lesson 6's own
three instances**.

**C4 — `status.md` counts commits, in the vocabulary just retired**

`status.md:14` ("**All fifteen commits done**") and `:83` ("Complete, all fifteen commits"). Fifteen
is the *task* count; the commit count is 24. Decision 22, adopted in the branch's final commit, says
at `README.md:290-291` that naming the unit of work after the unit of version control is "a mistake
this project made once and measured". `status.md` still speaks it, in the file most likely to be
read first.

**C5 — The manual carries the stale count that `lessons.md` warns about**

`README.md:339-341`: "**Four of six phases** in Milestone 1 found their own plan wrong on contact."
`reference/lessons.md:19-21`: "**Five of seven phases** discovered, in their first hour or during
execution, that the thing they were scheduled to do was already done, already measured, or wrongly
described."

`lessons.md` is the canonical-for-quotation tier, and it flags this exact trap at `:36-38`:

> "*This was titled 'Four times' with four rows until Phase 7 added a fifth on 2026-08-16. **A count in
> a heading goes stale the moment the thing it counts grows, and nothing re-checks it** — which is
> lesson 6 below, arriving in the file that records it.*"

The sweep that produced that note did not reach the manual. (`CLAUDE.md:31-32` states the narrower
"Phases 3, 4 and 5 each found a third or more" and is fine.)

Related, same paragraph family: `README.md:276` — "four of Milestone 1's **six phase notes** still
say 'merge back with `--no-ff`'". All checked: the four files are `phase-2/notes.md`,
`phase-3/notes.md`, `phase-4/`**`plan`**`.md` and `phase-5/`**`plan`**`.md`. Two are plans, not
notes, and six should be seven. `backlog.md:99` states the same fact correctly ("Five exist across
four of the six phases").

**C6 — `EPD-004`'s status line contradicts its own ending**

`EPD-004:3`: "**Status: decided 2026-08-15 … Nothing has been moved yet.**" `EPD-004:1376-1378`:
"**The gate was run on 2026-08-16, and it passed.** `docs/reference/backend-lmstudio.md` exists, at
228 lines…"

Everything has moved. The first line of a 1418-line document is the one a reader trusts most.

*(Minor, same document: `:1378` says 228 lines; the file is 230.)*

**C7 — A measurement whose premise the project then reversed**

`EPD-004:1102-1111`, decision 21's sizing table:

| Where | Addressed paths | Survives the restructure |
|---|---|---|
| the two migration documents | **189** — 42% of the total | **no, deleted at commit 15** |

They were not deleted. They are `milestone-1-core/phase-7-docs-restructure/plan.md` and `notes.md`,
frozen and permanent — the link checker's docstring at `:60-63` even gives them "a permanent
address" and attributes 71 of 78 hits to them. So the conclusion that follows — "451 addressed
paths, of which **42% evaporates on its own**" — is now false, and it is the argument's magnitude
claim. The refusal itself still stands on its other four reasons; the number under it does not.

**C8 — `EPD-001`'s confidence table contradicts `EPD-001`'s own addendum**

`EPD-001:8` instructs: "**Read the verification table before acting on any of it.**" That table, at
`:237-243`, still says:

| Claim | Status |
|---|---|
| Per-request dispatch routes a mixed-model session correctly | "…**never with two models *inside one session***" |
| `x-claude-code-agent-id` arrives on subagent requests | **Documented only** |

Both were measured, and `EPD-001`'s own Phase 4 addendum says so 210 lines earlier, at `:27-30`:
"**Mixed-model sessions are measured, not hypothetical.** Two client sessions … reached both
backends, and **seven rows carry a subagent's `agent_id`**." `measurements.md:70` carries the
canonical row. `EPD-000:64-70` calls this table "the repository's central discipline and it is not
optional".

**C9 — `EPD-002`'s addendum carries two questions Phase 5 closed**

`EPD-002:47`: "Also still open: whether trimming happens *below* the boundary. The run meant to
check hit the router's own 600 s read timeout first."

`reference/backend-lmstudio.md:144-147`: "**Below the window, nothing is dropped either.** A prompt
of **41595 tokens against the 44544 window — 93% full** — returned a codeword planted at its very
front … **So silent trimming is ruled out at both ends.**" And the 600 s timeout became per-backend
in Phase 5 (`config.yaml:48`, `read_timeout: 1800`). `EPD-001:39-42` carries the same retired
timeout claim.

Neither EPD was swept. `README.md:175-176` calls that sweep "expected, not optional — it is half of
what filing a finding means." Whether an EPD *addendum* is frozen like a phase note or live like a
reference file is genuinely unstated — see Q3.

**C10 — Five stale citations the checker structurally cannot see**

`link-check.py:118-124` skips any candidate containing no `/`, so bare filenames rot silently. Found
by grep:

| Where | Text | Should be |
|---|---|---|
| `reference/measurements.md:132` | "`handoff.md` says 'all 32 such rows are logged `ok`'" | `../milestone-1-core/closing-notes.md` |
| `backlog.md:99` | "only `phase-4-notes.md:7` records the merge commit" | `milestone-1-core/phase-4-lmstudio-parity/notes.md:7` (content verified correct) |
| `procedures/testing-against-claude-code.md:98` | "listed under 'What Phase 2 still has to prove' in `handoff.md`" | same |
| `procedures/testing-against-claude-code.md:153` | "the point of decision 5 in `phase-2-notes.md`" | `milestone-1-core/phase-2-observability/notes.md` |
| `procedures/testing-against-claude-code.md:83, :146` | "recorded in `CLAUDE.md`, not a bug"; "Say so in `CLAUDE.md`" | both facts moved to `reference/design-decisions.md` and `reference/observability.md` |

The `measurements.md` one is the worst placed — the canonical-for-quotation tier, in the paragraph
that exists to be quoted forward.

**C11 — The branch convention has two homes and is already diverging**

`CLAUDE.md:148-161` and `README.md:251-270` carry the same four-row prefix table and the same three
rules. `diff` shows they have already drifted: the manual's `docs/<slug>` row adds "— EPDs, a
milestone's opening"; the manual carries a milestone-opening clause `CLAUDE.md` lacks; `CLAUDE.md`
carries the `git merge -F -` trap the manual lacks. Neither names the other as canonical.

`reference/design-decisions.md:133-142` shows the pattern that should apply — an explicit "Decisions
that live in another file, and why" table, with the formatter pin listed as living in `CLAUDE.md`
because "every session runs `make format`; a pointer would not be read in time". The branch
convention has exactly the same shape and got no such marker.

**C12 — A live instrument teaches the field the reference tier calls wrong**

`procedures/lmstudio-usage-check.md:28-34` — a runnable snippet:

```
print(m['key'], m.get('max_context_length'), m.get('capabilities'))
```

`reference/backend-lmstudio.md:36-38`: "**Read the loaded window from
`loaded_instances[].config.context_length`, not from `max_context_length`.** On this machine those
differ by 262144 against 44544 … only the second one governs whether a request fits."

`EPD-002:50-58` records reading that neighbouring field as a defect in a proposal ("Scaling by the
larger number would report a window roughly six times too generous"). The procedure prints the wrong
one.

**C13 — `procedures/testing-against-claude-code.md` was not swept at all**

Three live claims the reference tier has superseded:

- `:29` and `:176` — "roughly **30k tokens** of fixed preamble" and "the ~30k fixed preamble".
  `measurements.md:163` **withdraws** that figure: "Superseded rather than wrong: measured at
  27924." The procedure's step 2 is exactly where somebody chooses a local model's window, and the
  file never mentions 27924, 44544, or 63%.
- `:62-63` — "The router injects nothing and holds no secret". `design-decisions.md:91-98` reverses
  this framing explicitly: "It stays true only of Anthropic, which is one backend's property rather
  than the architecture's." `README.md:47-49` states the qualified version correctly; the procedure
  does not.
- `:179` and `:184` — "Phase 4 should settle it"; "All of it is Phase 4." Phase 4 settled all of it
  on 2026-08-06.

**C14 — A `measurements.md` slice that recomputes to 0.25×**

`measurements.md:34`, the row that exists specifically to show the gap is robust:

| The intermediate slices: 13.5× (`/v1/messages` only), **26.6× (no warmup probes)** | … | **Slice: named in each cell** |

13.5× reproduced first try (41 Anthropic rows median 1254 ms, 65 LM Studio rows median 16902 ms →
13.48×). "26.6×" took four attempts. It is **`/v1/messages` only *and* warmup probes excluded** — it
silently inherits the previous cell's filter. Applied to the whole file as the cell literally reads,
"no warmup probes" gives **0.245×**, i.e. LM Studio four times *faster*.

This is the file's signature failure reproduced inside the file built to prevent it, and it is worse
than the original 26×/3.9× episode: that one was wrong by a factor of seven, this one by two orders
of magnitude and with the sign flipped.

**C15 — `26.1×` and its own operands disagree** *(marginal, reported for completeness)*

`measurements.md:32` states 1426 ms, 37136 ms and **26.1×**. 37136 ÷ 1426 = **26.04**. The 26.1 is
defensible from the unrounded median (1425.5 → 26.05), but the recipe column does not say the ratio
is taken over unrounded medians, and a reader dividing the two printed numbers gets 26.0.
`phase-6/notes.md:203` prints 26.1× the same way.

Everything else in that block reproduced exactly: 142 rows, 11 sessions, 7 agent rows under 1 agent
ID, 33 `count_tokens` (32 LM Studio / 1 Anthropic), 40 warmup probes at 20.04 of 45.60 minutes,
longest 111559 ms at 1960 bytes, 24 LM Studio cache rows max 40879 / 52 whole-file max 70692, 99
qwen rows with 95 `ok`, 1252/4904 → 3.92×. Fifteen of sixteen — the register is genuinely good.

**C16 — "The seven modules" is an unnamed slice**

`measurements.md:99`: "**58% of the source is prose: 1713 lines, 371 code, 1000 comment and
docstring** … Slice: **The seven modules**". `src/ilirium_llm_router/` holds ten `.py` files;
`CLAUDE.md:39-47` lists eight. The seven are `phase-6/notes.md:250-258`'s table, which silently
excludes `cli.py` (132 lines), `__init__.py` and `__main__.py`. A reader recomputing over `src/`
gets **1722** lines today and a different ratio. Under decision 20's own four columns, "the seven
modules" fails the population test — it names a cardinality, not a population.

**C17 — Two sizes for the capture**

`reference/architecture.md:86`: "it is one **120 KB** line, so read it with `jq`".
`captures/README.md`: "Line 31 | The body — **one 117920-byte line**", with the file at 119018 bytes
and `Content-Length: 118004`. Three numbers for one artefact across two live files; the reference
tier has the least precise one.

**C18 — `README.md`'s quick start rests on a "Documented only" row**

`README.md:42`: "Pick a model with `/model`: anything starting with `claude-` goes to Anthropic,
anything else goes to whatever LM Studio currently has loaded." `EPD-001:239` grades "`/model
<local-id>` is accepted behind a custom base URL" as **Documented only** — never run against this
router. (Evidence to promote it probably now exists in the frozen session, which spans backends
within single `session_id`s; the point is that nobody swept it, so the front page and the EPD
disagree about a claim's confidence.)

### 3. Hard to follow

**H3.1 — Two mechanically-repointed paths in `EPD-004` are now nonsense.** `EPD-004:178`, inside the
fenced directory tree, where every sibling is a bare filename:

```
  milestone-1-core/          the archive: how Milestone 1 was built
    README.md                what it was, what it proved, the index
    closing-notes.md         (was handoff.md, frozen at the boundary)
    implementation-plan.md
    outstanding-work.md      the survey, archived; its live items became backlog.md
    ../milestone-1-core/phase-7-docs-restructure/plan.md
```

A path beginning `../` inside a tree rooted at `docs/`. And `EPD-004:779-780`:

> "**Milestone-root files are for work spanning phases** — the milestone's `implementation-plan.md`,
> and documents like `../milestone-1-core/phase-7-docs-restructure/plan.md` that belong to no single
> phase."

A document filed *inside a phase folder*, cited as the example of something belonging to no single
phase. Both are the exact hazard `README.md:468` names — "**A name-based rewrite cannot fix a link
that broke by depth**, and will confidently make it worse" — landing in the document that names it.
`:780` had to be read three times before it was clear this was an artefact rather than a distinction
being missed.

**H3.2 — The manual's tie-break list is where the hard cases go to be answered wrongly.**
`README.md:37-51` promises to resolve "the expensive case", then gives four steps of which step 3
misroutes process lessons (G4) and step 4 ("Put it in the *bigger* file") is a coin flip. Meanwhile
the growth rule that actually decides most filings sits 20 lines further down under a different
heading, and the backend-symmetry override is not there at all. The section reads authoritative and
is the least reliable part of the file.

**H3.3 — `EPD-004`'s in-place-correction style is right in principle and past its density limit at
1418 lines.** The style is stated and defended (`:14-15`, and it is the right call), but by decision
16 the reader is tracking four layers at once: the original proposal, the 2026-08-15 decisions, the
2026-08-16 revisions, and corrections-to-the-revisions — with the fork text kept separately at
`:1244-1298`, meaning fork 5's *proposal* sits 750 lines below fork 5's *decision*. Reading it
forward, it is not possible to tell what fork 6 currently says without holding `:542-565`,
`:647-662`, `:1292-1298` and `:199-202` in view together. Not a request to cut it. A "current state"
header block — *seven reference files; Milestone 2 starts at Phase 8; the manual is
`docs/README.md`* — would cost ten lines and save every future reader the reconstruction. `:3`'s
"Nothing has been moved yet" is where that block should live.

**H3.4 — `measurements.md`'s "as above" chains break at the section boundary.** Rows 49-59 use "as
above" for both Instrument and Slice across eleven rows and two intervening full-width cells; by row
55 the reader must scroll back to row 48 to recover what "as above" referred to, and in row 51 the
Instrument cell restarts naming instruments mid-chain. This is the file most likely to be read by
jumping to one row.

**H3.5 — `reference/README.md:52` and `procedures/README.md:43` sign themselves "at commit 5 …
completed at commit 6".** Under decision 22 that vocabulary is retired everywhere except Phase 7's
own `plan.md` and `notes.md` (`README.md:320-323`). These are reference-tier files, not archive, and
their provenance footers now use a unit the manual says is not the unit of work. Whether the
forward-only exemption is meant to cover *citations of* Phase 7's numbering is unstated — see Q2.

### 4. Questions for the human

**Q1 — Which file owns the branch convention?** Both `CLAUDE.md:148-161` and `README.md:251-270`
state it in full and have already diverged (C11). `design-decisions.md:133-142` shows the
established pattern for resolving this. Is the intended answer "CLAUDE.md owns it, the manual
points"? If so the manual's copy needs cutting; if not, the reverse.

**Q2 — Is Phase 7 complete?** `status.md:14` says all fifteen commits are done, but four commits
landed after `eae1489` (the one that filed the phase and wrote the closing playbook), none of them
naming a task, and one of them — `32bf409`, decision 22 — changes a convention the phase's own plan
is written in. Either the plan gained tasks 16-19 that were never published, or the phase closed and
then kept going. Decision 11's new check ("did every phase complete the task list it published?")
cannot answer this from `git log`, which is the check's stated purpose.

**Q3 — Are EPD addenda frozen or live?** `README.md:112-116` freezes phase notes and `:170` sends
corrections to `reference/`. Nothing says which rule EPDs follow. Today `EPD-001` and `EPD-002`
carry Phase-4-era claims that Phase 5 retired (C9), and both documents are *proposals waiting on a
decision* — the person taking that decision reads the stale version. Two readings are defensible: an
addendum is a dated record like a phase note, or an EPD is live until decided. The answer changes
whether the "sweep the other documents" rule at `:175-176` reaches `docs/epd/`.

**Q4 — Growth rule or symmetry, for the next backend?** (G5.) `backend-anthropic.md` exists at 94
lines today but was created at 13, against the 40-line rule, on a symmetry argument that lives only
in `EPD-004`. When someone adds Ollama or vLLM, does `reference/backend-ollama.md` exist on day one?

**Q5 — Where does a finding go when there is no phase?** All three of the manual's worked examples
(`:379-397`) and the correction rule (`:170`) route through "the phase note that made it". This
review is a counter-example, and so is anything on a `fix/` branch — `README.md:254` explicitly
contemplates "a defect outside a phase". The measurement has nowhere to be primary, only somewhere
to be corrected.

**Q6 — Should `measurements.md` grow anchors, or should decision 1 be re-minuted?**
`EPD-004:454-459` is unusually honest here: the mechanism fork 1 chose was citation-by-anchor,
"**nothing in the repository cites `measurements.md` by an anchor** — not once", and that is also
why `link-check.py` never learned to resolve one. `README.md:146` still advertises "linked by
anchor" as the scheme. Half a decided mechanism is in use and the manual documents the unused half.

### What the reviewer did not check

- **`docs/milestone-1-core/**` and `docs/captures/log-the-whole-request.txt`** — out of scope. It
  opened `milestone-1-core/README.md`, `phase-6/notes.md` and the `Branch:` lines only to verify
  citations pointing *into* them, and `captures/README.md` only for C17.
- **`src/` and `tests/` as code.** It read the seven doc citations, `stats.py`'s `COLUMNS` (all 20,
  exact order match to `observability.md`), `observe.py`'s `MAX_SCAN_BYTES`, `app.py`'s four routes,
  and the ruff pin and line length. It did not review behaviour.
- **Anything requiring live traffic.** Nothing re-measures LM Studio, Anthropic, or Claude Code.
  Every LM Studio number in `backend-lmstudio.md` and every Phase 4/5 row in `measurements.md` is
  cited to a frozen transcript it did not open — it verified only the frozen 2026-07-31 CSV (14
  numbers) and the `git`/`make test`/line-count claims. **So `backend-lmstudio.md` is the largest
  in-scope file effectively not verified**, and `measurements.md:52` already flags that one of its
  rows (9166 → 115073 ms) has no frozen artefact at all.
- **`EPD-001`, `EPD-002`, `EPD-003` in full.** It read openings, addenda, `EPD-001`'s confidence
  table and cross-reference sections, and `EPD-003`'s reversal analysis. It did not audit their
  internal arguments or their numbers; `measurements.md:118-121` carries four EPD figures it did not
  recompute.
- **`EPD-004` decisions 18-20 and the original forks** were read once, not audited line by line.
  Given the density noted in H3.3, there may be further stale cross-references between the decision
  text and the fork text it did not catch.

---

## Part 4 — one finding from earlier in the session, not from the review

Raised separately when the owner asked whether `.claude/` had been forgotten. **Investigated,
proposed, and deliberately not acted on** — the review agent was reading the same documents at the
time and editing them would have moved the line numbers its findings cite.

**`.claude/settings.json` correctly does not exist.** `EPD-004` decision 17 decided the split and
deferred building the tracked half; `README.md:242` says "today only the local file exists";
`backlog.md` carries it as parked work. Working as designed, and it is one of the seven permanent
link-checker hits for exactly that reason.

**The real gap: this repository's `.gitignore` says nothing about `.claude/`.**

```
git check-ignore -v .claude/settings.local.json
→ /Users/ilirium/.config/git/ignore:1:**/.claude/settings.local.json
```

The file is ignored by the **owner's global git config**, not by the repository. But both documents
describe the untracking as a property of the project — decision 17 says "51 entries, git-ignored",
and `README.md` says "The untracked `.claude/settings.local.json`". On any other machine, or for any
contributor, that file is untracked-and-visible and a `git add -A` commits it. It has never happened
here only because of a setting that is not in the repository.

**And a decision-20 problem in the same paragraph.** Decision 17 says the local file holds **51
entries**. It holds **53** — it grew during this session, from clicking allow. The number's job is
to size the mess and justify the split, which it can still do, but it describes a file that accretes
by design and will drift forever. It wants a date and a recipe in the sentence, or no count at all.

**Proposed, not done:** add `.claude/settings.local.json` to the repository's `.gitignore` with a
comment saying why the tracked sibling is deliberately *not* ignored; correct both documents to say
the local file *should be* ignored by the repository rather than asserting it already is; pin or
drop the 51.

---

## Part 5 — where this stopped, and what to pick up

**Nothing in this file has been acted on.** Tree clean at `32bf409`, branch unmerged.

**Suggested order, by consequence rather than by ease:**

1. **`measurements.md:34`** (V1/C14) and **`README.md:381`** (V3/C2). Both make a future session act
   wrongly: one hands a reader a number with the sign reversed, the other tells them to create a
   second Phase 7.
2. **The four other confirmed factual errors** — `README.md:20` six phases (V2), `.env.example:5`
   (V4), decision 22's "twenty-one commit messages" and "21 commits from 15 units" (V5), and the
   `status.md:20` "every citation in the repository" claim that V4 falsifies.
3. **Verify the remaining ~25 findings before touching them.** They are reported with citations and
   the reviewer showed its work, but they were not independently re-checked, and this repository's
   most-repeated lesson is that claims get quoted forward without being checked.
4. **The closing playbook** (G1). Bigger than the rest and it wants its own task: the generic
   procedure from decision 12 restored, with the restructure narrative kept alongside rather than
   instead of it.
5. **The `.gitignore` fix** (Part 4), which is independent of everything above.

**Six questions are open for the owner** — Q1 to Q6 in Part 3. Q5 decides where this file itself
belongs. Q2 decides whether Phase 7 is even closed.

**One thing worth carrying forward regardless of what gets fixed:** the fresh-context review found
three errors in numbers written the same day by the agent that wrote the lesson about exactly that
failure. That is the strongest argument yet for the review phase being a standing part of a
milestone (`EPD-004` decision 11) rather than something done once.
