# For the owner — Phase 14

*`IDM-010`. Written during the phase, to a person. Numbered in order of appearance and never
renumbered. Anything needing a decision was asked out loud instead of being parked here.*

---

## 1 · ERRAND · ~~high~~ · Only you can run the measurement — ***DISCHARGED 2026-09-18***

> **Run five times that day, Claude Code 2.1.267.** It produced the measurement, and then four more
> experiments on top of it. *The text below is left exactly as written, because what it predicted —
> that only a person at a keyboard could take this — held for every one of the five.*


**Group C needs a real Claude Code session, through the router, with auto mode on.** A session
cannot do it: it needs your credential and your machine, and `CLAUDE.md` says driving a session is
never done freely.

**What it is for:** the 429's response headers have never been seen. They are the one thing that
separates *Anthropic restricts this request shape on a subscription credential* from *the router
provokes it* — and `BUG-001` has rested on timing and inference for three weeks for exactly the want
of them.

**What to do, once Group B is in:**

1. `make run` in `to-run-server/`, with the router built from this branch.
2. A Claude Code session pointed at it, auto mode **on**, and something that shells out — `printenv`
   was enough on 2026-08-25, and it failed within ninety seconds.
3. `claude --version` recorded. **`BUG-001` asks for it by name**: if the fix turns out to be
   client-side, the version is the only thing that will identify it.
4. Then stop, and hand back — Task 8 reads `router.log` and freezes the result.

**If it does not reproduce, that is a result and not a wasted session.** Say so rather than
retrying; an absence of 429s is `BUG-000`'s trap and a quiet session looks exactly like a fix.

## 2 · ASK · medium · The durable home is deferred, not answered

**You deferred it on 2026-09-18 and that was the right call** — the minimal form needs no schema, so
the question can be answered with the values in hand instead of guessed at beforehand.

**It comes back at Group D, and it is still the milestone plan's "Phase 14's plan cannot skip the
question".** Three candidates, unchanged: a sidecar telemetry file, the corpus day index, or
overturning the `calls.csv` non-goal. **Only you can overturn that non-goal**; it is
`implementation-plan.md`'s and this phase has no authority over it.

*Recorded here so the deferral cannot be mistaken later for the question having been settled.*

## 3 · IDEA · low · Keeping what the corpus already holds

**The diagnosis in the plan's evidence section cost nothing to produce** — every fact came from
`calls.csv` and corpus blobs already on disk in `to-run-server/`, three weeks after the traffic that
made them. The classifier's request body, the quota probe, the exact 429 text and its `request_id`
were all simply there.

**That is the corpus doing the job it was built for, on a question nobody had when it was built.**
Worth knowing when `BKL-0017` asks whether archiving is worth what it costs — this is the other side
of that ledger, and it is not written down anywhere else.

## 4 · ASK · high · `branch-index.py --write` now deletes a row it must not delete

**Found while checking this phase's own branch description. It is not this phase's doing** — it
reproduces on a clean `main` with nothing of this branch in the tree.

**What happens:** `temp/to-run-server` has been fast-forwarded to `main`'s exact tip. `resolve()`
treats a branch whose tip is on the trunk **with nothing between it and the trunk head** as *in
flight* — correct for a branch just cut and not yet committed to, and wrong for this one. It
therefore leaves `merged_rows`, and **`--write` silently drops its row from `reference/branches.md`.**

**Why it matters more than one row.** `IDM-001` says of exactly this row: ***"The row exists; do not
remove it as noise."*** It is the only place that records that `temp/to-run-server` is not work —
and that the telemetry and corpus `BUG-001` and Phase 11 both rest on were captured through it.
**And `IDM-001` puts `--write` as the last step of every merge**, so the next merge deletes it
without anyone looking.

***`--check` does not warn.*** It prints `STALE: branches.md does not match git. Re-run with
--write.` — the same thing it prints for an ordinary missing row. **A green `--write` followed by a
commit is what this looks like from the outside.**

**Not fixed here, and not worked around.** The fix is a judgement about what the script should treat
as in flight, and it belongs on its own branch rather than inside a phase about response headers.
**`main` is STALE right now** for this reason alone.

*Asked out loud on 2026-09-18. Recorded here because it survives the session.*

## 5 · REGRET · high · I read "Anthropic sent this" as "Anthropic is at fault"

**The headers were real and the inference was not.** A `429` carrying no metering, on a connection
whose successes carry twelve buckets, is a fact. *"Therefore it is Anthropic's fault"* is a
different claim, and **the one experiment separating them — direct against routed — had never been
run.** You ran it by asking why auto mode worked in the session you were reading the finding in.

**`BUG-001` had been making the same mistake since 2026-08-25**, with a worse version of it: its
table clears the router by comparing streamed against non-streamed *inside* the router, which
cannot see a router-caused defect specific to non-streamed requests. **Struck on this branch.**

*Recorded because the phase's instruments all worked and the reasoning on top of them did not.*

## 6 · REGRET · medium · Three instruments, three near-misses, one pattern

| | What it would have said |
|---|---|
| The allowlist, built from Anthropic's documentation | *"a 200 carries no rate-limit headers either"* — **none of the documented names arrives on your credential** |
| The sample latch, spent on `/api/hello` | `(none)` — **the same string a rejection prints** |
| The imitated billing header, ending `"; "` | Four tests asserted its content; **none validated it as HTTP**, and it broke as a 502 in your face |

***Each tested the thing it was pointed at. None tested whether it was pointed at the right
thing.*** *All three were caught by reading a line against a measurement taken minutes earlier, and
none by a test — while twenty-four mutations pass.*

## 7 · ERRAND · high · Three experiments are live in the router and one has a cost

**You asked for them to stay, and they have stayed.** So that the next session does not have to
rediscover it:

| In the tree | |
|---|---|
| `accept-encoding` relayed for non-streamed | ***The corpus now stores those bodies compressed.*** A stored non-streamed response blob is **brotli, not JSON**, and `extract` will hand a reader bytes |
| `http2=True` and the `h2` dependency | Harmless, buys nothing measured |
| The imitation headers | Fabricated attribution on every Anthropic call |

**All three are exonerated. None is reverted. That is your decision and it is recorded as yours.**

## 8 · IDEA · medium · The two things left, and neither is cheap

**The exact-fingerprint allowlist.** `curl_cffi` is Chrome, not Claude Code — it carries three
extensions a bare BoringSSL build does not. **Only Bun's own build could match, and even that is a
maybe**: Bun's `fetch` need not fingerprint like the compiled binary.

**Connection reuse**, which nothing here has touched. *Claude Code direct may put the classifier on
an HTTP/2 connection that already carried a conversation; the router and the forwarder each pool
their own.* **Untested, and named because it is untested.**

## 9 · ERRAND · medium · The upstream report is written but not sent

**`BUG-001` now holds the measurements both issues stall on** — the paired control, the meter
reading `allowed` at 52%, request ids, and the proof that the router alters no header. **Nobody has
told either issue any of it.** *It was `status.md`'s item 2 before this phase and it still is.*
