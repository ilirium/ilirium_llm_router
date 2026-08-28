# Phase 11 — Group D: the extractor

**Tasks 16–19.** Selection over an index; the output layout under one `--out`; `--agent` built
against real traffic; and `verify-archive` re-run against a dicted corpus.

**Complete, 2026-08-28.** Task 19 was discharged early — driven on 2026-08-26 as task 9's exercise,
over all four day folders, and left visible in the plan rather than struck.

**This is the group that writes to disk.** Everything before it returned structures; `extract` is the
first thing here a person runs and gets files from. Split out of `notes.md` per `../../README.md`'s
group rule.

---

## Tasks 16 and 18 — selection, and the one folder it reads uninvited, 2026-08-28

`extract.py` selects on the **index alone** — 26 columns of metadata — and opens a blob only once a
row has been chosen. **416 tests, 394 → 416.**

### Exactness is the whole of task 16, and the corpus is what proves it

Matching is exact on every field (position 18), repeats of one kind OR-ed, different kinds AND-ed.
Driven over the live corpus:

| Selection | Rows |
|---|---|
| *(none)* | **979** |
| `--path /v1/messages` | **902** |
| `--path /v1/messages/count_tokens` | **66** |
| `--agent a5d7f3de9660cef93` | **67** |
| `--session 15b29c2a…` **and** `--path /v1/messages` | **253** |
| rows with no `session_id` → `_no-session` | **11** |
| rows whose `request_ref` is a sentinel | **45** |

**902 + 66 + 11 = 979**, and that arithmetic *is* the exactness claim: a prefix match would fold the
66 into the 902 and the total would still look right. It only fails to add up if you count the two
paths separately, which is why both rows are here.

### `--agent` is built and the contingency behind it is dead

Task 18 carried a standing contingency: **if the forward review's cold run left `agent_id` empty, the
strike stood and `observe.py:40` had a defect.** It did not — 67 rows, one agent, all inside the
parent session. `--agent` selects them exactly.

*Worth keeping straight: the column is a **partition key, not a filter** (finding 4). `--agent`
selects a subagent's calls; it is task 12's root-message keying that stops them being spliced into the
parent's transcript, and that works whether or not the column is populated.*

### The sibling scan — the owner's decision, and why the defence needed it

**Task 12's `MissingDayError` could not fire from the CLI**, and this was found by reading the
extractor's own description against it rather than by anything failing. The extractor was specified to
read *"the day folders it is given and nothing above them"*, with **no corpus-root concept**. But the
error needs to know a session has calls in a folder that was **not** passed — which cannot be learned
from inside the folders that were.

**Put to the owner as three options on 2026-08-28, and (a) was chosen:** read the `index.csv` of
sibling day folders, and nothing else — never a blob, never a dictionary, never a folder that is not a
sibling of one given.

*The conflict was narrower than the plan's phrasing suggested, and checking that mattered.
`reference/corpus.md`'s self-containment guarantee is about **blobs opening**: "`tar` one, unpack it
on another machine, and every blob in it opens". It is silent on whether a tool may look at a sibling.
**So the qualified exception is to the plan's own stronger wording, not to the guarantee it cites** —
which made the decision much cheaper than it first appeared.*

**Option (b) was measured and refused**: detecting it from within the passed folders means "this
conversation starts too deep", and **11 of 36 conversations legitimately open at two messages**. A
threshold that separates 28 from 2 today is a magic number waiting to be wrong.

Checked both ways on the corpus: passing only `2026-08-26` reports that `15b29c2a` also lives in
`2026-08-25`, and **a session confined to one folder comes back with just that folder** — so it does
not cry wolf, which is the half that would have made it useless.

---

## Task 17 — the output layout, and the first thing here that writes files, 2026-08-28

**427 tests, 416 → 427.** `extract` stops returning 2.

```
<out>/bodies/<session-id>/00001-request.json
                          00001-response.sse     ← .sse streamed, .json buffered
<out>/bodies/_no-session/                        ← the 11 rows that have none
<out>/projects/corpus/<session-id>.jsonl         ← the main conversation
<out>/projects/corpus/<session-id>-<key>.jsonl   ← each of the others
```

Driven over one live day folder: **317 rows read, 317 selected, 634 body files and 35 conversation
files.** *35 for one day is not a defect: 17 of them are `count_tokens` conversations, which the
mechanical rule admits because it asks "is this response a message?" and never "is this call a probe?"
— `--path /v1/messages` brings it to 18. **Position 20 defers `count_tokens` as work, and the baseline
neither special-cases it nor hides it.***

### Two decisions that look small and are not

**The response's extension is read off the body, not off the index's `stream` column.** `observe.py`
sets that column from **content-type**, and the design deliberately allows the two to disagree — so
asking the bytes is one source instead of two that could. It is also the same question `reassemble`
asks, which means the extractor and the converter cannot disagree with each other either.

**A sentinel row gets no file at all, rather than an empty one.** An empty file is indistinguishable
from a body that was genuinely empty, and **the corpus holds four of those.** The count is reported
instead.

### The day check runs before anything is written, and that is deliberate

It would have been simpler to let `reconstruct` raise mid-run. **A run that wrote three files and then
failed would leave a directory whose good files cannot be told from its abandoned ones** — which is
the same failure the error exists to prevent one level up. So every selected session is checked first.

Driven through the command a person actually types:

```
extract .../2026-08-26 --out … --format jsonl --session 15b29c2a…
error: a selected session has calls in a day folder that was not passed.
  15b29c2a-… also has calls in 2026-08-25
```

**Exit 1, zero files written.**

### Two instrument errors, both already written down, both made again

**`$?` after a pipe into `tail` reported `0` for a run that had failed** — the third of the three
instrument errors the 2026-08-26 handoff records, repeated two days later while checking this very
command's exit code. Measured properly it is **1**. *That handoff lists it in a section headed "and
none was caught by anything failing"; it was not caught by anything failing this time either.*

**And a rewrapping script broke the module it was fixing** — 18 lint errors from an automated attempt
to wrap long lines, on a file that had six. Reverted and rewrapped by hand. **The rule that keeps
being relearned is that the instrument is the thing to check first**, and a script written in the
moment to fix a formatting nit is still an instrument.

### `make lint` was run, failed, and the commit went in anyway

Task 17 was staged and committed while `make lint` was failing; the failure was read afterwards. One
import out of order, fixed in its own commit. **Running a check and not reading it is
indistinguishable from not running it**, and the only reason it cost nothing here is that the defect
was trivial.
