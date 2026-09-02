# The `.env` discovery probe

**Run 2026-09-02 from an installed `ilirium-llm-router 0.1.0`**, installed with
`uv tool install ./main` and resolving to `~/.local/bin/ilirium-llm-router`. Re-runnable: everything
below happens in an empty directory.

**What it establishes:** an installed router **does not read a `.env` from the working
directory**, and the error it produces tells the user to do the thing they have already done. This
is the evidence behind the phase's `.env` fix; the mechanism is in `../notes.md`.

## Setup

```sh
mkdir t3 && cd t3
cp <repo>/config.yaml .
# switch the lmstudio backend from `strip` to `inject`, so a key is required
sed -e 's/^    credential: strip$/    credential: inject\n    api_key_env: PHASE12_TEST_KEY/' \
    config.yaml > cfg-inject.yaml
printf 'PHASE12_TEST_KEY=probe-value\n' > .env
```

`ls -a` at this point shows `.env`, `cfg-inject.yaml`, `config.yaml` — **and nothing else.**

## The probe, and the control

| Run | Exit | Result |
|---|---|---|
| `check -c cfg-inject.yaml`, with `./.env` present | **1** | the variable is reported unset |
| the same, with `PHASE12_TEST_KEY` exported | **0** | `Configuration is valid.` |

**The control is what makes it a measurement rather than an observation.** Exporting the variable
fixes it, so nothing about the backend, the config or `_check_api_keys` is at fault — **only the
discovery of `.env`.**

## The message it produces, quoted exactly

```
error: Backend 'lmstudio' has 'credential: inject' and expects its API key in the environment
variable 'PHASE12_TEST_KEY', which is unset or empty.
Set it in your .env file, or switch that backend to 'credential: forward' or 'credential: strip'
if it needs no key of its own.
```

**"Set it in your .env file" is advice the user has already followed.** The file is in the directory
they are standing in. That is what makes the defect worse than a missing feature: the tool does not
fail silently, it fails while giving an instruction that cannot work.

*Exit codes taken from unpiped runs. The first attempt piped to `tail` and reported `exit=0` for the
failing run — `$?` after a pipe is the last command's status, which `prompt.md` already warns about
and which this session walked into anyway.*
