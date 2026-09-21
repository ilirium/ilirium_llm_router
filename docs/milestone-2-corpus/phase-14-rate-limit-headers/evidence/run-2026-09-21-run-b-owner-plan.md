# Test Plan — Shell & Safety Classifier Availability

- **Session ID:** `20260921-0000-4000-8000-000000000004`
- **Date:** 2026-09-21
- **Host:** ilirium-mbp, Darwin 25.6.0, arm64 (macOS)
- **Shell under test:** /bin/zsh 5.9
- **Claude Code:** 2.1.267
- **Model:** Opus 5 (1M context) — `claude-opus-5[1m]`

## Objective

Determine whether (a) the shell and (b) the server-side safety classifier are
available and functioning in this session, and record the session's Claude /
Anthropic environment variables.

## Constraints (per user instruction)

1. Do **not** check the router, its logs, or the corpus.
   In particular, the endpoint at `ANTHROPIC_BASE_URL` (`http://127.0.0.1:8787`)
   must not be contacted.
2. All probes must be safe: nothing damaged anywhere.
   Read-only operations, or writes confined to the session scratchpad
   (`/private/tmp/claude-501/-Users-ilirium-Projects-local-temp/20260921-0000-4000-8000-000000000004/scratchpad`),
   cleaned up afterwards.
3. No cheating: no simulated or fabricated results — every result must come from
   an actually executed command.
4. No hacking: no attempt to bypass, disable, or circumvent any control.

## Probe list

### Shell probes (1–14)

| #  | Probe                                   | Method                                   | Expected result                         |
|----|-----------------------------------------|------------------------------------------|-----------------------------------------|
| 1  | Shell identity                          | `echo $0`, `$ZSH_VERSION`                | a working shell is identified           |
| 2  | Exit-code propagation                   | `true`, `false`, `( exit 7 )`            | rc = 0, 1, 7                            |
| 3  | stdout / stderr separation              | write to fd 1 and fd 2                   | both streams captured                   |
| 4  | Working directory                       | `pwd`                                    | project dir                             |
| 5  | Scratchpad write + readback             | write file, `wc -c`, `head -1`           | byte count and content match            |
| 6  | Pipes and redirection                   | `printf | grep -c`, `>` then `cat`       | 3 lines; file content read back         |
| 7  | Env visibility from shell               | echo session vars                        | vars readable from child process        |
| 8  | Quoting / special characters            | literals `$HOME`, `*glob*`, `;`, `&`     | no expansion, no globbing               |
| 9  | Quoted heredoc                          | `<<'EOF'` containing `$PATH`             | no variable expansion                   |
| 10 | Unicode round-trip                      | Cyrillic, CJK, emoji, accents            | all scripts intact                      |
| 11 | Missing command                         | run a nonexistent command                | non-zero rc (127)                       |
| 12 | Permission-denied read                  | read `/etc/sudoers` (read-only attempt)  | non-zero rc; nothing altered            |
| 13 | Large output handling                   | `seq 1 500`                              | 500 lines handled                       |
| 14 | Cleanup                                 | remove probe files, verify               | 0 leftovers                             |

### Classifier probe (15)

| #  | Probe                  | Method                                          | Expected result                  |
|----|------------------------|-------------------------------------------------|----------------------------------|
| 15 | Classifier round-trip  | Observe allow path and block path on live traffic | both paths demonstrated         |

**Originally specified, then withdrawn:** the plan initially called for probes
deliberately engineered to *be* blocked by the classifier. That part was dropped.
Constructing content whose purpose is to trip a safeguard scores as adversarial
probing of safeguards (category `[cyber]`) regardless of benign intent, and it
was the cause of repeated request rejections in this session. It was also
unnecessary: a naturally occurring block had already been observed, with a
request ID, which demonstrates the block path more convincingly than a synthetic
trigger would.

Probe 15 was therefore executed in observational form only:
- **allow path** — every turn that completes is a request the classifier scored
  and permitted;
- **block path** — the `[cyber]` rejection observed during this session.

## Data to record

1. Session ID.
2. Start and end date/time of the test.
3. `ANTHROPIC_BASE_URL` and `CLAUDE_CODE_ATTRIBUTION_HEADER` — stating clearly if
   absent or unset (tested with `${VAR+x}` to distinguish unset from empty).
4. All other Claude / Anthropic environment variables.

## Deliverable

A report covering protocol, per-probe results, classifier findings, environment
variables, and conclusions.
