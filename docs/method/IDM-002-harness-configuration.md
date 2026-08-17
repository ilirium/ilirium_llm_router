# IDM-002 — Harness configuration: the permission allowlist

**In force 2026-08-17.** The one home for what goes in `.claude/settings.json`, what stays in
`.claude/settings.local.json`, and why. Built in Phase 8 from `EPD-004` decision 17.

---

## The split

| File | Tracked | Holds |
|---|---|---|
| `.claude/settings.json` | **yes** | durable project policy — how this project is built, tested and probed, plus a deny rule |
| `.claude/settings.local.json` | **no**, by `.gitignore` | machine accretion: whatever this laptop clicked *allow* on |

**They are split the way the documents are split.** A tracked file says *this is how the project
works*, which is knowledge belonging to the project rather than to one laptop. An untracked one records
what one session happened to need.

**The two files must not overlap.** Every permission has exactly one home. A duplicated entry looks
harmless and is not: narrowing the tracked file later *appears to do nothing*, because the local copy
still grants it.

**A set intersection is the cheap check and it is not sufficient.** A **glob** in one file silently
subsumes an **exact** entry in the other while intersecting nothing. Live example, and it is left in
place deliberately: `Bash(uvx ruff *)` is local, `Bash(uvx ruff@0.16.1 format --check src tests)` is
tracked, and the intersection is empty — but the glob already grants any ruff version, so the tracked
entry grants nothing that was not granted anyway. **It is there to write the pin down, not to enforce
it**, and `IDM-003-development-tooling.md` says why the pin is not enforceable by an allowlist. Read the
intersection as *no literal duplicate*, and then read the globs.

**The local file is pruned periodically**, and pruning is the point rather than housekeeping. Phase 8
took it from 53 entries to 21; fifteen were fossils and duplicates that no longer described anything.

## The admission test for the tracked half

**Is this fact derivable from `config.yaml`, the `Makefile`, or `pyproject.toml`?**

If yes it is project policy and belongs in the tracked file. If no it is machine accretion and belongs
in the local one. That is the whole test, and it decides the cases that look hardest:

- `Bash(make test *)` — the `Makefile` has a `test` target. **Policy.** And so is every other target it
  declares: all eight are in the tracked file, plus bare `make`, which lists them.

  > **Two of them arrived late, and the reason is worth keeping.** Phase 8 wrote the tracked file with
  > **six** `make` entries — the six that had accreted into the local file — under a specification
  > reading *"every `make` target"* and a decided count of fourteen entries that could only be reached
  > with six. The count won, because Phase 8's deduplication arithmetic was built on it. `make sync` and
  > `make clean` were added on **2026-08-17**, immediately after, bringing the tracked file to **16**.
  > `make sync` is a fresh clone's *first* command, so prompting for it contradicted the very reason four
  > `config.yaml` probes had been promoted — *is the thing even running?* is a contributor's day-one
  > question and *how do I install it?* comes before that. **The admission test decides this on its own:
  > if a target is in the `Makefile`, it is policy.** The phase note records fourteen, correctly, as what
  > was true when it was written.
  >
  > `make help` went in at the same time and brought the file to **17**, even though nobody types it —
  > `.DEFAULT_GOAL := help`, so bare `make` already does that job. It is there so the rule above holds
  > **without an exception to explain.** Seven of eight targets present is a state that makes the next
  > reader hunt for which one is missing and why; eight of eight costs one line and asks nothing.
- `Bash(uvx ruff@0.16.1 format --check src tests)` — the `Makefile` pins `ruff@0.16.1` and
  `pyproject.toml` sets `line-length = 100`. **Policy**, and the entry is one of the places the pin is
  written down. See `IDM-003-development-tooling.md`.
- `Bash(ps -p 90607 -o pid,stat,command)` — a PID from one afternoon. **Accretion**, and by now not even
  that.

### A literal that appears in `config.yaml` is a constant, not a fossil

**This is the mistake worth stating, because it was made once and is easy to repeat.** Two entries look
exactly like machine junk and are project knowledge:

| Entry | Why it is a constant |
|---|---|
| `Bash(lsof -nP -iTCP:8787 -sTCP:LISTEN)` | `8787` is the router's configured port, `config.yaml:10` |
| `Bash(curl -s --max-time 5 http://localhost:1234/api/v1/models)` | `localhost:1234` is the LM Studio backend's `base_url`, `config.yaml:40` |

Both answer *is the thing even running?*, which is a contributor's first question on day one. A hardcoded
number is not evidence of a fossil; the test is whether the number is **in a committed file**. Along with
`Bash(lms --version)` and `Bash(lms ps *)` these were called machine junk on a first pass and promoted on
the second.

## What deliberately stays out of the tracked half

**Arbitrary execution and arbitrary network.** `Bash(curl *)`, `Bash(python3 *)` and `Bash(uv run *)` are
how this project is actually worked on — and a file whose job is to *state policy* should not bless them.
They stay local.

**The cost is accepted and named:** a fresh clone prompts for those until somebody approves them. That is
the correct outcome. A contributor being asked once before an agent runs arbitrary Python is a feature of
the arrangement, not friction in it.

## The `.env` deny

`.env` exists in this repository with real keys in it. `CLAUDE.md`'s working agreement — *ask before
touching the machine: GUI settings, `.env`, long-running local servers* — names it as a written rule.
The deny makes it enforced.

**The pattern must be exact-match, and this is a trap worth naming.** A glob like `Read(./.env.*)` also
matches **`.env.example`** — which is committed, carries no secrets, and is the file that documents which
key each backend needs. **Deny beats allow in precedence**, so a glob cannot be re-allowed for the
example afterwards. So: deny `Read(./.env)` and the `cat` form in both spellings a session would type,
and **do not glob**.

**What the deny is and is not.** It stops the reflex, not a determined path — `sed`, `head`, `python3` and
`env` all still read the file. That is not a hole to be plugged; it is the next section's argument.

### This does not reopen `EPD-004` decision 19

Decision 19 refused a `PreToolUse` **hook** that would parse shell quoting to block `$(...)`, on **six**
grounds: real false positives in this repository, undecidability without a shell parser, converting a
recoverable prompt into a hard block, sitting in the path of every Bash call, the written rule holding on
its own, and enforcement being unable to teach the alternative.

**An exact-path deny has none of the first four.** It cannot false-positive, needs no parser, blocks one
named path rather than a syntax, and runs no code. **And the last two argue against enforcing a *reflex*,
not against denying a *path*.** Recorded here because the next reader will otherwise see enforcement
where a refusal is on file and conclude the refusal was quietly overturned.

## What a permission does when nobody re-reads it

**A permission granted to get through a task can outlive the task and overrule a rule nobody re-read.**

Found in Phase 8, in this repository, and it is the strongest reason the local file gets pruned.
`Bash(lms load *)` and `Bash(lms unload *)` were allowlisted by clicking *allow* during Phase 4 probe
work. Loading a model into LM Studio evicts whatever is loaded and takes minutes — which is exactly what
`CLAUDE.md` means by *"ask before touching the machine … long-running local servers: ask rather than
detect-and-proceed."* **An allowlist entry had silently repealed a non-negotiable.**

Both were removed so they prompt again. **The finding is the class, not the fix:** an allowlist is a
record of past convenience, and it is read by the harness rather than by a person, so nothing makes a
session notice that an entry contradicts a written rule. Pruning is when somebody looks.

### The sharp edges that are staying

Named so that keeping them is a decision rather than an oversight:

| Entry | The edge |
|---|---|
| `Bash(curl *)` | arbitrary outbound network. **Kept:** it is how probes get written, and removing it buys a prompt on every one-off |
| `Bash(git checkout *)` | mostly branch switching, which this workflow does constantly. **Kept.** The destructive form is `git checkout -- <path>`, which discards uncommitted work |

## Two harness tools, and which file each belongs to

**`/fewer-permission-prompts` writes into the wrong file.** It scans transcripts for common tool calls
and writes an allowlist into the project's **tracked** `.claude/settings.json` — which is machine
accretion, generated automatically, landing in the file this split reserves for curated policy. **Its
output belongs in the local half.** Named explicitly because the command's name makes it sound like
precisely what this document is for, and a future session will reach for it.

**`/permissions` is the tool for reading the *effective* rule set**, which is the thing neither file shows
on its own: the harness merges tracked and local, and the merge is what actually governs. `settings.json`
is hand-written so the diff stays reviewable; `/permissions` is how the *result* is verified.

## Provenance

- **`EPD-004` decision 17** — the split, with an addendum dated 2026-08-17 recording that it is built,
  that the entry count had drifted from 51 to 53, and that the tracked half deliberately excludes the
  broad execution entries the decision itself flagged.
- **`EPD-004` decision 19** — the refusal this document is careful not to appear to overturn.
- **Replaces** `../README.md`'s "Where the harness configuration lives", which is now a pointer here.
- **Built and measured in** `../milestone-2-corpus/phase-8-method-and-guardrails/`, whose `notes.md`
  carries the before-and-after counts. The prune produced no commit, because the file it edits is
  gitignored.
