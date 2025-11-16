"""Conversation state models for the Landing Agents platform."""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ConversationPhase(str, Enum):
    """High-level phase of the conversation lifecycle."""

    GREET = "GREET"
    DISCOVER = "DISCOVER"
    QUALIFY = "QUALIFY"
    RECOMMEND = "RECOMMEND"
    OBJECTION = "OBJECTION"
    CTA = "CTA"
    HANDOFF = "HANDOFF"
    FOLLOW_UP = "FOLLOW_UP"


class ThreadState(BaseModel):
    """State for a topic-specific conversation thread."""

    last_doc_ids: List[str] = Field(default_factory=list)
    last_cta: Optional[str] = None
    summary: Optional[str] = None


class LeadProfile(BaseModel):
    """Captured or inferred lead attributes."""

    name: Optional[str] = None
    company: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    industry: Optional[str] = None
    budget_band: Optional[str] = None
    authority: Optional[str] = None
    need: Optional[str] = None
    timeline: Optional[str] = None
    score: Optional[float] = None


class ConversationState(BaseModel):
    """Full state snapshot shared across agents."""

    session_id: str
    tenant_id: str
    visitor_id: Optional[str] = None
    user_id: Optional[str] = None
    phase: ConversationPhase = ConversationPhase.GREET
    active_thread: Optional[str] = None
    threads: Dict[str, ThreadState] = Field(default_factory=dict)
    lead_profile: LeadProfile = Field(default_factory=LeadProfile)
    experiment_variant: Dict[str, str] = Field(default_factory=dict)
    context_ids: List[str] = Field(default_factory=list)

    def get_thread(self, thread_id: str) -> ThreadState:
        """Return the thread state, initialising it when required."""

        if thread_id not in self.threads:
            self.threads[thread_id] = ThreadState()
        return self.threads[thread_id]

    def update_phase(self, phase: Optional[ConversationPhase]) -> None:
        """Update the conversation phase if a new value is provided."""

        if phase is not None:
            self.phase = phase

    def update_active_thread(self, thread_id: Optional[str]) -> None:
        """Set the active thread identifier."""

        if thread_id is not None:
            self.active_thread = thread_id

    def merge_lead_profile(self, updates: Dict[str, Optional[str | float]]) -> None:
        """Merge partial lead profile information into the stored profile."""

        for key, value in updates.items():
            if value is None:
                continue
            if hasattr(self.lead_profile, key):
                setattr(self.lead_profile, key, value)

    def append_context_ids(self, context_ids: List[str]) -> None:
        """Attach additional context identifiers to the session."""

        if not context_ids:
            return
        existing = set(self.context_ids)
        for context_id in context_ids:
            if context_id not in existing:
                self.context_ids.append(context_id)
                existing.add(context_id)

