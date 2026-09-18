# For the owner — Phase 14

*`IDM-010`. Written during the phase, to a person. Numbered in order of appearance and never
renumbered. Anything needing a decision was asked out loud instead of being parked here.*

---

## 1 · ERRAND · high · Only you can run the measurement

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
