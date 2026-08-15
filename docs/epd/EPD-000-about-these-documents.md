# EPD-000 — What an EPD is, and the index of them

**EPD stands for Enhancement Proposal Document.**

An EPD is where a design question is written down *before* it is answered. It exists so that the
reasoning, the evidence, and the open forks survive somewhere other than a conversation — and so
that "we thought about this and deferred it" is distinguishable from "we never thought about it".

This file is the table of contents. It is also the place the conventions are recorded, so that each
EPD does not have to restate them.

## What an EPD is for

Three things, in order of importance:

1. **To separate a finding from a decision.** Most EPDs here exist because something was *measured*
   and the measurement raised a question nobody had asked yet. The measurement is durable and worth
   committing immediately. The decision it implies usually is not — it depends on work that has not
   happened.
2. **To hold a fork open honestly.** Where two designs are genuinely in tension, an EPD states both
   and picks neither. Picking one quietly, in code, is the failure mode this format exists to
   prevent.
3. **To record what is *not* in the specs.** EPD-001 exists because two requirements the owner
   assumed were specified turned out to be absent from every document in the repository.

## What an EPD is not

- **Not a design document.** `CLAUDE.md` holds the design. An EPD graduates *into* `CLAUDE.md` under
  "Design decisions" when a decision is taken, and the EPD then records that it was taken and where
  it went.
- **Not a plan.** `docs/implementation-plan.md` holds the phases. An EPD may name the phase it waits for;
  it does not schedule itself.
- **Not a build order.** Nothing in an EPD is implemented unless the document says so explicitly and
  names the date it was accepted.

## Conventions

**Numbering.** `EPD-NNN-kebab-case-title.md`, in `docs/epd/`, allocated in order written and never
reused. `EPD-000` is this index. Numbers do not imply priority or dependency. They lived directly in
`docs/` until 2026-07-31; if an old commit message or note points at `docs/EPD-…`, that is why.

**Every EPD opens with a status line.** It states the status, the date written, and — if nothing has
been decided — says so in the same sentence. The vocabulary in use:

| Status | Meaning |
|---|---|
| **proposal** | Written, nothing decided, nothing implemented |
| **partly accepted** | One named piece was accepted on a stated date; the rest is still a proposal |
| **decided** | The decision is taken and lives in `CLAUDE.md`; the EPD is kept for the reasoning |
| **withdrawn** | Superseded or shown wrong. Kept, with the reason, rather than deleted |

**Documented versus measured.** Every EPD carries a table separating what has been *observed on this
machine* from what has only been read in a vendor's documentation or inferred from a shape. This is
the repository's central discipline and it is not optional: one claim in `CLAUDE.md` was already
wrong once because a vendor capability was assumed rather than checked (see `docs/handoff.md`, last
section). Confidence words in that table are used deliberately — **Measured**, **Inferred strongly**,
**Inferred weakly**, **Documented only**, **Unmeasured hypothesis**, **Unknown**.

**Evidence is cited to something committed.** `logs/` is gitignored and rotates, so an EPD that rests
on a session cites a frozen copy under `docs/` instead. Identifiers in a frozen copy are mapped to
stable placeholders (`session-01`, `agent-01`), never blanked — blanking destroys the grouping the
argument depends on.

**Each EPD ends with the cheapest next step.** Usually minutes of measurement rather than any code,
and usually a *gate*: the one thing that, if it fails, makes the rest of the document not worth
building.

## The index

| EPD | Title | Written | Status | Waiting on | What it is about |
|---|---|---|---|---|---|
| **000** | About these documents | 2026-07-31 | — | — | This file: what an EPD is, and the index |
| **001** | [Model selection and mixed-model sessions](EPD-001-model-selection-and-mixed-model-sessions.md) | 2026-07-30 | **partly accepted** | Phase 4 | Choosing a local model with `/model` mid-session, and running subagents on local models alongside a Claude main conversation. Per-request dispatch already satisfies the second with no code. The accepted piece: the CSV's `session_id` and `agent_id` columns, taken into Phase 2 on 2026-07-30 |
| **002** | [Token counting for local backends](EPD-002-token-counting-for-local-backends.md) | 2026-07-31 | proposal | Phase 4 | LM Studio does not implement `/v1/messages/count_tokens` and answers it with HTTP 200 and an error body. Claude Code falls back to its own estimator against an assumed 200k window, which on a sub-200k local model means silent truncation behind a comfortable-looking meter |
| **003** | [Capturing bodies for a corpus](EPD-003-capturing-bodies-for-a-corpus.md) | 2026-07-31 | proposal | a decision on the fine-tuning goal | Storing every request and response body for later analysis, and possibly as a fine-tuning corpus. Establishes that the corpus is ~93% duplicated prefix, that the storage question is a compression-window question rather than a database question, and that the fine-tuning half of the goal runs into Anthropic's terms |
| **004** | [Documentation structure at the milestone boundary](EPD-004-documentation-structure.md) | 2026-08-15 | **decided** 2026-08-15, not yet implemented | — | The first EPD about the repository rather than the router. Milestone 1 is done and its documents no longer separate what is true from how it was found out. Four tiers — durable reference, re-runnable procedures, EPDs, and a per-milestone archive — and a numbering rule: number what needs a stable identity to be cited, not what needs an order. **All six forks decided 2026-08-15**; it graduates into `docs/README.md`, the documentation manual, rather than into `CLAUDE.md`. The migration is planned in `docs/docs-restructure-plan.md` |

## Cross-references between them

Worth knowing before reading any one of them, because they overlap at three points:

- **EPD-001 and EPD-002 both want `/v1/models`.** EPD-001 wants it to populate the model picker;
  EPD-002 wants `max_context_length` off it to fix the denominator. EPD-002's question 3 observes
  that building it might make its own central fork moot.
- **EPD-002 and EPD-003 both touch the byte-fidelity rule**, and both argue the rule is narrower than
  it looks — it protects bodies the router *relays*, because reserialization breaks the prompt-cache
  prefix. EPD-002 argues a body the router *answers itself* is exempt. EPD-003 argues storing opaque
  bytes is not reserialization at all. Neither argument has been accepted.
- **EPD-003 depends on the `session_id` / `agent_id` columns EPD-001 got accepted.** Without them a
  captured body cannot be attributed to a conversation or told apart from a subagent's.

## Related documents that are not EPDs

Findings and procedures live in their own files and are linked from `docs/handoff.md`. The distinction:
an EPD asks a question, these answer one.

`docs/anthropic-auth-check.md`, `docs/lmstudio-usage-check.md`, `docs/testing-against-claude-code.md` and its
`--results` companion, `docs/phase-1-notes.md`, `docs/phase-2-notes.md`, and the frozen session in
`docs/phase-2-step-6-session/`.
