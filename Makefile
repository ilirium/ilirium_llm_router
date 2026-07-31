# Shortcuts for the common jobs. Run `make` on its own to list them.
#
# Overridable, e.g. `make run CONFIG=other.yaml` or `make test ARGS=-x`:
CONFIG ?= config.yaml
ARGS   ?=

# ruff is fetched on demand rather than installed as a dependency, but it is pinned: an unpinned
# formatter reformats the whole repository the day it changes its mind, and a version bump then
# arrives disguised as someone's feature branch. This is the version that produced the current
# formatting. Bump it deliberately — `make format RUFF=ruff@x.y.z` tries a new one without
# committing to it, and the diff it produces is the reason to accept or reject the bump.
RUFF   ?= ruff@0.16.1

.DEFAULT_GOAL := help

.PHONY: help sync run check test lint format clean

help: ## List the available targets
	@grep -hE '^[a-z-]+:.*##' $(MAKEFILE_LIST) \
		| sed -e 's/:.*## / /' -e 's/^/  make /' \
		| awk '{ printf "%-14s %s\n", $$2, substr($$0, index($$0, $$3)) }'

sync: ## Install dependencies into the local environment
	uv sync

run: ## Start the router
	uv run ilirium-llm-router -c $(CONFIG)

check: ## Validate the config and print it, without starting the server
	uv run ilirium-llm-router -c $(CONFIG) --check

test: ## Run the tests (make test ARGS="tests/test_routing.py::test_..." for one)
	uv run pytest $(ARGS)

lint: ## Report style and correctness problems
	uvx $(RUFF) check src tests

format: ## Reformat the code in place
	uvx $(RUFF) format src tests

clean: ## Remove caches and build artefacts, leaving logs/ alone
	rm -rf .pytest_cache .ruff_cache build dist *.egg-info
	find src tests -type d -name __pycache__ -prune -exec rm -rf {} +
