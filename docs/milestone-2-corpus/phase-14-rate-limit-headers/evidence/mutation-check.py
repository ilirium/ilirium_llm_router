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
ANTHROPIC = ROOT / "src" / "ilirium_llm_router" / "backend_anthropic.py"
TESTS = "tests/test_proxy.py"


@dataclass
class Mutation:
    """One deliberate defect, and the test that has to die when it is introduced."""

    name: str
    old: str
    new: str
    expect_failing: str
    why: str
    # Which file to break. **Added 2026-09-20 with Group C4**, which put the block's construction in
    # `backend_anthropic.py`: a harness hardcoded to one file reports a clean run over code it never
    # touched, and that is this script's own documented failure mode rather than a new one.
    file: Path = PROXY


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
        old="    if wants_stream or not relay_accept_encoding:\n        headers.append((b\"accept-encoding\", b\"identity\"))",
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
    # The switches, 2026-09-19. Each of these is "the flag is ignored and the experiment runs
    # anyway", which is the failure a switch actually has: a config key that reads as off while the
    # behaviour is on is worse than no key at all.
    Mutation(
        name="relay_accept_encoding is ignored and the experiment always runs",
        old="    if relay_accept_encoding and not wants_stream:",
        new="    if not wants_stream:",
        expect_failing="test_a_non_streamed_request_forces_identity_by_default",
        why="the config says the experiment is off and non-streamed replies still arrive compressed",
    ),
    Mutation(
        name="the identity append stops covering the non-streamed default",
        old="    if wants_stream or not relay_accept_encoding:",
        new="    if wants_stream:",
        expect_failing="test_a_non_streamed_request_forces_identity_by_default",
        why="dropping the header is not the same as forcing identity -- httpx substitutes its own, "
        "so the request asks for compression while the config says it does not",
    ),
    Mutation(
        name="http2_upstream is ignored and h2 is always offered",
        old="    return httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=False, http2=http2)",
        new="    return httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=False, http2=True)",
        expect_failing="test_the_client_speaks_http_1_1_by_default",
        why="an eliminated variable rides along in every later measurement, unasked for",
    ),
    Mutation(
        name="imitate_attribution_headers is ignored and attribution is always fabricated",
        old='                if name == "anthropic" and self.config.experiments.imitate_attribution_headers',
        new='                if name == "anthropic"',
        expect_failing="test_no_attribution_is_fabricated_by_default",
        why="the router invents billing attribution on every Anthropic call while the config says "
        "it does not -- and a first-party client is already sending its own, which disagrees",
    ),
    # The imitation experiment, 2026-09-18.
    Mutation(
        name="the imitation is sent to LM Studio too",
        old='                if name == "anthropic" and self.config.experiments.imitate_attribution_headers',
        new="                if self.config.experiments.imitate_attribution_headers",
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
        name="the billing value regains its trailing space",
        old='        ) + ";"',
        new='        ) + "; "',
        expect_failing="test_every_imitated_header_is_legal_http",
        why="an illegal header value -- the 502 the caller actually saw",
    ),
    Mutation(
        name="cc_prompt_id becomes a constant",
        old="                f\"cc_prompt_id={uuid.uuid4()}\",",
        new='                "cc_prompt_id=00000000-0000-0000-0000-000000000000",',
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
        old="        if self.arrival_sampled.take(shape):",
        new="        if self.headers_sampled.take():",
        expect_failing="test_the_arriving_request_is_sampled_once_per_shape",
        why="only the shape that arrives first is ever sampled, and the pair IS the measurement",
    ),
    # The shape key gains the path and the size band, 2026-09-19 -- `for-the-owner.md` entry 11.
    # Every mutation below reintroduces a form of the defect the change was made to fix, and the
    # 14:52 run is what each one would have produced.
    Mutation(
        name="the size band drops out of the shape key",
        old="        shape = (request.url.path, bool(call.stream), size_band(len(body)))",
        new="        shape = (request.url.path, bool(call.stream), 0)",
        expect_failing="test_both_sizes_of_one_shape_are_sampled",
        why="exactly the 14:52 defect: the 323-byte warm-up takes the slot, the 127,949-byte "
        "classifier is never sampled, and the run cannot answer its own question",
    ),
    Mutation(
        name="the path drops out of the shape key",
        old="        shape = (request.url.path, bool(call.stream), size_band(len(body)))",
        new="        shape = (\"\", bool(call.stream), size_band(len(body)))",
        expect_failing="test_the_path_is_part_of_the_shape_key",
        why="the probe and a real call collapse into one shape, which is entry 6's defect again. "
        "**This mutation survived once**: it was aimed at the probe test, whose two requests differ "
        "in size as well as path and stay apart on the band alone. The test was vacuous for the "
        "path and a test that varies nothing else was written",
    ),
    Mutation(
        name="every size lands in the same band",
        old="    return len(str(length)) - 1",
        new="    return 0",
        expect_failing="test_size_band_is_the_decimal_order_of_magnitude",
        why="the ladder is inert while the key still looks as though it carries a size",
    ),
    Mutation(
        name="the band is off by one at a power of ten",
        old="    return len(str(length)) - 1",
        new="    return len(str(length))",
        expect_failing="test_size_band_is_the_decimal_order_of_magnitude",
        why="a band ladder nobody can predict is a band ladder nobody can read a log against",
    ),
    Mutation(
        name="the arrival latch fires on every request",
        old="        if key in self.seen or self.full:\n            return False\n        self.seen.add(key)",
        new="        if self.full:\n            return False",
        expect_failing="test_a_second_request_in_the_same_band_is_not_sampled",
        why="a busy session logs every request it carries and drowns the file",
    ),
    Mutation(
        name="the cap stops bounding the sampler",
        old="        if key in self.seen or self.full:",
        new="        if key in self.seen:",
        expect_failing="test_sampling_stops_at_the_cap_and_says_so",
        why="the path is caller-chosen and `app.py` has a catch-all, so the set grows without limit",
    ),
    Mutation(
        name="reaching the cap becomes a silent stop",
        old="        return self.full and self.announced.take()",
        new="        return False",
        expect_failing="test_sampling_stops_at_the_cap_and_says_so",
        why="***the phase's own recurring defect***: an instrument quietly stops looking and every "
        "line still present reads as though it were still watching",
    ),
    Mutation(
        name="the cap announcement repeats forever",
        old="        return self.full and self.announced.take()",
        new="        return self.full",
        expect_failing="test_sampling_stops_at_the_cap_and_says_so",
        why="one line per request once the cap is reached, which is the flood the cap prevents",
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
        old="    return httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=False, http2=http2)",
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
    # The gzip peek, 2026-09-19. A first-party client compresses some request bodies and the
    # router refused them for "carrying no 'model' field" -- the field was there, compressed.
    Mutation(
        name="the peek stops decoding and reads the compressed bytes again",
        old="            for_routing = decoded_for_peek(body, request.headers.get(\"content-encoding\"))",
        new="            for_routing = body",
        expect_failing="test_a_gzipped_body_is_routed_by_the_model_inside_it",
        why="the original defect, restored: a valid request refused for a field it does carry",
    ),
    Mutation(
        name="the DECODED copy is relayed instead of what arrived",
        old="        return call, body, peeked, unreadable",
        new="        return call, for_routing, peeked, unreadable",
        expect_failing="test_a_gzipped_body_is_relayed_still_compressed",
        why="***byte-relay broken***: the upstream gets bytes the caller never sent, the "
        "prompt-cache prefix stops matching, and every call starts costing full price",
    ),
    Mutation(
        name="the inflation cap is removed",
        old="            out = machine.decompress(body, PEEK_MAX_DECOMPRESSED)",
        new="            out = machine.decompress(body)",
        expect_failing="test_a_body_that_inflates_past_the_cap_is_refused",
        why="a few KB of zeros becomes gigabytes of memory, and the catch-all route means the "
        "caller is not necessarily Claude Code",
    ),
    Mutation(
        name="an unreadable encoding goes back to blaming a missing model field",
        old="            detail = unreadable or (",
        new="            detail = None or (",
        expect_failing="test_an_encoding_the_router_cannot_read_says_so",
        why="the message that sent a session hunting for a field that was there",
    ),
    Mutation(
        name="an unknown encoding is guessed at rather than refused",
        old="    if encoding not in PEEKABLE_ENCODINGS:",
        new="    if False:",
        expect_failing="test_an_encoding_the_router_cannot_read_says_so",
        why="`br` would be fed to zlib, and the failure would read as a corrupt body",
    ),
    # What the CLIENT receives from a compressed reply, 2026-09-19.
    Mutation(
        name="content-encoding is dropped from the reply",
        old='DROPPED_FROM_RESPONSE = CONNECTION_HEADERS | {"content-length", "date", "server"}',
        new='DROPPED_FROM_RESPONSE = CONNECTION_HEADERS | {"content-length", "date", "server", "content-encoding"}',
        expect_failing="test_a_compressed_reply_keeps_its_content_encoding",
        why="the caller is handed compressed bytes with nothing saying so -- the failure mode this "
        "phase wrongly suspected, and it must stay impossible rather than merely absent",
    ),
    Mutation(
        name="content-length is relayed after all",
        old='DROPPED_FROM_RESPONSE = CONNECTION_HEADERS | {"content-length", "date", "server"}',
        new='DROPPED_FROM_RESPONSE = CONNECTION_HEADERS | {"date", "server"}',
        expect_failing="test_a_relayed_reply_carries_no_content_length",
        why="separating chunked from compressed is `prompt.md` open item 2 and must be a deliberate "
        "change to that test, never a silent one",
    ),
    # --- Group C4: the attribution block, added 2026-09-20 -------------------------------------
    #
    # Nine tests went in with it and every one of them asserts an ABSENCE for some input -- byte
    # equality, or a field that must not appear. **An absence is the easiest thing in this
    # repository to assert vacuously**, which is why each mutation below makes the router do the
    # thing the test says it must not.
    Mutation(
        name="the block is appended last instead of first",
        old='    payload["system"] = [{"type": "text", "text": attribution_block()}, *system]',
        new='    payload["system"] = [*system, {"type": "text", "text": attribution_block()}]',
        expect_failing="test_the_attribution_block_is_added_as_the_first_system_element",
        why="first is where the client puts it, and a block appended last is a different request",
        file=ANTHROPIC,
    ),
    Mutation(
        name="a cch is invented",
        old='    return f"{ATTRIBUTION_PREFIX}cc_version={CC_VERSION}; cc_entrypoint={CC_ENTRYPOINT};"',
        new='    return f"{ATTRIBUTION_PREFIX}cc_version={CC_VERSION}; cc_entrypoint={CC_ENTRYPOINT}; cch=f65f6;"',
        expect_failing="test_the_injected_block_carries_no_cch_and_no_chaining_fields",
        why="a hardcoded cch repeats on every request, which no real client does",
        file=ANTHROPIC,
    ),
    Mutation(
        name="an existing block is no longer noticed",
        old="    return any(",
        new="    return False and any(",
        expect_failing="test_a_body_that_already_carries_a_block_is_left_alone",
        why="a first-party request would be sent carrying two contradictory blocks",
        file=ANTHROPIC,
    ),
    Mutation(
        name="the prefix match becomes an equality match",
        old='        and element["text"].startswith(ATTRIBUTION_PREFIX)',
        new='        and element["text"] == ATTRIBUTION_PREFIX',
        expect_failing="test_a_body_that_already_carries_a_block_is_left_alone",
        why="a real block carries cch, so equality finds nothing and injects a second one",
        file=ANTHROPIC,
    ),
    Mutation(
        name="a string `system` is rewritten into an array anyway",
        old='        return None, "the body\'s \'system\' is not an array, so there is nowhere to put a block"',
        new='        system = []',
        expect_failing="test_a_string_system_is_left_alone_rather_than_converted",
        why="turning a string into an array is a larger change to a body than this may make",
        file=ANTHROPIC,
    ),
    Mutation(
        name="streamed requests are rewritten too",
        old="            and call.stream is False",
        new="            and call.stream is not None",
        expect_failing="test_a_streamed_request_is_never_rewritten",
        why="every main-conversation turn would miss the prompt cache, for no benefit",
    ),
    Mutation(
        name="the local backend gets one as well",
        old='            and name == "anthropic"',
        new="            and True",
        expect_failing="test_the_local_backend_never_receives_an_attribution_block",
        why="LM Studio would be handed client details it has no use for",
    ),
    Mutation(
        name="a compressed body is rewritten",
        old='            if encoding != "identity":',
        new="            if False:",
        expect_failing="test_a_compressed_body_is_declined_for_being_compressed_not_unreadable",
        why="a compressed body would be reported as unreadable, which is the 2026-09-19 misdiagnosis",
    ),
    Mutation(
        name="the switch is on by default",
        old="            self.config.experiments.add_claude_code_hidden_attribution_block",
        new="            True",
        expect_failing="test_a_non_streamed_request_keeps_its_body_byte_for_byte_by_default",
        why="byte-relay is what the router IS; the exception has to be asked for",
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
    originals = {path: path.read_text() for path in (PROXY, ANTHROPIC)}

    if not run_tests("test_a_failed_reply_logs_the_allowlisted_headers_with_their_values"):
        print("BASELINE FAILED — the tests do not pass unmutated. Nothing below means anything.")
        return 1
    print("baseline: the test set passes on unmutated code\n")

    failures = 0
    for mutation in MUTATIONS:
        print(f"── {mutation.name}")
        print(f"   why it matters: {mutation.why}")

        # FACT ONE, reported on its own: did the edit actually land?
        original = originals[mutation.file]
        occurrences = original.count(mutation.old)
        if occurrences != 1:
            print(f"   mutation applied: NO — matched {occurrences} times, expected exactly 1")
            print("   RESULT: FAIL (this script is broken, not the test set)\n")
            failures += 1
            continue
        mutation.file.write_text(original.replace(mutation.old, mutation.new))
        print(f"   mutation applied: yes  ({mutation.file.name})")

        # FACT TWO, reported separately: did the test set notice?
        try:
            noticed = not run_tests(mutation.expect_failing)
        finally:
            mutation.file.write_text(original)

        print(f"   check failed: {'yes' if noticed else 'NO'}  ({mutation.expect_failing})")
        print(f"   RESULT: {'pass' if noticed else 'FAIL — the test is vacuous'}\n")
        failures += 0 if noticed else 1

    for path, text in originals.items():
        assert path.read_text() == text, f"{path.name} was not restored"
    print(f"{len(MUTATIONS) - failures}/{len(MUTATIONS)} mutations were caught.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
