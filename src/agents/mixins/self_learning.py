"""Mixin for agents to use self-learning."""

from typing import Optional


class SelfLearningMixin:
    """Mixin that adds self-learning capabilities to any agent."""

    def __init__(self, *args, self_learning_enabled: bool = True, **kwargs):
        super().__init__(*args, **kwargs)
        self.self_learning_enabled = self_learning_enabled
        self._self_learning = None

    def _init_self_learning(self, supabase_client):
        from src.agents.self_learning import SelfLearningAgent
        self._self_learning = SelfLearningAgent(supabase_client)

    async def _record_and_learn(
        self,
        action: str,
        outcome: str,
        context: dict,
        correction: Optional[str] = None
    ):
        if self.self_learning_enabled and self._self_learning:
            await self._self_learning.record_outcome(
                agent_role=self.__class__.__name__,
                action=action,
                outcome=outcome,
                context=context,
                correction=correction
            )
