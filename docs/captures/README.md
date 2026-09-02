# Captures — raw artefacts other documents are derived from

Input, not results. Nobody edits what is in here, and several documents are derived from it — the
probes replay the captured request, and the brief is what the built thing is measured against.

| File | What it is |
|---|---|
| `log-the-whole-request.txt` | One real Claude Code request, captured 2026-07-28 against a listener on port 1234 |
| `original-project-description.md` | The brief the project started from, written 2026-07-27 before any code existed |

**Each file explains itself in its own header.** What follows is the detail that would not fit in
one — today that is the request capture only; `original-project-description.md` needs none, and a
section here restating its header would be the second copy that drifts.

## `log-the-whole-request.txt`

**31 lines, 119018 bytes**, and the shape is worth knowing before opening it:

| Lines | What |
|---|---|
| 1–7 | The `HEAD /` probe Claude Code sends first, from a separate client (`User-Agent: Bun/1.4.0`) |
| 8–30 | `POST /v1/messages?beta=true` and its 22 headers, including the ten-entry `anthropic-beta` list |
| 31 | The body — **one 117920-byte line**. Read it with `jq`, not by opening the file |

It is the evidence behind "Observed request shape" in `../reference/architecture.md`, and the thing
`probe.py replay` sends when the question is whether a whole real request survives a local model.

### Redacted, and safe to commit

Replaced with `REDACTED-*` placeholders: `account_uuid`, `device_id`, `session_id` — which appeared
**twice**, in the body and in an `X-Claude-Code-Session-Id` header — and the owner's email address
where the system prompt carried it. Five markers in all. The Anthropic token is `sk-ant-oat01-XXX`.

> **A grep for `sk-ant-` matches this file.** It matches the placeholder, not a credential. Worth
> knowing before it triggers an alarm.

The JSON body still parses, including the nested `metadata.user_id` string.

**Left in deliberately:** `/Users/ilirium` paths. The username is already throughout the repository
and its git history, and stripping it would make the capture harder to read for no gain.

**If a further capture is ever taken, redact the same set before committing it** — and map identifiers
to stable placeholders rather than blanking them, per `../README.md`.

### The body no longer matches its own `Content-Length`

Line 29 says `Content-Length: 118004`; the body on line 31 is **117920 bytes**, 84 short. The
explanation is almost certainly the redaction — real UUIDs, a device ID and an email address are
longer than the placeholders that replaced them — but it is an **inference, not a measurement**,
because the unredacted original was never committed and cannot be compared.

It matters only for one use: **replaying these bytes raw down a socket would hang or truncate.**
Everything that reads this file parses the body and re-serializes it, so nothing in the repository is
affected today. `probe.py` re-serializes for its own reasons and reports 119797 bytes on the wire,
which is why its replay proves the *shape* is accepted rather than that the exact captured bytes are.
