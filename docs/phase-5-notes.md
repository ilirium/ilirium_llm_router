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

**Still outstanding: `inject` has never carried a live request.** That is the one part of item 1 that
unit tests cannot supply, and it is why the plan asks for LM Studio's "Require Authentication" to be
switched back on rather than for more tests.

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

Pending a decision.
