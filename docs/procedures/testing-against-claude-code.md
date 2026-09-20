# Testing the router against a real Claude Code session

The procedure for Phase 1's "done when": pointing Claude Code at the router and checking that both a
cloud model and a local one work in an actual session. Written 2026-07-29.

Keep the steps in this order. Each one fails more cheaply than the one after it, so a problem in the
LM Studio setup surfaces before you have spent a session discovering it through a proxy you were
meant to be testing.

## 1. Sort out the LM Studio credential

Do this first or the local half returns 401 and you will debug the router when the fault is in
LM Studio. Either:

- **Turn authentication off** — LM Studio's Developer / server settings, "Require Authentication"
  off. Simplest for a first test.
- **Or configure the key** — take the token from that same screen, put `LMSTUDIO_API_KEY=<token>` in
  `.env`, and uncomment `api_key_env: LMSTUDIO_API_KEY` under `lmstudio:` in `config.yaml`.

Then run `make check`. It fails fast when the named environment variable is missing or empty, so a
clean report means the credential path is actually wired rather than merely written down.

## 2. Load a model with enough context

Note its exact ID (`lms ls`, or the LM Studio UI) — that string is what you pass to `--model`, and
the routing rule sends anything not starting with `claude-` to LM Studio.

Context is the likeliest thing to bite. A bare `hi` turn measured **118 KB**: 81 KB of tool schemas,
28 KB of system prompt, and 368 bytes of actual conversation. That is roughly 30k tokens of fixed
preamble before the user types anything, so LM Studio's own ">~25k" guidance is too optimistic. Load
the model with as much context as the machine will allow.

## 3. Smoke-test with curl before involving `claude`

Much faster feedback than a real session, and it isolates the router from the harness.

```bash
make run   # in its own terminal

curl -i -X HEAD http://127.0.0.1:8787/

curl -N -X POST http://127.0.0.1:8787/v1/messages \
  -H 'content-type: application/json' \
  -d '{"model":"<your-lmstudio-id>","max_tokens":64,"stream":true,
       "messages":[{"role":"user","content":"count to five"}]}'
```

`-N` turns off curl's own buffering, so tokens arriving one at a time means streaming genuinely
works. If they land in a single lump, that is a real finding and not a display artefact.

## 4. Point Claude Code at it

Use a scratch directory rather than real work. This is a proxy under test and a failure mid-session
is disruptive.

> ***`CLAUDE_CODE_ATTRIBUTION_HEADER=0` IS UNDER INVESTIGATION AS OF 2026-09-20, AND IT IS THE
> FIRST THING TO DECIDE BEFORE FOLLOWING THIS STEP.*** **It switches off Claude Code's attribution
> block, and the absence of that block is what `BUG-001`'s `429` tracks** — *so a session that
> copies the line below and then measures non-streamed requests is measuring this variable without
> knowing it.* **That is what happened for three days.**
>
> **The line is left in place rather than removed**, because the confirming run has not happened:
> `milestone-2-corpus/phase-14-rate-limit-headers/for-the-owner.md` entry 22 is a two-minute A/B
> and only the owner can drive it. ***Until it does: if you are testing anything about non-streamed
> requests, drop the variable — and say in your notes which way you ran it.***
>
> *It appears in four documents — this one, `../../README.md`, `../reference/architecture.md` and
> `../milestone-1-core/phase-1-proxy/evidence/session-results.md` — and it has been in all of them
> since 2026-08-07 with no stated reason. Its origin looks like `architecture.md`, where it sits in
> the block for pointing Claude Code straight at **LM Studio**, and where it makes sense.*

```bash
cd /tmp/router-test
ANTHROPIC_BASE_URL=http://127.0.0.1:8787 CLAUDE_CODE_ATTRIBUTION_HEADER=0 \
  claude --model claude-sonnet-5
```

No token needs setting. The router injects nothing and holds no secret, so whatever credential
Claude Code would normally send is what goes out — that is the whole point of *forward for cloud,
strip for local*. `/status` inside the session shows the overridden base URL, which is how you know
traffic is going through the router rather than straight to Anthropic.

Then repeat the same session with `--model <your-lmstudio-id>`.

## 5. What to check in each session

The "done when" is three things, so exercise all three against both backends:

- **Streaming** — text appears progressively rather than in one block.
- **Tools** — ask it to read a file and run a command. Tool calls are where a local backend is most
  likely to diverge, since LM Studio publishes no parity matrix.
- **Multi-turn** — a follow-up that refers back to an earlier turn, so the conversation is genuinely
  being carried rather than each request standing alone.

## Two things to expect

**Background calls cost money even in a local session.** Claude Code makes auxiliary calls with a
`claude-` prefixed small model, and the routing rule sends those to Anthropic whatever the main model
is. That is a deliberate decision recorded in `CLAUDE.md`, not a bug — but do not be surprised by
charges during a session you thought was entirely local.

**Which backend a request took is now in `logs/telemetry/calls.csv`.** Phase 2 landed on 2026-07-30,
so the `backend` column answers directly what used to require reading LM Studio's own server log.
That log is still a useful independent witness when the two disagree — but the CSV is the first
place to look.

## 6. Phase 2's "done when" — the session that checks the CSV

Written 2026-07-30, **before it has been run**. Steps 1 to 4 above still apply unchanged; this is
what to do differently once the session is up, and what to read afterwards.

Phase 2's own "done when" is *"a short session produces a readable log and a CSV whose rows match
what actually happened"*. Everything in the writer is unit-tested, so this step is not looking for
crashes. It is looking for the four things a test cannot know, listed under "What Phase 2 still has
to prove" in `handoff.md`.

### Drive the session to produce the rows worth reading

An ordinary session exercises only the easy half. Do these four things deliberately:

1. **Use both backends in one session.** Start local, then `/model claude-sonnet-5` and continue, or
   the reverse. One CSV containing both is what makes the `backend` column worth having.
2. **Spawn a subagent** — any task that makes Claude Code delegate. This is the *only* way to find
   out whether `x-claude-code-agent-id` actually arrives, which is the one column whose meaning is
   currently assumed rather than measured.
3. **Interrupt a long reply mid-stream** — ask for something lengthy and press Esc while it is still
   printing. This is the only way to produce a real `client_disconnect`; the unit test proves the
   branch works, not that starlette reaches it.
4. **Take at least three turns on the cloud model.** Prompt caching needs a second turn to read
   anything back, and the cache columns are the check that byte-relay is intact.

### Then read the file

```bash
python3 - logs/telemetry/calls.csv <<'PY'
import csv, sys
from collections import Counter
rows = list(csv.DictReader(open(sys.argv[1], newline="")))
print(f"{len(rows)} rows\n")
print("backend       ", Counter(r["backend"] or "(none)" for r in rows))
print("path          ", Counter(r["path"] for r in rows))
print("error_status  ", Counter(r["error_status"] for r in rows))
print("stop_reason   ", Counter(r["stop_reason"] or "(empty)" for r in rows))
print("agent ids     ", Counter(r["agent_id"] or "(main)" for r in rows))
blank = [r for r in rows if not r["input_tokens"] and r["error_status"] == "ok"]
print(f"\nsuccessful rows with no input_tokens: {len(blank)}")
for r in blank:
    print(f"   {r['backend']:10} stream={r['stream']:5} {r['response_bytes']:>8} bytes")
print("\ncloud cache reads:", [
    (r["cache_read_input_tokens"], r["cache_creation_input_tokens"])
    for r in rows if r["backend"] == "anthropic"
])
PY
```

What each answer means:

| Look at | Expected | If not |
|---|---|---|
| `backend` | both `anthropic` and `lmstudio` present | the session never actually switched; the mixed-model claim is untested |
| **successful rows with no `input_tokens`** | **zero** | the scanner missed. `stream=true` means the SSE path failed, `stream=false` the buffered one — that is what the column is for |
| Anthropic rows' `input_tokens` | non-empty | **the most important check in this step.** The `message_start`-only rule was verified against LM Studio and taken from Anthropic's *documentation*. Empty here means the trap was sprung in reverse |
| `agent_id` | at least one non-`(main)` value | the header does not arrive, and an empty `agent_id` cannot be read as "main conversation". Say so in `CLAUDE.md` rather than leaving the column's meaning assumed |
| `error_status` | one `client_disconnect` after the Esc | starlette does not reach that branch; find what it raises instead and widen the `except` |
| cloud `cache_read_input_tokens` | rising after turn one | byte-relay is broken somewhere, which is the expensive failure the whole design exists to prevent |
| `path` | anything besides `/v1/messages` | not a fault — it is the answer to the standing "other endpoints" question. Write down whatever appears |
| `stop_reason` | mostly `end_turn` | `max_tokens` on the local model is the silent truncation the 34304-token question predicted |

Also confirm `logs/telemetry/router.log` carries uvicorn's startup and access lines
*interleaved with* the router's own per-call lines. That interleaving is the point of decision 5 in
`phase-2-notes.md`; if uvicorn's lines are missing, `log_config=None` and the handler attachment
have come apart.

Finally, check rotation once with real data rather than fixtures: set `stats.max_bytes` to something
small like `4096`, run a few turns, and confirm each `calls.csv.N` still starts with a header row.

## Results

**2026-07-29 — Phase 1's "done when" met.** Reported by the repository owner after running the above.

| | |
|---|---|
| Cloud | `claude-sonnet-5` through the router — works as a normal session |
| Local | `google/gemma-4-e4b` in LM Studio, context length 34304 tokens |
| Streaming | Confirmed in the curl smoke test: words arrived in separate blocks, not one lump |
| Multi-turn | Works |
| Tools | Writes and reads files, runs bash commands, runs a Python script and reads its stdout |

This is the result the whole design rests on. Both sides of the router speak the same protocol, no
translation layer exists anywhere in the code, and a locally served model nonetheless drives a real
coding session with working tool calls. The largest open question about LM Studio — whether tool
calls survive the round trip — is answered.

**One thing to watch.** 34304 tokens of context is only about 4k above the ~30k fixed preamble
measured from the captured request, and the session worked anyway. That is less headroom than the
estimate says a working session needs, so either the estimate is pessimistic for this tokenizer or
something is trimming context quietly. Phase 4 should settle it: silent truncation would degrade
answers without ever failing visibly.

**Still not covered here.** LM Studio's handling of the awkward cases — a `role: "system"` message
inside `messages`, `thinking` blocks, images — and whether it reports `usage` at all. That last one
decides whether half of Phase 2's CSV columns can be filled for local calls. All of it is Phase 4.
