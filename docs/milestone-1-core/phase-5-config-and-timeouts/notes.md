# Phase 5 notes — the credential shape and the read timeout

Findings as they are made. The plan is `phase-5-plan.md`; the survey that picked these two items out
of everything left is `outstanding-work.md`.

## Item 1 — the credential shape, done 2026-08-07

Transcription of a decision taken 2026-07-29, so there is little to report beyond it being done. 152
tests, up from 147.

**The shape.** `credential` is now the only knob — `forward`, `strip`, `inject` — and it is the only
thing `outgoing_headers` consults. `api_key_env` is required by `inject` and forbidden by the other
two.

**Where the old ambiguity actually lived, which was three places rather than one.** The known one was
`proxy.py`, where `if api_key is not None or backend.credential == "strip"` let a configured key win
over the declared mode. Writing it up turned out to need the same fix in two more:

- `config.py`'s `api_keys()` collected a key for any backend naming a variable, regardless of mode.
- `cli.py`'s `_credential()` printed `key from $VAR` whenever a key existed, so `--check` would have
  *displayed* injection for a backend configured to forward. The display half of the same bug, and
  the half that would have made the real one harder to spot.

All three now key on the mode. The predicate exists once.

**The validator lives on the model, not in `load_config`.** So a `Backend` constructed directly in a
test cannot be put in a contradictory state either — which matters here because the old shape's
`test_a_configured_key_replaces_the_incoming_credential` did exactly that, building
`credential="strip"` with an `api_key_env` and asserting the key was sent. That test was encoding the
ambiguity as intended behaviour. It now builds `credential="inject"` and asserts the same thing.

**One test had to be rewritten rather than added to.** `test_bad_credential_mode_is_rejected` used
`inject` as its example of an invalid mode. It now uses `inherit`.

**Messages, read rather than assumed.** All three refusals were checked by running `make check`
against a config carrying each contradiction, not by asserting on an exception type:

```
backends.lmstudio: Value error, 'credential: inject' needs 'api_key_env' naming the environment
variable that holds the key. Add it, or use 'forward' or 'strip' if this backend needs no key of
its own.

backends.lmstudio: Value error, 'api_key_env' is set but credential is 'strip', so that key would
never be sent. Use 'credential: inject' to send it, or remove 'api_key_env'.

Backend 'lmstudio' has 'credential: inject' and expects its API key in the environment variable
'LMSTUDIO_API_KEY', which is unset or empty.
Set it in your .env file, or switch that backend to 'credential: forward' or 'credential: strip' if
it needs no key of its own.
```

The third existed already; its old wording offered "remove `api_key_env` from that backend", which
was advice from the two-knob world.

**No existing config file breaks.** The only configuration this refuses is one that was already
lying about what it did.

### `inject` has now carried a live request, 2026-08-07

The one part of item 1 that unit tests cannot supply. LM Studio's "Require Authentication" was
switched back on for this — the first time since 2026-07-29 that the setting has been on with the
router pointed at it, and the first time the key path has ever carried real traffic.

Confirmed the setting was actually on before trusting anything: an unauthenticated
`GET /api/v1/models` answered **401** with `invalid_api_key`.

**The test and its control, both against `qwen/qwen3.5-9b` at 44544:**

| Mode | Result |
|---|---|
| `inject` | **HTTP 200**, `input_tokens: 18`, `output_tokens: 3`, the model answered `inject works`, CSV row `ok` |
| `strip` | **HTTP 401**, `authentication_error`, CSV row `http_error` / `401` |

The control is what makes it proof rather than a green light. An `inject` request succeeding could
mean the key was sent, or it could mean authentication was quietly off; the identical request under
`strip` failing at the same moment against the same server rules the second out.

Two details worth keeping. The caller sent `Authorization: Bearer sk-ant-oat01-…`, a
deliberately fake Anthropic token — so the 200 also shows the arriving credential was **replaced**
rather than passed alongside, which is the half of `inject` that `strip` does not test. And the
failing row reads `authentication_error: An LM Studio API token is required…`, which is the Phase 2
recorder fix — keeping the backend's symbolic `error.type` — earning itself on a failure nobody had
produced through the router before.

This also reproduces the Phase 1 finding that started the whole credential decision, from the other
side: back then a forwarded local request came back 401 and the conclusion was that `api_key_env` was
needed. It is now used.

**Authentication was then switched back off**, and the committed `config.yaml` re-checked against it,
so the repository's default matches the machine again. Both modes in one pass:

| Route | Result |
|---|---|
| `qwen/qwen3.5-9b` → lmstudio, `strip` | **200**, `ok`, the model answered `strip works` |
| `claude-sonnet-5` → anthropic, `forward` | **401**, `http_error` — the deliberately fake token reaching Anthropic and being rejected |

The 401 is the interesting half. It is the *expected* answer to a fake token, and getting it means
the credential was forwarded rather than dropped: a stripped request would have failed differently.
So one pass confirms both surviving modes still behave after the plumbing changed underneath them.

## Item 2, step 0 — what `read` actually applies to, measured 2026-08-07

The instrument is `phase-5-measurements/read_timeout_semantics.py`, which drives a backend at three
timing shapes against a deliberately short read timeout. It is committed and meant to be re-run,
because this is a fact about a pinned library that a bump could change.

```
read=2.0s  gap=3.0s  drip every 1.0s for 6.0s

path                elapsed  outcome
/slow-headers         2.01s  ReadTimeout
/slow-first-body      2.01s  ReadTimeout
/drip                 6.01s  completed, 6 chunks
```

**The hypothesis in `phase-5-plan.md` is confirmed, and one of the three candidate fixes does not
exist.** `handoff.md` has listed "a timeout that resets on progress rather than on first byte" as an
option since Phase 4. It is already the behaviour: `/drip` ran for three times the read timeout and
completed, because every chunk restarts the clock. There is nothing to change.

**What `read` really means is the longest permitted silence between two reads.** Both slow paths died
at exactly the timeout, and the pair separates two things worth keeping apart: `/slow-headers` shows
silence before the reply starts is fatal, and `/slow-first-body` shows that receiving *headers* does
not help — the wait for the first body chunk is governed by the same number. That is precisely the
Phase 4 failure. LM Studio prefilling a 41000-token prompt is silent, and silence is the only thing
this timeout measures.

### The consequence the plan did not anticipate

**Phase 3's stated reason for 600 s is weaker than it has been recorded as.** The number was chosen
so a wedged backend fails in bounded time, and `CLAUDE.md`, `handoff.md` and `phase-4-notes.md` all
repeat that. But because the clock restarts on every chunk, **600 s was never a bound on how long a
call can take** — a backend dribbling one byte every 599 s runs forever, and the router waits.

So the property being protected is narrower than "fails in bounded time": it is "fails if it goes
quiet". Raising the number therefore costs less than the record implies. It does not trade away a
guarantee about total duration, because there has never been one. It only lengthens how long a
*silent* backend is tolerated.

This is the third time a Phase 5 item has turned out to have been misdescribed in the notes rather
than mis-built — after the `api_keys()` and `_credential()` copies of the credential ambiguity above.

### What the options actually are, now that there are not three

- **A larger fixed number.** One line. Applies to Anthropic too, where 600 s of silence is already
  far past anything it does — measured median time to first byte was 1426 ms.
- **A per-backend number, configured.** Matches the measured 26× gap in time to first byte between
  the two backends, and puts the knob where the difference is. Today's values become the defaults, so
  nothing changes for a config that does not ask.
- **Separate budgets for the first byte and for going quiet mid-answer.** The genuinely distinct
  option, and it is the *reverse* of what the plan expected: since `read` already resets per chunk,
  the useful split is a **long** first-byte budget with a **short** inter-chunk one — more permissive
  during prefill and stricter mid-stream than today. httpx cannot express it through `read` alone, so
  it needs code in the relay rather than a config field.

## Item 2 — decided and built, 2026-08-07

**Per-backend, configured.** `read_timeout` on each backend, defaulting to 600 so a config written
before the field existed behaves exactly as it did. `config.yaml` sets Anthropic 600 and LM Studio
1800. Only `read` varies; connect, write and pool stay shared, because they are properties of this
machine rather than of the model at the other end — a backend that cannot be *reached* must still
fail fast, and that is the common LM Studio failure. There is a test for that distinction, since
"patient with a thinking model" and "patient with an absent one" are easy to conflate.

157 tests, up from 152.

### Verified against real traffic, in both directions

Unit tests can only show the number reaching the outgoing request object. Two live runs show it
deciding what happens to a real call — the same 135391-byte needle, the same model at 44544, the
same session, differing only in config. Both are frozen in this directory.

| `read_timeout` | Outcome |
|---|---|
| 1800 | **completed** — 41595 input tokens, first byte at 461712 ms, `ok`, codeword returned |
| 30 | **died at 30343 ms** — `transport_error` / `read_timeout`, no first byte, Phase 4's exact signature |

The 30-second run is the more useful instrument of the two. It reproduces the Phase 4 failure shape
exactly, in thirty seconds rather than the ten minutes the original cost, so anything later needing
that failure should lower the config rather than send a bigger request.

### Being honest about what the long run did and did not prove

**It did not reproduce the original failure, and it cannot be claimed to have fixed it.** Phase 4
measured this request being killed at 600247 ms without a first byte ever arriving. This run's first
byte arrived at **461712 ms** — under the old 600 s ceiling. So on this occasion the old setting
would have survived, and the completing run is evidence that the request works, not evidence that
the change was required for it.

**That variance is itself the finding, and it argues for what was built.** The same bytes, the same
model, the same window and the same machine took over 600 s once and 462 s another time — a spread
of at least 30% straddling the old fixed threshold. A single number sitting inside the working range
of ordinary traffic does not fail predictably; it fails when the machine is having a bad day, which
is the worst kind of threshold to hard-code. A configurable one does not have to be guessed right.

Two things are established regardless of the timing: the request completes end to end at a size
Phase 4 never saw finish, and the configured value is what decides — proven by the 30-second run
rather than inferred from the long one.

### The measurement this unblocked, taken: there is no trimming below the boundary

Phase 4 left "whether context is trimmed below the window" open **because the run meant to answer it
hit this timeout**. The same run that verified the fix answers it, because the needle exists for
exactly this: a codeword at the very front, filler in the middle, and a question at the end asking
for the codeword back.

**`ZARDOZ-QUILL-7734` came back**, from a prompt LM Studio counted as **41595 tokens against a 44544
window — 93% full**. Nothing was dropped from the front at 93% occupancy, and `input_tokens` matches
what was sent rather than a trimmed remainder.

So the picture Phase 4 half-drew is complete. At the boundary the request is refused, cleanly and in
under a second. Below the boundary, up to at least 93%, it is answered in full. **LM Studio does not
silently trim**, and the worry standing since Phase 1 is now closed at both ends rather than one.

One caveat, the same one Phase 4 carries: this is `qwen/qwen3.5-9b` at one window size. It is a
statement about this model's server behaviour, not a guarantee about every local model.
