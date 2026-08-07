# Phase 5 plan — the credential shape and the read timeout

Written 2026-08-07, before the phase starts. `implementation-plan.md` says what Phase 5 is for; this
says how it will be run and in what order. `outstanding-work.md` says why these two items and not the
others. Findings go in `phase-5-notes.md` as they are made.

Branch: `feat/phase-5-config-and-timeouts`, off `main` at `74f38d6`. Merge back with `--no-ff`.

This is a **configuration phase**, and the first one since Phase 0 whose output is mostly code. Both
items are small, both change how the router is configured, and both are the kind of change that is
cheap now and expensive once a third backend exists.

The two are grouped for a reason beyond size: **the timeout item is a decision that has to be taken
before it can be written**, and the credential item is a decision already taken that only needs
writing. Doing them together means the phase always has work to do while the harder question settles.

## Item 1 — one `credential` field, three modes

**Decided 2026-07-29.** Nothing about the design is open; this is transcription. The rationale is
under "Design decisions" in `CLAUDE.md` and is not repeated here.

### What is there now

`config.py:41-42` has two independent knobs:

```python
credential: Literal["forward", "strip"]
api_key_env: str | None = None
```

and `proxy.py:348` resolves the ambiguity by letting the key win:

```python
if api_key is not None or backend.credential == "strip":
```

So `credential: forward` alongside a configured `api_key_env` reads as "forward the caller's token"
and silently injects instead. That is the trap being closed.

### What it becomes

| Mode | Meaning | `api_key_env` |
|---|---|---|
| `forward` | pass the caller's credential through untouched | forbidden |
| `strip` | remove it — a local server has no use for a real token and might log it | forbidden |
| `inject` | remove it and send the key named by `api_key_env` instead | **required** |

**The mode is the only thing consulted at request time.** After this change `proxy.py` decides from
`backend.credential` alone and never from whether a key happens to exist, which is what makes the
ambiguity unrepresentable rather than merely discouraged.

### Three startup errors, each naming its fix

Contradictions are refused at startup and the process exits, matching how the rest of config loading
already behaves. Each message says what is wrong *and* what to do.

1. `credential: inject` with no `api_key_env`.
2. `api_key_env` set on a backend whose mode is `forward` or `strip`.
3. The named environment variable unset or empty. This one exists already in `_check_api_keys`
   (`config.py:143`), and its message needs rewording — it currently offers "remove `api_key_env`
   from that backend", which is advice from the two-knob world.

Both new errors are the failures that otherwise surface as a confusing 401 a long way from their
cause: a backend that authenticates with nothing, and a key that looks configured and is never sent.

### The work

- [ ] `config.py` — add `inject` to the literal, and a `model_validator(mode="after")` on `Backend`
      carrying rules 1 and 2. Keep them on the model rather than in `load_config`, so a `Backend`
      built in a test cannot be constructed in a contradictory state either.
- [ ] `config.py` — `api_keys()` currently keys on `if backend.api_key_env`. Key it on
      `credential == "inject"`, so the request path and the startup check agree on one predicate.
- [ ] `config.py` — reword the `_check_api_keys` message for the new shape.
- [ ] `proxy.py` — `outgoing_headers` decides from the mode. Strip the credential headers for `strip`
      and `inject`, append the key for `inject` only, forward untouched otherwise. The `api_key`
      argument stays, but it is no longer what decides.
- [ ] `cli.py:112` — `_credential` prefers `api_key_env` over the mode today, which is the same bug
      in the display. Three explicit strings, one per mode.
- [ ] `config.yaml` — the commented `api_key_env` block under `lmstudio` currently says naming the
      variable is enough. It now takes *two* lines, `credential: inject` and `api_key_env:`. Update
      the comment; it is the instruction somebody will follow when the auth setting goes back on.
- [ ] Tests for the three errors and the three modes' header behaviour.

**No existing config file breaks.** Today's `config.yaml` uses `forward` and `strip` with no key,
which stays valid unchanged. The only configuration this refuses is one that was already lying about
what it did.

### Exercise it, do not trust the tests

The whole point of `inject` is a path that **has never carried a live request** — the auth setting
was turned off rather than configured around, so it is a unit test and nothing more. A phase that
closes a two-knob ambiguity with more unit tests has not proven anything the old shape did not also
pass.

- [ ] Switch LM Studio's "Require Authentication" back on, put the key in `.env`, set
      `credential: inject`, and drive a real request through the router.
- [ ] Then switch it off again and confirm `strip` still works, so the phase does not leave the
      machine in a state the rest of the documentation does not describe.
- [ ] `make check` against a config in each of the three modes, and against each of the three
      contradictions, reading the actual message rather than the exit code.

## Item 2 — the 600-second read timeout

**Not decided.** This half of the phase starts with a measurement and a question, not with code.

### What is known

`proxy.py:81`, `TIMEOUT = httpx.Timeout(connect=5.0, read=600.0, write=30.0, pool=5.0)`. On
2026-08-06 a ~41000-token request against a 44544-token window was killed at exactly `read=600.0`
while LM Studio was still healthily prefilling — `transport_error` / `read_timeout`. Measured times
to first byte on that model: 9166 tokens → 115 s, 27924 tokens → 197 s, ~41000 tokens → never.

So a local model cannot be driven to the top of its own window through this router. Phase 3 chose
600 s on purpose, to make a wedged backend fail in bounded time; what Phase 4 added is that ordinary
traffic reaches it too.

### Step 0, before choosing anything: find out what `read` actually measures

`handoff.md` lists three candidate fixes — a larger timeout, a configurable one, or **one that resets
on progress rather than on first byte**. The third may already be the behaviour.

**The hypothesis to test: httpx applies `read` per socket read, not to the whole response.** If so it
already resets on every chunk, and the Phase 4 kill happened during prefill precisely because there
was no chunk yet to reset on — nothing was streaming slowly, nothing had arrived at all. That would
mean the third option is not an option, and the real distinction is between "how long may a backend
take to say its first word" and "how long may it go silent mid-answer", which httpx cannot express as
two numbers.

- [ ] Verify it directly. `phase-3-verification/` already has a backend that fails on purpose; extend
      it to emit one chunk every N seconds with `N` under the read timeout and a total run well over
      it. If the call survives, the timeout resets on progress and the candidate list shrinks by one.
- [ ] Record the answer in `phase-5-notes.md` either way. It is a fact about the library the project
      will keep needing, and it is cheap exactly once.

### Then the decision

Only after step 0 does the choice have real options. The likely shape:

- **A larger fixed number** is the smallest change and gives up the property Phase 3 wanted.
- **A configurable one, per backend**, keeps Anthropic tight and gives LM Studio room, which matches
  the measured reality that the two backends' time to first byte differs by 26×. It also lands in
  the same file and the same phase as item 1, which is the argument for grouping them.
- **A separate first-byte budget**, if step 0 confirms `read` resets on progress, is the only option
  that distinguishes a long prefill from a wedged backend — and it is the only one that needs code
  rather than a config field.

**A recommendation, not a decision:** per-backend configuration, with today's numbers kept as the
defaults so nothing changes for anyone who does not opt in. It is the option that does not have to be
right — a wrong number becomes a one-line edit instead of a release. The owner takes the call; this
plan will not take it by implementing one quietly.

- [ ] Decide, and write the reasoning down before writing the code.
- [ ] Implement. If it is configurable, timeouts are a `Server`-level or per-`Backend` block in YAML,
      validated like everything else, with `extra="forbid"` keeping a typo an error.
- [ ] Tests.

### Prove it against the traffic that exposed it

- [ ] Re-run the exact Phase 4 request that died — ~41000 tokens against the 44544-token window — and
      confirm it now completes. A timeout change verified only by unit tests is the same mistake the
      timeout itself is an example of: **every one of the 147 tests passed with the broken number.**

### The measurement this unblocks

Phase 4 left "whether trimming happens below the context boundary" open **because the run meant to
check it hit this timeout**. Once the fix is in, that measurement costs one more request.

- [ ] Take it, if the fix lands with time to spare. The boundary itself is known to refuse cleanly;
      what is uncharacterised is the region just under it. Fold the result into `phase-5-notes.md`
      and correct `phase-4-notes.md`'s open list in place rather than leaving it stale.

This is optional and clearly marked so, because it is a measurement in a phase that is otherwise
code, and a phase that quietly grows a measurement step is how the last three ran long.

## Out of scope, deliberately

- **The per-backend authentication header name.** `inject` means `Authorization: Bearer`, which suits
  LM Studio and OpenAI; Anthropic's native key is `x-api-key` and Gemini's is `x-goog-api-key`.
  `CLAUDE.md` records this as needed before the second cloud provider and not before. Phase 5 must
  not settle it as a side effect of touching the same function — if a header name becomes
  configurable here, that is a new decision taken by accident.
- **The three EPDs.** All are waiting on a person, none on work. See `outstanding-work.md`.
- **The prompt-cache warmup probes.** The 44% of local wall clock is a routing-rule question, not a
  configuration one, and it deserves its own phase or none.
- **Retries, failover, a merged model list.** Still in "Not doing yet" at the foot of
  `implementation-plan.md`.

## Done when

- One `credential` field with three modes, `api_key_env` required by `inject` and forbidden by the
  others, all three contradictions refused at startup with messages that name the fix.
- `inject` has carried at least one **live** request against LM Studio with authentication on.
- The read timeout question is decided, the reasoning written down, and the change verified against
  the ~41000-token request that exposed the defect rather than against tests alone.
- `CLAUDE.md` no longer says "Not yet implemented" about the credential shape, and no longer
  describes the 600 s timeout as an open defect.
- `handoff.md` and `outstanding-work.md` updated: this phase removes both items from the plate, and
  a file that lists work already done is worse than no file.
