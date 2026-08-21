# Procedures — the re-runnable tier

Instruments, not history. Everything here is committed **so it can be run again**, because the facts
it establishes expire: a vendor ships a release, a pinned library is bumped, a harness changes what it
sends.

Their *results* do not live here. A run that a claim rests on is frozen in that phase's `evidence/`;
what stays in this tier is the thing that produced it.

## The index, and when each is worth re-running

| Procedure | Establishes | Re-run when |
|---|---|---|
| `lmstudio-capability-probes/` | What LM Studio accepts, honours and silently ignores — the parity table in `../reference/backend-lmstudio.md` | **Every LM Studio release**, and before trusting any of that table against a *different local model*: capabilities vary per model |
| `lmstudio-usage-check.md` | Where `usage` and `stop_reason` live in a streamed reply, and that LM Studio repeats `input_tokens` in `message_delta` where Anthropic does not | Before changing the SSE scanner, and against any new local runner. Cited by `observe.py` and `tests/test_observe.py` as the authority for the scanner's rule |
| `anthropic-auth-check.md` | That Claude Code's OAuth bearer token is accepted by Anthropic as forwarded, and that the ten-entry `anthropic-beta` list must arrive intact | If forwarded requests start returning 401, or after a Claude Code version that changes what it sends. Cited by `config.yaml` |
| `testing-against-claude-code.md` | That a real session works end to end through the router, on both backends | At every milestone close, and after any change to the relay. This is the sign-off procedure — green tests are not one |
| `dying-backend/` | How the router behaves when a backend dies mid-answer, refuses to start, or when the caller hangs up | After any change to the relay or the error path. A backend cannot be asked politely to die halfway through a reply, so this is one that always does |
| `link-check.py` | Which cited paths no longer resolve, anywhere in the repository | **After any commit that moves a document**, and before and after a milestone close. It is the only check for a link that breaks by *depth* rather than by name, which no name-based grep can find |
| `branch-index.py` | The branch table in `../reference/branches.md` — every branch's opened date, fork point, merge commit and merge date, read out of git rather than typed | **At every merge**, with `--write`, committed alongside it. `--check` exits 1 when the table no longer matches git, which is the whole reason it exists: `../method/IDM-001-git-branching.md` refused a hand-maintained list because it drifts, and this is what makes the list derived. It reads git and nothing else — no router, no network |
| `read-timeout-semantics.py` | What httpx's `read` timeout actually applies to — the silence between two reads, restarted by every chunk | **After an httpx bump.** It is a fact about a pinned library, and the wrong belief about it stood in four documents for two phases |
| `corpus-benchmark/` | What the body store costs on this machine: whether more than one worker thread buys anything, what `corpus.compress_level_zstd` should default to, whether `store_ms` is compression or disk, and whether `zstandard`'s trainer agrees with `zstd --train` | **After a `zstandard` bump, and before trusting the level default on different hardware.** Also whenever the corpus grows enough to change the body mix — every number it prints is one machine on one day. It reads `logs/corpus-gate/` and starts nothing: no router, no backend, no network |
| `event-loop-lag/` | Whether a background thread actually protects the asyncio event loop — measured from inside, and as HTTP round-trips against real uvicorn from a separate process — and, when the work does *not* release the GIL, which offload does work and what it costs to hand a payload to | **After a Python upgrade** — the GIL and the switch interval are exactly what moves, and a free-threaded build changes the question entirely. Also if real Python work ever moves into the corpus worker, since the finding is that a thread only helps when the work **releases** the GIL. **And run `cpu_offload.py` under `python3` as well as the venv** — `InterpreterPoolExecutor` needs 3.14. It starts a server on `127.0.0.1:8791`, spawns worker processes, and writes nothing |

## Two rules that keep this tier working

**An instrument's `runs/` directory follows the instrument, never the archive.** Each of these that
writes output writes it beside itself, into a gitignored `runs/`. Put the output under a milestone
instead and two things break at once: the tool writes into a closed milestone's folder, and the ignore
rule stops covering the path it actually writes to.

**Each probe overwrites its own run file.** A result worth keeping must be copied out into a phase's
`evidence/` before the next run, and the test for "worth keeping" is *does re-running produce the same
number* — not *is this a tool or evidence*. A cold-cache replay, an over-window refusal and a timeout
are each unreproducible in that sense, and are frozen for exactly that reason.

## Writing a new one

A procedure document states, in this order: **why it matters, the procedure, what was actually
observed, and an explicit list of what it does *not* answer.** The last section is not optional — it
is what stops the next reader over-reading the result. Then add a row above, saying when it is worth
running again.

---

*Written 2026-08-16 at commit 5 of `../milestone-1-core/phase-7-docs-restructure/plan.md`. The instruments themselves arrive
here at commit 7; three of them are renamed on the way — `phase-4-probes/` →
`lmstudio-capability-probes/`, `phase-3-verification/` → `dying-backend/`, and
`phase-5-measurements/read_timeout_semantics.py` → `read-timeout-semantics.py`, which splits from a
README that stays with its evidence.*
