"""Facts about Claude Code's own requests to Anthropic, and the one thing the router does with them.

**This module exists because `proxy.py` is protocol-neutral and these are one backend's facts.**
Every constant here is a literal measured off the corpus rather than read out of documentation, and
each carries what it was measured against — because a hardcoded value whose provenance is not
written down is indistinguishable from a guess the next reader has to re-derive.

***What this module is for.*** Claude Code decides it is talking to Anthropic by comparing
`new URL(base).host` against the literal string `api.anthropic.com`. **When `ANTHROPIC_BASE_URL`
names anything else, it withholds content** — and every non-streamed `/v1/messages` it sends is then
refused with `429 rate_limit_error`, which makes auto mode's safety classifier unusable through a
proxy. *The one withheld thing that survives into a measured success is an attribution block in the
request body.* **This module rebuilds that block so the router can put it back.**

→ `docs/bugs/BUG-001-non-streaming-messages-rejected-as-rate-limited.md` for the bug,
`docs/wiki/claude-code-first-party-gate.md` for the gate and the block's full anatomy.

***It is off by default and it is the one deliberate exception to byte-relay in this router.***
Everything else here forwards a request body unchanged; `with_attribution` rewrites one. That is
why it is confined to the narrowest case that fixes the bug, and why the config key that enables it
is named after exactly what it does.
"""

from __future__ import annotations

import json
from typing import Any

# The literal text that opens the block. **It looks like an HTTP header and is not one** -- it is
# the start of a string inside the `system` array, and reading the name as a channel cost this
# phase two sessions and a negative experiment that tested nothing.
#
# The client's own internal name for the flag is `forceAttributionHeader`, which is where the
# misreading comes from. `claude --debug api` prints the value as though it were an attribution
# line. It is neither.
ATTRIBUTION_PREFIX = "x-anthropic-billing-header: "

# Claude Code 2.1.267, and `.608` is NOT a build number.
#
# **The fourth component identifies the call site.** Measured over 97 blocks captured on
# 2026-09-19 under the hosts route: one install, one build, one day, five values --
#
#     .608  every auto-mode safety classifier request and nothing else (25, both stages)
#     .d18  the main conversation            (45, streamed)
#     .daa  the haiku auxiliary calls        (14, streamed)
#     .682  claude-opus-5, not a classification (13, streamed)
#     .0a3  the `-p` probes                  (2, and the only `sdk-cli` ones)
#
# ***So it cannot be derived from anything the request carries.*** The `user-agent` reads
# `claude-cli/2.1.267 (external, cli)` -- three components where the block wants four -- and the
# suffix appears in no header, no body field and no handshake. Hardcoding is not a shortcut here;
# it is the only option, which is why this comment exists instead of a parser.
#
# **`.608` is the right value for what this router injects into.** The classifier is the only
# non-streamed call site ever observed carrying a block, and injection is confined to non-streamed
# requests. *The unobserved tail: on 2026-09-18 there were 9 non-streamed `claude-opus-5` requests
# and 1 haiku that were not classifications, and no non-streamed request outside the classifier has
# ever been seen carrying a block -- so what they would send is unknown rather than known-different.*
#
# Instrument: `docs/milestone-2-corpus/phase-14-rate-limit-headers/evidence/attribution-block-anatomy.sh`
CC_VERSION = "2.1.267.608"

# `cli` interactively, `sdk-cli` under `claude -p`. **The `-p` path is not the one that fails**, and
# this router's injection never sees it: a `-p` run sends its own block already.
CC_ENTRYPOINT = "cli"

# Three fields a real block can carry that this one NEVER does, and each omission is a decision.
#
#   cch            Per conversation TURN, not per request -- the classifier's two stages share one
#                  value, and so do two main-conversation calls in one turn. 5 hex characters,
#                  algorithm unknown, and it cannot be computed from anything the router holds.
#                  **A hardcoded one would repeat on every request**, which is visibly unlike a
#                  client that sent 74 distinct values across 97 blocks, so a stale value is worse
#                  than none. ***The two-field form is a shape the client itself sends***: the `-p`
#                  blocks carry no `cch` at all, so leaving it out reproduces an observed shape
#                  rather than inventing one.
#
#   cc_prompt_id   A UUID, repeating across the requests of one turn. **Neither kind of request this
#                  module touches ever carries one** -- 0 of 25 classifier calls, 0 of 14 haiku.
#
#   cc_prev_req    The `req_011C...` id Anthropic issued for the PREVIOUS reply. Also never present
#                  on the requests this touches -- and worse than merely unnecessary: it is a real
#                  identifier that refers to something, so fabricating one is the single kind of
#                  invention with no honest version. *The router could supply it truthfully one day,
#                  since it sees both legs and already allowlists `request-id`; it does not need to.*
#
# The reasoning is in `docs/milestone-2-corpus/phase-14-rate-limit-headers/notes.md`.


def attribution_block() -> str:
    """The block, as a string, with the two fields that can be known.

    **Takes no argument, because nothing in the request can inform any field it carries.** That is
    the honest summary of everything above: two hardcoded values and three deliberate omissions.
    """
    return f"{ATTRIBUTION_PREFIX}cc_version={CC_VERSION}; cc_entrypoint={CC_ENTRYPOINT};"


def carries_attribution(system: list[Any]) -> bool:
    """Whether a `system` array already holds an attribution block.

    **Matched on the prefix, not on the whole string**, because a real block carries `cch` and the
    chaining fields and ours does not — an equality test would find nothing and inject a second one.
    """
    return any(
        isinstance(element, dict)
        and isinstance(element.get("text"), str)
        and element["text"].startswith(ATTRIBUTION_PREFIX)
        for element in system
    )


def with_attribution(body: bytes) -> tuple[bytes | None, str]:
    """Return `body` with the attribution block prepended to `system`, or `None` and why not.

    ***Two things, not one***, in the shape `recorded_headers` already uses here: the caller needs to
    log why a request it expected to rewrite went out untouched, and a bare `None` cannot say.

    **The block goes FIRST in the array**, which is where Claude Code puts it — measured on
    2026-09-19, session `20260919-1`, where element 0 is the block and element 1 is the classifier's
    own system prompt. It is a plain `{"type": "text", "text": ...}` with **no `cache_control`**,
    also as measured.

    ***Every refusal below is a case where rewriting would be a guess***, and this module would
    rather relay a byte-perfect request that fails than a rewritten one that fails differently:

    - **not JSON, or not an object** — nothing to put a block into
    - **`system` missing, or not a list** — the API also accepts a plain string there, and turning a
      string into an array is a larger change to the body than this is allowed to make. *Claude Code
      sends an array; a caller that does not is not the one this exists for.*
    - **already carries a block** — a first-party client under the hosts route sends its own, and a
      second one is not an improvement

    **The caller is responsible for the other three conditions** — Anthropic backend, non-streamed,
    and an uncompressed body — because all three are known before this is worth parsing for.
    """
    try:
        payload = json.loads(body)
    except (ValueError, UnicodeDecodeError):
        return None, "the body is not readable JSON"
    if not isinstance(payload, dict):
        return None, "the body is not a JSON object"

    system = payload.get("system")
    if system is None:
        return None, "the body carries no 'system' field"
    if not isinstance(system, list):
        return None, "the body's 'system' is not an array, so there is nowhere to put a block"
    if carries_attribution(system):
        return None, "the body already carries an attribution block"

    payload["system"] = [{"type": "text", "text": attribution_block()}, *system]
    # `separators` matters: `json.dumps` puts a space after every `:` and `,` by default, which
    # would inflate a 128 KB body for nothing. This is the compact form the client itself sends.
    return json.dumps(payload, separators=(",", ":")).encode(), ""
