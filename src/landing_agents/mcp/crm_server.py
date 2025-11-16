"""CRM MCP server placeholder implementation."""

from __future__ import annotations

from typing import Any, Dict, Optional

from .server_base import create_app, define_tool, serve

app = create_app("crm-server", "Lead management tooling for Landing Agents.")

_FAKE_LEADS: Dict[str, Dict[str, Any]] = {}


async def upsert_lead(profile: Dict[str, Any]) -> Dict[str, Any]:
    """Insert or update a lead profile in the placeholder data store."""

    email = profile.get("email")
    if not email:
        raise ValueError("Lead profile must include an email field")
    existing = _FAKE_LEADS.get(email, {})
    existing.update(profile)
    _FAKE_LEADS[email] = existing
    return existing


define_tool(
    app,
    "crm.upsert_lead",
    upsert_lead,
    description="Create or update a lead profile in the CRM.",
)


async def get_lead_by_email(email: str) -> Dict[str, Any]:
    """Retrieve a lead by email address."""

    return _FAKE_LEADS.get(email, {})


define_tool(
    app,
    "crm.get_lead_by_email",
    get_lead_by_email,
    description="Fetch a lead profile by email address.",
)


async def append_activity(lead_id: str, activity: Dict[str, Any]) -> Dict[str, Any]:
    """Append an activity entry for the specified lead."""

    record = _FAKE_LEADS.setdefault(lead_id, {"activities": []})
    record.setdefault("activities", []).append(activity)
    return {"status": "queued", "lead_id": lead_id, "activity": activity}


define_tool(
    app,
    "crm.append_activity",
    append_activity,
    description="Record an activity associated with a lead.",
)


if __name__ == "__main__":  # pragma: no cover
    serve(app)

