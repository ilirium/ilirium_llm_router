"""A router that lets one coding harness reach several model backends at once."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

# Read from the installed metadata rather than written out here, so `pyproject.toml` is the single
# place the version lives. It is stamped onto every CSV row, and a second copy that can drift would
# eventually record a version that was never released.
try:
    __version__ = version("ilirium-llm-router")
except PackageNotFoundError:  # a source tree that was never installed
    __version__ = "0.0.0+unknown"
