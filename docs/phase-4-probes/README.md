# Phase 4 probes — sending LM Studio the awkward shapes

The instrument behind the findings in `../phase-4-notes.md`. LM Studio publishes no compatibility
table, so the only way to learn what it supports is to send the shape and read the answer.

**Meant to be re-run**, like `../phase-3-verification/` and unlike `../phase-2-step-6-session/`.
Every finding here expires the next time LM Studio ships a release, and re-running is how you find
out that it has.

## What is here

| | |
|---|---|
| `probe.py` | Sends one body through the router and reports what came back — status, event sequence, content block types, usage, and the CSV row the call wrote |
| `bodies/*.json` | One minimal request each, carrying exactly **one** unusual element, so a rejection names the element rather than the request |
| `make_image.py` | Regenerates `bodies/image.json`. Hand-rolled PNG; the project has no image dependency and needs none |
| `runs/` | Full transcripts. Gitignored — this is a tool, and its findings belong in the notes. **Each probe overwrites its own file**, so a result worth keeping must be copied out before the next run |

**Four results from this directory are frozen in `../phase-4-evidence/`** and must not be regenerated
from here. Re-running reproduces most of what these probes measure, which is why `runs/` is
disposable — but not the cold-cache replay, not the over-window refusal, and not the read timeout.
The rule is "does re-running produce the same number", not "is this a tool or evidence"; see that
directory's README.

## Running it

Needs the router up and a model loaded in LM Studio.

```
make run
python3 docs/phase-4-probes/probe.py --list
python3 docs/phase-4-probes/probe.py baseline
python3 docs/phase-4-probes/probe.py replay
```

`--model` picks a different local model, `--max-tokens` overrides the body's own, `--no-stream` asks
for a buffered reply — the non-streaming path is a different scanner in the recorder and a different
`usage` shape from the backend, so it is worth running both ways at least once.

**Start with `baseline`.** It carries nothing unusual. If it does not come back `PROBE OK`, the
problem is the router, the model or this script, and every other result is worthless until it does.

## Why the report says more than a status code

Three traps, each of which has already caught this project once:

- **An error can hide inside an HTTP 200.** LM Studio answers `count_tokens` that way — 32 rows of
  `calls.csv` are logged `ok` and are not (`../epd/EPD-002-token-counting-for-local-backends.md`).
  `probe.py` looks for an error shape in the body regardless of status, and says
  `REJECTED — inside an HTTP 200` when it finds one.
- **Accepted is not honoured.** A backend can take a field and ignore it. That is why the probes ask
  for something checkable: `system-role-message` asks a question in English and instructs *in the
  system message* to answer in French, so "Bleu" proves the message was read, while a correct English
  answer proves it was accepted and discarded. The two are different findings and a status code tells
  them apart not at all.
- **The image probe cannot be passed by agreeing.** Four colours in a stated order is not something a
  model guesses. A single solid colour would have been — expect `red green blue yellow`.

## The warning worth reading before trusting a result

Inherited from `../phase-3-verification/README.md`, which earned it: its first stand-in backend sent
a malformed reply, Claude Code complained, and **the complaint was worthless** because it fitted the
instrument as well as the subject.

So: `bodies/image.json` was rendered and looked at before it was ever sent, and the headers come from
`../log-the-whole-request.txt` at runtime rather than being retyped here — including the ten-entry
`anthropic-beta` list, which is itself one of the things under test.

If a result from this directory is surprising, suspect the instrument first.
