# Phase 11 — corpus tools: notes

**Not yet merged.** *(Closed out at the merge, per `plan.md`'s "Placeholders in this file".)*

**Branch `feat/phase-11-corpus-tools`, forked from `main` at `f445d6f`, opened 2026-08-24.** The
first phase of this project worked in a **git worktree** rather than in the trunk checkout —
`../../../../phase-11-corpus-tools`, beside `main` and `to-run-server` under a bare clone.

## Index of the group files

*In the order they were written, which is the chronology the letter-sorted split otherwise breaks.*

| | |
|---|---|
| *(none yet)* | Group A has not started |

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

## What is open at the end of Group A

*(Group A has not started.)*
