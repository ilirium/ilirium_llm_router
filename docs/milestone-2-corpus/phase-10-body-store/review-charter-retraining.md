# Forward review charter — the retraining revision

**Written 2026-08-19 under `../../method/IDM-004-reviewing-unexecuted-work.md`, iteration 1.**
The second forward review of this phase. `review-charter.md` beside this file is the first, covering
Tasks 4–24 as originally written; **this one covers only what the retraining interview changed on
2026-08-19**, which nobody has reviewed and nobody has executed.

**Named by subject rather than numbered**, so a third charter does not have to decide whether it is
`review-charter-3.md` or a rename of this one.

---

## Scope

**Under review: the parts of `plan.md` changed on 2026-08-19**, and the design they rest on.
Concretely — `git diff 379264a..HEAD -- plan.md`, 263 insertions:

- The **ten new rows** in "What is settled, and by whom", all dated 2026-08-19
- **"The retraining path, concretely"** — the whole section, including the two sub-sections on the
  comparison and on not pausing the router
- The rewritten **"One thing that is never in *the* worker"**
- The **`corpus.retrain:` config block** and its nesting argument
- **Task 13a** (the reader), **Tasks 14a–14f** (the trigger, the comparison, the pickup, the config,
  the commands, the tests), and the amendments to **Tasks 10, 11, 14, 15 and 18**
- The new rows in **"Documented versus measured"** and **"What this phase does not settle"**
- The **26th index column** and its `none`/empty encoding

**Explicitly NOT under review**, and a finding against any of these is out of scope:

- **Everything Groups A and B executed.** Tasks 1–6 ran; their results are frozen in `evidence/`
- **`notes.md`** — it records how decisions were reached, which `IDM-004` puts out of scope by name
- **`docs/wiki/` and `docs/procedures/event-loop-lag/`** — executed and measured, not forward-looking
- **The `IDM-002` amendment and `.claude/settings.json`** — in force now, not a plan
- **The original plan as reviewed on 2026-08-18.** Its 22 findings are applied; re-finding them is
  spent budget
- **How any decision was reached.** The owner's interview answers are decisions, not proposals

## The two questions — one per run

| Run | Question |
|---|---|
| **Author** — the session that wrote the revision | *Is this consistent with what was decided today, and with what the plan already decided before today?* It holds the interview and can see a contradiction with an earlier decision, or a question raised and never closed. **It cannot see its own blind spots** |
| **Cold reader** — fresh context | *Could you execute Tasks 13a and 14a–14f from this document alone?* **Name every place you had to guess.** The guesses are the findings |

## What to look for, defined against this document

- **Gaps** — a task that names an outcome without saying what produces it. The 2026-08-18 review's largest finding was of this kind: the plan said the router reads a dictionary and never said from where
- **Incorrect points** — a claim about `src/`, about the corpus, or about a library that the file does not support
- **Leftovers** — a sentence true before 2026-08-19 and false after. **This revision reversed a stated position** ("Task 11 stays at five keys") and rewrote another ("never in a worker"); anything else that assumed manual training is a leftover
- **Contradictions** — two places in `plan.md` that cannot both be acted on
- **Unanswered questions** — something the revision raised and left hanging without saying it is open
- **Concerns** — will it actually work

## Claims to re-verify by reading the source

**Each was checked once, by the session that wrote it, which is the weakest verification available.**
Named individually rather than as a category:

1. **`session_id` is column 2 of `calls.csv`**, so the index can split by session — claimed from `src/ilirium_llm_router/stats.py`
2. **`calls.csv` has 20 columns**, so the day index is 20 + 2 refs + 3 timings + 1 dictID = **26**
3. **`app.py`'s lifespan is where a background thread would start**, and it already owns the HTTP client and the stats writer
4. **`proxy.py`'s `record()` has four call sites** and every path reaches one *(carried from the first review; re-verify only if 14a's hook depends on it)*
5. **The path filter is a no-op** — every request body ≥ 1024 bytes in `logs/corpus-gate/` is `/v1/messages`, and `/api/hello`'s are 0 bytes
6. **`gate.py` does not deduplicate**, and its training set is 48 bodies / 26 distinct
7. **The duplicates are `overloaded_error` retries**, 73 request bodies / 47 distinct, concentrated in run-01
8. **`zstandard` API shape** — `train_dictionary`'s `threads` parameter affects only parameter variations, `dict_id=0` means a *random* id, `get_frame_parameters(...).dict_id` reads a frame's id
9. **The store deduplicates per day**, so a one-day training window needs no dedup step
10. **`logs/corpus/dicts/` is read at startup** in the pre-2026-08-19 design, which the rescan replaces

## Known false positives — do not spend findings here

- **Forward citations.** `plan.md` names files its own tasks create: `src/ilirium_llm_router/corpus.py`, `docs/reference/corpus.md`, `docs/procedures/corpus-dictionary/`. `../../procedures/link-check.py` reports these as broken and they are not
- **The link-checker count.** **76 broken, 2 roundabout** on this branch, re-derived by running on 2026-08-19. It never reports zero
- **`*(not started)*` on Groups C–F** and `Merge commit | not yet merged` — deliberate placeholders, catalogued in "Placeholders in this file"
- **Task numbers are not renumbered.** `13a` and `14a`–`14f` carry letters *because* execution has begun. That is the rule, not a defect
- **`--train-dict` working while `retrain.window_days: 0`** is deliberate, and the plan says why
- **A p50 lower than idle** in the wiki's tables is a measurement artefact that is already labelled as one — and the wiki is out of scope anyway

## The rules — copied in, not cited

1. **Read-only.** Return a work list; edit nothing. Fixing what you find destroys the ability to judge the finding.
2. **Label every finding `VERIFIED` or `REPORTED`.** VERIFIED means you opened the file and confirmed it. REPORTED means suspected and not confirmed. **A review that does not label cannot be triaged.**
3. **Findings and questions are separate sections.** A finding is a defect with evidence; a question is for the owner to decide.
4. **Nothing found is a complete answer.** A review that must produce findings will manufacture them. Say what you checked and found correct. **Refusals are first-class.**
5. **A settled decision may be questioned, never filed as a defect.** It goes in questions, with reasoning. The rows dated 2026-08-19 in "What is settled, and by whom" are settled.
6. **Every finding carries what it would cost to be wrong** — discovered now, against discovered after task N. That is the ranking.

## The output shape

```
[VERIFIED|REPORTED]  <one-line claim>
  Where:     file:line
  Evidence:  what was read, and what it said
  Cost:      what it costs to find this after task N instead of now
```

Then: a numbered **questions** list, each with what it would change. Then an **executability**
section — task by task for 13a and 14a–14f, could a cold reader run it, and every place a guess was
needed. Then **what was checked and found correct**.

**The merged work list goes in `notes.md`**, with what was accepted, what was refused, and why.
