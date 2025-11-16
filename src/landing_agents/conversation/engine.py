"""Lightweight conversation engine scaffold."""

from __future__ import annotations

from typing import Dict, Optional

from .agents import (
    AgentError,
    AgentRegistry,
    AgentResult,
    Director,
    SpecialistAgent,
    TurnContext,
)
from .state import ConversationPhase, ConversationState


class PhaseDrivenDirector:
    """Default director that selects agents based on the active phase."""

    def __init__(self, registry: AgentRegistry) -> None:
        self._registry = registry

    async def select_agent(self, state: ConversationState, *, hint: Optional[str] = None) -> str:
        if hint:
            try:
                self._registry.get(hint)
                return hint
            except AgentError:
                pass

        candidates = self._registry.eligible_for_phase(state.phase)
        if not candidates:
            raise AgentError(f"No agents registered for phase {state.phase}")
        return candidates[0].name


class ConversationEngine:
    """Coordinates specialist agents to handle user turns."""

    def __init__(self, director: Optional[Director] = None) -> None:
        self.registry = AgentRegistry()
        self.director = director or PhaseDrivenDirector(self.registry)

    def register_agent(self, agent: SpecialistAgent) -> None:
        """Register a specialist agent with the engine."""

        self.registry.register(agent)

    async def handle_turn(
        self,
        user_message: str,
        state: ConversationState,
        *,
        metadata: Optional[Dict[str, str]] = None,
        hint: Optional[str] = None,
    ) -> AgentResult:
        """Run the appropriate agent for the current turn and update state."""

        agent_name = await self.director.select_agent(state, hint=hint)
        agent = self.registry.get(agent_name)
        turn = TurnContext(state=state, user_message=user_message, metadata=metadata or {})
        result = await agent.run(turn)
        self._apply_result(state, result)
        return result

    @staticmethod
    def _apply_result(state: ConversationState, result: AgentResult) -> None:
        state.update_phase(result.phase)
        state.update_active_thread(result.active_thread)
        if result.lead_profile_updates:
            state.merge_lead_profile(result.lead_profile_updates)
        if result.context_ids:
            state.append_context_ids(result.context_ids)


async def bootstrap_engine(engine: ConversationEngine) -> None:
    """Helper hook to register placeholder agents for development."""

    class EchoAgent(SpecialistAgent):
        async def run(self, turn: TurnContext) -> AgentResult:
            return AgentResult(messages=[f"Echo: {turn.user_message}"], phase=turn.state.phase)

    for phase in ConversationPhase:
        engine.register_agent(EchoAgent(name=f"echo_{phase.value.lower()}", supported_phases=[phase]))

