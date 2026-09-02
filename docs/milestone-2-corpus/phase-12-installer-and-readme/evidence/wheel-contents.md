# What is inside the wheel

**Built 2026-09-02 from `feat/phase-12-installer-and-readme`**, with `uv build --wheel`, at the
bumped pin `uv_build>=0.11.32,<0.13.0`.

**Why this is frozen and the prose is not enough.** Phase 12's central packaging claim is that
`init` works on a machine with no checkout, which requires the two templates to be *inside the
wheel* rather than read from the source tree. That cannot be re-checked from a sentence saying it is
true, and the machine that would refute it — one without this repository — does not exist here.
**This listing is the nearest available proof**, and it is re-derivable: build a wheel and read its
archive.

**The two rows that matter are the templates.** Neither is a `.py` file, and there is **no
`[tool.uv.build-backend]` section in `pyproject.toml` and no `MANIFEST.in`** — so uv_build including
them is a default this project depends on rather than a setting it chose.

`ilirium_llm_router-0.1.0-py3-none-any.whl` — 23 entries.

| Entry | Bytes | sha256 (first 12) |
|---|---|---|
| `ilirium_llm_router-0.1.0.dist-info/` | 0 | `e3b0c44298fc` |
| `ilirium_llm_router-0.1.0.dist-info/METADATA` | 7112 | `ac16be729209` |
| `ilirium_llm_router-0.1.0.dist-info/RECORD` | 1822 | `9bceaaaf81c4` |
| `ilirium_llm_router-0.1.0.dist-info/WHEEL` | 80 | `cba7be6b9288` |
| `ilirium_llm_router-0.1.0.dist-info/entry_points.txt` | 68 | `f40384219051` |
| `ilirium_llm_router/` | 0 | `e3b0c44298fc` |
| `ilirium_llm_router/__init__.py` | 593 | `0b3d7e102648` |
| `ilirium_llm_router/__main__.py` | 165 | `3f7b3b3a7ea5` |
| `ilirium_llm_router/app.py` | 7546 | `9ad33fc42b0d` |
| `ilirium_llm_router/cli.py` | 30896 | `f83bebaac381` |
| `ilirium_llm_router/config-template.yaml` **←** | 4106 | `ed8cdec60d8b` |
| `ilirium_llm_router/config.py` | 13090 | `dde9fb1fbb7e` |
| `ilirium_llm_router/corpus.py` | 46976 | `1d34523b3019` |
| `ilirium_llm_router/dictionary.py` | 51404 | `c5c22d01cc9c` |
| `ilirium_llm_router/env-template` **←** | 504 | `d0d59c3003da` |
| `ilirium_llm_router/extract.py` | 13735 | `1b152183fd92` |
| `ilirium_llm_router/jsonl.py` | 9063 | `766619e19615` |
| `ilirium_llm_router/logging_setup.py` | 5423 | `d432dc06c4e3` |
| `ilirium_llm_router/observe.py` | 20327 | `6ac937fc669e` |
| `ilirium_llm_router/proxy.py` | 22752 | `31f6b75ddffc` |
| `ilirium_llm_router/routing.py` | 1097 | `2c14e1212ea7` |
| `ilirium_llm_router/stats.py` | 8430 | `320ea93b30e6` |
| `ilirium_llm_router/transcript.py` | 29160 | `3572af636e83` |

*The `uv_build` pin bump to `<0.13.0` was accepted on this same comparison — a wheel built either
side of it, every entry hashed and diffed, identical byte for byte. **That comparison covered 22
entries and this listing has 23**: `env-template` was added afterwards, when the owner asked for
`init` to write `.env.example` too.*
