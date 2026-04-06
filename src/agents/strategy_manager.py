"""Strategy Manager for Metanoia-QA.

This agent receives Context Analyst output and applies ISTQB Defect Clustering
principles to calculate effort distribution across functional, regression,
performance, and security testing. It generates test plans with priorities
and coordinates with Design Lead.
"""

import logging
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class EffortDistribution(BaseModel):
    """Model for effort distribution across test types."""
    functional: float = Field(
        ..., ge=0.0, le=1.0,
        description="Percentage of effort for functional testing"
    )
    regression: float = Field(
        ..., ge=0.0, le=1.0,
        description="Percentage of effort for regression testing"
    )
    performance: float = Field(
        ..., ge=0.0, le=1.0,
        description="Percentage of effort for performance testing"
    )
    security: float = Field(
        ..., ge=0.0, le=1.0,
        description="Percentage of effort for security testing"
    )

    def validate_total(self) -> bool:
        """Validate that effort percentages sum to 1.0."""
        total = self.functional + self.regression + self.performance + self.security
        return abs(total - 1.0) < 0.01


class TestPriority(BaseModel):
    """Model for individual test priority."""
    test_id: str
    test_name: str
    priority: str = Field(..., pattern="^(critical|high|medium|low)$")
    test_type: str
    module: str
    reason: str


class TestPlan(BaseModel):
    """Complete test plan model."""
    plan_id: str
    sprint_goal: str
    effort_distribution: EffortDistribution
    total_test_cases: int
    prioritized_tests: list[TestPriority] = Field(default_factory=list)
    phased_approach: list[dict[str, Any]] = Field(default_factory=list)
    resource_requirements: dict[str, int] = Field(default_factory=dict)
    risk_mitigations: list[str] = Field(default_factory=list)


class StrategyManager:
    """Agent for creating test strategies based on context analysis.

    Receives Context Analyst output and applies ISTQB Defect Clustering
    principle (80% of defects cluster in 20% of modules) to calculate
    effort distribution and generate prioritized test plans.

    Attributes:
        context_analyst: ContextAnalyst instance for historical data.
    """

    def __init__(self, context_analyst: Any | None = None):
        """Initialize the Strategy Manager.

        Args:
            context_analyst: Optional ContextAnalyst instance for coordination.
        """
        self.context_analyst = context_analyst
        self._defect_clustering_weight = 0.8
        self._module_focus_percentage = 0.2

    def _apply_defect_clustering(
        self,
        context: dict[str, Any]
    ) -> dict[str, float]:
        """Apply ISTQB Defect Clustering principle to focus testing.

        The principle states that 80% of defects are found in 20% of modules.
        This method identifies high-risk modules and adjusts focus accordingly.

        Args:
            context: Context analysis results.

        Returns:
            Dictionary of module focus weights.
        """
        module_risks = context.get("module_risks", [])
        module_weights: dict[str, float] = {}

        high_risk_modules = [
            m for m in module_risks
            if m.get("risk_level") in ("high", "critical")
        ]

        if not high_risk_modules:
            for module_data in module_risks:
                module_weights[module_data["module_name"]] = 0.5
        else:
            critical_weight = 0.8 / max(len(high_risk_modules), 1)
            remaining_weight = 0.2 / max(len(module_risks) - len(high_risk_modules), 1)

            for module_data in module_risks:
                if module_data["risk_level"] in ("high", "critical"):
                    module_weights[module_data["module_name"]] = critical_weight
                else:
                    module_weights[module_data["module_name"]] = remaining_weight

        return module_weights

    def _calculate_effort_distribution(
        self,
        context: dict[str, Any],
        sprint_goal: str
    ) -> EffortDistribution:
        """Calculate effort distribution across test types.

        Uses context analysis (risk level, defect density, flaky tests) and
        sprint goal to determine optimal effort allocation.

        Args:
            context: Context analysis results.
            sprint_goal: Sprint goal description.

        Returns:
            EffortDistribution with percentages for each test type.
        """
        risk_level = context.get("risk_level", "medium")
        context.get("risk_score", 0.5)
        flaky_test_count = len(context.get("flaky_tests", []))
        module_risks = context.get("module_risks", [])

        sprint_goal_lower = sprint_goal.lower()
        is_performance_focus = any(
            keyword in sprint_goal_lower
            for keyword in ["performance", "load", "scalability", "stress"]
        )
        is_security_focus = any(
            keyword in sprint_goal_lower
            for keyword in ["security", "auth", "permission", "access", "privacy"]
        )
        is_new_feature = any(
            keyword in sprint_goal_lower
            for keyword in ["new", "add", "implement", "create", "feature"]
        )
        is_refactor = any(
            keyword in sprint_goal_lower
            for keyword in ["refactor", "redesign", "optimize", "improve"]
        )

        functional_base = 0.4
        regression_base = 0.3
        performance_base = 0.15
        security_base = 0.15

        if risk_level == "critical":
            functional_base = 0.25
            regression_base = 0.45
            performance_base = 0.1
            security_base = 0.2
        elif risk_level == "high":
            functional_base = 0.3
            regression_base = 0.4
            performance_base = 0.1
            security_base = 0.2
        elif risk_level == "low":
            functional_base = 0.45
            regression_base = 0.2
            performance_base = 0.2
            security_base = 0.15

        if flaky_test_count > 5:
            regression_base += 0.1
            functional_base -= 0.1

        high_defect_modules = sum(
            1 for m in module_risks if m.get("risk_level") in ("high", "critical")
        )
        if high_defect_modules > 2:
            security_base += 0.05
            functional_base -= 0.05

        if is_performance_focus:
            performance_base = 0.35
            functional_base = 0.25
            regression_base = 0.2
            security_base = 0.2

        if is_security_focus:
            security_base = 0.35
            performance_base = 0.15
            functional_base = 0.3
            regression_base = 0.2

        if is_new_feature:
            functional_base += 0.15
            regression_base -= 0.1
            performance_base -= 0.05

        if is_refactor:
            regression_base += 0.2
            functional_base -= 0.1
            performance_base -= 0.1

        functional_base = max(0.1, min(0.6, functional_base))
        regression_base = max(0.1, min(0.5, regression_base))
        performance_base = max(0.05, min(0.35, performance_base))
        security_base = max(0.05, min(0.35, security_base))

        total = functional_base + regression_base + performance_base + security_base
        scale = 1.0 / total

        return EffortDistribution(
            functional=round(functional_base * scale, 2),
            regression=round(regression_base * scale, 2),
            performance=round(performance_base * scale, 2),
            security=round(security_base * scale, 2)
        )

    def _prioritize_tests(
        self,
        context: dict[str, Any],
        effort: EffortDistribution,
        sprint_goal: str
    ) -> list[TestPriority]:
        """Generate prioritized test list based on context and effort.

        Args:
            context: Context analysis results.
            effort: Calculated effort distribution.
            sprint_goal: Sprint goal description.

        Returns:
            List of prioritized tests.
        """
        prioritized = []

        module_risks = context.get("module_risks", [])
        flaky_tests = context.get("flaky_tests", [])
        similar_sprints = context.get("similar_sprints", [])

        sprint_goal_lower = sprint_goal.lower()

        if module_risks:
            high_risk_modules = [
                m["module_name"] for m in module_risks
                if m.get("risk_level") in ("high", "critical")
            ]

            for module in high_risk_modules:
                prioritized.append(TestPriority(
                    test_id=f"CRITICAL_{module}_01",
                    test_name=f"Critical path testing for {module}",
                    priority="critical",
                    test_type="functional",
                    module=module,
                    reason="Module has critical/high risk level with elevated defect density"
                ))

            for i, module_data in enumerate(module_risks):
                if module_data.get("risk_level") == "medium":
                    prioritized.append(TestPriority(
                        test_id=f"HIGH_{module_data['module_name']}_01",
                        test_name=f"Regression suite for {module_data['module_name']}",
                        priority="high",
                        test_type="regression",
                        module=module_data["module_name"],
                        reason="Module shows moderate defect density"
                    ))

        for flaky in flaky_tests[:5]:
            prioritized.append(TestPriority(
                test_id=f"MEDIUM_FLAKY_{flaky['test_id']}",
                test_name=f"Investigate and fix flaky test: {flaky['test_name']}",
                priority="medium",
                test_type="regression",
                module=flaky["module"],
                reason=f"Test has {flaky['failure_rate']*100:.0f}% failure rate"
            ))

        if any(k in sprint_goal_lower for k in ["new", "add", "create"]):
            prioritized.append(TestPriority(
                test_id="HIGH_NEW_FEATURE_01",
                test_name="New feature end-to-end validation",
                priority="high",
                test_type="functional",
                module="new_feature",
                reason="New feature requires full E2E validation"
            ))

        if any(k in sprint_goal_lower for k in ["performance", "load", "scalability"]):
            prioritized.append(TestPriority(
                test_id="HIGH_PERF_01",
                test_name="Load and stress testing",
                priority="high",
                test_type="performance",
                module="system",
                reason="Performance testing required per sprint goal"
            ))

        if any(k in sprint_goal_lower for k in ["security", "auth", "permission"]):
            prioritized.append(TestPriority(
                test_id="HIGH_SEC_01",
                test_name="Security vulnerability assessment",
                priority="high",
                test_type="security",
                module="system",
                reason="Security focus identified in sprint goal"
            ))

        for sprint in similar_sprints[:2]:
            for i, module in enumerate(sprint.get("shared_modules", [])[:3]):
                prioritized.append(TestPriority(
                    test_id=f"MEDIUM_REUSE_{sprint['sprint_id']}_{i}",
                    test_name=f"Reuse tests from sprint {sprint['sprint_id']}",
                    priority="medium",
                    test_type="regression",
                    module=module,
                    reason=f"Similarity score {sprint['similarity_score']:.2f} with historical sprint"
                ))

        return prioritized

    def _create_phased_approach(
        self,
        effort: EffortDistribution,
        sprint_goal: str
    ) -> list[dict[str, Any]]:
        """Create a phased testing approach for sprint execution.

        Args:
            effort: Effort distribution across test types.
            sprint_goal: Sprint goal description.

        Returns:
            List of phases with timing and focus areas.
        """
        phases = []

        phases.append({
            "phase": 1,
            "name": "Rapid Sanity",
            "duration_percentage": 10,
            "focus": ["critical_tests", "smoke_testing"],
            "test_types": ["functional"],
            "entry_criteria": ["Build successful", "Core functionality intact"],
            "exit_criteria": ["Critical paths working", "No blocker defects"]
        })

        phases.append({
            "phase": 2,
            "name": "Functional Deep Dive",
            "duration_percentage": int(effort.functional * 40),
            "focus": ["new_features", "changed_modules"],
            "test_types": ["functional"],
            "entry_criteria": ["Sanity tests passed", "Test environment ready"],
            "exit_criteria": ["All functional tests passing", "Code coverage targets met"]
        })

        phases.append({
            "phase": 3,
            "name": "Regression Suite",
            "duration_percentage": int(effort.regression * 40),
            "focus": ["existing_functionality", "integration_points"],
            "test_types": ["regression"],
            "entry_criteria": ["Functional tests stable", "Test data prepared"],
            "exit_criteria": ["Regression suite complete", "No high-severity regressions"]
        })

        if effort.performance > 0.1:
            phases.append({
                "phase": 4,
                "name": "Performance Testing",
                "duration_percentage": int(effort.performance * 30),
                "focus": ["load_testing", "stress_testing", "scalability"],
                "test_types": ["performance"],
                "entry_criteria": ["System stable", "Performance requirements defined"],
                "exit_criteria": ["Performance targets met", "No bottlenecks identified"]
            })

        if effort.security > 0.1:
            phases.append({
                "phase": 5,
                "name": "Security Assessment",
                "duration_percentage": int(effort.security * 30),
                "focus": ["vulnerability_scanning", "penetration_testing"],
                "test_types": ["security"],
                "entry_criteria": ["Functional testing complete", "Security test plan approved"],
                "exit_criteria": ["No critical/high vulnerabilities", "Security report generated"]
            })

        phases.append({
            "phase": 6,
            "name": "Final Verification",
            "duration_percentage": 10,
            "focus": ["final_smoke", "signoff"],
            "test_types": ["functional", "regression"],
            "entry_criteria": ["All test phases complete", "Defects resolved"],
            "exit_criteria": ["All critical tests passing", "Ready for release"]
        })

        return phases

    def _calculate_resource_requirements(
        self,
        effort: EffortDistribution,
        test_count: int
    ) -> dict[str, int]:
        """Calculate resource requirements for the test plan.

        Args:
            effort: Effort distribution across test types.
            test_count: Total number of test cases.

        Returns:
            Dictionary of resource requirements.
        """
        return {
            "qa_engineers": max(2, int(effort.functional * 4)),
            "automation_engineers": max(1, int(effort.regression * 2)),
            "performance_testers": max(1, int(effort.performance * 2)),
            "security_testers": max(1, int(effort.security * 2)),
            "test_environments": 3,
            "estimated_test_cases": test_count,
            "test_data_preparation_hours": int(test_count * 0.5)
        }

    async def create_test_plan(
        self,
        sprint_goal: str,
        context: dict[str, Any]
    ) -> dict[str, Any]:
        """Create a comprehensive test plan based on context analysis.

        Receives Context Analyst output and applies ISTQB Defect Clustering
        principle to calculate effort distribution across functional,
        regression, performance, and security testing. Generates a prioritized
        test plan with phased approach.

        Args:
            sprint_goal: Description of sprint goal.
            context: Context analysis results from ContextAnalyst.

        Returns:
            Dictionary containing:
                - plan_id: Unique identifier for the plan
                - sprint_goal: Original sprint goal
                - effort_distribution: Effort percentages per test type
                - total_test_cases: Estimated total test cases
                - prioritized_tests: List of prioritized tests
                - phased_approach: Execution phases with timing
                - resource_requirements: Required resources
                - risk_mitigations: Risk mitigation strategies
        """
        import uuid

        logger.info(f"Creating test plan for sprint: {sprint_goal[:100]}...")

        effort_distribution = self._calculate_effort_distribution(context, sprint_goal)

        if not effort_distribution.validate_total():
            logger.warning("Effort distribution does not sum to 1.0, normalizing")
            total = (
                effort_distribution.functional +
                effort_distribution.regression +
                effort_distribution.performance +
                effort_distribution.security
            )
            scale = 1.0 / total
            effort_distribution = EffortDistribution(
                functional=effort_distribution.functional * scale,
                regression=effort_distribution.regression * scale,
                performance=effort_distribution.performance * scale,
                security=effort_distribution.security * scale
            )

        self._apply_defect_clustering(context)

        prioritized_tests = self._prioritize_tests(
            context, effort_distribution, sprint_goal
        )

        phased_approach = self._create_phased_approach(effort_distribution, sprint_goal)

        base_test_count = 50
        risk_multiplier = 1.0 + (context.get("risk_score", 0.5) * 0.5)
        effort_multiplier = context.get("effort_multiplier", 1.0)
        total_test_cases = int(base_test_count * risk_multiplier * effort_multiplier)

        resource_requirements = self._calculate_resource_requirements(
            effort_distribution, total_test_cases
        )

        risk_mitigations = []
        if context.get("flaky_tests"):
            risk_mitigations.append(
                f"Address {len(context['flaky_tests'])} flaky tests in test automation "
                "before sprint execution to avoid false failures"
            )

        high_risk_modules = [
            m["module_name"] for m in context.get("module_risks", [])
            if m.get("risk_level") in ("high", "critical")
        ]
        if high_risk_modules:
            risk_mitigations.append(
                f"Focus additional review on high-risk modules: {', '.join(high_risk_modules)}. "
                "Apply ISTQB defect clustering - 80% of defects likely here."
            )

        if context.get("similar_sprints"):
            risk_mitigations.append(
                "Leverage historical test cases from similar sprints to reduce "
                "test design effort and improve coverage"
            )

        risk_mitigations.append(
            f"Apply {effort_distribution.regression*100:.0f}% regression effort "
            "to catch defects early in the sprint"
        )

        test_plan = TestPlan(
            plan_id=str(uuid.uuid4())[:8],
            sprint_goal=sprint_goal,
            effort_distribution=effort_distribution,
            total_test_cases=total_test_cases,
            prioritized_tests=prioritized_tests,
            phased_approach=phased_approach,
            resource_requirements=resource_requirements,
            risk_mitigations=risk_mitigations
        )

        logger.info(f"Test plan created: {test_plan.plan_id}")

        return test_plan.model_dump()
