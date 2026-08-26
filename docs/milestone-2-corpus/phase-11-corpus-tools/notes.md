# Phase 11 — corpus tools: notes

**Not yet merged.** *(Closed out at the merge, per `plan.md`'s "Placeholders in this file".)*

**Branch `feat/phase-11-corpus-tools`, forked from `main` at `f445d6f`, opened 2026-08-24.** The
first phase of this project worked in a **git worktree** rather than in the trunk checkout —
`../../../../phase-11-corpus-tools`, beside `main` and `to-run-server` under a bare clone.

**`for-the-owner.md` is beside this file, and it is written to a person rather than to a session.**
Questions only the owner can answer, ideas that are not this phase's business, and things I would do
differently. **Nothing in it blocks the build** — anything that did was asked in the session. Started
2026-08-26 on the owner's suggestion; **no tier, no rule, no template**, deliberately.

## How to read these notes

**Written while measuring, not afterwards** — `../../README.md` asks every phase note to say which,
because it changes how far a reader should trust the narrative. Each section was written in the session
that did the work, and where a figure was later found wrong it is **struck in place** rather than
replaced, so the mechanism that caught it stays visible.

**This file is the entry point and it is not the whole record.** A task group's notes live in
`notes-group-<letter>.md`; what stays here is what belongs to **no** group — the re-derivation before
Task 1, the session boundaries, the forward review, and what was open at the end of a group.

**Read by section.** `grep -n '^## ' <file>` first.

## Index of the group files

*In the order they were written, which is the chronology the letter-sorted split otherwise breaks.*

| | | |
|---|---|---|
| `notes-group-a.md` | **Group A — open the phase**, tasks 1–7 | **complete.** Its first three sections predate the group structure and are Task 5's working record, written 2026-08-24 and 2026-08-25 |
| `notes-group-b.md` | **Group B — the CLI restructure**, tasks 8–10 | **complete**, 2026-08-26. The first group in this phase to change `src/` |
| `notes-group-c.md` | **Group C — the converter**, tasks 11–13 | **in flight** — task 11 done, 12 and 13 not. Tasks 14 and 15 are **struck in place** |
| *(none yet)* | Groups D, E, F | not started |

**The split happened on 2026-08-26**, at the owner's instruction, once the phase had three groups' worth
of sections in one file. *`notes.md` was 963 lines by then. `../../README.md` says to expect this file
to stay the larger one and that this is not a failure of the rule — what the split buys is that a group
file can be read whole.*

## Verified by

*`../../README.md`: what was run, when, and what it produced — because **green tests are not a
sign-off**, and every phase here was signed off by driving the real thing.*

**The phase is in flight, so this line is not a sign-off yet.** What has been driven, all 2026-08-26 in
this worktree:

| What was driven | What it produced |
|---|---|
| `verify-archive` over **all four live day folders** | **1793 blobs, 0 failed**, every one verified against the digest in its own filename. Phase 10's round trip at scale for the first time |
| `reassemble` over **every response blob**, joined back to the index | **979 rows, 0 unresolved, 0 contradictions** against an `error_status` column written at capture time months earlier |
| Every CLI invocation shape, through the real parser | bare, `serve`, `-c` on either side of the subcommand, every `extract` error path, and the deleted flags — exit codes checked without a pipeline |
| `freeze.py` over the live corpus | the frozen slice, **979 rows**, secrets pass clean |
| Three mutations of `cli.py` | each killed by **exactly one** test, file restored byte-identically |
| `make test` / `make lint` / `make check` | **355 passed** / clean at the pinned `0.16.1` / valid |

***The one thing still owed is the largest.*** Task 14 is struck, so **the owner exercises the tools by
hand after the phase**, and **task 23's mutation testing on the converter** is the strongest evidence
the phase itself will produce. **A closing record that reports green tests as though the central
question were closed is the exact failure the plan's first "does not settle" bullet exists to prevent.**

## The re-derivation before Task 1

**Held 2026-08-24, before the plan was written, and it moved three things.** The findings are in
`plan.md`'s section of that name rather than duplicated here; what belongs in the notes is *how* they
were found, because two of them were found by accident and that is worth not repeating by accident.

**The corpus was read twice by chance.** The first read counted 114 request blobs; a later
re-count, run only because a blob total and an index row count disagreed by four, returned **123**.
The router in `to-run-server` was still up. **The disagreement was the signal, and it was nearly
explained away** — the plausible story was that `wc -l` miscounts a CSV whose free-text
`error_message` column can hold newlines, which is *also true* and would have accounted for a small
gap. Two mechanisms, one of them real, and the wrong one was the more sophisticated.

*This is `../phase-10-body-store/`'s "interrogating a passing check" arriving unprompted: **what
would make this discrepancy innocent anyway?** The answer existed, and it was not the explanation.*

**The empty `dicts/` looked like the invariant failing and was not.** `reference/corpus.md` warns
that a day folder holding a blob whose dictID names an absent dictionary is a real corruption that
**nothing reports until somebody reads it back** — so an empty `dicts/` in both day folders read as
exactly that. Reading it back is the check, `--extract` is the instrument, and it returned **280
blobs, 0 failed**. `request_dict_id` is `none`, not a dictID: the blobs name no dictionary, so there
is none to be missing. **The alarming reading and the true one differ by one column of the index.**


## Where the opening session stopped — 2026-08-24

**The project-level handoff is `../../prompt.md`, rewritten for this phase on 2026-08-24, and
`../../status.md` carries the in-flight row.** This section is the *phase's* record of its opening
session and does not repeat them.

*It briefly claimed both files were stale "until Task 6 fixes them", which was wrong twice over:
Task 6 is about `../implementation-plan.md`, and `status.md`'s in-flight table is **live state** that
`../../method/IDM-001-git-branching.md` requires a branch to appear in the moment it opens — not
phase work to be scheduled. Both were updated the same day.*

**Start in the `phase-11-corpus-tools` worktree.** The plan, these notes and the settings change are
on the branch; a session started in `main` sees none of them.

**Four commits, tree clean:** `052ea3e` opened the phase, `12ada32` fixed a dead WebFetch domain,
`3d8ae54` added the deny rules and folded the git allows, `9e0b59d` recorded that the denies did not
fire. *(Said "three" over a list of four until 2026-08-26, when the forward review's cold run counted
them. A prose count beside the thing it counts, again.)*

### The first thing to do, and it costs nothing — *run 2026-08-25, and it is done*

**Was:** run `git add -A` on a clean tree; blocked → settings are session-cached and the rules work;
not blocked → a tracked permission change on a phase branch has no effect until it merges.

**It was blocked.** Settings are session-cached, the rules work, and the merge-scope constraint Task 3
was going to have to record does not exist. The full result, and the larger finding the check ran into,
are two sections above.

### Two things waiting on the owner

1. **Position 3** in `plan.md`'s settled table — whether *"document the dictionary tooling"* also
   means build something. One word, and it changes whether Group D has another section.
2. **Every `❓` in the register**, listed in "Placeholders in this file".

### What is deliberately not in the plan

**The auto-mode classifier diagnosis.** A day of telemetry was spent establishing that Claude Code's
auto-mode classifier gets HTTP 429 from Anthropic — 66 of 232 calls, **every one of them
non-streaming**, against 138 of 145 streaming calls succeeding. It is **not a router defect**: the
router relays the upstream status with its headers, `retry-after` and `anthropic-ratelimit-*` are not
in `DROPPED_FROM_RESPONSE`, and a streaming call to the same model succeeded five seconds after five
consecutive 429s on it.

**It is not Phase 11's subject and no task covers it.** What it left behind that *is* the project's:
a `backlog.md` item to overturn, since `backlog.md`'s *"do not go looking"* note on the rate-limit
headers rests on the recorder keeping the error body's symbolic type — and 66 rows of
`rate_limit_error: Error` do not say **which** limit. That reasoning failed its first real test.
**Two open upstream issues stall on exactly the measurement this router could take:**
[`anthropics/claude-code#82653`](https://github.com/anthropics/claude-code/issues/82653) and
[`BerriAI/litellm#30365`](https://github.com/BerriAI/litellm/issues/30365).


## Where the second session stopped — 2026-08-25

**No phase task was started, and no corpus tool was written.** The session opened on the one check the
handoff put first, and the check turned into the whole session. What it produced is in the two
sections above; this is the state it leaves.

**Still five commits, and the tree is deliberately dirty.** One modified file — `.claude/settings.json`
— **uncommitted on purpose**, because it cannot be exercised until a restart and `3d8ae54` already
demonstrated what committing first costs. `settings.local.json` was deleted by the owner; it was
untracked, so git records nothing of it.

**Nothing moved on Group A, the register, or the plan's approval.** The two items waiting on the owner
are unchanged and still waiting: **position 3** in `plan.md`'s settled table, and **every `❓` in the
register**.

**Task 5 gained its material.** `IDM-002` now has a measured account to record rather than an
inherited claim — that git is outside the built-in read-only set, that deny is exact-match while allow
is a wildcard, and that a model cannot observe its own approvals. The third of those is the reason the
first was wrong in `../../prompt.md` for a day.

**Task 3 lost a constraint.** The worktree practice it records does not need to say anything about
tracked permissions being inert until merge, because they are not — they are inert until restart.


## Where the third session stopped — 2026-08-25

**No phase task ran. Everything below is either the settings work closing out, or work that belongs to
other branches and was kept off this one.**

**The three probes ran and the settings file was committed** — `b70769a`, in that order, which was the
whole point. Recorded in full above under "What `.claude/settings.json` now says".

**Then the owner turned auto mode on to test whether Anthropic's rate-limiter had been fixed, and it
failed inside two minutes.** The result is `../../bugs/BUG-001-non-streaming-messages-rejected-as-rate-limited.md`,
on `main` — **not on this branch**, because the classifier diagnosis is not this phase's work and
`../../method/IDM-001-git-branching.md` gives documentation its own prefix. It went to
`docs/bugs-tier`, forked from `main`, merged `--no-ff`, and the tier it introduced is new.

**What this branch kept**, because both correct text this branch's own commits added:

- **Phase 13 allocated** in `../implementation-plan.md` for the rate-limit response headers, with its
  two gates written into the entry rather than left to be rediscovered — `calls.csv` takes no new
  columns under Milestone 2's non-goals, and the store's bodies-only-never-headers promise means a
  **named allowlist** rather than a copy. Phases 11 and 12 were added at the same time; the list ran
  8, 9, 10, "closing review".
- **The capture step marked discharged in fact, evidence pending Task 7.** It had read "NOT
  discharged" since 2026-08-17 on a ground that stopped being true on 2026-08-24.
- **A correction to this branch's own text, the same day it was written**: *no LM Studio traffic has
  **ever** been captured* overreached. The 171 rows are the corpus; `calls.csv` holds 15 LM Studio
  calls on 2026-08-21. One population is a subset of the other and they are easy to conflate.

**Two things a session picking this branch up should not get wrong.**

**`main` was merged into this branch to bring `docs/bugs/` onto it**, which is a shape this project
had not used before — the trunk into a phase branch, rather than the reverse. The reason is specific:
the handoff documents cite `BUG-001`, **a path in backticks is a link here**, and the branch could not
resolve them. `link-check.py` reported **seven** broken links repairable only from the other side.
Un-backticking them would have silenced the instrument without fixing anything, which is the one
option that was refused. Baseline restored to **86**.

**A fresh worktree reports 13 more broken links than this one, and it is not a regression.**
`.claude/settings.local.json` is gitignored, so `git worktree add` does not create it, and a path in
backticks is a link here. That is the same 13 measured on 2026-08-25 when the file was briefly
removed.

**A merged branch is kept here, and `../../procedures/branch-index.py` enforces it. Found by breaking
it.** `docs/bugs-tier` was deleted straight after its merge as tidying the owner had not asked for.
**Nothing was lost** — `git branch -d` refuses an unmerged branch, and `c889207` is the second parent
of the merge commit on `main`, so it stays permanently reachable. **What broke was the index.** The
script's `stale` check reports a description naming a branch that no longer exists and **refuses to
render at all**, on the stated ground that a half-written table spliced into the file is worse than
none. So the next merge's regeneration would have failed before doing anything, with
`../../reference/branches.md` correct on disk but unverifiable.

**Two things were already available and were not consulted.** Every one of the twenty other branches
survives — `docs/add-claude-md` and `feat/phase-0-skeleton` among them, merged weeks earlier — so
`git branch -a` answers this in one line. And `../../method/IDM-001-git-branching.md` has **already
reversed a branch-deletion rule once**: `EPD-004` decision 14 said a rejected plan's branch is
deleted, and 2026-08-17 changed it to merged-and-marked, because *"a deleted branch was the one place
this project discarded a refusal."* That section is about **rejected plans, not merged ones**, so this
deletion did not violate its letter — but it ran against the grain of the only statement the method
tier makes on the subject, and the tool enforces the general case that the rule does not state.

Restored with `git branch docs/bugs-tier c889207`; `--check` then reported **"branches.md is current:
21 rows"**, which also establishes that the generated table had been right the whole time and only the
ref was missing.

**One instrument lesson, and it generalises past permissions.** The probe table in the handoff assumed
its three outcomes were readable by whoever ran them. Only one was: a denial arrives as a tool error,
while a silent run and an approved-after-prompt run are the same observation from inside the model.
**A probe whose outcomes are indistinguishable to its reader is not a probe until someone who can tell
them apart is asked.** The same shape produced `BUG-000`'s founding rule hours later — *an absence is
not a fix* — arrived at independently, from counting 429s rather than from watching prompts.


## What is open at the end of Group A

*(**Corrected 2026-08-26**, on the forward review's finding 15. This read "Group A has not started"
while `plan.md` recorded three of its seven tasks done — **Tasks 1, 5 and 6**, all executed ahead of
the plan on the owner's instruction. The two statements sat in two files for two days. A cold reader
opening the notes first would have re-done the `IDM-002` amendment and the implementation-plan edit,
which is exactly the cost the review priced.)*

---


## The forward review — both runs and the reconciliation, 2026-08-26

**Protocol: `../../method/IDM-004-reviewing-unexecuted-work.md`. Charter: `review-charter.md`, written
first and committed at `8bb501c` before either run started**, because `IDM-004`'s first rule is that
the charter decides what the review finds.

**Subject:** `plan.md` at `2d04840` — the ratification revision, not the version any earlier session
saw. Tasks 2, 3, 4, 7 and Groups B–F. Tasks 1, 5 and 6 out of scope as executed.

| | |
|---|---|
| Runs | the author (this session) and one fresh-context agent, **in parallel**, read-only |
| Cold run's cost | ~157k tokens, 42 tool calls, ~23 minutes |
| Findings | **~18 distinct.** 11 by the cold reader alone, 3 by the author alone, ~4 by both |
| Overlap | **~22%** — and see "What this says about `IDM-004`" below, because it is **not** comparable with Phase 10's 18% |

### The departure from `IDM-004` that was declared in advance

**`IDM-004` assumes the author run is performed by the session that *wrote* the document.** That
session was gone. This one is its successor by handoff: it ratified and revised the plan on 2026-08-26
but did not hold the 2026-08-24 interviews behind positions 1–6. **The charter said so before the runs
rather than after**, which is why the overlap figure above is recorded with a warning attached instead
of being compared.

---

### One refutation was checked and did not survive

**`IDM-004`: *verify a refutation before accepting it. A reviewer can be confidently wrong.*** This is
the run where that rule earned its place.

**The cold reader reported that finding 3's `agent_id` prediction had already resolved *before* the
review began**, from "a subagent spawned earlier today" — 20 rows, timestamps 12:51:08–12:56:21.

**Checked, and the causation is backwards.** Across all four day folders there is **exactly one
distinct `agent_id`**, on **67 rows**, running 12:51:08 → 13:10:53. One value, not two. Those rows are
**the cold reader's own calls**: it read the index partway through its own run, saw 20 of them, and
attributed them to somebody else. The count reached 67 by the time it finished.

**So the prediction resolved positively, and it resolved *because of* this review run — exactly as
`plan.md`'s finding 3 said it would.** The outcome the reviewer reported is right; the mechanism it
gave is not. **`observe.py:40` is confirmed by measurement for the first time in this project's
history**, and task 18's defect-filing contingency is dead.

*This is the repository's own recurring shape landing on the reviewer rather than on a session: a
plausible reading and the true one, one query apart. It is the sixth recorded instance.*

---

### Accepted, ranked by what it costs to find later

**Verified against the disk by the author before acceptance, not taken from the report.**

| # | Finding | Evidence re-checked | Lands on |
|---|---|---|---|
| **1** | **45 consecutive calls have no stored request body.** `request_ref = too_large`, all in session `ad9392ae` — the corpus's largest at 292 calls, the one a reader would pick to demo. Structural, not a fluke: request bodies grow monotonically, so every long session eventually crosses the cap and **the tail is always what is lost** | **45 rows, the only sentinel present in the whole corpus** | task 12, `JSONL_SCHEMA_NOTE` |
| **2** | **"Requests are cumulative" is false on raw bytes.** True only after two normalisations the plan never names: `cache_control` markers migrate between calls, and the same message is serialised as a bare string in one call and as content blocks in the next. Raw: 9 prefix / 84 not. Normalised: 85 / 8. Plus a filter: 75 / 0 | accepted on the reviewer's evidence; the author's own corpus-gate check confirmed the premise holds *with* retries as the visible artefact | tasks 11, 12, 13 |
| **3** | **Interleaved request classes share one `session_id`** — recap, suggestion-mode, two-message classifiers, and `count_tokens`. **Four kinds, not the five reported** — see the correction below | `count_tokens`: **65 rows** — 0/21/43/1 across the four days. The plan says "**No `count_tokens` at all**" | task 12 |

***One of the reviewer's five classes was a real user message and is struck.*** It listed
`"Ping to you to keep cache warm: I still reading and thinking"` ×2 as a synthetic probe. **The owner
typed it, twice, and confirmed so on 2026-08-26 when asked.** The author flagged it as suspect before
the owner was asked, on the grounds that it appears verbatim in this session's own dialogue — *a class
of error only available to a reviewer that cannot see the conversation it is reading about.* **Had
"drop the probe classes" been implemented from the reviewer's list unchecked, it would have deleted
genuine turns** — the exact failure this phase names as refuting it.
| **4** | **`agent_id` is a partition key, not a filter.** A subagent's calls carry the **parent's** `session_id`, so a converter keyed on session alone splices a separate conversation into the parent transcript | **all 67 agent rows carry this session's id** | task 12 |
| **5** | **`messages` carries a third role, `system`; the plan's model has two.** On 14 calls the *last* message — the one delta reconstruction emits as the new turn — is `system` | author confirmed independently in `corpus-gate/run-01/requests/00012.bin`: roles user, **system**, assistant, user | tasks 12, 13 |
| **5b** | **…and it collides with the fidelity marker.** `JSONL_SCHEMA_NOTE` was settled as "a `system` record at the head of each file". **If real `system` turns exist in reconstructions, the marker announcing "this is not a real record" is indistinguishable from one** | author-only finding | register §5, task 13 |
| **6** | **94 calls have an error response and no task says what the converter emits.** 92 `http_error` + 1 `client_disconnect` on `/v1/messages`. An error body is `{"type":"error",…}` — not a message | author's cross-tab: **693 stream=true ok; 92 stream=false http_error; 66 stream=false ok** | task 11 |
| **7** | **Task 19 names a command that cannot produce the number it exists to produce.** The ratio is printed inside the verify loop at `cli.py:176`, which register §2 assigns to **`verify-archive`**, not `extract` | verified by reading the register against `cli.py` | task 19 |
| **8** | **There is no `❓` column, so task 22's check cannot fail.** `❓` was always a marker inside cells. Two §5 rows defer their value to task 13 and under `IDM-008` should carry `❓`: `JSONL_SCHEMA_NOTE` and `SYNTHETIC_UUID_NAMESPACE` | verified against the register's own tables | register, task 22 |
| **9** | **The register carries no record shape and no index shape**, both of which `IDM-008` requires by name. The JSONL record shape — **this phase's entire output** — appears nowhere; nor do the index's 26 columns; nor the five `request_ref` sentinels | `IDM-008` re-read; `stats.COLUMNS` (20) + `corpus.INDEX_EXTRA_COLUMNS` (6) = the 26 every day's `manifest` reports | register §§1–8 |
| **10** | **`<seq>` is never defined** — per-session or per-day, width, timestamp or index order (the index is in **completion** order), and what it means for a session spanning days. 10 rows have an empty `session_id`, rendering `<out>/bodies//…` | accepted; dedup makes it load-bearing — 849 digest rows resolve to 737 distinct digests | register §7, task 17 |
| **11** | **`corpus-gate` is misdescribed.** No root `manifest.csv` — one per run, no header row. "Responses as **raw SSE**" is wrong for 22 of run-01's 49, which are error JSON | author confirmed: `run-01/`, `run-02/`, `run-03/` each hold their own manifest; `00006.bin` is an `overloaded_error` body | finding 4, task 15 |
| **12** | **"No LM Studio traffic exists in the captured corpus" is false in both places it is asserted** | **1 `backend=lmstudio` row** in `2026-08-21`, plus 3 calls in `corpus-gate/run-02-lmstudio/` | finding 3, "does not settle" |
| **13** | **Task 14 has nothing to run.** It is "drive it and diff it", but `--format jsonl`'s writer is **task 17, in Group D, after it**. Group C is placed first deliberately and the dependency runs the other way | verified by reading the task order | Groups C/D ordering |
| **14** | **Task 9 breaks an existing test and the plan does not mention it.** `tests/test_corpus.py:453` shells out to `python -m ilirium_llm_router --extract <day>` | accepted on the reviewer's citation | task 9 |
| **15** | **`notes.md` said Group A had not started** while `plan.md` recorded three of its tasks done; and "Three commits" sat above a list of four | **fixed in this file, above**, at the two cited places | — |
| **16** | **The register's SSE event list is incomplete — `event: ping` is absent** | author-only; observed in `corpus-gate/run-01/responses/00012.bin` | register §5, task 11 |
| **17** | **Retries produce byte-identical consecutive requests** and delta reconstruction has no defined behaviour for a zero delta | author-only; `00003.bin`≡`00004.bin`, `00006.bin`≡`00008.bin` | task 12 |

### Refused, downgraded, or already true

**Recorded with reasons, per `IDM-004` — a refused finding with no reason is re-raised by the next review.**

- **The `agent_id` causation.** Refuted above. **The finding's *conclusion* is accepted and its
  *mechanism* is not**, and register §8's "0 of 770" needs replacing with a real number rather than
  merely being corrected.
- **`.sse`/`.json` extension rule.** The reviewer checked every stored response in all four folders
  and found **zero mismatches** — the rule is sound. Downgraded to finding 10's edge case: 10 rows with
  empty `stream` and zero-byte bodies. *Kept because the reviewer also noticed `observe.py` decides by
  **content-type**, not by the request's `stream` flag, and the design deliberately allows them to
  disagree.*
- **The four superseded spellings** — `--to-jsonl`, `--verify-only`, `--day`-as-option,
  `corpus-<day>`, the two-modules proposal, finding 2's old heading. The reviewer checked each against
  the charter's test ("still presented as current") and **filed none.** The false-positive list did its
  job; this is what naming them in advance buys.
- **`link-check.py` at 87 broken / 97 files**, not 86/96. **Not a regression — the delta is entirely
  `review-charter.md` itself** and its own forward citation. The baseline is confirmed rather than
  moved.
- **`Bash(uvx ruff *)`** remains a raised concern with no home. Not a plan defect; still nobody's.

### Questions this review hands to the owner

**None of these is a defect, and none can be settled by reading. They block the plan revision.**

1. **The probe-class calls — emit, drop, or refuse the session?** Dropping them makes the transcript
   match ground truth. Emitting them is the more honest record of *what crossed the wire*, which is
   this milestone's stated subject. **They cannot both be right**, and the choice decides whether task
   14's *"anything else in the diff is a converter defect"* survives as written or becomes a growing
   list of expected differences.
2. **A session whose request bodies stop being captured** — refuse it, emit up to the gap with the gap
   named in-band, or emit assistant-only turns? Not recoverable by any tool: the bytes were never
   written.
3. **Where does the viewer's record schema come from?** It is not published. Two sources: the viewer's
   Rust source, or a real `~/.claude/projects/*.jsonl`. **The plan forbids the second as *input* —
   "oracle, never input" — but task 13 is schema discovery, not conversion, and the plan does not draw
   that distinction.**
4. **Is `PROJECT_NAME_DEFAULT = corpus` compatible with the viewer?** Every real project folder is
   path-mangled. The plan asserts a plain name works, with no evidence.
5. **Matching semantics for `--path`, `--session`, `--model`** — exact or prefix, and how repeated
   filters of different kinds combine. `--path /v1/messages` under prefix matching now sweeps in 65
   `count_tokens` rows.

### What this says about `IDM-004` itself

**Its predicted split did not hold, and that is evidence rather than noise.** `IDM-004` says the
author finds defects about *the record* and the cold reader finds what the author *could not un-know*.
Here the **cold reader found the record defects too** — the missing `❓` column, and this file
contradicting `plan.md` about Group A. The author's three unique findings were all **data** findings:
`ping`, retries, and the `system`-record collision.

**`IDM-004` says its numbers are n=1 and not a rule.** This is n=2, and n=2 disagrees with n=1 about
where the value comes from. *The overlap figure is not evidence either way, for the reason declared
above.*

### ~~One side effect~~ — **retracted 2026-08-26. This section was wrong, and it was the author's error, not the reviewer's**

**This read: *"The cold run created a `.venv` in this worktree"*, and built a governance lesson on it —
that a constraint the parent honours does not reach a delegate unless the prompt carries it, therefore
the charter template needs an environment clause.**

**The owner created the `.venv`.** Told plainly when asked. **There was no side effect, no delegate
exceeded its brief, and the lesson has no evidence under it.** It is struck rather than deleted,
because a retracted claim that vanishes cannot show that the mechanism caught it.

**How it happened is the part worth keeping.** The author observed a `.venv` that had not been there
an hour earlier, knew a delegate had just run and had needed `zstandard`, and **inferred a cause that
fit perfectly**. It was never checked against the one person who could confirm it. *That is the same
shape as the reviewer's `agent_id` error two sections above — a plausible reading, a true one, and one
question between them — except this time it is the author's, in the document that records the
reviewer's.*

**The charter's environment clause is not adopted**, having been argued from a fiction. If a future
delegate does exceed its brief, that will be the evidence, and this paragraph is the reason to wait
for it.
