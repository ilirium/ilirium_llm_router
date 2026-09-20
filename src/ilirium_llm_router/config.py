"""Configuration loading and validation.

The config file is validated once at startup. Anything wrong with it stops the program with a
readable message, rather than surfacing as a confusing failure on the first request.

Relative paths in the config are resolved against the directory holding the config file, so the
router behaves the same whichever directory it is started from.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

import yaml
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)


class ConfigError(Exception):
    """Raised when the configuration cannot be loaded or is invalid.

    Carries a message already written for a human reading a terminal.
    """


class Strict(BaseModel):
    """Base for config models: unknown keys are an error, not silently ignored.

    A typo in a YAML key would otherwise leave the default silently in place, which is exactly the
    kind of failure this file exists to prevent.
    """

    model_config = ConfigDict(extra="forbid")


class Backend(Strict):
    """One place requests can be sent.

    `credential` says what happens to the credential arriving from the caller, and it is the *only*
    thing consulted when the request goes out — `forward` passes it through, `strip` removes it, and
    `inject` removes it and sends the key named by `api_key_env` instead.

    The two used to be independent, and a configured key silently won over whatever `credential`
    said, so `credential: forward` beside a key read as "forward the caller's token" and did not do
    that. The validator below makes that state unrepresentable rather than merely discouraged.
    """

    base_url: str
    credential: Literal["forward", "strip", "inject"]
    api_key_env: str | None = None
    read_timeout: float = Field(default=600.0, gt=0)
    """How long this backend may stay silent before the call is abandoned, in seconds.

    Measured on 2026-08-07 (`docs/milestone-1-core/phase-5-config-and-timeouts/evidence/`): this is
    the longest gap permitted *between* two reads, not a budget for the whole reply — every chunk
    restarts it. So it bounds silence, never duration.

    It is per backend because the two differ by 26× in time to first byte — measured over successful
    streamed `/v1/messages` calls, which is the slice that gap describes — and because the only thing
    that has ever hit the old shared 600 s was a local model prefilling a large prompt, which is
    silence that means the backend is working rather than wedged.
    """

    @field_validator("base_url")
    @classmethod
    def _clean_base_url(cls, value: str) -> str:
        value = value.strip()
        if not value.startswith(("http://", "https://")):
            raise ValueError("must start with http:// or https://")
        return value.rstrip("/")

    @model_validator(mode="after")
    def _mode_and_key_agree(self) -> Backend:
        """Refuse the two ways of asking for a key and a mode that contradict each other.

        Both are the failures that otherwise surface as a confusing 401 a long way from their
        cause: a backend that authenticates with nothing, and a key that looks configured and is
        never sent.
        """
        if self.credential == "inject" and not self.api_key_env:
            raise ValueError(
                "'credential: inject' needs 'api_key_env' naming the environment variable that "
                "holds the key. Add it, or use 'forward' or 'strip' if this backend needs no key "
                "of its own."
            )
        if self.credential != "inject" and self.api_key_env:
            raise ValueError(
                f"'api_key_env' is set but credential is '{self.credential}', so that key would "
                f"never be sent. Use 'credential: inject' to send it, or remove 'api_key_env'."
            )
        return self


class Backends(Strict):
    """The two backends, named explicitly because the routing rule names them explicitly."""

    anthropic: Backend
    lmstudio: Backend


class Server(Strict):
    host: str = "127.0.0.1"
    port: int = Field(default=8787, ge=1, le=65535)


class Logging(Strict):
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    file: Path = Path("logs/telemetry/router.log")
    max_bytes: int = Field(default=10_485_760, gt=0)
    backup_count: int = Field(default=5, ge=0)


class Stats(Strict):
    file: Path = Path("logs/telemetry/calls.csv")
    max_bytes: int = Field(default=5_242_880, gt=0)
    backup_count: int = Field(default=10, ge=0)


class Retrain(Strict):
    """When and how the router retrains its own dictionary.

    **Everything here runs offline, in its own thread, and never in the path of a call.** That is
    what the nesting says, and it is why these four are grouped rather than sitting flat beside the
    write-path keys — a reader tuning a live call never has to look in here.

    All four take a CLI flag on the trainer, and the flag wins for that one run: the config is what
    automatic retraining uses, the flags are for experiments, which are run by hand.
    """

    window_days: int = Field(default=1, ge=0)
    """Complete days of material to train from, as a **minimum** rather than a fixed count — the
    window widens until it holds two sessions, because one harness on one laptop produces
    single-session days as the ordinary case.

    **`0` disables automatic retraining** and is the one "off" value in the block; the router keeps
    using the newest dictionary already installed. A separate `enabled` boolean would be redundant
    beside it.
    """

    sample_min_bytes: int = Field(default=1024, ge=1)
    """A body smaller than this is not a training sample.

    **No path filter beside it, and that costs nothing**: measured 2026-08-19, every request body at
    or above this size in the whole corpus is already `/v1/messages`, the only other path having
    0-byte request bodies. A path filter would also have excluded `count_tokens` requests, which
    carry the same preamble and are ideal material.
    """

    maxdict: int = Field(default=262_144, gt=0)
    """The dictionary size cap. **Provisional, not measured-optimal** — the corpus has no usable
    validation split, so this was chosen with knowledge of the slice it was scored on. Training is
    **non-monotonic** in this parameter on both trainers, so a bigger cap is not a better
    dictionary."""

    k: int = Field(default=8000, gt=0)
    """COVER's segment size. **Provisional**, and the one parameter that must never be left to the
    library's own optimiser: at this sample count that is up to 15% *worse* than `zstd --train`'s
    default, while this value is 13% *better*. The tool is not the variable — `k` is."""


class Corpus(Strict):
    """The body store. Opt-in, and nothing under `dir` is created until `enabled` is true.

    Off by default because `calls.csv` is always on for reasons that do not transfer: it is cheap
    and holds nothing sensitive, and **neither is true here** — bodies hold source code, file
    contents and anything typed.
    """

    enabled: bool = False
    dir: Path = Path("logs/corpus")
    compress_level_zstd: int = Field(default=9, ge=1, le=22)
    """The level the write path stores at — **and the level the trainer scores a candidate
    dictionary against the incumbent at**, so the comparison cannot drift from what is actually
    stored. It does **not** set the level a dictionary is *trained* at; that is `TRAIN_LEVEL`,
    measured to move the ratio by 0.03%.

    Bounds are hardcoded rather than read from libzstd: 1–19 are the ordinary levels and 20–22 the
    ultra ones, so a number outside that is a typo rather than a preference. This is a sanity check,
    not a contract with the library.

    Named `compress_level_zstd` rather than `level` because `logging.level` two blocks away is a
    severity, and a key read in isolation should say what it sets and whose scale it is on.
    """

    body_max_bytes: int = Field(default=1_048_576, gt=0)
    """One body larger than this is not stored, and the ref cell reads `too_large`. **Bounds peak
    memory for one body**, checked on every chunk while the call runs.

    **Not disableable.** An "unlimited" setting reads as *capture everything* and means *let an
    unknown endpoint decide how much memory this process uses* — and the catch-all route forwards
    any path, so the reply to an unanticipated endpoint could be any size at all.
    """

    queue_max_bytes: int = Field(default=67_108_864, gt=0)
    """Total bytes waiting to be written; over it, the body is dropped and the row says so.
    **Bounds memory for all waiting bodies**, checked once at submit.

    **The two limits cannot cover for each other**, which is why both exist: by the time submit runs
    the memory for one huge body has already been spent, and a thousand ordinary 100 KB bodies are
    each far under the ceiling and together are 100 MB in the queue. Also not disableable.
    """

    retrain: Retrain = Field(default_factory=Retrain)


class Experiments(Strict):
    """Phase 14's three live experiments, **every one off by default**.

    They exist because `BUG-001` needed the router varied one flip at a time, and each came back
    **negative** for the 429. The owner chose on 2026-09-18 to keep them running; on 2026-09-19 that
    reversed, because a run with the client fully first-party showed the classifier still failing
    after the 429 was gone — and a router that relays *plus three modifications* cannot be the
    control that result has to be read against.

    ***Switches rather than deletions, at the owner's choice***, so a flip is one config line rather
    than git archaeology. **The default is the honest relay**; turning one on is a deliberate act and
    the config file records which experiment is running.

    *This section is the first configurable thing in the phase and reverses the plan's "the minimal
    form is deliberately not configurable" — the register says so, and why.*
    """

    relay_accept_encoding: bool = False
    """Relay the caller's `accept-encoding` on a **non-streamed** request instead of forcing
    `identity`.

    ***The standing cost is why this one matters most.*** With it on, a non-streamed reply arrives
    **compressed**, so the corpus stores brotli rather than JSON and `extract` hands a reader bytes.
    **It is also the prime suspect** for the classifier failing after the 429 went away: it is the
    only change that alters what a non-streamed reply looks like to the client, and the classifier
    is always non-streamed.

    *Streamed requests are unaffected either way — the SSE scanner reads raw bytes and has always
    required `identity`.*
    """

    http2_upstream: bool = False
    """Offer HTTP/2 to the backend over ALPN.

    **Negotiates rather than demands**, so a backend that declines gets HTTP/1.1 and LM Studio is
    unaffected. *It buys nothing measured and is eliminated twice over: the nine classifier calls
    Anthropic answered correctly on 2026-09-19 went over HTTP/1.1 on both legs.*

    **Inbound is HTTP/1.1 whatever this says** — uvicorn's implementations are `h11` and
    `httptools`, neither of which speaks h2. → `BKL-0039`.
    """

    imitate_attribution_headers: bool = False
    """Add fabricated attribution headers to every Anthropic call.

    ***Built on a misreading and now known to be wrong three ways over.*** The client's
    `x-anthropic-billing-header` is a **system-prompt block in the request body, not an HTTP
    header**, so this tests a channel the client never uses; and the values it invents — `0a3`,
    `sdk-cli` — disagree with the real ones, `2.1.267.608` and `cli`.

    ***Worst with a first-party client***, which sends its own genuine attribution in the body: the
    request then carries both, and they contradict each other. **Kept switchable rather than deleted
    only so the negative result stays reproducible.**
    """

    add_claude_code_hidden_attribution_block: bool = False
    """Put back the attribution block Claude Code withholds when `ANTHROPIC_BASE_URL` is set.

    ***This is the only one of these that is meant to WORK rather than to be eliminated.*** The
    other three are experiments whose negative results are their value; this one is a candidate fix
    for `BUG-001`, and if it succeeds it leaves `experiments` and becomes the Anthropic backend's own
    setting.

    **It is the one deliberate exception to byte-relay in this router.** *A request it applies to is
    parsed, given one more element in its `system` array, and re-serialised* — so the bytes the
    backend receives are not the bytes that arrived, and **the prompt-cache prefix for that request
    changes**. Four conditions keep that as narrow as it can be:

    - the **Anthropic** backend, since the block means nothing to LM Studio
    - **non-streamed** only — *streamed requests were never refused (0 of 16, 0 of 230, 0 of 145 on
      the measured days), they are the large ones, and they are where prompt caching earns its keep*
    - an **uncompressed** body, because rewriting a compressed one means re-compressing it and a
      wrong guess about a format is indistinguishable from a corrupt body
    - a body that **does not already carry a block** — a first-party client sends its own

    ***What goes in it is two hardcoded fields and three deliberate omissions***, all measured; the
    reasoning lives in `backend_anthropic.py` next to the constants, where a reader meets it before
    the code that uses them.

    **`check` names it like the others**, and a startup that says nothing about it is a router
    relaying bytes unchanged.
    """


class Config(Strict):
    backends: Backends
    server: Server = Field(default_factory=Server)
    logging: Logging = Field(default_factory=Logging)
    stats: Stats = Field(default_factory=Stats)
    corpus: Corpus = Field(default_factory=Corpus)
    experiments: Experiments = Field(default_factory=Experiments)

    def resolve_paths(self, base_dir: Path) -> None:
        """Make log, stats and corpus paths absolute, against the config file's directory."""
        self.logging.file = _resolve(self.logging.file, base_dir)
        self.stats.file = _resolve(self.stats.file, base_dir)
        self.corpus.dir = _resolve(self.corpus.dir, base_dir)

    def api_keys(self) -> dict[str, str]:
        """Read the API key for every backend that asks for one.

        Returns a mapping of backend name to key. Backends that forward or strip the incoming
        credential do not appear.

        Keyed on the mode, so this and the request path decide from the same thing. The second
        clause narrows the type; the model validator already guarantees it.
        """
        keys: dict[str, str] = {}
        for name, backend in _named_backends(self.backends):
            if backend.credential == "inject" and backend.api_key_env:
                keys[name] = os.environ[backend.api_key_env]
        return keys


def _resolve(path: Path, base_dir: Path) -> Path:
    return path if path.is_absolute() else (base_dir / path)


def _named_backends(backends: Backends) -> list[tuple[str, Backend]]:
    return [("anthropic", backends.anthropic), ("lmstudio", backends.lmstudio)]


def load_config(path: Path) -> Config:
    """Read, validate and return the configuration, or raise ConfigError with a readable message."""
    raw = _read_yaml(path)
    try:
        config = Config.model_validate(raw)
    except ValidationError as exc:
        raise ConfigError(_describe(exc, path)) from exc

    config.resolve_paths(path.parent.resolve())
    _check_api_keys(config)
    return config


def _read_yaml(path: Path) -> dict[str, object]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise ConfigError(f"Config file not found: {path}") from None
    except OSError as exc:
        raise ConfigError(f"Could not read config file {path}: {exc}") from exc

    try:
        loaded = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ConfigError(f"Config file {path} is not valid YAML:\n{exc}") from exc

    if loaded is None:
        raise ConfigError(f"Config file {path} is empty.")
    if not isinstance(loaded, dict):
        raise ConfigError(f"Config file {path} must contain a mapping at the top level.")
    return loaded


def _check_api_keys(config: Config) -> None:
    """Fail now if a backend names an environment variable that is missing or empty.

    Waiting until the first request would turn a configuration mistake into a runtime one.
    """
    for name, backend in _named_backends(config.backends):
        if backend.credential != "inject":
            continue
        variable = backend.api_key_env
        if variable and not os.environ.get(variable, "").strip():
            raise ConfigError(
                f"Backend '{name}' has 'credential: inject' and expects its API key in the "
                f"environment variable '{variable}', which is unset or empty.\n"
                f"Set it in your .env file, or switch that backend to 'credential: forward' or "
                f"'credential: strip' if it needs no key of its own."
            )


def _describe(exc: ValidationError, path: Path) -> str:
    """Turn pydantic's error report into something readable in a terminal."""
    lines = [f"Config file {path} is invalid:"]
    for error in exc.errors():
        location = ".".join(str(part) for part in error["loc"]) or "(top level)"
        lines.append(f"  {location}: {error['msg']}")
    return "\n".join(lines)
