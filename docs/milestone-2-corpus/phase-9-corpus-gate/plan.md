# Phase 9 — decide EPD-003, and run its gate: plan

**Written 2026-08-17 on `docs/phase-9-corpus-gate`, forked from `main` at `97f6563`. All sixteen tasks
executed; merged with `--no-ff` as `b29d502` the same day. No task letters were inserted.**

*This line said "Only tasks 1–4 have been executed" until the phase closed. **Closing it out is the
only kind of edit this file takes** — the same rule `../../method/IDM-001-git-branching.md` states for
a `Merge commit` row: the placeholder is correct while it is true and is the defect once it is not.
The plan's content below is **not** revised. It records what was believed before the work ran,
including where it turned out to be wrong; **what actually happened is in `notes.md`**, task by task.*

**Sixteen tasks in four groups.** Group A opens the phase and records the decisions taken in the
interview that produced this file. Group B captures real bodies, which the gate needs and the
repository does not have. Group C is the gate itself. Group D decides `../../epd/EPD-003-capturing-bodies-for-a-corpus.md`,
harvests, and names the milestone's central claim.

**The task list was renumbered once, before publication.** It changed across the opening interview as
five separate findings landed. Publishing it and then amending it would have spent letters (`4a`,
`4b`) on work nobody had started. From this commit forward `../../README.md`'s rule applies: **task
numbers are never renumbered; an insertion is a letter.**

---

## Why this is a `docs/` branch

`../../method/IDM-001-git-branching.md` — the prefix answers *which kind of work*, and `phase-N-` is
orthogonal to it. **No `src/` change survives this phase.** The capture in Task 6 patches `proxy.py`
and restores it; nothing is committed to `src/`, and `git diff main -- src/` must be empty at the
merge. The deliverables are documents: a dated decision, a measurement, a central claim.

`IDM-001` also answers the objection directly: a `docs/` branch is no longer *"documentation work
belonging to no phase"*, and Phase 8 is the form to copy.

**If execution forces a committed `src/` change, that is a re-derivation finding and the phase stops
and asks** rather than quietly re-prefixing.

---

## The question this phase closes

**Does the corpus proposal survive its own cheapest test?**

`EPD-003`'s sketch stores each body as its own content-addressed file. Per-file compression cannot
see across bodies, so it gets the ~3.1× a single body allows rather than the 28.6× measured across
twenty — **the sketch throws away the entire cross-body ratio by construction.** A trained `zstd`
dictionary is the only mechanism that could give it back while keeping files independent, and
`EPD-003` grades that as its one **unmeasured hypothesis**, *"the load-bearing one for the sketch"*.

If a dictionary recovers the ratio, the sketch ships. If it does not, per-call files are the wrong
unit, and Phase 10 designs per-session streams instead.

---

## What is settled, and by whom

Decided by the owner on 2026-08-17, in the interview that opened this branch.

| | Decision |
|---|---|
| **Fine-tuning** | **Dropped. Analysis only.** `EPD-003` open question 1, which everything else was downstream of. The Anthropic/LM Studio partition becomes optional rather than structural. Recorded in `EPD-003` at Task 3, which is why that document is now **partly accepted** |
| Who captures | **The session, headless.** `claude -p` against the router, no GUI, no interactive tab |
| Which backend | **Anthropic.** The redundancy the gate measures is Claude Code's preamble, which is identical whichever backend answers |
| Rigour | **Held-out split.** Train on ~70% of bodies, report the held-out ~30% as the honest figure and the self-trained figure beside it as the upper bound |
| Capture mechanism | **Patch `proxy.py`, restore, diff reproduced verbatim in `notes.md`.** Never committed |
| The conditional design | **This file**, fenced and marked as conditional — see "Design produced by the interview" below |
| `EPD-003`'s status | **Changed now, not at the close.** The fine-tuning decision does not depend on the gate, and a decision taken today belongs in the repository today |

---

## What the re-derivation found, before Task 1

`../../README.md`: *a phase's first act is to re-derive its own plan against what is now known.* Five
of Milestone 1's and 2's phases found their plan wrong on contact. This one was re-derived **before**
publication rather than after, so the findings below shaped the task list instead of correcting it.

### Verified, and passed

| Claim | Verified |
|---|---|
| `make test` reports **158** | ✅ 158 passed |
| `procedures/link-check.py` reports **68 broken, 2 roundabout** | ✅ run, not predicted — see below |
| `zstd` is present, 1.5.x from Homebrew as `EPD-003`'s Evidence assumes | ✅ 1.5.7 |
| `logs/` is gitignored, so a corpus under it needs no new rule | ✅ `.gitignore:228`, confirmed with `git check-ignore` |
| Working tree clean at the fork | ✅ `97f6563` |

**The link-checker count was run rather than predicted**, per `../../status.md`'s standing warning
and Phase 8's two failed attempts to predict it from its own docstring.

### Finding 1 — the capture is **not** discharged

`../implementation-plan.md:103` hedges that step 3 of the opening playbook *"may already be
discharged"* because `../../captures/` holds Milestone 1's request bytes. **It is not discharged**,
and the hedge was right to exist.

`../../captures/log-the-whole-request.txt` is **one** body. A single body cannot exercise a
cross-body dictionary — the entire question is what happens *between* bodies. The other frozen
artefacts were swept for a substitute and none serves:

| Artefact | Why it does not serve |
|---|---|
| `../../milestone-1-core/phase-2-observability/evidence/step-6-session/calls.csv` | Body *lengths*, no bodies. That is the point of the file |
| `../../procedures/lmstudio-capability-probes/bodies/*.json` | Synthetic and 189–856 bytes; the one large sample is generated filler and gitignored |
| `../../procedures/lmstudio-capability-probes/runs/*.txt` | Probe transcripts, not a session |

**Consequence: the gate is not twenty minutes of `zstd`.** It is a live capture session plus twenty
minutes of `zstd`, and Group B exists because of this finding.

### Finding 2 — `EPD-003`'s gate, run as written, trains on its test set

*"per-file zstd with a dictionary trained by `zstd --train` **on the session**"* — then compressing
that same session. That figure is an upper bound, not a deployment figure: in use a dictionary is
trained once and applied to sessions that did not exist when it was trained.

Since the whole question is whether the dictionary lands near the stream figure or near the 3×, an
optimistic dictionary figure biases the gate toward *"the sketch survives"*. **This is a weakness in
the EPD's specified method**, and the held-out split above is the fix.

The split does more than add rigour. A self-trained dictionary **can** memorise session-local
content; a held-out one can only carry the static preamble. So **the gap between the two numbers is
the static-versus-session-local decomposition, measured directly** — and that decomposition is what
decides the design.

### Finding 3 — `--maxdict` defaults below the preamble

`zstd --help`: `--maxdict` defaults to **112,640 bytes**. `src/ilirium_llm_router/stats.py` records,
measured, that `request_bytes` *"is dominated by the fixed preamble of roughly 110 KB of system
prompt and tool schemas."*

**The default cap is sitting on the preamble.** A single-point run at the default could not
distinguish *"a dictionary cannot recover this redundancy"* from *"the dictionary was capped below
the thing it needed to hold"* — and those have opposite design consequences. Task 9 sweeps
`--maxdict` for this reason.

### Finding 4 — `calls.csv` expires, so it cannot be the corpus's join table

`EPD-003`'s sketch says *"Add two columns to `calls.csv` … The CSV becomes the join table it already
almost is."*

`config.yaml:58–61` sets `max_bytes: 5 MiB` with **`backup_count: 10`**, and `stats.py` rides
`RotatingFileHandler`, which discards the oldest segment at each rollover. So `calls.csv` is a
**capped rolling window of ~55 MiB**, not an archive. A corpus keyed to it would outlive its own
index: a year in, the bodies persist and nothing says which call, model, backend or session produced
them.

`EPD-003` came close — its constraints say *"refs must survive rotation"* — but read rotation as a
ref-integrity concern rather than as the index being **deleted**.

**Two things follow.** Rotation is *correct* for the CSV's own purpose, which
`../../reference/observability.md` states is model/backend comparison — a recent-window question. So
the defect is in borrowing the file, not in the file. And **this finding is independent of the gate**:
it is true whatever the compression numbers say, and it is recorded here for Phase 10 either way.

### Finding 5 — concurrency dilutes a dictionary, and the planned capture would have hidden it

Subagents and parallel sessions each add a **preamble family** a dictionary must cover within its
size budget. `../../reference/observability.md` records that a subagent's `agent_id` is *"generated
fresh each time"*, and agent *type* appears only in the body — which the router is forbidden to
parse. **So dictionaries cannot be partitioned by agent type**, and the dictionary is stuck covering
the union.

As first planned, Task 6 would have captured a single main conversation and produced a dictionary
figure that flatters real use. It now captures **two concurrent sessions in different directories,
one spawning a subagent**, and Task 9 reports the decomposition. This deliberately makes the gate
harder to pass, which is the point: a flattering positive is worse than a true negative.

---

## The tasks

**All four groups ran. The markers below are closed out; the task descriptions are not revised.**
`notes.md` carries what each one found, including the three tasks whose scope grew on contact — Task 3
took a five-document sweep the plan named as three, Task 4 took `../implementation-plan.md` as well as
`../../status.md`, and Task 6 took three capture runs rather than one.

### Group A — open the phase and record what was decided *(executed)*

| # | Task |
|---|---|
| **1** | Open the branch and the folder; commit this file |
| **2** | Record the re-derivation in `notes.md` |
| **3** | `EPD-003` → **partly accepted**: the fine-tuning decision, dated; strike stale open question 7; update `EPD-000`'s index row |
| **4** | `../../status.md` — record the in-flight branch |

### Group B — the capture *(executed; three runs, not one)*

| # | Task |
|---|---|
| **5** | Verify the ignore coverage for the capture directory and that `make clean` leaves `logs/` alone. **Verify, not add** — Finding above |
| **6** | Patch `proxy.py` (uncommitted), run the router, capture two concurrent headless sessions in different directories with one subagent, restore `src/`. Diff reproduced verbatim in `notes.md` |
| **7** | **Verify the instrument before believing it.** Cross-check every captured length against the same run's `calls.csv` rows; compare a captured body's shape against `../../captures/log-the-whole-request.txt`; require **≥50 request bodies** or capture again |

### Group C — the gate *(executed; it passed)*

| # | Task |
|---|---|
| **8** | Write the measurement script. It reads and writes under `logs/`, **never into `evidence/`** — `../../README.md`: an instrument's output follows the instrument, never the archive |
| **9** | Run it: raw; per-file `zstd`; per-file + **self-trained** dictionary; per-file + **held-out** dictionary; one long-window stream over the concatenation. **Sweep `--maxdict`.** Report requests and responses separately, and single-session against the mixed corpus |
| **10** | Read the verdict and write it: near the stream, the sketch survives; near 3×, per-call files are the wrong unit |

### Group D — decide and harvest *(executed)*

| # | Task |
|---|---|
| **11** | `EPD-003` → its final status, carrying the per-call-versus-per-session answer |
| **12** | Graduate the decided parts into `../../reference/design-decisions.md`, per `EPD-000` |
| **13** | The gate's numbers into `../../reference/measurements.md` — all four columns or they do not go in |
| **14** | **Write the milestone's central claim** into `../implementation-plan.md`, replacing "NOT YET NAMED"; raise Phase 10 to outline, including the `logs/telemetry/` move |
| **15** | `../../status.md` and `../../backlog.md` — remove `EPD-003` from "Decisions waiting on a person" |
| **16** | Close out: `notes.md` "Verified by"; run `link-check.py`; `make test` must report **158**; merge `--no-ff` with the message from a temp file; record the hash in `notes.md` **and** this file's Record table at the merge |

---

## Design produced by the interview — **conditional on the gate, and not a specification**

> **Nothing below is decided, and none of it is Phase 9's to decide.** Phase 10's question is *"what
> does the router store, and where"*, and `../implementation-plan.md` says it is *"only answerable
> once Phase 9 has said whether per-call files are the unit."* **If the gate fails, most of this
> section is void.**
>
> It is recorded here, fenced, on the owner's instruction of 2026-08-17, for the reason
> `../../method/IDM-001-git-branching.md` would otherwise argue against: this repository's sessions
> are cleared deliberately and no handoff notes are kept, so a design that exists only in a
> conversation does not survive it. **It is input to Phase 10, not output of Phase 9.**

**Shape, if per-call files survive the gate:**

```
logs/
  telemetry/                          calls.csv and router.log — moved in Phase 10, not here
  corpus/
    2026-08-17/                       UTC-derived, never local — see below
      index.csv                       22 columns: calls.csv's 20, in order, plus the two refs
      manifest                        router version, dictIDs referenced, schema version
      dicts/                          copies of whichever dictionaries this day used
        req-2026-08-17T091403Z.dict
        res-2026-08-17T091403Z.dict
      incoming/                       staging for atomic rename
      requests/3f/3f9c….zst
      responses/b2/b20e….zst
```

**The reasoning that produced each choice, so Phase 10 does not have to re-derive it:**

| Choice | Why |
|---|---|
| Hash the **plaintext**, not the compressed bytes | The same body under two dictionaries compresses to different bytes; hashing the compressed form would break deduplication the moment a dictionary changes |
| Frames are **self-describing** | `zstd` embeds a dictID in every frame, so no index is needed to know which dictionary a blob requires. This is what makes more than one dictionary safe |
| Blobs are **immutable**, never recompressed | A new dictionary applies to new bodies only; old frames name the old dictionary and stay valid |
| `write → fsync → rename` from `incoming/` | Atomic within a filesystem; content addressing makes the collision case free — if the target exists, the body is already stored |
| Date folders, **UTC-derived** | `../../reference/observability.md` records both files timestamp in UTC. A local-time folder name would contradict the `timestamp` column of the rows inside it, twice a day |
| Dictionaries **inside** the date folder | Portability: `tar` one folder and it decompresses elsewhere with nothing else needed. Storage placement is independent of training cadence — train infrequently on a cross-day window, *copy* into each day that uses it |
| **Full** telemetry per day, not a subset | Follows from self-containment: `calls.csv` expires (Finding 4), so the archive is the only durable home. Same column order means a rotated segment and a day-file are interchangeable inputs to one spreadsheet |
| Header row in **every** day file | Inherited, not invented — `stats.py` re-emits the header on rotation because *"a segment that cannot be read alone is the one that gets thrown away"* |
| Truncation needs **no new column** | `error_status` already says a call broke; a consumer joining on the ref learns it there. A `.partial` suffix would break content addressing |
| Separate dictionaries per **direction** | Requests are conversation JSON, responses are SSE frames. Task 9 measures whether the split pays |
| **No** session/agent subfolder layer | A session crosses midnight, so one-session-one-folder is already false under date partitioning; there is no session-end signal (`EPD-003`'s reason 2), so such folders never close; and the index answers "session A's bodies" with a filter, which is cheaper than a tree |
| **No** per-session dictionaries | The material a dictionary can hold is cross-session static; session-local material is what it cannot hold. Buffering a session's early bodies to train on them **is a per-session stream with extra steps** — which is evidence for the stream side of `EPD-003` open question 2, not for more folders |
| Dictionaries are **never deleted** | Losing one makes every blob referencing it unreadable, and they cost ~110 KB. Blobs may be pruned freely; dictionaries are append-only forever |
| Force the **dictID** | `--dictID` defaults to *Random*. The timestamped filename names the file for humans; the forced sequential dictID is what binds the blobs |
| `calls.csv` is **not changed** | Not its rotation, not its columns. Finding 4 — the defect is in borrowing the file, not in the file |

**Two costs named rather than hidden.** Copying a dictionary into each date folder costs ~80 MB a
year at the 110 KB default — roughly a quarter of `EPD-003`'s projected corpus — and more if the
sweep says the dictionary wants to be larger. **The choice between plain copies and APFS clones is
downstream of Task 9's `--maxdict` result** and is deliberately not made here. And making the
opt-in corpus the only durable home for telemetry is an asymmetry; it is still strictly an
improvement, because that telemetry is discarded today.

---

## Documented versus measured

| Claim | Status |
|---|---|
| `../../captures/` holds one body, and no frozen artefact substitutes for a session | **Measured** — swept, this branch |
| `make test` 158; link-check 68 broken / 2 roundabout; `zstd` 1.5.7 | **Measured** — run 2026-08-17 |
| `--maxdict` defaults to 112,640 bytes | **Measured** — `zstd --help` |
| The static preamble is ~110 KB | **Measured** — `stats.py`, from Milestone 1 |
| `calls.csv` discards rows at rollover | **Inferred strongly** — `backup_count: 10` plus `RotatingFileHandler`'s documented semantics; not observed rolling over here |
| A dictionary recovers the cross-body ratio | **Unmeasured hypothesis** — this is the gate |
| A dictionary captures static material but not session-local material | **Inferred** — from what `--train` is; Task 9's two figures measure it |
| Concurrency dilutes a dictionary | **Inferred** — Task 9 measures it |
| Headless `claude -p` produces the same preamble as an interactive session | **Assumed** — Task 7 checks it |
| Copying dictionaries costs ~80 MB/year | **Extrapolated** — from the 110 KB default against `EPD-003`'s own projection, itself extrapolated from one session |

---

## Done when

The gate has a number and a verdict; `EPD-003` carries a dated decision; the milestone's central
claim is written; `make test` reports **158**; `link-check.py`'s count is re-derived **by running
it**; `git diff main -- src/` is empty; and **no captured body or dictionary is committed.**

## What could go wrong

- **The gate lands mid-range and decides nothing.** Then the held-out figure is what we lean on, and
  the phase records that the gate was less decisive than `EPD-003` assumed rather than rounding it
  to a verdict.
- **A headless preamble differs from an interactive one.** Task 7 measures it rather than assuming;
  a difference is a caveat on the number, not a reason to stop.
- **A short session starves `zstd --train`.** Task 7's ≥50 threshold catches it before any number is
  computed.
- **The capture contains something sensitive.** The session is driven with tasks that do not read
  `.env`, and Task 5 confirms the ignore before Task 6 writes a byte. **A trained dictionary contains
  verbatim substrings of its samples and is exactly as uncommittable as the bodies.**

---

## Record

| | |
|---|---|
| Branch | `docs/phase-9-corpus-gate` |
| Fork point | `97f6563` |
| Merge commit | **`b29d502`** — merged 2026-08-17 with `--no-ff` |

*Writing "not yet merged" while it is true is correct; leaving it there after the branch is gone is
this repository's signature failure, and `../../method/IDM-001-git-branching.md` names it. Closed out
at Task 16.*
