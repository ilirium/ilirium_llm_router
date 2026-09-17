"""Checks Phase 13's register in `../plan.md` against what actually shipped.

`../../../method/IDM-008-the-register.md` makes this a numbered task rather than a habit: the plan
carries one section listing every name and number the phase introduces, with `❓` on anything named
and never valued, and the closing task checks that section against the artefacts.

**Written against this phase's register, not adapted from Phase 12's** — the register's own row says
so. Phase 12's checked module names and config keys; this phase introduces no `src/` name at all,
so every row here resolves to a document, a scheme value, or a fact about a script.

**It reads the artefacts, never the register's prose about them.** A register row saying "eight
category tokens" is checked by counting the tokens in `backlog-index.py`, not by trusting the row.
That is the whole point: a register that checked itself would pass while both copies were wrong.

Usage, from anywhere:

    python3 docs/milestone-2-corpus/phase-13-method-and-backlog/evidence/register-check.py

Exit 0 if every row holds and the `❓` column is empty; 1 otherwise, as `backlog-index.py --check`.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PHASE = HERE.parent
DOCS = PHASE.parent.parent
ROOT = DOCS.parent


def check() -> list[str]:
    """One line per broken promise. Empty means the register is true."""
    bad: list[str] = []
    plan = (PHASE / "plan.md").read_text()

    # 1 · The `?` column must be empty. The register's own stated exit condition.
    #
    # The header row is identified by its cells, not by its suffix. The first version of this check
    # skipped any row ending `"? |"` as "the header" — which is what a row carrying a live `?` looks
    # like, so it skipped exactly the rows it exists to find. It passed on a planted `?` and was
    # caught by mutation, not by reading. Same failure class as the heading-count assertion in
    # `backlog-index.py`: a check whose exclusion swallows its own subject.
    register = plan[plan.index("## The register"):]
    for line in register.split("\n"):
        if not line.startswith("|") or "❓" not in line:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells == ["Name", "Value", "❓"]:
            continue  # the header row, and only the header row
        bad.append(f"REGISTER: a ❓ survives — {line.strip()[:90]}")

    # 2 · Every document and path the register names exists.
    for rel in (
        "docs/method/IDM-009-reviewing-executed-work.md",
        "docs/method/IDM-010-writing-for-the-owner.md",
        "docs/method/IDM-011-the-backlog.md",
        "docs/backlog-done.md",
        "docs/procedures/backlog-index.py",
    ):
        if not (ROOT / rel).exists():
            bad.append(f"MISSING: {rel}")
    for name in (
        "review-charter.md",
        "notes-review-plan.md",
        "review-charter-jobs-done.md",
        "notes-review-jobs-done.md",
        "for-the-owner.md",
    ):
        if not (PHASE / name).exists():
            bad.append(f"MISSING: {name} in the phase folder")
    if not (HERE / "register-check.py").exists():
        bad.append("MISSING: evidence/register-check.py")

    # 3 · The folder slug equals the branch slug. `IDM-001`'s one-way check, applied here because
    #     the register claims it rather than because git is consulted.
    if PHASE.name != "phase-13-method-and-backlog":
        bad.append(f"SLUG: folder is {PHASE.name!r}")

    # 4 · The `BKL` scheme, read off the two backlog files.
    live = (DOCS / "backlog.md").read_text()
    done = (DOCS / "backlog-done.md").read_text()
    ids = sorted(re.findall(r"^### (BKL-\d{4}) — ", live + "\n" + done, re.MULTILINE))
    if len(ids) != len(set(ids)):
        bad.append("BKL: an id appears twice")
    if not ids or ids[0] != "BKL-0001":
        bad.append(f"BKL: first id is {ids[0] if ids else 'none'}, register says BKL-0001")
    if not ids or ids[-1] != "BKL-0038":
        bad.append(f"BKL: highest id is {ids[-1] if ids else 'none'}, register says BKL-0038")
    if len(ids) != 38:
        bad.append(f"BKL: {len(ids)} items, register says 38")
    numbers = [int(i.split("-")[1]) for i in ids]
    if numbers != list(range(1, 39)):
        bad.append("BKL: ids are not contiguous 1..38")

    # 5 · One item shape, and the metadata line carries no id. Both are register rows and both were
    #     false for part of this phase, which is why they are checked rather than asserted.
    for label, text in (("backlog.md", live), ("backlog-done.md", done)):
        for n, line in enumerate(text.split("\n"), 1):
            if line.startswith("### ") and not re.match(r"^### BKL-\d{4} — .+$", line):
                bad.append(f"SHAPE: {label}:{n} is a `###` that is not an item heading")
        if re.search(r"^\*\*BKL-\d{4}\*\* · ", text, re.MULTILINE):
            bad.append(f"SHAPE: {label} has a metadata line still carrying its id")

    # 6 · The five statuses and the eight category tokens, counted in the script that owns them.
    script = (DOCS / "procedures" / "backlog-index.py").read_text()
    statuses = re.search(r"STATUSES = \(([^)]*)\)", script)
    found = set(re.findall(r'"([a-z-]+)"', statuses.group(1) if statuses else ""))
    if found != {"open", "partly-done", "done", "refused", "superseded"}:
        bad.append(f"STATUSES: script has {sorted(found)}")
    cats = re.search(r"CATEGORIES = \{(.*?)\n\}", script, re.DOTALL)
    tokens = set(re.findall(r':\s*"([a-z-]+)"', cats.group(1) if cats else ""))
    expected = {"method", "documentation-defects", "decisions-waiting", "measurements",
                "owner-shaped", "instruments", "dictionaries", "not-on-this-list"}
    if tokens != expected:
        bad.append(f"CATEGORIES: script has {sorted(tokens)}")

    # 7 · Only `done` leaves `backlog.md` — checked against the files, not the rule.
    for label, text, want_done in (("backlog.md", live, False), ("backlog-done.md", done, True)):
        for m in re.finditer(r"^### (BKL-\d{4}) — .+\n\n([^\n]+)$", text, re.MULTILINE):
            is_done = " · done" in m.group(2) or m.group(2).split(" · ")[1] == "done"
            if is_done != want_done:
                bad.append(f"LIFECYCLE: {m.group(1)} is in {label} with the wrong status")

    # 8 · The generated table's eight columns, in order.
    head = re.search(r"head = \"(\| ID \|[^\"]*)\"", script)
    want = "| ID | Added | Status | Category | What it is | Done | Phase | See |"
    if not head or head.group(1) != want:
        bad.append(f"COLUMNS: script renders {head.group(1) if head else 'nothing'!r}")

    # 9 · `for-the-owner.md`: four kinds, three levels, the heading shape, and 1..N with no gaps.
    owner = (PHASE / "for-the-owner.md").read_text()
    heads = re.findall(r"^## (\d+) · ([A-Z]+) · ([a-z]+) · .+$", owner, re.MULTILINE)
    if len(heads) != len(re.findall(r"^## ", owner, re.MULTILINE)):
        bad.append("FOR-THE-OWNER: an entry heading does not match `## n · KIND · level · title`")
    nums = [int(h[0]) for h in heads]
    if nums != list(range(1, len(nums) + 1)):
        bad.append(f"FOR-THE-OWNER: entry numbers are {nums}, expected 1..N with no gaps")
    if not {h[1] for h in heads} <= {"ASK", "IDEA", "REGRET", "ERRAND"}:
        bad.append(f"FOR-THE-OWNER: unknown kind in {sorted({h[1] for h in heads})}")
    if not {h[2] for h in heads} <= {"high", "medium", "low"}:
        bad.append(f"FOR-THE-OWNER: unknown level in {sorted({h[2] for h in heads})}")

    # 10 · `backlog-index.py`'s flags and its two exit codes.
    for flag in ("--print", "--write", "--check"):
        if flag not in script:
            bad.append(f"FLAGS: {flag} not in backlog-index.py")

    return bad


def main() -> int:
    problems = check()
    for p in problems:
        print(p)
    if problems:
        print(f"\n{len(problems)} register rows do not hold.")
        return 1
    print("Phase 13's register holds: every row checked against what shipped, ❓ column empty.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
