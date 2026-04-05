"""
Metanoia-QA Self-Learning System

Tracks agent mistakes and corrections, builds learned patterns,
and optimizes prompts automatically.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class LearningType(str, Enum):
    MISTAKE = "mistake"
    CORRECTION = "correction"
    PATTERN = "pattern"
    OPTIMIZATION = "optimization"


class LearnedPattern(BaseModel):
    id: str
    agent_role: str
    pattern_type: str
    trigger: str
    response: str
    success_rate: float
    times_applied: int
    created_at: datetime
    updated_at: datetime


class SelfLearningAgent:
    """
    Self-learning system that:
    - Tracks agent mistakes and corrections
    - Identifies patterns from successful executions
    - Optimizes prompts based on success rate
    """

    def __init__(self, supabase_client):
        self.supabase = supabase_client

    async def record_outcome(
        self,
        agent_role: str,
        action: str,
        outcome: str,
        context: dict,
        correction: Optional[str] = None
    ) -> LearnedPattern:
        """Record an outcome and learn from it."""

        existing = await self._find_pattern(agent_role, action, context)

        if existing:
            return await self._update_pattern(existing, outcome, correction)
        else:
            return await self._create_pattern(agent_role, action, context, outcome, correction)

    async def _find_pattern(
        self,
        agent_role: str,
        action: str,
        context: dict
    ) -> Optional[dict]:
        """Find existing pattern matching the action and context."""
        trigger_context = str(context.get("trigger", action))

        response = self.supabase.table("agent_patterns").select("*").eq(
            "agent_role", agent_role
        ).eq(
            "trigger_context", trigger_context
        ).execute()

        if response.data:
            return dict(response.data[0])
        return None

    async def _create_pattern(
        self,
        agent_role: str,
        action: str,
        context: dict,
        outcome: str,
        correction: Optional[str] = None
    ) -> LearnedPattern:
        """Create a new learned pattern."""
        trigger_context = str(context.get("trigger", action))
        response_text = correction or context.get("response", "")

        times_succeeded = 1 if outcome == "success" else 0
        times_applied = 1

        data = {
            "id": str(uuid.uuid4()),
            "agent_role": agent_role,
            "pattern_type": LearningType.MISTAKE.value if outcome == "failure" else LearningType.PATTERN.value,
            "trigger_context": trigger_context,
            "response": response_text,
            "success_rate": 0.5,
            "times_applied": times_applied,
            "times_succeeded": times_succeeded,
            "metadata": context
        }

        response = self.supabase.table("agent_patterns").insert(data).execute()

        if response.data:
            return self._to_learned_pattern(response.data[0])
        raise ValueError("Failed to create pattern")

    async def _update_pattern(
        self,
        existing: dict,
        outcome: str,
        correction: Optional[str] = None
    ) -> LearnedPattern:
        """Update existing pattern with new outcome."""
        times_applied = existing["times_applied"] + 1
        times_succeeded = existing["times_succeeded"] + (1 if outcome == "success" else 0)

        update_data = {
            "times_applied": times_applied,
            "times_succeeded": times_succeeded,
        }

        if correction and outcome == "success":
            update_data["response"] = correction

        response = self.supabase.table("agent_patterns").update(
            update_data
        ).eq("id", existing["id"]).execute()

        if response.data:
            return self._to_learned_pattern(response.data[0])
        raise ValueError("Failed to update pattern")

    def _to_learned_pattern(self, data: dict) -> LearnedPattern:
        """Convert database row to LearnedPattern model."""
        return LearnedPattern(
            id=data["id"],
            agent_role=data["agent_role"],
            pattern_type=data["pattern_type"],
            trigger=data["trigger_context"],
            response=data["response"],
            success_rate=data["success_rate"],
            times_applied=data["times_applied"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )

    async def get_optimization(
        self,
        agent_role: str,
        context: dict
    ) -> Optional[str]:
        """Get optimized prompt/response based on learned patterns."""
        str(context.get("trigger", ""))

        response = self.supabase.table("agent_patterns").select(
            "response", "success_rate", "times_applied"
        ).eq(
            "agent_role", agent_role
        ).eq(
            "pattern_type", LearningType.OPTIMIZATION.value
        ).gte(
            "success_rate", 0.7
        ).order(
            "success_rate", desc=True
        ).limit(1).execute()

        if response.data:
            await self._increment_applied(response.data[0]["id"])
            return str(response.data[0]["response"])
        return None

    async def _increment_applied(self, pattern_id: str) -> None:
        """Increment times_applied for a pattern."""
        self.supabase.table("agent_patterns").update({
            "times_applied": self.supabase.rpc("increment_times_applied", {"pid": pattern_id})
        }).eq("id", pattern_id).execute()

    async def identify_patterns(self, agent_role: str) -> list[LearnedPattern]:
        """Identify recurring patterns for an agent."""
        response = self.supabase.table("agent_patterns").select(
            "*"
        ).eq(
            "agent_role", agent_role
        ).gte(
            "times_applied", 3
        ).order(
            "success_rate", desc=True
        ).execute()

        return [self._to_learned_pattern(row) for row in response.data]

    async def calculate_success_rate(
        self,
        pattern_id: str
    ) -> float:
        """Calculate success rate for a pattern."""
        response = self.supabase.table("agent_patterns").select(
            "times_applied", "times_succeeded"
        ).eq("id", pattern_id).execute()

        if response.data:
            row = response.data[0]
            if row["times_applied"] > 0:
                return float(row["times_succeeded"]) / float(row["times_applied"])
        return 0.5

    async def suggest_prompt_optimization(
        self,
        agent_role: str,
        current_prompt: str
    ) -> str:
        """Suggest optimized version of a prompt."""
        patterns = await self.identify_patterns(agent_role)

        if not patterns:
            return current_prompt

        high_success_patterns = [p for p in patterns if p.success_rate >= 0.8]

        if high_success_patterns:
            best = high_success_patterns[0]
            return f"{current_prompt}\n\n[Optimized based on pattern {best.id[:8]}...: {best.response}]"

        return current_prompt
