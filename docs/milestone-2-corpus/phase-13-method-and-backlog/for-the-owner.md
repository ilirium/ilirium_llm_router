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

**It was 338 lines when this branch opened and is 359 now**, with the `IDM-009`, `IDM-010` and
`IDM-011` pointers added. Every one is a pointer rather than a restatement, which is the cheap form.

**Nothing here argues for cutting it.** The item's own framing is that the fix is a *measurement*,
not a cut, and two of the restatements already have arguments on the record.

***Amended 2026-09-17, and the amendment is the point.*** *When written, this entry told you the
number in `BKL-0005` was stale and that this phase was one of the reasons. **Task 15 then corrected
that item to 359** — so the entry outlived its own complaint, while carrying "345 now", which was
itself already wrong. **An entry written to report a stale number went stale about it.** Amended in
place rather than removed: `IDM-010` only forbids rewriting one at the close, and what is worth
keeping is that the file written to a person needs re-reading like everything else.*

## 5 · IDEA · medium · Six count errors now, every one caught by opening the file

*This entry said **three** and was raised to six on 2026-09-04, by opening the files. **It went
stale about the count of things going stale**, which is either the strongest version of its own
argument or a joke at my expense; I record it as both.*

This phase got a number wrong three times in its first four commits: Phase 11's entry count (twice,
in one sentence), and a "two phase plans" figure relayed from a document written a week earlier.

**Three more since.** *(4)* `prompt.md:58` said this file has **five entries** while citing entry 7
eleven lines later — written in the same commit that added entries 6 and 7. *(5)* `prompt.md:112`
said **both** `REGRET` entries; there are three. *(6)* The item inventory said **36 items** and the
backlog holds **38** — the expensive one, because ids are permanent and it was two commits away from
being frozen wrong.

**None was caught by rereading the prose. All three were caught by opening the thing being
described** — and the third only because the forward review was told, in its charter, to treat every
number as unverified until the file was open.

*If a rule ever comes out of this, it is probably that one sentence: **a number in a document is
unverified until you open the thing it counts**. It is in `prompt.md` now as a session-level
warning, which is the weakest form. I am not proposing a rule; I am noting that the same defect
arrived three times in two days.*


## 6 · REGRET · low · I committed an over-width line after the check had already reported it

The width check printed `over-width: [(80, 101)]` for `prompt.md` and I ran the commit in the same
breath without reading it. Fixed in the commit after.

**Nothing was harmed** — it is one column over on one line of the file that is allowed to go stale
anyway. **What is worth telling you is the shape**: this is the third time in this phase that an
instrument produced the right answer and the failure was in reading it, after the byte-counting
`awk` and the mutation script that errored where a check should have failed.

*The rule this repository already has is `CLAUDE.md`'s — when a check comes back, fix the instrument
before believing the result. **The gap it does not cover is not believing a result you never
read.***


## 7 · IDEA · medium · The 100-column rule may not exist for prose, and I enforced it all phase

**Where it is actually written:** `pyproject.toml`'s `[tool.ruff] line-length = 100`, and `IDM-003`
saying *"the codebase is written at 100 columns"*. **Both are about `src/` and `tests/`.** I can
find no statement of a column rule for markdown anywhere in `CLAUDE.md`, `README.md` or `method/`.

**What the files actually do**, counted across the six documents this branch touched — 377 prose
lines over 100 columns, distributed **149 at 101, 107 at 102, 56 at 103**, tapering to one at 157.
*That is the signature of prose wrapped at about a hundred by eye, not of a rule enforced at exactly
100 and then drifting.*

**I have been holding my own markdown to a hard 100 for the whole phase**, at real cost: several
rewrap passes, one line committed over and fixed after, and entry 2 above — where the wrong
instrument gave you a wrong number in the course of enforcing it.

**Two readings and I cannot separate them from the text:**

- **The rule is for code only**, prose is wrapped by eye, and I invented a constraint. *Then the fix
  is a sentence somewhere saying so, and sessions stop paying for it.*
- **The rule is meant for prose too** and 377 lines are in violation. *Then it is a real
  documentation defect, and the fix is a decision about whether it is worth a sweep.*

**Not filed as a backlog item** — you asked to be asked first, and this is the asking. **The cheap
half is worth doing either way:** one sentence stating which it is would have saved this phase a
measurable amount of work.


## 8 · IDEA · high · The cold review paid for itself on its first run, and the author run had said the opposite

**You extended the checkpoint to require a fresh-context review of the inventory. It found two
missing items.** `backlog.md:716` and `:735` — real items with bodies, in *Instruments and
housekeeping*, which holds ten and was reported as eight.

**What makes this worth an entry is not the finding. It is that the author run had specifically
cleared it.** That run said *"No item was missed … the count of 36 holds"*, and it named that very
claim as **"the one an author is least entitled to be believed on"**, asking for a cold run to redo
exactly it. It was right to ask and wrong on the fact.

**The cause was mechanical, not a lapse of care.** The enumeration matched a paragraph opening with
bold or `###` at the line start. The two missed items open `~~**` — strike before bold. The two
struck entries that open `**~~` were both caught. *Two bytes in the wrong order.*

**And the author run's own arithmetic would have shown it.** Its reconciliation summed to 61
openings against a real 59, and the gap was exactly the two. Nobody added the column up — the
subtraction was done, the total was not.

*What I take from it, and it is narrower than "always run a cold review": **a pass that enumerates
by pattern should state the pattern**, because a stated pattern is falsifiable by one grep and a
described pass is not. The author run described what it had done. The cold run asked what the
description would exclude.*

## 9 · IDEA · medium · Asking the two leftover questions found a third thing neither of them was about

**Both leftover inventory questions were answered on 2026-09-04** — `BKL-0007` stays `open`,
`BKL-0020` stays one id with the refusal noted in its description. **Neither is the interesting
part.**

**Writing `BKL-0007` up properly is what exposed it.** The item reasons from *"four places across
two files"* to eliminate two of its three candidate fixes, because *"only deriving the count works
across two files."* **There are two copies now, both in `status.md`.** `CLAUDE.md` dropped its copy
in this phase and "Where we stopped" dropped the other. **The constraint that disqualified the
cheapest fix has expired, and the item still argues against it.**

*I had asked the question in four words — "`BKL-0007`'s status" — and you said the questions were
unclear and to re-ask them with the detail. **Going back to write the detail is what found this.**
The compressed version would have got an answer and left the expired premise sitting there.*

**What I take from it:** a question worth asking is worth writing out, and not because the reader
needs it. *`IDM-007` says a concern raised where it will not be read has not been raised. This is
the weaker sibling — a question compressed past the point of being answerable is one the asker has
not finished thinking about either.*


## 10 · IDEA · high · Three instruments in this phase passed while testing nothing, and none was found by reading

**The register check I wrote at task 25 passed on its first run, and the pass was worthless.** Its
`❓` test skipped any table row ending `❓ |` as "the header row" — which is exactly what a row
carrying a live `❓` looks like. **It skipped the rows it exists to find.**

***That is the third instance in this phase, and the pattern is one shape.*** The heading-count
assertion in `backlog-index.py` cannot detect the failure it was built for, because its counter sits
inside the branch that succeeds. The `See` column was named by two documents and written by no code,
so nothing could fail. **All three are checks whose exclusion swallows their own subject**, and
**all three exited 0 while a person read them and saw nothing wrong.**

**The way each was found was the same: make the thing it checks go wrong, and see whether it
notices.** Not one was found by reading the code — including by me, twice, in code I had just
written.

**And the mutation harness itself failed silently.** Seven mutations "survived" the register check,
one of which deleted a whole method document. **The check was right; the harness never ran the
mutations.** This repository had already written that trap down — `notes-group-e.md` records *"the
mutation did not apply and the test did not fail are the same output at a glance"* — **and it
happened anyway, eight days later, to the person who wrote it down.**

*What I would suggest, and it is a suggestion rather than a rule: **a new check does not count as
written until one mutation has killed it**, and the harness reports "mutation applied" separately
from "check failed". Both are one extra line. The second one is what would have caught this.*

