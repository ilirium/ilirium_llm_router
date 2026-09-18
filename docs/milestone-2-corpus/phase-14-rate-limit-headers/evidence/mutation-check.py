#!/usr/bin/env python3
"""Does Group B's test set actually test anything? Break the code and see whether it notices.

`CLAUDE.md`: *exercise it before committing; green tests are not evidence.* Phase 13 shipped three
checks that passed while testing nothing, and none was found by reading.

**The one thing this script is built around**: Phase 13's own mutation harness silently never
applied its mutations, which looks identical to a clean pass. So each mutation reports TWO facts
separately -- whether the edit landed in the file, and whether the tests then failed. A mutation
that cannot be applied is a FAILURE of this script, never a pass of the test set.

**What it still cannot tell apart, found by being bitten 2026-09-18.** "the test is vacuous" and
"the mutation did not do what it claimed" produce the identical report. The allowlist mutation was
first written as `... and not print(dict(reply.headers))`, which leaks the headers to **stdout** --
where the assertion, which reads `caplog`, cannot see them. The harness said the test was vacuous.
**The test was fine; the mutation was.** So a surviving mutation is a prompt to read the mutation
first and the test second, and the `why` line on each row is what makes that re-reading possible.

Run from the worktree root:  python3 docs/milestone-2-corpus/phase-14-rate-limit-headers/evidence/mutation-check.py
"""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PROXY = ROOT / "src" / "ilirium_llm_router" / "proxy.py"
TESTS = "tests/test_proxy.py"


@dataclass
class Mutation:
    """One deliberate defect, and the test that has to die when it is introduced."""

    name: str
    old: str
    new: str
    expect_failing: str
    why: str


MUTATIONS = [
    Mutation(
        name="the allowlist stops filtering",
        old="        if lowered in RECORDED_RESPONSE_HEADERS:",
        new="        if True:",
        expect_failing="test_a_header_outside_the_allowlist_never_reaches_the_log",
        why="every header is recorded, so a credential would reach the log",
    ),
    Mutation(
        name="nothing is recorded at all",
        old="            recorded[lowered] = value",
        new="            pass",
        expect_failing="test_a_failed_reply_logs_the_allowlisted_headers_with_their_values",
        why="the values the phase exists to capture are silently dropped",
    ),
    Mutation(
        name="an unlisted bucket is logged WITH its value",
        old='    parts += [f"{name}=<unlisted>" for name in sorted(set(unlisted))]',
        new='    parts += [f"{name}=?" for name in sorted(set(unlisted))]',
        expect_failing="test_an_unlisted_rate_limit_bucket_is_named_but_never_valued",
        why="the names-only promise is the reason the prefix catch is safe",
    ),
    Mutation(
        name="the prefix catch stops catching",
        old="        elif lowered.startswith(RECORDED_HEADER_PREFIX):",
        new="        elif False:",
        expect_failing="test_an_unlisted_rate_limit_bucket_is_named_but_never_valued",
        why="a bucket added by Anthropic later becomes invisible again",
    ),
    Mutation(
        name="an empty header set logs a blank instead of (none)",
        # Anchored on the line above it: `describe_request_headers` ends with the same return, and
        # the harness refused the ambiguous version rather than guessing which one to break.
        old='    parts += [f"{name}=<unlisted>" for name in sorted(set(unlisted))]\n'
        '    return " ".join(parts) if parts else "(none)"',
        new='    parts += [f"{name}=<unlisted>" for name in sorted(set(unlisted))]\n'
        '    return " ".join(parts)',
        expect_failing="test_a_rejection_carrying_no_rate_limit_headers_says_so",
        why="'no buckets named' is the finding, and a blank tail reads as a logging failure",
    ),
    Mutation(
        name="the log fires on success too",
        old="        if reply.status_code >= 400:",
        new="        if reply.status_code >= 0:",
        expect_failing="test_a_successful_reply_never_warns",
        why="every call would log its buckets and drown the file",
    ),
    # The control, added after the first real measurement showed why it was needed.
    Mutation(
        name="the latch never fires",
        old="        if self.fired:\n            return False",
        new="        if True:\n            return False",
        expect_failing="test_the_first_successful_reply_samples_its_headers_once",
        why="the control is silently absent, and the 429's empty header set proves nothing",
    ),
    Mutation(
        name="the latch fires every time",
        old="        self.fired = True\n        return True",
        new="        return True",
        expect_failing="test_the_sample_is_taken_only_once_per_process",
        why="every successful call logs its buckets, drowning the failure lines",
    ),
    Mutation(
        name="a failure consumes the sample",
        old="        if reply.status_code >= 400:\n            # The status is known now;",
        new="        if self.headers_sampled.take() and reply.status_code >= 400:\n            # The status is known now;",
        expect_failing="test_a_burst_of_failures_does_not_consume_the_sample",
        why="a session opening with 429s -- the real one did -- never samples a success",
    ),
    Mutation(
        name="the representative-claim value is recorded after all",
        old='        "anthropic-ratelimit-unified-overage-disabled-reason",',
        new='        "anthropic-ratelimit-unified-overage-disabled-reason",\n'
        '        "anthropic-ratelimit-unified-representative-claim",',
        expect_failing="test_the_representative_claim_is_named_but_its_value_withheld",
        why="a value nobody has established the contents of would start being written down",
    ),
    Mutation(
        name="the unified family falls back out of the allowlist",
        old='        "anthropic-ratelimit-unified-status",',
        new='        "anthropic-ratelimit-unified-status-NOPE",',
        expect_failing="test_the_unified_family_is_recorded_with_its_values",
        why="the only family a subscription credential is actually metered by stops being valued",
    ),
    Mutation(
        name="the probe endpoint can spend the sample again",
        old='        elif request.url.path.startswith("/v1/messages") and self.headers_sampled.take():',
        new="        elif self.headers_sampled.take():",
        expect_failing="test_the_probe_endpoint_does_not_spend_the_sample",
        why="the control samples /api/hello, reports (none), and reverses the phase's conclusion",
    ),
    # The accept-encoding experiment, 2026-09-18.
    Mutation(
        name="a streamed request stops asking for identity",
        old="    if wants_stream:\n        headers.append((b\"accept-encoding\", b\"identity\"))",
        new="    if False:\n        headers.append((b\"accept-encoding\", b\"identity\"))",
        expect_failing="test_a_streamed_request_asks_for_an_uncompressed_reply",
        why="the SSE scanner would be handed compressed bytes and silently find no usage",
    ),
    Mutation(
        name="a non-streamed request goes back to forced identity",
        old='        dropped.discard("accept-encoding")',
        new="        pass",
        expect_failing="test_a_non_streamed_request_relays_the_callers_own_accept_encoding",
        why="the experiment silently stops running while still looking like it does",
    ),
    # The imitation experiment, 2026-09-18.
    Mutation(
        name="the imitation is sent to LM Studio too",
        old='            + (imitation_headers(request) if name == "anthropic" else []),',
        new="            + imitation_headers(request),",
        expect_failing="test_the_imitation_never_reaches_lmstudio",
        why="a local backend is handed client attribution it has no use for",
    ),
    Mutation(
        name="the imitation overrides what the caller sent",
        old='    if "x-anthropic-billing-header" not in present:',
        new="    if True:",
        expect_failing="test_the_imitation_never_overrides_what_the_caller_sent",
        why="a client that sends its own attribution has it silently replaced",
    ),
    Mutation(
        name="an unrecognised client is imitated anyway",
        old="    if match is None:",
        new="    if False:",
        expect_failing="test_an_unrecognised_client_is_not_imitated",
        why="a guessed shape is sent for a client nothing has ever measured",
    ),
    Mutation(
        name="cc_prompt_id becomes a constant",
        old="            f\"cc_prompt_id={uuid.uuid4()}; \"",
        new='            f"cc_prompt_id=00000000-0000-0000-0000-000000000000; "',
        expect_failing="test_each_call_gets_its_own_prompt_id",
        why="per-prompt on the direct path, so a constant is a visible tell",
    ),
    # The arriving-request sampler, 2026-09-18.
    Mutation(
        name="the arriving sampler logs every header by value",
        old="        if name in RECORDED_REQUEST_HEADERS:",
        new="        if True:",
        expect_failing="test_the_arriving_sample_never_logs_the_credential",
        why="the credential arrives on every request and would go straight into the log file",
    ),
    Mutation(
        name="one arrival latch instead of one per shape",
        old="        if request.url.path.startswith(\"/v1/messages\") and self.arrival_sampled[\n"
        "            bool(call.stream)\n"
        "        ].take():",
        new='        if request.url.path.startswith("/v1/messages") and self.headers_sampled.take():',
        expect_failing="test_the_arriving_request_is_sampled_once_per_shape",
        why="only the shape that arrives first is ever sampled, and the pair IS the measurement",
    ),
    Mutation(
        name="the arriving sampler sorts the headers",
        old="    return \" \".join(parts) if parts else \"(none)\"\n\n\ndef response_headers",
        new="    return \" \".join(sorted(parts)) if parts else \"(none)\"\n\n\ndef response_headers",
        expect_failing="test_the_arriving_sample_preserves_header_order",
        why="header order is a difference a client could have, and sorting hides the quarry",
    ),
    # The HTTP/2 experiment, 2026-09-18, running alongside the accept-encoding one.
    Mutation(
        name="http2 is quietly switched back off",
        old="    return httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=False, http2=True)",
        new="    return httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=False)",
        expect_failing="test_the_client_offers_http2",
        why="the experiment stops running while the dependency and the comments say it does",
    ),
    Mutation(
        name="the sample skips the allowlist",
        # Anchored on the success line's own wording: the call to `describe_headers` is identical
        # at both sites, and a mutation that matches twice is refused rather than guessed at.
        old='                "%s replied %s to %s, sampling rate-limit headers once: %s",\n'
        "                name,\n"
        "                reply.status_code,\n"
        "                request.url.path,\n"
        "                describe_headers(*recorded_headers(reply)),",
        new='                "%s replied %s to %s, sampling rate-limit headers once: %s",\n'
        "                name,\n"
        "                reply.status_code,\n"
        "                request.url.path,\n"
        "                dict(reply.headers),",
        expect_failing="test_the_sample_obeys_the_same_allowlist",
        why="a second place headers are written is a second place a credential could land",
    ),
]


def run_tests(selector: str) -> bool:
    """True when the selected tests pass."""
    done = subprocess.run(
        ["uv", "run", "pytest", f"{TESTS}::{selector}", "-q", "--no-header"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return done.returncode == 0


def main() -> int:
    original = PROXY.read_text()

    if not run_tests("test_a_failed_reply_logs_the_allowlisted_headers_with_their_values"):
        print("BASELINE FAILED — the tests do not pass unmutated. Nothing below means anything.")
        return 1
    print("baseline: the test set passes on unmutated code\n")

    failures = 0
    for mutation in MUTATIONS:
        print(f"── {mutation.name}")
        print(f"   why it matters: {mutation.why}")

        # FACT ONE, reported on its own: did the edit actually land?
        occurrences = original.count(mutation.old)
        if occurrences != 1:
            print(f"   mutation applied: NO — matched {occurrences} times, expected exactly 1")
            print("   RESULT: FAIL (this script is broken, not the test set)\n")
            failures += 1
            continue
        PROXY.write_text(original.replace(mutation.old, mutation.new))
        print("   mutation applied: yes")

        # FACT TWO, reported separately: did the test set notice?
        try:
            noticed = not run_tests(mutation.expect_failing)
        finally:
            PROXY.write_text(original)

        print(f"   check failed: {'yes' if noticed else 'NO'}  ({mutation.expect_failing})")
        print(f"   RESULT: {'pass' if noticed else 'FAIL — the test is vacuous'}\n")
        failures += 0 if noticed else 1

    assert PROXY.read_text() == original, "proxy.py was not restored"
    print(f"{len(MUTATIONS) - failures}/{len(MUTATIONS)} mutations were caught.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
