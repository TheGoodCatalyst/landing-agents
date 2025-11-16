"""Messaging MCP server placeholder implementation."""

from __future__ import annotations

from typing import Any, Dict

from .server_base import create_app, define_tool, serve

app = create_app("messaging-server", "Outbound messaging tooling for Landing Agents.")


async def send_email(template_id: str, vars: Dict[str, Any]) -> Dict[str, Any]:
    """Simulate sending an email using the specified template."""

    return {
        "status": "queued",
        "channel": "email",
        "template_id": template_id,
        "variables": vars,
    }


define_tool(
    app,
    "messaging.send_email",
    send_email,
    description="Send an email using a templated provider integration.",
)


async def send_whatsapp(template_id: str, vars: Dict[str, Any]) -> Dict[str, Any]:
    """Simulate sending a WhatsApp message."""

    return {
        "status": "queued",
        "channel": "whatsapp",
        "template_id": template_id,
        "variables": vars,
    }


define_tool(
    app,
    "messaging.send_whatsapp",
    send_whatsapp,
    description="Send a WhatsApp message using a pre-approved template.",
)


if __name__ == "__main__":  # pragma: no cover
    serve(app)

