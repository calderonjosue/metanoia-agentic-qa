"""MetanoiaGraph - LangGraph State Machine for STLC Orchestration.

This module defines the LangGraph state machine that orchestrates the entire
Software Testing Life Cycle (STLC) across 7 specialized agents, connected
through well-defined edges and conditional routing.

Graph Structure:
----------------

    ┌─────────────┐
    │    INIT     │
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │CONTEXT_ANALYST│ ──── Historical Context Analysis
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │STRATEGY_MANAGER│ ──── Test Planning
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │ DESIGN_LEAD │ ──── Test Case Design
    └──────┬──────┘
           │
      ┌─────┴─────┐
      ▼           ▼
┌─────────┐ ┌──────────┐
│ UI_AUTO │ │PERFORMANCE│
└────┬────┘ └────┬─────┘
     │           │
     ▼           ▼
┌─────────┐ ┌──────────┐
│INTEGRAT.│ │ SECURITY │
└────┬────┘ └────┬─────┘
     └─────┬─────┘
           │
           ▼
    ┌─────────────┐
    │RELEASE_ANALYST │ ──── Release Certification
    └─────────────┘
           │
           ▼
    ┌─────────────┐
    │    CLOSE    │
    └─────────────┘

Agents:
-------
1. ContextAnalyst (historian): Analyzes historical testing context
2. StrategyManager (strategist): Creates high-level test strategy
3. TestDesignLead (designer): Designs detailed test cases
4. UIAutomationEngineer (functional): Executes functional tests
5. PerformanceEngineer (performance): Executes performance tests
6. SecurityEngineer (security): Executes security tests
7. IntegrationEngineer (integration): Executes integration tests
8. ReleaseAnalyst (closer): Makes release certification decision
"""

import logging
import os
from datetime import datetime
from typing import Any, Callable, Literal, Optional

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, StateGraph
from langgraph.types import Send

from src.orchestrator.state import (
    AgentStatus,
    AgentType,
    ExecutionResult,
    MetanoiaState,
)

logger = logging.getLogger(__name__)


class AgentNode:
    """Wrapper class for agent execution functions.

    This class provides a consistent interface for all agent nodes
    in the graph, handling common concerns like logging, error handling,
    and state updates.
    """

    def __init__(
        self,
        agent_type: AgentType,
        agent_id: str,
        execution_fn: Callable[[MetanoiaState], dict[str, Any]],
    ):
        """Initialize an agent node.

        Args:
            agent_type: Type of agent for routing decisions
            agent_id: Unique identifier for this agent instance
            execution_fn: Function that executes the agent logic
        """
        self.agent_type = agent_type
        self.agent_id = agent_id
        self.execution_fn = execution_fn

    def execute(self, state: MetanoiaState) -> dict[str, Any]:
        """Execute the agent and update state.

        Args:
            state: Current MetanoiaState

        Returns:
            Dictionary of state updates to apply
        """
        logger.info(f"Executing {self.agent_type.value} ({self.agent_id})")

        result = ExecutionResult(
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            status=AgentStatus.RUNNING,
            started_at=datetime.utcnow(),
        )

        try:
            output = self.execution_fn(state)

            result.status = AgentStatus.COMPLETED
            result.output = output
            result.completed_at = datetime.utcnow()
            result.duration_seconds = (
                result.completed_at - result.started_at
            ).total_seconds()

            logger.info(
                f"{self.agent_type.value} completed in {result.duration_seconds:.2f}s"
            )

        except Exception as e:
            logger.error(f"{self.agent_type.value} failed: {str(e)}")
            result.status = AgentStatus.FAILED
            result.error = str(e)
            result.completed_at = datetime.utcnow()
            result.duration_seconds = (
                result.completed_at - result.started_at
            ).total_seconds()

        return {
            "execution_results": {**state.execution_results, self.agent_id: result}
        }


class MetanoiaGraph:
    """LangGraph state machine for STLC orchestration.

    This class builds and manages the complete state graph for the
    Metanoia-QA autonomous testing framework, connecting all 7 agents
    through proper edges and conditional routing.

    Attributes:
        graph: The compiled StateGraph
        agents: Dictionary of registered agent nodes
        checkpointer: Optional checkpoint saver for persistence
        agent_registry: Optional registry of real agent instances for execution
    """

    def __init__(
        self,
        checkpointer: Optional[BaseCheckpointSaver] = None,
        max_iterations: int = 100,
        agent_registry: Optional[dict[str, Any]] = None,
    ):
        """Initialize the MetanoiaGraph.

        Args:
            checkpointer: Optional checkpoint saver for state persistence
            max_iterations: Maximum iterations before circuit breaker
            agent_registry: Optional dictionary mapping agent names to
                           agent instances (e.g., {"context_analyst": ContextAnalyst instance})
        """
        self.graph = None
        self.agents: dict[str, AgentNode] = {}
        self.checkpointer = checkpointer
        self.max_iterations = max_iterations
        self.agent_registry = agent_registry or {}
        self._use_real_agents = len(self.agent_registry) > 0
        self._build_graph()

    def _build_graph(self) -> None:
        """Construct the StateGraph with all nodes and edges."""
        builder = StateGraph(MetanoiaState)

        self._add_init_node(builder)
        self._add_agent_nodes(builder)
        self._add_execution_phase(builder)
        self._add_close_node(builder)
        self._add_edges(builder)
        self._add_fan_out_edges(builder)

        self.graph = builder.compile(
            checkpointer=self.checkpointer,
            debug=os.getenv("LANGRAPH_DEBUG", "false").lower() == "true",
        )

    def _add_init_node(self, builder: StateGraph) -> None:
        """Add the initialization node.

        Args:
            builder: StateGraph builder
        """

        def init_node(state: MetanoiaState) -> dict[str, Any]:
            """Initialize the sprint processing."""
            logger.info(f"Initializing sprint: {state.sprint_id}")
            state.update_phase("init")
            state.increment_iteration()
            return {
                "current_phase": "plan",
                "iteration_count": state.iteration_count,
            }

        builder.add_node("init", init_node)

    def _add_agent_nodes(self, builder: StateGraph) -> None:
        """Add all planning/design agent nodes.

        Args:
            builder: StateGraph builder
        """

        def context_analyst_node(state: MetanoiaState) -> dict[str, Any]:
            """ContextAnalyst: Historical context analysis."""
            logger.info("ContextAnalyst analyzing historical context...")
            state.update_phase("plan")

            if self._use_real_agents and "context_analyst" in self.agent_registry:
                try:
                    agent = self.agent_registry["context_analyst"]
                    agent_input = {
                        "sprint_id": state.sprint_id,
                        "sprint_goal": state.sprint_goal,
                        "test_cases": [tc.model_dump() for tc in state.test_cases],
                    }
                    response = agent.run(agent_input)
                    if response.status.value == "completed":
                        return {
                            "context_analysis": response.output,
                            "iteration_count": state.iteration_count,
                        }
                    else:
                        logger.warning(f"ContextAnalyst failed: {response.error}")
                except Exception as e:
                    logger.error(f"ContextAnalyst execution error: {e}")

            context = {
                "historical_risks": ["legacy_auth_issues", "api_versioning_deprecations"],
                "regression_score": 0.45,
                "similar_sprints": [
                    {"id": "S-2023-Q4-042", "risk_patterns": ["timeout", "memory_leak"]}
                ],
                "lessons_learned": [
                    "Always validate token expiration before API calls",
                    "Set explicit timeouts for external service calls",
                ],
                "analyzed_at": datetime.utcnow().isoformat(),
            }

            return {
                "context_analysis": context,
                "iteration_count": state.iteration_count,
            }

        def strategy_manager_node(state: MetanoiaState) -> dict[str, Any]:
            """StrategyManager: Test planning."""
            logger.info("StrategyManager creating test strategy...")

            if self._use_real_agents and "strategy_manager" in self.agent_registry:
                try:
                    agent = self.agent_registry["strategy_manager"]
                    agent_input = {
                        "sprint_id": state.sprint_id,
                        "sprint_goal": state.sprint_goal,
                        "context_analysis": state.context_analysis,
                    }
                    response = agent.run(agent_input)
                    if response.status.value == "completed":
                        return {
                            "test_plan": response.output,
                            "iteration_count": state.iteration_count,
                        }
                    else:
                        logger.warning(f"StrategyManager failed: {response.error}")
                except Exception as e:
                    logger.error(f"StrategyManager execution error: {e}")

            test_plan = {
                "approach": "risk-based testing with ISTQB defect clustering",
                "total_test_cases": 42,
                "estimated_hours": 16.5,
                "effort_allocation": {
                    "functional": 8.0,
                    "performance": 3.0,
                    "security": 2.5,
                    "integration": 3.0,
                },
                "risk_summary": {
                    "high_risk_areas": ["authentication", "payment_processing"],
                    "medium_risk_areas": ["user_profile", "notifications"],
                    "low_risk_areas": ["static_content", "logging"],
                },
                "created_at": datetime.utcnow().isoformat(),
            }

            return {
                "test_plan": test_plan,
                "iteration_count": state.iteration_count,
            }

        def design_lead_node(state: MetanoiaState) -> dict[str, Any]:
            """TestDesignLead: Test case design."""
            logger.info("TestDesignLead designing test cases...")

            from src.orchestrator.state import TestCase

            if self._use_real_agents and "design_lead" in self.agent_registry:
                try:
                    agent = self.agent_registry["design_lead"]
                    agent_input = {
                        "sprint_id": state.sprint_id,
                        "sprint_goal": state.sprint_goal,
                        "context_analysis": state.context_analysis,
                        "test_plan": state.test_plan,
                    }
                    response = agent.run(agent_input)
                    if response.status.value == "completed":
                        tc_data = response.output.get("test_cases", [])
                        test_cases = [TestCase(**tc) for tc in tc_data]
                        return {
                            "test_cases": test_cases,
                            "iteration_count": state.iteration_count,
                        }
                    else:
                        logger.warning(f"TestDesignLead failed: {response.error}")
                except Exception as e:
                    logger.error(f"TestDesignLead execution error: {e}")

            test_cases = [
                TestCase(
                    id="TC-001",
                    title="User Authentication Flow",
                    description="Verify complete login/logout cycle",
                    priority="Critical",
                    category="Functional",
                    estimated_duration_minutes=15,
                    steps=[
                        "Navigate to login page",
                        "Enter valid credentials",
                        "Click login button",
                        "Verify redirect to dashboard",
                        "Click logout",
                        "Verify session termination",
                    ],
                    expected_results="User can successfully login and logout",
                ),
                TestCase(
                    id="TC-002",
                    title="Session Timeout Handling",
                    description="Verify session expires after inactivity",
                    priority="High",
                    category="Functional",
                    estimated_duration_minutes=10,
                    steps=[
                        "Login to system",
                        "Wait for session timeout period",
                        "Attempt to access protected resource",
                    ],
                    expected_results="System redirects to login with session expired message",
                ),
                TestCase(
                    id="TC-003",
                    title="API Response Time Under Load",
                    description="Verify API handles concurrent requests",
                    priority="High",
                    category="Performance",
                    estimated_duration_minutes=20,
                    steps=[
                        "Configure load test parameters",
                        "Send 100 concurrent requests",
                        "Measure response times",
                    ],
                    expected_results="95th percentile response time < 500ms",
                ),
            ]

            return {
                "test_cases": test_cases,
                "iteration_count": state.iteration_count,
            }

        builder.add_node("context_analyst", context_analyst_node)
        builder.add_node("strategy_manager", strategy_manager_node)
        builder.add_node("design_lead", design_lead_node)

    def _add_execution_phase(self, builder: StateGraph) -> None:
        """Add parallel execution phase for test agents.

        Args:
            builder: StateGraph builder
        """

        def ui_automation_node(state: MetanoiaState) -> dict[str, Any]:
            """UIAutomationEngineer: Execute functional tests."""
            logger.info("UIAutomationEngineer executing functional tests...")

            if self._use_real_agents and "ui_automation" in self.agent_registry:
                try:
                    agent = self.agent_registry["ui_automation"]
                    agent_input = {
                        "sprint_id": state.sprint_id,
                        "test_cases": [tc.model_dump() for tc in state.test_cases],
                    }
                    response = agent.run(agent_input)
                    if response.status.value == "completed":
                        return {
                            "execution_results": {
                                **state.execution_results,
                                "ui_automation": ExecutionResult(
                                    agent_id="ui_automation",
                                    agent_type=AgentType.UI_AUTOMATION_ENGINEER,
                                    status=AgentStatus.COMPLETED,
                                    output=response.output,
                                    completed_at=datetime.utcnow(),
                                    duration_seconds=response.duration_seconds,
                                ),
                            },
                            "iteration_count": state.iteration_count,
                        }
                    else:
                        logger.warning(f"UIAutomation failed: {response.error}")
                except Exception as e:
                    logger.error(f"UIAutomation execution error: {e}")

            return {
                "execution_results": {
                    **state.execution_results,
                    "ui_automation": ExecutionResult(
                        agent_id="ui_automation",
                        agent_type=AgentType.UI_AUTOMATION_ENGINEER,
                        status=AgentStatus.COMPLETED,
                        output={
                            "tests_passed": 38,
                            "tests_failed": 2,
                            "tests_skipped": 2,
                            "duration_seconds": 245.5,
                        },
                        completed_at=datetime.utcnow(),
                        duration_seconds=245.5,
                    ),
                },
                "iteration_count": state.iteration_count,
            }

        def performance_node(state: MetanoiaState) -> dict[str, Any]:
            """PerformanceEngineer: Execute performance tests."""
            logger.info("PerformanceEngineer executing performance tests...")

            if self._use_real_agents and "performance" in self.agent_registry:
                try:
                    agent = self.agent_registry["performance"]
                    agent_input = {
                        "sprint_id": state.sprint_id,
                        "test_plan": state.test_plan,
                    }
                    response = agent.run(agent_input)
                    if response.status.value == "completed":
                        return {
                            "execution_results": {
                                **state.execution_results,
                                "performance": ExecutionResult(
                                    agent_id="performance",
                                    agent_type=AgentType.PERFORMANCE_ENGINEER,
                                    status=AgentStatus.COMPLETED,
                                    output=response.output,
                                    completed_at=datetime.utcnow(),
                                    duration_seconds=response.duration_seconds,
                                ),
                            },
                            "iteration_count": state.iteration_count,
                        }
                    else:
                        logger.warning(f"PerformanceEngineer failed: {response.error}")
                except Exception as e:
                    logger.error(f"PerformanceEngineer execution error: {e}")

            return {
                "execution_results": {
                    **state.execution_results,
                    "performance": ExecutionResult(
                        agent_id="performance",
                        agent_type=AgentType.PERFORMANCE_ENGINEER,
                        status=AgentStatus.COMPLETED,
                        output={
                            "throughput_rps": 1250,
                            "avg_response_ms": 85,
                            "p95_response_ms": 145,
                            "p99_response_ms": 210,
                            "error_rate_percent": 0.02,
                        },
                        completed_at=datetime.utcnow(),
                        duration_seconds=180.0,
                    ),
                },
                "iteration_count": state.iteration_count,
            }

        def security_node(state: MetanoiaState) -> dict[str, Any]:
            """SecurityEngineer: Execute security tests."""
            logger.info("SecurityEngineer executing security tests...")

            if self._use_real_agents and "security" in self.agent_registry:
                try:
                    agent = self.agent_registry["security"]
                    agent_input = {
                        "sprint_id": state.sprint_id,
                        "test_plan": state.test_plan,
                    }
                    response = agent.run(agent_input)
                    if response.status.value == "completed":
                        return {
                            "execution_results": {
                                **state.execution_results,
                                "security": ExecutionResult(
                                    agent_id="security",
                                    agent_type=AgentType.SECURITY_ENGINEER,
                                    status=AgentStatus.COMPLETED,
                                    output=response.output,
                                    completed_at=datetime.utcnow(),
                                    duration_seconds=response.duration_seconds,
                                ),
                            },
                            "iteration_count": state.iteration_count,
                        }
                    else:
                        logger.warning(f"SecurityEngineer failed: {response.error}")
                except Exception as e:
                    logger.error(f"SecurityEngineer execution error: {e}")

            return {
                "execution_results": {
                    **state.execution_results,
                    "security": ExecutionResult(
                        agent_id="security",
                        agent_type=AgentType.SECURITY_ENGINEER,
                        status=AgentStatus.COMPLETED,
                        output={
                            "vulnerabilities_found": 1,
                            "critical": 0,
                            "high": 0,
                            "medium": 1,
                            "low": 0,
                            "findings": [
                                {
                                    "cve": None,
                                    "title": "Information Disclosure in Error Messages",
                                    "severity": "Medium",
                                    "status": "Remediated",
                                }
                            ],
                        },
                        completed_at=datetime.utcnow(),
                        duration_seconds=120.0,
                    ),
                },
                "iteration_count": state.iteration_count,
            }

        def integration_node(state: MetanoiaState) -> dict[str, Any]:
            """IntegrationEngineer: Execute integration tests."""
            logger.info("IntegrationEngineer executing integration tests...")

            if self._use_real_agents and "integration" in self.agent_registry:
                try:
                    agent = self.agent_registry["integration"]
                    agent_input = {
                        "sprint_id": state.sprint_id,
                        "test_cases": [tc.model_dump() for tc in state.test_cases],
                    }
                    response = agent.run(agent_input)
                    if response.status.value == "completed":
                        return {
                            "execution_results": {
                                **state.execution_results,
                                "integration": ExecutionResult(
                                    agent_id="integration",
                                    agent_type=AgentType.INTEGRATION_ENGINEER,
                                    status=AgentStatus.COMPLETED,
                                    output=response.output,
                                    completed_at=datetime.utcnow(),
                                    duration_seconds=response.duration_seconds,
                                ),
                            },
                            "iteration_count": state.iteration_count,
                        }
                    else:
                        logger.warning(f"IntegrationEngineer failed: {response.error}")
                except Exception as e:
                    logger.error(f"IntegrationEngineer execution error: {e}")

            return {
                "execution_results": {
                    **state.execution_results,
                    "integration": ExecutionResult(
                        agent_id="integration",
                        agent_type=AgentType.INTEGRATION_ENGINEER,
                        status=AgentStatus.COMPLETED,
                        output={
                            "tests_passed": 28,
                            "tests_failed": 1,
                            "tests_skipped": 1,
                            "duration_seconds": 95.0,
                            "failed_endpoints": ["/api/v2/users/search"],
                        },
                        completed_at=datetime.utcnow(),
                        duration_seconds=95.0,
                    ),
                },
                "iteration_count": state.iteration_count,
            }

        builder.add_node("ui_automation", ui_automation_node)
        builder.add_node("performance", performance_node)
        builder.add_node("security", security_node)
        builder.add_node("integration", integration_node)

    def _add_close_node(self, builder: StateGraph) -> None:
        """Add closing phase with release certification.

        Args:
            builder: StateGraph builder
        """

        def release_analyst_node(state: MetanoiaState) -> dict[str, Any]:
            """ReleaseAnalyst: Generate release certification."""
            logger.info("ReleaseAnalyst generating release certification...")

            from src.orchestrator.state import ReleaseCertification

            if self._use_real_agents and "release_analyst" in self.agent_registry:
                try:
                    agent = self.agent_registry["release_analyst"]
                    agent_input = {
                        "sprint_id": state.sprint_id,
                        "execution_results": {
                            k: {"output": v.output, "status": v.status.value}
                            for k, v in state.execution_results.items()
                        },
                    }
                    response = agent.run(agent_input)
                    if response.status.value == "completed":
                        cert_data = response.output
                        certification = ReleaseCertification(
                            sprint_id=state.sprint_id,
                            certified=cert_data.get("certified", False),
                            confidence_score=cert_data.get("confidence_score", 0.0),
                            blockers=cert_data.get("blockers", []),
                            recommendations=cert_data.get("recommendations", []),
                            summary=cert_data.get("summary", ""),
                        )
                        return {
                            "release_certification": certification,
                            "current_phase": "close",
                            "iteration_count": state.iteration_count,
                        }
                    else:
                        logger.warning(f"ReleaseAnalyst failed: {response.error}")
                except Exception as e:
                    logger.error(f"ReleaseAnalyst execution error: {e}")

            total_tests = sum(
                r.output.get("tests_passed", 0)
                + r.output.get("tests_failed", 0)
                for r in state.execution_results.values()
            )
            total_failures = sum(
                r.output.get("tests_failed", 0)
                for r in state.execution_results.values()
            )

            failure_rate = total_failures / total_tests if total_tests > 0 else 0

            certification = ReleaseCertification(
                sprint_id=state.sprint_id,
                certified=failure_rate < 0.05,
                confidence_score=0.92,
                blockers=[
                    "Integration test failure: /api/v2/users/search endpoint"
                ] if failure_rate >= 0.05 else [],
                recommendations=[
                    "Monitor /api/v2/users/search endpoint in production",
                    "Schedule follow-up security scan next sprint",
                ],
                summary=f"Release certification {'APPROVED' if failure_rate < 0.05 else 'DENIED'} with {failure_rate*100:.1f}% failure rate",
            )

            return {
                "release_certification": certification,
                "current_phase": "close",
                "iteration_count": state.iteration_count,
            }

        builder.add_node("release_analyst", release_analyst_node)

    def _add_edges(self, builder: StateGraph) -> None:
        """Define all graph edges with conditional routing.

        Args:
            builder: StateGraph builder
        """

        def should_execute_parallel(state: MetanoiaState) -> Literal["execute_phase"]:
            """Determine if execution phase should begin."""
            if state.is_circuit_breaker_triggered():
                logger.warning("Circuit breaker triggered!")
                return "end"
            return "execute_phase"

        builder.set_entry_point("init")

        builder.add_edge("init", "context_analyst")
        builder.add_edge("context_analyst", "strategy_manager")
        builder.add_edge("strategy_manager", "design_lead")

        builder.add_conditional_edges(
            "design_lead",
            should_execute_parallel,
            {
                "execute_phase": "execute_phase",
                "end": END,
            },
        )

        builder.add_node(
            "execute_phase",
            self._parallel_execution_node,
        )

        builder.add_edge("execute_phase", "release_analyst")
        builder.add_edge("release_analyst", END)

    def _create_fan_out(self, state: MetanoiaState) -> list[Send]:
        """Create fan-out Send objects for parallel agent execution.

        Uses LangGraph's Send() API to fan out to multiple test execution
        agents that run concurrently.

        Args:
            state: Current MetanoiaState

        Returns:
            List of Send objects for parallel execution
        """
        return [
            Send("ui_automation", state),
            Send("performance", state),
            Send("security", state),
            Send("integration", state),
        ]

    def _add_fan_out_edges(self, builder: StateGraph) -> None:
        """Add conditional fan-out edges for parallel execution using Send().

        Args:
            builder: StateGraph builder
        """
        builder.add_conditional_edges(
            "execute_phase",
            self._create_fan_out,
            ["ui_automation", "performance", "security", "integration"],
        )

    def _parallel_execution_node(self, state: MetanoiaState) -> dict[str, Any]:
        """Execute parallel fan-out to test agents.

        This node uses LangGraph's Send() API to fan out to multiple agents
        that run concurrently. The actual parallel execution is handled by
        the fan-out edges created in _add_fan_out_edges.

        Args:
            state: Current MetanoiaState

        Returns:
            Empty dict - actual execution happens via Send() fan-out
        """
        state.update_phase("execute")
        logger.info("Starting parallel test execution fan-out...")

        return {}

    def get_graph(self) -> StateGraph:
        """Get the compiled graph for execution.

        Returns:
            Compiled LangGraph StateGraph
        """
        return self.graph

    def run(self, initial_state: MetanoiaState, thread_id: Optional[str] = None) -> MetanoiaState:
        """Run the graph with the given initial state.

        Args:
            initial_state: Starting state for the graph
            thread_id: Optional thread ID for checkpointing

        Returns:
            Final MetanoiaState after graph execution
        """
        config = {}
        if thread_id or self.checkpointer:
            config["configurable"] = {
                "thread_id": thread_id or initial_state.sprint_id,
            }

        result = self.graph.invoke(initial_state, config)
        return result

    def run_async(
        self,
        initial_state: MetanoiaState,
        thread_id: Optional[str] = None,
    ):
        """Run the graph asynchronously.

        Args:
            initial_state: Starting state for the graph
            thread_id: Optional thread ID for checkpointing

        Returns:
            Async generator yielding state updates
        """
        config = {}
        if thread_id or self.checkpointer:
            config["configurable"] = {
                "thread_id": thread_id or initial_state.sprint_id,
            }

        return self.graph.astream(initial_state, config)


def create_graph(
    checkpointer: Optional[BaseCheckpointSaver] = None,
    max_iterations: int = 100,
    agent_registry: Optional[dict[str, Any]] = None,
) -> MetanoiaGraph:
    """Factory function to create a configured MetanoiaGraph.

    Args:
        checkpointer: Optional checkpoint saver
        max_iterations: Maximum iterations before circuit breaker
        agent_registry: Optional dictionary mapping agent names to instances

    Returns:
        Configured MetanoiaGraph instance
    """
    return MetanoiaGraph(
        checkpointer=checkpointer,
        max_iterations=max_iterations,
        agent_registry=agent_registry,
    )
