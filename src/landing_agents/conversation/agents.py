"""Agent definitions and registry for the conversation engine."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Protocol

from pydantic import BaseModel, Field

from .state import ConversationPhase, ConversationState


class AgentError(RuntimeError):
    """Raised when an agent cannot handle a turn."""


class AgentResult(BaseModel):
    """Structured response returned by specialist agents."""

    messages: List[str] = Field(default_factory=list)
    phase: Optional[ConversationPhase] = None
    next_agent: Optional[str] = None
    active_thread: Optional[str] = None
    lead_profile_updates: Dict[str, Optional[str | float]] = Field(default_factory=dict)
    context_ids: List[str] = Field(default_factory=list)


@dataclass
class TurnContext:
    """Context supplied to agents for each user turn."""

    state: ConversationState
    user_message: str
    metadata: Dict[str, str] = field(default_factory=dict)


class SpecialistAgent(ABC):
    """Base class for all specialist agents."""

    name: str
    supported_phases: Iterable[ConversationPhase]

    def __init__(self, name: str, supported_phases: Iterable[ConversationPhase]):
        self.name = name
        self.supported_phases = tuple(supported_phases)

    def supports_phase(self, phase: ConversationPhase) -> bool:
        return phase in self.supported_phases

    @abstractmethod
    async def run(self, turn: TurnContext) -> AgentResult:
        """Execute the agent against the provided turn context."""


class Director(Protocol):
    """Protocol for director/orchestrator implementations."""

    async def select_agent(self, state: ConversationState, *, hint: Optional[str] = None) -> str:
        """Return the name of the next agent to execute."""


class AgentRegistry:
    """Registry storing agent implementations by name."""

    def __init__(self) -> None:
        self._agents: Dict[str, SpecialistAgent] = {}

    def register(self, agent: SpecialistAgent) -> None:
        if agent.name in self._agents:
            raise ValueError(f"Agent '{agent.name}' is already registered")
        self._agents[agent.name] = agent

    def get(self, name: str) -> SpecialistAgent:
        try:
            return self._agents[name]
        except KeyError as exc:
            raise AgentError(f"Unknown agent '{name}'") from exc

    def eligible_for_phase(self, phase: ConversationPhase) -> List[SpecialistAgent]:
        return [agent for agent in self._agents.values() if agent.supports_phase(phase)]

    def all_agents(self) -> List[SpecialistAgent]:
        return list(self._agents.values())

