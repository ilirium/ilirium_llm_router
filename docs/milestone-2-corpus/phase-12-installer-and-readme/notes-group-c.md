# Phase 12 — Group C: the installer

*Tasks 6 to 10. Entry point is `notes.md`. This is the phase's only `src/` work, and **two of its
four changes are defects the forward review found rather than planned work.***

## What was built

| | |
|---|---|
| `init` | writes a starter `config.yaml` into the working directory; refuses if one is there |
| `--version` | an argparse action, so it answers before anything can fail |
| the `.env` fix | read from beside the config file, not from wherever python-dotenv guesses |
| `config-template.yaml` | the starter, shipped inside the package |

**`make test` 438 → 445. Lint clean at the pinned `0.16.1`, `make check` valid.**

## Task 6 — `init`, and where it had to sit

**The review's finding decided the implementation, not just the plan.** `main()` had exactly two
early returns. Everything else reached `load_config`, so an `init` added as an ordinary subcommand
would have printed `Config file not found: config.yaml` **in the empty directory it exists to
serve** — the command that creates a config would have required one.

It now returns third, above `verify-archive` and `extract`, with the comment saying why it is there
for the *opposite* reason to those two: they need no config, `init` must not have one.

**The path comes from `-c`,** so `init -c other.yaml` writes `other.yaml`. Not invented here — `-c`
already names the file every other command reads, and having `init` write elsewhere would make one
flag mean two things.

## Task 7 — the template, and the two questions it carried

**Where it lives:** `src/ilirium_llm_router/config-template.yaml`, a **data file in the package**.

**Whether `uv_build` ships it: established by building, not assumed.** The plan flagged this as
unknown and said not to guess. `uv build --wheel` then reading the archive:

```
ilirium_llm_router/cli.py
ilirium_llm_router/config-template.yaml     ← present
```

**No `[tool.uv.build-backend]` section, no `MANIFEST.in`.** uv_build includes non-Python files in
the package directory by default, so the register row that asked for the configuration is answered
with *none*.

**What it contains: `config.yaml` byte for byte, and a test pins that.** The alternative — a Python
string holding YAML — ships just as reliably and would have to be kept in step by hand. That is the
second copy this project's documentation rules exist to prevent, so it is a comparison a test can
make instead of a discipline a person has to keep.

**`.env.example` is written. This reverses a decision this session made and the owner overturned**
on 2026-09-02. The argument for not writing it was that the shipped backends are `forward` and
`strip`, so no key is needed and the file is noise. **The argument against is stronger and it is
the owner's:** a template you did not get is not discoverable, and the cost of an unneeded commented
file is a reader spending ten seconds on it.

**It ships as `env-template` and is written as `.env.example`, never `.env`.** The written file is
an example a reader copies; writing `.env` would create a file the router actually *reads*, in a
directory where somebody may already have one, and no amount of refusing-to-overwrite makes that a
sound default.

**It lands beside the config, not in the working directory**, because `main()` reads
`args.config.parent / ".env"`. The two have to agree or `init -c sub/other.yaml` would leave the
example where nothing looks for it. A test pins it.

**One existing target refuses the whole command.** Writing what is missing would be friendlier and
would leave a directory half-populated by two runs with nothing saying which file came from where.
Refusing whole is what *"it refuses rather than overwriting"* predicts, and it is what a reader can
act on.

**And the repository's own `.env.example` was reworded to make byte-identity honest.** It cited
`docs/procedures/anthropic-auth-check.md` — a path an installed user does not have. Shipping that
unchanged would repeat, in the file `init` writes, exactly the defect this phase fixed in the `.env`
error message: advice the reader cannot act on. The line now says *"in the project repository"*,
which is true for both audiences.

## Tasks 8 and 9 — the two defects

**`.env` is now read from `args.config.parent / ".env"`** — beside the config it serves, which is
the rule `config.py` already uses for log, stats and corpus paths. With the default `./config.yaml`
that is the working directory, so settled row 1 holds; with `-c /elsewhere/config.yaml` it is
`/elsewhere/.env`, which the plain-cwd version would have got wrong.

**`--version` is `action="version"`,** so it prints and exits during parsing — before the config is
looked for, before `.env` is read, before dispatch. That is the point: *did the install work* has to
be answerable in a directory holding nothing.

`load_dotenv` also moved **below** the early returns, so `extract`, `verify-archive` and `init` no
longer read an environment file none of them uses.

## Task 10 — tests, and whether they test anything

**Seven tests in `tests/test_cli_init.py`. Then they were mutated, because green is not evidence.**

Three mutations applied at once — the old `load_dotenv()`, the `--version` action deleted, and
`init`'s early return removed:

```
3 failed, 4 passed
FAILED test_init_needs_no_config_to_exist
FAILED test_version_prints_and_exits_zero_with_no_config
FAILED test_dotenv_is_read_from_beside_the_config
```

**Exactly the three, each attributable to its own mutation.** Phase 11 found *twelve tests comparing
the code to itself*; this is the cheap check that stops the count growing to thirteen.

*`git status` was read immediately after restoring, per `prompt.md`'s standing warning that an
interrupted mutation left `transcript.py` comment-stripped and the suite passing. The tree held only
the three intended changes.*

## Driven, not only tested

**From a directory that has never seen this repository**, using `uvx --from` so the owner's own
installed tool was left alone:

| | |
|---|---|
| `--version` in an empty directory | exit **0**, `ilirium-llm-router 0.1.0` |
| `init` | exit **0**, `Wrote config.yaml` |
| `check` on that file, unmodified | exit **0**, `Configuration is valid.` |
| `init` again | exit **1**, `config.yaml already exists; refusing to overwrite it` |
| `check` with a `.env` beside the config and an `inject` backend | exit **0** — *the same probe returned 1 before this group* |

## An instrument that produced a false pass, caught by reading the output

**`uvx --from <path>` served a stale build, and `--refresh` did not fix it.** After `init` was
changed to write two files, `uvx --from` ran the *previous* code: one file written, and the old
"Edit it" message rather than the new "Edit them". The wheel and the source both already had the
new code — checked directly, by reading `cli.py` out of the freshly built archive.

**Nothing failed. That is what makes it dangerous:** the run exited 0, and taken at face value it
was a passing test of a feature that had not shipped. It was caught because the *message* was wrong,
not because anything reported an error.

**The reliable route is a wheel installed into a throwaway venv**, and that is how every driven
result in this section was produced after the discovery:

```
uv build --wheel -o /tmp/whl3
uv venv venv-t --python 3.13
uv pip install --python venv-t/bin/python /tmp/whl3/*.whl
```

*Group C's earlier `uvx --from` results were re-run this way and held. But the earlier ones were
taken on trust, and one of them could as easily have been stale.*

## One thing found and deliberately not acted on

**`uv build` warns that the pinned build backend excludes the installed uv:**

```
warning: `build_system.requires = ["uv-build>=0.11.32,<0.12.0"]`
         does not contain the current uv version 0.12.5
```

**It builds and installs anyway**, and every result above was produced through it. **Not bumped**,
because `../../method/IDM-003-development-tooling.md`'s standing rule is that a pin moves
deliberately and in its own commit — the ruff pin has the same rule and `CLAUDE.md` says never to
move it as a side effect. *Raised for the owner; it is not this phase's decision.*
