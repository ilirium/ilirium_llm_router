# Phase 11 — corpus tools: plan

**Ratified, reviewed, and revised from the review — 2026-08-26.** The forward review under
`../../method/IDM-004-reviewing-unexecuted-work.md` ran against the `2d04840` revision of this file;
its charter is `review-charter.md`, both runs and the reconciliation are in `notes.md`, and
**seventeen findings are folded in below.** Twenty positions are settled, every one owned and dated.

**The heaviest thing the review returned was not a defect in the plan's reasoning — it was the cost of
one measurement nobody had taken.** The document's model of a captured session (*cumulative calls, one
user turn and one assistant turn each*) is simpler than the traffic on disk, which is five interleaved
request classes, three roles, two content serialisations, a migrating `cache_control` annotation, 94
error responses and a 45-call tail with no request body at all. **Every one of those was an hour's
reading away, and this plan asserted the opposite of several of them in bold.**

**Work may begin at Task 2.**

**Subject.** The offline tools that sit on top of the store Phase 10 built: **extract** bodies out of
a corpus with selection, **verify** an archive as its own command, and **convert** captured calls into
Claude Code session `JSONL` so a session can be read in
[`claude-code-history-viewer`](https://github.com/jhlee0409/claude-code-history-viewer). The CLI is
restructured into subcommands to hold them.

**Dictionaries are documented, not extended.** *Corrected 2026-08-26 — this paragraph promised
"**train** dictionaries as a first-class command rather than a flag" until position 3 was ratified the
other way.* The phase writes a temporary `README.md` note covering the commands that already ship;
`list`/`show`/`install`, response dictionaries and a dicted-vs-undicted benchmark are all in
`../../backlog.md`.

**`--extract` already exists and is deliberately minimal.** `cli.py:135` says so in its own docstring
and names this phase: *"the extraction tool — selection by session, call or model, output layout,
bulk verification — is Phase 11's."* `reference/corpus.md:110` says the same. This phase is the
promise those two lines make.

## Why this is a `feat/` branch

It changes `src/`, so `../../method/IDM-001-git-branching.md` makes the prefix `feat/`. Branch
`feat/phase-11-corpus-tools`, forked from `main` at `f445d6f`, and this folder takes its slug.

## What is settled, and by whom

*The table `../../backlog.md` asks a forward review to check every load-bearing position against —
see its method item on classifying by authority. A position not in this table is **this plan's own
assumption** and the review reports it as unratified.*

| | Position | Whose |
|---|---|---|
| 1 | Phase 11 belongs to **Milestone 2**, and the milestone stays open past Phase 12 | **owner**, 2026-08-24 |
| 2 | The CLI becomes **subcommands on one entry point**, not more flags and not a second console script | **owner**, 2026-08-24 |
| 3 | **No new dictionary features.** The gap is that the existing ones are undocumented — the phase writes a user-facing note in the top-level `README.md`, explicitly temporary until Phase 12 reworks it | **owner**, 2026-08-24, **ratified 2026-08-26** |
| 4 | The real input is the owner's own driven session at `to-run-server/logs/corpus/` | **owner**, 2026-08-24 |
| 5 | Work moves to **git worktrees** as the standing practice | **owner**, 2026-08-24 |
| 6 | Phase 12 is the installer (`uv tool`) and the `README.md` rewrite | **owner**, 2026-08-24 |
| 7 | **`extract` takes one or more day folders as positional arguments**, and **errors** if a selected session has calls in a folder that was not passed | **owner**, 2026-08-26 |
| 8 | **`--out` is required. `--format` is required and repeatable** — `bodies`, `jsonl`, or both. A run always states what it produces | **owner**, 2026-08-26 |
| 9 | **Verification is its own command, `verify-archive`**, not a flag on `extract` | **owner**, 2026-08-26 |
| 10 | **No header capture, and the reason is recorded in `CLAUDE.md`** rather than left to be rediscovered | **owner**, 2026-08-26 |
| 11 | **`--agent` is built after all** — this phase's own review run is what generates the first subagent traffic | **owner**, 2026-08-26 |
| 12 | One `--out` root with `projects/` beside `bodies/`, and **never into `~/.claude/projects/`** | **owner**, 2026-08-26 |
| 13 | Dictionary work — response dictionaries, `list`/`show`/`install`, and a dicted-vs-undicted benchmark — is **postponed into `../../backlog.md`**, under a new `Dictionaries` section | **owner**, 2026-08-26 |
| 14 | The evidence slice is a **live snapshot labelled with its moment**, not a stopped router | **owner**, 2026-08-26 |
| 15 | **The converter emits every call it can reconstruct a turn from, and filters nothing.** No probe-class detection, no auxiliary-call heuristics | **owner**, 2026-08-26 |
| 16 | A session whose request bodies stop being captured is **emitted up to the gap, then stopped, with the gap stated in-band** | **owner**, 2026-08-26 |
| 17 | The viewer's record shape is learned from **its source and one real session file**, shallowly — schema only, and **not** by diffing | **owner**, 2026-08-26 |
| 18 | Selection matching is **exact** on `--path`, `--session` and `--model` | **owner**, 2026-08-26 |
| 19 | **Task 14 is struck.** The owner exercises the tools by hand **after the phase is finished**; the phase's own evidence is code, tests and mutation testing | **owner**, 2026-08-26 |
| 20 | **This is a baseline tool.** Error responses, `count_tokens`, subagent partitioning and the second-source check are all **deferred to a later phase** — *"step by step, not leaps by leaps"* | **owner**, 2026-08-26 |

**Position 3 was ratified on 2026-08-26, and it was decided against a premise that had changed since
it was asked.** When the question was put, the machinery had never produced a dictionary and 2.815×
was *"the number a dictionary must beat"*. By the time it was answered a dictionary had installed
itself unattended at **3.317×** — so the decision was taken knowing the mechanism works, which is the
strongest argument available for **not** building more of it. The three postponed ideas are in
`../../backlog.md`; **whether a response dictionary pays was already there**, added 2026-08-19, and was
pointed at rather than restated.

*Positions 7–14 were settled in one ratification pass on 2026-08-26, which is also when the register's
nine original `❓` were valued — **three more were opened by the review later the same day, and are
listed in "Placeholders in this file".** **Two of these positions came from the owner rather than from
this plan** —
`verify-archive` as a separate command, and `--format` as a selector instead of the `--to-jsonl`
boolean this plan proposed. The second fixed a defect the plan had reproduced: a mode flag whose
companion option is meaningless without it, which is the exact problem position 2 adopted subcommands
to solve.*

## The re-derivation before Task 1, and it moved six things

`../../../CLAUDE.md`: *check prior evidence before planning a rerun*. Done in **two passes** — 2026-08-24
against the owner's live corpus and Phase 9's frozen one, then again on **2026-08-26** during
ratification. **Six findings. The first invalidates a measurement taken during this very session, and
the fifth invalidates the converter's core assumption.**

**The second pass exists because the first one's findings decayed in under two days.** Finding 2 was
false by 2026-08-25 and finding 3's sample had quadrupled by 2026-08-26. That is not a criticism of
the first pass — it is what re-deriving against a **live** corpus means, and it is the reason every
figure here carries its moment.

**1 · The corpus is live and was growing while it was being read.** Request blobs in the
`2026-08-24` day folder went **114 → 123** between two reads minutes apart; `index.csv` went 165
lines → 171 rows over the same span. **The router in `to-run-server` is still up and capturing.**

Every figure below is therefore a **snapshot with a moment attached**, and the phase must freeze a
slice before it measures anything. *This is the instrument lying with a plausible number again — the
Phase 10 pattern — except here the number was not wrong, it was unrepeatable, which is harder to see.*

**2 · The corpus was undicted on 2026-08-24, the round trip worked anyway, and it has been dicted
since 2026-08-25T10:32:50Z.**

*Heading corrected 2026-08-26. It read **"The captured corpus is undicted"** in the present tense and
stayed on the page for a full day after it stopped being true — while the register below already
carried the contradicting figure. **Two adjacent statements in one document, one true and one false,
and the false one was the heading.** That is the same failure this plan records against `status.md`'s
prose, happening here.*

Driven, not assumed — `ilirium-llm-router --extract` on the `2026-08-24` folder, at the moment it held
280 blobs:

```
index_schema_version: 1
index_columns: 26
dictionaries: none
280 blob(s), 0 failed
30036825 → 10669134 bytes, 2.815x
every blob verified against the digest in its own filename
```

**As of 2026-08-24** `request_dict_id` was `none` on all 171 rows, both day folders then in existence
had an **empty `dicts/`**, and there was no `logs/corpus/dicts/` in that worktree at all.
`retrain.log` said why, and it was working as designed rather than failing:

```
2026-08-21T14:29:14Z verdict=skipped reason=no-complete-day
2026-08-24T13:35:10Z verdict=skipped reason=too-few-samples window=2026-08-21 samples=0 holdout=4
```

**Then it dicted itself, unattended, and nothing noticed for a day.** A third verdict —
`verdict=installed`, **2026-08-25T10:32:50Z** — produced `req-2026-08-25T103250Z-9dd33823.dict`,
262,144 bytes, scoring **3.317×** against incumbent `none` on its own holdout. **The number this
finding called *"the number a dictionary must beat"* had been beaten while the branch was busy with
permissions.**

**2.815× was the honest no-dictionary baseline on real traffic** and it is *not* a headline ratio —
`reference/corpus.md:193` refuses those and this phase does not start one. **It must not be compared
against 3.317×**; the register below says why, at length, and that warning is the load-bearing part of
this finding now. What survives is the round trip: 280 blobs, 0 failed, every one verified against the
digest in its own filename.

**3 · What the index actually holds, measured 2026-08-24 on 171 rows.** This is what the extractor
can select on, so an assumption here is expensive:

| Column | What is really in it |
|---|---|
| `path` | `/v1/messages` 168, `/api/hello` 3. ~~**No `count_tokens` at all**~~ — **false by 2026-08-26: 65 `count_tokens` rows**, 0/21/43/1 across the four days, inside the same sessions |
| `backend` | `anthropic` 171 — ~~**no LM Studio traffic captured**~~ **false: `2026-08-21` holds one `backend=lmstudio` row**, `google/gemma-4-e4b`, both bodies stored and readable now |
| `model` | `claude-opus-5` 158, `claude-sonnet-5` 10, empty 3 |
| `stream` | **`true` 105, `false` 63.** Both response encodings are present |
| `session_id` | **4 distinct**, 3 rows empty (the `/api/hello` calls) |
| `agent_id` | **empty on all 171 rows** — and re-measured 2026-08-26 across **all four day folders, 770 rows: still empty on every one** |

**Two of those change the design.** `stream: false` on 63 of 168 means the converter meets **plain
JSON replies as well as SSE**, so "reassemble the SSE stream" is half the job and a plan that says
only that is wrong.

**And `agent_id` is not what this plan first said it was.** The original wording — *"the column
exists, the capture never populated it"* — reads as a defect, and it is wrong. `observe.py:317` reads
the `x-claude-code-agent-id` header, and `observe.py:40` states that an `agent_id` *"arrives only on a
subagent's call, so an empty one means the main conversation rather than a missing value."* **The
column works. No subagent has ever run through this router.** The distinction is not pedantic: *broken*
invites a fix, *never exercised* invites generating the traffic.

**Which is what settled it.** `--agent` was struck on 2026-08-24 and is **reinstated as of
2026-08-26**, because this phase's own IDM-004 review spawns a cold-reader subagent whose calls pass
through the router while it is capturing. **The review generates the first agent traffic this corpus
has ever held**, so the filter can be built and tested against real rows rather than shipped empty.

**One claim in this repository has never been observed, and the review run tests it.** `observe.py:40`
asserts that `agent_id` arrives on a subagent's call. That is a **comment, not a measurement** — 770
rows have never contained one. Stating the positive result before the run, per the instrument lesson
this phase inherited:

> **After the cold run, `2026-08-26/index.csv` column 3 must hold at least one non-empty value.**
> If it is still empty on every row, `observe.py:40` is **wrong**, `--agent` cannot be built, and the
> phase has found a defect instead of a feature. Either outcome is worth having; the run was happening
> regardless.

**4 · Phase 9's gate corpus is on disk, and this plan described it wrongly in three ways.**
`logs/corpus-gate/` — 8.8 MB, three runs, `requests/NNNNN.bin` as **plaintext JSON**. It is not
day-folder shaped, so it is no use to the extractor.

***Corrected 2026-08-26 by the forward review. The description below is what is actually there; the
task that would have used it is struck (task 15), and the correction stays anyway so no later session
inherits the wrong picture.***

- **There is no `manifest.csv` at the root.** There is **one per run** — `run-01-anthropic/`,
  `run-02-lmstudio/`, `run-03-anthropic/`. The root holds only `dicts/`.
- **The manifests have no header row**, and six unnamed columns (seven in `run-02`). This plan said
  they "carry `session_id` and `path`"; a reader must infer which position each is.
- **"Responses as raw SSE" is wrong for 22 of run-01's 49**, which are
  `{"type":"error","error":{"type":"overloaded_error"…}}`. Two more are zero-length, and one SSE
  response opens with `event: error` and no `message_start` at all.
- **`run-02-lmstudio` is real LM Studio traffic** — `lfm2.5-8b-a1b-mlx`, responses in SSE. See the
  correction to finding 3's `backend` row.

**5 · A session spans day folders, and the naive converter would produce a *wrong* transcript rather
than a short one.** Measured 2026-08-26 over all four day indexes:

```
2026-08-25:  20260825-0000-4000-8000-000000000001   39 calls
2026-08-26:  20260825-0000-4000-8000-000000000001   19 calls
```

**That session id is the session that ratified this plan.** The conversation being used to design the
converter is itself the counter-example, and it was found by looking rather than by reasoning.

**Why this is the sharpest finding in the list.** Requests are cumulative — request *N* carries turns
1..*N*. A converter given only `2026-08-26` has **no previous call to diff against**, so it emits that
day's first request's entire prior history **as a single opening turn**. The output is not incomplete;
it is **misleading**, which is the exact condition this plan names as refuting the phase:
*"a fidelity loss that makes the viewer's output misleading rather than merely incomplete."*

**Two consequences, both settled as positions 7 and 12.** Day folders are **positional and
repeatable**, so `extract 2026-08-25 2026-08-26 --session 20260825-1…` is expressible and
`extract logs/corpus/2026-*/` extracts everything without needing an `--all` flag or a corpus-root
concept. And the converter **errors** when a selected session has calls in a folder that was not
passed, rather than silently reconstructing a partial one. **That error is the whole defence** — it is
what keeps a cross-day session from failing quietly.

**6 · The real session records exist on this machine, which turns Task 14 from eyeballing into
diffing.** Claude Code keeps its own records at `~/.claude/projects/<mangled-path>/<session-id>.jsonl`,
and **all three session ids in the `2026-08-25` index have a file there** — `20260825-1…`, `8aa605b9…`,
`ad9392ae…`. *(Established 2026-08-26 by listing filenames only; no session content was read.)*

**Oracle, never input, and the distinction is load-bearing.** A reconstruction can be **diffed against
the real record**, which is a far stronger check than opening it in a viewer and forming an
impression. But a converter that *reads* uuids out of `~/.claude/` no longer reconstructs from the
corpus alone and **silently breaks for a corpus copied from another machine** — destroying the very
property this phase exists to demonstrate. Synthetic deterministic uuids stay the default; the local
records are a test fixture. The research item is in `../../backlog.md`.

## The question this phase closes

> **Can a captured corpus be read back out by somebody who did not write it — selectively, into a
> shape another tool already understands — without the store learning anything about the payload?**

Phase 10 settled that a day folder is self-contained and that every blob verifies. That is the
*storage* half. This is the *retrieval* half, and its sharp end is the converter: **the store went to
some trouble never to parse a body, and the converter parses every one of them.** That is not a
contradiction — it is the line this phase has to keep on the right side of. **Parsing lives in the
tools; the store stays opaque.** If that line moves, the phase has failed even with green tests.

**What would refute it:** a body the converter cannot reconstruct a turn from, or a fidelity loss
that makes the viewer's output misleading rather than merely incomplete.

***Group C was built to find that early. The forward review found it first, and without any code
being written*** — the 45-call tail with no request bodies, the two normalisations, the third role,
and a session spanning midnight. **Four candidate refutations surfaced by reading the disk rather than
by building against it**, which is what `../../method/IDM-004-reviewing-unexecuted-work.md` costs one
review run to buy.

**And the question is not closed inside this phase.** Position 19 moves the hands-on check after the
merge, so what the phase itself establishes is that the tools are **correct by test and by mutation**.
Whether a corpus reads back out *legibly, to a person* is confirmed afterwards, by the owner. **That
is a real gap and it is named in "What this phase does not settle" rather than papered over here.**

## The shape

### The CLI becomes subcommands

Position 2. Today's surface is nine flags on one parser, most of which apply to exactly one mode —
`--maxdict` is meaningless with `--extract`, and argparse cannot say so. Subcommands make that
structural instead of documented.

**Bare `ilirium-llm-router` keeps starting the server.** `make run` depends on it, so does habit, and
Phase 12 will make this a `uv tool` where the bare form is the one people type. **This is my
proposal, not the owner's position** — it is the one place where subcommands could reasonably have
been total.

**The old flags are removed rather than aliased.** They have one user, on this machine, and Phase 12
is where the spelling becomes a promise to strangers. **Renaming after the installer ships is the
expensive version of this change; renaming now is free.**

**This plan reproduced, inside a subcommand, the exact defect subcommands were adopted to fix.** It
proposed `extract --to-jsonl` — a **mode flag** — alongside `--project-name`, which is meaningless
without it. That is position 2's own complaint (*"most of which apply to exactly one mode, and argparse
cannot say so"*) at one level down. **The owner caught it on 2026-08-26** and replaced the boolean with
a **required, repeatable `--format`** taking `bodies` and `jsonl`. `--project-name` is now scoped to a
format rather than to a mode, and argparse errors explicitly when it is passed without
`--format jsonl`. *Recorded rather than quietly corrected: the fix came from the owner, and the plan
had reviewed its own CLI section twice without seeing it.*

**Verification became its own command on the same pass.** `verify-archive <DAY>...` reads and checks
and writes nothing — which is what today's `--extract` already does. The plan had carried a
`--verify-only` flag on `extract`; that flag **named the default**, since an `extract` with no output
destination cannot do anything else, and two spellings for one behaviour is what the register exists
to catch. The row is struck below.

### The extractor

Selection over the index, output as files a person can open. It reads **the day folders it is given
and nothing above them**, which is `reference/corpus.md`'s self-containment guarantee kept executable.
Days are positional and repeatable (position 7), so the shell's own glob covers *"all of it"* and no
`--all` flag or corpus-root concept is needed:

```
ilirium-llm-router extract 2026-08-25 --out ./dump --format bodies
ilirium-llm-router extract logs/corpus/2026-*/ --out ./dump --format bodies --format jsonl
ilirium-llm-router verify-archive logs/corpus/2026-*/
```

**One `--out` root holds both formats**, and the layout is the reason it can:

```
<out>/bodies/<session-id>/00001-request.json
                          00001-response.sse     ← .sse streamed, .json not
<out>/projects/corpus/<session-id>.jsonl
```

**`projects/` sits at the root deliberately** — the viewer's Custom Claude Directory can be pointed
straight at `<out>` and works, while `bodies/` sits beside it and is ignored. **Never
`~/.claude/projects/`** (position 12): writing lossy reconstructions into the real history directory
would corrupt the owner's own record, and that is not a reversible mistake.

**`--agent` is implemented, reversing this plan's 2026-08-24 decision.** It was struck because the
column is empty on every row the corpus has ever held — still true at 770 rows on 2026-08-26 — and a
filter that silently returns empty is worse than no filter. **What changed is that the traffic is
about to exist:** this phase's IDM-004 review spawns a cold-reader subagent through a capturing
router, so `--agent` gets built against real rows. **If the review's run leaves column 3 empty, the
strike stands and finding 3's prediction has caught a defect in `observe.py` instead.**

### The converter, and the part that is actually hard

**Requests are cumulative.** Request *N* of a session carries turns 1..*N*, so the naive read — one
call, one exchange — reconstructs the same opening turn dozens of times.

**The proposal is delta reconstruction:** walk a session's calls in timestamp order; for each, diff
its `messages` array against the previous call's and emit only the **new** user-side entries, then
emit the assistant turn from that call's response. Tool results ride in as `tool_result` blocks in
the next request's user turn, so they arrive for free.

**And a session's calls are not all in one day folder — finding 5.** Delta reconstruction walks a
session in timestamp order **across every folder it was given**, so the diff for the first call after
midnight is taken against the last call of the previous day rather than against nothing. **When a
selected session has calls in a folder that was not passed, the converter errors and names the missing
day.** It does not reconstruct what it can and stay quiet: the failure mode this guards against
produces a transcript whose opening turn silently contains a whole day of prior conversation, which
reads as real.

**Three fidelity limits, and they are limits rather than bugs.** The store keeps **bodies only, never
headers**, and Claude Code's own session records carry client-side facts that never crossed the wire:

| Field the viewer reads | Why the corpus cannot supply it |
|---|---|
| `cwd`, `gitBranch`, `version` | Client state. Never in an API body |
| `toolUseResult` | Claude Code's own enriched record. The wire carries `tool_result` content, not this |
| `agentId` / sidechain attribution | Header-derived. The column exists and works; empty on all **770** captured rows because no subagent has ever run through the router |

**A fourth limit was proposed on 2026-08-26 and rejected, and the reasoning belongs here because the
proposal is the obvious one.** The question was whether headers could be captured selectively —
keeping the useful ones, dropping anything sensitive. **It does not work, for a reason that has
nothing to do with sensitivity: none of the missing fields is a header.** `cwd`, `gitBranch`,
`version` and `toolUseResult` are client-side state that never crosses the wire in any form; at most
`User-Agent` yields a version string. The two header-derived facts that matter — `session_id` and
`agent_id` — are **already columns**, read at `observe.py:316`. Capturing headers would buy a version
string in exchange for a write-path change. *The credential argument is real and secondary: the store
is attached to a tee of body bytes and never sees a header, so no token can reach disk. Both halves
are now in `../../../CLAUDE.md`, because a session carrying only the security half proposes the wrong
fix.*

**The output says so in-band, as a `system` record at the head of each file** — settled 2026-08-26,
against a sidecar. A sidecar is not in-band: the viewer is the only place these files get read, and it
would not show one. `JSONL_SCHEMA_NOTE` in the register carries the wording. **One risk, checked at
Task 14:** if the viewer refuses to render an unrecognised `system` record, the fallback is a `user`
record carrying the same text — uglier, still visible, still in-band.

**Output goes to its own root, never into `~/.claude/projects/`.** The viewer supports custom Claude
directories (Settings → Custom Claude Directories), so reconstructed sessions stay separable from
real ones. **Writing reconstructions into the real history directory would corrupt the user's own
record with lossy copies**, and that is not a reversible mistake.

## Non-goals

- **Not a retention or deletion tool.** Milestone 2's scope boundary; `../../backlog.md` records that
  it is deliberately absent rather than forgotten.
- **Not a live metrics or status endpoint.** Reserved out of Phase 10 and still reserved.
- **No change to `calls.csv`, its rotation or its columns** — the milestone's standing non-goal.
- **No change to the write path.** This phase adds no capture-time behaviour at all.
- **Not a viewer.** The output is `JSONL` for somebody else's tool.
- **Does not measure whether archiving slows a call.** Failure mode 3 stays open and stays in
  `../../backlog.md`.

## The tasks

**Six groups. `notes-group-<letter>.md` per group**, per `../../README.md`'s split rule. **Done
2026-08-26**, on the owner's instruction, once three groups' worth of sections had accumulated in one
file: `notes-group-a.md`, `notes-group-b.md` and `notes-group-c.md` exist and `notes.md` went 963 →
403 lines. **`notes.md` stays the entry point** and keeps what belongs to no group.

### Group A — open the phase

1. Branch, worktree and this folder. **Done** — branch `feat/phase-11-corpus-tools`, worktree at
   `../../../../phase-11-corpus-tools`.
2. **Done 2026-08-26.** **Fix `CLAUDE.md`'s inode note, first commit.** It says the code-2026 and OneDrive paths are the
   same directory and *"editing either edits both"*. With this clone there are now genuinely two
   checkouts and **the note tells a session the opposite of the truth**. Also correct
   `reference/corpus.md`'s mtime justification, which cites a cloud-synced `logs/` that this
   worktree's is not.
3. **Done 2026-08-26.** **Record the worktree practice** — an `IDM-001` amendment covering the layout, and the
   `temp/to-run-server` branch, whose prefix `IDM-001` does not define and which never merges.
   **The mechanism is settled and this task no longer has to hedge it.** Settings are
   **session-cached**: a tracked permission change is inert until the session **restarts**, not until
   the branch merges. The competing explanation this task was written around — that tracked settings
   resolve *"through worktrees to the main checkout"* — is **dead**, measured 2026-08-25, and Task 3b
   does not need to carry it.

   *Also worth recording here, found on 2026-08-25:* `temp/to-run-server` carries **no commits of its
   own**, so its tip sits on the trunk and `../../procedures/branch-index.py` tables it as **merged**
   rather than reporting it in flight — which is why a utility worktree needs a description in a table
   of work.
4. **Done 2026-08-26.** **Amend `CLAUDE.md`'s Shell section**, which today says only *"no `$(...)`"*. The general rule
   behind it is the documented one: **a command Claude Code cannot fully parse falls through to
   approval instead of being treated as read-only**, and commands over 10,000 characters always do.
   One clause on the existing line, same reason, same place. *Compound commands are **not** the
   trigger — `cd packages/api && ls` runs unprompted when each part qualifies. That claim came from a
   user-filed issue, was repeated here on 2026-08-24 without checking, and is corrected rather than
   quietly dropped.*
5. **Done 2026-08-26 — later than this plan recorded; see below.** **Amend `IDM-002` with the built-in read-only set** — `ls`, `cat`, `echo`, `pwd`, `head`, `tail`,
   `grep`, `find`, `wc`, `which`, `diff`, `stat`, `du`, `cd`, which run without a prompt and are
   **not configurable**.

   **`git` is not in that set, and this task claimed it was until 2026-08-25.** Seven measurements in
   this worktree settled it, and the decisive one is that **`git --version` prompted** — it touches
   no repository, so the failure is neither the worktree layout nor an index refresh, both of which
   were proposed and both of which were wrong. **Every git command prompts unless an allow rule
   matches it.**

   **The old claim was unobservable by whoever wrote it**, which is the part worth carrying into
   `IDM-002`: a model sees a denial as a tool error and **cannot see an approval at all**, so a silent
   run and an approved-after-prompt run are the same observation from the inside. The owner was the
   only instrument available and was never asked. **`IDM-002` gets the measured version; do not
   re-assert the old one.**

   *Why documentation and not allow rules, which is the question that produced this task:* an allow
   entry for a built-in read-only command grants nothing, so it is the fossil `IDM-002`'s pruning
   exists to remove — and it is a second home for a fact **Anthropic owns and can change**, which
   would then disagree with reality silently. Record it dated, with the source link, the way
   `../../wiki/` records everything learned by reading somebody else's software.

   **The settings half was executed ahead of the plan on 2026-08-24, on the owner's instruction**,
   and this task records what was done rather than proposing it: the four mutating git rules moved to
   the tracked file, the six read-only ones were **deleted rather than moved**, and two deny rules
   were added.

   ***The `IDM-002` half — which is what this task's title names — was not done, and was recorded here
   as though it were.*** Written **2026-08-26**, found by Task 4 going to point at it and discovering
   there was nothing there. **`IDM-002` had no read-only-set section at all.** *The failure is this
   plan's own recurring shape: a task with two halves, one executed, the whole marked done, and the
   note describing only the half that ran. Placeholder 4 below carried the wrong count for two days.*

   **And the amendment, once written, immediately contradicted the measurement above.** Anthropic's
   documentation puts **read-only forms of `git` inside the built-in set**; this branch's seven
   measurements say every git command prompts. **The conflict is recorded unresolved in `IDM-002`**
   with the one-observation check that settles it, because a model cannot see an approval and
   therefore cannot run that check alone. **No git allow rule was removed on the strength of it.**
6. Add Phase 11 to `milestone-2-corpus/implementation-plan.md`, which currently jumps 10 → closing
   review. **Done 2026-08-25, ahead of the plan.** Phases 11, 12 **and 13** went in together, because
   adding 11 alone leaves the list reading 8, 9, 10, "closing review" with two settled owner decisions
   missing. **Phase 13 is new** — the rate-limit response headers, allocated on the owner's
   instruction, and its entry carries its two gates rather than just a title. The same pass marked the
   capture step **discharged in fact, evidence pending Task 7**.
7. **Done 2026-08-26.** Freeze the evidence slice. **Index and derived metrics only, redacted to stable placeholders per
   `../../README.md`; no blobs.** Bodies are real source and real prompts.

### Group B — the CLI restructure

8. **Done 2026-08-26.** Subcommand skeleton, bare invocation still serving.
9. **Done 2026-08-26.** Move `check`, `train-dict`, `tune-dict`, `extract` across; **split verification out as
   `verify-archive`**; delete the old flags; update `Makefile` (one line — `Makefile:30`, `--check` →
   `check`; `make run` needs no change). **And fix `tests/test_corpus.py:453`, which shells out to
   `python -m ilirium_llm_router --extract <day>` and asserts on its output** — deleting the flag
   breaks it. *Named here because task 10 reads as "write new tests" and this is an existing one; the
   forward review found it, and the only other way to find it is to run `make test` and be surprised.*
10. **Done 2026-08-26 — 27 tests, and three mutations to show they can fail.** Tests for the surface, including that bare invocation still resolves to serve, that `--format` and
    `--out` are **required** on `extract`, and that `--project-name` without `--format jsonl` is a
    **parse error rather than a silent no-op**.

### Group C — the converter

*It was "first because it is the risk" until 2026-08-26, and **that rationale is spent**. Group C ran
ahead of the extractor so the expensive discovery would arrive early. **The forward review delivered
that discovery without any code being written** — the 45-call tail, the two normalisations, the third
role. The ordering now costs nothing and buys nothing, and it is left alone rather than churned.*

11. **Done 2026-08-26.** SSE reassembly **and** the plain-JSON path. **`ping` is a real event and is in the list** — see
    register §5.

    ***The buffered-reply count was wrong twice, and the second time it was wrong in the sentence
    that corrected the first.*** This task said *"63 of 168 real calls need the second"*, then said
    the conflation of *"not streamed"* with *"a buffered assistant reply"* had been fixed and the
    figure was **66**. **66 is the `count_tokens` count.** Measured 2026-08-26 by decompressing
    **every response blob in the live corpus** and reading its shape:

    | Response shape | Blobs | What the converter does |
    |---|---|---|
    | SSE | **808** | reassemble — the main path |
    | JSON, `type=error` | **93** | **skipped**, deferred by position 20 |
    | JSON, `{"input_tokens": N}` — a `count_tokens` reply | **47** blobs / 66 index rows | **skipped**: not a message |
    | zero-length | **4** | **skipped** |
    | **JSON, `type=message` — an actual buffered reply** | **1** | reassemble |

    **The plain-JSON message path is exercised by exactly one call in the whole corpus.** It is still
    built — position 15 filters nothing, and a `stream=false` success is legal — **but it must be
    tested synthetically, and a later session must not read "buffered replies are handled" as
    coverage.** → "What this phase does not settle".

    *The conclusion the old note defended does survive: both paths are needed. What does not survive
    is the impression that the second one is a third of the traffic. **It is one call in 979.***
12. **Done 2026-08-28.** Delta reconstruction across a session's calls, **spanning day folders**
    (finding 5), **the two normalisations without which it is wrong on real data** (finding 7),
    **and the error when a selected session has calls in a folder that was not passed.**

    ***The stated reason for that error does not survive this design, and the error is kept anyway.***
    This task said the failure mode was *"a plausible-looking transcript whose first turn silently
    contains a day of prior conversation"*. **That cannot happen here.** Turns are taken from the
    conversation's *latest* state rather than from per-call deltas, and requests are cumulative — so
    the final call carries the whole conversation and the array is fully expanded whichever folders
    were passed. Driven on the one real cross-day session, `20260825-1`, reconstructing from the later
    day alone: **depth 337 either way, and every message identical at every position.**

    **What it actually costs was measured, and is enough to keep the error:** **26 turns are
    misdated**, attributed to 2026-08-26 when they happened on 2026-08-25, and **12 assistant turns
    fall back to the poorer request-side copy** — against 0 with both folders. A transcript that
    claims a day it did not happen on is exactly the silent-and-plausible failure the original
    sentence was reaching for; it is the *timestamps* that lie, not the turns.

    **A third mechanism was needed and it is not a normalisation.** Finding 7's two make two
    *encodings* of one message compare equal. Neither helps when the content genuinely changed — 100
    times in the corpus, 9 of them changing role. → `notes-group-c.md`.
13. **Done 2026-08-28.** `uuid`/`parentUuid` synthesis and the record types the viewer needs —
    **register §9 carries the shape**. **Determinism is a test, not an aspiration** — convert twice,
    diff, expect zero bytes of difference.

    **All four `❓` are resolved** — three planned, plus `sessionId` which task 12 opened. Settled
    from the two sources position 17 names, **with the owner's go-ahead on the day**: the viewer's
    source, and one real session file read only far enough to learn field names.

    ***The `uuid` recipe had to change and that is a register edit, not an implementation detail.***
    `<request-blob-digest>` cannot be supplied by task 12's design — a turn comes from the
    conversation's latest state, so it belongs to no single call. Session, conversation and position
    are what a turn actually has. → §5.

    ***And the corpus found a defect the tests did not.*** Emitting all 36 conversations produced
    **1,615 records and 1,614 distinct `uuid5` values**. The final call's reply sits at position
    `depth` — the one turn no request carries — and the `too_large` gaps began numbering at `depth`
    too. **378 tests passed throughout.** Fixed in `transcript.py`, with the regression test the
    mutation run confirms can fail.
14. ~~**Drive it against the real corpus, diff it against the real session record, then open it in the
    viewer.**~~ **Struck 2026-08-26 on the owner's decision, and struck whole rather than narrowed.**
    The owner tests by hand **after the phase is finished**, having said plainly why: the ground-truth
    diff costs a great many tokens, it generates more decisions than it settles, and *"this is too
    early — I want to test by hand first, and only then will I have enough understanding of what I
    want."* **This phase's evidence is therefore mechanical: code and tests, plus task 21's mutation
    check.** → "What this phase does not settle", which now carries the consequence rather than
    leaving it implied.

    *Striking this also discharged a review finding for free. Task 14 **had nothing to run**: the writer
    for `--format jsonl` is task 15 below, in Group D, **after** it. The dependency ran backwards and
    would have forced a group reorder. Removing the task removed the inversion.*
15. ~~Run it against `corpus-gate` too — the second-source check.~~ **Struck 2026-08-26**, deferred to a
    later phase. Its value fell once error bodies were deferred: **22 of run-01's 49 responses are
    error JSON**, which this phase skips. **The corrected description of `corpus-gate` stays in finding
    4 regardless**, so no later session inherits the wrong picture of it.

### Group D — the extractor

16. **Done 2026-08-28.** Selection by session, model, path, **and `--agent`**, over one or more
    positional day folders. **Matching is exact on all three** (position 18) — so `--path
    /v1/messages` does **not** sweep in `/v1/messages/count_tokens`. Repeated filters of one kind are
    OR; different kinds are AND. *Measured on the corpus: **902** against **66**, and 902 + 66 + 11
    no-session rows = **979**, which is the arithmetic the exactness claim rests on.*

    ***And it gained one thing the plan forbade, on the owner's decision.*** Task 12's
    `MissingDayError` **could not fire from the CLI**: it must know a session has calls in a folder
    that was *not* passed, and this task was specified to read "the day folders it is given and
    nothing above them" with **no corpus-root concept**. `days_of_sessions` now reads the
    **`index.csv` of sibling day folders and nothing else**. *The exception is to this plan's
    phrasing, not to `../../reference/corpus.md`'s guarantee, which is about **blobs opening**
    standalone and is untouched.* → `notes-group-d.md`.
17. **Done 2026-08-28.** Output layout — `bodies/` and `projects/` under one `--out` — and
    `verify-archive`. **The day check runs before anything is written**, rather than letting
    `reconstruct` raise mid-run and leave a directory whose good files cannot be told from its
    abandoned ones.
18. **Done 2026-08-28.** **`--agent` built against the review run's traffic**, and it selects the
    **67** rows exactly. *The contingency this task carried — file a
    defect against `observe.py:40` if the review left `agent_id` empty — is **dead, discharged
    positively**. The forward review's cold run produced **67 rows** carrying an `agent_id`, and
    `observe.py:40` is confirmed by measurement for the first time in this project's history.*
19. **Discharged in fact 2026-08-26, ahead of the group** — driven as task 9's exercise, over all four day folders. The figures are in register §8 and the task stays visible rather than being struck. **Re-run `verify-archive` now that a dictionary exists.** The register records that there is **no
    post-dictionary end-to-end ratio** and that 3.317× must not be read as one. This closes that hole
    and is a **measurement, not a feature** — position 3 postpones dictionary *work*, not dictionary
    *numbers*.

    *This task said **`extract`** until 2026-08-26 and would have closed nothing. The ratio is printed
    at `cli.py:176`, inside the verify loop — which register §2 assigns to **`verify-archive`**, not to
    `extract`. **The split that created `verify-archive` moved the print statement away from the task
    that needs it, in the same revision, and neither noticed the other.** Two adjacent register rows
    are what made it visible, which is the second time in this phase `IDM-008`'s instrument has caught
    something two prose passes read past.*

### Group E — documentation

20. **Done 2026-08-28.** The temporary `README.md` note (position 3) — the dictionary commands and
    the new subcommands, marked as superseded by Phase 12. **It carries the Phase 12 commitment**,
    which is recorded in only one other place. *The section opens with the warning rather than
    closing with it, so a rewrite meets it before deciding what to keep.*
21. **Done 2026-08-28.** `reference/corpus.md` and `reference/observability.md` updated for the
    tools. *`corpus.md` had a sentence saying the extraction tool "is a later phase's subject" and
    naming a `--extract` flag that no longer exists — both replaced.* `observability.md` gains what
    it never had: **which columns anybody reads back.** Until this phase they had a writer and no
    reader, so nothing recorded that `timestamp`, `agent_id` and the two `*_ref` columns are now
    load-bearing outside the recorder.

### Group F — verify, harvest and close

22. **Done 2026-08-28.** **The register check** — `../../method/IDM-008-the-register.md`'s closing
    task. Every row below against the code, **and no `❓` left anywhere in the register.**
    **`evidence/register-check.py`, 89 checks, 0 failed**, and it exits 1 so it can be a gate rather
    than a report.

    ***It found something two `grep`s had missed, on its first run.*** A `❓` survived in a cell —
    not a live placeholder but a *reference* to one, in prose reading "the `❓`'s requirement is
    met". **Reworded rather than taught to the checker**, because a marker that sometimes means
    "unvalued" and sometimes means "the thing formerly unvalued" is a marker whose check cannot be
    trusted — which is the same defect as the one this task was rewritten to fix on 2026-08-26.

    *The script was itself mutated four ways — a constant drifted from its stated value, a constant
    renamed, a `❓` reopened in a cell, an SSE event dropped — and caught all four. **What it cannot
    check is prose**, so a row whose description has drifted still passes; the closing task is the
    script **and** a read.

    *This said "`❓` column empty" until 2026-08-26, and **the check could not fail**: there is no `❓`
    column. `❓` has always been a marker inside a cell, and the register's tables are
    `| Flag | Type | Default |` and `| Name | Value |`. The claim "the `❓` column is now empty" was
    written into this file and into `status.md` and committed, and it was true only because the column
    does not exist. **A check that cannot fail is not a check** — which is the exact defect `IDM-008`
    exists to catch, found by the forward review in the section describing the instrument.*
23. **Done 2026-08-28.** **Mutation testing on the converter**, systematically:
    **279 mutants, 105 survived; after the fixes, 277 mutants and 75.** `evidence/mutate.py`,
    hand-rolled on the owner's decision — a tool is parked in `../../backlog.md` under `IDM-003`.

    ***The per-task mutations were not this task and the difference is the finding.*** 23 targeted
    mutations ran across tasks 12, 13, 16 and 17; **all died and none surprised**, each having been
    chosen because a test was expected to catch it. **Targeted mutation tests the tests you wrote.**

    **105 decomposes into four categories and only three are defects** — ~24 are the harness
    mutating error-message wording, **parked** on the owner's decision. The rest: **twelve
    self-referential tests** (`assert len(key) == CONVERSATION_KEY_CHARS` cannot fail), **dead code**
    (`SSE_EVENTS` is read by nothing; an unreachable `default=`), and **twelve missing tests** —
    including `isMeta`, whose mutation would have **hidden the record that says the file is not a
    real transcript**. **All five real logic survivors are now dead.** → `notes-group-f.md`.

    ***The first sweep nearly destroyed the module it was measuring.*** Killed by a timeout, and
    `finally` does not run on `SIGTERM`: it left `transcript.py` as `ast.unparse` output — every
    comment stripped, 256 of 670 lines gone, **suite passing 427/427**. `git status` caught it. The
    harness now has three restore paths, tested by killing a run on purpose.
24. **Done 2026-08-28.** Harvest into `reference/lessons.md` and `reference/measurements.md`.
    Thirteen measurement rows, each with its slice. **Three additions to `lessons.md` and not one is
    a new lesson** — §1 gains a sixth form (a *justification* going stale while the requirement stays
    right), §7 gains the sharpest instance of its family (a test comparing the code to itself), and
    §8 gains a third practice (targeted versus systematic mutation, with this phase's numbers).
25. **Done 2026-08-28.** Merge `--no-ff` (**`7e53f74`**, 51 commits), then regenerate the branch
    index **after** the merge commit (**`f97c4b6`**, 22 rows). *The order is not a preference: the
    new row records `7e53f74`, so writing it first is impossible and amending afterwards would
    change the hash the row had just recorded.*

    ***`branch-index.py` refused before it wrote***, because `feat/phase-11-corpus-tools` had no
    entry in its `DESCRIPTIONS` — reported, exit 1, rather than inventing a description or dropping
    the row. **That refusal is the guarantee working**: a landed branch with no row is the defect
    `--check` exists to catch. The entry was added, then the table regenerated.

    **Phase 11 is closed.** Tasks 14 and 15 remain struck in place. The owner exercises the tools by
    hand **after** this merge, which is what striking task 14 bought.

## The register — every name and number this phase introduces

*Per `../../method/IDM-008-the-register.md`. **Authoritative for the value; the prose above holds the
why.** `❓` marks something named and never valued. **It is a marker inside a cell, not a column** —
this section said "that column is the instrument" until 2026-08-26, and Task 22's closing check was
written against a column that does not exist, so it could not fail. ~~**Three `❓` are live**~~ — **all resolved at Task 13 on 2026-08-28, and there were four by then**: task 12 added `sessionId`. **None is left.** Task 22's closing check now has something to check.*

### 1 · New modules

| Name | | |
|---|---|---|
| `src/ilirium_llm_router/extract.py` | selection over an index, output layout | **built at tasks 16–18, 2026-08-28** |
| `src/ilirium_llm_router/transcript.py` | SSE + JSON reassembly, delta reconstruction | **complete — task 11 built reassembly 2026-08-26, task 12 the reconstruction 2026-08-28** |
| `src/ilirium_llm_router/jsonl.py` | the viewer's record shapes | **built at task 13, 2026-08-28** |
| `src/ilirium_llm_router/cli.py` | restructured, not new | **modified** |

**Three, settled 2026-08-26.** This plan proposed folding `jsonl.py` into `transcript.py` on the
grounds that record shapes are small; the owner kept them apart. The split that earns it:
`transcript.py` answers *what was said* (reassembly, delta reconstruction, cross-day ordering),
`jsonl.py` answers *what the viewer will accept* (record shapes, `uuid` chaining, the schema note).
**The second is somebody else's schema and will move when their tool moves** — a boundary worth having
a file for.

### 2 · CLI — the exact spelling

| Command | Replaces |
|---|---|
| `ilirium-llm-router` (bare) | unchanged — serves |
| `ilirium-llm-router serve` | explicit form, new |
| `ilirium-llm-router check` | `--check` |
| `ilirium-llm-router train-dict` | `--train-dict` |
| `ilirium-llm-router tune-dict` | `--tune-dict` |
| `ilirium-llm-router extract` | `--extract`'s selection and output half |
| `ilirium-llm-router verify-archive` | `--extract`'s read-and-check half — **new command**, settled 2026-08-26 |

*There is **no** `to-jsonl` command. It was proposed, then proposed again as `extract --to-jsonl`, and
settled as `extract --format jsonl`. See §3.*

### 3 · `extract` flags

| Flag | Type | Default |
|---|---|---|
| *(positional)* `DAY...` | one or more paths | **required, repeatable** — the shell's glob is the "all days" case |
| `--out` | path | **required** |
| `--format` | `bodies` \| `jsonl`, repeatable | **required** — a run always states what it produces |
| `--session` | str, repeatable | all |
| `--model` | str, repeatable | all |
| `--path` | str | all |
| `--agent` | str, repeatable | all — **reinstated 2026-08-26** |
| `--project-name` | str | `corpus` — **error** if passed without `--format jsonl` |
| ~~`--day`~~ | — | **struck** — a required *option* is the wrong shape; days are positional |
| ~~`--verify-only`~~ | — | **struck** — it named the default; verification is now `verify-archive` |

### 4 · `verify-archive` flags

| Flag | Type | Default |
|---|---|---|
| *(positional)* `DAY...` | one or more paths | **required, repeatable** |

*No `--out`, by construction. It reads, verifies against the digest in each filename, and reports —
which is exactly what `--extract` does today.*

### 5 · Constants

| Name | Value |
|---|---|
| `JSONL_SCHEMA_NOTE` | **Valued 2026-08-28.** A format string in `jsonl.py`, carried in the note record's `content`. It names the tool and version, the generation moment, the session, the day folders, the call count, **the count that contributed no turn**, the gap count, the unconfirmed-tail count, and the five absent fields — and opens *"This is NOT a Claude Code session record"*. *The requirement list was met in full; the gap and unconfirmed counts are additions task 12 made necessary.* |
| the fidelity record's `type` | **Valued 2026-08-28: a `system` record with `subtype = "corpus-reconstruction"` (`SCHEMA_NOTE_SUBTYPE`), `isMeta: false`.** Settled from the viewer's source, not guessed: `if msg.message_type == "system" { return !is_hidden_system_subtype(...) }`, and `HIDDEN_SYSTEM_SUBTYPES` holds exactly `stop_hook_summary` and `turn_duration` — so an unknown subtype **renders**. **The placeholder's requirement is met:** it is not a *plain* `system` record, and the subtype distinguishes it from the three real ones observed (`turn_duration`, `away_summary`, `local_command`) and from any turn. Gaps use `corpus-gap` on the same footing |
| SSE event names consumed | `message_start`, `content_block_start`, `content_block_delta`, `content_block_stop`, `message_delta`, `message_stop`, `error`, **`ping`** — **all eight observed**, 2026-08-26 |
| **`content_block` types** | **Five, not three** — `text`, `tool_use`, `thinking`, **`server_tool_use`**, **`web_search_tool_result`**. *Added 2026-08-26: the register named the events and never what they carry, and the reassembler consumes these. Counts over the **whole** corpus, by reassembling every response: 552 / 654 / 461 / 4 / 4 — so **`tool_use` is the most common block here and `thinking` is not rare**. The last two are Anthropic **server-side** tools and were missed by a two-day sample, which is why the count was re-run over all four days* |
| **`content_block_delta` types** | `text_delta`, `input_json_delta`, `thinking_delta`, **`signature_delta`** — *`input_json_delta` carries a **tool input as JSON string fragments** that must be concatenated and only then parsed, which is the one piece of real work in reassembly. 64,260 of them in two days against 2,071 `text_delta`* |
| `message_delta`'s `stop_reason` | `tool_use` **626**, `end_turn` **181**, `max_tokens` **1**, over the whole corpus — so **most turns here end in a tool call**, not in text to the user |
| **skip reasons** — `transcript.py` | `empty`, `error`, `stream-error`, `not-a-message`, `malformed`, `incomplete`. **Six, and each is a different fact about the capture**, which is why they are not one `skipped` flag. Live counts: 93 `error`, 66 `not-a-message`, 11 `empty`, **1 `incomplete`**, 0 `stream-error`, 0 `malformed` |
| `SYNTHETIC_UUID_NAMESPACE` | **Minted 2026-08-28: `5791f885-4f45-4b01-bbd1-5ac2631bf167`.** **And the recipe changed with it, which is the more important half.** It was `uuid5(NS, "<request-blob-digest>:<record-index-within-call>")`; it is now `uuid5(NS, "<session_id>:<conversation-key>:<slot>")`. *Task 12's design cannot supply the old one: a turn is taken from the conversation's **latest** state, so it belongs to no single call and has no one request blob — the same objection that retired `<block-index>` on 2026-08-26, one level further up. Conversation and position are what a turn actually has, and both are stable because the message array is append-only (678 grew, 143 held, **0 shrank**).* |
| `SCHEMA_NOTE_SUBTYPE` / `GAP_SUBTYPE` | `corpus-reconstruction` / `corpus-gap` |
| `ABSENT_BY_CONSTRUCTION` | `cwd`, `gitBranch`, `version`, `toolUseResult`, `agent attribution` — the five named in the note |
| `CONVERSATION_KEY_CHARS` | **8** — hex characters of the **normalised** root message's sha256 that name a non-main conversation on disk. *A digest and not an ordinal: `-02` is stable only within one run, and a growing corpus or a different day selection silently repoints it. Measured over all 36 conversations — no within-session collision. Normalised matters: one session sent its opening message as a bare string in the first call and as blocks thereafter, and hashing raw bytes would give one conversation two names.* |
| `GAP_NO_REQUEST_BODY` | `no-request-body` — **not a skip reason.** A skip means a *response* carried no turn; this means the *request* body is not on disk to diff against. 45 rows, all `too_large` |
| `PROJECT_NAME_DEFAULT` | `corpus` — one bucket. **`corpus-<day>` was proposed and killed by finding 5**: a session spanning two days has no single day to file under |

### 6 · Existing names this must not collide with

`CorpusReader`, `CorpusError`, `CorpusWriter`, `DictionaryTrainer`, `Corpus`, `Call`, `CallRecord`,
`COLUMNS`, `MAX_ERROR_MESSAGE`, `TRAIN_LEVEL`, `RESCAN_EVERY`, `SUMMARY_EVERY`, `DRAIN_TIMEOUT_S`,
`_extract`, `_train_dict`, `_tune`, `_with_overrides`, `_report`, `_report_corpus`.

### 7 · Names that go on disk

| | Form |
|---|---|
| output root | **whatever `--out` names.** No default — nothing is written unless a destination is given |
| a session file | `<out>/projects/<project>/<session_id>.jsonl`, `<project>` defaulting to `corpus` |
| a session's **other** conversations | `<out>/projects/<project>/<session_id>-<key>.jsonl`, `<key>` being `CONVERSATION_KEY_CHARS` of the root digest. **Settled 2026-08-28 by the owner**, who chose one file per conversation over emitting only the main one. **A `session_id` holds several conversations** — 36 across 9 sessions, including a 66-call subagent carrying the parent's id. The **deepest** takes the plain name; depth and call count agree in all nine sessions here, but 111-against-2 is a margin 58-against-45 is not |
| extracted body | `<out>/bodies/<session_id>/<seq>-request.json` and `<seq>-response.json` **or** `<seq>-response.sse` |
| `<seq>` | **Five digits, zero-padded, assigned per session in `timestamp` order, starting at `00001`.** *Defined 2026-08-26; it was undefined, and the forward review priced that as silently mis-labelling every extracted body.* **Timestamp order, not index order** — `stats.py` says the index is in **completion** order, so reading it in file order would number a session's bodies by when each call *finished* |
| a row with no `session_id` | goes to `<out>/bodies/_no-session/`. **11 rows have one at 2026-08-26T15:16Z** — 9 × `/api/hello`, 1 × `/`, 1 × `/favicon.ico` — and `<out>/bodies//00001-request.json` is not a path. *Read **10** at 770 rows; the figure moves with the corpus and the shape does not* |
| never | **`~/.claude/projects/`** — position 12. Lossy reconstructions in the real history directory is not a reversible mistake |

*The response extension is not decoration: it is **`.sse` for a streamed reply and `.json` for a
buffered one**, and the encoding is legible without opening the file. **Task 17 settled how it is
decided: off the body's own first byte, not off the index's `stream` column.** `observe.py` sets
that column from **content-type** and the design deliberately allows the two to disagree, so the
bytes are one source instead of two — and it is the same question `reassemble` asks, so the
extractor and the converter cannot disagree either. **A row with no blob gets no file**, never an
empty one: the corpus holds four genuinely empty bodies and the two would be indistinguishable.*

*`projects/` sits directly under `<out>` so the viewer's Custom Claude Directory can be pointed at
`<out>` itself; `bodies/` sits beside it and the viewer ignores it. **That is why one `--out` serves
both formats** rather than needing two destinations.*

### 8 · Numbers measured, with their moment

**Two moments, and the second changed a premise this plan was written on.** Both are kept rather than
overwritten — a figure with its moment attached is a record, and replacing one loses the fact that
the corpus moved underneath it.

**Measured 2026-08-24, on a day folder that was still being written:**

| | Value | Slice |
|---|---|---|
| undicted ratio | **2.815×** | `2026-08-24` day folder, 280 blobs, **at 2026-08-24 while growing** |
| real calls | 171 rows | same folder, same caveat |
| streamed / not | 105 / 63 | of 168 `/v1/messages` |
| distinct sessions | 4 | same |
| populated `agent_id` | **0 of 171** | same |

**Measured 2026-08-25 18:27 local, over frozen copies of all three day indexes:**

| | Value | Slice |
|---|---|---|
| **a dictionary exists** | `req-2026-08-25T103250Z-9dd33823.dict`, **262,144 bytes** | `retrain.log`, `verdict=installed` at **2026-08-25T10:32:50Z** |
| **trainer's candidate score** | **3.317×**, incumbent `none` | the trainer's own holdout — window `2026-08-24`, 1 day, **69 samples / 180 holdout**, level 9 |
| rows carrying `9dd33823` | **328 of 331** | `2026-08-25` index. The other **3 are empty, not `none`** |
| rows carrying `none` | **317** and **10** | the `2026-08-24` and `2026-08-21` folders, entirely undicted |
| day folders | **3** | `2026-08-21`, `2026-08-24`, `2026-08-25` — every document saying "two" predates 2026-08-25 |
| `2026-08-24`, completed | **317 rows** | the same folder the **171** above came from, read mid-day |

**Do not compare 3.317× against 2.815× as though they were the same measurement.** 2.815× is
`--extract` over 280 stored blobs; 3.317× is the trainer scoring a candidate against a 180-sample
holdout at level 9. They answer different questions. Both spellings are kept so the difference
survives contact with a later reader who wants one number.

~~**`--extract` has not been re-run since the dictionary landed**, so there is **no post-dictionary
end-to-end ratio in this table**, and one must not be inferred from the candidate score.~~
**Closed 2026-08-26** — `verify-archive` was driven over all four folders as task 9's exercise; the
block below carries the result. *The warning it ends with survives the closure: the candidate score is
still not an end-to-end ratio, and the two are still not the same measurement.*

**171 → 317 is one folder read twice, not a discrepancy.** The first reading caught a day still being
written; the second is that day finished.

**Measured 2026-08-26 during ratification, over all four day indexes:**

| | Value | Slice |
|---|---|---|
| **day folders** | **4** — `2026-08-26` appeared | *the "3" one row-group above went stale in a single day* |
| total index rows | **770** | 10 + 317 + 413 + 30 |
| populated `agent_id` | **0 of 770** | every row, every folder. The column works; no subagent has ever run |
| **a session spanning two folders** | `20260825-1…` — **39** calls on the 25th, **19** on the 26th | the session that ratified this plan |
| distinct sessions | 3 on the 25th, 1 so far on the 26th | plus 3 empty-`session_id` rows on the 25th |
| **ground-truth session records on disk** | **3 of 3** for the `2026-08-25` index | `~/.claude/projects/…/<session-id>.jsonl`; filenames listed, contents not read |

**`2026-08-25` went 331 → 413 rows and `2026-08-26` went 19 → 30 during the ratification conversation
itself.** That is roughly two hours. It is the fourth separate occasion this document has recorded the
corpus moving underneath a measurement, and it is why position 14 accepts a **labelled live snapshot**
rather than pretending a still one is available.

**Measured 2026-08-26T15:16:22Z, on the frozen slice — and this is the first block here that is
citable, because it is the only one whose source is committed.** → `evidence/`, redacted, with
`freeze.py` beside it.

| | Value | Slice |
|---|---|---|
| total index rows | **979** | 10 + 317 + 413 + 239, four day folders |
| **populated `agent_id`** | **67 of 979**, **one** distinct agent | *replaces "0 of 770", which the review said needed a real number rather than a correction* |
| …and their parent | **all 67 inside one session** | `agent_id` is a **partition key**, not a filter — review finding 4, confirmed on the frozen slice |
| distinct sessions | **9** non-empty, **11** rows empty | across all four days |
| **a session spanning two folders** | **276 calls** across the 25th and 26th | it was **39 + 19** when finding 5 was written, on the same session |
| `too_large` | **45 rows, all in one session** — the largest, at 292 calls | the **only** sentinel present. **No response is ever `too_large`** |
| **sentinels never observed** | **four of five** — `dropped`, `absent`, `error`, and `none` as a *response* ref | `absent` does not appear even on the 9 router-authored `/api/hello` rows, which carry real digests |
| streamed ok / buffered ok | **807 / 67** | of 902 `/v1/messages` |
| error rows | **93** `http_error` + **2** with `stream` empty + **1** `client_disconnect` | all 93 are `429` |
| `count_tokens` | **66** | same sessions as `/v1/messages` |
| dedup | request **934 rows → 821 distinct**; response **979 → 934** | so `<seq>` cannot be derived from a digest |
| LM Studio | **1 row**, `google/gemma-4-e4b` | `2026-08-21` |

**770 → 979 in one afternoon**, the fifth occasion this document records the corpus moving under a
measurement — and the last one that has to, because from here the phase measures the frozen copy.

**Measured 2026-08-26 ~18:40 local, by driving `verify-archive` over all four day folders.** This
is the **same instrument on every row**, which none of the blocks above can say.

| Day | Blobs | Dictionary | Ratio |
|---|---|---|---|
| `2026-08-21` | 14 | none | **3.140×** |
| `2026-08-24` | 580 | none | **2.553×** |
| `2026-08-25` | 729 | `9dd33823` | **3.120×** |
| `2026-08-26` | 470 | `9dd33823` | **3.056×** |
| **all four** | **1793, 0 failed** | mixed | **2.927×** — 424,909,243 → 145,169,429 bytes |

**Every blob in the live corpus opens and verifies against the digest in its own filename.** 1793 of
1793. That is the round trip Phase 10 promised, driven at scale for the first time.

***The one number in this document that moved without the corpus growing a new day: `2026-08-24` read
**2.815×** at 280 blobs mid-day and reads **2.553×** at 580 blobs complete.*** Same folder, same
command, same absence of a dictionary — **the derived ratio fell as the day filled up.** Every earlier
note here warns that *counts* move under a measurement; this is the first showing that a **ratio** does
too, which is worse, because a count that looks stale is obvious and a ratio never does.

**A dicted day beats an undicted one on this instrument — 3.120× and 3.056× against 2.553× — and that
is still not a headline ratio.** Different days carry different traffic, so this is **suggestive and
uncontrolled**, not a measurement of what the dictionary is worth. `reference/corpus.md:193` refuses
headline ratios and this phase does not start one. **The controlled version is the dicted-vs-undicted
benchmark, which position 13 postponed into `../../backlog.md`.**

*1793 blobs against the frozen slice's 821 + 934 = 1755 distinct digests is **not** a discrepancy —
the slice was taken at 15:16Z and this run is some four hours later, on a corpus that is still being
written.*

*None of these goes in `reference/measurements.md` until **Task 7** freezes a slice — a number whose
slice is still moving cannot fill the four columns `../../README.md` requires. **The corpus was still
moving while this very table was written:** two copies of the `2026-08-25` index taken one minute
apart differed by 259 bytes.*

*(That sentence named **Task 5** until 2026-08-25. Task 5 is the `IDM-002` amendment and is already
executed — it cannot also be the task that freezes a slice; **Task 7** is "Freeze the evidence slice".
Two adjacent rows of this register are what made it visible, which is what `IDM-008` says the
instrument is for.)*

### 9 · The JSONL record shape — this phase's own output

***Added 2026-08-26. `IDM-008` requires "any record or index shape — columns in order, fields, the
schema version" and `../../README.md` repeats it, and the register carried neither — while §1 said
`jsonl.py` "answers what the viewer will accept" and then never said what that is.* The phase's entire
output had no row in its own register.**

| Field | Value |
|---|---|
| `type` | **Valued 2026-08-28. Three kinds are emitted**: `user` (user- and system-role turns), `assistant`, and `system` (the note and the gaps, each with a subtype). *Read from the viewer: **only four types carry `uuid`/`parentUuid`** — `user`, `assistant`, `system`, `attachment` — and the six others in a real file are session-level sidecars outside the chain. `EXCLUDED_MESSAGE_TYPES` is `progress`, `queue-operation`, `file-history-snapshot`, `last-prompt`, `pr-link`, `agent-name`, and none of ours is in it.* |
| `uuid` | `uuid5(SYNTHETIC_UUID_NAMESPACE, "<session_id>:<conversation-key>:<slot>")` — **changed at task 13, see §5 for why the digest form could not be built** |
| `parentUuid` | the previous record's `uuid`; `null` on the first record of a file |
| `sessionId` | the corpus's `session_id`, **verbatim in every file — the question task 12 opened is closed, 2026-08-28.** The viewer identifies a session by its **filename**, not by this field (`session_id: file_path_str`), and **two files carrying the same `sessionId` are not merged**. So one-file-per-conversation is safe and the value stays true |
| `timestamp` | the call's index `timestamp`, verbatim |
| `message` | the reconstructed turn |
| `cwd`, `gitBranch`, `version`, `toolUseResult` | **absent by construction** — never on the wire. *Confirmed against a real file: all four are present on every `user` and `assistant` record there, so their absence is visible to anyone comparing, which is why the note names them* |
| `isSidechain` | `false` on every record. **Not a guess and not nothing**: the viewer reads it, and the corpus's one subagent conversation is already a separate file, so no record here is a sidechain *of its own file*. Revisit if subagent partitioning is ever built — position 20 |

~~**The shape is `❓` where it depends on somebody else's schema.**~~ **Settled 2026-08-28.** The
viewer does not publish it, so task 13 read it from **two** sources, per the owner's decision of
2026-08-26 and with their go-ahead on the day: the viewer's own source, and **one** real session file read only far enough to learn the
field names. **Schema knowledge at design time is not the same act as the converter reading
`~/.claude/` at runtime** — the second is what "oracle, never input" forbids, and the plan did not
draw that line until now.

### 10 · The index shape — 26 columns, in order

*Also added 2026-08-26, and also required by `IDM-008`. The extractor selects on these; nothing in the
register named them. Verified three ways: `stats.COLUMNS` (20) + `corpus.INDEX_EXTRA_COLUMNS` (6),
concatenated at `corpus.py:71`; every day folder's `manifest` reading `index_columns: 26`; and the
header line on disk in all four folders.*

```
timestamp, session_id, agent_id, backend, model, path, stream,
input_tokens, output_tokens, cache_read_input_tokens, cache_creation_input_tokens,
stop_reason, request_bytes, response_bytes, ttfb_ms, duration_ms,
error_status, error_code, error_message, router_version,
request_ref, response_ref, queue_ms, store_ms, queue_bytes, request_dict_id
```

`INDEX_SCHEMA_VERSION` is **1**, and this phase does not change it — position 3 postponed the one
thing that would have.

### 11 · Sentinel values — what a `request_ref` holds instead of a digest

*Added 2026-08-26. **Five sentinels, and not one appeared in either document** — `grep` for
`too_large` over `plan.md` and `notes.md` returned nothing, while **45 rows on disk carry it**.*

| Constant | Value | Means |
|---|---|---|
| `DROPPED` | `dropped` | the queue was over its byte bound |
| `TOO_LARGE` | `too_large` | one body over `body_max_bytes`; **discarded, not truncated** |
| `ABSENT` | `absent` | **the router authored the body** — not one it carried |
| `STORE_ERROR` | **`error`** | compression or the write failed |
| `NO_DICTIONARY` | `none` | stored with no dictionary — a **word**, not `0` |

**`STORE_ERROR`'s value is `error`, not `store_error`.** The constant name and the string on disk
differ, which is exactly the kind of thing a register exists to put in adjacent rows.

**Only `too_large` is present in the corpus today**, on 45 rows. The extractor must treat all five as
"no blob here" rather than as a digest — **a sentinel silently used as a filename is a lookup that
fails at the filesystem**, which is a worse error than the honest one.

**Two more constants the extractor needs and §6 does not list:** `FANOUT = 2` and
`BLOB_SUFFIX = ".zst"`, which together reconstruct `<day>/<direction>/<digest[:2]>/<digest>.zst`.
`CorpusReader` offers `directions()`, `blobs()` and `read()` and **no index reader and no
digest→path helper**, so the extractor builds the path itself rather than "building on" the class.

## Placeholders in this file

*The section that exists so these are closed out deliberately rather than found by chance —
Phase 10's worked.*

1. ~~**Position 3 needs the owner's one word.**~~ **Closed 2026-08-26** — documentation only, and the
   three dictionary ideas are in `../../backlog.md` under a new `Dictionaries` section.
2. ~~**Three `❓` remain, and they are supposed to.**~~ **None remains — all resolved 2026-08-28 at Task 13, and there were four by then:** task 12 opened `sessionId` and task 13 closed it with the other three. *This item said "closed — the `❓` column is now
   empty" for one day. **There is no `❓` column**, so the claim was true only because the thing it
   described did not exist, and Task 22's check could not fail. The forward review found it.* The nine
   original placeholders were valued on 2026-08-26 — **three changing shape rather than acquiring a
   value**: `--day` became positional, `--verify-only` was struck as a duplicate of the default, and
   `to-jsonl` stopped being a command. **Three new ones were then opened deliberately**, all in §5 and
   §9, all resolved at Task 13: `JSONL_SCHEMA_NOTE`'s wording, `SYNTHETIC_UUID_NAMESPACE`'s literal,
   and the fidelity record's `type`. **Deferring a value to a task is a plan for getting one, not a
   value** — `IDM-008`'s rule, applied to this plan for the first time.
3. **The Record table** below — the merge commit, which cannot exist until the merge.
4. **Task 1 and Task 6 ran ahead of the plan; Task 5 was recorded as having done so and only half
   had.** *Corrected 2026-08-26.* This item read *"three tasks are already executed and say so — Task
   1, Task 5 and Task 6"* until Task 4 went to cite `IDM-002`'s read-only set and found the section
   did not exist. **Task 5's settings half ran on 2026-08-24; its `IDM-002` half was written on
   2026-08-26**, in order, as part of this phase. **No other task may claim early execution.** Both deviations ran ahead of the plan on the owner's instruction, and both are worth
   seeing rather than smoothing over. **Task 5** — the settings work — was done while diagnosing an
   unrelated problem. **Task 6** was done on 2026-08-25 and grew in the doing: it went in as Phases
   11, 12 *and* 13, because adding 11 alone would have left two settled owner decisions missing from
   the list.

   *This item read "two tasks… Task 1 and Task 5" until 2026-08-25. **An unapproved plan accumulating
   executed tasks is the thing to watch here** — three of Group A's seven are now done before the plan
   they belong to has been reviewed.*

## What this phase does not settle

- Whether archiving slows a call. Failure mode 3, still open.
- The vanishing-row race. Still parked, still needs the never-write-twice guarantee.
- **Whether the tools actually work, in the sense `../../../CLAUDE.md` means by *exercise it*.**
  **This is the phase's largest deliberate gap and it is stated first because of that.** The working
  agreement says *green tests are not evidence — drive the real thing*, and **task 14 was the step that
  did.** It is struck (position 19): the owner exercises the tools **after** the phase, having judged
  that a ground-truth diff costs too much and settles too little before anyone has held the tool.
  **So the phase's central question — can a captured corpus be read back out by somebody who did not
  write it — is answered mechanically inside the phase and confirmed by hand outside it.** The closing
  record must say so; **a phase note that reports green tests as though the question were closed would
  be the exact failure this bullet exists to prevent.** *The one measurement this milestone has already
  paid for twice is the one nobody took.*
- **Whether the plain-JSON message path works on anything but a synthetic fixture.** The whole live
  corpus holds **one** buffered assistant reply. The path is built and unit-tested; it is **not**
  exercised at scale, and *"both response encodings are handled"* must not be read as coverage of the
  second. *Found 2026-08-26 by decompressing every response blob — see task 11, which carried 66 as
  that count until then.*
- **Error responses, `count_tokens` calls, subagent partitioning, and the second-source check.**
  Deferred by position 20. **What the baseline does instead is mechanical and stated, not undefined:**
  a call contributes a turn **only if its response is a message**, and the rest are skipped and
  counted. *That rule is lossless because requests are cumulative — anything a skipped call carried
  reappears in the next real one — and it asks "is this response a message?", never "is this call a
  probe?", so it does not smuggle back the classification position 15 removed.*
- **That a subagent's turns will interleave into its parent's transcript.** Known, measured — **67
  rows carry an `agent_id` and all of them carry the parent's `session_id`** — and deliberately not
  fixed. Position 20; the owner sees it by hand first.
- **Anything about dictionaries beyond documenting what ships.** Response dictionaries,
  `list`/`show`/`install`, and a dicted-vs-undicted benchmark are all in `../../backlog.md` under
  `Dictionaries` — position 13, and the reason that section exists.
- Anything about LM Studio — **no local traffic exists in the captured corpus**, so every tool here
  is exercised against Anthropic material only. Stated because it is exactly the kind of gap a later
  session reads as coverage. *Accepted on 2026-08-26 with a reason rather than by omission: LM Studio
  natively implements the same `POST /v1/messages`, so its bodies are the same shape and are unlikely
  to move the converter. That is an argument, not a measurement, and it is written down so a later
  session can disagree with it.*
- **Whether the client-side fields can ever be recovered.** `cwd`, `gitBranch`, `version`,
  `toolUseResult` and agent attribution are absent by construction; the item in `../../backlog.md`
  records why capturing headers is **not** the fix.

## Record

| | |
|---|---|
| Branch | `feat/phase-11-corpus-tools` |
| Fork point | `f445d6f` |
| Merge commit | **`7e53f74`**, 2026-08-28, `--no-ff`, 51 commits. Branch index regenerated after it at **`f97c4b6`** |
