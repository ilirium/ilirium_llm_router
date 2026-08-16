# Phase 4 evidence — the four measurements that cannot be taken again

**Frozen. Do not regenerate.** These are the sources behind numbers quoted in `../notes.md`,
`../../../../CLAUDE.md`, `../../implementation-plan.md` and `../../../epd/EPD-002-token-counting-for-local-backends.md`.

## Why this exists when `../../../procedures/lmstudio-capability-probes/runs/` is gitignored

That rule was written on the assumption that Phase 4's probes are a tool like
`../../../procedures/dying-backend/`, whose runs are disposable because the failures reproduce on demand — the
dying backend always dies. **Four of Phase 4's results do not reproduce**, and the rule missed it:

| File | Why it cannot be re-obtained |
|---|---|
| `replay-cold-cache.txt` | `cache_read_input_tokens: 0`, ttfb **196789 ms**. Re-running now hits a warm cache. Getting this back means evicting LM Studio's prefix cache first |
| `replay-warm-cache.txt` | `cache_read_input_tokens: 27904` of 27924, ttfb **49629 ms**. Meaningless without the cold run above — the pair is the measurement, not either half |
| `needle-over-window.txt` | LM Studio's verbatim refusal when input exceeds the loaded window. Needs a window smaller than the request, and the context length **cannot be set from the CLI** — `lms load -c` is silently ignored, so reproducing this needs a person in the GUI |
| `needle-read-timeout.txt` | The router's 600 s read timeout firing on a healthy backend. Costs ten minutes of prefill per attempt and depends on the machine being about this fast |

Each probe also **overwrites its own transcript** in `runs/`, so the second replay destroyed the
first one's and the third needle run destroyed the other two. By the end of the session the cold-cache
and over-window transcripts existed nowhere but a scratch directory.

`replay-warm-cache-full-stream.txt` is the one complete transcript kept — request body and every SSE
event of a real Claude Code request answered by a local model, including the `thinking` block and the
`text` block. The other four files are `probe.py`'s reports, which carry every number quoted
elsewhere.

## What is in them

The replay is `../../../captures/log-the-whole-request.txt` with only the model name changed: 27 tool schemas, a
`role: "system"` message inside `messages`, two `cache_control` markers, `context_management`,
`output_config`, `metadata.user_id` and `thinking`, against `qwen/qwen3.5-9b` loaded at 44544 tokens.

## Redaction

**None was needed, and that was checked rather than assumed.** The bodies here are the already-redacted
capture — `REDACTED-EMAIL` and friends survive intact — and `probe.py` writes only the request body
and the reply, never the request headers, so the `Authorization: Bearer` line never reaches these
files.

A grep for `sk-ant`, `Bearer `, `oat01` and `authorization` matches twice in
`replay-warm-cache-full-stream.txt`, and both are **false positives**: they are Claude Code's own
system-prompt text about authorization scope for security work, which is already committed verbatim
in `../../../captures/log-the-whole-request.txt`. No credential is present.

## The lesson, since this is the second time

Phase 2 froze its session for exactly this reason and said so: *"without this directory the numbers
quoted in EPD-002 would have no source."* Phase 4 then wrote a gitignore rule that would have thrown
the equivalent away, because the directory looked like Phase 3's tool rather than Phase 2's evidence.
It is both. **The test is not "is this a tool or evidence" but "does re-running produce the same
number".** Where it does, keep the tool. Where it does not, keep the output.
