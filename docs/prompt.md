# The next session's prompt

*The one file in `docs/` allowed to go stale, per `README.md` — which is why it is rewritten at each
handoff rather than left. **Replaced 2026-09-20**, mid-phase rather than at a merge. Whatever comes
next replaces it again.*

---

**Phase 14 is OPEN and IN FLIGHT. Nothing is merged.** Work in
`/Users/ilirium/Projects/local/ilirium_llm_router/phase-14-rate-limit-headers` — *that worktree, not
`main`. A session started in `main` sees none of this.* Branch
`feat/phase-14-rate-limit-headers`, forked from `main` at `ac2976e`.

***The working tree is clean and every check is green*** — 510 tests, 52/52 mutations, `make lint`
at the pinned `0.16.1`, `backlog-index --check` at 37 live / 41 ids, `link-check.py` at 112 in this
worktree. *No commit count is written here; `git rev-list --count main..HEAD` is the answer, and
this repository has recorded the defect of writing one down seven times.*

## Read this first, because it reverses three days of conclusions

***THE PHASE'S CENTRAL FINDING IS IN DOUBT, AND THE LIKELY CAUSE IS THIS REPOSITORY'S OWN
`README.md`.***

**`CLAUDE_CODE_ATTRIBUTION_HEADER=0` sits in the documented command for pointing Claude Code at the
router.** *Added 2026-08-07 in `7cd90f9`, six weeks before this phase opened, with no stated reason
in any of the four documents that carry it.* **It switches off the attribution block whose absence
this phase spent three days attributing to a client-side gate on `ANTHROPIC_BASE_URL`** — and *the
owner had been setting it on every run that also set the base URL.*

| Day | Base URL | The env var | Blocks | Non-streamed |
|---|---|---|---|---|
| 09-18 | set | ***`=0`*** | **none** | **119 × 429** |
| 09-19 | unset, hosts route | not used — no base URL to pair it with | 97 | all ok |
| **09-20** | **set** | ***dropped*** | **19** | classifier ok |

***The two variables were never separated.*** **`ANTHROPIC_BASE_URL` may suppress nothing at all.**

***And the disproof was on disk from the first hour.*** *Two requests on 2026-09-18 carried
attribution with the base URL set — the `-p` probes. `notes.md` recorded them and read them as a
quirk of the `-p` entrypoint; they were almost certainly a command line without the env var.*

## What is waiting on the owner, and it is two minutes of their time

**`for-the-owner.md` entry 22 is the runbook.** *Same machine, `ANTHROPIC_BASE_URL` set both times,
the router's own injection **off** — so `config.yaml`, not `config-attribution.yaml`:*

| **A** | ***with*** `CLAUDE_CODE_ATTRIBUTION_HEADER=0` | **429s return** → the cause is named |
|---|---|---|
| **B** | ***without it*** | **429s stay away** → the fix is deleting a line from a README |

***Entry 22 also carries the one question a session cannot answer for itself:*** **did the owner
drop the variable for the 2026-09-20 run?** *Everything above rests on it, and it was asked rather
than inferred — the memory note `ask-rather-than-infer-about-the-setup`.*

***Drive harsher probes than 2026-09-20's.*** **Every verdict that day was stage 1, ceiling severity
25, and stage 2 never ran** — *so there is still no blocked verdict in the record.* **`BUG-000`: an
absence of 429s proves nothing, and 2026-09-19's blocked probe scored 68.**

## Read these, in this order

1. **`docs/status.md`** — first, every session. The only file that holds state. *"Where we stopped"
   was rewritten at this handoff and is current.*
2. **`.../phase-14-rate-limit-headers/for-the-owner.md`** — ***twenty-two entries; 21 and 22 are the
   live ones.*** Read it before `plan.md`.
3. **`docs/bugs/BUG-001-…`** — ***its banner first.*** The one-page synthesis below the banner is
   the doubted conclusion, kept because the measurements in it are still good.
4. **`.../phase-14-rate-limit-headers/notes.md`** — long, and written while the work ran. **Read it
   by section**, per `CLAUDE.md`. *The last three sections are 2026-09-20's.*

## What must NOT be done before the A/B run answers

- ***Do not edit `README.md`.*** **Removing the env var line is acting on a conclusion with one
  unconfirmed fact in it.** *It is the first thing to do once entry 22's run confirms it — and then
  in all four documents that carry it, not only the README.*
- ***Do not rewrite `BUG-001` or `wiki/claude-code-first-party-gate.md`.*** **Both carry banners
  saying what is in doubt and why.** *Replacing one unverified conclusion with another is the move
  that already cost that document three retractions.*
- ***Do not read Group C4's 2026-09-20 run as a result about C4.*** **The injection fired zero
  times.** *Every request it could have helped already carried a block, so the run says nothing
  about whether it works.*

## Group C4, which is built and may be deleted rather than shipped

**`src/ilirium_llm_router/backend_anthropic.py`** — the block's constants and the one function that
builds it, with the measurement behind each hardcoded value in the docstrings.
**`experiments.add_claude_code_hidden_attribution_block`**, off by default, pinned `false` in all
four committed configs, named by `check` when on. **The one deliberate exception to byte-relay**,
narrowed to the Anthropic backend, non-streamed, uncompressed, and bodies with no block already.

***If the A/B confirms the env var, all of it comes out.*** **A router that needs no code to fix
this is a better outcome than an injection that works**, and `for-the-owner.md` entry 22 says so.

*`config-attribution.yaml` and `make run-with-attribution` drive it. `make check
CONFIG=config-attribution.yaml` must print `EXPERIMENTS ON` naming exactly that key, or the config
did not take.*

## Five things a session will still get wrong here

- ***The corpus stores WHAT ARRIVED, not what was sent.*** **A body will never show the injected
  block.** *The proof it fired is the `attribution block added` line in `router.log`, and the log
  says why for every request it declined.*
- ***A `200` from the router is not a working classifier***, and **a status code is not an
  outcome.** *On 2026-09-19 the router served nine classifications with valid verdicts while the
  client reported every one unavailable. **Ask the person who was in the session.***
- ***Grepping for `<severity>N</severity>` finds the classifier's own PROMPT EXAMPLES, not
  verdicts.*** **The real verdict is truncated — `</severity>` is the stop sequence**, so the text
  ends `<severity>15`. *A response that looks empty of verdicts is not.*
- ***`branch-index.py --write` DELETES a row it must not delete, and `--check` says only `STALE`.***
  **It is STALE right now, here and on a clean `main`, for that reason alone.** *A branch
  fast-forwarded to the trunk's tip and one cut from the trunk's head are **topologically
  identical**, so no topological fix exists — the fix is declarative.* **`IDM-001` puts `--write` as
  the last step of every merge.** → entry 4, plan task **19**, and **`BKL-0041`** for the general
  guard. ***Do not "fix" the STALE with `--write`.***
- **`link-check.py`'s count is a property of the worktree.** **112 here**; `main` was 92 at the last
  merge. *Compare within one tree or not at all.*

## Phase 14's own corpus lives in THIS worktree

**`logs/` is per-worktree and gitignored whole.** ***The 2026-09-18, `-19` and `-20` day folders
exist only here*** — *`to-run-server/logs/` holds August and nothing of this phase.* **2026-09-18
and the 12:31 slice of 2026-09-19 hold response blobs that are brotli INSIDE the zstd**, so
`extract --format bodies` over those days hands a reader bytes; `reference/corpus.md` warns by name.

*`evidence/attribution-block-anatomy.sh` reproduces every number in the wiki page's anatomy section —
saved rather than run in a heredoc, which is the defect `c54f45c` was about.*

## What Group E has to do at the merge, and none of it is started

**Tasks 16–19, in `plan.md`.** *16 removes the three failed experiments and the five tests plus
`conftest` helper that serve them; 17 graduates or deletes the survivor and kills the `experiments`
block — **and something at startup must still say the router modifies requests**, because whatever
survives breaks byte-relay exactly as the experiments did; 18 promotes `tools/tls-terminator/` with
`escape-the-hosts-file.py` beside it, renames `make run-hosts` to `run-in-the-middle`, and documents
both in the root `README.md` as the FALLBACK; 19 is `branch-index.py`.*

***Task 12 is amended: the upstream report is WITHDRAWN***, owner's decision. **The bug is that the
router cannot carry Claude Code's non-streamed requests**, and a client-side cause does not make it
somebody else's to fix. *Consequence, recorded with it: the `relay_accept_encoding` isolation test
is not worth a session, so that switch's authorship of the second defect stays an **inference** and
`BUG-001` must say so rather than assert it.*

**Also open and none of it blocks:** *`BKL-0040` (the dropped `content-length`, a latent HTTP defect
any client could meet), `BKL-0041`, Group D, the corpus tools undriven by hand, `BKL-0017`,
`EPD-001`, `EPD-002`, `BKL-0007`, and `git fetch origin`.*

## The working agreement still applies

`CLAUDE.md`, in full. Two were paid for again on 2026-09-20:

**Exercise it before committing.** ***The mutation harness caught two things reading did not*** — a
test that passed with its own guard deleted, and a branch no test could reach. *It also had to be
fixed first: it could only break `proxy.py` and reported a clean run over a module it never touched,
which is its own documented failure mode.*

**Ask before inferring, and raise it rather than burying it.** ***The owner supplied the thing no
log could***, a third time: the env var that was switching off the block the whole time. → the
memory note `ask-rather-than-infer-about-the-setup`.

*Push state was deliberately not checked at this handoff, on the owner's instruction — as at the
last three.*
