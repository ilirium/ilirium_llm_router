# Evidence for the bug documents

One entry per frozen artefact. Per `../../README.md`'s "Evidence and redaction": what produced it,
what it proves, what was redacted and how, and whether it can be regenerated.

---

## `calls-2026-08-21-to-2026-08-25-redacted.csv`

**Supports:** [`../BUG-001-non-streaming-messages-rejected-as-rate-limited.md`](../BUG-001-non-streaming-messages-rejected-as-rate-limited.md)

**What produced it.** The router's own telemetry, `logs/telemetry/calls.csv` in the `to-run-server`
worktree, written by `stats.py` — one row per call, 20 columns, in **completion order**. Copied out on
2026-08-25 at 14:07 UTC while the router was running and the file was being appended to, so it is a
**frozen slice**, not a live read. 526 lines including the header.

**What it proves.** That non-streamed `POST /v1/messages` was rejected with HTTP 429 categorically
rather than under load:

- 83 of 83 rate-limited calls in the slice are non-streamed; **none of 391 streamed calls is**.
- Three pairs on 2026-08-25 where a streamed request **2.8× larger** to the same model succeeded under
  a second after a non-streamed one was rejected.
- 21 non-streamed `count_tokens` calls succeeded on 2026-08-24, the day 63 of 63 non-streamed
  `/v1/messages` calls failed — which is what narrows the defect to one path rather than to
  non-streaming in general.

**What was redacted, and how.** `session_id` only — 9 distinct values, mapped to `session-01` …
`session-09` in **first-appearance order**, the mapping applied once and the raw values not recorded
anywhere. Placeholders rather than blanking, because which rows shared a session is part of what the
file demonstrates.

`agent_id` was checked and is **empty on every row**, so nothing was mapped for it; this is stated
rather than left silent, because an untouched identifier column and an absent one look identical
afterwards.

**Secrets were checked separately from identifiers**, as the manual requires — the file was scanned
for `sk-`, `bearer`, `authorization` and `api[_-]key` shapes and matched none. It structurally cannot
carry a credential: `calls.csv` records metadata only, never bodies and never headers.

Nothing else was altered. Verified after redaction: 526 lines still present, all 83 non-streamed 429s
preserved, zero remaining UUID-shaped strings.

**Can it be regenerated?** **No.** The source is under `logs/`, which is gitignored and size-rotated,
and the router was live when this was taken. The window 2026-08-21 to 2026-08-25 cannot be
reconstructed once that file rotates. **A comparable slice can be captured again; this one cannot.**

**One caveat a later reader needs.** The slice contains 15 LM Studio calls, all on 2026-08-21, all
outside the defect being documented. They are left in rather than filtered out — a slice edited to fit
its claim is no longer evidence for it.
