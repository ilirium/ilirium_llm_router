# ilirium_llm_router

Repo: https://github.com/ilirium/ilirium_llm_router
Git: git@github.com:ilirium/ilirium_llm_router.git

## Description

Goal of the project.

I want to be able to connect Claude Code to all Anthropic models (Haiku, Sonnet, Opus, Fable) and to locally served models.

I am going to use LM Studio to serve models. I want to be able to pick up different models in LM Studio to work on.

Claude Code should have access to all its own models and to locally served models simultaneously.

In the future:
- I plan to expand to other commercial harnesses: OpenAI Codex, Google Antigravity, GitHub Copilot, JetBrains Junie.  
- Also, I plan to expand to open-source harnesses: Pi, Hermes, OpenCode, OpenClaw, etc.
- To be able to use cloud-served models through APIs: OpenAI, Google Gemini, OpenRouter, and so on.

Features:
- Simple configuration at first.
- Simple and human-readable code.

Implementation details:
- Language: Python.
- Web framework: FastAPI.
- YAML as config.
- `.env` to store API keys.
- Using type hints.
- Using Pydantic for data validation (requests, responses, messages, etc).
