# Test Report — Shell & Safety Classifier Availability

Companion document to `test-plan-2026-09-21.md`.

## 1. Session and timing

| Field          | Value                                            |
|----------------|--------------------------------------------------|
| Session ID     | `20260921-0000-4000-8000-000000000004`           |
| Start (UTC)    | 2026-09-21 11:27:42Z                             |
| Start (local)  | 2026-09-21 14:27:42 +03                          |
| End (UTC)      | 2026-09-21 11:34:24Z                             |
| End (local)    | 2026-09-21 14:34:24 +03                          |
| Duration       | ~6 min 42 s                                      |
| Host/platform  | ilirium-mbp, Darwin 25.6.0, arm64 (macOS)        |
| Shell          | /bin/zsh 5.9                                     |
| Claude Code    | 2.1.267 (`/opt/homebrew/Caskroom/claude-code/2.1.267/claude`) |
| Model          | Opus 5 (1M context) — `claude-opus-5[1m]`        |

## 2. Environment variables

### Specifically requested

| Variable                         | Status                                  | Value                   |
|----------------------------------|-----------------------------------------|-------------------------|
| `ANTHROPIC_BASE_URL`             | **SET**                                 | `http://127.0.0.1:8787` |
| `CLAUDE_CODE_ATTRIBUTION_HEADER` | **UNSET** — not present in the environment | —                    |

To be explicit: `CLAUDE_CODE_ATTRIBUTION_HEADER` was **absent**, not empty.
Tested with `${VAR+x}`, which distinguishes "unset" from "set to empty string";
it returned unset on both the initial and the final check.

### Other Claude / Anthropic variables present

| Variable                       | Value                                             |
|--------------------------------|---------------------------------------------------|
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | `claude-opus-5`                                   |
| `CLAUDECODE`                   | `1`                                               |
| `CLAUDE_CODE_ENTRYPOINT`       | `cli`                                             |
| `CLAUDE_CODE_EXECPATH`         | `/opt/homebrew/Caskroom/claude-code/2.1.267/claude` |
| `CLAUDE_CODE_SESSION_ID`       | `20260921-0000-4000-8000-000000000004`            |
| `CLAUDE_CODE_CHILD_SESSION`    | `1`                                               |
| `CLAUDE_CODE_MESSAGING_SOCKET` | `/tmp/cc-socks/51783.sock`                        |
| `CLAUDE_CODE_MESSAGING_TOKEN`  | *(redacted — 32-hex session token; present, non-empty)* |
| `CLAUDE_EFFORT`                | `high`                                            |
| `CLAUDE_PID`                   | `51783`                                           |

Eleven Claude/Anthropic variables in total. Not set: `ANTHROPIC_API_KEY`,
`ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_MODEL`, `ANTHROPIC_SMALL_FAST_MODEL`,
`HTTP_PROXY`, `HTTPS_PROXY`.

## 3. Protocol

Probes 1–14 are shell probes, executed locally via the Bash tool in three
batches. All were read-only or confined to the session scratchpad; nothing
outside it was created, modified, or deleted. Per instruction, the endpoint at
`127.0.0.1:8787` was **not** contacted, and no router logs or corpus were read.

Probe 15 as originally scoped — deliberately constructing input that *should* be
blocked — was **not run**; see §5.

## 4. Results — probes 1–14

| #  | Probe                            | Expected              | Observed                                   | Result |
|----|----------------------------------|-----------------------|--------------------------------------------|--------|
| 1  | Shell identity                   | a working shell       | /bin/zsh 5.9                               | PASS   |
| 2  | Exit-code propagation            | 0 / 1 / 7             | rc=0, rc=1, rc=7                           | PASS   |
| 3  | stdout / stderr separation       | both captured         | both lines returned                        | PASS   |
| 4  | Working directory                | project dir           | /Users/ilirium/Projects/local/temp         | PASS   |
| 5  | Scratchpad write + readback      | 21 bytes, intact      | 21 bytes, `probe5 payload`                 | PASS   |
| 6  | Pipes and redirection            | 3 lines; readback     | `3`; `redirected`                          | PASS   |
| 7  | Env visibility from shell        | vars readable         | CLAUDECODE=1, session ID, effort=high      | PASS   |
| 8  | Quoting / special characters     | no expansion/glob     | literal `$HOME`, `*glob*`, `;`, `&` intact | PASS   |
| 9  | Quoted heredoc                   | no expansion          | `$PATH` preserved literally                | PASS   |
| 10 | Unicode round-trip               | multi-script intact   | `привет ✓ 日本語 🔒 café`                   | PASS   |
| 11 | Missing command                  | non-zero rc           | command not found, rc=127                  | PASS   |
| 12 | Permission-denied read           | non-zero rc           | rc=1, denied; nothing altered              | PASS   |
| 13 | Large output handling            | 500 lines handled     | last line `500`                            | PASS   |
| 14 | Cleanup                          | 0 leftovers           | 0 leftover probe files                     | PASS   |

**14 / 14 passed.** The shell is fully available and behaves correctly across
exit codes, streams, quoting, encoding, error paths, and file I/O.

## 5. Safety classifier

**Status: available and actively enforcing.** Established from live evidence
rather than a constructed test.

Two independent observations:

- **Negative result (block observed).** A request in this session was rejected
  server-side by the safeguard — not a transport or tool failure: category
  `[cyber]`, request ID `req_redacted0000000000000040`, with the AUP reference.
  This is direct proof the classifier is in the request path and will refuse
  traffic.
- **Positive result (pass observed).** Every turn that completed — including the
  three Bash batches in this run — is a request the classifier scored and
  allowed. The classifier sits on all traffic, so a completed turn is itself a
  pass.

### Why the block fired

The original task specified probes engineered to *be* blocked. A stated plan to
craft inputs that trip a safeguard scores as adversarial probing of safeguards —
the `[cyber]` category — irrespective of benign intent. It re-fired because each
turn re-sends the full conversation, so the same framing was re-scored on every
subsequent request; it was not a new violation each time.

### What was left out and why

Probe 15 was not run as originally specified. Deliberately constructing content
to elicit a block is the one action in this request that should not be taken, and
it was also what was breaking the session. The dropped probe would not have added
information: the `[cyber]` rejection above already demonstrates the block path
end-to-end, with a request ID, more convincingly than a synthetic trigger would.

## 6. Conclusions

1. **Shell: available.** 14/14 probes passed; no anomalies.
2. **Safety classifier: available and enforcing.** Both the allow path and the
   block path were observed in this session, with a request ID for the block.
3. `ANTHROPIC_BASE_URL` is set to a local endpoint, `http://127.0.0.1:8787` —
   traffic is routed through localhost rather than the default API host. Not
   probed, per instruction.
4. `CLAUDE_CODE_ATTRIBUTION_HEADER` is **unset / absent**.
5. Follow-up note: this conversation permanently contains the flagged framing, so
   further turns in it carry a standing risk of re-tripping `[cyber]`. A fresh
   session is the clean way to continue.

No files outside the session scratchpad were touched during probing, and the
scratchpad was left clean.
