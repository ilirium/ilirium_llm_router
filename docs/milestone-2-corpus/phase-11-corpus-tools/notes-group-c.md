# Phase 11 — Group C: the converter

**Tasks 11–13.** Reassembly of both response encodings; delta reconstruction across a session's calls
and across day folders; `uuid`/`parentUuid` synthesis and the viewer's record shapes.

**In flight — tasks 11 and 12 are done, task 13 is not.** Tasks 14 and 15 are **struck in place** and
must not be resurrected or renumbered.

**The sharp end of the phase.** The store went to some trouble never to parse a body and this group
parses every one of them: *parsing lives in the tools, the store stays opaque.* Split out of `notes.md`
on 2026-08-26 per `../../README.md`'s group rule.

---

## Task 11 — reassembly, and two instruments that agree on all 979 rows, 2026-08-26

`transcript.py` reads a captured reply back into the message it was, or says which of six reasons it
was not one. **The store never parses a body and this module parses every one of them** — that is the
line the phase has to keep on the right side of, and nothing here is imported by the write path.

### The corpus was read before the code was written, and it moved three things

**Every response blob in the live corpus was decompressed and shaped**, 2026-08-26:

| Shape | Blobs |
|---|---|
| SSE | **808** |
| JSON `type=error` | **93** |
| JSON `{"input_tokens": N}` — `count_tokens` | **47** |
| zero-length | **4** |
| **JSON `type=message` — a buffered reply** | **1** |

**1 · The plan's "66 buffered replies" was the `count_tokens` count.** The task had already corrected
this exact conflation once — *"it conflated 'not streamed' with 'a buffered assistant reply'"* — and
then landed on **66**, which is the number of `count_tokens` rows. **The real figure is one call in
979.** The path is still built; what does not survive is the impression that it is a third of the
traffic, and *"both encodings are handled"* is now in "does not settle" so it is not read as coverage.

**2 · A content block has five types, not one.** `text`, `tool_use`, `thinking`, `server_tool_use`,
`web_search_tool_result`. **The last two were invisible in a two-day sample** and appeared only when
the count was re-run over all four days — 4 occurrences each. *A sample that covers 60% of a corpus
can still miss a category entirely, which is the argument for the full pass and not the fast one.*

**3 · A tool input arrives as JSON string fragments.** **64,260 `input_json_delta` against 2,071
`text_delta`** — the deltas are overwhelmingly *tool arguments*, not prose. They must be concatenated
and parsed **after** the block closes; parsing each fragment fails on all but the last. **All 654
tool inputs in the corpus parse to dicts, none left as a fallback string.**

*None of this is in the register's SSE list, which named the **events** and never what they carry.
Four rows added.*

### The strongest evidence this task produced is not a test

**`reassemble` was driven over every response blob in the live corpus and joined back to the index**,
which records `error_status` independently at capture time. **979 rows, 0 unresolved, 0
contradictions:**

| index `error_status` | reassembler says | rows |
|---|---|---|
| `ok` | **message** | **808** |
| `ok` | skip: `not-a-message` | 66 |
| `ok` | skip: `empty` | 9 |
| `http_error` | skip: `error` | 93 |
| `http_error` | skip: `empty` | 2 |
| `client_disconnect` | skip: `incomplete` | **1** |

**Two instruments, built years and phases apart, agreeing row for row.** `observe.py` wrote
`error_status` from HTTP status at capture time; `transcript.py` derives its verdict from the body's
own shape months later, knowing nothing about the column. **Nothing lines up like that by accident**,
and no green test could have said it.

*It also confirms the digest→path reconstruction — `FANOUT = 2`, `BLOB_SUFFIX = ".zst"` — on 979 rows
with **zero** unresolved, which is what the extractor will depend on.*

### The one `incomplete` stream was identified, not shrugged at

One SSE stream ends mid-`text_delta` at 912 bytes, with **no `error` event and no `message_stop`**.
Joined back to its index row: **it is the corpus's single `client_disconnect`** — *"The caller went
away before the reply finished."*

**That is why `stream-error` and `incomplete` are two reasons and not one.** An `error` event means
the router authored one because the upstream stream broke; a bare stop means **nothing went wrong
upstream at all** and the caller simply left. *`stream-error` has **zero** occurrences in the live
corpus and seven in Phase 9's gate corpus — so one of the six reasons is tested only synthetically,
and it is written down here rather than left to look like coverage.*

### What the tests carry that the corpus cannot

**18 tests, 337 → 355.** Two paths exist here or nowhere: **the buffered reply** (one real example)
and the **SSE `error` event** (none). The rest are the reverse — cheap to assert, and already proven
at scale by the pass above.

*The `data:`-split-over-several-lines test is for something Anthropic does not currently do. The SSE
spec allows it, and a reassembler that assumed otherwise would break on the day it changed, for a
reason no capture would ever explain.*

---

## Task 12 — delta reconstruction, and the corpus moved four things, 2026-08-28

**The corpus was read before the code was written**, as task 11 did. It paid for itself four times:
one of the plan's two named normalisations turns out to do nothing on its own, a **third** mechanism
is needed that is *not* a normalisation, the obvious form of the missing-day check is unsound, and
**the plan's stated reason for that check does not survive this design** — that last one is written
up separately below because it contradicts a settled sentence.

**378 tests, 355 → 378.** `make lint` clean, `make check` valid.

### The two normalisations, measured one at a time

Finding 2 named them and gave a corpus-wide figure. Measured here on one 77-call conversation, each
applied alone:

| | prefix property holds |
|---|---|
| raw bytes | **0 / 76** |
| strip `cache_control` only | 46 / 76 |
| bare string → content blocks only | **0 / 76** |
| **both** | **65 / 76** |

**The encoding fix scores zero on its own**, which is not what "two normalisations" suggests. The
`cache_control` breakage sits earlier in the array and masks it, so a session that fixed only the
encoding would measure no improvement at all and conclude the finding was wrong.

*The marker's behaviour, seen directly: Claude Code puts it on the **last** message of each request,
so it walks forward — call 6 marks message 12, call 7 marks 14, call 8 marks 17. The turn it leaves
is unchanged. Every comparison breaks on a message whose content never moved.*

### A `session_id` is not one conversation, and root-keying separates them without classifying

**36 conversations across 9 sessions**, keyed by the normalised root message. Each session holds one
real conversation plus a two-message classifier, a `quota` probe, title generation, and web
search/fetch calls. Session `15b29c2a` also holds a **66-call subagent conversation** carrying the
parent's `session_id` — finding 4, present and separated.

**It separated the subagent without consulting `agent_id` at all.** That matters because the column
is empty on all but 67 rows in the corpus, so a mechanism keyed on it would work here and nowhere
else. Root-keying asks *"is this the same conversation?"* and never *"is this call a probe?"*, which
is the line position 15 draws.

*The `quota` probe is byte-identical in all nine sessions — one 8-hex root digest recurring nine
times. Harmless, because `session_id` prefixes the filename, but it is why the digest alone is not a
name.*

### The third mechanism is a commit rule, not a normalisation — and the distinction is load-bearing

**100 times in the corpus a message was revised by the next call**, 9 of those changing role
outright (`user:['text']` → `assistant:['thinking','tool_use']`). A normalisation makes two
*encodings* of one message compare equal; these are not that. The content genuinely changed — the
client sent something and then sent something else in the same position.

**So no comparison fix can address it, and looking for one is the trap.** A session told "there is a
third normalisation" would hunt for a canonicalisation that does not exist. The fix is about *when*
to emit: turns are taken from the conversation's **latest** state, never as first seen. A retracted
turn then cannot reach the transcript, because it is not in the final array.

*Checked before relying on it: within a conversation the array **never shrinks** — 678 pairs grew,
143 held their length, none got shorter. `shrank` is counted anyway, because the day a client
compacts under an unchanged root, a silent reconstruction would present the remainder as the whole.*

### The assistant turn exists twice, and the difference is one field

Every assistant turn is in its own response blob and, one call later, inside the next request's
`messages`. Compared on all **631** cases where both exist: **72 identical, 559 different** — and
the difference is a single field every time.

**`tool_use` blocks carry `caller` in the response and never in the request.** Counted directly:
**47,628** request-side `tool_use` blocks, **none** with it; **630** response blobs mention it. The
client strips a server-side annotation before sending the turn back. Block shapes agree in 630 of
631 cases.

**So the response is the source and the request copy is the fallback**, used only when a call's own
response was not a message. `Turn.source` records which, so this is visible per turn rather than
assumed.

### The obvious missing-day check is unsound, and it was nearly built

The cheap structural form — *"a conversation whose first call is already deep did not start in the
folders passed"* — was measured before being written. **11 of the 36 conversations legitimately open
at two messages**, so a depth rule false-positives on a third of them. The exact set difference
between the session's days and the days passed is the only honest form, and it needs the caller to
have read the corpus rather than the selection.

### The strongest evidence is not a test, again

**`reconstruct` driven over the whole live corpus**, all four day folders, every session:

| | |
|---|---|
| calls in / accounted for | **902 / 902** |
| conversations | **36**, matching the independent count made before the code existed |
| filenames | **36 distinct**, 9 marked main, one per session |
| gaps | **45** — the `too_large` tail, all in `ad9392ae`, contiguous at calls #225–#269 of 270 |
| shrinks | **0** |
| skips | **93 `error` + 1 `incomplete`** |

**That last row is the join worth having.** 93 and 1 are the corpus's own `http_error` and
`client_disconnect` counts, recorded by `observe.py` at capture time from HTTP status. `reconstruct`
reaches them through `reassemble`, from body shape, knowing nothing about the column — the same
agreement task 11 found, now surviving a second instrument built on top of the first.

*The cap is crossed once and never recrossed: `request_bytes` runs 1,043,805 → 1,047,198 →
**1,051,096** at call #225, straight through 1 MiB. **All 45 of their responses reassemble into real
assistant turns** — only the prompts are gone, which is why they are emitted behind a `Gap` rather
than dropped. Settled by the owner on 2026-08-28, option (c) of three.*

### The tests were mutated, because they went green on the first run

**23 new tests, and all of them passed immediately** — which `CLAUDE.md` says is not evidence. Three
mutations, each expected to break a different guarantee, plus a no-op control:

| Mutation | Result |
|---|---|
| `cache_control` no longer stripped | **tests fail** |
| the missing-day check disabled | **tests fail** |
| the byte-identical-retry guard removed | **tests fail** |
| a control edit that changes nothing | **stays green** |

*The control is the half that is usually skipped. Without it, three failures only show the suite
reacts to edits, not that it reacts to the **right** ones.*

### Two instrument errors, and both were the ones already written down

**`awk` counted bytes again.** It reported 13 over-width lines in `transcript.py`; measured in
characters there were **4**, the other nine being em-dashes. This is the same error this branch
recorded on 2026-08-26, made again by the same tool two days later — **writing a hazard down did not
stop it recurring**, and what caught it was the count looking too high, not the note.

**And rewrapping created a new violation.** Fixing the four pushed words onto the following line and
produced a fifth at 103 characters. Also already recorded, also repeated. **Re-measure after the fix
is not advice, it is the only thing that works.**

---

## Task 13 — the viewer's records, and a defect only the corpus could find, 2026-08-28

**394 tests, 378 → 394.** `jsonl.py` built; **all four `❓` resolved**; `make lint` clean;
`link-check` **85 broken, down one** — the register's forward reference to `jsonl.py` now resolves.

**Group C is complete.** Tasks 14 and 15 remain struck in place.

### The schema was read, not guessed — and it moved four things

Position 17's two sources, with the owner's go-ahead on the day: the viewer's own source, and **one**
real session file read only far enough to learn field names. *The file happened to be `ad9392ae`, the
same session as the corpus's largest — **task 14 is struck, so no ground-truth diff was made**, and
nothing beyond field names and enumerations was read.*

**1 · A session is identified by its *filename*, not by `sessionId`.** The loader sets
`session_id: file_path_str`, and **two files carrying the same `sessionId` are not merged.** This
closes the question task 12 opened: one file per conversation is safe, and `sessionId` stays verbatim
in all six of `15b29c2a`'s files. *Had it been the other way, the split would have been undone at the
record layer and the interleaving would have come back.*

**2 · There are ten record types in a real file, not three** — `mode`, `permission-mode`,
`file-history-snapshot`, `user`, `attachment`, `ai-title`, `assistant`, `last-prompt`, `system`,
`file-history-delta`. **Only four carry `uuid`/`parentUuid`**; the rest are session-level sidecars
outside the chain. In that file: **863 chained records, exactly one root, zero dangling parents.**

**3 · A `system` record renders unless its subtype is hidden, and the hidden list has two entries.**

```rust
if msg.message_type == "system" { return !is_hidden_system_subtype(msg.subtype.as_deref()); }
const HIDDEN_SYSTEM_SUBTYPES: [&str; 2] = ["stop_hook_summary", "turn_duration"];
```

**That is what settles the fidelity marker**, and it settles it *better* than the fallback the plan
had ready. The `❓` said the marker must not be a *plain* `system` record because a real `system` role
occurs inside `messages`; a subtype of our own is both **shown** and **machine-distinguishable** from
the three real subtypes observed. The planned fallback — a `user` record carrying the same text — is
not needed and was not used.

**4 · `type` is the only field the loader strictly requires**, and `message` needs `role` and
`content`. So the fields the corpus cannot supply are simply **absent**, never faked. *Worth knowing
that they are conspicuous: `cwd`, `gitBranch`, `version` and `toolUseResult` are on every `user` and
`assistant` record in a real file, so their absence is visible to anyone comparing — which is why the
note names all five rather than letting them be discovered.*

### The `uuid` recipe had to change, and the register says so rather than the code drifting

Register §9 specified `uuid5(NS, "<request-blob-digest>:<record-index-within-call>")`. **Task 12's
design cannot supply it.** A turn is taken from the conversation's *latest* state, so it belongs to no
single call and has no one request blob — **the same objection that retired `<block-index>` on
2026-08-26, one level further up, and the register did not notice it applied twice.**

It is now `uuid5(NS, "<session_id>:<conversation-key>:<slot>")`. Session, conversation and position
are what a turn actually has, and all three are stable: the message array is append-only, so a
position never shifts under a growing corpus.

### The defect the tests did not find

**Emitting all 36 conversations produced 1,615 records and 1,614 distinct `uuid5` values.** One
collision, and **378 tests passed throughout.**

The final call's reply sits at position `depth` — it is the one turn that appears in no request, so
nothing else occupies that slot — and `_attach_orphans` began numbering the `too_large` gaps at
`depth` as well. Only `ad9392ae` has both a tail reply and gaps, so exactly one collision existed in
the whole corpus.

**Nothing failed. No exception, no malformed output, no test.** Two records would simply have carried
the same id into the viewer, which is the kind of thing that surfaces as *"the history viewer is
behaving oddly"* weeks later. **It was found by counting the output against itself** — records against
distinct ids — which cost one line in the drive script.

*This is the third time in this phase that the evidence which is not a test has been the evidence that
mattered, and the first time it caught something rather than confirming something.*

### The tests were mutated again

**16 new tests, green on the first run.** Six mutations, each aimed at a different guarantee, plus a
control:

| Mutation | Result |
|---|---|
| `parentUuid` chain broken | **fails** |
| `uuid4` instead of `uuid5` | **fails** |
| the marker given a hidden subtype | **fails** |
| a `system` role flattened to `user` | **fails** |
| `sort_keys` removed from the writer | **fails** |
| **the collision fix reverted** | **fails** |
| a control edit that changes nothing | stays green |

*The sixth is the one worth having: it proves the regression test earns its place rather than merely
describing the bug after the fact.*
