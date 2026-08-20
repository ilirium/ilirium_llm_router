# Claude Code's auto mode, and the working-style instruction that is not in the docs

**Read this when a session is spending an unexpected share of its context on tool results, when you
want to change *how* Claude edits files rather than *what it may do*, or before you go looking in
`settings.json` for a knob that turns out not to exist.**

**Established 2026-08-20** against **Claude Code v2.1.228**, by reading the published documentation,
the settings JSON schema this build ships, and the system-reminder text of a live auto-mode session.

**A boundary note, because this tier's own test asks for one.** `README.md` says `wiki/` is for *"a
library, protocol or tool we are built on"* and asks whether the page would help a different project
using the same tool. **Claude Code is not a dependency of the router — it is the tool this repository
is built *with*.** The second test is what places it here: everything below is true for any project
using Claude Code, and none of it is about this router. `CLAUDE.md`, `method/IDM-*` and `prompt.md`
already exist to steer this tool, so it is a real dependency of the *work* if not of the *program*.

---

## What auto mode is, and what it is not

**Auto mode is a permission mechanism.** It routes tool calls through a second model — the classifier
— which blocks actions that are irreversible, destructive, or aimed outside your environment, instead
of prompting you for each one. On Pro, Max and Team plans it is the built-in starting mode.

**It is configured through the `autoMode` settings block**, whose entire surface is the classifier:

| Key | What it controls |
|---|---|
| `autoMode.environment` | What the classifier treats as inside your trust boundary — repos, buckets, domains, services. Prose, not patterns |
| `autoMode.allow` | Exceptions to soft blocks |
| `autoMode.soft_deny` | Destructive actions that explicit user intent can clear |
| `autoMode.hard_deny` | Unconditional boundaries that intent cannot clear |
| `autoMode.classifyAllShell` | Suspend narrow `Bash(...)` allow rules so every shell command reaches the classifier |

**Include the literal `"$defaults"` in any of those arrays** or you replace the built-in list
entirely — including the force-push, `curl | bash` and data-exfiltration rules.

**The classifier does not read project settings.** `autoMode` is read from `~/.claude/settings.json`,
managed settings, and `--settings` only — never `.claude/settings.json` or `.claude/settings.local.json`,
because both live in the repo and a checked-in file could otherwise inject its own allow rules.

## The finding: auto mode also changes *how* Claude works, and that part is undocumented

**A live auto-mode session carries a system-reminder beginning `While auto mode is active:` that tells
Claude to prefer the Bash tool for file changes** — to read with `cat`/`head`/`sed`, search with
`grep`, and **make edits with `sed`, heredocs or short scripts rather than the `Edit`/`Write` tools**,
falling back to a dedicated tool only when Bash genuinely cannot do the job.

**None of that is in the documentation.** Both auto mode pages describe only the permission
mechanism; searching them for `heredoc`, `sed`, "Edit tool", "Write tool", "prefer Bash" and
"instead of" returns nothing. **And the settings schema exposes no key for it** — it is not in
`autoMode`, not in `permissions`, and not a top-level setting.

**So the honest statement is narrow:** the behaviour is *gated on* auto mode, because the reminder
says so and it is observable in the transcript; it is **not documented, and not configurable through
settings.** Anyone who states more than that — as this repository's first attempt at this page did —
is reasoning from the reminder's wording and calling it design.

### Why it is worth knowing rather than merely curious

**Editing through Bash heredocs makes the harness echo the modified file back.** Each such edit
returns a *"this file was modified"* notice carrying a large excerpt, where `Edit` returns a one-line
confirmation. Over a long session that is the difference between a few hundred tokens and tens of
thousands. **Measured on this repository, 2026-08-20:** a session that edited five source files
repeatedly through heredocs attributed **187.5k tokens (19% of a 1M window)** to Bash results, with
the file echoes the largest avoidable share.

**It also interacts badly with large files.** `cat` on a 37 KB source file spills to a persisted
tool-result file; `sed -n '1,200p'` sweeps over a 1,500-line document read far more than a targeted
section would.

## How to check this yourself, in this or any later version

**Do not take the paragraphs above on trust — every one of them is checkable, and the version pin at
the top is the reason to re-check.**

| Question | How to answer it |
|---|---|
| Is the Bash preference a **classifier rule**? | `claude auto-mode defaults` prints the built-in `allow` / `soft_deny` / `hard_deny` / `environment` lists as JSON. **If the instruction is absent there, it is not classifier configuration** — it is in the auto-mode system prompt, with no exposed knob |
| What is my **effective** config? | `claude auto-mode config` — same four lists with your settings applied and `"$defaults"` expanded in place |
| Are my custom rules sane? | `claude auto-mode critique` flags ambiguous, redundant or false-positive-prone entries |
| Is there a settings key I missed? | The `update-config` skill prints the full settings JSON schema; search it for the behaviour rather than guessing a key name |
| Is it really tied to auto mode? | Start a session in another permission mode and see whether the `While auto mode is active:` reminder appears at all |

## What you can actually do about it

**There is no setting, so all three levers are indirect.**

1. **Turn auto mode off** — `permissions.defaultMode` set to another mode, or `disableAutoMode:
   "disable"`. Removes the instruction and the classifier together. If you have invested in an
   `autoMode.environment` block, this throws that away.
2. **Counteract it in `CLAUDE.md`.** The documentation says the classifier *"reads the same CLAUDE.md
   content Claude itself loads"* and — the sentence that matters — **"Start there for project
   conventions and behavioral rules."** A user-level `~/.claude/CLAUDE.md` keeps it out of a
   checked-in repo file, which is right for a personal tool preference rather than a project rule.
   **The caveat is real: this is an instruction competing with an instruction, not a switch.**
3. **Change reading habits instead.** Grep for structure before reading a file whole; read long
   documents by section rather than in wide `sed` sweeps. This costs nothing and helps in every mode.

## Reading list

- **Configure auto mode** — <https://code.claude.com/docs/en/auto-mode-config>
- **Choose a permission mode** — <https://code.claude.com/docs/en/permission-modes>
- **How we built Claude Code auto mode** (engineering deep dive) — <https://www.anthropic.com/engineering/claude-code-auto-mode>
- Settings reference — <https://code.claude.com/docs/en/settings>
- Permissions, and the rules evaluated before the classifier — <https://code.claude.com/docs/en/permissions>
- Memory and `CLAUDE.md` — <https://code.claude.com/docs/en/memory>

*Upstream landing pages, chosen to outlive version numbers. **All fetched from this machine on
2026-08-20.***

## Where these claims came from, and what expires

| Claim | How it was established |
|---|---|
| Auto mode is a permission classifier, and the five `autoMode` keys | Read both upstream pages, 2026-08-20 |
| `autoMode` is not read from project settings | Stated on the configuration page, quoted above |
| **The Bash-preference instruction exists and is gated on auto mode** | **Read from the live system-reminder in an auto-mode session.** Not from documentation — there is none |
| **It is absent from the documentation** | Searched both auto mode pages for `heredoc`, `sed`, "Edit tool", "Write tool", "prefer Bash", "instead of" — no matches |
| **No settings key controls it** | Searched the full settings JSON schema this build ships, via the `update-config` skill |
| Heredoc edits cause the harness to echo the file back | Observed across ~10 edits in one session; the token share came from `/context` |

**What expires:** the version pin, the `autoMode` key list, the CLI subcommand names, and — most
likely of all — **whether the Bash-preference instruction is still present, still worded this way, or
still tied to auto mode.** It is undocumented, so nothing obliges it to stay.

**What does not:** that `autoMode` configures the *classifier* and not Claude's working style; that
the classifier ignores project-scoped settings; and that **an undocumented instruction observed in a
system-reminder is evidence about this build only** — which is the same discipline
`zstandard-and-libzstd.md` applies to a docstring from the backend that is not running.
