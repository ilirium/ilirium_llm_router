# Status

**State, not inventory.** Unscheduled work lives in `backlog.md`; this file says where the project
is and what is in flight. Three sections, most volatile first.

---

## Where we stopped

*Changes every session. If this section passes ~30 lines, or starts carrying anything that outlives
the session that wrote it, it has become a document and gets its own file.*

**2026-08-21 — Phase 10 is complete and the merge is the next action.** All thirty-three tasks are
done and `make test` is **310**. The branch is `feat/phase-10-body-store`, forked at `d885b2f`; the
permanent record is `milestone-2-corpus/phase-10-body-store/`.

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
| **2** | The corpus — capturing bodies for analysis | 8– | **open**, two phases in | `milestone-2-corpus/implementation-plan.md` **until the milestone closes**; its `README.md` is a closing artefact and does not exist yet |

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

**One of its three failure modes is already discharged** by Phase 9's measurement; the other two —
that archiving cannot stay opaque, and that it slows a call — are Phase 10's to test.

**Two phases done, neither touching `src/`** — Phase 8 built the method tier and the guardrails, Phase 9
decided `EPD-003` and ran the gate that named the claim above. **Phase 10 is the first of this milestone
to touch `src/`.** `milestone-2-corpus/implementation-plan.md` describes both phases; **their merge
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

1. **Merge `feat/phase-10-body-store`, then exercise the corpus by hand.** The phase is finished and
   the merge is the only action left in it. **It closes two placeholders** — the Record table at the
   foot of `plan.md` and `notes.md`'s first line, which reads *"Not yet merged."* Both are named in
   `plan.md`'s "Placeholders in this file", which is the section that exists so they are not
   forgotten, and neither can be written until the merge commit has a hash. **The owner then drives
   the corpus against a real session** before any new work opens — the store has been driven by
   Phase 10's own checks, never by its owner in ordinary use.
   *(This item read "Execute Phase 10 — the body store, from Task 16 (Group E)" until 2026-08-21,
   eight tasks after it stopped being true. It is the defect this file's own milestone-table entry
   describes: prose that undercounts goes stale invisibly, where a missing row would not.)*
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

*Merged branches are not listed — git already holds that, and a hand-maintained list would drift.
The permanent record of a phase's branch, fork point and merge commit belongs in its phase note.*

| Branch | Purpose | Tree | Next |
|---|---|---|---|
| `feat/phase-10-body-store` | Phase 10 — the body store, forked at `d885b2f` | docs, the benchmark instrument, `pyproject.toml` / `uv.lock`, and **the whole store: `corpus.py` new, `config.py`, `proxy.py`, `observe.py`, `app.py`, `cli.py` and `config.yaml` all changed, `tests/test_corpus.py` new — and now **`dictionary.py` new, `tests/test_dictionary.py` new**, with `corpus.py` gaining the shared `newest_dictionary()` / `write_atomically()` and an `on_day_rollover` hook, and `app.py` starting the training thread, and `cli.py` carrying `--train-dict` / `--tune-dict` / `--from`. `make test` **310**.** `plan.md` now carries **"The register"**, and every value in it is settled, and the telemetry paths now read `logs/telemetry/` | **The merge, and it is the owner's.** **All thirty-three tasks are done**; Task 18 ran, nine of ten observations first time and the tenth after **Task 18a** made it performable at all; `make test` 310 — **E moved nothing on disk**, on the owner's decision, so `logs/telemetry/` does not exist until the router next starts; the benchmark is frozen in `evidence/`, and the executor was chosen from measurement rather than argued. The trainer measured **0.03 s**, so the `TRAIN_BUDGET_S` gate permits day-rollover triggering — **re-measure, do not inherit.** **Re-scoped and re-reviewed 2026-08-19** to thirty-two tasks — the router retrains itself, `13a`/`14a`–`14f` are lettered because execution has begun, and `14d` is **struck and absorbed into Task 11**. The tree also now carries `docs/wiki/`, `procedures/event-loop-lag/` and an `attribution` block in `.claude/settings.json` |

*`docs/phase-9-corpus-gate` merged as **`b29d502`** on 2026-08-17 and this table was empty until Phase
10 opened.*

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
