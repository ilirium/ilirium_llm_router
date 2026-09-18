# The next session's prompt

*The one file in `docs/` allowed to go stale, per `README.md` — which is why it is rewritten at each
handoff rather than left. **Replaced 2026-09-18**, mid-phase rather than at a merge. Whatever comes
next replaces it again.*

---

**Phase 14 is OPEN and IN FLIGHT. Nothing is merged.** Work in
`/Users/ilirium/Projects/local/ilirium_llm_router/phase-14-rate-limit-headers` — *that worktree, not
`main`. A session started in `main` sees none of this.* Branch
`feat/phase-14-rate-limit-headers`, forked from `main` at `ac2976e`.

**This is different from the last five handoffs**, which all closed a merged phase. **You are
picking up an unfinished one**, and the first thing to know is that **the phase's chartered work is
not what most of it turned out to be.**

## Read these, in this order

1. **`docs/status.md`** — first, every session. The only file that holds state.
2. **`docs/milestone-2-corpus/phase-14-rate-limit-headers/for-the-owner.md`** — **nine entries, and
   four of them are things you would otherwise rediscover the hard way.** Read it before `plan.md`.
3. **`.../phase-14-rate-limit-headers/notes.md`** — long, and written while the work ran. **Read it
   by section**, per `CLAUDE.md`.
4. **`.../phase-14-rate-limit-headers/plan.md`** — its register is where every name and number is.

## What the phase is, and what it became

**Chartered:** record `retry-after` and the `anthropic-ratelimit-*` family — `BKL-0034`.

**Reshaped by the owner on the day it opened**, around a live symptom: **Claude Code's auto mode
cannot run its safety classifier through the router.** The classifier's request omits `stream`, so
it goes upstream non-streamed, and **every non-streamed `/v1/messages` comes back `429`.**

**The instrument was built, it works, and it is the phase's real deliverable.** An allowlist of
response headers logged at `WARNING` on a failure and sampled once at `INFO` on a success; **28
names**, plus a prefix catch that reports an unknown `anthropic-ratelimit-*` header **by name and
never by value**.

## What is established, and it is a lot

| | |
|---|---|
| **The rejection is Anthropic's own** | Every one carries a distinct `request_id` |
| **A `429` carries no metering at all** | No `retry-after`, no bucket, not even an unlisted one |
| **A `200` on the same connection carries twelve** | `unified-status=allowed`, `5h` at **0.52**, `7d` at **0.59** — *so it is not quota* |
| **The classifier works DIRECT and fails ROUTED** | Same credential, machine, client version, afternoon |
| **The router alters no header** | Computed from a capture: nothing dropped, nothing added |
| **The two TLS fingerprints differ trivially** | And a **Chrome** fingerprint is rejected exactly as Python's is |

***Eleven hypotheses are eliminated by measurement*** — `accept-encoding`, HTTP/2, a dropped header,
an added header, the `anthropic-beta` list, the withheld attribution headers, quota, request size,
the model, the router inventing it, and a non-browser TLS fingerprint.

***The cause is NOT identified.*** **Say so.** *What is left is an exact-fingerprint allowlist that
only Bun's own build could match, and connection reuse, which nothing has touched.*

## Five things you will get wrong here

- ***Three experiments are live in `src/` and the owner chose to keep them.*** **Do not revert them
  without asking** — he wants to keep experimenting on this branch. **One has a standing cost: the
  corpus now stores non-streamed response bodies brotli-compressed**, so `extract` hands a reader
  bytes where it used to hand them JSON.
- ***`make run` now starts with the corpus OFF.*** `config.yaml` was restored to the shipped default
  so `test_template_matches_the_repository_config` would stop being red. **`make run-boringssl` with
  `config-boringssl.yaml` is the one that captures**, and it needs `make forwarder` running first.
- ***An instrument that passes its tests can still be pointed at the wrong thing.*** **Three times
  in this phase**, and none was caught by a test while twenty-four mutations passed: an allowlist
  built from documentation that matched nothing on this credential; a sample latch spent on
  `/api/hello` printing `(none)`, *the same string a rejection prints*; and a header that four tests
  asserted the content of and none validated as legal HTTP. **Read a new line against a measurement
  you already have.**
- **`branch-index.py --write` deletes the `temp/to-run-server` row**, on this branch and on a clean
  `main` alike, and `--check` says only `STALE`. **`IDM-001` says that row must not be removed, and
  puts `--write` as the last step of every merge** — so the next merge deletes it silently.
  **`main` is STALE right now for this reason alone.** → `for-the-owner.md` entry 4.
- **`link-check.py`'s count is a property of the worktree.** **92 on `main`, 112 here.** Compare
  within one tree or not at all.

## Open, and the owner's to choose between

- **Group D has never started** — where the headers durably live. ***It is still the milestone
  plan's "Phase 14's plan cannot skip the question"***, deferred on the owner's decision with the
  values now in hand. Three candidates: a sidecar telemetry file, the corpus day index, or
  overturning the `calls.csv` non-goal — **and only the owner can overturn that.**
- **The upstream report is not sent.** `BUG-001` now holds what both issues stall on and **neither
  has been told any of it.** `status.md`'s item 2, unchanged since 2026-08-25.
- **The Bun exact-fingerprint test**, if it is wanted: a runtime to install, a second forwarder, and
  a maybe — Bun's `fetch` need not fingerprint like the compiled Claude Code binary.
- **`BUG-001` is retracted and corrected on this branch, not on the trunk.** It reaches `main` only
  at the merge.
- **Everything `prompt.md` listed on 2026-09-17 is still open**: the corpus tools undriven by hand,
  `BUG-001` unreported, `BKL-0017`, `EPD-001` and `EPD-002`, `BKL-0007`, and `git fetch origin`.

## What is finished, so nothing is half-done

**Groups A, B and C are complete. Group C2 — the eleven eliminated hypotheses — was not planned and
is written into `plan.md` after the fact.** **Every check on the branch is green**: 475 tests, 24
mutations, `make lint` at the pinned `0.16.1`, `backlog-index --check`.

**The working tree is clean and every finding is committed** across 21 commits. **Nothing is
half-written**: each experiment is recorded with its result, its cost, and whether it was verified
to have actually run.

*Push state was deliberately not checked at this handoff, on the owner's instruction.*

## The working agreement still applies

`CLAUDE.md`, in full. Three earned their place again in Phase 14:

**Exercise it before committing** — and the sharper version this phase paid for three times: *a
green check tells you the instrument works, never that it is aimed correctly.*

**Ask before inferring.** The owner is present. **The control that overturned this phase's headline
finding came from him asking a question**, not from another experiment. → the memory note
`ask-rather-than-infer-about-the-setup`.

**Raise it rather than burying it.** *"Anthropic sent this rejection"* was read as *"Anthropic is at
fault"*, and `BUG-001` had been making a worse version of the same mistake since 2026-08-25.
