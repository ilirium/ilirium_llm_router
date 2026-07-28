# Shortcuts for the common jobs. Run `make` on its own to list them.
#
# Overridable, e.g. `make run CONFIG=other.yaml` or `make test ARGS=-x`:
CONFIG ?= config.yaml
ARGS   ?=

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
	uvx ruff check src tests

format: ## Reformat the code in place
	uvx ruff format src tests

clean: ## Remove caches and build artefacts, leaving logs/ alone
	rm -rf .pytest_cache .ruff_cache build dist *.egg-info
	find src tests -type d -name __pycache__ -prune -exec rm -rf {} +
