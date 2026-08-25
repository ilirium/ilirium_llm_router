# BUG-000 — What a bug document is, and the index of them

**BUG stands for what it looks like.** No expansion is needed and inventing one would be worse.

A bug document records **a defect this project cannot fix from here** — in software it dispatches to,
or is built on — written down with the evidence that establishes it and the check that would show it
gone.

## Why the tier exists, stated before anything else

**A defect we own is closed by a commit. A defect we do not own has no such ending.** It survives
sessions, outlives phases, gets rediscovered from scratch by whoever hits it next, and — worst — gets
*assumed fixed* because nobody saw it lately. Nothing in `docs/` was shaped to hold that: `../backlog.md`
holds work we might schedule, `../epd/` holds questions we have not answered, `../wiki/` holds how
somebody else's software **works**.

This tier holds how somebody else's software is **broken**, which is a different thing with a
different lifetime.

## What belongs here, and what does not

**The admission test: is the behaviour wrong rather than merely surprising, and is it outside our
power to fix?** Both halves are load-bearing.

- **Wrong rather than surprising.** A dependency that is awkward, undocumented or counter-intuitive is
  a `../wiki/` page. A dependency that does something it says it does not do, or refuses something it
  says it accepts, is a bug.
- **Outside our power to fix.** Our own defects end in a `fix/` branch and the phase note that records
  them; they need no durable home because the commit *is* the ending. A document here exists precisely
  because no commit of ours can close it.

Where the neighbouring tiers draw the line:

| | |
|---|---|
| `../wiki/` | how somebody else's software **works** — durable, and useful to any project using it |
| `bugs/` | how it is **broken** — perishable, status-bearing, expected to become obsolete |
| `../reference/` | what is true about this router |
| `../backlog.md` | unscheduled work **we** could do |
| `../epd/` | a design question we have not decided |
| `../method/` | how the work is done |

**The `wiki/` boundary is the one that will be got wrong**, because a defect is genuinely a fact about
somebody else's software and `wiki/`'s own test — *would this page be just as useful to a different
project using the same library?* — says yes for most bugs. The tiebreak is **lifetime**: a `wiki/` page
is written to stay true, and a bug document is written hoping to stop being true. Filing a bug as a
wiki page produces a page that quietly becomes a lie the day it is fixed.

## An absence is not a fix

**The rule this tier was founded on, and it is not a formality.** Not observing a defect is not
evidence that it is gone; it is evidence that you did not observe it. A quiet afternoon, a shorter
session, a lighter account — all of them look exactly like a fix.

**So every bug document names, before it is filed, the positive check that would show it fixed.**
Without that line the document has no ending condition and the question *"is this still a thing?"*
degrades into folklore within two milestones.

This mirrors `../method/IDM-005-opening-a-milestone.md`'s first step, which requires naming what would
refute a claim at the moment the claim is made, for the same reason: the check is easy to specify
while the evidence is in front of you and nearly impossible to reconstruct later.

## Numbering

`BUG-NNN-kebab-slug.md`, allocated **in order written**, never reused and never renumbered. `BUG-000`
is this index. Numbers imply neither severity nor priority — **severity is not encoded in the
number**, because a number that means something has to be maintained when the meaning changes.

**The number is what is cited; the slug is for grepping and may drift.** Write a rename with `→`,
which `../procedures/link-check.py` depends on.

This mirrors `../epd/EPD-000-about-these-documents.md` and `../method/IDM-000-about-these-documents.md`
deliberately. Three adjacent numbered schemes is a hazard those two already named, so the difference
has to be stated loudly rather than inferred:

| | Asks or answers | What to do with it |
|---|---|---|
| `EPD-NNN` | asks a design question, and may pick nothing | do not build from it unless it names an acceptance date |
| `IDM-NNN` | answers a process question | follow it; if it is wrong, change it here first |
| `BUG-NNN` | reports a defect we cannot fix | **work around it, and re-run its check before assuming it is gone** |

## Status

Every bug document opens with a status line: the status, and **the date it was last confirmed** — not
the date it was written. Those diverge immediately, and the second is the one a reader needs.

| Status | Meaning |
|---|---|
| **open** | Reproduced here and not fixed. The date says when that was last true |
| **fixed** | The document's own check was run and passed. Records the date, the version, and the measurement — never "seems fine now" |
| **not a defect** | Investigated and found to be correct behaviour, or ours after all. Kept, with what it actually turned out to be |
| **superseded by BUG-NNN** | The same defect, better characterised elsewhere |

**A fixed or withdrawn document is never deleted.** `EPD-000` established this for proposals and
`../README.md` states the general form. Here it earns its place twice over: a defect that returns is
common, and the document that already characterised it is worth more than the one somebody would write
from scratch.

## Evidence

**Evidence is cited to something committed**, per `../README.md`'s "Evidence and redaction". Frozen
artefacts live in `evidence/` beside these documents, with `evidence/README.md` saying what produced
each one, what it proves, what was redacted and how, and whether it can be regenerated.

**Redaction is not optional and not partial.** Stable placeholders in first-appearance order, every
identifier family treated consistently, and secrets checked **separately** — a file with no
identifiers may still carry a token.

## Numbers carry their moment, and here that is sharper than elsewhere

`../README.md` requires every quoted number to have a row in `../reference/measurements.md` with when,
with what, over which slice, and what for. **A bug's numbers expire faster than anything else in
`docs/`** — they describe a system somebody else is actively changing.

So a figure in a bug document is written with its date attached **in the sentence**, not only in a
register. A bare number here is a number that will be quoted after it stopped being true.

## The index

Each document adds its own row when it is written, rather than the index describing files that do not
exist yet.

| BUG | Title | Status | Last confirmed | What it is about |
|---|---|---|---|---|
| **000** | About these documents | — | — | This file: what a bug document is, how they are numbered, the status vocabulary, and the index |
| **001** | [Non-streamed `/v1/messages` rejected as rate-limited](BUG-001-non-streaming-messages-rejected-as-rate-limited.md) | **open** | 2026-08-25 | Every non-streamed `POST /v1/messages` returns `429 rate_limit_error`, while a streamed request **2.8× larger** to the same model succeeds 0.6 s later. 83 of 83 rate-limited calls were non-streamed; 375 streamed calls in the same window produced none. Disables Claude Code's auto mode, whose safety classifier is non-streaming |
