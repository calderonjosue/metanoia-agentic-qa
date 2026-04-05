"""Tests for StrategyManager agent."""

import pytest

from src.agents.strategy_manager import (
    EffortDistribution,
    StrategyManager,
    TestPriority,
)


class TestEffortDistribution:
    """Tests for EffortDistribution model."""

    def test_effort_distribution_creation(self):
        """Test creating EffortDistribution."""
        effort = EffortDistribution(
            functional=0.4,
            regression=0.3,
            performance=0.15,
            security=0.15
        )

        assert effort.functional == 0.4
        assert effort.regression == 0.3
        assert effort.performance == 0.15
        assert effort.security == 0.15

    def test_effort_distribution_validate_total(self):
        """Test validate_total method."""
        effort = EffortDistribution(
            functional=0.4,
            regression=0.3,
            performance=0.15,
            security=0.15
        )

        assert effort.validate_total() is True

    def test_effort_distribution_invalid_total(self):
        """Test validate_total fails with invalid total."""
        effort = EffortDistribution(
            functional=0.5,
            regression=0.5,
            performance=0.0,
            security=0.0
        )

        assert effort.validate_total() is False


class TestTestPriority:
    """Tests for TestPriority model."""

    def test_test_priority_creation(self):
        """Test creating TestPriority."""
        priority = TestPriority(
            test_id="TEST-001",
            test_name="Login Test",
            priority="high",
            test_type="functional",
            module="auth",
            reason="Security critical"
        )

        assert priority.test_id == "TEST-001"
        assert priority.priority == "high"

    def test_test_priority_invalid_priority(self):
        """Test TestPriority rejects invalid priority."""
        with pytest.raises(ValueError):
            TestPriority(
                test_id="TEST-001",
                test_name="Test",
                priority="urgent",
                test_type="functional",
                module="auth",
                reason="test"
            )


class TestStrategyManager:
    """Tests for StrategyManager agent."""

    @pytest.fixture
    def strategy_manager(self):
        """Create StrategyManager instance."""
        return StrategyManager(context_analyst=None)

    @pytest.fixture
    def sample_context(self):
        """Create sample context analysis result."""
        return {
            "risk_level": "medium",
            "risk_score": 0.45,
            "flaky_tests": [
                {"test_id": "T1", "test_name": "Flaky Test 1", "module": "auth", "failure_rate": 0.15},
                {"test_id": "T2", "test_name": "Flaky Test 2", "module": "payment", "failure_rate": 0.20},
            ],
            "module_risks": [
                {
                    "module_name": "payment",
                    "defect_density": 0.35,
                    "change_frequency": 0.6,
                    "test_coverage": 0.7,
                    "risk_level": "high",
                    "recommendations": []
                },
                {
                    "module_name": "auth",
                    "defect_density": 0.15,
                    "change_frequency": 0.3,
                    "test_coverage": 0.8,
                    "risk_level": "medium",
                    "recommendations": []
                }
            ],
            "similar_sprints": [
                {
                    "sprint_id": "SP-40",
                    "similarity_score": 0.75,
                    "shared_modules": ["payment"]
                }
            ],
            "effort_multiplier": 1.2
        }

    def test_strategy_manager_initialization(self, strategy_manager):
        """Test StrategyManager initializes correctly."""
        assert strategy_manager.context_analyst is None
        assert strategy_manager._defect_clustering_weight == 0.8
        assert strategy_manager._module_focus_percentage == 0.2

    def test_apply_defect_clustering_high_risk(self, strategy_manager, sample_context):
        """Test defect clustering focuses on high-risk modules."""
        weights = strategy_manager._apply_defect_clustering(sample_context)

        assert "payment" in weights
        assert weights["payment"] > weights.get("auth", 0)

    def test_apply_defect_clustering_no_high_risk(self, strategy_manager):
        """Test defect clustering with no high-risk modules."""
        context = {
            "module_risks": [
                {"module_name": "logging", "risk_level": "low"},
                {"module_name": "ui", "risk_level": "low"}
            ]
        }

        weights = strategy_manager._apply_defect_clustering(context)

        assert all(w == 0.5 for w in weights.values())

    def test_calculate_effort_distribution_critical_risk(self, strategy_manager):
        """Test effort distribution for critical risk level."""
        context = {
            "risk_level": "critical",
            "risk_score": 0.8,
            "flaky_tests": [],
            "module_risks": []
        }

        effort = strategy_manager._calculate_effort_distribution(context, "critical sprint")

        assert effort.regression > effort.functional
        assert effort.security >= 0.1

    def test_calculate_effort_distribution_low_risk(self, strategy_manager):
        """Test effort distribution for low risk level."""
        context = {
            "risk_level": "low",
            "risk_score": 0.2,
            "flaky_tests": [],
            "module_risks": []
        }

        effort = strategy_manager._calculate_effort_distribution(context, "simple fix")

        assert effort.functional > effort.regression

    def test_calculate_effort_distribution_performance_focus(self, strategy_manager):
        """Test effort distribution for performance-focused sprint."""
        context = {
            "risk_level": "medium",
            "risk_score": 0.5,
            "flaky_tests": [],
            "module_risks": []
        }

        effort = strategy_manager._calculate_effort_distribution(
            context, "Improve performance and load handling"
        )

        assert effort.performance >= 0.3

    def test_calculate_effort_distribution_security_focus(self, strategy_manager):
        """Test effort distribution for security-focused sprint."""
        context = {
            "risk_level": "medium",
            "risk_score": 0.5,
            "flaky_tests": [],
            "module_risks": []
        }

        effort = strategy_manager._calculate_effort_distribution(
            context, "Implement authentication and authorization"
        )

        assert effort.security >= 0.3

    def test_calculate_effort_distribution_new_feature(self, strategy_manager):
        """Test effort distribution for new feature sprint."""
        context = {
            "risk_level": "medium",
            "risk_score": 0.5,
            "flaky_tests": [],
            "module_risks": []
        }

        effort = strategy_manager._calculate_effort_distribution(
            context, "Add new payment method"
        )

        assert effort.functional >= 0.3

    def test_calculate_effort_distribution_refactor(self, strategy_manager):
        """Test effort distribution for refactor sprint."""
        context = {
            "risk_level": "medium",
            "risk_score": 0.5,
            "flaky_tests": [],
            "module_risks": []
        }

        effort = strategy_manager._calculate_effort_distribution(
            context, "Refactor authentication module"
        )

        assert effort.regression >= 0.3

    def test_calculate_effort_distribution_flaky_tests(self, strategy_manager):
        """Test effort distribution adjusts for flaky tests."""
        context = {
            "risk_level": "medium",
            "risk_score": 0.5,
            "flaky_tests": [{"test_id": f"T{i}", "failure_rate": 0.2} for i in range(7)],
            "module_risks": []
        }

        effort = strategy_manager._calculate_effort_distribution(context, "sprint")

        assert effort.regression >= 0.4

    def test_calculate_effort_distribution_effort_valid(self, strategy_manager):
        """Test effort distribution values are valid."""
        context = {
            "risk_level": "high",
            "risk_score": 0.6,
            "flaky_tests": [],
            "module_risks": [
                {"module_name": "m1", "risk_level": "high"},
                {"module_name": "m2", "risk_level": "high"}
            ]
        }

        effort = strategy_manager._calculate_effort_distribution(context, "test")

        assert 0.1 <= effort.functional <= 0.6
        assert 0.1 <= effort.regression <= 0.5
        assert 0.05 <= effort.performance <= 0.35
        assert 0.05 <= effort.security <= 0.35

    def test_prioritize_tests_high_risk_modules(self, strategy_manager, sample_context):
        """Test prioritization includes high-risk modules."""
        effort = EffortDistribution(
            functional=0.4, regression=0.3, performance=0.15, security=0.15
        )

        priorities = strategy_manager._prioritize_tests(
            sample_context, effort, "test sprint"
        )

        assert any(p.priority == "critical" for p in priorities)
        assert any("payment" in p.module.lower() for p in priorities)

    def test_prioritize_tests_flaky_tests(self, strategy_manager, sample_context):
        """Test prioritization includes flaky tests."""
        effort = EffortDistribution(
            functional=0.4, regression=0.3, performance=0.15, security=0.15
        )

        priorities = strategy_manager._prioritize_tests(
            sample_context, effort, "test sprint"
        )

        assert any("flaky" in p.test_name.lower() for p in priorities)

    def test_prioritize_tests_new_feature(self, strategy_manager):
        """Test prioritization for new feature sprint."""
        context = {"module_risks": [], "flaky_tests": [], "similar_sprints": []}
        effort = EffortDistribution(
            functional=0.4, regression=0.3, performance=0.15, security=0.15
        )

        priorities = strategy_manager._prioritize_tests(
            context, effort, "Add new checkout feature"
        )

        assert any("new feature" in p.test_name.lower() for p in priorities)

    def test_prioritize_tests_performance(self, strategy_manager):
        """Test prioritization for performance sprint."""
        context = {"module_risks": [], "flaky_tests": [], "similar_sprints": []}
        effort = EffortDistribution(
            functional=0.4, regression=0.3, performance=0.15, security=0.15
        )

        priorities = strategy_manager._prioritize_tests(
            context, effort, "Performance optimization sprint"
        )

        assert any("performance" in p.test_name.lower() for p in priorities)

    def test_prioritize_tests_security(self, strategy_manager):
        """Test prioritization for security sprint."""
        context = {"module_risks": [], "flaky_tests": [], "similar_sprints": []}
        effort = EffortDistribution(
            functional=0.4, regression=0.3, performance=0.15, security=0.15
        )

        priorities = strategy_manager._prioritize_tests(
            context, effort, "Security hardening sprint"
        )

        assert any("security" in p.test_name.lower() for p in priorities)

    def test_create_phased_approach(self, strategy_manager):
        """Test phased approach creation."""
        effort = EffortDistribution(
            functional=0.4, regression=0.3, performance=0.15, security=0.15
        )

        phases = strategy_manager._create_phased_approach(effort, "test sprint")

        assert len(phases) >= 4
        assert any(p["name"] == "Rapid Sanity" for p in phases)
        assert any(p["name"] == "Final Verification" for p in phases)

    def test_create_phased_approach_no_performance(self, strategy_manager):
        """Test phased approach without performance phase."""
        effort = EffortDistribution(
            functional=0.5, regression=0.4, performance=0.05, security=0.05
        )

        phases = strategy_manager._create_phased_approach(effort, "test sprint")

        assert not any(p["name"] == "Performance Testing" for p in phases)

    def test_calculate_resource_requirements(self, strategy_manager):
        """Test resource requirements calculation."""
        effort = EffortDistribution(
            functional=0.4, regression=0.3, performance=0.15, security=0.15
        )

        resources = strategy_manager._calculate_resource_requirements(effort, 100)

        assert "qa_engineers" in resources
        assert "test_environments" in resources
        assert resources["test_environments"] == 3

    @pytest.mark.asyncio
    async def test_create_test_plan_returns_complete_plan(self, strategy_manager, sample_context):
        """Test create_test_plan returns complete plan."""
        plan = await strategy_manager.create_test_plan(
            sprint_goal="Implement checkout flow",
            context=sample_context
        )

        assert "plan_id" in plan
        assert "sprint_goal" in plan
        assert "effort_distribution" in plan
        assert "total_test_cases" in plan
        assert "prioritized_tests" in plan
        assert "phased_approach" in plan
        assert "resource_requirements" in plan
        assert "risk_mitigations" in plan

    @pytest.mark.asyncio
    async def test_create_test_plan_total_cases_calculation(self, strategy_manager, sample_context):
        """Test total test cases calculated correctly."""
        plan = await strategy_manager.create_test_plan(
            sprint_goal="Test sprint",
            context=sample_context
        )

        base = 50
        risk_mult = 1.0 + (sample_context["risk_score"] * 0.5)
        effort_mult = sample_context["effort_multiplier"]
        expected = int(base * risk_mult * effort_mult)

        assert plan["total_test_cases"] == expected

    @pytest.mark.asyncio
    async def test_create_test_plan_risk_mitigations(self, strategy_manager, sample_context):
        """Test risk mitigations are generated."""
        plan = await strategy_manager.create_test_plan(
            sprint_goal="Test sprint",
            context=sample_context
        )

        assert len(plan["risk_mitigations"]) > 0

    @pytest.mark.asyncio
    async def test_create_test_plan_effort_distribution_validates(self, strategy_manager):
        """Test effort distribution sums to 1.0 after creation."""
        context = {
            "risk_level": "high",
            "risk_score": 0.6,
            "flaky_tests": [{"test_id": "T1", "failure_rate": 0.2}] * 6,
            "module_risks": [
                {"module_name": "m1", "risk_level": "high"},
                {"module_name": "m2", "risk_level": "high"}
            ],
            "effort_multiplier": 1.0
        }

        plan = await strategy_manager.create_test_plan("Test", context)
        effort = plan["effort_distribution"]
        total = effort["functional"] + effort["regression"] + effort["performance"] + effort["security"]

        assert abs(total - 1.0) < 0.01
