# Phase 12 — Group E: the close

*Tasks 15 to 17. Entry point is `notes.md`.*

## Task 15 — the register check, and it found one

**Done 2026-09-02. 28 checks, 28 passed** — but not on the first run, and not before the check
itself was tested.

**It is frozen as `evidence/register-check.py` rather than done by hand**, following Phase 11's
precedent. A check performed once in a session cannot be re-run on the trunk after the merge, which
is exactly when somebody will want to know whether the register still describes the code.

### What it found: the caveats section had five items and the owner settled four

**Settled row 6 fixes the caveats section at four items.** The `README.md` as written had five — the
fifth being that a caller disconnecting before the response generator's first step leaves no CSV row
and no corpus entry.

**The fifth was this session's own judgement, added because a reader of a caveats section is exactly
the person who should know a call can vanish.** That is a reasonable argument and it is not the
session's to make: settled row 6 is the owner's decision, and a plan's settled table is not
overridden by the plan being executed. **The fact was moved rather than dropped** — it is now a
bullet in "What it does, and what it does not", beside the other statements of what the router does
not guarantee, where it costs the caveats section nothing.

*Raised here rather than buried: if the owner would rather it were a fifth caveat, that is a
one-line move and the argument for it is above.*

### Two register rows were corrected rather than checked

**`init`'s refusal exit code cited `cli.py:49`** for the config-error path it matches. That path is
now at `cli.py:65` — the file grew by sixteen lines during the phase, which is what a line citation
does. The value, `1`, was right. **Both line numbers are now in the row**, the current one and the
one it was written against, because a citation that silently moves is worse than one that shows its
age.

**The install command row said `uv tool install <path to the repo worktree>`.** It now records that
there is **no `--force`**, which is the correction task 17's drive produced.

### The check was mutation-tested before it was trusted

**28 passing assertions prove nothing on their own** — Phase 11 found twelve tests comparing the
code to itself. Three targets were changed at once: the README's test count, the config template's
bytes, and `load_dotenv`'s argument reverted to the old broken call. **The check failed on exactly
three rows, each attributable to its own mutation.** `git status` was read immediately after
restoring, per the standing warning, and the tree held nothing.

### One check needed narrowing, for a reason that has happened before

**Testing for unvalued register rows with a plain search for the `❓` marker fails the phase.** The
marker appears in the register's own preamble and in the plan's exit criterion — two sentences that
*state the rule* — so the check reported the phase incomplete because it had documented what
complete means.

**That is the same false positive `IDM-001`'s placeholder sweep hits**, met independently, in a
different instrument, in the same week. The check looks at table rows only. *The general shape is
worth naming: a document that describes a marker will always contain the marker, so any check for
one has to distinguish a **use** from a **mention**.*

## Task 16 — the implementation plan's Phase 12 entry

**Done 2026-09-02.** `../implementation-plan.md`'s Phase 12 entry now records what was built, in the
shape Phases 10 and 11 used, and **marks the inherited commitment discharged** — Phase 11's
temporary corpus-tools section is `README.md`'s "Commands", and a 38-element sweep checked that
rather than assuming it.

It also carries the two things the phase did not settle — the `uv_build` pin bump with no rule
covering build backends, and `status.md`'s phase count going stale a third time — because an entry
that records only what was finished is the kind of document this repository keeps finding wrong.

## Task 17 — the sweep, and the merge

**The placeholder sweep runs before the merge message, not after.** `IDM-001` says so, and Phase
11's merge is the reason it says so in those words: the sweep was run afterwards, and the owner had
already found a row reading `| *(none yet)* | Groups D, E, F | not started |` sitting under two rows
naming files for two of those groups.
