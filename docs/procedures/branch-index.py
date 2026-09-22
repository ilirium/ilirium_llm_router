"""Derives the branch table in `../reference/branches.md` from git, so five of its six columns cannot drift.

`../method/IDM-001-git-branching.md` refused a list of merged branches for one reason, and the reason
was right: *"git already holds that, and a hand-maintained list would drift."* This repository has
that failure four times over — four of Milestone 1's six phase notes carried a `Merge commit` row
still reading "merge back with `--no-ff`" long after the merge happened.

So the answer is not to hand-maintain it more carefully. **The branch, the fork point, the opened
date, the merge commit and the merge date are read out of git every time this runs.** The only column
written by a person is the last one — what the branch was *for*, which git does not hold and cannot.

Usage, from anywhere:

    python3 docs/procedures/branch-index.py            # print the table
    python3 docs/procedures/branch-index.py --write    # splice it into reference/branches.md
    python3 docs/procedures/branch-index.py --check    # exit 1 if the file is stale

**`--check` is the point of the whole script.** Run it after any merge; it fails when a branch has
landed and the table has not been regenerated, which is precisely the drift `IDM-001` predicted.

## What it will not let you get away with

A branch with no entry in `DESCRIPTIONS` below is reported and the run exits 1. That is deliberate:
the generated columns appear by themselves, so without this the description column would fill up with
blanks and the file would silently become a worse `git branch -a`. **Adding the description is the
work; the rest is bookkeeping this script does.**

An entry naming a branch that no longer exists is reported the same way.

## In-flight branches are not in the table

`IDM-001` gives in-flight branches to `../status.md` — name, purpose, tree state, next action — and
that is a different job from this one: a row here records what a branch *did*, which is not knowable
until it is done. Unmerged branches are printed as a note under the table instead, so a run tells you
they exist without this file competing with `status.md` for the live state.

## Fast-forwarded branches, and why their opened dates carry a `~`

**A fast-forward leaves no trace of where the branch began.** Its commits are on `main`'s first-parent
line and are indistinguishable from commits made on `main` directly; there is no merge commit, so
there is no second parent to take a merge base against. Three branches here predate the `--no-ff`
convention and are in that state: `docs/add-claude-md`, `feat/phase-0-skeleton`, `feat/phase-1-proxy`.

What *is* recoverable is a **window**: the run of commits between the previous boundary — the nearest
older merge commit or fast-forwarded branch tip — and this branch's tip. The branch began somewhere in
that window. This script reports the earliest date in it, marked `~`, which is therefore an **earliest
possible** date and not necessarily the true one.

Worth knowing before comparing a `~` date against a phase note: for `feat/phase-0-skeleton` the window
spans two days, so its `~2026-07-27` is a day earlier than the commit that actually says
*"added: Phase 0 project skeleton"*. The other two windows fall on a single date and the `~` costs
nothing. **Do not silently correct these to the phase note's date** — the marker is the honest answer,
and hand-editing it puts a column back under human maintenance for the sake of one day.

## What it does not answer

**The fork point is a merge base, which is not always where the branch began.** A branch that pulls
`main` in mid-flight moves its own merge base forward, so the column then shows the *last* point the
two sides shared rather than the first. `docs/idm-and-claude-md` is the worked example: it forked
from `feat/phase-10-body-store` in order to see `IDM-004`, merged `main` at `c1f9d97`, and this table
prints `2a4e186`. Both are true and they answer different questions. Where it matters, the
description column says it in words — which is one of the things that column is for.

It also does not check whether a phase folder's slug matches its branch; `IDM-001` states that rule
and nothing enforces it.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# The one hand-written column, plus the milestone and phase a branch belongs to.
#
# Milestone and phase are here rather than derived because `phase-N-` in a branch name is a
# convention that arrived at Phase 8 — Phase 7 is `docs/milestone-boundary-restructure` and carries
# no number, which is IDM-001's standing exception. Parsing the name would get that row wrong.
#
# `milestone` and `phase` are None when the branch belongs to neither.
# Branches that are NOT work in flight, declared by hand because git cannot tell.
#
# ***This is the fix for a defect that deleted a row every time `--write` ran.*** `resolve()` sorts a
# branch by its topology, and two different things have the SAME topology: a branch
# fast-forwarded to the trunk's tip, and a branch cut from the trunk's head with nothing committed
# to it yet. **They are indistinguishable by construction**, so no topological test can separate
# them — which means the one piece of information that separates them has to be written down.
#
# Without this, `temp/to-run-server` was classified in-flight, excluded from the table, and its row
# silently removed — **the only record that the branch is a worktree pin and not somebody's unfinished
# work.** `--check` said `STALE` and did not say which row was at risk. *Found 2026-09-18 by reading;
# it then fired again on 2026-09-22, on a clean `main`, during routine work.*
#
# Two kinds, because they are not the same thing:
#
#   "pin"     — a worktree parked on the trunk. Not work, never will be, and its tip moves with the
#               trunk. `temp/to-run-server`.
#   "archive" — a branch with its own commits that is deliberately NEVER merging, kept for what it
#               records, and carrying the `unmerged/` prefix `IDM-001` defines.
#               `unmerged/phase-14-rate-limit-headers` is the first.
#
# **Both are TABLED rather than excluded**, because the table is where a reader looks to find out
# what a branch is, and "absent" is the one answer that teaches them nothing.
NOT_IN_FLIGHT: dict[str, str] = {
    "temp/to-run-server": "pin",
    "unmerged/phase-14-rate-limit-headers": "archive",
}

DESCRIPTIONS: dict[str, tuple[int | None, int | None, str]] = {
    "docs/add-claude-md": (
        None,
        None,
        "The repository's first documentation — the README, `CLAUDE.md`, the design decisions and "
        "observability spec, and the phased implementation plan. **Predates Phase 0 and the "
        "milestone scheme**, so it belongs to neither.",
    ),
    "feat/phase-0-skeleton": (
        1,
        0,
        "The uv project, config loading and the CLI. No notes file — its record is a section of "
        "`milestone-1-core/implementation-plan.md`.",
    ),
    "feat/phase-1-proxy": (
        1,
        1,
        "Dispatch working end to end: the `HEAD /` probe, `POST /v1/messages` by model name, a "
        "catch-all, byte relay and streaming. Verified in a real session on 2026-07-29.",
    ),
    "feat/phase-2-observability": (
        1,
        2,
        "The rotating log and the twenty-column CSV. Its step 6 session — long, both backends, "
        "subagents, an interrupted response — is the evidence half the project still rests on.",
    ),
    "docs/epd-index-and-corpus-proposal": (
        1,
        None,
        "`EPD-000` as the index and `EPD-003` on body capture: the proposal Milestone 2 was later "
        "built from. Documentation work belonging to the milestone without being a phase.",
    ),
    "feat/phase-3-failure-handling": (
        1,
        3,
        "The failure taxonomy — and the finding that **four of its five planned items were already "
        "built** by Phase 2. Measured what Claude Code does with an error: retries a 502 ten times, "
        "ignores a mid-stream `error` event.",
    ),
    "feat/phase-4-lmstudio-parity": (
        1,
        4,
        "What LM Studio supports, measured instead of guessed. **Nothing was rejected**; the gaps "
        "are things accepted and not honoured. Found the router's read timeout reachable by "
        "ordinary traffic.",
    ),
    "feat/phase-5-config-and-timeouts": (
        1,
        5,
        "The three credential modes, built and carried live against an authenticated LM Studio, and "
        "`read_timeout` made per backend — which unblocked ruling out silent trimming below the "
        "context boundary.",
    ),
    "feat/phase-6-review-and-cleanup": (
        1,
        6,
        "The review. Fifteen of sixteen quoted measurements reproduced to the digit; seven items "
        "fixed in about forty lines; two proposed cuts refused with the measurement that refused "
        "them.",
    ),
    "docs/milestone-boundary-restructure": (
        1,
        7,
        "The documentation restructure — the archive, the reference tier, the manual, and "
        "`CLAUDE.md` cut from 337 lines to 188. **The one phase whose folder and branch slugs "
        "disagree**, which is IDM-001's standing exception.",
    ),
    "docs/phase-8-method-and-guardrails": (
        2,
        8,
        "Opened Milestone 2 and built the `method/` tier: `IDM-000`–`IDM-003`, the branching rules "
        "unified from two homes that disagreed in seven places, and the tracked permission "
        "allowlist. **The first branch to carry a phase number on a non-`feat/` prefix.**",
    ),
    "chore/tracked-allowlist-make-sync-and-clean": (
        2,
        None,
        "Allowed all eight `make` targets in the tracked settings file rather than six. One commit; "
        "the smallest branch in the repository.",
    ),
    "docs/phase-9-corpus-gate": (
        2,
        9,
        "The corpus gate: 73 bodies captured over three runs, a held-out dictionary reaching "
        "12.10×, and **`EPD-003` decided** — bodies are archived, fine-tuning dropped. Named "
        "Milestone 2's central claim.",
    ),
    "docs/idm-001-status-placeholders": (
        2,
        None,
        "Generalised `IDM-001`'s closeout rule from the `Merge commit` row to **any** statement of "
        "unfinished state, after the narrow wording was obeyed as an instance and missed twice in "
        "one phase.",
    ),
    "docs/status-shape-one-row-per-milestone": (
        2,
        None,
        "Replaced `status.md`'s per-phase table with one row per milestone. The per-phase merge "
        "hashes were not lost — each keeps two to six homes in the archive.",
    ),
    "docs/prompt-refresh-after-idm-001": (
        2,
        None,
        "Refreshed `prompt.md` for `IDM-001`'s new rule, and for a gap it had carried from the "
        "start.",
    ),
    "feat/phase-10-body-store": (
        2,
        10,
        "The body store built: content-addressed blobs, the byte-bounded queue and its worker "
        "thread, dictionary training and retraining, and `reference/corpus.md`. Thirty-three tasks, "
        "`make test` 310. The largest branch in the repository at 63 commits.",
    ),
    "feat/phase-11-corpus-tools": (
        2,
        11,
        "The tools that read the archive back: `extract` and `verify-archive`, the CLI on "
        "subcommands, and a session rebuilt into a transcript a history viewer opens. `make test` "
        "438. **Tasks 14 and 15 are struck in place** — the owner exercises the tools by hand after "
        "the merge. Found that a `session_id` holds several conversations, that a request's tail is "
        "provisional, and — by systematic mutation — five logic defects that 23 targeted mutations "
        "could not.",
    ),
    "feat/phase-12-installer-and-readme": (
        2,
        12,
        "The installer and the `README.md` rewrite: an `init` subcommand writing `config.yaml` and "
        "`.env.example`, a `--version` flag, a fix to the `.env` search, two templates shipped as "
        "package data, and ten sections replacing 133 lines. `make test` 448. **Three of its five "
        "`src/` changes came from the forward review**, the largest being that `load_dotenv()` "
        "never read the working directory. **Reviewed a second time against the finished work "
        "before the merge** — the first such review here, at 11% overlap between its two runs "
        "against `IDM-004`'s forward 18%, and it found a fourth stale copy of the phase count in "
        "`CLAUDE.md`.",
    ),
    "docs/phase-13-method-and-backlog": (
        2,
        13,
        "Three method documents and the backlog refactor, carrying no `src/` change. `IDM-009` "
        "reviewing executed work, `IDM-010` the per-phase `for-the-owner.md`, `IDM-011` the "
        "backlog — and every item in `backlog.md` given a permanent `BKL-NNNN` id, with done items "
        "moved to a new `backlog-done.md` and a generated table in each from a new "
        "`backlog-index.py`. **A cold review of the item inventory found two items the compile "
        "pass had missed**, so 36 became 38 before any id was applied; the two open `~~**`, where "
        "the pass matched bold-or-`###` at the line start. **The owner then rejected the item "
        "shape**, and a late group made every item a `### BKL-NNNN — title` heading, retiring the "
        "two shapes that had hidden them. **Phase 13 is `IDM-009`'s first subject and the protocol "
        "stopped its own author's merge**: two runs, 23 findings, five method-tier, **none of them "
        "caught by any instrument the phase built** while every check was green. Three of the 23 "
        "are checks that passed while testing nothing.",
    ),
    "docs/idm-and-claude-md": (
        2,
        None,
        "The two milestone playbooks moved out to `IDM-005` and `IDM-006`, the closing one "
        "**repaired as it moved** — five of its seven decided steps were missing. Forked from "
        "`feat/phase-10-body-store` rather than `main`, and having nowhere to record that is what "
        "added `IDM-001`'s third row.",
    ),
    "docs/branch-index": (
        2,
        None,
        "Two things. **The branch index** — this table, the script that generates it, and the "
        "`IDM-001` amendment that admits a derived index where a hand-maintained list was refused; "
        "enumerating refs found `docs/add-claude-md`, unrecorded for twenty-five days. **And four "
        "method items**: `IDM-007` on raising a concern where it will be read, `IDM-008` on the "
        "register, the read-by-section rule, and the forward-only `notes.md` split.",
    ),
    "docs/bugs-tier": (
        2,
        None,
        "The `bugs/` tier — defects in software this project does not own, where no commit of ours "
        "is the ending. **Its boundary against `wiki/` is lifetime**: a wiki page is written to "
        "stay true, a bug document hoping to stop being true. `BUG-000` carries the founding rule "
        "that **an absence is not a fix**, so every entry names the positive check that would "
        "close it. `BUG-001` is Anthropic rejecting non-streamed `/v1/messages` with 429 while a "
        "streamed request **2.8× larger** to the same model succeeds 0.6 s later.",
    ),
    "fix-slop-docs/opening-playbook-not-run-table": (
        2,
        None,
        "**The first `fix-slop-docs/` branch, and the prefix arrives with it** — a defect class "
        "named by cause rather than by artefact: documentation that is wrong because a model wrote "
        "it. Two sentences that had outlived the tables they introduce, both corrected in place: "
        "`milestone-2-corpus/implementation-plan.md` counted opening-playbook step 1 as unrun 230 "
        "lines below the claim that discharged it, and `IDM-005` warned that the same table was "
        "stale twelve days after it had been repointed. Also `IDM-001` reading *five* beside a "
        "list of six, four documents describing a worktree that had been deleted, and the finding "
        "that "
        "`link-check.py`'s headline count is a property of the **worktree** rather than of the "
        "repository — 83 on `main`, 101 in a clean checkout, the whole delta one untracked path.",
    ),
    "feat/phase-14-rate-limit-headers": (
        2,
        14,
        "What Phase 14 shipped: the rate-limit response header recorder it was opened to build, the "
        "gzip `400` fix — a live defect in `peek`, not experiment scaffolding — and the fix that "
        "actually resolved `BUG-001`, which was removing `CLAUDE_CODE_ATTRIBUTION_HEADER=0` from "
        "five of this repository's own documents. **The investigation it came out of is on "
        "`unmerged/phase-14-rate-limit-headers` and did not merge.** See "
        "`milestone-2-corpus/phase-14-rate-limit-headers/README.md`.",
    ),
    "unmerged/phase-14-rate-limit-headers": (
        2,
        14,
        "The investigation behind `BUG-001`, kept and **deliberately never merged**. Three days on a "
        "`429` that turned out to be ours: `CLAUDE_CODE_ATTRIBUTION_HEADER=0`, in this repository's "
        "own README since 2026-08-07, suppressing the attribution block Anthropic gates on. "
        "Thirteen eliminated hypotheses, a TLS-fingerprint comparison, a hosts route with its own "
        "terminator and a working attribution injection are kept here and nowhere else; what "
        "shipped went to `main` on `feat/phase-14-rate-limit-headers`. See "
        "`milestone-2-corpus/phase-14-rate-limit-headers/README.md` and `bugs/BUG-001-…`.",
    ),
    "temp/to-run-server": (
        None,
        None,
        "**Not a piece of work, and the only row here that is not.** A worktree pinned to `main` "
        "so the router can be run and driven while another branch holds the editable tree. It "
        "carries no commits of its own — which is *why* it appears in this table at all: its tip "
        "sits on the trunk, so it resolves as merged rather than in flight. The telemetry and "
        "corpus that `BUG-001` and Phase 11 both rest on were captured through it.",
    ),
}

TRUNK = "main"
BEGIN = "<!-- generated by procedures/branch-index.py — do not edit between these markers -->"
END = "<!-- end generated -->"


def git(*args: str) -> str:
    """Runs a git command in this repository and returns its stripped stdout."""
    root = Path(__file__).resolve().parent.parent.parent
    return subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def lines(*args: str) -> list[str]:
    out = git(*args)
    return out.splitlines() if out else []


def branch_tips() -> dict[str, str]:
    """Every branch name → tip hash, local and remote-only alike, trunk excluded.

    A branch pushed and then deleted locally still counts — `docs/add-claude-md` exists only under
    `refs/remotes/origin` and is one of the three the repository had never written down.
    """
    tips: dict[str, str] = {}
    for ref in ("refs/heads", "refs/remotes/origin"):
        for line in lines("for-each-ref", "--format=%(refname:short) %(objectname)", ref):
            name, sha = line.split(" ", 1)
            # `refs/remotes/origin/HEAD` shortens to a bare `origin`, which is not a branch.
            if name == "origin":
                continue
            name = name.removeprefix("origin/")
            if name in (TRUNK, "HEAD"):
                continue
            # A local branch wins over its remote twin: it is the one that can still move.
            tips.setdefault(name, sha)
        # Local refs are read first so setdefault above prefers them.
    return tips


def merges_by_side_parent() -> dict[str, str]:
    """Second-parent hash → the merge commit on trunk that brought it in.

    Only first-parent merges count. A merge *into* a branch — `c1f9d97`, where
    `docs/idm-and-claude-md` pulled `main` in — is not a branch landing and must not be read as one.
    """
    found = {}
    for merge in lines("rev-list", "--first-parent", "--merges", TRUNK):
        found[git("rev-parse", f"{merge}^2")] = merge
    return found


def trunk_first_parents() -> list[str]:
    """Trunk's first-parent line, newest first."""
    return lines("rev-list", "--first-parent", TRUNK)


def field(commit: str, fmt: str) -> str:
    return git("log", "-1", "--date=short", f"--format={fmt}", commit)


class Row:
    """One branch, with everything git could prove about it."""

    def __init__(self, name: str, tip: str):
        self.name = name
        self.tip = tip
        self.merge: str | None = None
        self.fork: str | None = None
        self.opened = ""
        self.opened_sort = 0
        self.merged = ""
        self.fast_forward = False
        self.in_flight = False
        self.declared: str | None = None


def resolve(name: str, tip: str, merges: dict[str, str], trunk: list[str]) -> Row:
    """Fills in a row's dates and hashes, by whichever of the three shapes the branch is in."""
    row = Row(name, tip)

    if tip in merges:
        # The ordinary shape: merged --no-ff, so both sides of the fork are addressable.
        row.merge = merges[tip]
        row.fork = git("merge-base", f"{row.merge}^1", f"{row.merge}^2")
        first = lines("rev-list", "--reverse", f"{row.merge}^1..{row.merge}^2")[0]
        row.opened = field(first, "%ad")
        row.opened_sort = int(field(first, "%at"))
        row.merged = field(row.merge, "%ad")
        return row

    if tip not in trunk or not lines("rev-list", f"{tip}..{TRUNK}"):
        # Not merged. Either it has commits trunk does not, or it was branched and not committed to
        # yet — the second is why `tip..TRUNK` is checked as well as membership, since a branch cut
        # from trunk's head is *on* trunk and is not a fast-forward. status.md's job, not this file's.
        row.in_flight = True
        row.fork = git("merge-base", TRUNK, tip)
        own = lines("rev-list", "--reverse", f"{row.fork}..{tip}")
        first = own[0] if own else tip
        row.opened = field(first, "%ad")
        row.opened_sort = int(field(first, "%at"))
        return row

    # Fast-forwarded. The fork point is gone; see the docstring. Recover the window instead.
    row.fast_forward = True
    other_tips = {t for n, t in branch_tips().items() if t != tip}
    window: list[str] = []
    for commit in trunk[trunk.index(tip) :]:
        window.append(commit)
        if commit != tip and (commit in other_tips or len(lines("rev-parse", f"{commit}^@")) > 1):
            window.pop()  # the boundary itself belongs to whatever came before
            break
    earliest = window[-1]
    row.opened = f"~{field(earliest, '%ad')}"
    row.opened_sort = int(field(earliest, "%at"))
    row.merged = "fast-forward"
    return row


def table(rows: list[Row]) -> str:
    """The markdown table, newest-opened first."""
    out = [
        "| Branch | Opened / forked at | Merged / commit | M | Phase | What it was for |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        milestone, phase, text = DESCRIPTIONS[row.name]
        if row.declared == "pin":
            # A pin's tip moves with the trunk, so every date derived from it is "when the trunk
            # last moved" wearing the clothes of branch history. Say nothing rather than that.
            opened = "*not opened as work*<br>*moves with the trunk*"
        elif row.fork:
            opened = f"{row.opened}<br>from `{row.fork[:7]}`"
        else:
            opened = f"{row.opened}<br>*fork lost*"
        merged = (
            f"{row.merged}<br>`{row.merge[:7]}`"
            if row.merge
            else f"*{row.merged}*<br>tip `{row.tip[:7]}`"
        )
        out.append(
            f"| `{row.name}` | {opened} | {merged} | "
            f"{milestone if milestone else '—'} | {phase if phase is not None else '—'} | {text} |"
        )
    return "\n".join(out)


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "--print"
    merges = merges_by_side_parent()
    trunk = trunk_first_parents()

    rows = [resolve(name, tip, merges, trunk) for name, tip in branch_tips().items()]
    rows.sort(key=lambda r: r.opened_sort, reverse=True)

    # A declared branch is tabled whatever its topology says. See `NOT_IN_FLIGHT`.
    for row in rows:
        kind = NOT_IN_FLIGHT.get(row.name)
        if kind is None:
            continue
        row.in_flight = False
        row.declared = kind
        row.merged = "worktree pin" if kind == "pin" else "never merged"

    merged_rows = [r for r in rows if not r.in_flight]
    flight = [r for r in rows if r.in_flight]

    # A branch with no description would render as an empty cell, which is how a generated file
    # quietly turns into a worse `git branch -a`. Refuse instead.
    missing = [r.name for r in merged_rows if r.name not in DESCRIPTIONS]
    stale = [n for n in DESCRIPTIONS if n not in {r.name for r in rows}]
    # Same rule for a declaration: it names a branch by hand, so it can go stale the same way.
    stale += [n for n in NOT_IN_FLIGHT if n not in {r.name for r in rows}]

    if missing or stale:
        # Refuse to render at all: a half-written table spliced into the file is worse than none.
        for name in missing:
            print(f"NO DESCRIPTION: {name} — add it to DESCRIPTIONS in this script")
        for name in stale:
            print(f"DESCRIPTION FOR A BRANCH THAT IS GONE: {name}")
        return 1

    rendered = table(merged_rows)

    if mode == "--print":
        print(rendered)
    elif mode in ("--write", "--check"):
        target = Path(__file__).resolve().parent.parent / "reference" / "branches.md"
        text = target.read_text()
        head, _, rest = text.partition(BEGIN)
        _, _, tail = rest.partition(END)
        fresh = f"{head}{BEGIN}\n\n{rendered}\n\n{END}{tail}"
        if mode == "--write":
            target.write_text(fresh)
            print(f"wrote {len(merged_rows)} rows into {target.name}")
        elif fresh != text:
            print(f"STALE: {target.name} does not match git. Re-run with --write.")
            return 1
        else:
            print(f"{target.name} is current: {len(merged_rows)} rows.")
    else:
        print(__doc__)
        return 2

    for name in flight:
        print(f"in flight, not tabled: {name.name} (opened {name.opened}) — see docs/status.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
