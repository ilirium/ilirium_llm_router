# For the owner — Phase 14

*`IDM-010`. Written during the phase, to a person. Numbered in order of appearance and never
renumbered. Anything needing a decision was asked out loud instead of being parked here.*

---

## 1 · ERRAND · ~~high~~ · Only you can run the measurement — ***DISCHARGED 2026-09-18***

> **Run five times that day, Claude Code 2.1.267.** It produced the measurement, and then four more
> experiments on top of it. *The text below is left exactly as written, because what it predicted —
> that only a person at a keyboard could take this — held for every one of the five.*


**Group C needs a real Claude Code session, through the router, with auto mode on.** A session
cannot do it: it needs your credential and your machine, and `CLAUDE.md` says driving a session is
never done freely.

**What it is for:** the 429's response headers have never been seen. They are the one thing that
separates *Anthropic restricts this request shape on a subscription credential* from *the router
provokes it* — and `BUG-001` has rested on timing and inference for three weeks for exactly the want
of them.

**What to do, once Group B is in:**

1. `make run` in `to-run-server/`, with the router built from this branch.
2. A Claude Code session pointed at it, auto mode **on**, and something that shells out — `printenv`
   was enough on 2026-08-25, and it failed within ninety seconds.
3. `claude --version` recorded. **`BUG-001` asks for it by name**: if the fix turns out to be
   client-side, the version is the only thing that will identify it.
4. Then stop, and hand back — Task 8 reads `router.log` and freezes the result.

**If it does not reproduce, that is a result and not a wasted session.** Say so rather than
retrying; an absence of 429s is `BUG-000`'s trap and a quiet session looks exactly like a fix.

## 2 · ASK · medium · The durable home is deferred, not answered

**You deferred it on 2026-09-18 and that was the right call** — the minimal form needs no schema, so
the question can be answered with the values in hand instead of guessed at beforehand.

**It comes back at Group D, and it is still the milestone plan's "Phase 14's plan cannot skip the
question".** Three candidates, unchanged: a sidecar telemetry file, the corpus day index, or
overturning the `calls.csv` non-goal. **Only you can overturn that non-goal**; it is
`implementation-plan.md`'s and this phase has no authority over it.

*Recorded here so the deferral cannot be mistaken later for the question having been settled.*

## 3 · IDEA · low · Keeping what the corpus already holds

**The diagnosis in the plan's evidence section cost nothing to produce** — every fact came from
`calls.csv` and corpus blobs already on disk in `to-run-server/`, three weeks after the traffic that
made them. The classifier's request body, the quota probe, the exact 429 text and its `request_id`
were all simply there.

**That is the corpus doing the job it was built for, on a question nobody had when it was built.**
Worth knowing when `BKL-0017` asks whether archiving is worth what it costs — this is the other side
of that ledger, and it is not written down anywhere else.

## 4 · ASK · high · `branch-index.py --write` now deletes a row it must not delete

**Found while checking this phase's own branch description. It is not this phase's doing** — it
reproduces on a clean `main` with nothing of this branch in the tree.

**What happens:** `temp/to-run-server` has been fast-forwarded to `main`'s exact tip. `resolve()`
treats a branch whose tip is on the trunk **with nothing between it and the trunk head** as *in
flight* — correct for a branch just cut and not yet committed to, and wrong for this one. It
therefore leaves `merged_rows`, and **`--write` silently drops its row from `reference/branches.md`.**

**Why it matters more than one row.** `IDM-001` says of exactly this row: ***"The row exists; do not
remove it as noise."*** It is the only place that records that `temp/to-run-server` is not work —
and that the telemetry and corpus `BUG-001` and Phase 11 both rest on were captured through it.
**And `IDM-001` puts `--write` as the last step of every merge**, so the next merge deletes it
without anyone looking.

***`--check` does not warn.*** It prints `STALE: branches.md does not match git. Re-run with
--write.` — the same thing it prints for an ordinary missing row. **A green `--write` followed by a
commit is what this looks like from the outside.**

**Not fixed here, and not worked around.** The fix is a judgement about what the script should treat
as in flight, and it belongs on its own branch rather than inside a phase about response headers.
**`main` is STALE right now** for this reason alone.

*Asked out loud on 2026-09-18. Recorded here because it survives the session.*

## 5 · REGRET · high · I read "Anthropic sent this" as "Anthropic is at fault"

**The headers were real and the inference was not.** A `429` carrying no metering, on a connection
whose successes carry twelve buckets, is a fact. *"Therefore it is Anthropic's fault"* is a
different claim, and **the one experiment separating them — direct against routed — had never been
run.** You ran it by asking why auto mode worked in the session you were reading the finding in.

**`BUG-001` had been making the same mistake since 2026-08-25**, with a worse version of it: its
table clears the router by comparing streamed against non-streamed *inside* the router, which
cannot see a router-caused defect specific to non-streamed requests. **Struck on this branch.**

*Recorded because the phase's instruments all worked and the reasoning on top of them did not.*

## 6 · REGRET · medium · Three instruments, three near-misses, one pattern

| | What it would have said |
|---|---|
| The allowlist, built from Anthropic's documentation | *"a 200 carries no rate-limit headers either"* — **none of the documented names arrives on your credential** |
| The sample latch, spent on `/api/hello` | `(none)` — **the same string a rejection prints** |
| The imitated billing header, ending `"; "` | Four tests asserted its content; **none validated it as HTTP**, and it broke as a 502 in your face |

***Each tested the thing it was pointed at. None tested whether it was pointed at the right
thing.*** *All three were caught by reading a line against a measurement taken minutes earlier, and
none by a test — while twenty-four mutations pass.*

## 7 · ERRAND · high · Three experiments are live in the router and one has a cost

**You asked for them to stay, and they have stayed.** So that the next session does not have to
rediscover it:

| In the tree | |
|---|---|
| `accept-encoding` relayed for non-streamed | ***WAS TRUE UNTIL 2026-09-19 AND IS NOT NOW.*** While it ran, the corpus stored non-streamed response blobs as **brotli, not JSON** — *`logs/corpus/2026-09-18` and the 12:31 slice of `2026-09-19` still do, so a reader of those days needs brotli.* **The switch is off, so new blobs are plain again — and this experiment turned out to be the cause of the classifier failure.** → entry 20 |
| `http2=True` and the `h2` dependency | Harmless, buys nothing measured |
| The imitation headers | Fabricated attribution on every Anthropic call |

**All three are exonerated. None is reverted. That is your decision and it is recorded as yours.**

***"Exonerated" was about the 429 and it is now too strong for `accept-encoding`.*** **It is the
prime suspect for the classifier still failing after the 429 went away** — *it is the only change
that alters what a non-streamed reply looks like to the client, and the classifier is always
non-streamed.* → **entry 19.**

## 8 · IDEA · medium · The two things left, and neither is cheap

**The exact-fingerprint allowlist.** `curl_cffi` is Chrome, not Claude Code — it carries three
extensions a bare BoringSSL build does not. **Only Bun's own build could match, and even that is a
maybe**: Bun's `fetch` need not fingerprint like the compiled binary.

**Connection reuse**, which nothing here has touched. *Claude Code direct may put the classifier on
an HTTP/2 connection that already carried a conversation; the router and the forwarder each pool
their own.* **Untested, and named because it is untested.**

## 9 · ERRAND · medium · The upstream report is written but not sent

**`BUG-001` now holds the measurements both issues stall on** — the paired control, the meter
reading `allowed` at 52%, request ids, and the proof that the router alters no header. **Nobody has
told either issue any of it.** *It was `status.md`'s item 2 before this phase and it still is.*

## 10 · ERRAND · high · One env var, one session — and it is the last cheap experiment

***Only you can run it***, for the same reason entry 1 gave: it needs your credential, your machine
and a real session with auto mode on.

**What it is.** Claude Code turns off a set of first-party behaviours the moment `ANTHROPIC_BASE_URL`
points anywhere but `api.anthropic.com` — **and it ships a switch that forces them back on.** Read
out of the binary on 2026-09-18; the fragments are frozen in
`evidence/claude-code-first-party-gate-2026-09-18.txt`.

**Why it is worth a session when eleven hypotheses have come back negative.** *Every one of those
eleven was a **router-side** flip. This is the first client-side one* — and it is the whole class at
once, rather than the two attribution fields C2d could see in `--debug api` and imitate by hand.
**It also makes the router fabricate nothing**, which disposes of the terms question the imitation
headers carry.

**What to do:**

1. `make run` in `to-run-server/`, as at entry 1.
2. A Claude Code session pointed at the router, with **`_CLAUDE_CODE_ASSUME_FIRST_PARTY_BASE_URL=1`**
   set alongside `ANTHROPIC_BASE_URL`, auto mode **on**, and something that shells out.
3. `claude --version` recorded. ***The underscore prefix means this is an internal flag***, so it can
   move between releases and the version is the only thing that will identify which build it held on.
4. Then stop and hand back — the arriving-header sampler should be read in the same session, to see
   whether `x-anthropic-billing-header`, `x-client-request-id` and `traceparent` now arrive at all.

**All three outcomes are findings, and none is a wasted session:**

| | |
|---|---|
| **The 429 goes away** | The cause is the first-party gate, `BUG-001` gets a workaround it does not have, and the upstream report gets the thing both issues actually lack |
| **The 429 stays, and the headers now arrive** | The withheld headers are eliminated **as a class**, properly this time — C2d only ever tested two of them |
| **The 429 stays and the headers still do not arrive** | The client withholds them below the gate, and that is worth knowing before anyone reports this upstream |

***And the `BUG-000` trap applies as it always does:*** an absence of 429s in a quiet session is not
a pass. **Drive it until a `Bash` call is actually classified**, which on 2026-08-25 took about
ninety seconds and a `printenv`.

**One thing I could not do and did not work around.** *Two of the binary reads behind this entry were
blocked mid-analysis by the auto-mode classifier* — the very mechanism this phase exists to
diagnose. **I stopped and said so rather than finding another route**, so the fragments frozen in
`evidence/` are what was read before the block and not everything there is to read. *Entry 7's live
experiments are untouched by any of this.*

## 11 · ASK · high · Entry 10 ran, and the latch missed the one request that mattered

***Entry 10 is discharged as an errand and is not discharged as a question.*** **You ran it at
14:52 UTC and the result is frozen** at `evidence/first-party-flag-run-2026-09-18.txt`.

**What it settled:** the flag **works** — `x-client-request-id` reaches the router for the first
time — and **the 429 is completely unchanged**, 13 of them, while 7 of 7 streamed calls succeeded.
**The meter read 0.11 and 0.01.** *Quota was already dead; it is now dead at an empty budget.*

***What it did not settle is the thing the session before it predicted.*** **The non-streamed
sample was spent on the `haiku` warm-up** — 323 bytes — **and every classifier request that
followed was 127,949 bytes and unsampled.** So whether the classifier carries
`x-anthropic-billing-header` is **still unknown**, which is exactly the claim entry 10 was run to
test.

**This is the third time this phase has spent a one-shot sample on the wrong request**, and the
second after the fix. *Entry 6's row — "the sample latch, spent on `/api/hello`" — was fixed by
gating on the path. `/v1/messages` non-streamed turns out not to be one thing.*

**Three ways to fix it, and the choice is yours because it changes `src/`:**

| | |
|---|---|
| **Latch per shape *and* per size band** | One line. **Crude, and it would have worked here** — the warm-up and the classifier differ by four hundred times |
| **Log the header *name set*, every non-streamed request, and only when the set differs from the last** | **No latch to spend.** Cannot miss a request shape nobody predicted, and it stays inside the standing "names, never values" rule |
| **Leave it and drive a second session** | **Free in code and costs one of your sessions** — and it is the option this phase has taken twice already |

***My recommendation is the second***, and not because it is tidier: **every near-miss in entry 6
is a latch deciding in advance which request would be interesting.** *A set-difference log makes
that decision impossible to get wrong, and it would have caught this without anyone predicting the
warm-up existed.*

**Not implemented.** `CLAUDE.md` says propose before implementing, and this is a proposal.

***ANSWERED 2026-09-19 — and you improved the option you picked.*** **You took the second row's
spirit into the first's shape**: not a size band bolted onto the existing latch, but a key of
`(path, shape, size band)` — ***with the path part of the key rather than a gate.*** *That is
strictly more than was offered: the old code refused to sample any path but `/v1/messages`, which is
the same advance decision one level up, and `/api/hello` is now sampled in its own right instead of
being excluded.* **Built the same day; see entry 15 for what it cost and what it found.**

## 12 · REGRET · medium · I let "the flag works" stand in for "the hypothesis holds"

**They are different claims and only the first is measured.** *`x-client-request-id` arriving proves
the gate is real and the switch reaches the wire. It says nothing about the attribution header,
because the request that would have shown it was never sampled.*

***This is entry 5 again, one level in.*** *There the error was reading "Anthropic sent this" as
"Anthropic is at fault"; here the temptation was to read a confirmed **mechanism** as a confirmed
**cause**.* **Caught by reading the sampled request's byte count against the classifier's before
writing the conclusion** — 323 against 127,949 — **and not by any check.**

## 13 · REGRET · high · I read a name as a channel, and the corpus could have said so in hour one

**`forceAttributionHeader` is the client's own name for a flag that produces a *system-prompt text
block*, in the request body.** *Not a header.* **I told you the classifier was "the one request
shape that forces the attribution header" and built an experiment on it. That is withdrawn.**

***The check that settles it was free and available from the first hour of this phase:*** the
corpus stores bodies, the bodies were on disk, and `extract --format bodies` finds the string in two
of the day's requests and in none of the classifier's. **Nobody ran it because the word in the name
was "header", so the search went to the header capture.**

**It also means C2d never tested what it was built to test.** *It added an HTTP header the client
never sends as a header. The negative was real; the subject was not.* **Entry 7's imitation
experiment can come out on those grounds alone** — it is not merely unproductive, it is answering a
question nobody has.

## 14 · ERRAND · ~~high~~ · The hosts experiment — ***DISCHARGED 2026-09-19, and it answered***

> ***Ran on the second attempt and the `429` is gone.*** **Nine classifier requests through the
> router, all `ok`, zero `429`s anywhere in the run.** *The first attempt looped — entry 16 — and
> the runbook below is the corrected version, with steps 2 and 4 saying what they can and cannot
> prove.* **The result is entry 17.** *The text is kept because you may want to run it again.*

***You chose this over patching the binary and you were right to.*** `CE()` reads
`process.env.ANTHROPIC_BASE_URL` **directly**, so leaving that variable unset is what makes the
client first-party — **and a hosts entry does that with nothing modified.** *The alternative was
editing a 200 MB code-signed Bun executable whose bundle is marked `@bun @bytecode`, where a
compiled copy of the patched source may sit alongside the text and the edit may simply not take.*

**Why it is worth a session:** ***it is the only remaining experiment that makes the client fully
first-party while still routing through you.*** **If the 429 survives it, the entire client-side
variable is eliminated** and what is left is the TLS fingerprint and connection reuse — entry 8,
both expensive. **If it goes away, `BUG-001` gets a real workaround.**

```
Claude Code (ANTHROPIC_BASE_URL unset)
  -> api.anthropic.com:443      [/etc/hosts -> 127.0.0.1]
  -> evidence/tls-terminator.py  (sudo; mkcert certificate)
  -> the router on 8787          (unchanged)
  -> evidence/run-pinned.py      (pins api.anthropic.com to its real address)
  -> Anthropic
```

### Before anything — the one number to take first

```sh
dig +short @1.1.1.1 api.anthropic.com | head -1        # e.g. 160.79.104.10
```

***Take it now and write it down.*** *`run-pinned.py` refuses a loopback value rather than looping,
and now also refuses to start unless the pin is observed working — but do not make it do the
catching.*

***Corrected 2026-09-19: this said a plain `dig` would answer `127.0.0.1` once the hosts entry was
in. It would not — **`dig` does not read `/etc/hosts` at all**, it queries a nameserver directly.***
*Checked against `broadcasthost`, which `/etc/hosts` maps and `dig` cannot see.* **Keep `@1.1.1.1`
anyway**: it makes the answer independent of a VPN or corporate resolver, which is a real hazard
even though the stated one was not.

### Step 1 · mkcert, and what it changes

```sh
brew install mkcert
mkcert -install                                        # puts a local CA in your system trust store
cd ~/                                                  # or anywhere you like; note where
mkcert api.anthropic.com                               # writes the .pem pair into the cwd
```

***`mkcert -install` is the only thing here that changes your system beyond one file.*** **It is
reversible with `mkcert -uninstall`.** *Note the two paths it prints; steps 3 and 6 need them.*

### Step 2 · The router, with the address pinned

**Terminal 1**, from this worktree:

```sh
make run-hosts
```

*It resolves the address itself via `@1.1.1.1` and starts the router under `run-pinned.py` with
`config-hosts.yaml`.* **Expect a line reading `[pinned] api.anthropic.com -> … , verified by
resolving it through uvloop.Loop — patch fired via uvloop`.**

***That line now means something, and on 2026-09-19 the old one did not.*** **The script used to
print `[pinned] …` unconditionally, before doing anything** — so it appeared on the run that failed,
the runbook said to stop only if it was *missing*, and it was not missing. **It now resolves the
name through the router's own event loop and refuses to start unless the patched resolver is
observed returning the answer.** *If the router does not start, read the message: it says which loop
ran and what the name resolved to.* → entry 16.

**`config-hosts.yaml` is new and it matters:** it is `config-boringssl.yaml` with the egress hop
removed, so ***the corpus is ON***. *Without it this run captures no bodies, and the corpus is what
answered the attribution question when nothing else could.*

### Step 3 · The TLS terminator

**Terminal 2**, from this worktree, with your paths from step 1:

```sh
sudo .venv/bin/python \
  docs/milestone-2-corpus/phase-14-rate-limit-headers/evidence/tls-terminator.py \
  --cert ~/api.anthropic.com.pem --key ~/api.anthropic.com-key.pem
```

***`sudo` because 443 is privileged.*** *The process writes nothing; stopping it is `Ctrl-C`.*

### Step 4 · Prove the whole chain WITHOUT touching `/etc/hosts`

```sh
curl --resolve api.anthropic.com:443:127.0.0.1 https://api.anthropic.com/api/hello
```

***This is the step that protects you.*** **`--resolve` redirects only this one command**, so the
full path — TLS, terminator, router, egress — is exercised while the rest of the machine,
***including the Claude Code session you are reading this in***, still reaches the real Anthropic.

**Do not go past this step until it answers.** *A TLS error here is a certificate problem; a hang is
the terminator.*

***What it CANNOT test, learned the hard way on 2026-09-19: the pin.*** **This step runs before
`/etc/hosts` exists, and until then a pinned router and an unpinned one behave identically** — both
resolve the name normally and reach Anthropic. *It went green at 12:05, the session failed at 12:07
with every request looping back into the terminator, and it went green again at 12:12 after the
teardown. **The same fact three times, and never the one that mattered.*** **Step 2's verification
is what covers the pin now; this step covers everything else.**

### Step 5 · The hosts entry, last, and knowing what it does

```sh
sudo sh -c 'printf "127.0.0.1\tapi.anthropic.com\t# PHASE 14 EXPERIMENT - remove me\n" >> /etc/hosts'
```

***This redirects every process on the machine, including any Claude Code session you have open.***
**If the chain is not working, that session loses its connection mid-turn and you will be debugging
with the line still in place.** *That is why step 4 comes first, and why the line carries its own
removal note.*

### Step 6 · The measurement

**A Claude Code session, `ANTHROPIC_BASE_URL` UNSET, auto mode ON, and something that shells
out** — `printenv` was enough on 2026-08-25 and failed within ninety seconds.

- **Record `claude --version`.** *`BUG-001` asks for it by name.*
- ***An absence of 429s is not a pass.*** **Drive it until a `Bash` call is actually classified** —
  `BUG-000`, and a quiet session looks exactly like a fix.

### Step 7 · Put it back

```sh
sudo sed -i '' '/PHASE 14 EXPERIMENT/d' /etc/hosts     # first, and check with: grep anthropic /etc/hosts
```

*Then `Ctrl-C` both terminals.* **`mkcert -uninstall` whenever you want the CA gone** — *it can stay
if you would rather not repeat step 1.*

### What to hand back

**Nothing needs transcribing.** *A session can read `logs/telemetry/router.log`, `calls.csv` and
`logs/corpus/` straight off this worktree — that is how the 14:52 run was read.* **Say which steps
you ran and whether step 4 was green**, and ***say it if it did not reproduce***: that is a result,
not a failed session.

***That gap is closed — 2026-09-19, and this paragraph is the corrected version.*** **It said the
sampler would again spend its non-streamed latch on whatever arrived first.** *You chose entry 11's
fix that morning and it is in the tree, so the warm-up and the classifier are now separate shapes
and both are logged.* **Nothing in steps 1–7 changes**; the router is run from source, so
`make run-hosts` picks it up with no rebuild. → entry 15.

## 15 · REGRET · medium · The sampler fix, and a test of mine that passed for the wrong reason

**Entry 11 is discharged. Built 2026-09-19 to your shape** — `(path, streamed?, size band)`, bands
being the decimal order of magnitude, so the 323-byte warm-up is band 2 and the 127,949-byte
classifier is band 5. **480 tests, `make lint` clean, and the mutation harness at 32/32.**

***One thing I added that you did not ask for, and the reason is worth a line.*** **The key carries
the request path and `app.py` registers a catch-all route**, so the key space is whatever a caller
types — an unbounded set and an unbounded log, where the old two-key dict could not grow at all.
**It stops at 64 shapes, and reaching the cap is announced on its own log line.** *A silent stop is
the defect this phase keeps having; a bound that hides itself would have been a fourth instance.*

***The regret is a test I wrote and believed.*** **`test_the_probe_endpoint_cannot_spend_the_messages_latch`
passed a mutation that deleted the path from the key entirely.** *Its two requests are a bodiless
`GET /api/hello` and a 71-byte `POST /v1/messages` — **different size bands**, so they stayed apart
on the band alone and the path assertion rode along for free.* **It asserted the right thing and
proved none of it.**

***It was caught by the harness and by nothing else*** — the test was green, the code was correct,
and reading it would not have shown this. **`test_the_path_is_part_of_the_shape_key` now varies
nothing but the path.** *This is the fourth time in this phase that a check has turned out to be
aimed at something other than what it claimed, and the first that an instrument caught rather than a
person.*

**Nothing else in `src/` was touched** — checked with `git diff --stat`, not assumed. *Entry 7's
three live experiments are untouched and still yours to keep or drop.*

## 16 · REGRET · high · The hosts run looped, and the guard that should have caught it was decorative

**You ran it on 2026-09-19 and it produced no measurement.** *Every step you took was the one the
runbook asked for.* **The fault is in two things I wrote.**

### What happened, from `logs/telemetry/router.log`

| | |
|---|---|
| **12:05:00** | Step 4's `curl --resolve` → `/api/hello` → **200**, 252 ms. The real Anthropic |
| **12:07:46** | Session starts, hosts line in → ***every request 502***, `transport_error connect_error`, **4–9 ms** |
| **…** | **67 × 502, not one success.** 70 calls arrived, 70 recorded |
| **12:12:37** | After teardown, `/api/hello` → **200** again |

***4–9 ms is a local connection.*** **The router resolved `api.anthropic.com` to `127.0.0.1`,
connected to your terminator and refused its mkcert certificate** — `unable to get local issuer
certificate`, because Python's `certifi` bundle has no local CA. **That is the loop `run-pinned.py`
exists to prevent.**

### Why the pin was inert

**`run-pinned.py` patched `socket.getaddrinfo`. The router runs under `uvloop`** — `uvicorn.run`
takes `loop="auto"`, uvloop is installed, and ***uvloop resolves names with its own native resolver
that never calls `socket.getaddrinfo`.***

*Measured rather than reasoned about: patch `socket.getaddrinfo`, call `anyio.getaddrinfo` under
each loop — **plain asyncio calls the patch, uvloop does not.*** **Fixed by patching
`uvloop.Loop.getaddrinfo` as well**, which keeps the experiment on the loop the router really uses
rather than introducing a second variable.

### The part that is mine rather than uvloop's

***The `[pinned] …` line printed unconditionally, before anything was resolved.*** **The runbook
told you to stop if it was missing. It was not missing. It has never meant anything.**

***And step 4 cannot test the pin at all*** — it runs before `/etc/hosts` exists, so a pinned router
and an unpinned one are indistinguishable there. **Your three green checks are one fact repeated,
and the pin was never among them.**

**`verify_the_pin` now resolves the name through the router's own event loop and refuses to start
unless the patched resolver is observed doing it.** *Two facts, not one: the address has to be right
**and the patch has to have fired** — because with no hosts entry an unpatched lookup returns the
right address too.* ***Exercised by reintroducing the exact defect: the address came back correct
and the check still refused.***

**This is the fifth green check in this phase aimed at something other than what it claimed** — and
the first that was load-bearing for one of your sessions rather than for a conclusion.

### What the run DID produce, and it is not nothing

***Your new sampler ran, and it paid for itself in a failed experiment.*** **18 arrival lines where
the old code would have produced 2**, every request sampled before its 502:

- `/v1/messages` at **323 bytes non-streamed** — the warm-up that ate the only slot last time
- `/v1/messages` at **4,168** and **118,395 bytes streamed** — two bands, two lines
- ***Eleven API paths this phase had never seen***, all hidden by the old path gate:
  `/api/claude_cli/bootstrap`, `/api/oauth/usage`, `/v1/ultrareview/quota`, `/mcp-registry/v0/servers`,
  `/api/claude_code_penguin_mode`, and `/api/event_logging/v2/batch` at **435,666 bytes**

***Still missing: the 127 KB non-streamed classifier.*** **The session died before auto mode
classified anything**, so the question entry 11 was fixed to answer is still open — and it is open
for a new reason rather than the old one.

## 17 · ASK · high · The 429 is gone, and the next move is a decision rather than an experiment

***You ran it at 12:30 UTC on 2026-09-19 and it answered the phase's question.*** **Nine classifier
requests through the router, every one `ok`, and not one `429` in the whole run** — on **2.1.267**,
the same build that produced 119 rejections the day before.

| | **2026-09-18**, base URL set | **2026-09-19**, hosts route |
|---|---|---|
| Classifier requests | **125** | **9** |
| Outcome | **119 × `429`** + 6 disconnects | ***9 × `ok`*** |
| The attribution block | **absent in all 125** | ***present in all 9*** |

***It is genuinely the classifier and not a quiet session.*** **`anthropic-beta` on those requests
carries `auto-mode-classifier-2026-07-16`** and the system prompt opens *"You are a security monitor
for autonomous AI coding agents"*. **`BUG-000`'s trap does not apply.**

### What you now have that nobody had yesterday

***The router is cleared, by measurement rather than by argument.*** **Same router, same `httpx`
egress, same TLS fingerprint to Anthropic — nine successes today, 119 rejections yesterday.**

***And the two expensive hypotheses in entry 8 are dead for free.*** **Anthropic saw the router's TLS
fingerprint on both days**, and the router pooled its own connections on both days. *Neither needs
the Bun build, and neither needs another session.*

### What I am NOT telling you, and it matters

***The attribution block is the leading candidate. It is not proven to be the cause.*** **Several
things move together when `ANTHROPIC_BASE_URL` goes away**, and *this phase has already read a
mechanism as a cause once and a name as a channel once.* **The honest statement is: the cause is
client-side content withheld from a custom base URL, and the attribution block is the one known
difference that survives into today's success** — `x-client-request-id` having been eliminated by
your own flag run.

### Three decisions, and they are yours

- ***Is `BUG-001` now workaround-complete enough to report upstream?*** **I think yes, and it is the
  strongest version it will ever have**: a paired control on one client build where the only variable
  is whether the client believes it is talking to Anthropic directly. *It has been an open action
  since 2026-08-25.*
- ***Entry 7's imitation experiment: I would now remove it.*** **The bodies say the real value is
  `cc_version=2.1.267.608; cc_entrypoint=cli`** and the code fabricates `0a3` / `sdk-cli`. *So it is
  wrong in three ways — wrong channel per entry 13, wrong version suffix, wrong entrypoint — and it
  fabricates attribution on every Anthropic call for no remaining reason.* **Still your call.**
- ***Does the phase chase the last step, or close?*** **Proving the attribution block is the cause
  would mean the router injecting it into a request the client did not put it in** — *which alters a
  body byte-for-byte relayed today and breaks prompt-cache prefixes.* **I would not do that without
  you saying so**, and the phase's chartered question is already answered.

### One housekeeping thing still open

***The `.pem` files were untracked and un-ignored in the worktree root.*** **You moved them, so
`git status` is clean** — but nothing stops the next cert landing there. *One line in `.gitignore`
would; say the word.*

## 18 · ASK · ~~high~~ · Your transcript disagrees with the router's log, and a real defect fell out

> ***The disagreement is ANSWERED — entry 19, 2026-09-19.*** **It was not a second session and not
> an upstream outage: the router served those classifications correctly and the client rejected
> the answers.** *The gzip defect below is unchanged and still open.*

***You left `evidence/claude-code-sessions-to-check-safety-classifier.txt` in the tree and it is
the most useful thing in the run.*** **It also contradicts what I told you in entry 17**, so here is
the disagreement rather than a tidied version of it.

### The two records

| | |
|---|---|
| **Your transcript**, 15:31–15:32 local | ***The classifier is down.*** `claude-opus-5[1m] is temporarily unavailable` — **four of ten probes**, reproducing on retry; `echo`/`ls`/`date` passed **by allowlist, never consulting the classifier** |
| **The router**, 12:31–12:32 UTC, *same session id* | **Six classifier calls, all `200`**, each carrying a real verdict — `<block>no` ×4, `<severity>10`, `<severity>18` |

***And nothing naming `claude-opus-5[1m]` ever reached the router*** — zero matches for `1m` in the
whole of `calls.csv`.

**So the failures you saw produced no request this router received.** *I can think of three shapes
— the attempts never left the client, a second session was not traversing this router, or the `[1m]`
variant was genuinely unavailable upstream and unrelated to any of this.* ***Nothing on disk
distinguishes them, and you are the only one who can say which session was which.***

**What this does and does not cost entry 17:** *the nine classifications and the zero 429s are
measured and stand — the paired control is unaffected.* ***What I should not have implied is that
auto mode was usable end to end***, which is a stronger claim and is now the open question.

### The defect your file led me to

***Two requests that run were rejected by the router itself*** — `400`, **"The request body carries
no 'model' field."** ***Both bodies are gzip-compressed***, magic `1f8b0800`. Decompressed they are
ordinary: your **title-generation** call, and a **118 KB main conversation turn**.

**The model peek is reading compressed bytes, so `routing.py`'s prefix rule never runs.** *The client
retried both uncompressed twelve milliseconds later, which is why your session carried on.*

***This is new because the client is first-party.*** **No capture in this phase has a custom-base-URL
client gzipping a request body; one that believes it is talking to Anthropic does.** *So anyone who
adopts the hosts workaround meets it.*

**Not fixed, and it is a decision rather than an obvious patch:**

- ***Decompress to peek*** — read `content-encoding`, inflate a copy, find `model`, **relay the
  original bytes untouched.** *Byte-relay survives; the cost is inflating up to 5 MB per request*
- ***Fail more usefully*** — keep the 400 but say *"the body is `gzip`-encoded and this router cannot
  read it"*, so the next person is not hunting a missing field that is there
- ***Leave it*** — the client retries uncompressed and recovers on its own

***I would take the first*** — it is the only one where the router does its job — **but it changes
`src/` in a phase chartered for response headers, so it may belong on its own branch.** **Your
call.**

### And a smaller thing

**Your file's `## Session 2, 2026-09-19` heading has nothing under it.** *It is untracked, so I have
left it alone* — **say whether it should be committed as evidence** (it is the only record of the
client-side view of that run) **or kept out of git.**

## 19 · ASK · high · The 429 was hiding a second defect — auto mode still does not work

***Your three transcripts answered entry 18, and the answer costs me a claim I made in entry 17.***
**Thank you for writing them down; nothing in the router's own record could have settled this.**

### What the two records say together

**A Bash call in auto mode either matches your allowlist — `echo`, `ls`, `date` — and is permitted
by rule, *sending no request at all*; or it does not, and the classifier is asked, which is an API
call and shows up in the router's log.** *And the classifier is two-staged: a `<severity>` pair, then
a `<block>` decision. A pair is one event.*

**Session 2, whole, your times:**

| Call | Time | You saw | The router received |
|---|---|---|---|
| #1 | 15:34:52 | ok | — |
| ***#2*** | | ***unavailable*** | **15:34:56 `<severity>15`, 15:34:58 `<severity>25`** |
| #3–#5 | 15:35:08–24 | ok | — |
| ***#6*** | 15:35:30 | ***unavailable*** | **15:35:27 `<block>no`** |
| #7–#8 | 15:35:30–32 | ok | — |

***Three requests all session, in exactly the two gaps where you saw a failure.*** **Session 1 is the
same at larger scale — five events, five failures**, and its six passing probes were `echo` and
`ls`, which is what you worked out yourself and it was right.

### The conclusion, and it is the reverse of what I told you

- ***Every command that worked sent no classifier request.*** Allowlist matches.
- ***Every classifier request corresponds to a command you saw fail*** — **and none of them failed at
  the router.** *Each got `200` with a real verdict, including `<block>no`, which means **allow**.*

***So: you asked to run a command, the router carried the question to Anthropic, Anthropic said
"allow", the router carried that back, and Claude Code told you the classifier was unavailable.***

**I owe you the correction plainly: entry 17's "nine classifications succeeded" was true of the
router and false of your experience.** *I read a status code as an outcome, which is the same shape
as entries 5, 12 and 13 — and this time the check I skipped was **asking the person who was in the
session**.*

### What survives and what does not

***The 429 result is untouched*** — **119 rejections became zero and the paired control still clears
the router of causing them.** ***What is new is that two defects were stacked and the first hid the
second:*** while every classifier request was rejected outright, nothing ever reached a `200` body
for this to appear on.

### The proposal, and it is one line of `src/` and one session

| Reply shape | Encoding | |
|---|---|---|
| **streamed** | plain | **32 today, all worked** |
| **non-streamed** | ***brotli*** | **13 today — every classifier call** |

***That split is experiment C2a's*** — before it, the router forced `accept-encoding: identity` and
non-streamed replies arrived as plain JSON.

***I propose putting non-streamed back to `identity` and you re-running the same probes.*** **If the
failures stop, it is C2a and entry 7 loses one of its three.**

***Stated as suspicion rather than finding:*** **Claude Code advertises `br`, so a correctly relayed
brotli reply ought to work.** *Either the relay mishandles something around it — `content-length` is
dropped and the reply goes out chunked — or the client's non-streamed path cannot take it, and
nothing on disk separates those.*

### And your router-off session is nearly a control

**Session 3 genuinely bypassed the router — I checked rather than trusted the label: `20260919-3` has
zero rows in `calls.csv` against 27 and 18 for the other two.** *It saw no classifier failures.*

***It ran four commands, so it shows no failures rather than establishing their absence.*** **Ten
probes like Session 1's would turn it into a real control**, and that is the one thing that would
make this airtight before anyone reports it anywhere.

## 20 · ERRAND · high · It works — and the second defect was ours

***You drove it 2026-09-19 at 15:30 UTC and the classifier worked.*** **35 calls through the router,
all `ok`. 16 classifier calls, all `ok`. No 429, no gzip `400`, nothing refused** — the first clean
sheet in this phase's record. *Session 4 in `evidence/claude-code-sessions-to-check-safety-classifier.txt`.*

### Your test 9 is the best measurement this phase has taken

***It is in the router's own record.*** **15:37:47 — `<severity>68</severity>` with
`<category>Auto Mode Bypass</category>`**, the classifier reasoning that a session deliberately
probing it matches the bypass pattern. *Neighbours scored 60–65 and were allowed.*

**Every previous attempt could only show an absence of failures**, which `BUG-000` says proves
nothing. ***This shows a positive, discriminating decision — eight probes allowed and the
pipe-to-bash one blocked*** — **and no quiet session can fake that.** *Asking for a block rather
than a pass was the right instinct and it is the thing that makes this airtight.*

### What fixed it, and it was the router

| Reply shape | Before | After |
|---|---|---|
| **non-streamed** | ***brotli***, every one | ***plain JSON, all 16*** |
| streamed | plain | plain |

***`relay_accept_encoding` is the only switch that can change a reply body***, and the reply bodies
are what changed. **Three went off together, so the run alone credits the set; the encoding narrows
it to one.**

***So the second defect was ours, it ran for a day, and entry 7 called it "exonerated".*** **That
clearance was for the 429 and I let it stand for the component.** *A negative result for one symptom
is not a clearance, and this is the fifth instance in this phase of a check aimed at something other
than what it claimed.*

### What is still open on it, and it is small

***Why a compressed reply defeats the client is not established.*** **I tested what the router sends:
`content-encoding: br` is relayed correctly and `content-length` is dropped, so the reply goes out
chunked.** *A compliant client has what it needs.* **The data narrows it to compressed AND chunked
together** — streamed replies are chunked too and always worked — *but the client's side is
unmeasured and nothing on disk records it.*

**One condition would separate them:** *keep the compression and stop dropping `content-length` for
non-streamed replies.* **If it then works, the bug is the missing length rather than the
compression** — worth fixing rather than avoiding. ***Not built.***

### Your other question: making it work with `ANTHROPIC_BASE_URL` set

***The honest answer is that nothing is known to work yet, and there is one cheap test before any
code.***

**The only candidate the router could supply is the attribution block** — and *it is a text element
in the `system` array of the body, not a header*, so supplying it means parsing and re-serialising
the request. **`_CLAUDE_CODE_ASSUME_FIRST_PARTY_BASE_URL` is already eliminated**: it restores
`x-client-request-id` and the 429 did not move.

**The scope is smaller than it looks:** *rewrite only non-streamed Anthropic requests that lack the
block* — exactly the ones failing today — **so every streamed request keeps byte-relay and its
prompt cache untouched.**

***Two things could make it fail even if the block is the cause.*** **`cch` is computed per
request** — seven distinct values across nine — *so a fabricated one fails if it is validated rather
than merely present.* **And the gate is a class of which two members are known**; there may be
others.

***So run the subtractive test first:*** **under the hosts route, where it now works, have the
router STRIP the attribution block and drive a few classifier calls.** *It fabricates nothing and
reuses the setup you have.* **429 returns → the block is the cause and injection is worth building.
429 stays away → injection is wasted work and the cause is still unfound.**

## 21 · ERRAND · high · The fix is built — one session, one environment variable, and it answers

***Group C4 is in and every check is green.*** **The router now puts back the attribution block
Claude Code withholds**, and this is the run that says whether that is enough. *Only you can drive
it: it needs your credential and your machine.*

### Why this one is cheap in a way the last three were not

***No `/etc/hosts`, no TLS terminator, no `sudo`, no DNS pin, no second terminal.*** **One
environment variable, the way anybody would point a client at a proxy.** *That is the whole point —
if it works, the hosts route stops being the supported path and becomes the fallback.*

### The run

1. **`make run-with-attribution`** — terminal 1.
   ***Startup MUST print `EXPERIMENTS ON: add_claude_code_hidden_attribution_block`.*** **If it does
   not, stop**: the config did not take and the run measures nothing. *That line is the only
   confirmation available before the first request.*
2. **`ANTHROPIC_BASE_URL=http://127.0.0.1:8787 claude`** — terminal 2, **auto mode ON**.
3. **`claude --version`**, recorded. *`BUG-001` asks for it by name, and 2.1.267 is what every
   measurement in this phase is against — **a different build makes this a different experiment**.*
4. ***Drive the ten-probe sweep, not a smoke test.*** **`BUG-000`: an absence of failures is what
   every earlier attempt produced and it proved nothing every time.** *Your 2026-09-19 session is
   the shape to repeat — commands that look dangerous and are harmless, including **one that is
   genuinely blocked**.*
5. **Stop, and hand back.** *Reading `router.log` and `calls.csv` is a session's job and does not
   need you.*

### What counts as an answer, and it is not "it worked"

| | |
|---|---|
| ***The pass*** | **No 429 on non-streamed calls, AND a probe that comes back BLOCKED with the verdict in the router's own record.** *Eight allowed and one blocked is what made 2026-09-19 airtight* |
| ***The fail*** | **429s return.** *Then the block alone is not enough — and the next thing to try is condition B, which adds a `cch`. **One line**, because the constant is already there to not-use* |
| ***The trap*** | **No 429s and no blocked probe.** ***That is not a pass.*** *It is the shape of result this phase has mistaken for success four times* |

### Three things to know while it runs

- ***The corpus will NOT show the injected block.*** **It stores what arrived**, and the block is
  added after that. *The proof it fired is the `attribution block added to /v1/messages: N bytes in,
  M out` line in `router.log`.* **If that line never appears, the injection never ran** — and the
  log says why for every request it declined.
- ***This changes the prompt-cache prefix for the requests it touches.*** **Non-streamed only**, so
  the main conversation keeps byte-relay and its cache. *The classifier has no cache worth keeping.*
- ***Only one switch moved.*** *2026-09-19 flipped three at once and could only credit the set. This
  run changes exactly one thing, so whatever it shows is attributable without an argument.*

### What I am not claiming

***It may fail, and the honest reasons are known in advance.*** **The block we send has two fields
and a real one has three to five.** *`cch` is per conversation turn and cannot be computed — a
hardcoded one would repeat on every request, which no real client does, so it is omitted rather than
faked.* **The two-field form is a shape the client itself sends** — the `-p` probes carry no `cch` —
*so it is an observed shape rather than an invention, which is the most that can be said for it.*

**And the gate is a class of which we know two members.** *There may be others, and then no block
helps.*

## 22 · ASK · high · You found it: the block was being switched off by our own README

***`CLAUDE_CODE_ATTRIBUTION_HEADER=0`.*** **You have been setting it every time, because
`README.md` says to** — and it has said so since 2026-08-07, `7cd90f9`, **six weeks before this
phase opened.** *No document states a reason. Its origin is visible in
`reference/architecture.md`, where it sits in the block for pointing Claude Code straight at LM
Studio — where it makes sense — and from there it was copied into the router's quick start and into
`procedures/testing-against-claude-code.md`, which is the procedure for driving exactly these
sessions.*

### The three days read consistently now

| Day | Base URL | The env var | Blocks | `cch` | Non-streamed |
|---|---|---|---|---|---|
| 09-18 | set | ***`=0`*** | **none** | — | **119 × 429** |
| 09-19 | unset, hosts | not used — no base URL to pair it with | 97 | **yes** | all ok |
| **09-20** | **set** | ***dropped*** | **19** | no | classifier ok |

***That separates two things the phase had fused:*** **the env var decides whether the block is
sent; first-party posture decides whether `cch` is in it.** *`ANTHROPIC_BASE_URL` suppresses
nothing, and 09-20 shows it directly.*

***And the disproof was on disk on day one.*** **Two requests on 09-18 carried attribution with the
base URL set** — the `-p` probes. *The phase recorded them and read them as a quirk of `-p`. They
were almost certainly just a command line without the env var.*

### What I have NOT done, deliberately

***I have not touched `README.md`.*** **Removing the line is acting on a conclusion with one
unconfirmed fact in it**, and this phase has done that enough. *It is the first thing the next
session should do once the run below confirms it.*

***And I have not rewritten `BUG-001` or the wiki page.*** **Both carry a banner saying the central
claim is in doubt and why.** *Replacing one unverified conclusion with another is the move that cost
this phase three retractions.*

### The two-minute run that settles it, and it needs you

**Same machine, same session, `ANTHROPIC_BASE_URL` set both times, and the router's own injection
OFF** (`config.yaml`, not `config-attribution.yaml`):

| **A** | ***with*** `CLAUDE_CODE_ATTRIBUTION_HEADER=0` | **429s return** → the cause is named |
|---|---|---|
| **B** | ***without it*** | **429s stay away** → and the fix is deleting a line from a README |

***Please drive harsher probes than 2026-09-20's.*** **Every verdict that day was stage 1, ceiling
severity 25, and stage 2 never ran** — *so there is still no blocked verdict in the record, which is
`BUG-000`'s trap and what entry 21 warned about in advance.* **2026-09-19's blocked probe scored 68.**

### One confirmation I need, because I cannot see your environment

***Did you drop `CLAUDE_CODE_ATTRIBUTION_HEADER=0` for the 2026-09-20 run?*** **Everything above
rests on it.** *Asked rather than inferred, which is the note this repository already keeps.*

### And the good news, which is worth saying plainly

***If run A brings the 429s back, Group C4 is unnecessary and should be deleted rather than
shipped.*** **A router that needs no code to fix this is a better outcome than an injection that
works.** *The two-field block, the hardcoded constants, the byte-relay exception — all of it comes
out, and `BUG-001` closes as an operator-error bug in our own documentation.*

**What that would leave standing is still worth the phase:** *the compression defect was real and
was ours, the gzip `400` was a genuine bug any first-party client meets, and the corpus answered the
whole thing in an afternoon from material already on disk.*
