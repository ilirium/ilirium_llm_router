# EPD-003 — Capturing bodies for a corpus

**Status: proposal. Written 2026-07-31. No decision is taken here.** Nothing in this document is
implemented. Unlike EPD-001 and EPD-002 it does not wait on Phase 4 — it waits on a decision the
repository owner has to take first, about what the corpus is *for*. See "The fine-tuning half runs
into the terms" below; that question changes the design, not merely its priority.

## The requirement this document is about

Stated on 2026-07-31, before Phase 3 began:

> Save all requests and all responses to/from models for later analysis, and maybe use this corpus
> as a dataset for fine-tuning.

With a question attached: **is a text file bad, and is special storage needed?**

The short answer is that text files are not the problem and a database is not the fix. The problem
is that the corpus is almost entirely the same bytes over and over, and the fix is a compressor with
a large enough window. That is one flag, not an architecture. The measurements are below.

## What this reverses, and what it does not

This matters more than the storage format, because the project has an explicit rule about bodies and
this proposal is adjacent to it.

**Not reversed.** `../reference/design-decisions.md`, "Relay the body, log only metadata":
*"Forward the request body byte-for-byte … never deserialize or re-serialize the payload."* Storing
an opaque copy of bytes that already exist in memory is not deserialization. It is the same
discipline the response tee already follows — watch, copy, never touch. The rule that protects
prompt-cache prefixes is untouched, because nothing here changes what gets forwarded.

**Reversed, deliberately, and this is the thing to agree to.** `../reference/observability.md`:

> Same for anything body-shaped — no prompts, no message counts, no tool names. Those are steps
> toward parsing what the router promised only to relay.

That sentence was written about the *CSV*, and its reasoning holds for the CSV: a column named
`tool_names` is parsing. But the requirement above is precisely a request for the body-shaped data
that sentence rules out. So this is a genuine change of scope, not a loophole — the router stops
being a thing that only measures calls and becomes a thing that also archives them.

The narrow version worth defending: **store bytes, parse never.** The corpus holds opaque blobs; any
parsing happens offline, in an export step, against a file — never on the request path, never in the
router process. That keeps the reversal to one sentence rather than to the whole rule.

## How much data this actually is

From `../milestone-1-core/phase-2-observability/evidence/step-6-session/calls.csv` — 142 calls,
2026-07-31, 08:21:15 to 09:38:12 UTC, **77 minutes** of real work across eleven sessions. The CSV
does not hold bodies, but it holds their lengths, so the corpus that *would* have been captured is
exactly known:

| Backend | Path | Calls | Request bytes | Response bytes |
|---|---|---:|---:|---:|
| anthropic | `/v1/messages` | 41 | 5.19 MB | 0.274 MB |
| anthropic | `/v1/messages/count_tokens` | 1 | 0.05 MB | 0.000 MB |
| lmstudio | `/v1/messages` | 68 | 4.12 MB | 0.451 MB |
| lmstudio | `/v1/messages/count_tokens` | 32 | 0.26 MB | 0.003 MB |
| **total** | | **142** | **9.62 MB** | **0.727 MB** |

**10.35 MB for 77 minutes**, or about **8 MB an hour** of active use. At an hour a day that is
roughly **3 GB a year** stored naively.

Three things in that table shape everything below.

**Requests are 93% of the volume.** Median request 20.5 KB, max 203.2 KB. Median *response* is
0.3 KB. The corpus is overwhelmingly made of things sent, not things received — which is the
opposite of the intuition that a reply is the interesting part.

**The reason is that every request re-sends the whole conversation.** An N-turn session sends the
preamble N times and turn *k*'s text N−*k* times. Storage is O(N²) in turns while the actual
transcript is O(N). The largest single session here accounts for 4.95 MB of the 10.35 MB on its own.

**A third of the calls are `count_tokens`**, and 32 of those 33 are answered by LM Studio with an
85-byte error body (EPD-002). 0.31 MB of request bodies whose replies contain nothing. Whatever gets
captured, this is a category worth being able to exclude.

## Text files are not the problem — the compressor's window is

The instinct that a plain text file is the wrong answer is right, but for a reason worth measuring
rather than assuming. Here is the measurement.

**Control, on one body.** The real captured request, `../captures/log-the-whole-request.txt`,
119,018 bytes:

```
gzip -9    41,054  (2.9x)
xz         37,404  (3.2x)
zstd -19   38,000  (3.1x)
```

All three agree. On a single body there is nothing to choose between them.

**The same compressors, on twenty growing bodies.** Built the way Claude Code actually builds them:
the real capture, with one more user/assistant pair appended per turn — 5,056,469 bytes in total.
The script is in "Evidence" below and takes a few seconds to re-run.

```
raw       5,056,469   1.0x
gzip -6   2,105,279   2.4x
gzip -9   2,103,468   2.4x
zstd -3     176,743  28.6x
zstd -19    161,305  31.3x
```

**gzip gets *worse* across many bodies than it did on one; zstd gets ten times better.** That is not
a tuning difference and it is not about compression levels — `-6` and `-9` are within 0.1% of each
other. It is the match window. gzip's window is **32 KB**, so when the second 119 KB body arrives,
gzip can no longer see the first one's copy of the identical preamble. zstd's default window at
level 3 is megabytes, so from the second body onward almost everything is a back-reference.

The control is what makes this conclusive: within one body the two are 2.9× and 3.1×, essentially
tied. Across twenty, they are 2.4× and 28.6×. **The entire 12× gap is cross-request redundancy** —
exactly the redundancy this corpus is made of.

Two honest caveats on the 28.6×. The appended turns are random dictionary words, which compress
poorly *within themselves*, so the figure understates what real prose would achieve on the new
content and overstates the fraction of the file that is genuinely new. And the ratio depends
entirely on how much fresh content a session produces; a session of many short turns will do better
than this, a session that pastes large distinct files will do worse. The **direction** is robust; the
number is one measurement.

Applied to the projection: 3 GB a year naive becomes somewhere in the low hundreds of megabytes.
**Neither figure justifies special storage infrastructure.**

## So what does "special storage" mean here

The question splits into three that get answered separately, and conflating them is what makes this
look like it needs a database.

| Question | What it actually needs |
|---|---|
| **Write path** — how does a 200 KB blob leave the request without slowing it? | An off-thread queue and a drop policy |
| **Deduplication** — how do identical preambles stop being stored 40 times? | Content addressing, or a large compression window, or both |
| **Query and export** — how does a corpus become a dataset? | An offline step over files. Not the router's problem |

Only the second is about storage format at all, and it has a cheap answer.

## What comparable tools do

Checked 2026-07-31. Two tiers, and they answer differently.

**The local tier** — [`llm.log`](https://github.com/lanesket/llm.log),
[`llm_intercept`](https://github.com/mlech26l/llm_intercept), Datasette's
[`llm`](https://llm.datasette.io/en/stable/logging.html) — all use **SQLite** as the capture store,
bodies inline. Notably, `llm.log` ships a **prune** command specifically to delete old bodies while
keeping the metadata, which is a direct admission that bodies grow unbounded and metadata does not.
`llm_intercept` exports to **JSONL.zstd or Parquet** for ML pipelines. None of them deduplicate.

**The hosted tier** — [Langfuse](https://langfuse.com/self-hosting/deployment/infrastructure/blobstorage)
and [Helicone](https://www.helicone.ai/blog/self-hosting-journey) — both land raw payloads in **S3
or S3-compatible blob storage first**, and only then process into a queryable database (ClickHouse
in both cases). Langfuse is explicit that writing to blob storage before the database is what makes
ingestion survive a database outage. [LiteLLM](https://docs.litellm.ai/docs/proxy/logging) does not
store payloads itself at all: it fires callbacks and lets Langfuse, Helicone, or an S3 bucket own the
problem.

The consensus shape, across both tiers: **a cheap append-only store for the bytes, a separate index
for the metadata, and a separate offline format for the dataset.** Nobody puts all three in one
place. This repository already has the middle one — `calls.csv` is an index of every call with the
session, agent, model, backend, status, and timing already on it.

## Sketch of a proposal

Not a design, and deliberately short. The point is to show that the pieces the project already has
do most of the work.

**Content-addressed blobs, compressed individually, indexed by the existing CSV.**

- Hash each body; write it once as `bodies/<sha256>.zst`. Identical bodies — the 85-byte
  `count_tokens` error appears 32 times in one session — collapse for free, without needing a shared
  compression window across files.
- Add two columns to `calls.csv`: `request_body_ref` and `response_body_ref`, holding the hash or
  empty when nothing was stored. The CSV becomes the join table it already almost is.
- Export to JSONL or Parquet as an offline command over the store, never on the request path.

**The known weakness, stated up front.** Content addressing catches *identical* bodies. It does not
catch the dominant case, which is bodies that share a 100 KB prefix and differ in the tail — each
one hashes differently and is stored whole. Per-file zstd then only gets the ~3× a single body
allows, not the 28× measured across bodies. Recovering that needs either a **shared zstd dictionary**
trained on the preamble, or storing per-session rather than per-call in one long-window stream. Both
are real options; neither is chosen here, and the difference between them is perhaps 3× against 28×
on 93% of the corpus, so it is the one part of this worth measuring properly before building.

**What is deliberately *not* proposed:** a database, a schema for message content, an ingestion
service, or anything that parses a body inside the router process.

## The fine-tuning half runs into the terms

This is the finding that could change the goal, so it is not buried at the bottom.

Anthropic's published position on using outputs to train models
([support article](https://support.claude.com/en/articles/12326764-can-i-use-my-outputs-to-train-an-ai-model),
read 2026-07-31) permits narrow, non-competing uses — classifiers, categorization, summarization
tools, integrating outputs into applications — and explicitly prohibits *"using Outputs as training
targets for models"*, *"general purpose chatbots"*, and *"models designed for open-ended text
generation"*. The umbrella term is that customers may not use the service *"to train or develop AI
models without our written permission"*. The article does not distinguish consumer subscription use
from commercial API use.

A corpus captured from this router is **mixed**. In the session above, 41 of 109 `/v1/messages` calls
went to Anthropic and 68 to LM Studio. Fine-tuning a local coding model on the Anthropic half is
close to the centre of what that article rules out. The LM Studio half is the machine's own model
answering, and is not Anthropic's to restrict.

Three consequences:

1. **The analysis goal is unaffected.** Nothing above restricts keeping bodies to understand what
   the router carries, debug parity, or measure prefix cache behaviour. That is the stronger half of
   the requirement anyway.
2. **If fine-tuning stays a goal, the corpus wants a partition by backend from day one** — which is
   nearly free, since `backend` is already a CSV column and would be part of any export filter.
   Retrofitting a provenance split into an undifferentiated pile is much worse.
3. **This is a decision for the repository owner, not a design question.** It is stated here so it is
   taken deliberately rather than discovered after the corpus exists.

## Constraints this inherits from the router

Six, all from properties the project already established. They are why this is not simply "write the
bytes to a file".

**Telemetry must never break a call.** `observe.py` catches everything on principle. A CSV row is a
few hundred bytes and writes in microseconds; a 203 KB blob does not. This needs an off-thread queue
with a **bounded** size and an explicit answer to what happens when it fills. The answer has to be
*drop the body and record that it was dropped* — a corpus with a known hole is fine, a stalled
request is not.

**There is already a ceiling, and it was reasoned about.** `observe.py:50` sets
`MAX_SCAN_BYTES = 1 MiB` with the justification that the catch-all forwards paths nobody enumerated,
so a reply could be any size at all. A body store faces exactly that question again, and should reuse
the reasoning rather than invent a new number.

**Partial bodies are the interesting rows, not the broken ones.** The step 6 session produced six
`client_disconnect` rows and the Phase 3 work list adds `stream_error`. In those cases the bytes that
arrived before the failure are precisely what an analysis wants. The store must be able to hold a
truncated body and say that it is truncated.

**Rotation and completion order already have decided answers.** `calls.csv` is size-rotated and is in
*completion* order, deliberately — `CLAUDE.md` explains why ordering it would mean losing buffered
rows on shutdown. Anything keyed to the CSV inherits both: refs must survive rotation, and an export
must sort rather than assume.

**Streamed responses raise a format question the CSV never had to answer.** A streamed reply is SSE
frames; a non-streamed one is a JSON object. Storing raw bytes preserves fidelity and matches the
project's instincts, but means every consumer re-parses SSE. Storing a reassembled body is more
useful and is exactly the reserialization the project avoids elsewhere. **Store raw** is the answer
consistent with everything else here, with reassembly as an export-time concern — but it is a real
choice and should be made out loud.

**The repository's handling posture changes.** `calls.csv` holds no content, which is why the step 6
session could be frozen into `docs/` after mapping identifiers to placeholders. Bodies hold source
code, file contents, whatever a tool read, and anything the user typed — including a `.env` if an
agent ever reads one. A body store is **not** committable, not by redaction and not by placeholder
mapping. It needs its own gitignore entry, and it means the answer to "can I share this session"
stops being yes by default.

## The tempting shortcut, and why it probably fails

Worth writing down because it is the first idea anyone has, and it would cut the corpus by ~95%.

Request *N+1* contains turn *N*'s assistant reply, because that is how conversation history works. So
in principle the **last request of a session is a near-complete transcript**, and storing one body
per session plus the final response would reconstruct everything at a fraction of the size.

It probably does not hold, for three reasons, in descending order of confidence:

1. **Context compaction rewrites history.** Claude Code summarizes and replaces earlier turns when it
   approaches the window. After a compaction the last request is not a superset of the earlier ones —
   the original text is gone. EPD-002 establishes that compaction fires against an assumed 200k
   window on local models, so on a small-context model it may fire often.
2. **There is no session-end signal.** The router sees requests, not endings. "The last request of a
   session" is only knowable in retrospect, which means buffering the previous one indefinitely
   against a session that may never return.
3. **Subagents and interruptions branch.** A subagent has its own message tree, and the step 6
   session contained an interrupted response. Neither appears in the main conversation's final
   request.

Reason 1 is the fatal one and it is **unverified against this router** — it comes from how compaction
is documented to work, not from anything observed here. It is cheap to check (see below), and if it
turned out that compaction were rare in practice, a hybrid — full capture, with a periodic prune down
to session-final bodies — would become attractive.

## Documented versus measured

| Claim | Status |
|---|---|
| 142 calls over 77 minutes would have produced 10.35 MB of bodies | **Measured** — summed from `../milestone-1-core/phase-2-observability/evidence/step-6-session/calls.csv` |
| Requests are 93% of the volume; median request 20.5 KB, median response 0.3 KB | **Measured** — same file |
| gzip achieves 2.4× and zstd 28.6× across twenty growing bodies | **Measured** — reproducible script, see Evidence |
| Within one body the two are within 7% of each other (2.9× / 3.1×) | **Measured** — same script's control |
| The gap is caused by gzip's 32 KB window | **Inferred strongly** — the control isolates it to cross-body matching, and the window size is a documented property of DEFLATE |
| The 28.6× figure transfers to a real corpus | **Unmeasured.** The tail content is synthetic; only the direction is established |
| ~8 MB/hour, ~3 GB/year naive at an hour a day | **Extrapolated** from one 77-minute session. One session is not a usage pattern |
| Identical bodies recur often enough for content addressing to pay | **Inferred weakly** — 32 identical 85-byte `count_tokens` errors is a real but tiny case. The dominant case is shared *prefixes*, which content addressing does not catch |
| A shared zstd dictionary would recover the cross-body ratio for per-file storage | **Unmeasured hypothesis.** This is the load-bearing one for the sketch above |
| Anthropic prohibits using outputs as training targets | **Documented** — quoted from the support article, read 2026-07-31 |
| Langfuse and Helicone store raw payloads in blob storage before the database | **Documented only** — vendor documentation, not verified by running either |
| Context compaction breaks the last-request-is-the-transcript shortcut | **Documented only**, and never observed on this router |
| Bodies would contain secrets a `.env` read would expose | **Inferred**, obviously, but never demonstrated — no body has ever been stored here |

## The cheapest next step

Two measurements, roughly twenty minutes, no router code. Do them in this order; the first is the
gate.

**1. Does a shared dictionary recover the ratio?** Capture bodies from one short real session by any
throwaway means — a few lines in `proxy.py` on a scratch branch, or `mitmproxy` in front of the
router. Then compare, on those real bodies: per-file zstd; per-file zstd with a dictionary trained by
`zstd --train` on the session; and one long-window stream over the concatenation. If the dictionary
lands near the stream figure, the sketch above works as written. If it lands near the 3× per-file
figure, then per-call files are the wrong unit and the design should be per-session streams instead —
which changes everything downstream, including how a partial body is stored.

**2. Does compaction actually destroy history?** Run one local session long enough to trigger
auto-compaction and keep the captured requests. Diff the last request against an earlier one. This
converts the shortcut above from "probably fails" to a fact either way, and it happens to be the same
session EPD-002's step 1 asks for — worth running once and using for both.

## Open questions

1. **Is fine-tuning still a goal, given the terms?** Everything else is downstream of this. If the
   answer is "analysis only", the design gets simpler and the Anthropic/LM Studio partition becomes
   optional rather than structural.
2. **Per-call files or per-session streams?** Measurement 1 decides it. Per-session is far better on
   size and far worse on everything else — random access, partial writes, a process that stops
   mid-session.
3. **What is captured by default?** Everything, or `/v1/messages` only? The 32 `count_tokens`
   non-answers are pure noise, but excluding by path means the catch-all's genuinely unexpected
   traffic — the thing the `path` column exists to surface — gets excluded too.
4. **Is capture on by default, or opt-in?** The CSV is always on because it is cheap and holds
   nothing sensitive. Neither is true here.
5. **Retention.** `llm.log` grew a prune command for a reason. Size-based like the existing rotation,
   age-based, or never — and if never, does that survive the first 10 GB?
6. **Does the corpus store request *headers*?** They carry `anthropic-beta`, the session and agent
   IDs, and the credential. Interesting for analysis, and the credential makes it the single most
   sensitive thing the router touches. Currently the router tees bodies only, which is also why the
   `anthropic-ratelimit-*` question in `../milestone-1-core/closing-notes.md` is still open.
7. **Does this land before or after Phase 3?** Phase 3 adds `stream_error` and firms up
   `client_disconnect`, and both change what a partial body means. Building capture first means
   revisiting it.

## Evidence

**Measured on this machine, 2026-07-31.** Volume figures are summed from
`../milestone-1-core/phase-2-observability/evidence/step-6-session/calls.csv` — 142 rows,
identifiers mapped to stable placeholders; see that directory's `README.md`. `logs/` is gitignored
and rotates, so the frozen copy is the citable source.

The compression figures come from this script, **run from the repository root** against the real
119 KB capture — `docs/captures/log-the-whole-request.txt` from there, `../captures/…` from here —
with `zstd` 1.5.x from Homebrew:

```python
import gzip, json, pathlib, random, subprocess
random.seed(1)
WORDS = open("/usr/share/dict/words").read().split()
turn = lambda n: " ".join(random.choices(WORDS, k=n))

base = pathlib.Path("docs/captures/log-the-whole-request.txt").read_bytes().rstrip(b"\n")
bodies, tail = [], ""
for _ in range(20):                      # twenty turns of a growing conversation
    tail += json.dumps({"role": "user", "content": turn(300)})
    tail += json.dumps({"role": "assistant", "content": turn(900)})
    bodies.append(base + tail.encode() + b"\n")

blob = b"".join(bodies)
pathlib.Path("/tmp/bodies.bin").write_bytes(blob)
print(f"raw      {len(blob):9,}")
for lvl in (6, 9):
    n = len(gzip.compress(blob, lvl));  print(f"gzip -{lvl}  {n:9,}  {len(blob)/n:.1f}x")
for lvl in (3, 19):
    n = len(subprocess.run(["zstd","-q",f"-{lvl}","-c","/tmp/bodies.bin"],
                           capture_output=True).stdout)
    print(f"zstd -{lvl}  {n:9,}  {len(blob)/n:.1f}x")
```

Replace the loop body with the single capture to reproduce the control.

**Documentation, all read 2026-07-31.**

- Anthropic on using outputs to train models —
  <https://support.claude.com/en/articles/12326764-can-i-use-my-outputs-to-train-an-ai-model>
- Langfuse blob storage —
  <https://langfuse.com/self-hosting/deployment/infrastructure/blobstorage>
- Helicone's storage split across S3, Kafka and ClickHouse —
  <https://www.helicone.ai/blog/self-hosting-journey>
- LiteLLM logging callbacks — <https://docs.litellm.ai/docs/proxy/logging>
- `llm_intercept` (SQLite capture, JSONL.zstd / Parquet export) —
  <https://github.com/mlech26l/llm_intercept>
- `llm.log` (SQLite capture, prune command) — <https://github.com/lanesket/llm.log>
- Datasette `llm` logging to SQLite — <https://llm.datasette.io/en/stable/logging.html>
- Letta's Trajectory format, for what a *consumer* of this corpus wants: harness bookkeeping
  stripped, 5.6× token reduction against native formats —
  <https://www.letta.com/blog/trajectory/>

**Related.** `EPD-000-about-these-documents.md` for the conventions; `EPD-001` for the `session_id`
and `agent_id` columns this depends on; `EPD-002` for the argument that the byte-fidelity rule is
narrower than it looks, and for the `count_tokens` rows this would otherwise capture; `CLAUDE.md`
"Observability" for the sentence this proposal reverses and "Design decisions" for the one it does
not.
