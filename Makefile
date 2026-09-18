# Shortcuts for the common jobs. Run `make` on its own to list them.
#
# Overridable, e.g. `make run CONFIG=other.yaml` or `make test ARGS=-x`:
CONFIG ?= config.yaml
ARGS   ?=

# Phase 14 experiment only. Both of the next two come out when it does.
PORT   ?= 8799
EVID   := docs/milestone-2-corpus/phase-14-rate-limit-headers/evidence
FWD    := $(EVID)/boringssl-forwarder.py
PIN    := $(EVID)/run-pinned.py

# ruff is fetched on demand rather than installed as a dependency, but it is pinned: an unpinned
# formatter reformats the whole repository the day it changes its mind, and a version bump then
# arrives disguised as someone's feature branch. This is the version that produced the current
# formatting. Bump it deliberately — `make format RUFF=ruff@x.y.z` tries a new one without
# committing to it, and the diff it produces is the reason to accept or reject the bump.
RUFF   ?= ruff@0.16.1

.DEFAULT_GOAL := help

.PHONY: help sync run check test lint format clean forwarder run-boringssl run-hosts

help: ## List the available targets
	@grep -hE '^[a-z-]+:.*##' $(MAKEFILE_LIST) \
		| sed -e 's/:.*## / /' -e 's/^/  make /' \
		| awk '{ printf "%-14s %s\n", $$2, substr($$0, index($$0, $$3)) }'

sync: ## Install dependencies into the local environment
	uv sync

run: ## Start the router
	uv run ilirium-llm-router -c $(CONFIG)

forwarder: ## Phase 14 experiment: start the BoringSSL egress hop (PORT=8799)
	uv run --group experiment python $(FWD) $(PORT)

run-boringssl: ## Phase 14 experiment: start the router pointed at the forwarder above
	uv run ilirium-llm-router -c config-boringssl.yaml

# The address is resolved HERE rather than inside the router, because once the hosts entry exists a
# plain lookup answers 127.0.0.1 and the router would forward to itself. @1.1.1.1 ignores the file.
run-hosts: ## Phase 14 experiment: the router behind the hosts entry, api.anthropic.com pinned
	PINNED_ANTHROPIC_IP="$${PINNED_ANTHROPIC_IP:-$$(dig +short @1.1.1.1 api.anthropic.com | head -1)}" \
		uv run python $(PIN) -c config-hosts.yaml

check: ## Validate the config and print it, without starting the server
	uv run ilirium-llm-router -c $(CONFIG) check

test: ## Run the tests (make test ARGS="tests/test_routing.py::test_..." for one)
	uv run pytest $(ARGS)

lint: ## Report style and correctness problems
	uvx $(RUFF) check src tests

format: ## Reformat the code in place
	uvx $(RUFF) format src tests

clean: ## Remove caches and build artefacts, leaving logs/ alone
	rm -rf .pytest_cache .ruff_cache build dist *.egg-info
	find src tests -type d -name __pycache__ -prune -exec rm -rf {} +
