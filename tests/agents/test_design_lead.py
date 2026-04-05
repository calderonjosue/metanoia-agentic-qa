"""Tests for DesignLead agent."""

import pytest
from unittest.mock import AsyncMock, Mock

from src.agents.design_lead import (
    TestDesignLead,
    TestScenario,
    TestCase,
    TestEnvironment,
)


class TestTestScenario:
    """Tests for TestScenario model."""

    def test_test_scenario_creation(self):
        """Test creating TestScenario."""
        scenario = TestScenario(
            scenario_id="SCEN_001",
            scenario_name="Login Test",
            description="Test user login functionality",
            preconditions=["User registered", "Browser open"],
            test_steps=["Navigate to login", "Enter credentials", "Click submit"],
            expected_results=["Login successful", "Redirect to dashboard"],
            happy_path=True,
            edge_cases=[]
        )
        
        assert scenario.scenario_id == "SCEN_001"
        assert scenario.happy_path is True
        assert len(scenario.test_steps) == 3


class TestTestCase:
    """Tests for TestCase model."""

    def test_test_case_creation(self):
        """Test creating TestCase."""
        test_case = TestCase(
            case_id="TC_001",
            case_name="Login Success",
            scenario_id="SCEN_001",
            module="auth",
            test_type="functional",
            priority="high",
            prerequisites=["User exists"],
            test_data={"username": "test", "password": "pass123"},
            steps=[{"step_number": "1", "action": "Enter credentials", "expected": "Fields filled"}],
            assertions=["User logged in"],
            tags=["smoke", "auth"]
        )
        
        assert test_case.priority == "high"
        assert test_case.module == "auth"

    def test_test_case_priority_validation(self):
        """Test TestCase validates priority."""
        with pytest.raises(ValueError):
            TestCase(
                case_id="TC_001",
                case_name="Test",
                scenario_id="SCEN_001",
                module="auth",
                test_type="functional",
                priority="urgent",
                prerequisites=[],
                test_data={},
                steps=[],
                assertions=[],
                tags=[]
            )


class TestTestEnvironment:
    """Tests for TestEnvironment model."""

    def test_test_environment_creation(self):
        """Test creating TestEnvironment."""
        env = TestEnvironment(
            environment_id="ENV_001",
            name="Staging Environment",
            type="staging",
            configuration={"url": "https://staging.example.com"},
            required_services=["api", "database"],
            network_config={"vpc": "vpc-123"},
            secrets_required=["api_key"]
        )
        
        assert env.type == "staging"
        assert len(env.required_services) == 2

    def test_test_environment_type_validation(self):
        """Test TestEnvironment validates type."""
        with pytest.raises(ValueError):
            TestEnvironment(
                environment_id="ENV_001",
                name="Test",
                type="invalid",
                configuration={},
                required_services=[],
                network_config={},
                secrets_required=[]
            )


class TestTestDesignLead:
    """Tests for TestDesignLead agent."""

    @pytest.fixture
    def mock_gemini(self):
        """Create mock Gemini client."""
        mock = AsyncMock()
        mock.generate_content = AsyncMock(return_value=Mock(
            text='[{"case_name": "Empty input", "case_type": "boundary", "trigger_condition": "Input is empty", "expected_behavior": "Show error"}]'
        ))
        return mock

    @pytest.fixture
    def design_lead(self, mock_gemini):
        """Create TestDesignLead instance."""
        return TestDesignLead(gemini_client=mock_gemini)

    @pytest.fixture
    def design_lead_no_llm(self):
        """Create TestDesignLead without LLM."""
        return TestDesignLead(gemini_client=None)

    @pytest.fixture
    def sample_test_plan(self):
        """Create sample test plan."""
        return {
            "prioritized_tests": [
                {
                    "test_id": "HIGH_auth_01",
                    "test_name": "User authentication",
                    "test_type": "functional",
                    "module": "auth",
                    "priority": "high"
                },
                {
                    "test_id": "HIGH_payment_01",
                    "test_name": "Payment processing",
                    "test_type": "functional",
                    "module": "payment",
                    "priority": "high"
                },
                {
                    "test_id": "MEDIUM_regression_01",
                    "test_name": "Existing user flow",
                    "test_type": "regression",
                    "module": "user",
                    "priority": "medium"
                }
            ],
            "total_test_cases": 50,
            "effort_distribution": {
                "functional": 0.4,
                "regression": 0.3,
                "performance": 0.15,
                "security": 0.15
            }
        }

    def test_design_lead_initialization(self, design_lead):
        """Test DesignLead initializes correctly."""
        assert design_lead.gemini_client is not None
        assert len(design_lead._default_environment_types) == 4

    def test_design_lead_initialization_no_llm(self, design_lead_no_llm):
        """Test DesignLead initializes without LLM."""
        assert design_lead_no_llm.gemini_client is None

    def test_generate_default_edge_cases(self, design_lead_no_llm):
        """Test default edge case generation."""
        scenario = TestScenario(
            scenario_id="SCEN_test_01",
            scenario_name="Test Scenario",
            description="Test",
            preconditions=[],
            test_steps=[],
            expected_results=[],
            happy_path=True,
            edge_cases=[]
        )
        
        edge_cases = design_lead_no_llm._generate_default_edge_cases(scenario, "auth")
        
        assert len(edge_cases) == 4
        assert all("case_name" in ec for ec in edge_cases)
        assert all("case_type" in ec for ec in edge_cases)

    @pytest.mark.asyncio
    async def test_infer_edge_cases_llm(self, design_lead):
        """Test LLM edge case inference."""
        scenario = TestScenario(
            scenario_id="SCEN_test_01",
            scenario_name="Test Scenario",
            description="Test scenario",
            preconditions=[],
            test_steps=[],
            expected_results=[],
            happy_path=True,
            edge_cases=[]
        )
        
        edge_cases = await design_lead._infer_edge_cases_llm(scenario, "auth")
        
        assert len(edge_cases) > 0
        assert edge_cases[0]["case_type"] == "boundary"

    @pytest.mark.asyncio
    async def test_infer_edge_cases_llm_fallback(self, design_lead_no_llm):
        """Test LLM fallback when no client."""
        scenario = TestScenario(
            scenario_id="SCEN_test_01",
            scenario_name="Test",
            description="Test",
            preconditions=[],
            test_steps=[],
            expected_results=[],
            happy_path=True,
            edge_cases=[]
        )
        
        edge_cases = await design_lead_no_llm._infer_edge_cases_llm(scenario, "auth")
        
        assert len(edge_cases) == 4

    @pytest.mark.asyncio
    async def test_generate_scenarios(self, design_lead, sample_test_plan):
        """Test scenario generation from test plan."""
        scenarios = await design_lead._generate_scenarios(
            sample_test_plan, "Implement authentication flow"
        )
        
        assert len(scenarios) > 0
        assert all(isinstance(s, TestScenario) for s in scenarios)

    @pytest.mark.asyncio
    async def test_generate_scenarios_includes_edge_cases(self, design_lead, sample_test_plan):
        """Test scenarios include edge cases."""
        scenarios = await design_lead._generate_scenarios(
            sample_test_plan, "Test sprint"
        )
        
        assert all(len(s.edge_cases) > 0 for s in scenarios[:3])

    @pytest.mark.asyncio
    async def test_generate_scenarios_performance_sprint(self, design_lead, sample_test_plan):
        """Test scenarios include performance scenario for performance sprint."""
        scenarios = await design_lead._generate_scenarios(
            sample_test_plan, "Performance and load testing sprint"
        )
        
        assert any("performance" in s.scenario_name.lower() for s in scenarios)

    def test_create_test_cases_from_scenarios(self, design_lead_no_llm):
        """Test test case creation from scenarios."""
        scenarios = [
            TestScenario(
                scenario_id="SCEN_AUTH_01",
                scenario_name="Login Test",
                description="Test login",
                preconditions=["User exists"],
                test_steps=["Enter credentials", "Submit"],
                expected_results=["Logged in"],
                happy_path=True,
                edge_cases=[
                    {
                        "case_name": "Invalid password",
                        "case_type": "negative",
                        "trigger_condition": "Wrong password",
                        "expected_behavior": "Show error",
                        "priority": "high"
                    }
                ]
            )
        ]
        
        test_cases = design_lead_no_llm._create_test_cases_from_scenarios(scenarios)
        
        assert len(test_cases) == 2
        assert any("happy" in tc.case_name.lower() for tc in test_cases)
        assert any("edge" in tc.case_name.lower() for tc in test_cases)

    def test_generate_test_data_for_scenario(self, design_lead_no_llm):
        """Test test data generation."""
        scenario = TestScenario(
            scenario_id="SCEN_USER_01",
            scenario_name="User Test",
            description="Test",
            preconditions=[],
            test_steps=[],
            expected_results=[],
            happy_path=True,
            edge_cases=[]
        )
        
        data = design_lead_no_llm._generate_test_data_for_scenario(scenario)
        
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_design_test_environment(self, design_lead_no_llm, sample_test_plan):
        """Test environment design."""
        env = design_lead_no_llm._design_test_environment(
            sample_test_plan, "Staging release sprint"
        )
        
        assert isinstance(env, TestEnvironment)
        assert env.type == "staging"
        assert len(env.required_services) > 0

    def test_design_test_environment_production(self, design_lead_no_llm, sample_test_plan):
        """Test environment design for production."""
        env = design_lead_no_llm._design_test_environment(
            sample_test_plan, "Production release sprint"
        )
        
        assert env.type == "production"

    def test_design_test_environment_performance(self, design_lead_no_llm, sample_test_plan):
        """Test environment includes performance services."""
        env = design_lead_no_llm._design_test_environment(
            sample_test_plan, "Performance testing sprint"
        )
        
        assert "load_balancer" in env.required_services
        assert "monitoring" in env.required_services

    def test_design_test_environment_security(self, design_lead_no_llm, sample_test_plan):
        """Test environment includes security services."""
        env = design_lead_no_llm._design_test_environment(
            sample_test_plan, "Security hardening sprint"
        )
        
        assert "identity_provider" in env.required_services
        assert "secret_manager" in env.required_services

    def test_generate_synthetic_data_templates(self, design_lead_no_llm):
        """Test synthetic data template generation."""
        scenarios = [
            TestScenario(
                scenario_id="SCEN_01",
                scenario_name="Test",
                description="Test",
                preconditions=[],
                test_steps=[],
                expected_results=[],
                happy_path=True,
                edge_cases=[]
            )
        ]
        
        templates = design_lead_no_llm._generate_synthetic_data_templates(scenarios)
        
        assert len(templates) == 5
        entity_types = [t.entity_type for t in templates]
        assert "user" in entity_types
        assert "order" in entity_types

    def test_calculate_coverage_metrics(self, design_lead_no_llm):
        """Test coverage metrics calculation."""
        scenarios = [
            TestScenario(
                scenario_id="SCEN_01",
                scenario_name="Test 1",
                description="Test",
                preconditions=[],
                test_steps=[],
                expected_results=[],
                happy_path=True,
                edge_cases=[]
            )
        ]
        test_cases = [
            TestCase(
                case_id="TC_01",
                case_name="Happy Path",
                scenario_id="SCEN_01",
                module="auth",
                test_type="functional",
                priority="high",
                prerequisites=[],
                test_data={},
                steps=[],
                assertions=[],
                tags=["happy_path", "SCEN_01"]
            ),
            TestCase(
                case_id="TC_02",
                case_name="Edge",
                scenario_id="SCEN_01",
                module="auth",
                test_type="functional",
                priority="medium",
                prerequisites=[],
                test_data={},
                steps=[],
                assertions=[],
                tags=["edge_case", "SCEN_01"]
            )
        ]
        
        metrics = design_lead_no_llm._calculate_coverage_metrics(scenarios, test_cases)
        
        assert "happy_path_coverage" in metrics
        assert "edge_case_coverage" in metrics
        assert "module_coverage" in metrics
        assert metrics["total_scenarios"] == 1
        assert metrics["total_test_cases"] == 2

    @pytest.mark.asyncio
    async def test_design_tests_returns_complete_result(self, design_lead, sample_test_plan):
        """Test design_tests returns complete result."""
        result = await design_lead.design_tests(
            sample_test_plan, "Implement authentication"
        )
        
        assert "scenarios" in result
        assert "test_cases" in result
        assert "environment" in result
        assert "synthetic_data" in result
        assert "design_rationale" in result
        assert "coverage_metrics" in result

    @pytest.mark.asyncio
    async def test_design_tests_generates_test_cases(self, design_lead, sample_test_plan):
        """Test design_tests generates test cases."""
        result = await design_lead.design_tests(
            sample_test_plan, "Test sprint"
        )
        
        assert len(result["test_cases"]) > 0
        assert all("case_id" in tc for tc in result["test_cases"])

    @pytest.mark.asyncio
    async def test_design_tests_environment_configured(self, design_lead, sample_test_plan):
        """Test design_tests configures environment."""
        result = await design_lead.design_tests(
            sample_test_plan, "Staging QA sprint"
        )
        
        assert result["environment"] is not None
        assert "environment_id" in result["environment"]
        assert "type" in result["environment"]

    @pytest.mark.asyncio
    async def test_design_tests_coverage_metrics(self, design_lead, sample_test_plan):
        """Test design_tests provides coverage metrics."""
        result = await design_lead.design_tests(
            sample_test_plan, "Test sprint"
        )
        
        metrics = result["coverage_metrics"]
        assert "total_scenarios" in metrics
        assert "total_test_cases" in metrics
        assert metrics["total_test_cases"] >= metrics["total_scenarios"]
