"""Tests for base agent classes."""

import pytest
from datetime import datetime
from unittest.mock import Mock

from src.agents.base import (
    AgentType,
    AgentStatus,
    AgentConfig,
    AgentResponse,
    BaseAgent,
    ElArqueologo,
    ElEstratega,
    ElDisenador,
    AgenteFuncional,
    AgenteRendimiento,
    AgenteSeguridad,
    AgenteIntegracion,
    ElCerrador,
)


class TestAgentConfig:
    """Tests for AgentConfig dataclass."""

    def test_agent_config_creation(self):
        """Test creating an AgentConfig with default values."""
        config = AgentConfig(
            agent_type=AgentType.EL_ARQUEOLOGO,
            agent_id="test-001"
        )
        
        assert config.agent_type == AgentType.EL_ARQUEOLOGO
        assert config.agent_id == "test-001"
        assert config.model == "gemini-1.5-flash"
        assert config.temperature == 0.7
        assert config.max_retries == 3
        assert config.timeout_seconds == 300
        assert config.metadata == {}

    def test_agent_config_custom_values(self):
        """Test creating an AgentConfig with custom values."""
        config = AgentConfig(
            agent_type=AgentType.EL_DISENADOR,
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
            agent_type=AgentType.EL_ARQUEOLOGO,
            status=AgentStatus.COMPLETED,
            output={"result": "success"}
        )
        
        assert response.agent_id == "test-001"
        assert response.agent_type == AgentType.EL_ARQUEOLOGO
        assert response.status == AgentStatus.COMPLETED
        assert response.output == {"result": "success"}
        assert response.error is None
        assert response.completed_at is None
        assert response.duration_seconds is None

    def test_agent_response_with_error(self):
        """Test AgentResponse with error."""
        response = AgentResponse(
            agent_id="test-002",
            agent_type=AgentType.EL_CERRADOR,
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
            agent_type=AgentType.EL_ESTRATEGA,
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
                agent_type=AgentType.EL_ARQUEOLOGO,
                agent_id="test"
            ))

    def test_concrete_agent_inherits_base(self):
        """Test that concrete agents inherit from BaseAgent."""
        agent = ElArqueologo()
        
        assert isinstance(agent, BaseAgent)
        assert agent.status == AgentStatus.IDLE

    def test_agent_config_stored(self):
        """Test that agent config is stored correctly."""
        config = AgentConfig(
            agent_type=AgentType.EL_DISENADOR,
            agent_id="designer-001",
            temperature=0.5
        )
        agent = ElDisenador(config=config)
        
        assert agent.config == config
        assert agent.config.temperature == 0.5

    def test_agent_run_method(self):
        """Test the run method with error handling."""
        config = AgentConfig(
            agent_type=AgentType.EL_ARQUEOLOGO,
            agent_id="test-run"
        )
        agent = ElArqueologo(config=config)
        
        state = {"sprint_goal": "Test sprint"}
        response = agent.run(state)
        
        assert response.agent_id == "test-run"
        assert response.status == AgentStatus.COMPLETED


class TestAgentType:
    """Tests for AgentType enumeration."""

    def test_agent_types_exist(self):
        """Test all expected agent types exist."""
        assert AgentType.EL_ARQUEOLOGO == "el_arqueologo"
        assert AgentType.EL_ESTRATEGA == "el_estratega"
        assert AgentType.EL_DISENADOR == "el_disenador"
        assert AgentType.AGENTE_FUNCIONAL == "agente_funcional"
        assert AgentType.AGENTE_RENDIMIENTO == "agente_rendimiento"
        assert AgentType.AGENTE_SEGURIDAD == "agente_seguridad"
        assert AgentType.AGENTE_INTEGRACION == "agente_integracion"
        assert AgentType.EL_CERRADOR == "el_cerrador"


class TestAgentStatus:
    """Tests for AgentStatus enumeration."""

    def test_agent_statuses_exist(self):
        """Test all expected agent statuses exist."""
        assert AgentStatus.IDLE == "idle"
        assert AgentStatus.RUNNING == "running"
        assert AgentStatus.COMPLETED == "completed"
        assert AgentStatus.FAILED == "failed"
        assert AgentStatus.PAUSED == "paused"


class TestElArqueologo:
    """Tests for El Arqueólogo (Historian) agent."""

    def test_el_arqueologo_initialization(self):
        """Test El Arqueólogo initialization."""
        agent = ElArqueologo()
        
        assert agent.config.agent_type == AgentType.EL_ARQUEOLOGO
        assert agent.config.agent_id == "arqueologo-001"

    def test_el_arqueologo_execute_returns_response(self):
        """Test El Arqueólogo execute returns proper response."""
        agent = ElArqueologo()
        state = {"sprint_goal": "Test goal"}
        
        response = agent.execute(state)
        
        assert response.agent_type == AgentType.EL_ARQUEOLOGO
        assert response.status == AgentStatus.COMPLETED
        assert "regression_score" in response.output


class TestElEstratega:
    """Tests for El Estratega (Strategist) agent."""

    def test_el_estratega_initialization(self):
        """Test El Estratega initialization."""
        agent = ElEstratega()
        
        assert agent.config.agent_type == AgentType.EL_ESTRATEGA
        assert agent.config.agent_id == "estratega-001"

    def test_el_estratega_execute_with_context(self):
        """Test El Estratega execute with context analysis."""
        agent = ElEstratega()
        state = {
            "context_analysis": {"regression_score": 0.5},
            "sprint_goal": "Implement feature"
        }
        
        response = agent.execute(state)
        
        assert response.status == AgentStatus.COMPLETED
        assert "total_test_cases" in response.output
        assert "effort_allocation" in response.output


class TestElDisenador:
    """Tests for El Diseñador (Designer) agent."""

    def test_el_disenador_initialization(self):
        """Test El Diseñador initialization."""
        agent = ElDisenador()
        
        assert agent.config.agent_type == AgentType.EL_DISENADOR
        assert agent.config.agent_id == "disenador-001"

    def test_el_disenador_execute_generates_test_cases(self):
        """Test El Diseñador execute generates test cases."""
        agent = ElDisenador()
        state = {"test_plan": {"total_test_cases": 10}}
        
        response = agent.execute(state)
        
        assert response.status == AgentStatus.COMPLETED
        assert "test_cases" in response.output
        assert response.output["count"] > 0


class TestAgenteFuncional:
    """Tests for Agente Funcional (Functional) agent."""

    def test_agente_funcional_initialization(self):
        """Test Agente Funcional initialization."""
        agent = AgenteFuncional()
        
        assert agent.config.agent_type == AgentType.AGENTE_FUNCIONAL
        assert agent.config.agent_id == "funcional-001"

    def test_agente_funcional_execute(self):
        """Test Agente Funcional execute returns results."""
        agent = AgenteFuncional()
        state = {}
        
        response = agent.execute(state)
        
        assert response.status == AgentStatus.COMPLETED
        assert "tests_passed" in response.output
        assert response.output["tests_passed"] == 38


class TestAgenteRendimiento:
    """Tests for Agente Rendimiento (Performance) agent."""

    def test_agente_rendimiento_initialization(self):
        """Test Agente Rendimiento initialization."""
        agent = AgenteRendimiento()
        
        assert agent.config.agent_type == AgentType.AGENTE_RENDIMIENTO
        assert agent.config.agent_id == "rendimiento-001"

    def test_agente_rendimiento_execute(self):
        """Test Agente Rendimiento execute returns metrics."""
        agent = AgenteRendimiento()
        state = {}
        
        response = agent.execute(state)
        
        assert response.status == AgentStatus.COMPLETED
        assert "throughput_rps" in response.output
        assert "p95_response_ms" in response.output


class TestAgenteSeguridad:
    """Tests for Agente Seguridad (Security) agent."""

    def test_agente_seguridad_initialization(self):
        """Test Agente Seguridad initialization."""
        agent = AgenteSeguridad()
        
        assert agent.config.agent_type == AgentType.AGENTE_SEGURIDAD
        assert agent.config.agent_id == "seguridad-001"

    def test_agente_seguridad_execute(self):
        """Test Agente Seguridad execute returns findings."""
        agent = AgenteSeguridad()
        state = {}
        
        response = agent.execute(state)
        
        assert response.status == AgentStatus.COMPLETED
        assert "vulnerabilities_found" in response.output


class TestAgenteIntegracion:
    """Tests for Agente Integración (Integration) agent."""

    def test_agente_integracion_initialization(self):
        """Test Agente Integración initialization."""
        agent = AgenteIntegracion()
        
        assert agent.config.agent_type == AgentType.AGENTE_INTEGRACION
        assert agent.config.agent_id == "integracion-001"

    def test_agente_integracion_execute(self):
        """Test Agente Integración execute returns results."""
        agent = AgenteIntegracion()
        state = {}
        
        response = agent.execute(state)
        
        assert response.status == AgentStatus.COMPLETED
        assert "tests_passed" in response.output


class TestElCerrador:
    """Tests for El Cerrador (Closer) agent."""

    def test_el_cerrador_initialization(self):
        """Test El Cerrador initialization."""
        agent = ElCerrador()
        
        assert agent.config.agent_type == AgentType.EL_CERRADOR
        assert agent.config.agent_id == "cerrador-001"

    def test_el_cerrador_execute_certified(self):
        """Test El Cerrador execute with low failure rate."""
        agent = ElCerrador()
        state = {
            "sprint_id": "SP-45",
            "execution_results": {
                "functional": {"output": {"tests_passed": 95, "tests_failed": 2}},
                "performance": {"output": {"tests_passed": 50, "tests_failed": 0}}
            }
        }
        
        response = agent.execute(state)
        
        assert response.status == AgentStatus.COMPLETED
        assert response.output["certified"] is True

    def test_el_cerrador_execute_not_certified(self):
        """Test El Cerrador execute with high failure rate."""
        agent = ElCerrador()
        state = {
            "sprint_id": "SP-46",
            "execution_results": {
                "functional": {"output": {"tests_passed": 50, "tests_failed": 10}}
            }
        }
        
        response = agent.execute(state)
        
        assert response.status == AgentStatus.COMPLETED
        assert response.output["certified"] is False
