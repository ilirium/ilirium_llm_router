# Phase 11 — corpus tools: plan

**Draft, not approved. Nothing here is a build order** — `../../../CLAUDE.md`'s working agreement
says a design answer is not one, and this document is the proposal the owner reviews before Task 1.

**Subject.** The offline tools that sit on top of the store Phase 10 built: **extract** bodies out of
a corpus with selection, **train** dictionaries as a first-class command rather than a flag, and
**convert** captured calls into Claude Code session `JSONL` so a session can be read in
[`claude-code-history-viewer`](https://github.com/jhlee0409/claude-code-history-viewer). The CLI is
restructured into subcommands to hold them.

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
| 3 | **No new dictionary features.** The gap is that the existing ones are undocumented — the phase writes a user-facing note in the top-level `README.md`, explicitly temporary until Phase 12 reworks it | **owner**, 2026-08-24 — *see the caveat below, this is my reading of a free-text answer and needs one word of ratification* |
| 4 | The real input is the owner's own driven session at `to-run-server/logs/corpus/` | **owner**, 2026-08-24 |
| 5 | Work moves to **git worktrees** as the standing practice | **owner**, 2026-08-24 |
| 6 | Phase 12 is the installer (`uv tool`) and the `README.md` rewrite | **owner**, 2026-08-24 |

**Position 3 is the one I am least sure I have right.** The question asked what was missing from the
dictionary tooling; the answer was *"write a user-faced note in the main README.md to be visible, it
would be temporal, when we will rework the README.md in Phase 12."* I read that as **no new dictionary
code, document what ships**. If it instead meant *"and also add the standalone/response-dictionary
work"*, the register below is short by a section and Group D changes shape. **One word settles it.**

## The re-derivation before Task 1, and it moved three things

`../../../CLAUDE.md`: *check prior evidence before planning a rerun*. Done 2026-08-24, against the
owner's live corpus and Phase 9's frozen one. Four findings, and the first one invalidates a
measurement taken during this very session.

**1 · The corpus is live and was growing while it was being read.** Request blobs in the
`2026-08-24` day folder went **114 → 123** between two reads minutes apart; `index.csv` went 165
lines → 171 rows over the same span. **The router in `to-run-server` is still up and capturing.**

Every figure below is therefore a **snapshot with a moment attached**, and the phase must freeze a
slice before it measures anything. *This is the instrument lying with a plausible number again — the
Phase 10 pattern — except here the number was not wrong, it was unrepeatable, which is harder to see.*

**2 · The captured corpus is undicted, and the round trip works anyway.** Driven, not assumed —
`ilirium-llm-router --extract` on the `2026-08-24` folder, at the moment it held 280 blobs:

```
index_schema_version: 1
index_columns: 26
dictionaries: none
280 blob(s), 0 failed
30036825 → 10669134 bytes, 2.815x
every blob verified against the digest in its own filename
```

`request_dict_id` is `none` on **all 171 rows**, both day folders have an **empty `dicts/`**, and
there is no `logs/corpus/dicts/` in that worktree at all. `retrain.log` says why, and it is working
as designed rather than failing:

```
2026-08-21T14:29:14Z verdict=skipped reason=no-complete-day
2026-08-24T13:35:10Z verdict=skipped reason=too-few-samples window=2026-08-21 samples=0 holdout=4
```

**2.815× is the honest no-dictionary baseline on real traffic**, and it is *not* a headline ratio —
`reference/corpus.md:193` refuses those and this phase does not start one. It is a snapshot of one
growing day, undicted, and its only job is to be the number a dictionary must beat.

**3 · What the index actually holds, measured 2026-08-24 on 171 rows.** This is what the extractor
can select on, so an assumption here is expensive:

| Column | What is really in it |
|---|---|
| `path` | `/v1/messages` 168, `/api/hello` 3. **No `count_tokens` at all** |
| `backend` | `anthropic` **171 — no LM Studio traffic captured** |
| `model` | `claude-opus-5` 158, `claude-sonnet-5` 10, empty 3 |
| `stream` | **`true` 105, `false` 63.** Both response encodings are present |
| `session_id` | **4 distinct**, 3 rows empty (the `/api/hello` calls) |
| `agent_id` | **empty on all 171 rows** |

**Two of those change the design.** `stream: false` on 63 of 168 means the converter meets **plain
JSON replies as well as SSE**, so "reassemble the SSE stream" is half the job and a plan that says
only that is wrong. And **`--agent` selection would match nothing today** — the column exists, the
capture never populated it, and shipping a filter that silently returns empty is worse than not
shipping it.

**4 · Phase 9's gate corpus is usable input and is already on disk.** `logs/corpus-gate/` — 8.8 MB,
three runs, `requests/NNNNN.bin` as **plaintext JSON** and `responses/NNNNN.bin` as **raw SSE**, with
`manifest.csv` carrying `session_id` and `path`. It is not day-folder shaped, so it is no use to the
extractor — but it is a second, differently-shaped source for the converter, and having two is what
stops the converter being written against one folder's accidents.

## The question this phase closes

> **Can a captured corpus be read back out by somebody who did not write it — selectively, into a
> shape another tool already understands — without the store learning anything about the payload?**

Phase 10 settled that a day folder is self-contained and that every blob verifies. That is the
*storage* half. This is the *retrieval* half, and its sharp end is the converter: **the store went to
some trouble never to parse a body, and the converter parses every one of them.** That is not a
contradiction — it is the line this phase has to keep on the right side of. **Parsing lives in the
tools; the store stays opaque.** If that line moves, the phase has failed even with green tests.

**What would refute it:** a body the converter cannot reconstruct a turn from, or a fidelity loss
that makes the viewer's output misleading rather than merely incomplete. Group C is built to find
that early rather than at the close.

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

### The extractor

Selection over the index, output as files a person can open. It reads the day folder **and nothing
above it**, which is `reference/corpus.md`'s self-containment guarantee kept executable.

`--agent` is **not** implemented, on finding 3. The register carries the row struck with the reason,
so the next phase does not rediscover the column and assume it was forgotten.

### The converter, and the part that is actually hard

**Requests are cumulative.** Request *N* of a session carries turns 1..*N*, so the naive read — one
call, one exchange — reconstructs the same opening turn dozens of times.

**The proposal is delta reconstruction:** walk a session's calls in timestamp order; for each, diff
its `messages` array against the previous call's and emit only the **new** user-side entries, then
emit the assistant turn from that call's response. Tool results ride in as `tool_result` blocks in
the next request's user turn, so they arrive for free.

**Three fidelity limits, and they are limits rather than bugs.** The store keeps **bodies only, never
headers**, and Claude Code's own session records carry client-side facts that never crossed the wire:

| Field the viewer reads | Why the corpus cannot supply it |
|---|---|
| `cwd`, `gitBranch`, `version` | Client state. Never in an API body |
| `toolUseResult` | Claude Code's own enriched record. The wire carries `tool_result` content, not this |
| `agentId` / sidechain attribution | Header-derived, and empty on all 171 captured rows |

**The output must say so in-band rather than look complete.** How — a `system` line at the head of
each file, or a sidecar — is ❓ in the register.

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
2. **Fix `CLAUDE.md`'s inode note, first commit.** It says the code-2026 and OneDrive paths are the
   same directory and *"editing either edits both"*. With this clone there are now genuinely two
   checkouts and **the note tells a session the opposite of the truth**. Also correct
   `reference/corpus.md`'s mtime justification, which cites a cloud-synced `logs/` that this
   worktree's is not.
3. **Record the worktree practice** — an `IDM-001` amendment covering the layout, and the
   `temp/to-run-server` branch, whose prefix `IDM-001` does not define and which never merges.
   **Do not claim a new worktree starts with no allowlist** — the permissions doc says rules resolve
   *"through worktrees to the main checkout"* and apply in worktrees, so state what was observed and
   leave the mechanism to Task 3b.
4. **Amend `CLAUDE.md`'s Shell section**, which today says only *"no `$(...)`"*. The general rule
   behind it is the documented one: **a command Claude Code cannot fully parse falls through to
   approval instead of being treated as read-only**, and commands over 10,000 characters always do.
   One clause on the existing line, same reason, same place. *Compound commands are **not** the
   trigger — `cd packages/api && ls` runs unprompted when each part qualifies. That claim came from a
   user-filed issue, was repeated here on 2026-08-24 without checking, and is corrected rather than
   quietly dropped.*
5. **Amend `IDM-002` with the built-in read-only set** — `ls`, `cat`, `echo`, `pwd`, `head`, `tail`,
   `grep`, `find`, `wc`, `which`, `diff`, `stat`, `du`, `cd`, and read-only forms of `git`, which run
   without a prompt in **every** mode and are **not configurable**.

   *Why documentation and not allow rules, which is the question that produced this task:* an allow
   entry for a built-in read-only command grants nothing, so it is the fossil `IDM-002`'s pruning
   exists to remove — and it is a second home for a fact **Anthropic owns and can change**, which
   would then disagree with reality silently. Record it dated, with the source link, the way
   `../../wiki/` records everything learned by reading somebody else's software.

   **Executed ahead of the plan on 2026-08-24, on the owner's instruction**, and this task now
   records what was done rather than proposing it: the four mutating git rules moved to the tracked
   file, the six read-only ones were **deleted rather than moved**, and two deny rules were added.
6. Add Phase 11 to `milestone-2-corpus/implementation-plan.md`, which currently jumps 10 → closing
   review.
7. Freeze the evidence slice. **Index and derived metrics only, redacted to stable placeholders per
   `../../README.md`; no blobs.** Bodies are real source and real prompts.

### Group B — the CLI restructure

8. Subcommand skeleton, bare invocation still serving.
9. Move `check`, `train-dict`, `tune-dict`, `extract` across; delete the old flags; update `Makefile`.
10. Tests for the surface, including that bare invocation still resolves to serve.

### Group C — the converter, first because it is the risk

*Deliberately ahead of the extractor.* It is the only part that can fail on something a plan cannot
foresee, and Phase 10's lesson is that the expensive discovery should arrive early.

11. SSE reassembly **and** the plain-JSON path — 63 of 168 real calls need the second.
12. Delta reconstruction across a session's calls.
13. `uuid`/`parentUuid` synthesis and the record types the viewer needs.
14. **Drive it against the real corpus and open the result in the viewer.** Green tests are not
    evidence. This task is the one that says whether the phase works.
15. Run it against `corpus-gate` too — the second-source check.

### Group D — the extractor

16. Selection by day, session, model, path.
17. Output layout and bulk verification.
18. `--agent` struck, with the reason recorded rather than the row deleted.

### Group E — documentation

19. The temporary `README.md` note (position 3) — the dictionary commands and the new subcommands,
    marked as superseded by Phase 12.
20. `reference/corpus.md` and `reference/observability.md` updated for the tools.

### Group F — verify, harvest and close

21. **The register check** — `../../method/IDM-008-the-register.md`'s closing task. Every row below
    against the code, `❓` column empty.
22. **Mutation testing on the converter.** One deliberate fault, a targeted test must fail. A
    mutation that survives is a missing test or a dead line — find out which.
23. Harvest into `reference/lessons.md` and `reference/measurements.md`.
24. Merge `--no-ff`, then regenerate the branch index **after** the merge commit.

## The register — every name and number this phase introduces

*Per `../../method/IDM-008-the-register.md`. **Authoritative for the value; the prose above holds the
why.** `❓` marks something named and never valued — that column is the instrument, and it is
deliberately not empty yet.*

### 1 · New modules

| Name | | |
|---|---|---|
| `src/ilirium_llm_router/extract.py` | selection over an index, output layout | new |
| `src/ilirium_llm_router/transcript.py` | SSE + JSON reassembly, delta reconstruction | new |
| `src/ilirium_llm_router/jsonl.py` | the viewer's record shapes | new |
| `src/ilirium_llm_router/cli.py` | restructured, not new | **modified** |

*Three modules or two is ❓ — `transcript.py` and `jsonl.py` may not earn separate homes.*

### 2 · CLI — the exact spelling

| Command | Replaces |
|---|---|
| `ilirium-llm-router` (bare) | unchanged — serves |
| `ilirium-llm-router serve` | explicit form, new |
| `ilirium-llm-router check` | `--check` |
| `ilirium-llm-router train-dict` | `--train-dict` |
| `ilirium-llm-router tune-dict` | `--tune-dict` |
| `ilirium-llm-router extract` | `--extract` |
| `ilirium-llm-router to-jsonl` | new — **name ❓**, `to-jsonl` / `sessions` / `replay` |

### 3 · `extract` flags

| Flag | Type | Default |
|---|---|---|
| `--day` | path | required |
| `--session` | str, repeatable | all |
| `--model` | str, repeatable | all |
| `--path` | str | all |
| `--out` | path | ❓ |
| `--verify-only` | flag | today's behaviour |
| ~~`--agent`~~ | — | **struck** — empty on all 171 real rows |

### 4 · `to-jsonl` flags

| Flag | Type | Default |
|---|---|---|
| `--day` | path | required |
| `--session` | str, repeatable | all |
| `--out` | path | ❓ |
| `--project-name` | str | ❓ — the folder name under the output root |

### 5 · Constants

| Name | Value |
|---|---|
| `JSONL_SCHEMA_NOTE` | ❓ — the in-band fidelity statement, if that is the shape chosen |
| SSE event names consumed | `message_start`, `content_block_start`, `content_block_delta`, `content_block_stop`, `message_delta`, `message_stop`, `error` |
| `SYNTHETIC_UUID_NAMESPACE` | ❓ — must be deterministic so reruns produce stable files |

### 6 · Existing names this must not collide with

`CorpusReader`, `CorpusError`, `CorpusWriter`, `DictionaryTrainer`, `Corpus`, `Call`, `CallRecord`,
`COLUMNS`, `MAX_ERROR_MESSAGE`, `TRAIN_LEVEL`, `RESCAN_EVERY`, `SUMMARY_EVERY`, `DRAIN_TIMEOUT_S`,
`_extract`, `_train_dict`, `_tune`, `_with_overrides`, `_report`, `_report_corpus`.

### 7 · Names that go on disk

| | Form |
|---|---|
| output root | ❓ |
| a session file | `<root>/projects/<project>/<session_id>.jsonl` |
| extracted body | ❓ — `<out>/<session>/<seq>-{request,response}.json`? |

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

*None of these goes in `reference/measurements.md` until **Task 7** freezes a slice — a number whose
slice is still moving cannot fill the four columns `../../README.md` requires. **The corpus was still
moving while this very table was written:** two copies of the `2026-08-25` index taken one minute
apart differed by 259 bytes.*

*(That sentence named **Task 5** until 2026-08-25. Task 5 is the `IDM-002` amendment and is already
executed — it cannot also be the task that freezes a slice; **Task 7** is "Freeze the evidence slice".
Two adjacent rows of this register are what made it visible, which is what `IDM-008` says the
instrument is for.)*

## Placeholders in this file

*The section that exists so these are closed out deliberately rather than found by chance —
Phase 10's worked.*

1. **Position 3 needs the owner's one word.** Documentation only, or dictionary work too.
2. **Every `❓` in the register.**
3. **The Record table** below.
4. **Two tasks are already executed and say so — Task 1 and Task 5.** No other task may claim it.
   Task 5 ran ahead of the plan on the owner's instruction, which is a deviation worth seeing rather
   than smoothing over: the settings work was done while diagnosing an unrelated problem, and the
   task now records it instead of proposing it.

## What this phase does not settle

- Whether archiving slows a call. Failure mode 3, still open.
- The vanishing-row race. Still parked, still needs the never-write-twice guarantee.
- Whether a response dictionary pays. Still in `../../backlog.md`.
- Anything about LM Studio — **no local traffic exists in the captured corpus**, so every tool here
  is exercised against Anthropic material only. Stated because it is exactly the kind of gap a later
  session reads as coverage.

## Record

| | |
|---|---|
| Branch | `feat/phase-11-corpus-tools` |
| Fork point | `f445d6f` |
| Merge commit | **not yet merged** |
