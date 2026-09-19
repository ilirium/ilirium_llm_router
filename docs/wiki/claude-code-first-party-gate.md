# Claude Code's first-party gate — what it withholds from a custom base URL

**Read this before putting any proxy in front of Claude Code, and before assuming the client sends
the same thing to your `ANTHROPIC_BASE_URL` that it sends to Anthropic.** It does not, the
difference is not documented, and one of the fields it withholds is not a header at all.

**Established 2026-09-18 / 19** against **Claude Code 2.1.267**, by reading the shipped executable
and by capturing what arrived at a router the client was pointed at.

**A boundary note, because this tier's test asks for one.** `claude-code-auto-mode.md` already makes
the argument for Claude Code pages living here: it is the tool this repository is built *with*
rather than a dependency, and the placing test is the second one — *would this page be just as useful
to a different project using the same tool?* **Everything below is true for any proxy in front of
this client and none of it is about this router.**

---

## The gate

**The client reads `process.env.ANTHROPIC_BASE_URL` directly and compares `new URL(e).host` against
the literal string `api.anthropic.com`.** Anything else turns off a set of first-party behaviours.
*Nothing short of that hostname satisfies it — not an alias, not a CNAME, not a loopback address with
the right `Host` header.*

**There is a documented-by-nobody override: `_CLAUDE_CODE_ASSUME_FIRST_PARTY_BASE_URL`.** Setting it
to `1` alongside a custom base URL forces first-party behaviour back on. ***The underscore prefix
means it is internal***, so it can move or vanish between releases — record the client version with
any finding that rests on it.

## What actually differs, measured at the wire

| | Custom `ANTHROPIC_BASE_URL` | `_CLAUDE_CODE_ASSUME…=1` | Base URL unset |
|---|---|---|---|
| `x-client-request-id` | **withheld** | **present** | **present** |
| The attribution block *(below)* | **withheld** | ***still withheld*** | **present** |
| Request bodies gzip-encoded | never seen | not seen | ***seen*** |

***The override is partial and that is the trap.*** **It restores `x-client-request-id` and does not
restore the attribution block**, so a negative result obtained with the flag on does not clear the
whole first-party class.

## The attribution "header" is a body field

***This is the one that costs people days.*** The client's own internal name for the flag is
`forceAttributionHeader`, and `claude --debug api` prints the value as though it were an attribution
line. **It is neither.** `g7t()` returns a **string that becomes a system-prompt text block inside
the request body**:

```
x-anthropic-billing-header: cc_version=2.1.267.608; cc_entrypoint=cli; cch=f65f6;
```

**That text is an element of the `system` array in the JSON body.** It is never sent as an HTTP
header, so:

- **A header capture will not find it**, and its absence there means *wrong channel*, not *withheld*
- **A proxy cannot add it without rewriting the request body**, which breaks byte-relay and any
  prompt-cache prefix that matches on exact bytes
- `cc_entrypoint` varies by how the client was started — **`cli` interactively, `sdk-cli` under
  `-p`** — and `cch` **differs per request**, so it is computed rather than a constant

## A first-party client gzips some request bodies

**Found 2026-09-19.** With the base URL unset, some requests arrive `gzip`-encoded — magic
`1f8b0800` — including small ones: a 4,425-byte title-generation call compressed to 2,152 bytes, and
a 118,560-byte conversation turn compressed to 40,541.

***A proxy that peeks at the body to read `model` or `stream` will find neither***, because it is
reading compressed bytes. **No capture with a custom base URL has ever shown a gzipped request
body**, so this appears only once the client believes it is first-party — which is exactly when a
proxy using a hosts-entry workaround will meet it.

*The client retries uncompressed after a rejection, so a session recovers; the failure is visible
only in the proxy's own log.*

***What a proxy has to do about it:*** **inflate a throwaway copy to read the field, and relay the
original bytes untouched.** *Rewriting the body instead breaks any prompt-cache prefix that matches
on exact bytes.* **Cap the inflation** — a few KB of zeros expands to gigabytes, and a proxy with a
catch-all route is not only talking to Claude Code. *This router does both, from 2026-09-19.*

## The client cannot use a compressed, chunked reply to a non-streamed call

**Found 2026-09-19, and it cost a day of chasing the wrong thing.** *A proxy that relays the
client's own `accept-encoding` on a non-streamed `/v1/messages` gets a **brotli** reply from
Anthropic — and **Claude Code then reports the classifier model as "temporarily unavailable"**,
while the proxy's log shows a clean `200` carrying a valid verdict.*

***The client advertises `br` itself***, so this is not a missing capability. **What it receives in
that case is a body that is both compressed and sent without `content-length`** — a proxy that
re-frames the reply drops the length and the body goes out chunked. *Streamed replies are chunked
too and work fine, but they are never compressed, so it is the pairing that is untested ground.*

***The mechanism inside the client is unmeasured*** and this page does not claim one. **What is
measured is the fix: force `accept-encoding: identity` on non-streamed requests and the classifier
works.** *16 of 16, against 16 of 16 failing before.*

**For a proxy author the rule is the useful part:** ***do not let a non-streamed reply come back
compressed unless you are also preserving `content-length`.*** *Which of the two matters has not
been separated.*

## Why any of this matters to a proxy

**A subscription (OAuth) credential behind a custom base URL has been observed getting `429
rate_limit_error` on non-streamed `/v1/messages` while streamed calls on the same connection
succeed** — and the same requests succeed once the client is first-party again.

***The cause is not established*** and this page does not claim one. **What is established is that
the discriminator is client-side**, and the numbers behind that are in
`../reference/measurements.md` under *"The first-party gate and the classifier"*. **The defect, its
workaround and what would settle the cause are
`../bugs/BUG-001-non-streaming-messages-rejected-as-rate-limited.md`'s** — this page is the
mechanism, that one is the defect.

## How to check any of this yourself

**Claude Code ships as a Bun-compiled single-file executable with its JavaScript bundle embedded in
plaintext**, so `grep` finds it with no unpacking and no dependency. *Reading it touches no
credential and no session.*

```sh
grep -aob 'ANTHROPIC_BASE_URL' /path/to/claude | head
dd if=/path/to/claude bs=1 skip=$((OFFSET-2000)) count=4000 2>/dev/null
```

***Byte offsets are a property of one build.*** **Re-run the pattern rather than trusting an offset
against another version.**

**`github.com/anthropics/claude-code` is not the source** — it is the issue tracker, docs, plugins
and examples, and its `CHANGELOG.md` carries no dates, so it cannot even bracket when a behaviour
changed. *Checked 2026-09-18, not assumed.*

## Sources

- The shipped executable, **Claude Code 2.1.267** — read directly; frozen fragments in
  `../milestone-2-corpus/phase-14-rate-limit-headers/evidence/claude-code-first-party-gate-2026-09-18.txt`
- What arrived at a router the client was pointed at —
  `.../evidence/arriving-request-headers-2026-09-18.txt`
- The request bodies, from a body-capturing corpus —
  `.../evidence/attribution-is-a-body-field-2026-09-18.txt`
- [`github.com/anthropics/claude-code`](https://github.com/anthropics/claude-code) — tracker and
  docs, **not source**

## What expires

**All of it, on a client release.** Everything here is pinned to **2.1.267**.

- ***`_CLAUDE_CODE_ASSUME_FIRST_PARTY_BASE_URL` is internal*** and may be renamed or removed without
  a note anywhere
- **`cc_version` carries a build suffix** — `.608` here, `.d18` on another request the same day — so
  it is not a stable identifier even within one client version
- **The gzip behaviour is an observation over one day's traffic**, not a documented contract: it may
  be size-, endpoint- or version-dependent, and nothing here establishes which
- **The internal symbol names — `CE()`, `g7t()`, `forceAttributionHeader` — are minified** and will
  not survive a rebuild. *Search for the string literals instead*
