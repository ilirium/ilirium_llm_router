# The next session's prompt

*The one file in `docs/` allowed to go stale, per `README.md` — which is why it is rewritten at each
handoff rather than left. **Replaced 2026-09-19 (evening)**, mid-phase rather than at a merge.
Whatever comes next replaces it again.*

---

**Phase 14 is OPEN and IN FLIGHT. Nothing is merged.** Work in
`/Users/ilirium/Projects/local/ilirium_llm_router/phase-14-rate-limit-headers` — *that worktree, not
`main`. A session started in `main` sees none of this.* Branch
`feat/phase-14-rate-limit-headers`, forked from `main` at `ac2976e`.

***The phase's question is ANSWERED and nothing is in flight inside it.*** **Auto mode's safety
classifier now works through the router**, measured 2026-09-19 with a positive verdict rather than
an absence of failures. **The working tree is clean and every check is green.** *No experiment is
set up and waiting, unlike the last two handoffs.*

*No commit count is written here. A count written at a handoff is wrong at the next commit, and this
repository has recorded that defect six times — including in `status.md`'s own in-flight section,
which said 21 while the branch held 29.*

## Read these, in this order

1. **`docs/status.md`** — first, every session. The only file that holds state. *"Where we stopped"
   was rewritten at this handoff and is current.*
2. **`.../phase-14-rate-limit-headers/for-the-owner.md`** — ***twenty entries; 17, 18, 19 and 20 are
   the live ones.*** Read it before `plan.md`.
3. **`docs/bugs/BUG-001-non-streaming-messages-rejected-as-rate-limited.md`** — its top section is a
   one-page synthesis written for exactly this purpose. **Read that before the phase notes.**
4. **`.../phase-14-rate-limit-headers/notes.md`** — long, and written while the work ran. **Read it
   by section**, per `CLAUDE.md`. *The last four sections are 2026-09-19's.*

## What the phase settled, in the shape that matters

***There were TWO defects, stacked, and the first hid the second.*** **Conflating them is the
single easiest mistake to make here.**

| | Cause | State |
|---|---|---|
| **The `429` on non-streamed `/v1/messages`** | ***Client-side.*** Claude Code withholds things when `ANTHROPIC_BASE_URL` names any host but `api.anthropic.com` | **Worked around, not fixed.** The hosts route makes the client first-party while still routed. ***The cause is not identified beyond the gate*** |
| **The classifier failing after the 429 went away** | ***The router's own `accept-encoding` experiment.*** Non-streamed replies came back **brotli** | ***Fixed.*** Off by default and pinned off in every committed config |

**The second one was ours**, it ran for a day, and `for-the-owner.md` entry 7 called it
*"exonerated"* — a clearance earned against the 429 and allowed to stand for the component.
***A negative result for one symptom is not a clearance for the thing that produced it.***

## Five things a session will get wrong here

- ***"It works" is not one claim.*** **The 429 is worked around; the compression defect is fixed;
  the CAUSE of the 429 is still unknown.** *Saying the phase "solved `BUG-001`" is wrong on the
  third.*
- ***A `200` from the router is not a working classifier.*** **On 2026-09-19 at 12:31 the router
  served nine classifications with valid verdicts and the client reported every one as
  unavailable.** *The check that settled it was aligning the owner's transcript against
  `calls.csv` — **ask the person who was in the session**, and `evidence/claude-code-sessions-to-check-safety-classifier.txt` is that record.*
- ***An absence of 429s proves nothing*** — `BUG-000`, and this phase spent three runs on it.
  **What closed it was a `<block>` verdict**: drive probes until one is actually *blocked*, not
  until nothing fails.
- ***The three experiments are config keys now and all are `false`.*** **`check` prints
  `EXPERIMENTS ON` and names any that are not**, and two tests assert every committed config keeps
  them off. *An `EXPERIMENTS ON` line at startup means the router is not a plain byte-relay and no
  measurement taken with it is a control.*
- ***`branch-index.py --write` DELETES a row it must not delete, and `--check` says only `STALE`.***
  **It is STALE right now, here and on a clean `main`, for that reason alone.** *`temp/to-run-server`
  has been fast-forwarded to `main`'s tip, `resolve()` reads that as in-flight, and `--write` drops
  its row — the only record that the branch is not work.* **`IDM-001` puts `--write` as the last
  step of every merge, so the next merge deletes it without anyone looking.** → `for-the-owner.md`
  entry 4. ***Do not "fix" the STALE with `--write`.***
- **`link-check.py`'s count is a property of the worktree.** **112 here**; `main` was 92 at the last
  merge. *Compare within one tree or not at all.*

## Open, smallest first, and none of it blocks

1. ***Isolate `relay_accept_encoding`.*** **Turn only that one back on and drive three probes.**
   *Three switches went off together, so the run credits the set; the reply encodings narrow it to
   one, but that is mechanism rather than measurement.* **Worth doing before anything goes upstream,
   because the report has to say the router was at fault for half of it.**
2. ***`content-length` versus compression.*** **Both facts are now pinned by tests** —
   `test_a_compressed_reply_keeps_its_content_encoding` and
   `test_a_relayed_reply_carries_no_content_length` — *so separating them is a deliberate
   change to the second rather than a silent change in behaviour.* **The router relays `content-encoding: br` correctly
   — tested — and drops `content-length`, so a compressed reply goes out chunked.** *Keep the
   compression and stop dropping the length: if it then works, the bug is the missing length rather
   than the compression, which is fixable rather than merely avoidable.*
3. ***The subtractive attribution test.*** **Under the hosts route, have the router STRIP the
   attribution block and drive a few classifier calls.** *It fabricates nothing.* **429 returns →
   the block is the cause of the gate's effect. 429 stays away → the cause is still unfound.**
   ***This decides whether item 4 is worth building at all.***
4. ***Making it work with `ANTHROPIC_BASE_URL` set*** — the owner asked for this directly.
   **The only candidate is supplying the attribution block, which is a text element in the `system`
   array of the BODY, not a header**, so it means parsing and re-serialising. *Scope is narrow:
   rewrite only non-streamed Anthropic requests that lack the block — the ones failing today — so
   streamed requests keep byte-relay and their prompt cache.* ***Do not build before item 3.***
   **`cch` is computed per request and the gate is a class of which two members are known**, so it
   may fail even if the block is the cause.
5. **`BUG-001` upstream.** *Open since 2026-08-25 and now far stronger than it has ever been: a
   paired control on one client build where the only variable is whether the client believes its
   base URL is Anthropic's.* **Both issues are named in the file.**
6. **Group D has never started** — where the headers durably live, still the milestone plan's
   *"Phase 14's plan cannot skip the question"*. **Only the owner can overturn the `calls.csv`
   non-goal.**
7. **Everything the 2026-09-17 handoff listed is still open**: the corpus tools undriven by hand
   *(partly discharged — `extract --format bodies` was driven, the history-viewer half was not)*,
   `BKL-0017`, `EPD-001`, `EPD-002`, `BKL-0007`, and `git fetch origin`.

## What changed in the repository itself, which a session will not expect

- ***Three new config keys***, `experiments.*`, documented in `config.yaml` and its shipped
  template. **`plan.md`'s register said "New config keys: None" and that row now records the
  reversal and why.**
- ***`backlog-index.py`'s order rule changed*** — **ids ascend within a SECTION, not across the
  file.** *The old rule left exactly one legal position for any new item, the end of the last
  section, which is "Not on this list, and why". **Nothing had ever been added** since Phase 13
  numbered all 38 in one bulk pass, so nobody had met it.* **`IDM-011` carries the amendment.**
- **`BKL-0039`** — a protocol matcher and an HTTP/2-capable inbound. *Parked with the reason:
  uvicorn speaks only `h11`/`httptools`, so the matcher's second branch could never execute.*
- **A gzip request-body defect was fixed.** *A first-party client compresses some bodies and the
  model peek was reading them compressed.* **`decoded_for_peek` inflates a throwaway copy; the
  original bytes are what get relayed and stored.**

## What is finished, so nothing is half-done

**The working tree is clean and every finding is committed.** ***Every check re-run at this
handoff:*** **500 tests, 43/43 mutations, `make lint` clean at the pinned `0.16.1`,
`backlog-index --check` at 35 live / 39 ids, `link-check.py` at 112.** ***`branch-index --check`
is `STALE` and must not be fixed with `--write`*** — entry 4, and it is not this branch's doing.

*Push state was deliberately not checked at this handoff, on the owner's instruction — as at the
last two.*

## The working agreement still applies

`CLAUDE.md`, in full. Two were paid for again on 2026-09-19:

**Exercise it before committing** — *and the version this phase has now paid for five times:*
***a green check tells you the instrument works, never that it is aimed correctly.*** **A test
written this session passed a mutation that deleted half the thing it was asserting**, and it was
caught by the harness rather than by reading.

**Ask before inferring, and raise it rather than burying it.** ***The owner supplied the thing no
log could***, twice: the transcripts that showed the classifier failing while the router's record
said `200`, and the instinct to drive probes until one was **blocked**. → the memory note
`ask-rather-than-infer-about-the-setup`.
