"""Experiment MCP server placeholder implementation."""

from __future__ import annotations

from typing import Any, Dict, Tuple

from .server_base import create_app, define_tool, serve

app = create_app("experiment-server", "Experimentation and feature flag tooling for Landing Agents.")

_VARIANTS: Dict[Tuple[str, str], str] = {}


async def get_variant(surface: str, user_hash: str) -> Dict[str, Any]:
    """Return a deterministic variant assignment for testing."""

    key = (surface, user_hash)
    variant = _VARIANTS.get(key)
    if variant is None:
        variant = "A"
        _VARIANTS[key] = variant
    return {"surface": surface, "user_hash": user_hash, "variant": variant}


define_tool(
    app,
    "experiment.get_variant",
    get_variant,
    description="Fetch the experiment variant for a user on a given surface.",
)


async def log_outcome(surface: str, variant: str, event: Dict[str, Any]) -> Dict[str, Any]:
    """Record an experiment outcome event."""

    return {"surface": surface, "variant": variant, "event": event, "status": "logged"}


define_tool(
    app,
    "experiment.log_outcome",
    log_outcome,
    description="Log an outcome for an experiment variant.",
)


if __name__ == "__main__":  # pragma: no cover
    serve(app)

