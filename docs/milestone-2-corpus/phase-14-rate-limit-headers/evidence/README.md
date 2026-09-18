# Phase 14 — evidence

**One entry per artefact**, per `../../../README.md`'s "Evidence and redaction": what produced it,
what it proves, what was redacted and how, and whether it can be regenerated.

***Nine artefacts: three instruments that can be re-run, and six records of runs that cannot.*** All
six were produced on **2026-09-18**, by the owner, against **Claude Code 2.1.267** and router
`0.1.0`, on an OAuth subscription credential with `credential: forward`.

---

## The instruments

### `mutation-check.py`

**What it is.** **Twenty-four deliberate defects**, each paired with the test that has to die when
it is introduced. `python3 docs/milestone-2-corpus/phase-14-rate-limit-headers/evidence/mutation-check.py`
from the worktree root; exits 0 when every mutation is caught.

***It reports "mutation applied" and "check failed" as two separate lines.*** *Phase 13's harness
silently never applied its mutations, which is indistinguishable from a clean pass — so a mutation
whose anchor does not match **exactly once** is reported as a **failure of the script**, never as a
pass of the test set.* **That design fired three times in this phase**, twice on anchors that went
stale when the code under them moved, and once on a string that came to exist in two functions.

**What it cannot tell apart, and says so in its own docstring:** *"the test is vacuous"* and *"the
mutation did not do what it claimed"*. **A surviving mutation is a prompt to read the mutation
first and the test second.**

### `clienthello-capture.py`

**What it is.** A socket that accepts one connection, reads the TLS `ClientHello`, parses its cipher
suites, extensions and supported groups, and prints a JA3 hash. *A `ClientHello` is **plaintext**
and arrives **before** certificate validation, so a listener **with no certificate at all** sees the
client and the client then fails.*

**Why it is worth keeping.** **No credential, no API call, nothing installed**, and it answers
"which TLS stack is this?" about any client that can be pointed at a URL.

    python3 clienthello-capture.py <port> <label>     # then point the client at https://127.0.0.1:<port>

### `boringssl-forwarder.py`

**What it is.** A one-hop forwarder whose outbound TLS is **BoringSSL's rather than OpenSSL's**,
via `curl_cffi` with `impersonate="chrome"`:

    Claude Code -> router -> http://127.0.0.1:<port> (this) -> TLS(chrome) -> api.anthropic.com

**`make forwarder`**, with `config-boringssl.yaml` and `make run-boringssl` on the router side.
**`curl_cffi` is in its own `experiment` dependency group** — not installed by `uv sync`, not pulled
in by `uv run`, and imported by nothing under `src/`.

***It streams, and that was verified rather than assumed*** — against a local SSE origin with
**no Anthropic traffic**, five events 0.4 s apart arrived at `+0.07 +0.46 +0.87 +1.27 +1.67`.
*`FORWARDER_UPSTREAM` exists for that test.* **A forwarder that buffered would break every streamed
call and turn `ttfb_ms` into a measurement of itself.**

---

## The records, in the order they were taken

### `rate-limit-headers-2026-09-18.txt` — 11:02–11:05 UTC

**What produced it.** One driven Claude Code session through the router, auto mode on. *Group C is
not a session's to run.*

**What it proves.** **Twelve `429`s, every one carrying `request-id` and nothing else.** No
`retry-after`, no `anthropic-ratelimit-*` header of any kind — **not even an unlisted one**, which
would have rendered as `<unlisted>`.

**Redaction.** None; the lines are verbatim. *`request-id` values are Anthropic's own correlation
ids, carry no credential, and are **the thing an upstream report needs**.*

**Regenerable?** No — a record of one session. The instrument that made it is re-runnable.

### `calls-2026-09-18-redacted.csv` — the same session, complete

**What it proves.** `BUG-001` reproduces on current versions. **22 rows**, 11:02:33 to 11:05:45:
**12 non-streamed `/v1/messages` all `429`, 8 streamed all `ok`**, and 2 `/api/hello`. *The retry
signature the bug predicts is visible* — five attempts at `claude-sonnet-5` and 128,250 bytes, then
five at `claude-opus-5` and **128,248**, *a two-byte difference which is exactly the model-name
length difference.*

**Redaction, and how.** `session_id` only — **2 distinct values**, mapped to `session-01` and
`session-02` in order of first appearance. **Nothing else altered.** *Verified after redaction: 22
rows present, all 12 `429`s present.*

**Regenerable?** No. Same session as above.

### `rate-limit-headers-success-control-2026-09-18.txt` — 11:19 UTC

**What produced it.** A second run, after the reply sampler was added. *One successful call was
enough.*

**What it proves, and it is the control the first record could not supply.** **A successful reply
carries twelve `anthropic-ratelimit-unified-*` headers where the `429`s carried none.** *So
Anthropic does meter this credential and does report the meter — and said `rate_limit_error` while
reporting nothing.*

***And it proves the allowlist was wrong.*** **All twelve arrived as `<unlisted>`**: not one of the
documented API-key bucket names reaches an OAuth subscription credential. *Without the prefix catch
this line would have read `request-id=…` alone, and the conclusion drawn from it would have been the
opposite of the truth.*

**Redaction.** None. **Names only, no values** — the sampler had not yet been taught these names.

**Regenerable?** No.

### `unified-meter-values-2026-09-18.txt` — 12:13 UTC

**What produced it.** A third run, with the twelve names added to the allowlist.

**What it proves.** The meter's **values**, on a `200` taken **twenty-two seconds before five
rejections on the same connection**: `unified-status=allowed`, `5h-utilization=0.52`,
`7d-utilization=0.59`, every bucket `allowed`. ***So the 429 is not quota exhaustion, measured
rather than argued.*** *The five rejections that followed are in the same file.*

*`overage-status=rejected` with `org_level_disabled_until` is present and **deliberately not leaned
on** — utilization is nowhere near a limit, so nothing connects it to a rejection. It is recorded
because it is the only value in the set that reads like a refusal.*

**Redaction.** None. **`anthropic-ratelimit-unified-representative-claim` appears as `<unlisted>` by
design, not by redaction** — its name is not the vocabulary of counters and nobody has established
what it holds, so it is reported by name and its value is never written.

**Regenerable?** No.

### `arriving-request-headers-2026-09-18.txt` — 12:40 UTC

**What produced it.** A fourth run, with the arriving-request sampler. **This is the byte capture's
cheap half** — the router receives exactly what Claude Code sends it.

**What it proves, in two halves.** The two request shapes are **byte-identical except
`anthropic-beta`** — 9 entries on the non-streamed request, 13 on the streamed one. **And the router
forwards all of it unchanged**: *computed rather than measured, by feeding the captured list through
`outgoing_headers()` and `httpx.build_request()`* — **nothing dropped, nothing added**, with `host`
and `content-length` correctly re-derived.

**Redaction.** None needed **by construction**: seven header names are allowlisted for their values
and **everything else prints `<unlisted>`**, `authorization` and `x-api-key` included. *A name
cannot carry a credential.*

**Regenerable?** No.

### `tls-clienthello-2026-09-18.txt`

**What produced it.** `clienthello-capture.py`, twice — once for the router's own client, once for
the `claude` binary. **No Anthropic traffic and no credential.**

**What it proves.** **The two stacks are trivially distinguishable before a byte of HTTP is read.**
Eight of seventeen cipher suites differ and the shared ones are offered in a different order; Python
sends `encrypt_then_mac` and Claude Code does not; Claude Code sends `status_request` and `SCT` and
Python does not; Python offers eight supported groups against four.

*The file names its own inference: the shape is **BoringSSL**-like rather than OpenSSL-like, and a
compiled single-file binary is consistent with a Bun build. **The measured fact is only that the two
hellos differ.***

**Regenerable?** **Yes** — re-run the instrument. *The values will move with the client version and
the Python build, which is the point of keeping the tool beside the record.*

---

## What this evidence establishes, and what it does not

***Together these six records eliminate eleven hypotheses*** — `accept-encoding`, HTTP/2, a dropped
header, an added header, the `anthropic-beta` list, the withheld attribution headers, quota
exhaustion, request size, the model, the router inventing the rejection, and a non-browser TLS
fingerprint.

***They do not identify the cause, and nothing here should be read as though they do.***

**Two things remain untested:** an **exact-fingerprint allowlist**, which only Bun's own build could
match and perhaps not even that; and **connection reuse**, which nothing in this phase has touched.

*This section replaced one that said the success control was unmeasured. **It was true when written
and false within the hour** — the control ran at 11:19 and its record is the third entry above.*
