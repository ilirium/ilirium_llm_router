# EPD-001 — Model selection and mixed-model sessions

**Status: proposal. Written 2026-07-30. No decision is taken here.** By agreement the spec decision
is deferred until Phase 4 is done, because Phase 4 is what establishes how much of a real session a
local model can actually carry — and that answer changes how much this is worth building.

Nothing in this document has been implemented, and the parts marked *documented* below have not been
run against this router even once. Read the verification table before acting on any of it.

**One exception**, so this file does not misrepresent itself: the two CSV identifier columns were
accepted into the spec on the day this was written, because they are nearly free while Phase 2 is
being built and awkward afterwards. They are specified, not written. Everything else waits.

---

## Phase 4 addendum, 2026-08-06 — the gate is met; the decision is still not taken

The deferral above names a condition: **how much of a real session a local model can carry.** Phase 4
answers it, and the answer is *most of it*. Full detail in `../phase-4-notes.md`; the parts that bear
on this document:

- **Nothing was rejected.** Tool calls, tool results, images, `thinking` blocks, a system-role message
  inside `messages`, and the entire captured 118 KB Claude Code request all work against
  `qwen/qwen3.5-9b` unmodified.
- **A real session already happened.** The Phase 2 step 6 session ran 99 calls against this same model
  — multi-turn, subagents, tool use, file editing — which is why Phase 4 did not run another.
- **Mixed-model sessions are measured, not hypothetical.** Two client sessions in
  `../phase-2-step-6-session/calls.csv` reached both backends, and seven rows carry a subagent's
  `agent_id`. The per-request dispatch this document says already satisfies the subagent requirement
  does satisfy it.

So the reason for waiting is discharged. **This does not accept the proposal** — an EPD is accepted
deliberately, on a stated date, or not at all, and nobody has taken that decision. What has changed is
that the objection "a picker full of local models is worth nothing until a local model can hold a
session" no longer applies.

Two findings from Phase 4 that a model picker would have to live with, neither of them blocking:

- **The usable window is bounded by time, not by its size.** The router's 600 s read timeout is
  reachable by an ordinary large request — a ~41000-token call against a 44544-token window was
  killed while the backend was still healthily prefilling. Offering a model in a picker implies it can
  be used at its stated context; on this hardware it cannot.
- **Cold prompts are slow enough to look broken.** 197 s to first byte for a one-word turn against a
  cold cache, 50 s against a warm one. Anything that switches models mid-session pays the cold number
  on the first turn after the switch.

## The requirement this document is about

Two things the repository owner wants, stated on 2026-07-30:

1. Choose a locally served LM Studio model with the **`/model` command inside a running session**,
   not only with `--model` at launch.
2. Run **subagents on local models at the same time** as the main conversation runs on a Claude
   model — mixed models within one session.

Both are aimed at a "first release" that covers Claude plus LM Studio, before other cloud providers
and other local runners arrive.

## Neither is in the specs

Checked rather than recalled, by grepping `docs/` and `README.md` for `/model`, `subagent`, `agent`
and `picker`:

| Where | What it says | Gap |
|---|---|---|
| `README.md:12-14` | "pick up different models in LM Studio"; Claude Code has access to its own models and local ones "simultaneously" | Closest thing to the requirement. It is about *serving*, and "simultaneously" is never pinned down to mean *within one session* |
| `docs/implementation-plan.md:66-68` | Phase 1 done-when is `claude --model claude-sonnet-5` and `claude --model <some-local-model>` | A launch flag, **one model per session**. Mid-session switching appears nowhere |
| everywhere | — | **Subagents are mentioned zero times in the repository** |
| `docs/implementation-plan.md:237` | a combined model list endpoint is "Not doing yet" | The mechanism that would populate the picker is explicitly out of scope |

So requirement 1 is half-implied and requirement 2 is absent. That is the finding: these are not
things the current specs promise, and they should be written down as requirements before anything
gets designed around them by accident.

## What already works with no change to the router

Dispatch is per-request on the `model` field in the body (`routing.py:23`) and holds no session
state. That single property is what makes mixed-model sessions an architectural non-event: a session
whose main loop is `claude-sonnet-5` and whose subagent is `google/gemma-4-e4b` produces two requests
that route independently and correctly. **No router code is required for requirement 2.**

Three client-side facts complete the picture, all from Claude Code's documentation:

- **`/model <any-string>` is not validated behind a custom base URL.** Claude Code normally rejects
  an unrecognised model ID, but "the check runs only on the Anthropic API… behind an LLM gateway or a
  custom `ANTHROPIC_BASE_URL`, your provider or gateway defines the model names, so Claude Code
  passes any string through without checking it." So `/model google/gemma-4-e4b` should already work
  against the Phase 1 router.
- **Subagent frontmatter takes a full model ID.** The `model` field accepts `sonnet`, `opus`,
  `haiku`, `fable`, a full model ID, or `inherit`, and "accepts the same values as the `--model`
  flag". A `.claude/agents/local-helper.md` carrying `model: google/gemma-4-e4b` is the mechanism for
  requirement 2.
- **Subagent model resolution order** is `CLAUDE_CODE_SUBAGENT_MODEL` → per-invocation `model`
  parameter → frontmatter → the main conversation's model. The environment variable overrides both of
  the others, so it is also the blunt instrument for putting *every* subagent on a local model.

## Three ways to reach a local model, in order of cost

| Mechanism | What it buys | Cost | Blocker |
|---|---|---|---|
| Type `/model <exact-lmstudio-id>` | Everything functional | Nothing at all | Must retype a long ID; no picker row |
| `ANTHROPIC_CUSTOM_MODEL_OPTION` | One labelled row in the picker | Three env vars, restart to change | **One entry only** |
| Gateway model discovery | Every local model in the picker | A `/v1/models` endpoint plus an unresolved design question | The ID prefix filter — see below |

The important thing about the first row: the picker entry is **ergonomics, not capability**. Nothing
in requirement 1 is impossible today; it is merely inconvenient. That is the main reason this can wait
for Phase 4.

### `ANTHROPIC_CUSTOM_MODEL_OPTION`

Adds exactly one extra row to the `/model` picker, with validation disabled for that row.

```bash
export ANTHROPIC_CUSTOM_MODEL_OPTION="google/gemma-4-e4b"
export ANTHROPIC_CUSTOM_MODEL_OPTION_NAME="Gemma 4 E4B (local)"
export ANTHROPIC_CUSTOM_MODEL_OPTION_DESCRIPTION="LM Studio via ilirium_llm_router"
```

- Only the first is required. `_NAME` defaults to the model ID, `_DESCRIPTION` to
  `Custom model (<model-id>)`.
- The row appears at the bottom of the picker, alongside the built-in aliases rather than replacing
  them.
- "Claude Code skips validation for the model ID set in `ANTHROPIC_CUSTOM_MODEL_OPTION`, so you can
  use any string your API endpoint accepts."
- Read at **startup**: export before launching `claude`, or restart the session.

Why it suits this router better than discovery does: it carries **no prefix filter**, so the real LM
Studio ID goes in the picker, arrives in the body verbatim, and `backend_name_for_model` sends it to
LM Studio with no rewrite, no cache-prefix damage, and no change to the routing rule.

Limits that matter:

1. **One entry, singular** — there is no list form. Requirement 1 is about picking *different* local
   models, and this gives one per session.
2. **`_SUPPORTED_CAPABILITIES` does not apply here.** The suffix exists for this variable, but those
   capability declarations "take effect on third-party providers", and the gateway protocol page is
   explicit that `ANTHROPIC_DEFAULT_*_MODEL_SUPPORTED_CAPABILITIES` "have no effect behind an
   `ANTHROPIC_BASE_URL` gateway". Only `_NAME` and `_DESCRIPTION` cross over. The row can be
   labelled, not described as capable.
3. **`availableModels`**, if it is ever set, must include the custom ID or the row is filtered out and
   `--model` on it is rejected. Not the situation on this machine today.
4. **It does nothing for subagents** — frontmatter resolves independently of the picker.

### Gateway model discovery, and the prefix filter

`CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1` (Claude Code v2.1.129 or later) makes Claude Code
query the gateway's `/v1/models` at startup and add what it finds to the picker, each row labelled
"From gateway". It is off by default. This is the mechanism that would satisfy requirement 1
properly, and it is the one `docs/implementation-plan.md` currently defers.

The constraint that shapes the design, quoted verbatim from the source:

> Claude Code reads `id` and the optional `display_name` from each entry in the response's `data`
> array, and ignores entries whose `id` doesn't begin with `claude` or `anthropic`

Verified 2026-07-30 against both the raw markdown (`llm-gateway-protocol.md` line 166) and the
rendered HTML of the same page, after a first reading through a summarising fetch — the summariser's
wording turned out to be exact, but it was worth checking, and the same care is worth taking with
everything else quoted here.

The documentation acknowledges the limitation in the same section and points at the previous
mechanism as the workaround: "If your gateway serves Claude models under aliases that don't match the
discovery filter, developers can add those aliases manually with the model configuration variables."

Other requirements from that section, all of which constrain a future `/v1/models`:

- The request is `GET /v1/models?limit=1000` with a **3-second timeout**. A slow answer fails
  discovery **silently**.
- **Any redirect is treated as failure**, even `http` to `https`, so the endpoint must be served
  directly at the configured base URL.
- Discovery sends **exactly one** credential header — `ANTHROPIC_AUTH_TOKEN` as a bearer token when
  set, otherwise the resolved API key as `x-api-key`. Inference requests send both. So this endpoint's
  auth path differs from `/v1/messages`, which is directly relevant to the `credential:` design
  decision that is agreed and not yet implemented.
- Results cache to `~/.claude/cache/gateway-models.json` and refresh each startup; a failed probe
  falls back to the previous list rather than emptying the picker.

## The one architectural question, stated but not answered

An earlier reading of this called the prefix filter a direct conflict with the routing rule. **That
was an overstatement and is corrected here.** The filter admits IDs beginning with `claude` *or*
`anthropic`; the routing rule keys on `claude-` specifically (`routing.py:20`). An advertised ID such
as `anthropic/google/gemma-4-e4b` therefore passes the filter *and* still routes to LM Studio under
the existing rule. The routing rule needs no change.

What remains is narrower: LM Studio needs **its own** ID in the request body, so anything advertised
under an `anthropic…` alias must be mapped back before forwarding. That is a body rewrite, and body
rewriting is the one thing the project has deliberately ruled out — the whole reason for byte relay is
that prompt caching matches on exact prefix bytes (`CLAUDE.md`, "Design decisions"; the captured
request carries `cache_control` on the system blocks).

Worth noting that the `model` field is small, sits in the body, and is *already* peeked at for
routing — so a rewrite of that one field is not obviously as damaging as reserialising the body. It is
still a change of kind rather than degree, and it deserves a decision of its own rather than being
slipped in. Options exist that avoid it entirely (advertising only Claude models through discovery and
handling local ones with the custom-option variable, for instance). **No option is chosen here.**

## Two CSV columns — the one part of this that *is* decided

**Accepted into the spec on 2026-07-30**, while the rest of this document stays deferred. `CLAUDE.md`
now carries `session_id` and `agent_id` in the CSV column table, `docs/implementation-plan.md` carries
them in the Phase 2 work list, and `stats.py`'s docstring records where they come from. They were
accepted on the cheapness argument below, not because anything else here was settled.

Claude Code's gateway contract documents three headers on inference requests:

| Header | Meaning |
|---|---|
| `x-claude-code-session-id` | identifies the session; aggregates its requests without parsing bodies |
| `x-claude-code-agent-id` | present **only** on requests from a subagent Claude Code spawned |
| `x-claude-code-parent-agent-id` | present only for nested agents |

The session header is not merely documented: it is in this repository's own captured request, which
is why `docs/handoff.md` records redacting an `X-Claude-Code-Session-Id`. The agent header is documented
only — the capture predates any subagent use here.

If requirement 2 matters, the agent header is the *only* way the CSV can attribute a call to a
subagent rather than the main loop, and without it a mixed-model session collapses into an
indistinguishable pile of rows. The documentation makes the same point from the operator's side: use
it "with the session ID to attribute cost to parallel agents". It also warns that the ID "identifies
an agent, not a person or a device", so it must not be treated as a user identifier.

One related opportunity, and one related trap, both touching the existing decision that background
traffic gets no special case: `ANTHROPIC_DEFAULT_HAIKU_MODEL` is what background functionality uses,
so pointing it at a local model would keep background calls on this machine — and leaving it alone
means they keep costing money even when the main model is local, exactly as `routing.py`'s docstring
already warns.

## Documented versus measured

The distinction this repository has been careful about, applied here. **Everything in the right-hand
column is unverified against this router.**

| Claim | Status |
|---|---|
| Per-request dispatch routes a mixed-model session correctly | **Measured** in the design sense — Phase 1 ran both backends through the same rule — but never with two models *inside one session* |
| `x-claude-code-session-id` arrives on real requests | **Measured** — present in `docs/log-the-whole-request.txt` |
| `/model <local-id>` is accepted behind a custom base URL | Documented only |
| Subagent frontmatter accepts a full local model ID and routes there | Documented only |
| `ANTHROPIC_CUSTOM_MODEL_OPTION` produces a working picker row | Documented only |
| The `claude`/`anthropic` discovery filter, and its request constraints | Documented, quoted verbatim from source, cross-checked in two renderings |
| `x-claude-code-agent-id` arrives on subagent requests | Documented only |
| A local model can usefully *serve* a subagent's workload | **Unknown, and this is Phase 4's question** |

The last row is the reason for deferring. A picker full of local models is worth nothing if a local
model cannot hold a real session, and Phase 4 is what settles that. `google/gemma-4-e4b` did carry
tools and multi-turn on 2026-07-29, at 34304 tokens of context against a ~30k fixed preamble — which
is either evidence that the estimate is pessimistic or evidence of silent trimming, and that too is a
Phase 4 question.

The cheapest possible next step, whenever this is picked up, is roughly ten minutes of measurement
rather than any code: start the router, type `/model google/gemma-4-e4b` in a live session, then add
a subagent with a local `model:` in its frontmatter and watch which backend each call lands on. That
converts five of the rows above from documented to measured, and it can be done before deciding
anything.

## Open questions for after Phase 4

1. Are requirement 1 and requirement 2 in scope for the first release at all, or is `--model` at
   launch enough for it?
2. Does the router rewrite the `model` field to support an advertised alias, or is a rewrite ruled
   out and discovery limited to what can be advertised honestly?
3. If `/v1/models` is built: does it merge Anthropic's list with LM Studio's, or serve local models
   only? Anthropic publishes no `/v1/models` under the Anthropic-compat namespace that LM Studio
   exposes, and LM Studio's own list lives at its native `GET /api/v1/models`.
4. Does `/v1/models` authenticate, given that discovery sends one credential header where inference
   sends two? This should be answered together with the `credential:` shape, not after it.
5. ~~Do the CSV gain `session_id` and `agent_id` columns, and does that happen in Phase 2 or
   later?~~ **Settled 2026-07-30: yes, both, in Phase 2.** The remaining piece is measurement rather
   than decision — confirm `x-claude-code-agent-id` actually arrives, since only the session header
   has been observed here.

## Sources

Claude Code documentation, all read 2026-07-30 against Claude Code **2.1.212** as installed on this
machine:

- Gateway protocol, model discovery and the request headers —
  <https://code.claude.com/docs/en/llm-gateway-protocol#model-discovery>. Appending `.md` to that
  URL serves the raw markdown, which is the form the quotations above were checked against.
- Model configuration, `/model` precedence, the validation exemption behind a custom base URL, and
  the custom model option — <https://code.claude.com/docs/en/model-config>
- Subagents, the `model` frontmatter field and its resolution order —
  <https://code.claude.com/docs/en/sub-agents>

Local evidence: `routing.py:20-25` for the prefix rule, `docs/log-the-whole-request.txt` for the
session header, `docs/testing-against-claude-code.md` for the Phase 1 session, and `CLAUDE.md`
"Design decisions" for byte relay and prompt caching.
