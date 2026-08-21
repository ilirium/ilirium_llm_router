# Status

**State, not inventory.** Unscheduled work lives in `backlog.md`; this file says where the project
is and what is in flight. Three sections, most volatile first.

---

## Where we stopped

*Changes every session. If this section passes ~30 lines, or starts carrying anything that outlives
the session that wrote it, it has become a document and gets its own file.*

**2026-08-21 — four method items added on the owner's instruction: `IDM-007`, `IDM-008`, a reading
rule and a `notes.md` split.** Two of the four were **already in the repository and neither was a new
rule.** `IDM-008` generalises Phase 10's register, which the owner instructed on 2026-08-19 in almost
the same words; the reading rule is `wiki/claude-code-context-budget.md`'s lever 2, which needed a
**trigger** in `CLAUDE.md` rather than a home. **Checking before writing is what found both**, and it
changed what got written: `IDM-008` carries Phase 10's four findings as its argument instead of an
assertion.

**`IDM-007` is the one that is genuinely new**, and its evidence is three prior instances *about
documents rather than people* — `IDM-005`'s step 2 caveat sitting below the stop line where a
compliant reader never reaches it, and this file's own two records of prose that undercounts going
stale invisibly. Same mechanism each time: something true, written down, in a place that does not
reach the reader.

**Two of the four were argued down from what was proposed, and both are recorded where the argument
is.** `IDM-008` was proposed for `CLAUDE.md` and is a **pointer** instead — writing a plan is a
look-it-up moment, which is why `IDM-005` and `IDM-006` are pointers too; `IDM-000` now states that
neither shortness nor importance earns a restatement. The `notes.md` split is **forward-only**:
Phase 10's 3,284-line `notes.md` stays whole, because `notes.md:2143`-style citations break
**silently** when a section moves — `link-check.py` checks paths, not line numbers.

**`CLAUDE.md` is 292 lines, up from 260**, and the growth was accepted deliberately against upstream's
~200 guidance. The measurement of what it could lose is in `backlog.md` as a review-phase item, which
is the condition it was accepted under.

**2026-08-21 — the branch index exists, on `docs/branch-index`, and it is generated rather than
written.** `reference/branches.md` carries all nineteen merged branches — opened date and fork point,
merge date and merge commit, milestone, phase, and one line on what each was for. Five of its six
columns come out of git via `procedures/branch-index.py`; only the description is typed.
**`IDM-001` refused exactly this list on 2026-08-17** — *"a hand-maintained list would drift"* — so
the amendment is narrow and keeps the objection: derived factual columns, hand-written interpretive
one, and `--check` exits 1 when a branch has landed without a row. **Regenerating is part of the
merge**, which is `CLAUDE.md`'s sixth restated fact and the reason it earned a place there:
a merging session does not know the file exists.

**Enumerating refs found a branch nobody had written down.** `docs/add-claude-md` — five commits on
2026-07-27, the README, `CLAUDE.md`, the design decisions and the first implementation plan. **It is
the repository's first branch and appeared in no document for twenty-five days.** No rule was broken:
it belongs to no phase and was fast-forwarded, so until `IDM-001` gained its third row there was
nowhere to record it. Two counts move with it — there are **three** fast-forwarded branches where every
sentence says two (each correct, each counting *phases*), and **eight of nineteen** branches carry no
phase number.

**Baselines, run 2026-08-21: `make test` 310, `make lint` clean.** `link-check.py` is quoted as a
**delta** on purpose — this branch adds **one file and no broken path**, measured by running it on
`main` and on the branch in the same checkout. The absolute count depends on files git does not
carry, which is why the figure above and the one in `procedures/link-check.py`'s docstring disagree
without either being wrong. **Both refusal paths of the new script were driven, not assumed**: a
deleted row makes `--check` exit 1, and a missing description makes `--write` refuse rather than
splice a blank column.

**2026-08-21 — Phase 10 is merged as `32c26bb`, and the next thing is the owner driving the corpus.**
All thirty-three tasks done, `make test` **310**, `feat/phase-10-body-store` forked at `d885b2f` and
merged `--no-ff`. **Both placeholders closed with it** — the Record table at the foot of `plan.md`
and `notes.md`'s first line — which were the only two the phase left standing. The permanent record
is `milestone-2-corpus/phase-10-body-store/`.

**Trimmed to the current state on 2026-08-21, on the owner's decision** — it had reached ~560 lines
against the ~30 above, in fifteen entries back to 2026-08-18. **Nothing was lost:** each restated
what `phase-10-body-store/notes.md` holds as frozen-primary, the case the rule names.

**Three documentation defects were closed the same day**, on the owner's instruction and outside any
review phase. `reference/measurements.md`'s intermediate-slices row stated its slice as *"26.6× (no
warmup probes)"* while silently inheriting the `/v1/messages` filter from the row above it, so read
as written it recomputed to **0.245×** with the sign reversed. **All four slices were re-derived from
the frozen CSV rather than relayed**, and the warmup predicate — which produced two plausible wrong
answers first, 23.4× and 0.216× — is now written down beside them, which no document had done. The
four `Branch:` lines that still said *"Merge back with `--no-ff`"* now carry their merge commits, and
the in-flight table below no longer reads `make test` **308** in one clause and **310** in the next.
The first two are recorded in `backlog.md` rather than deleted; the wider review stays parked.

**What Phase 10 does not claim, stated in the documents rather than only here.** **Failure mode 3 is
not discharged** — archiving cannot *break* a call, which was driven, but whether it *slows* one is
unmeasured and needs a driven session with capture on against off. **A call can still vanish**; Task
18a made that visible rather than impossible, and closing it needs a guarantee that a row can never
be written twice. **There is no headline compression ratio**, on the owner's instruction: every
figure is a small-sample confirmation that the mechanism works.

**Baselines, run not predicted 2026-08-21: `make test` 310, `make lint` clean, `make check` valid,
`link-check.py` 86 files, 75 broken, 2 roundabout — unchanged, correctly: today's edits added no
`*.md` file and cited nothing that does not already exist.** *(`make test` is ~2 s warm; a **first**
run after the cloud folder evicts the virtualenv takes two to three minutes on hydration alone —
slow, not stuck.)*

## Where the project is

*Changes every phase.*

**One row per milestone. Per-phase detail lives in the archive** — branch, fork point and merge commit
belong to the phase note, and each milestone's own index reads its phases in order.

| | Subject | Phases | State | Read it in |
|---|---|---|---|---|
| **1** | The core router — dispatch, byte-relay, observability, failure handling | 1–7 | **complete** 2026-08-07 | `milestone-1-core/README.md`, which carries every branch and merge hash with what each phase settled |
| **2** | The corpus — capturing bodies for analysis | 8– | **open**, three phases in — 8, 9 and 10, the last merged 2026-08-21 | `milestone-2-corpus/implementation-plan.md` **until the milestone closes**; its `README.md` is a closing artefact and does not exist yet |

*Changed 2026-08-17 from a per-phase table of Milestone 1's merge commits, per the `backlog.md` item
that proposed it. **The hashes are not lost** — each one keeps two to six homes, the fewest being
`532dc86` and `9c30924` at two apiece, and `milestone-1-core/README.md`'s table is strictly richer than
the one removed. What this file kept is
the part that is **state**; a closed milestone's per-phase merge hashes are archive record, and
`status.md` says so at the top.*

Phases 0 and 1 were fast-forwarded before the `--no-ff` convention existed;
`milestone-1-core/README.md` says why they are left that way. **Milestone 2 starts at Phase 8**,
since 7 is taken.

**What Milestone 1 settles:** no protocol translation is needed, and a local model can drive a real
coding session through the router. Both halves were measured rather than argued — one session reached
both backends, and a local model handled tool use, file editing and multi-turn conversation.

**Milestone 2's subject is `EPD-003`** — capturing bodies for a corpus, **decided 2026-08-17**.

**Its central claim is now named**, at the end of Phase 9 and from what the gate returned:

> *The router can archive every body it carries — as opaque, content-addressed, per-call files
> compressed against a shared dictionary — without parsing a payload, without slowing a call, and
> without special storage infrastructure.*

**Two of its three failure modes are discharged**, and the third is not. Phase 9's measurement
settled the storage-infrastructure half; **Phase 10 settled that archiving cannot stay opaque** — tar
a day folder, unpack it elsewhere, and every blob opens and verifies against the digest in its own
filename. **Whether archiving slows a call is untested**, and is parked in `backlog.md`.

**Three phases done. The first two touched no `src/`** — Phase 8 built the method tier and the
guardrails, Phase 9 decided `EPD-003` and ran the gate that named the claim above — **and Phase 10 is
the first of this milestone that did**, merging 2026-08-21 as `32c26bb`.
*(Both sentences above were stale between Phase 10's close and this edit: they said two phases and
that Phase 10 had the opaque half still to test. **That is the paragraph below happening again, to
the paragraph that describes it** — prose that undercounts goes stale where a missing table row would
be visible. Recorded rather than quietly fixed, because it is now the second instance.)*
`milestone-2-corpus/implementation-plan.md` describes all three; **their merge
hashes are in their phase notes**, which is where `method/IDM-001-git-branching.md` puts the permanent
record. *(This sentence first said the plan indexes both hashes. It carries Phase 8's and not Phase 9's
— the plan's Record table records the branch **that file** was created on, which was Phase 8's.)*

*This paragraph carried both merge hashes and a note deferring to the `backlog.md` item above. **That
item is now decided and this is the evidence it asked for:** the prose version said "one phase of it is
done" after Phase 9 merged, and stayed wrong until the owner noticed — while the per-phase table beside
it never went stale, because a merged phase without a row is visibly missing and a sentence that
undercounts is not. **The conclusion is not "prefer tables"** — it is that the row-versus-prose choice
is about what goes stale invisibly, which is a different axis from the duplication the item was
arguing.*

## What is next

*Changes every phase. Two or three items lifted from `backlog.md` and cited to it — the file itself
is the full inventory.*

1. **Exercise the corpus by hand — the owner's, and it comes before Phase 11 opens.** The store has
   been driven by Phase 10's own checks and never by its owner in ordinary use. **It is off by
   default**, so turning it on is the first step and no `logs/corpus/` until then is correct
   behaviour; `reference/corpus.md` is the spec and names what else a session gets wrong from the
   name alone. **`logs/telemetry/` does not exist yet either** — the router creates it on its next
   start, and the old `logs/calls.csv` and `logs/router.log` were deliberately left where they are.
   *(This item read "Execute Phase 10 — the body store, from Task 16 (Group E)" until 2026-08-21,
   eight tasks after it stopped being true, and was then the merge until the merge happened. It is
   the defect this file's own milestone-table entry describes: prose that undercounts goes stale
   invisibly, where a missing row would not.)*
2. **Plan Phase 11 — and its subject is deliberately not chosen here.** The candidates are in
   `backlog.md`, which is the full inventory; picking one is a planning decision, not something the
   next session inherits from this file. **`EPD-003`'s open questions 3–6 are not among them** — they
   were closed in `EPD-003` itself on 2026-08-20 at Task 20, three answered and retention marked out
   of scope for Milestone 2 on the owner's decision rather than answered.
3. **Decide `EPD-001` or `002`.** Both are blocked on a person rather than on work, and both are argued
   on a case Phase 4 measurably weakened — see `backlog.md`, "Decisions waiting on a person". Deciding
   one is cheaper than any measurement in the list, and neither decision waits on Phase 11.
   (`EPD-003` is no longer among them — decided 2026-08-17 by Phase 9.)

*The measurement items are both in `backlog.md` under "Measurements left open" and neither is listed
here as next, because the owner has not chosen Phase 11's subject and this file is not the inventory.
Whether Claude Code shows LM Studio's context error was already there. **Whether archiving slows a
call was added there on 2026-08-21** — until then it lived only in `prompt.md`, which is the one file
allowed to go stale, and in `milestone-2-corpus/implementation-plan.md`'s table.*

## In-flight branches

*Merged branches are not listed here — this section holds live state. **They are indexed in
`reference/branches.md`, generated from git**, which is the 2026-08-21 amendment to
`method/IDM-001-git-branching.md`: a hand-maintained list would drift and a derived one cannot. The
permanent record of a phase's branch, fork point and merge commit is still its phase note.*

**None. The table is empty as of 2026-08-21**, when `docs/branch-index` merged as **`3233fb7`** and
its row went with it — forked at `5352d0d`, six commits, documentation only. **Phase 11 still has no
branch because its subject is not chosen** — the plan opens the phase branch, so there is nothing to
list until one is.

*What that branch was is no longer this file's job to remember, and that is the point of it.* It
carried no phase number, so it has no phase note; its permanent record is **its merge commit
message**, which `IDM-001`'s third row added on the day it was needed, plus **its row in
`reference/branches.md`**, which the fourth row added the same day. The branch that exposed both gaps
is the first to be recorded by both.

*It was empty in exactly this way once before: `docs/phase-9-corpus-gate` merged as **`b29d502`** on
2026-08-17 and nothing replaced it until Phase 10 opened. The permanent record of both — branch, fork
point and merge commit — is in the phase notes, which is where `method/IDM-001-git-branching.md` puts
it and why this section may go empty without losing anything.*

**It was a `docs/` branch although the phase was about the router**, because no `src/` change survived
it: Task 6 patched `proxy.py` and restored it, and `git diff main -- src/` was empty at the merge.
`method/IDM-001-git-branching.md` is what makes that the right prefix — the prefix says what kind of
work it is, and `phase-N-` says it is numbered work. **Phase 10 is the opposite case**, and it is: `feat/phase-10-body-store`,
opened 2026-08-18. *(This sentence read "will be" until then.)*

`docs/phase-8-method-and-guardrails` was the first branch to **carry a phase number on a `docs/`
prefix** — the form it settled: the prefix says what kind of work it is, `phase-N-` says it is a phase.
`method/IDM-001-git-branching.md` now states that as the rule, with Phase 7 as the old form and Phase 8
as the new one. `main` is ahead of `origin/main` and nothing has been pushed;
`docs/milestone-boundary-restructure` and `docs/phase-8-method-and-guardrails` both still exist locally.
