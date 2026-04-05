"""Tests for base agent classes."""

from datetime import datetime

import pytest

from src.agents import (
    ContextAnalyst,
    PerformanceEngineer,
    ReleaseAnalyst,
    SecurityEngineer,
    StrategyManager,
    TestDesignLead,
    UIAutomationEngineer,
)
from src.agents.base import (
    AgentConfig,
    AgentResponse,
    AgentStatus,
    AgentType,
    BaseAgent,
)


class TestAgentConfig:
    """Tests for AgentConfig dataclass."""

    def test_agent_config_creation(self):
        """Test creating an AgentConfig with default values."""
        config = AgentConfig(
            agent_type=AgentType.CONTEXT_ANALYST,
            agent_id="test-001"
        )

        assert config.agent_type == AgentType.CONTEXT_ANALYST
        assert config.agent_id == "test-001"
        assert config.model == "gemini-1.5-flash"
        assert config.temperature == 0.7
        assert config.max_retries == 3
        assert config.timeout_seconds == 300
        assert config.metadata == {}

    def test_agent_config_custom_values(self):
        """Test creating an AgentConfig with custom values."""
        config = AgentConfig(
            agent_type=AgentType.STRATEGY_MANAGER,
            agent_id="custom-001",
            model="gemini-1.5-pro",
            temperature=0.9,
            max_retries=5,
            timeout_seconds=600,
            metadata={"key": "value"}
        )

        assert config.model == "gemini-1.5-pro"
        assert config.temperature == 0.9
        assert config.max_retries == 5
        assert config.timeout_seconds == 600
        assert config.metadata == {"key": "value"}


class TestAgentResponse:
    """Tests for AgentResponse model."""

    def test_agent_response_creation(self):
        """Test creating an AgentResponse."""
        response = AgentResponse(
            agent_id="test-001",
            agent_type=AgentType.CONTEXT_ANALYST,
            status=AgentStatus.COMPLETED,
            output={"result": "success"}
        )

        assert response.agent_id == "test-001"
        assert response.agent_type == AgentType.CONTEXT_ANALYST
        assert response.status == AgentStatus.COMPLETED
        assert response.output == {"result": "success"}
        assert response.error is None
        assert response.completed_at is None
        assert response.duration_seconds is None

    def test_agent_response_with_error(self):
        """Test AgentResponse with error."""
        response = AgentResponse(
            agent_id="test-002",
            agent_type=AgentType.RELEASE_ANALYST,
            status=AgentStatus.FAILED,
            error="Test execution failed"
        )

        assert response.status == AgentStatus.FAILED
        assert response.error == "Test execution failed"

    def test_agent_response_timestamps(self):
        """Test AgentResponse timestamps are set correctly."""
        started = datetime.utcnow()
        response = AgentResponse(
            agent_id="test-003",
            agent_type=AgentType.STRATEGY_MANAGER,
            status=AgentStatus.RUNNING,
            started_at=started
        )

        assert response.started_at == started


class TestBaseAgent:
    """Tests for BaseAgent abstract class."""

    def test_base_agent_is_abstract(self):
        """Test that BaseAgent cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseAgent(config=AgentConfig(
                agent_type=AgentType.CONTEXT_ANALYST,
                agent_id="test"
            ))

    def test_concrete_agent_inherits_base(self):
        """Test that concrete agents inherit from BaseAgent."""
        agent = ContextAnalyst(supabase_client=None, gemini_client=None)

        assert isinstance(agent, BaseAgent)
        assert agent.status == AgentStatus.IDLE

    def test_agent_config_stored(self):
        """Test that agent config is stored correctly."""
        config = AgentConfig(
            agent_type=AgentType.STRATEGY_MANAGER,
            agent_id="strategy-001",
            temperature=0.5
        )
        agent = StrategyManager(config=config)

        assert agent.config == config
        assert agent.config.temperature == 0.5

    def test_agent_run_method(self):
        """Test the run method with error handling."""
        config = AgentConfig(
            agent_type=AgentType.CONTEXT_ANALYST,
            agent_id="test-run"
        )
        agent = ContextAnalyst(supabase_client=None, gemini_client=None)
        agent.config = config

        state = {"sprint_goal": "Test sprint"}
        response = agent.run(state)

        assert response.agent_id == "test-run"
        assert response.status == AgentStatus.COMPLETED


class TestAgentType:
    """Tests for AgentType enumeration."""

    def test_agent_types_exist(self):
        """Test all expected agent types exist."""
        assert AgentType.CONTEXT_ANALYST == "context_analyst"
        assert AgentType.STRATEGY_MANAGER == "strategy_manager"
        assert AgentType.TEST_DESIGN_LEAD == "test_design_lead"
        assert AgentType.UI_AUTOMATION_ENGINEER == "ui_automation_engineer"
        assert AgentType.PERFORMANCE_ENGINEER == "performance_engineer"
        assert AgentType.SECURITY_ENGINEER == "security_engineer"
        assert AgentType.INTEGRATION_ENGINEER == "integration_engineer"
        assert AgentType.RELEASE_ANALYST == "release_analyst"


class TestAgentStatus:
    """Tests for AgentStatus enumeration."""

    def test_agent_statuses_exist(self):
        """Test all expected agent statuses exist."""
        assert AgentStatus.IDLE == "idle"
        assert AgentStatus.RUNNING == "running"
        assert AgentStatus.COMPLETED == "completed"
        assert AgentStatus.FAILED == "failed"
        assert AgentStatus.PAUSED == "paused"


class TestContextAnalyst:
    """Tests for Context Analyst agent."""

    def test_context_analyst_initialization(self):
        """Test Context Analyst initialization."""
        agent = ContextAnalyst(supabase_client=None, gemini_client=None)

        assert agent.supabase_client is None
        assert agent.gemini_client is None

    @pytest.mark.asyncio
    async def test_context_analyst_analyze(self):
        """Test Context Analyst analyze returns result."""
        agent = ContextAnalyst(supabase_client=None, gemini_client=None)

        result = await agent.analyze("Test sprint goal")

        assert "risk_level" in result
        assert "risk_score" in result


class TestStrategyManager:
    """Tests for Strategy Manager agent."""

    def test_strategy_manager_initialization(self):
        """Test Strategy Manager initialization."""
        agent = StrategyManager()

        assert agent.config.agent_type == AgentType.STRATEGY_MANAGER

    def test_strategy_manager_execute(self):
        """Test Strategy Manager execute returns plan."""
        agent = StrategyManager()
        state = {"context_analysis": {"risk_score": 0.3}}

        response = agent.execute(state)

        assert response.status == AgentStatus.COMPLETED
        assert "test_plan" in response.output


class TestTestDesignLead:
    """Tests for Test Design Lead agent."""

    def test_design_lead_initialization(self):
        """Test Design Lead initialization."""
        agent = TestDesignLead(gemini_client=None)

        assert agent.gemini_client is None


class TestUIAutomationEngineer:
    """Tests for UI Automation Engineer agent."""

    def test_ui_automation_initialization(self):
        """Test UI Automation Engineer initialization."""
        agent = UIAutomationEngineer()

        assert agent.config.agent_type == AgentType.UI_AUTOMATION_ENGINEER


class TestPerformanceEngineer:
    """Tests for Performance Engineer agent."""

    def test_performance_engineer_initialization(self):
        """Test Performance Engineer initialization."""
        agent = PerformanceEngineer()

        assert agent.config.agent_type == AgentType.PERFORMANCE_ENGINEER


class TestSecurityEngineer:
    """Tests for Security Engineer agent."""

    def test_security_engineer_initialization(self):
        """Test Security Engineer initialization."""
        agent = SecurityEngineer()

        assert agent.config.agent_type == AgentType.SECURITY_ENGINEER


class TestReleaseAnalyst:
    """Tests for Release Analyst agent."""

    def test_release_analyst_initialization(self):
        """Test Release Analyst initialization."""
        agent = ReleaseAnalyst()

        assert agent.config.agent_type == AgentType.RELEASE_ANALYST
