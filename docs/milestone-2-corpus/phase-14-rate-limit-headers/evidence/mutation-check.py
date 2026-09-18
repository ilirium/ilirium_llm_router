#!/usr/bin/env python3
"""Does Group B's test set actually test anything? Break the code and see whether it notices.

`CLAUDE.md`: *exercise it before committing; green tests are not evidence.* Phase 13 shipped three
checks that passed while testing nothing, and none was found by reading.

**The one thing this script is built around**: Phase 13's own mutation harness silently never
applied its mutations, which looks identical to a clean pass. So each mutation reports TWO facts
separately -- whether the edit landed in the file, and whether the tests then failed. A mutation
that cannot be applied is a FAILURE of this script, never a pass of the test set.

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
        old='    return " ".join(parts) if parts else "(none)"',
        new='    return " ".join(parts)',
        expect_failing="test_a_rejection_carrying_no_rate_limit_headers_says_so",
        why="'no buckets named' is the finding, and a blank tail reads as a logging failure",
    ),
    Mutation(
        name="the log fires on success too",
        old="        if reply.status_code >= 400:",
        new="        if reply.status_code >= 0:",
        expect_failing="test_a_successful_reply_logs_nothing",
        why="every call would log its buckets and drown the file",
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
