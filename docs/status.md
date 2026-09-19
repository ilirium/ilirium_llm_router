# Status

**State, not inventory.** Unscheduled work lives in `backlog.md`; this file says where the project
is and what is in flight. Three sections, most volatile first.

---

## Where we stopped

*Changes every session. If this section passes ~30 lines, or starts carrying anything that outlives
the session that wrote it, it has become a document and gets its own file.*

**2026-09-18 — Phase 14 is open and in flight on `feat/phase-14-rate-limit-headers`.** *Not
merged. Work in `/Users/ilirium/Projects/local/ilirium_llm_router/phase-14-rate-limit-headers`.*

**It was chartered to record the Anthropic rate-limit headers and the owner reshaped it, on the day
it opened, around a live symptom: Claude Code's auto mode cannot run its safety classifier through
the router.** The instrument was built, it worked, and **fifteen hypotheses have been eliminated by
measurement.**

***2026-09-19: the 429 is gone under the hosts route and the router is cleared.*** **The same
router, `httpx` egress and TLS fingerprint carried nine classifier requests successfully that had
been rejected 119 times the day before** — so what remains is **client-side content withheld from a
custom `ANTHROPIC_BASE_URL`.** *The attribution block is the leading candidate and **is not proven
to be the cause**; the phase says which it is rather than implying otherwise.*

***Two things qualify that and neither is buried.*** **The owner's own transcript reports the
classifier unavailable in the same two minutes** the router logged six successful classifications —
unexplained, `for-the-owner.md` entry 18. **And a first-party client gzips some request bodies,
which the router cannot route**: two `400`s, *"the request body carries no 'model' field"*, because
the model peek reads compressed bytes. ***A real `src/` defect, not fixed, and the owner's to
place.***

***The 2026-09-18 evening session read the client instead of the router***, which nothing in this
phase had done. **Claude Code ships as a Bun executable with its JavaScript embedded in plaintext**,
so it is greppable — `evidence/binary-extract.sh`.

***What a next session most needs to know, in one line each:***

| | |
|---|---|
| **The instrument works** | An allowlist of response headers, logged on a failure and sampled once on a success. **28 names** and a prefix catch that reports unknown `anthropic-ratelimit-*` **by name, never by value** |
| **The finding** | A `429` carries **no metering at all**; a `200` on the same connection carries **twelve** `unified` buckets, `allowed` at 52% / 59% — *and at **0.11 / 0.01** in the later run, so quota is dead twice* |
| **The control that broke the conclusion** | **The classifier works direct and fails through the router.** The owner found it by asking why auto mode worked in the session he was reading the finding in |
| ***The attribution "header" is a body field*** | **Retracted 2026-09-18.** It is a system-prompt block inside the request, not an HTTP header — ***so `C2d` added a header the client never sends as one and tested the wrong channel entirely*** |
| **The first-party gate, and its switch** | `ANTHROPIC_BASE_URL` naming any host but `api.anthropic.com` turns off first-party behaviour; **`_CLAUDE_CODE_ASSUME_FIRST_PARTY_BASE_URL` forces it back.** *Run: it reaches the wire — `x-client-request-id` arrives — and **the 429 does not move*** |
| ***THE HOSTS EXPERIMENT RAN AND THE 429 IS GONE*** | **2026-09-19, Claude Code 2.1.267** — the client fully first-party while still routed. ***9 classifier requests, 9 × `ok`, zero 429s***, against **119 rejections** on the same build the day before. *Counts: `reference/measurements.md`; mechanism: `wiki/claude-code-first-party-gate.md`; the diagnosis: `bugs/BUG-001-non-streaming-messages-rejected-as-rate-limited.md`* |
| **Three experiments are live in `src/`** | **Deliberately not reverted** — owner's decision. *One of them makes the corpus store non-streamed bodies **brotli-compressed***. ***The imitation header can now come out on its own merits***: it imitates a header that is not one |
| **Group D never started** | Where the headers durably live — the milestone plan's *"Phase 14's plan cannot skip the question"* — **is still deferred** |

*Phase 13 merged 2026-09-17 at `97fd822`; its review stopped its own merge on five method-tier
findings, all answered by the owner and fixed before it landed.*

**Phase 13, in the one line a session still needs it:** `docs/backlog.md` and
`docs/backlog-done.md` carry **38 permanent `BKL-NNNN` ids**, one item per `### BKL-NNNN — title`
heading, and **both tables are generated — do not hand-type in them.**
`method/IDM-011-the-backlog.md` is canonical, and **a session asks the owner before filing an
item.**

*The rest of Phase 13's detail was removed from this section on 2026-09-18 — roughly seventy lines
of execution record. **Every fact in it was checked for a home before it went**: the backlog's shape
is in `IDM-011` and in `backlog.md`'s own preamble, the inventory ratification and the task-by-task
record are in `milestone-2-corpus/phase-13-method-and-backlog/`, the commit table is `git log` and
`reference/branches.md`, and `IDM-001`'s two amendments are stated in `IDM-001`. **This section is
state; that was archive**, and it was pushing thirty lines before Phase 14 added a word to it.*

**Baselines.** The trunk's test count is **448**. **On the Phase 14 branch it is 475**, with
`make lint` clean at the pinned `0.16.1`, `24/24` on that phase's mutation harness, and
`backlog-index --check` green. ***`link-check.py` is worktree-dependent and must never be compared
across trees*** — **92 on `main`, 112 in the Phase 14 worktree**, and about twenty of that gap is
untracked per-worktree files rather than content.

*Two Phase 13 paragraphs stood here until 2026-09-18 and were removed with the rest of its record:
its own `link-check` arithmetic, and a note that this section had been 154 lines. **What `--check`
does and does not see is `IDM-011`'s to say** and it says it, under "What `--check` cannot see, said
here so nobody reads its silence as coverage".*

## Where the project is

*Changes every phase.*

**One row per milestone. Per-phase detail lives in the archive** — branch, fork point and merge commit
belong to the phase note, and each milestone's own index reads its phases in order.

| | Subject | Phases | State | Read it in |
|---|---|---|---|---|
| **1** | The core router — dispatch, byte-relay, observability, failure handling | 1–7 | **complete** 2026-08-07 | `milestone-1-core/README.md`, which carries every branch and merge hash with what each phase settled |
| **2** | The corpus — capturing bodies for analysis | 8– | **open**, six phases merged — 8 through 13, the last 2026-09-17 | `milestone-2-corpus/implementation-plan.md` **until the milestone closes**; its `README.md` is a closing artefact and does not exist yet |

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
filename. **Whether archiving slows a call is untested**, and is parked as **`BKL-0017`**.

**Six phases done. The first two touched no `src/`** — Phase 8 built the method tier and the
guardrails, Phase 9 decided `EPD-003` and ran the gate that named the claim above — **and Phase 10 is
the first of this milestone that did**, merging 2026-08-21 as `32c26bb`; Phase 11 built the offline
tools over the store, merging 2026-08-28 as `7e53f74`; Phase 12 made it installable, merging
2026-09-02 as `6c75997`; **and Phase 13 touched no `src/` either**, merging 2026-09-17 as
`97fd822`.

***Fifth instance, 2026-09-17, and it is the cleanest one yet.*** *This paragraph said **five** the
moment Phase 13 landed — the phase whose own `BKL-0007` is about this sentence, whose review found
three other stale counts, and which corrected this file twice on the way. **It still went stale at
the merge**, because a merge is the one moment nobody is rereading prose. The item's argument no
longer needs a fourth example; it needs the decision.*

**And the merge that closed Phase 12 made this paragraph stale for a fourth time, within minutes of
the phase that existed to fix it.** *Written down rather than quietly corrected, because it is the
strongest evidence the `backlog.md` item has: the count went stale **because a phase landed**, which
is the one moment nobody is reading prose. A derived count would not have moved.*
*(Both sentences above were stale between Phase 10's close and the 2026-08-21 edit: they said two
phases and that Phase 10 had the opaque half still to test. **That is the paragraph below happening
again, to the paragraph that describes it** — prose that undercounts goes stale where a missing
table row would be visible. Recorded rather than quietly fixed, because it was the second instance.*
**And it happened a third time.** *This paragraph and the milestone row above both said **three**
from Phase 11's merge on 2026-08-28 until Phase 12's task 12 fixed them on 2026-09-02, while
"Where we stopped" said four on the day of that merge — so the file disagreed with itself for five
days. Three instances of one defect in one file is no longer evidence about prose; it is the
argument for the count living in exactly one place. **Filed in `backlog.md` rather than fixed
here**, because choosing that place is a change to what this file is.)*
`milestone-2-corpus/implementation-plan.md` describes all four; **their merge
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

1. **Exercise the corpus tools by hand.** ***Partly discharged 2026-09-19***, though not the way this
   item asks: `extract --format bodies` was driven over both day folders to answer the attribution
   question, and it answered it. **The history-viewer half below is untouched.** *The owner's, and the phase was shaped around it: task 14
   was struck so this would happen after the merge rather than inside it.* Nothing has driven
   `extract` against the real corpus except the author's own scripts.

   ```sh
   ilirium-llm-router extract logs/corpus/2026-*/ --out ./dump --format jsonl --format bodies
   ```

   Then point a history viewer's Custom Claude Directory at `./dump` — **never at
   `~/.claude/projects/`**, which position 12 forbids and which is not a reversible mistake. **What
   to look at first:** whether the fidelity note renders at all, whether a session's several files
   read as separate conversations, and whether the 45 gaps in the largest session look like gaps.

2. **Report `BUG-001` to the two upstream issues.** They are named in
   `bugs/BUG-001-non-streaming-messages-rejected-as-rate-limited.md`, and both stall on exactly the
   measurement it contains — a paired control showing a streamed request **2.8× larger** to the same
   model accepted **0.6 s** after a non-streamed one was rejected. **The document says this is an
   action, not a finished thing.** It is the only open item here that is not blocked on a decision.
   *(This item replaced **"settle whether a tracked permission change takes effect before it
   merges"**, answered 2026-08-25: settings are **session-cached**, inert until restart rather than
   until merge, and the worktree-resolution explanation is dead. Before that, items 1 and 2 replaced
   **"exercise the corpus by hand"** and **"plan Phase 11"**, both spent. The corpus figures that
   entry quoted — two day folders, 171 rows, **undicted** — are all superseded; see "Where we
   stopped".)*
3. **Decide `EPD-001` or `002`.** Both are blocked on a person rather than on work, and both are argued
   on a case Phase 4 measurably weakened — see `backlog.md`, "Decisions waiting on a person". Deciding
   one is cheaper than any measurement in the list, and neither decision waits on Phase 11.
   (`EPD-003` is no longer among them — decided 2026-08-17 by Phase 9.)

*The measurement items are both in `backlog.md` under "Measurements left open" — **`BKL-0012`** and
**`BKL-0017`** — and neither is listed
here as next, because a phase was in flight when this was written and this file is not the
inventory. *It named **Phase 11** as that phase until 2026-09-17 — Phase 11 merged 2026-08-28, and
the sentence survived being edited by this phase's own citation sweep, which added the two ids
without reading the clause they sit in.* Whether
Claude Code shows LM Studio's context error was already there. **Whether archiving slows a call was
added there on 2026-08-21** — until then it lived only in `prompt.md`, which is the one file allowed
to go stale, and in `milestone-2-corpus/implementation-plan.md`'s table. *(This sentence gave as its
reason that "the owner has not chosen Phase 11's subject" until 2026-08-25, which stopped being true
on 2026-08-24 — the conclusion held, the reason for it did not.)**

## What is on disk and not in git

*Harvested from `prompt.md` on 2026-08-21, which was the only place it was written down and which
expires by design. **Re-verified by looking on 2026-08-25**, not relayed — and it had gone stale in
three ways, which is what this section warns about happening to itself. This is working-copy state.
Re-check before trusting a line of it.*

**`logs/` is gitignored whole (`.gitignore:228`), so none of this can be committed by accident.**
**And it is now per-worktree** — the layout below differs in each, and **`git worktree list` is the
count** rather than a number written here. That is new since this section was written. *This
sentence said "there are three checkouts" until 2026-09-02, when it was two: the phase-11 worktree
had been removed and nothing that said three was re-run. It is three again today, for a different
reason, which is exactly why the number does not belong in prose.*

**`to-run-server/logs/` — the live one, 153 MB** *(re-measured 2026-09-02; it read 93 MB, taken
2026-08-25)*

| Path | What it is |
|---|---|
| `logs/corpus/2026-08-21/`, `2026-08-24/`, `2026-08-25/` | **Three** day folders. Every document that says "two" was written on 2026-08-24 and has not been re-counted |
| `logs/corpus/dicts/req-2026-08-25T103250Z-9dd33823.dict` | **The corpus is no longer undicted.** Installed 2026-08-25T10:32:50Z, 262,144 bytes. All 320 rows in that day's index reference it |
| `logs/corpus/retrain.log` | Three verdicts: `no-complete-day`, then `too-few-samples`, then **`installed`** |
| `logs/telemetry/calls.csv`, `router.log` | **Exists.** This section said *"does not exist yet"* until 2026-08-25; the router created it on 2026-08-21 |

**`main/logs/` — historical, 260 KB of corpus plus Phase 9's**

| Path | What it is |
|---|---|
| `logs/corpus/dicts/req-2026-08-20T110338Z-0e4d84d1.dict` | **The first real dictionary**, 262,144 bytes exactly. **Do not delete it.** `reference/measurements.md` cites the `0e4d84d1` ID as evidence that the same parameters reproduce the same dictionary byte for byte |
| `logs/corpus-gate/` | Phase 9's corpus, **8.8 MB** — re-measured 2026-08-25, unchanged. `measurements.md` names it as the slice behind four rows. It stays |
| `logs/calls.csv`, `logs/router.log` | The router's history to 2026-08-20. **Deliberately left** where they are when the config moved to `logs/telemetry/` — owner's decision, in `milestone-2-corpus/phase-10-body-store/plan.md`'s settled table |

**Worktrees that have been removed are not described here.** `phase-11-corpus-tools/` and
`…/opening-playbook-not-run-table` are both gone; `git worktree list` is the answer to what exists,
and today it is `main`, `to-run-server` and `phase-13-method-and-backlog`. *The findings those trees
carried are kept in their branches' records — the tree was only ever the instrument.*

**`phase-13-method-and-backlog/` is a merged phase's tree and is kept, not removed.** *Its branch is
merged into `main` at `97fd822` and **the branch itself must not be deleted** — `branch-index.py`
refuses to render when a description names a branch that no longer exists. **Removing the working
tree is safe and removing the branch is not**; the two are separate acts and only the second breaks
the next merge.*

**`make test`, `make lint` and `make check` all ran there and none of them created `logs/`** — which
is `cli.py`'s documented promise that `--check` configures no logging, demonstrated rather than
asserted. That worktree's config also reported `Corpus: off`, so nothing done in it could reach the
corpus. Its `.venv/` was created **by the owner**, which is why `uv run python` worked there. *(This
file briefly recorded that a review subagent created it. It did not; that claim is retracted in
`milestone-2-corpus/phase-11-corpus-tools/notes.md`.)*

**A fresh worktree starts with neither.** So `uv run python` does **not** work in a new tree until a
venv is made there, and anything importing `zstandard` needs one. *Confirmed again 2026-09-04 in
`phase-13-method-and-backlog/`, which has neither. This sentence named
`…/opening-playbook-not-run-table` as the live example until that worktree was removed — **a fresh
example goes stale exactly as fast as the last one**, which is why the rule is stated and the tree
is only cited as evidence for it.*

**One warning was dropped rather than carried across, and it stays dropped.** `prompt.md` said
*"stage with explicit paths, never `git add -A`."* The stated reason was that `logs/` holds
uncommittable things — and `logs/` is gitignored, so `git add -A` cannot stage any of it. **The advice
survives on other grounds** — there is now a deny rule that fires — **but the reason originally given
was not a real hazard**, and repeating it would preserve a rule whose justification does not hold.

## In-flight branches

*Merged branches are not listed here — this section holds live state. **They are indexed in
`reference/branches.md`, generated from git**, which is the 2026-08-21 amendment to
`method/IDM-001-git-branching.md`: a hand-maintained list would drift and a derived one cannot. The
permanent record of a phase's branch, fork point and merge commit is still its phase note.*

**`feat/phase-14-rate-limit-headers`** — Phase 14, forked from `main` at `ac2976e` on 2026-09-18,
**not merged.** *A commit count stood here and was **eight out** within a day of being written — it said 21 while the branch held 29. **`git rev-list --count main..HEAD` is the answer**, and it is not written down here for the reason `BKL-0007` exists.* The Anthropic rate-limit response headers, **reshaped around
`BUG-001`'s live symptom**: Claude Code's auto mode cannot run its safety classifier through the
router, because the classifier's request is non-streamed and comes back `429`.

***Groups A, B, C and C3 are done. Group C2 — thirteen eliminated hypotheses — was not planned and
happened anyway. Group D has not started.*** *Where the headers durably live is still the milestone
plan's "cannot skip the question", still deferred, and still the owner's.*

***C3 answered the phase's question on 2026-09-19.*** **Under the hosts route the classifier
succeeds through the router** — 9 of 9 — **and the paired control clears the router entirely.**
*Entry 8's two remaining hypotheses, the TLS fingerprint and connection reuse, are eliminated as a
side effect: **Anthropic saw the router's own fingerprint on both days.***

**Every check on that branch is green** — 475 tests, 24 mutations, `make lint`, `backlog-index
--check`. **`BUG-001` is retracted and corrected there**, not on the trunk: its table cleared the
router with an argument that compares streamed against non-streamed *inside* the router.

***Three experiments are live in `src/` and are deliberately not reverted*** — owner's decision,
2026-09-18, to keep experimenting on the branch. **The `accept-encoding` one has a standing cost:
the corpus stores non-streamed response bodies brotli-compressed.**

*Phase 13 was entered here at task 1 and removed at its merge on
2026-09-17; its row is in `reference/branches.md` and its permanent record is its phase note.*

***Closing this section is not one of `IDM-001`'s three merge steps, and it should be.*** *`dec7c4a`
— the commit this phase forked from — exists because this section still opened with a branch it then
said had merged. **Phase 13 reached its own merge with the same two sentences still live**, and
caught them only because a session went looking. A third instance would be the argument for a
check.*

**Merged branches are kept, not deleted, and the tooling enforces it.** `branch-index.py` refuses to
render when a description names a branch that no longer exists, so deleting one breaks the next
merge's regeneration. Found on 2026-08-25 by deleting `docs/bugs-tier` and restoring it.

**Push state cannot be checked from here.** `origin` is configured, but this clone holds **no
remote-tracking refs at all** — `git branch -r` is empty — so no local command can tell whether
anything has been pushed without a fetch. *The last word is the owner's, and `status.md` has always
recorded that as reported rather than checked. What was established 2026-09-04 is that it is
**unverifiable locally**, not merely unverified — so a session must ask rather than look.*

**Reported pushed, 2026-09-17, by the owner.** *That covers the work up to the moment it was said,
and nothing since. It is not a claim this clone can re-derive on any later day, so a session that
needs to know asks again rather than reading this line.*

*Trimmed twice for the same reason, and the second time is the interesting one. On 2026-08-25 four
paragraphs of commentary on **merged** branches were cut, because this section's opening rule says
merged branches are not listed and it had accumulated 22 lines of them. **By 2026-09-04 it had
re-accumulated four more** — Phase 12, `fix-slop-docs/opening-playbook-not-run-table`, Phase 11 and
`docs/bugs-tier` — each a paragraph explaining that the branch is merged and therefore not listed
here. **Each of the four was verified to have a row in `reference/branches.md` before it was cut.**
The rule did not fail; what fails is closing a branch out by writing a sentence here instead of
deleting one, and the second instance is the argument for that being the thing to notice.*
