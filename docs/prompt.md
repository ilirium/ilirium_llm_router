# The next session's prompt

*The one file in `docs/` allowed to go stale, per `README.md` — which is why it is rewritten at each
handoff rather than left. **Replaced 2026-09-18 (evening)**, mid-phase rather than at a merge.
Whatever comes next replaces it again.*

---

**Phase 14 is OPEN and IN FLIGHT. Nothing is merged.** Work in
`/Users/ilirium/Projects/local/ilirium_llm_router/phase-14-rate-limit-headers` — *that worktree, not
`main`. A session started in `main` sees none of this.* Branch
`feat/phase-14-rate-limit-headers`, forked from `main` at `ac2976e`.

***The first thing to know is that an experiment is set up, not run, and the owner runs it on
2026-09-19.*** **Do not start anything that would disturb it. Read `for-the-owner.md` entry 14
before touching the worktree.**

*No commit count is written here. A count written at a handoff is wrong at the next commit, and
this repository has recorded that defect five times.*

## Read these, in this order

1. **`docs/status.md`** — first, every session. The only file that holds state.
2. **`.../phase-14-rate-limit-headers/for-the-owner.md`** — ***fourteen entries now, and five were
   added on 2026-09-18 evening.*** **Entries 10–14 are the live ones.** Read it before `plan.md`.
3. **`.../phase-14-rate-limit-headers/notes.md`** — long, and written while the work ran. **Read it
   by section**, per `CLAUDE.md`. *Its last three sections are the evening's, and one of them
   retracts an earlier one.*
4. **`.../phase-14-rate-limit-headers/plan.md`** — its register is where every name and number is.

## What is waiting for the owner, and it is the whole of the next step

**The hosts-entry experiment. Built 2026-09-18, run 2026-09-19.** *Chosen by the owner over
patching the client binary.*

```
Claude Code (ANTHROPIC_BASE_URL unset)
  -> api.anthropic.com:443      [/etc/hosts -> 127.0.0.1]
  -> evidence/tls-terminator.py [sudo; mkcert certificate]
  -> the router on 8787         [unchanged]
  -> evidence/run-pinned.py     [pins api.anthropic.com to its real address]
  -> Anthropic
```

***`for-the-owner.md` entry 14 is the complete runbook*** — seven steps, the exact commands, what
each failure mode looks like, and the rollback. **Do not reconstruct it from this file.**

**Why it is worth a session:** ***it is the only remaining experiment that makes the client fully
first-party while still routing through the router.*** **If the 429 survives it, the entire
client-side variable is eliminated** and what is left is the TLS fingerprint and connection reuse —
both expensive. **If it goes away, `BUG-001` gets a real workaround.**

***`config-hosts.yaml` and `make run-hosts` are new and both come out with the experiment.*** *The
config is `config-boringssl.yaml` with the egress hop removed, which means **the corpus is ON** —
without that the run captures no bodies, and the corpus is what answered the attribution question
when nothing else could.* **`make run-hosts` resolves the address via `@1.1.1.1` and starts the
router under `run-pinned.py`.**

**Four things about it that a session will otherwise get wrong:**

- ***The hosts line redirects the session you are talking in.*** **It is machine-wide.** If TLS is
  not right, the conversation dies mid-turn with the line still in place. **It goes in LAST**, and
  `curl --resolve api.anthropic.com:443:127.0.0.1 https://api.anthropic.com/api/hello` proves the
  whole chain without touching `/etc/hosts`.
- ***`/etc/hosts` makes the router resolve `api.anthropic.com` to itself.*** That is the loop
  `run-pinned.py` exists to break. **Take the real address from `dig +short @1.1.1.1`** — a plain
  `dig` answers `127.0.0.1` once the line is in. *The script refuses a loopback value rather than
  looping.*
- **The router has no TLS at all.** `Server` is host and port only. That is why a terminator exists
  and why it needs `sudo`.
- ***The arrival sampler will miss the classifier again.*** *The corpus captures every body, so
  nothing is lost — but the log line will once more describe the wrong request.* **Entry 11.**
- **`mkcert -install` puts a CA in the system trust store.** *Reversible with `mkcert -uninstall`,
  and it is the owner's to run, not a session's.*

## What is established, and it is a lot

| | |
|---|---|
| **The rejection is Anthropic's own** | Every one carries a distinct `request_id` |
| **A `429` carries no metering at all** | No `retry-after`, no bucket, not even an unlisted one |
| **A `200` on the same connection carries twelve** | `allowed` at **0.52 / 0.59**, and at **0.11 / 0.01** in the later run — ***quota is dead twice over, and that pair is what the upstream issues need*** |
| **The classifier works DIRECT and fails ROUTED** | Same credential, machine, client version, afternoon |
| **The router alters no header** | Computed from a capture: nothing dropped, nothing added |
| **A Chrome TLS fingerprint is rejected too** | So it is not a bot score against scripted stacks |
| **The first-party gate is real, and it has a switch** | `_CLAUDE_CODE_ASSUME_FIRST_PARTY_BASE_URL`. **Run 2026-09-18: `x-client-request-id` reaches the router for the first time, and the 429 does not move** |

***Thirteen hypotheses are eliminated by measurement.*** *The cause is **NOT identified. Say so.***

## Five things you will get wrong here

- ***The "attribution header" is not a header.*** **It is a system-prompt block inside the request
  body** — `x-anthropic-billing-header: cc_version=…` is a *string in `system`*, and
  `claude --debug api` printing it as "an attribution line" is what fooled this phase for a day.
  ***So `C2d` added an HTTP header the client never sends as one: the negative was real and the
  subject was not.*** **Entry 13.** *The check that settles it is free —
  `extract --format bodies` over `logs/corpus/2026-09-18`, material already on disk.*
- ***A one-shot sample latch decides in advance which request is interesting, and it has been wrong
  three times.*** **The 14:52 run spent the non-streamed latch on a 323-byte `haiku` warm-up**; the
  classifier requests are **127,949 bytes** and none was sampled. **So the thing that run existed to
  measure is still unmeasured.** ***Entry 11 puts three fixes to the owner and nothing is chosen
  yet*** — it changes `src/`, so propose before implementing.
- ***Three experiments are live in `src/` and the owner chose to keep them.*** **Do not revert
  without asking.** *One has a standing cost: the corpus stores non-streamed response bodies
  **brotli-compressed**, so `extract` hands a reader bytes where it used to hand them JSON.* **The
  imitation header can now be argued out on its own merits** — it imitates something that is not a
  header — **but that is still the owner's call.**
- **`branch-index.py --write` deletes the `temp/to-run-server` row**, on this branch and on a clean
  `main` alike, and `--check` says only `STALE`. **`IDM-001` says that row must not be removed and
  puts `--write` as the last step of every merge.** **`main` is STALE right now for this reason
  alone.** → entry 4.
- **`link-check.py`'s count is a property of the worktree.** **112 broken here**, *unchanged by the
  evening's work*; **92 on `main`.** Compare within one tree or not at all.

## Reading the client, which is new and cost nothing

**Claude Code ships as a Bun-compiled single-file executable with its JavaScript bundle embedded in
plaintext.** `evidence/binary-extract.sh` prints readable context around any string in it — *`grep`
and `dd`, no unpacking, no dependency, **no credential and no session***.

***`github.com/anthropics/claude-code` is NOT the source*** — issue tracker, docs, plugins,
examples, and a `CHANGELOG.md` with **no dates**, so it cannot even bracket `BUG-001`'s
2026-08-21 → 2026-08-24 regression window. *Checked, not assumed.*

**Byte offsets in the frozen fragments are a property of one build.** *Re-run the patterns rather
than trusting an offset against another version, and record the client version with any finding.*

## Open, and the owner's to choose between

- **Entry 11's sampler fix** — three options, none chosen, and it changes `src/`.
- **Group D has never started** — where the headers durably live. ***Still the milestone plan's
  "Phase 14's plan cannot skip the question"***, deferred with the values now in hand. **Only the
  owner can overturn the `calls.csv` non-goal.**
- **The upstream report is not sent.** `BUG-001` now holds what both issues stall on and **neither
  has been told any of it.** *`status.md`'s item 2, unchanged since 2026-08-25.*
- **The Bun exact-fingerprint test**, and **connection reuse** — entry 8, both still untouched.
- **`BUG-001` is retracted and corrected on this branch, not on the trunk.** It reaches `main` only
  at the merge.
- **Everything the 2026-09-17 handoff listed is still open**: the corpus tools undriven by hand,
  `BUG-001` unreported, `BKL-0017`, `EPD-001`, `EPD-002`, `BKL-0007`, and `git fetch origin`.

## What is finished, so nothing is half-done

**Groups A, B and C are complete; Group C2's eliminations are written into `plan.md` after the
fact.** **The working tree is clean and every finding is committed.** *`src/` is untouched by the
evening's work — checked with `git diff --stat`, not assumed. The Makefile gained one target and
the repository one config file, which is why the suite was re-run rather than quoted forward.*

**Every check is green, re-run at this handoff: 475 tests, 24/24 mutations, `make lint` clean at
the pinned `0.16.1`, `backlog-index --check`, and `link-check.py` at 112 broken — unchanged.** *`branch-index`
is STALE for the reason in entry 4 and **must not** be fixed with `--write`.*

*Push state was deliberately not checked at this handoff, on the owner's instruction — as at the
last one.*

## The working agreement still applies

`CLAUDE.md`, in full. Three earned their place again on 2026-09-18:

**Exercise it before committing** — and the sharper version this phase has now paid for four times:
***a green check tells you the instrument works, never that it is aimed correctly.*** *The evening's
own instrument shipped a defect of exactly that kind and it is recorded rather than quietly fixed.*

**Ask before inferring.** *The owner is present, and he has now twice supplied the thing no
experiment did* — the direct-versus-routed control, and the challenge to whether
`_CLAUDE_CODE_ASSUME_FIRST_PARTY_BASE_URL` was an env var at all. → the memory note
`ask-rather-than-infer-about-the-setup`.

**Raise it rather than burying it, and say it is wrong rather than working around it.** ***Three
retractions now sit in `notes.md`, each one a real observation carrying a claim it did not make***:
"Anthropic sent this" read as "Anthropic is at fault"; a confirmed mechanism read as a confirmed
cause; and a confirmed *name* read as a confirmed *channel*.
