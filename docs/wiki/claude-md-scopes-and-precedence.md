# `CLAUDE.md` scopes, and what an instruction there can and cannot override

**Read this before putting a rule in a `CLAUDE.md` and expecting it to win** — against another
`CLAUDE.md`, against a setting, or against something in Claude's system prompt. The four scopes are
**concatenated, not overridden**, and the whole mechanism is **context rather than enforcement**,
which decides what it can actually beat.

**Established 2026-08-20** against **Claude Code v2.1.228**, by reading the upstream memory
documentation. **The worked example throughout is a real one from this repository**: making Claude
use the `Edit`/`Write` tools for file changes instead of the shell heredocs auto mode asks for — see
`claude-code-auto-mode.md` for why that came up.

---

## The four scopes, in load order

**Broadest first. A later file's instructions appear in context after an earlier one's.**

| Scope | Location | Shared with |
|---|---|---|
| **Managed policy** | one path per OS — see the block below | Everyone on the machine. **Cannot be excluded** by individual settings |
| **User** | **`~/.claude/CLAUDE.md`** | **Just you, every project** |
| **Project** | the repository root — see below | The team, through source control |
| **Local** | the repository root — see below | Just you, this project. Gitignore it |

*The paths are in a fenced block rather than inline, deliberately: they name files on other machines
and generic repository-root forms, and `../procedures/link-check.py` resolves an inline backticked
path against **this** repository. Measured 2026-08-20 — the checker skips fenced blocks and reports
inline ones, so a page about somebody else's layout puts its paths in a fence or adds false
positives to everyone's baseline.*

```
Managed policy   macOS    /Library/Application Support/ClaudeCode/CLAUDE.md
                 Linux    /etc/claude-code/CLAUDE.md
                 Windows  C:\Program Files\ClaudeCode\CLAUDE.md
User                      ~/.claude/CLAUDE.md
Project                   ./CLAUDE.md   or   ./.claude/CLAUDE.md
Local                     ./CLAUDE.local.md
```

**Files are also discovered by walking up the directory tree** from the working directory, and files
in *subdirectories* load on demand when Claude reads a file there. Within one directory,
`CLAUDE.local.md` is appended after `CLAUDE.md`.

**The key sentence, quoted rather than paraphrased:**

> All discovered files are concatenated into context rather than overriding each other.

**So there is no precedence in the settings sense.** A user-scope rule is not *replaced* by a project
rule that disagrees; both are present, and the documentation is blunt about the result:

> If two rules contradict each other, Claude may pick one arbitrarily.

**Ordering is the only lever**, and it is weak: instructions closer to where you launched Claude are
read last.

## What a `CLAUDE.md` instruction can actually override

**This is the part that gets assumed wrong, and the documentation states it plainly:**

> CLAUDE.md content is delivered as a user message after the system prompt, not as part of the system
> prompt itself. Claude reads it and tries to follow it, but there's no guarantee of strict
> compliance, especially for vague or conflicting instructions.

And, of both memory mechanisms:

> Claude treats them as context, not enforced configuration.

**Two consequences worth having in front of you before you write the rule:**

1. **Against another `CLAUDE.md`, it is a coin-flip when they contradict.** Fix that by removing the
   contradiction, not by ordering.
2. **Against a system-prompt instruction, it is context arguing with the prompt.** It often works. It
   is not a mechanism, and it cannot be verified the way a settings key can.

### The three tiers, from weakest to strongest

| Want | Use | Strength |
|---|---|---|
| Behavioural guidance | `CLAUDE.md` | **Context.** No compliance guarantee |
| The same, at system-prompt level | `--append-system-prompt` | Stronger placement, but **must be passed on every invocation** — suited to scripts, not interactive use |
| It must happen, whatever Claude decides | **A `PreToolUse` hook** | **Enforced by the client.** Runs regardless of what Claude decides |

> If the instruction is something that must run at a specific point… write it as a hook instead.
> Hooks execute as shell commands at fixed lifecycle events and apply regardless of what Claude
> decides to do.

## The worked example: preferring `Edit`/`Write` over shell heredocs

**The weak version, and it is still the one to try first**, in `~/.claude/CLAUDE.md` so it applies to
every project and stays out of any checked-in repo file:

```markdown
## Editing files

Use the `Edit` and `Write` tools to change files. Do not edit through the shell —
no `sed -i`, no `python - <<'PY'` heredocs, no `>` redirection onto a tracked file.
Bash stays for running things and for read-only inspection.
```

**Specific and verifiable, which the documentation says matters** — *"Use 2-space indentation"*
beats *"format code properly"*. Naming the three shell forms is what makes it checkable rather than
a preference.

**The strong version, if the weak one does not hold.** A `PreToolUse` hook on `Bash` can inspect the
command and deny it with a reason, which is enforcement rather than persuasion. That is the
documented answer for *"must happen at a specific point"*, and it is the honest fallback — but it
needs care not to block legitimate shell work, so build it with the `update-config` skill's
construct-and-verify flow rather than by hand.

**Where this rule does *not* belong: a checked-in project `CLAUDE.md`.** How an agent edits files is
a personal tooling preference, not a project convention — the documentation's own split is *"focus on
project-level standards rather than personal preferences"* for the shared file.

## Practical limits worth knowing before you write one

- **Target under 200 lines per file.** *"Longer files consume more context and reduce adherence."*
  There is no hard cap — `CLAUDE.md` is loaded in full however long it is — which makes this a
  discipline rather than an error you will be shown.
- **`@path` imports do not save context.** Imported files are expanded and loaded at launch. They
  help organisation only.
- **Path-scoped rules do save context.** `.claude/rules/*.md` with `paths:` frontmatter load only
  when Claude reads a matching file.
- **Block-level HTML comments are stripped** before injection, so maintainer notes cost nothing.
- **Project-root `CLAUDE.md` survives compaction** — re-read from disk and re-injected. **Nested
  `CLAUDE.md` files and path-scoped rules are not** re-injected; they reload the next time a matching
  file is read. An instruction given only in conversation does not survive at all.

## How to check what actually loaded

**Do not assume a file was read.** `/context` lists the memory files that loaded in the current
session — a file missing there is invisible to Claude, whatever it contains. `/memory` lists the
locations across user and project scope, *including files that do not exist yet*, and creates one if
you select it. For a full trace of which instruction files loaded, when and why, there is an
`InstructionsLoaded` hook.

## Reading list

- **How Claude remembers your project** (the canonical page for everything above) — <https://code.claude.com/docs/en/memory>
- Hooks, for the enforcement tier — <https://code.claude.com/docs/en/hooks-guide>
- CLI reference, for `--append-system-prompt` — <https://code.claude.com/docs/en/cli-reference>
- Settings, and how they differ from behavioural guidance — <https://code.claude.com/docs/en/settings>
- Debug your configuration — <https://code.claude.com/docs/en/debug-your-config>

*Upstream landing pages, chosen to outlive version numbers. **All fetched from this machine on
2026-08-20.***

## Where these claims came from, and what expires

| Claim | How it was established |
|---|---|
| The four scopes, their paths, and load order | Read the memory page, 2026-08-20 |
| **Files are concatenated, not overridden** | Quoted from that page |
| **`CLAUDE.md` is a user message after the system prompt, with no compliance guarantee** | Quoted from that page's troubleshooting section |
| Contradictory rules are resolved arbitrarily | Quoted |
| Hooks are the enforcement tier; `--append-system-prompt` the middle one | Quoted |
| 200-line guidance, imports not saving context, compaction behaviour | Read from the same page |

**A correction this page exists to carry.** When the Edit/Write question first came up in this
repository, the recommendation was that a `CLAUDE.md` instruction *"should win"* against auto mode's
shell-editing instruction, on the strength of `CLAUDE.md` being described as overriding default
behaviour. **The documentation does not support that.** It places `CLAUDE.md` *after* the system
prompt as ordinary context and explicitly declines to guarantee compliance. The instruction is still
worth writing — it is the cheapest lever and it usually works — but **"should win" was an overclaim,
and the enforceable answer is a hook.**

**What expires:** the version pin, the managed-policy paths, and the CLI flag names. **What does
not:** that `CLAUDE.md` is context rather than configuration, that scopes concatenate instead of
overriding, and that **anything which genuinely must happen belongs in a hook** — the same
distinction this repository's own `method/IDM-002` draws between a permission rule and a convention.
