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
2026-08-25:  15b29c2a-3678-450e-8408-598fa7843099   39 calls
2026-08-26:  15b29c2a-3678-450e-8408-598fa7843099   19 calls
```

**That session id is the session that ratified this plan.** The conversation being used to design the
converter is itself the counter-example, and it was found by looking rather than by reasoning.

**Why this is the sharpest finding in the list.** Requests are cumulative — request *N* carries turns
1..*N*. A converter given only `2026-08-26` has **no previous call to diff against**, so it emits that
day's first request's entire prior history **as a single opening turn**. The output is not incomplete;
it is **misleading**, which is the exact condition this plan names as refuting the phase:
*"a fidelity loss that makes the viewer's output misleading rather than merely incomplete."*

**Two consequences, both settled as positions 7 and 12.** Day folders are **positional and
repeatable**, so `extract 2026-08-25 2026-08-26 --session 15b29c2a…` is expressible and
`extract logs/corpus/2026-*/` extracts everything without needing an `--all` flag or a corpus-root
concept. And the converter **errors** when a selected session has calls in a folder that was not
passed, rather than silently reconstructing a partial one. **That error is the whole defence** — it is
what keeps a cross-day session from failing quietly.

**6 · The real session records exist on this machine, which turns Task 14 from eyeballing into
diffing.** Claude Code keeps its own records at `~/.claude/projects/<mangled-path>/<session-id>.jsonl`,
and **all three session ids in the `2026-08-25` index have a file there** — `15b29c2a…`, `8aa605b9…`,
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

**Six groups. `notes-group-<letter>.md` per group**, per `../../README.md`'s split rule.

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

8. Subcommand skeleton, bare invocation still serving.
9. Move `check`, `train-dict`, `tune-dict`, `extract` across; **split verification out as
   `verify-archive`**; delete the old flags; update `Makefile` (one line — `Makefile:30`, `--check` →
   `check`; `make run` needs no change). **And fix `tests/test_corpus.py:453`, which shells out to
   `python -m ilirium_llm_router --extract <day>` and asserts on its output** — deleting the flag
   breaks it. *Named here because task 10 reads as "write new tests" and this is an existing one; the
   forward review found it, and the only other way to find it is to run `make test` and be surprised.*
10. Tests for the surface, including that bare invocation still resolves to serve, that `--format` and
    `--out` are **required** on `extract`, and that `--project-name` without `--format jsonl` is a
    **parse error rather than a silent no-op**.

### Group C — the converter

*It was "first because it is the risk" until 2026-08-26, and **that rationale is spent**. Group C ran
ahead of the extractor so the expensive discovery would arrive early. **The forward review delivered
that discovery without any code being written** — the 45-call tail, the two normalisations, the third
role. The ordering now costs nothing and buys nothing, and it is left alone rather than churned.*

11. SSE reassembly **and** the plain-JSON path. **`ping` is a real event and is in the list** — see
    register §5. *This task said "63 of 168 real calls need the second" until 2026-08-26; that figure
    was a partial-day snapshot and it conflated "not streamed" with "a buffered assistant reply". The
    current corpus has **66** buffered replies, and the conclusion is unaffected.*
12. Delta reconstruction across a session's calls, **spanning day folders** (finding 5), **the two
    normalisations without which it is wrong on real data** (finding 7), **and the error when a
    selected session has calls in a folder that was not passed.** The error is not a nicety: without
    it a cross-day session reconstructs into a plausible-looking transcript whose first turn silently
    contains a day of prior conversation.
13. `uuid`/`parentUuid` synthesis and the record types the viewer needs — **register §9 carries the
    shape**. **Determinism is a test, not an aspiration** — convert twice, diff, expect zero bytes of
    difference.
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

16. Selection by session, model, path, **and `--agent`**, over one or more positional day folders.
    **Matching is exact on all three** (position 18) — so `--path /v1/messages` does **not** sweep in
    `/v1/messages/count_tokens`. Repeated filters of one kind are OR; different kinds are AND.
17. Output layout — `bodies/` and `projects/` under one `--out` — and `verify-archive`.
18. **`--agent` built against the review run's traffic.** *The contingency this task carried — file a
    defect against `observe.py:40` if the review left `agent_id` empty — is **dead, discharged
    positively**. The forward review's cold run produced **67 rows** carrying an `agent_id`, and
    `observe.py:40` is confirmed by measurement for the first time in this project's history.*
19. **Re-run `verify-archive` now that a dictionary exists.** The register records that there is **no
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

20. The temporary `README.md` note (position 3) — the dictionary commands and the new subcommands,
    marked as superseded by Phase 12. **It carries the Phase 12 commitment**, which is recorded in only
    one other place.
21. `reference/corpus.md` and `reference/observability.md` updated for the tools.

### Group F — verify, harvest and close

22. **The register check** — `../../method/IDM-008-the-register.md`'s closing task. Every row below
    against the code, **and no `❓` left anywhere in the register.**

    *This said "`❓` column empty" until 2026-08-26, and **the check could not fail**: there is no `❓`
    column. `❓` has always been a marker inside a cell, and the register's tables are
    `| Flag | Type | Default |` and `| Name | Value |`. The claim "the `❓` column is now empty" was
    written into this file and into `status.md` and committed, and it was true only because the column
    does not exist. **A check that cannot fail is not a check** — which is the exact defect `IDM-008`
    exists to catch, found by the forward review in the section describing the instrument.*
23. **Mutation testing on the converter.** One deliberate fault, a targeted test must fail. A
    mutation that survives is a missing test or a dead line — find out which. **With task 14 struck,
    this is the strongest evidence the phase produces**, so it is no longer optional polish.
24. Harvest into `reference/lessons.md` and `reference/measurements.md`.
25. Merge `--no-ff`, then regenerate the branch index **after** the merge commit.

## The register — every name and number this phase introduces

*Per `../../method/IDM-008-the-register.md`. **Authoritative for the value; the prose above holds the
why.** `❓` marks something named and never valued. **It is a marker inside a cell, not a column** —
this section said "that column is the instrument" until 2026-08-26, and Task 22's closing check was
written against a column that does not exist, so it could not fail. **Three `❓` are live**, all
deliberate, all resolved at Task 13.*

### 1 · New modules

| Name | | |
|---|---|---|
| `src/ilirium_llm_router/extract.py` | selection over an index, output layout | new |
| `src/ilirium_llm_router/transcript.py` | SSE + JSON reassembly, delta reconstruction | new |
| `src/ilirium_llm_router/jsonl.py` | the viewer's record shapes | new |
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
| `JSONL_SCHEMA_NOTE` | **❓ — wording deferred to Task 13.** *Marked `❓` rather than left blank on 2026-08-26: `IDM-008`'s rule is that anything named and never valued is `❓`, and **deferring a value to a task is a plan for getting one, not a value**.* What it must contain is settled: the tool, the source days and session, the call count, **the count of calls skipped because their response was not a message**, the generation moment, and the five fields absent by construction — `cwd`, `gitBranch`, `version`, `toolUseResult`, agent attribution |
| the fidelity record's `type` | **❓ — must not be plain `system`.** A real `system` role occurs *inside* `messages` and reaches the transcript, so a `system` record announcing *"this is not a real record"* is **indistinguishable from a real turn**. Settled at Q4/N3 as "a `system` record at the head of the file" before that was known. Resolve at Task 13 |
| SSE event names consumed | `message_start`, `content_block_start`, `content_block_delta`, `content_block_stop`, `message_delta`, `message_stop`, `error`, **`ping`** |
| `SYNTHETIC_UUID_NAMESPACE` | **❓ — the literal is minted at Task 13.** The *mechanism* is settled and is not `❓`: `uuid5(NAMESPACE, "<request-blob-digest>:<record-index-within-call>")`, so **the same corpus produces the same file forever, on any machine.** Minted rather than borrowed so our ids cannot collide with anyone else's `uuid5` values. **Not** `uuid4` — Task 13 tests determinism by converting twice and diffing. *`<block-index>` was the spelling until 2026-08-26 and was undefined for a delta-reconstructed turn, which by construction is not a content block of any one response* |
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
| extracted body | `<out>/bodies/<session_id>/<seq>-request.json` and `<seq>-response.json` **or** `<seq>-response.sse` |
| `<seq>` | **Five digits, zero-padded, assigned per session in `timestamp` order, starting at `00001`.** *Defined 2026-08-26; it was undefined, and the forward review priced that as silently mis-labelling every extracted body.* **Timestamp order, not index order** — `stats.py` says the index is in **completion** order, so reading it in file order would number a session's bodies by when each call *finished* |
| a row with no `session_id` | goes to `<out>/bodies/_no-session/`. **11 rows have one at 2026-08-26T15:16Z** — 9 × `/api/hello`, 1 × `/`, 1 × `/favicon.ico` — and `<out>/bodies//00001-request.json` is not a path. *Read **10** at 770 rows; the figure moves with the corpus and the shape does not* |
| never | **`~/.claude/projects/`** — position 12. Lossy reconstructions in the real history directory is not a reversible mistake |

*The response extension is not decoration: it is **`.sse` for a streamed reply and `.json` for a
buffered one**, which at 105 streamed against 63 buffered is a distinction a reader meets immediately.
The encoding is legible without opening the file.*

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

**`--extract` has not been re-run since the dictionary landed**, so there is **no post-dictionary
end-to-end ratio in this table**, and one must not be inferred from the candidate score.

**171 → 317 is one folder read twice, not a discrepancy.** The first reading caught a day still being
written; the second is that day finished.

**Measured 2026-08-26 during ratification, over all four day indexes:**

| | Value | Slice |
|---|---|---|
| **day folders** | **4** — `2026-08-26` appeared | *the "3" one row-group above went stale in a single day* |
| total index rows | **770** | 10 + 317 + 413 + 30 |
| populated `agent_id` | **0 of 770** | every row, every folder. The column works; no subagent has ever run |
| **a session spanning two folders** | `15b29c2a…` — **39** calls on the 25th, **19** on the 26th | the session that ratified this plan |
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
| `type` | ❓ — see §5. The record kinds needed, and their spellings, come out of Task 13 |
| `uuid` | `uuid5(SYNTHETIC_UUID_NAMESPACE, "<request-blob-digest>:<record-index-within-call>")` |
| `parentUuid` | the previous record's `uuid`; `null` on the first record of a file |
| `sessionId` | the corpus's `session_id`, verbatim |
| `timestamp` | the call's index `timestamp`, verbatim |
| `message` | the reconstructed turn |
| `cwd`, `gitBranch`, `version`, `toolUseResult` | **absent by construction** — never on the wire |

**The shape is `❓` where it depends on somebody else's schema, and that is the honest state.** The
viewer does not publish it. Task 13 settles it from **two** sources, per the owner's decision of
2026-08-26: the viewer's own source, and **one** real session file read only far enough to learn the
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
2. **Three `❓` remain, and they are supposed to.** *This item said "closed — the `❓` column is now
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
| Merge commit | **not yet merged** |
