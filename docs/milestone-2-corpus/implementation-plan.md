# Milestone 2 — the corpus: implementation plan

**Opened 2026-08-17 on `docs/phase-8-method-and-guardrails`, forked from `main` at `6253cbc`.**

Written at **decreasing resolution**, per the opening playbook's step 6: the next
phase in full, the one after in outline, the rest as a title and the question it exists to close.
Plans here are wrong on contact often enough that detail beyond the next phase is waste. **How
often is `../reference/lessons.md` lesson 1's to say, and that file is canonical** — this sentence
carried its own count until 2026-08-21, and both halves of it were wrong.

*The opening playbook moved from `../README.md` to `../method/IDM-005-opening-a-milestone.md` on
2026-08-20 with its steps unchanged, and was then **amended on 2026-08-21**: the old step 2 folded
into step 1, leaving seven, renumbered. Every reference to it in this file is to the seven-step
form.*

---

## The central claim, named 2026-08-17 at the end of Phase 9

> **The router can archive every body it carries — as opaque, content-addressed, per-call files
> compressed against a shared dictionary — without parsing a payload, without slowing a call, and
> without special storage infrastructure.**

**Three ways it could come out false**, which is what makes it a claim rather than a plan:

| It fails if | Status |
|---|---|
| **The size forces infrastructure** — per-call files cost so much more than a stream that a database or blob service becomes the answer | **Tested in Phase 9 and survived.** 12.10× held-out against 3.12× unaided; per-file lands at 2.47× a stream, and a year of use stays in the low hundreds of MB |
| **Archiving cannot stay opaque** — something in the write path turns out to need the body parsed | **Tested in Phase 10 and survived.** The write path hashes and compresses **raw bytes** and never parses one. `peek()` still reads `model` and `stream`, but it predates the corpus, reads a copy, and rewrites nothing — the stored blob is the arriving bytes. Task 18 read five bodies back off disk **byte-identical to what the client sent**, and a day folder unpacked elsewhere opened all of them |
| **Archiving slows or breaks a call** — a 200 KB blob cannot leave the request path the way a 300-byte CSV row can | **NOT discharged, and this phase says so rather than letting the table imply otherwise.** *Half of it survived:* archiving cannot **break** a call — the queue is byte-bounded, drops rather than stalls, and Task 18 saw a forced drop become a row with `dropped` in both ref cells, one `WARNING`, and no blob. **Whether it *slows* one is unmeasured.** The scope had no live session, and in-process timing is not the same measurement. What would settle it: **one driven session with capture on against one with it off**, comparing `ttfb_ms` and `duration_ms` over the same work. A later phase, or an addendum |

**Read the first row's numbers as small-sample confirmations that compression works, not as
performance claims.** *Added 2026-08-20, on the owner's instruction at Phase 10's Task 21.* Every
compression figure this milestone owns comes from a handful of sessions — Phase 9's from 73 bodies,
Phase 10's from 21 held out — and they exist to show the mechanism functions, not to advertise a
ratio. **A number here is evidence that the gate was passed, not a specification.**

**Non-goals**, named now rather than discovered later:

- **Fine-tuning.** Decided out on 2026-08-17 — the corpus is for analysis. Anthropic's terms prohibit
  using outputs as training targets, and this removes the need for a structural provenance split.
- **A database, a query engine, or a schema for message content.** The corpus is files; an export step
  is an offline concern.
- **Reconstructing transcripts inside the router.** Bodies go in opaque and come out opaque.
- **Changing `calls.csv`.** Not its rotation, not its columns. It is a comparison instrument over a
  recent window, and the corpus brings its own durable index.
- **Retention for the corpus.** *Added 2026-08-20, on the owner's decision, closing `EPD-003`'s open
  question 5.* Nothing deletes an archived body, and **no policy was decided, designed or deferred to
  a trigger** — this milestone declines the question rather than answering it. It may become a feature
  in a later milestone. **Not in `../backlog.md`, deliberately:** that file holds unscheduled work,
  and this is a scope boundary, which belongs here.

---

### Why this section was blank until Phase 9, kept as written

The opening playbook's first step is to name a falsifiable central claim. **It was not written here,
and the blank was the honest state rather than an omission.**

Milestone 2's subject is `../epd/EPD-003-capturing-bodies-for-a-corpus.md`, which was still a
**proposal** when this was written. A central claim written then would have been written against a
document that may not survive its own gate.

*Updated 2026-08-17, Phase 9 Task 4. `EPD-003` is now **partly accepted**: fine-tuning is dropped and
the corpus is for analysis only. **The blank still stands**, because the half that was decided is not
the half a central claim would rest on — the storage question is open until the gate runs, and that is
exactly the document-may-not-survive risk this section was written about.* Milestone 1's spec is the precedent and the warning: it was *"reliable where it recorded
measurements and unreliable where it recorded predictions, with both in the same prose"*, and
several of those predictions stood unchallenged for five phases.

**When it is named:** after EPD-003 is decided and its gate has been run. That is Phase 9. *(It was,
and it is — above. The discipline held: the claim is written from what the gate returned, and one of
its three failure modes is already discharged by measurement rather than by assertion.)*

**What this costs, named rather than waved away:** Phase 8 runs without a milestone-level claim to
serve. That is acceptable only because Phase 8 is housekeeping which would be worth doing under any
claim — it changes no `src/` and settles conventions the milestone will use whatever it decides. **A
phase that shapes the router must not start before the claim exists.**

**Non-goals:** not yet named, for the same reason. *(Named above, 2026-08-17.)*

---

## The phases

### Phase 8 — the method tier and the guardrails *(in full)*

`phase-8-method-and-guardrails/plan.md`, beside this file. **Seventeen tasks in three groups** of
housekeeping, each of which blocks cheap work later and none of which depends on EPD-003:

1. **The Git branching rules are in two documents and they disagree** — seven differences. Unified into
   one numbered method document, `docs/method/IDM-001-git-branching.md`, cited from both. This also
   establishes the `docs/method/` tier and the **IDM-NNN** numbering scheme in `IDM-000`.
2. **A tracked `.claude/settings.json`.** `EPD-004` decision 17 split the permission allowlist into
   a tracked policy half and an untracked local half, and only the local half existed. Interviewed and
   settled 2026-08-17; `IDM-002` holds the reasoning.
3. **Two tooling decisions with no home** — the ruff pin, and `ty`, which was tried and refused with the
   refusal recorded nowhere. `IDM-003`. This group emerged from group B's review rather than being
   planned.

**Done when:** the tier holds `IDM-000` through `IDM-003` and no `README.md`; the branching rules have
exactly one home, with `CLAUDE.md`'s restatement labelled as one; the tracked settings file exists with
an exact-match `.env` deny and its sibling ignored by *this* repository's `.gitignore`;
`procedures/link-check.py` reports only its known-permanent hits, re-derived by running it; and
`make test` still reports 158.

*This section said "two small pieces of housekeeping", that the settings half was "not yet specified —
the owner has not been interviewed on it", and that Phase 8 was done when "both documents exist". All
three were true when written on 2026-08-17 and false by the end of the same day. Corrected in place at
Task 17a, which the plan did not contain — the phase's own re-derivation found it.*

### Phase 9 — decide EPD-003, and run its gate *(in full)*

`phase-9-corpus-gate/plan.md`, beside this file. **Sixteen tasks in four groups**, on
`docs/phase-9-corpus-gate` — a `docs/` prefix because no `src/` change survives the phase.

**The question it closes:** does the corpus proposal survive its own cheapest test?

*Raised from outline to full on 2026-08-17, when the phase opened. The two halves below are what this
file said then, and both still hold — but the outline **understated the first**, which is Finding 1 of
the phase's re-derivation.*

Two halves, in this order:

- **The gate — a twenty-minute measurement.** Whether a trained zstd dictionary recovers the
  cross-body compression ratio for per-file storage. **If it does not, per-call files are the wrong
  unit and the sketch does not survive.** Stated in `../backlog.md` and argued in EPD-003.
- **The decision the gate cannot make.** Whether the fine-tuning half of the goal survives
  Anthropic's terms. That is a person's call, not a measurement's, and the corpus may be worth
  building for analysis alone even if fine-tuning is cut. **Taken 2026-08-17: fine-tuning is dropped,
  analysis only.** The last clause of that sentence is what happened.

**The milestone's central claim is written at the end of this phase**, from what the gate returned.

*Everything below Phase 9 is a title and a question. Nothing about it is planned.*

### Phase 10 — the body store *(record — executed 2026-08-18 to 2026-08-20)*

**The question it exists to close:** what does the router store, and where. **Phase 9 answered the
prerequisite** — per-call files are the unit — so this is now answerable and is a `feat/` phase, the
first of this milestone to touch `src/`.

**Its shape is already sketched.** `phase-9-corpus-gate/plan.md` carries a fenced section, "Design
produced by the interview", holding the tree, the dictionary lifecycle and the reasoning behind each
choice. **It was written conditional on the gate, and the gate passed, so it stands as input** — but it
is a sketch produced before any of it was built, and this phase's first act is to re-derive it.

What it must settle, beyond the sketch:

- **The write path.** A bounded off-thread queue, and an explicit answer to what happens when it fills.
  `EPD-003`: *drop the body and record that it was dropped* — a corpus with a known hole is fine, a
  stalled request is not. This is the second of the central claim's three failure modes.
- **`EPD-003`'s open questions 3–6**, which it left as design detail: what is captured by default,
  opt-in versus always-on, retention, and whether headers are stored. Question 6 is the sensitive one —
  headers carry the credential.
- **Capture at the point of failure, not only in the streaming path.** Phase 9 measured its own
  throwaway hook missing **9 of 158** calls, all of them error paths that return before the response
  generator runs — which is precisely the class `EPD-003` calls *"the interesting rows, not the broken
  ones"*.
- **A dictionary bootstrap and retraining policy**, given that `zstd --train` was measured
  non-monotonic at 68 samples. A new dictionary must be compared against the one it replaces.
- **Move `calls.csv` and `router.log` into `logs/telemetry/`**, alongside the new `logs/corpus/`. Small,
  and deliberately bundled here rather than done as a `chore/`: it touches `config.yaml` and paths cited
  from `src/` docstrings, which `link-check.py` cannot see, so it wants one move and one sweep rather
  than two.

**What it actually built, 2026-08-20.** Thirty-three tasks in six groups — thirty-two planned, plus
**Task 18a** inserted during execution. `corpus.py` and `dictionary.py` are new; `config.py`,
`proxy.py`, `observe.py`, `app.py`, `cli.py` and `config.yaml` changed. **`make test` 158 → 310.**
The store writes content-addressed per-call blobs into UTC day folders against a shared dictionary,
each day folder carrying a **plain copy** of every dictionary its blobs reference, so it opens
elsewhere from itself alone. The router **trains its own dictionary** offline in a thread, installs
one only when it beats the incumbent by a margin, and picks up a dictionary another process installed
without restarting. `calls.csv` and `router.log` moved to `logs/telemetry/`.

**The record of what was found, not just what was built.** The phase's defects were found by
**driving and by attacking the tests**, never by the suite as written — a dictionary built from
unvalidated bytes that silently destroyed its own blobs, a leakage that produced a plausible
`26.210x`, a second `26.870x` by a different mechanism the same day, and a counter pair that counted
correctly and **reported nothing**. `phase-10-body-store/notes.md` carries all of them.

**One thing it did not build, deliberately: it does not close the recorder's blind spot.** Task 18a
made the loss *visible* — a caller already gone at response-start leaves no row, now observed rather
than theorised — and the owner's decision was to **report the hole, not close it**, because writing
the row from elsewhere must guarantee it can never write one twice.


### The closing review phase — *unnamed, number unallocated*

Every milestone closes with one, specified as measurement rather than removal; the checklist is in
`../README.md`. It touches `src/`, so it is a numbered `feat/` phase. **Its number is not allocated
here** — phase numbers are globally sequential and how many phases sit between Phase 9 and the close
is not known.

---

## What is deliberately not done yet

The opening playbook has seven steps. **Steps 1–6 are not run**, and this section exists so that a
later session does not read their absence as an oversight.

| Step | State |
|---|---|
| 1. Name the falsifiable central claim, the non-goals, and what would refute it | **deferred to Phase 9** — see above. The refuting experiment *is* Phase 9's gate |
| 2. Capture the real input | **NOT discharged** — settled 2026-08-17 by Phase 9's re-derivation. `docs/captures/` holds **one** body, and one body cannot exercise a cross-body dictionary. Phase 9's Group B spends it |
| 3. Spike whatever the architecture depends on | not started |
| 4. Settle the expensive-to-reverse questions as EPD forks | **EPD-003 already is one.** Whether it needs a sibling is unknown |
| 5. Write the spec, marking every statement measured / inferred / assumed | not started |
| 6. Write `implementation-plan.md` at decreasing resolution | **this file, partially** — Phase 8 in full, Phase 9 in outline, the rest as titles |
| 7. Open the folder and the branch | **done** — this folder, and `docs/phase-8-method-and-guardrails` |

*Renumbered 2026-08-21 when the playbook lost a step. This table read eight rows, with a separate
step 2 — "Run the cheapest experiment that could refute it — deferred; it is Phase 9's gate" — until
that step was folded into step 1. Nothing about what Milestone 2 did or skipped changed; only the
numbering did.*

**The capture step, now step 2, was the one worth re-reading before Phase 9**, and re-reading it
paid. The playbook calls it the highest-leverage step and the easiest to skip, and Milestone 1's
capture *changed* the architecture rather than informing it.

*Settled 2026-08-17. It is **not** discharged, and the hedge above was right to exist. `docs/captures/`
holds one 119 KB request; the frozen CSV holds body lengths and no bodies; the probe bodies are
synthetic and under a kilobyte. **The consequence is that the gate is not the twenty-minute measurement
this plan and `EPD-003` both call it** — it is a live capture session plus twenty minutes of `zstd`.*

---

## Record

| | |
|---|---|
| Branch | `docs/phase-8-method-and-guardrails` |
| Fork point | `6253cbc` |
| Merge commit | `22a6d20` — merged 2026-08-17 with `--no-ff` |

*A `Merge commit` row that still says "not yet merged" after the branch is gone is this
repository's signature failure — four of Milestone 1's six phase notes did exactly that. **Closed out at
the merge, 2026-08-17.** The permanent record is the phase note, per
`../method/IDM-001-git-branching.md`; this row and the plan's repeat it because a merge hash is immutable
and therefore cannot drift, which is what the one-home rule is protecting against.*

*This table records the branch **this file** was created on. Milestone 2's opening shared Phase 8's
branch, which is why the two Record tables carry the same three values.*
