"""Shared helpers for FastMCP servers."""

from __future__ import annotations

from typing import Any, Callable, Dict

try:  # pragma: no cover - used for local development fallbacks
    from fastmcp import FastMCP
except ModuleNotFoundError:  # pragma: no cover
    class FastMCP:
        """Fallback placeholder when fastmcp is not installed."""

        def __init__(self, name: str, description: str | None = None) -> None:
            self.name = name
            self.description = description
            self._tools: Dict[str, Callable[..., Any]] = {}

        def tool(self, name: str | None = None, *, description: str | None = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
            def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
                tool_name = name or func.__name__
                self._tools[tool_name] = func
                return func

            return decorator

        def run(self) -> None:
            raise RuntimeError("fastmcp must be installed to run MCP servers.")


def create_app(name: str, description: str) -> FastMCP:
    """Create a FastMCP application with shared configuration."""

    return FastMCP(name=name, description=description)


def define_tool(
    app: FastMCP,
    name: str,
    handler: Callable[..., Any],
    *,
    description: str,
) -> None:
    """Register a tool handler with the provided FastMCP app."""

    decorated = app.tool(name, description=description)
    decorated(handler)


def serve(app: FastMCP) -> None:
    """Run the FastMCP application using its native runner."""

    app.run()

