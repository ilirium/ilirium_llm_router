# Phase 13 — for the owner

**Read this after the phase is finished.** It is the one document in this folder written *to a
person* rather than to a session. **Nothing here blocks the build** — anything that did was asked in
the session instead, which is `../../method/IDM-010-writing-for-the-owner.md`'s rule and this phase
wrote it.

**Four kinds:** `ASK` needs an answer only you can give and was already raised aloud; `IDEA` is a
suggestion you can ignore; `REGRET` is something I would do differently and am telling you rather
than quietly fixing; **`ERRAND` is an action only a person at a keyboard can perform.**

*Written during the phase, in order of appearance. Numbers are not a ranking — the importance mark
is.*

---

## 1 · ERRAND · medium · Run `git fetch origin` once, so push state becomes checkable

**`origin` is configured and this clone holds no remote-tracking refs at all** — `git branch -r` is
empty. So no local command can tell whether anything has been pushed, and `status.md` now records
that push state is **unverifiable locally** rather than merely unverified.

**One `git fetch origin` would create the refs** and make `git log origin/main..HEAD` meaningful for
every future session. I did not run it: it is a network action against your remote and nothing in
this phase needed it.

*Until then, a session has to ask you, and `status.md` says so.*

## 2 · REGRET · medium · I measured column width with `awk`, which counts bytes

I reported **19** over-width lines in `status.md` and later **15**. The second number is right. The
first came from an `awk` check counting **bytes**, and this repository had already recorded that
exact trap — *"`awk` counts bytes and reported 13 where there were 4"*, in Phase 11's own baseline
note.

**The finding survived the bad instrument** — none of the lines is this branch's either way — but
you were given a wrong number first, and the correction cost a round trip. **Everything since is
measured in Python, in characters.**

*The rule I should have applied is one this repository already holds: when a check comes back, fix
the instrument before believing the result.*

## 3 · REGRET · low · I proposed a closing trim for this file, and it did not survive one question

I recommended that `for-the-owner.md` be written during a phase and **trimmed at its close**, and
you selected it. You then asked what trimming meant, and the answer collapsed on contact: **a
per-phase file cannot accumulate, so there is nothing to trim** — and the archive rule forbids
editing an entry out afterwards in any case.

**The cost landed on you**, because it was presented as a recommendation with a rationale rather
than as the half-formed idea it was. *A design that does not survive its first question should not
have been the recommended option.*

## 4 · IDEA · medium · `CLAUDE.md` grew again, and its backlog item's number is stale

The backlog carries an item recording that `CLAUDE.md` is long — **297 lines** when it was written,
and that you accepted the growth deliberately *"so a later review can act on it"*.

**It was 338 lines when this branch opened and is 345 now**, with `IDM-009` and `IDM-010` pointers
added and `IDM-011`'s still to come. Every one is a pointer rather than a restatement, which is the
cheap form — but the file is now ~48 lines past the figure the item records.

**Nothing here argues for cutting it.** The item's own framing is that the fix is a *measurement*,
not a cut, and two of the restatements already have arguments on the record. **What I am telling you
is that the number in that item is stale and this phase is one of the reasons.**

## 5 · IDEA · low · Three count errors in four commits, every one caught by opening the file

This phase got a number wrong three times in its first four commits: Phase 11's entry count (twice,
in one sentence), and a "two phase plans" figure relayed from a document written a week earlier.

**None was caught by rereading the prose. All three were caught by opening the thing being
described** — and the third only because the forward review was told, in its charter, to treat every
number as unverified until the file was open.

*If a rule ever comes out of this, it is probably that one sentence: **a number in a document is
unverified until you open the thing it counts**. It is in `prompt.md` now as a session-level
warning, which is the weakest form. I am not proposing a rule; I am noting that the same defect
arrived three times in two days.*
