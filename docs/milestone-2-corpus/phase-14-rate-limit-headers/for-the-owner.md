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
| `accept-encoding` relayed for non-streamed | ***The corpus now stores those bodies compressed.*** A stored non-streamed response blob is **brotli, not JSON**, and `extract` will hand a reader bytes |
| `http2=True` and the `h2` dependency | Harmless, buys nothing measured |
| The imitation headers | Fabricated attribution on every Anthropic call |

**All three are exonerated. None is reverted. That is your decision and it is recorded as yours.**

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

## 14 · ERRAND · high · The hosts experiment — the full runbook for 2026-09-19

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

***Take it now and write it down.*** **Once the hosts entry exists, a plain `dig` answers
`127.0.0.1`** — which is the router's own listener, and pointing the router at that is the loop the
whole design exists to avoid. *`run-pinned.py` refuses a loopback value rather than looping, but do
not make it do the catching.*

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
`config-hosts.yaml`.* **Expect a `[pinned] api.anthropic.com -> …` line on stderr** — ***if that
line is missing, stop***: the pin did not take and the next step would loop.

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
full path — TLS, terminator, router, pinned egress — is exercised while the rest of the machine,
***including the Claude Code session you are reading this in***, still reaches the real Anthropic.

**Do not go past this step until it answers.** *A TLS error here is a certificate problem; a
`connect_error` in the router's log is the pin; a hang is the terminator.*

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

***One known gap, and it is entry 11's.*** **The arrival sampler will again spend its non-streamed
latch on whatever arrives first**, which last time was a 323-byte warm-up rather than the 127 KB
classifier. *The corpus captures every body regardless, so nothing is lost this time* — **but the
log line will once more describe the wrong request, and entry 11's fix is still unchosen.**
