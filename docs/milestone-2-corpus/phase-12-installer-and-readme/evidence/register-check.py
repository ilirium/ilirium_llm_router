#!/usr/bin/env python3
"""Check Phase 12's register against the code and the documents it describes.

`method/IDM-008-the-register.md` makes this the phase's closing task: every name and number the plan
introduces is checked against what was actually built, and the `❓` column is expected to be empty.

**Run it from anywhere; it locates the repository root from its own path.** It reads only, prints one
line per check, and exits 1 if any fails -- so it can be re-run on the trunk after the merge, which
is the point of freezing it rather than doing the check by hand once.

    python3 docs/milestone-2-corpus/phase-12-installer-and-readme/evidence/register-check.py

**One check earned its own note.** The "no unvalued rows" test looks at *table rows only*. A plain
grep for the marker matches the two sentences that *state the rule* -- the register's own preamble
and the plan's exit criterion -- and reports the phase as incomplete because it documented what
complete means. That is the same false positive `IDM-001`'s placeholder sweep hits, and it was hit
here on the first run.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PLAN = ROOT / "docs/milestone-2-corpus/phase-12-installer-and-readme/plan.md"
CLI = ROOT / "src/ilirium_llm_router/cli.py"
README = ROOT / "README.md"

UNVALUED = "❓"  # the register's ❓, kept out of the source so a grep for it finds rows not code


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def caveat_count() -> int:
    """Paragraphs in the README's caveats section. Settled row 6 fixes this at four."""
    section = read(README).split("## Bugs and caveats")[1].split("## Roadmap")[0]
    return len([p for p in section.strip().split("\n\n") if p.strip()])


def unvalued_rows() -> int:
    return sum(1 for line in read(PLAN).splitlines() if line.startswith("|") and UNVALUED in line)


def checks() -> list[tuple[str, bool]]:
    cli, readme = read(CLI), read(README)
    return [
        # names the phase added to src/
        ("init is a subcommand", "init = commands.add_parser" in cli),
        ("--version exists, with no short form", '"--version",' in cli and '"-v",' not in cli),
        ("init has no --force", "--force" not in cli.replace("`--force`", "")),
        ("_init(path: Path) -> int", "def _init(path: Path) -> int:" in cli),
        ("CONFIG_TEMPLATE", 'CONFIG_TEMPLATE = "config-template.yaml"' in cli),
        ("ENV_TEMPLATE", 'ENV_TEMPLATE = "env-template"' in cli),
        ("ENV_EXAMPLE", 'ENV_EXAMPLE = ".env.example"' in cli),
        ("DEFAULT_CONFIG_PATH unchanged", 'DEFAULT_CONFIG_PATH = Path("config.yaml")' in cli),
        (".env is read beside the config", 'load_dotenv(args.config.parent / ".env")' in cli),
        ("init refuses rather than overwriting", "refusing to overwrite it" in cli),
        # names that go on disk
        ("config template ships", (ROOT / "src/ilirium_llm_router/config-template.yaml").is_file()),
        ("env template ships", (ROOT / "src/ilirium_llm_router/env-template").is_file()),
        (
            "config template is config.yaml byte for byte",
            read(ROOT / "src/ilirium_llm_router/config-template.yaml") == read(ROOT / "config.yaml"),
        ),
        (
            "env template is .env.example byte for byte",
            read(ROOT / "src/ilirium_llm_router/env-template") == read(ROOT / ".env.example"),
        ),
        ("no uv build-backend section", "tool.uv.build-backend" not in read(ROOT / "pyproject.toml")),
        ("no MANIFEST.in", not (ROOT / "MANIFEST.in").exists()),
        ("tests/test_cli_init.py", (ROOT / "tests/test_cli_init.py").is_file()),
        # the documents
        ("the brief is in captures/", (ROOT / "docs/captures/original-project-description.md").is_file()),
        (
            "the brief is indexed there",
            "original-project-description.md" in read(ROOT / "docs/captures/README.md"),
        ),
        ("README has ten sections", readme.count("\n## ") + readme.startswith("## ") == 10),
        ("README caveats are four", caveat_count() == 4),
        ("README says seven Milestone 1 phases", "seven phases" in readme),
        ("README says four Milestone 2 phases", "four phases in" in readme),
        ("README test count is 448", "448 tests" in readme),
        ("README no longer says 158", "158 tests" not in readme),
        ("README quotes the shipped --help", "sweep maxdict x k and print the whole surface" in readme),
        ("install line carries no --force", "uv tool install --force" not in readme),
        # the register itself
        ("no unvalued register rows", unvalued_rows() == 0),
    ]


def main() -> int:
    results = checks()
    for name, ok in results:
        print(f"{'PASS' if ok else 'FAIL'}  {name}")
    failed = sum(1 for _, ok in results if not ok)
    print(f"\n{len(results)} checks: {len(results) - failed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
