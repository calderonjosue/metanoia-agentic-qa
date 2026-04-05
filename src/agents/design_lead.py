"""Design Lead for Metanoia-QA.

This agent generates test scenarios, infers edge cases using LLM, creates
synthetic test data, designs test environment requirements, and outputs
test cases to execution agents.
"""

import logging
import uuid
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class TestScenario(BaseModel):
    """Model for a test scenario with happy path and edge cases."""
    scenario_id: str
    scenario_name: str
    description: str
    preconditions: list[str] = Field(default_factory=list)
    test_steps: list[str] = Field(default_factory=list)
    expected_results: list[str] = Field(default_factory=list)
    happy_path: bool = True
    edge_cases: list[dict[str, Any]] = Field(default_factory=list)


class TestCase(BaseModel):
    """Model for an individual test case."""
    case_id: str
    case_name: str
    scenario_id: str
    module: str
    test_type: str
    priority: str = Field(..., pattern="^(critical|high|medium|low)$")
    prerequisites: list[str] = Field(default_factory=list)
    test_data: dict[str, Any] = Field(default_factory=dict)
    steps: list[dict[str, str]] = Field(default_factory=list)
    assertions: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class TestEnvironment(BaseModel):
    """Model for test environment configuration."""
    environment_id: str
    name: str
    type: str = Field(..., pattern="^(dev|staging|uat|production)$")
    configuration: dict[str, Any] = Field(default_factory=dict)
    required_services: list[str] = Field(default_factory=list)
    network_config: dict[str, Any] = Field(default_factory=dict)
    secrets_required: list[str] = Field(default_factory=list)


class SyntheticDataTemplate(BaseModel):
    """Model for synthetic test data generation."""
    template_id: str
    entity_type: str
    fields: dict[str, str] = Field(default_factory=dict)
    generation_rules: dict[str, Any] = Field(default_factory=dict)
    constraints: list[str] = Field(default_factory=list)


class TestDesignResult(BaseModel):
    """Complete output from test design."""
    scenarios: list[TestScenario] = Field(default_factory=list)
    test_cases: list[TestCase] = Field(default_factory=list)
    environment: TestEnvironment | None = None
    synthetic_data: list[SyntheticDataTemplate] = Field(default_factory=list)
    design_rationale: str = ""
    coverage_metrics: dict[str, float] = Field(default_factory=dict)


class TestDesignLead:
    """Agent for designing test scenarios, cases, and environments.
    
    Generates test scenarios (happy paths), infers edge cases using LLM,
    creates synthetic test data, designs test environment requirements,
    and outputs test cases to execution agents.
    
    Attributes:
        gemini_client: Gemini client for LLM-based edge case inference.
    """

    def __init__(self, gemini_client: Any | None = None):
        """Initialize the Test Design Lead.
        
        Args:
            gemini_client: Optional Gemini client for LLM inference.
        """
        self.gemini_client = gemini_client
        self._default_environment_types = ["functional", "regression", "performance", "security"]

    async def _infer_edge_cases_llm(
        self,
        scenario: TestScenario,
        module: str
    ) -> list[dict[str, Any]]:
        """Use LLM to infer edge cases for a scenario.
        
        Args:
            scenario: The base test scenario.
            module: Module name for context.
            
        Returns:
            List of inferred edge cases with descriptions and approaches.
        """
        if self.gemini_client is None:
            return self._generate_default_edge_cases(scenario, module)
        
        try:
            prompt = f"""Analyze this test scenario and identify edge cases and boundary conditions.

Scenario: {scenario.scenario_name}
Description: {scenario.description}
Module: {module}

Based on ISTQB guidelines, identify:
1. Boundary value analysis cases (min, max, just inside, just outside)
2. Equivalence partition cases
3. Error guessing cases based on common defect patterns
4. Negative test cases

Return 3-5 specific edge cases with:
- case_name: descriptive name
- case_type: boundary|equivalence|error_guess|negative
- trigger_condition: what triggers this edge case
- expected_behavior: what should happen

Return as JSON array."""
            
            response = await self.gemini_client.generate_content(prompt)
            
            import json
            edge_cases = json.loads(response.text)
            
            return [
                {
                    "case_name": ec.get("case_name", "Unknown"),
                    "case_type": ec.get("case_type", "unknown"),
                    "trigger_condition": ec.get("trigger_condition", ""),
                    "expected_behavior": ec.get("expected_behavior", ""),
                    "priority": "high" if ec.get("case_type") in ["boundary", "negative"] else "medium"
                }
                for ec in edge_cases
            ]
            
        except Exception as e:
            logger.warning(f"LLM edge case inference failed: {e}")
            return self._generate_default_edge_cases(scenario, module)

    def _generate_default_edge_cases(
        self,
        scenario: TestScenario,
        module: str
    ) -> list[dict[str, Any]]:
        """Generate default edge cases without LLM.
        
        Args:
            scenario: The base test scenario.
            module: Module name for context.
            
        Returns:
            List of common edge cases.
        """
        edge_cases = [
            {
                "case_name": f"Empty {module} input",
                "case_type": "boundary",
                "trigger_condition": "Input is empty or null",
                "expected_behavior": "System handles gracefully with appropriate message",
                "priority": "high"
            },
            {
                "case_name": f"Maximum length input for {module}",
                "case_type": "boundary",
                "trigger_condition": "Input exceeds maximum character limit",
                "expected_behavior": "System truncates or rejects with validation message",
                "priority": "medium"
            },
            {
                "case_name": f"Special characters in {module}",
                "case_type": "equivalence",
                "trigger_condition": "Input contains special characters (!@#$%^&*)",
                "expected_behavior": "System handles or escapes special characters",
                "priority": "medium"
            },
            {
                "case_name": f"Concurrent access to {module}",
                "case_type": "error_guess",
                "trigger_condition": "Multiple users access same resource simultaneously",
                "expected_behavior": "System handles race conditions properly",
                "priority": "high"
            }
        ]
        
        return edge_cases

    async def _generate_scenarios(
        self,
        test_plan: dict[str, Any],
        sprint_goal: str
    ) -> list[TestScenario]:
        """Generate test scenarios from test plan.
        
        Args:
            test_plan: Test plan from StrategyManager.
            sprint_goal: Sprint goal description.
            
        Returns:
            List of generated test scenarios.
        """
        scenarios = []
        sprint_goal_lower = sprint_goal.lower()
        
        functional_tests = [
            t for t in test_plan.get("prioritized_tests", [])
            if t.get("test_type") == "functional"
        ]
        
        for i, test in enumerate(functional_tests[:5]):
            scenario_id = f"SCEN_{test.get('module', 'unknown')}_{i+1:02d}"
            
            scenario = TestScenario(
                scenario_id=scenario_id,
                scenario_name=test.get("test_name", f"Scenario for {test.get('module')}"),
                description=f"Validates {test.get('test_name')} meets acceptance criteria",
                preconditions=[
                    "Test environment is ready",
                    "Test data is prepared",
                    "User is authenticated"
                ],
                test_steps=[
                    f"Navigate to {test.get('module')} feature",
                    "Input valid test data",
                    "Submit the request",
                    "Verify response matches expected result"
                ],
                expected_results=[
                    "Operation completes successfully",
                    "Data is persisted correctly",
                    "UI reflects the changes"
                ],
                happy_path=True,
                edge_cases=[]
            )
            
            edge_cases = await self._infer_edge_cases_llm(scenario, test.get("module", ""))
            scenario.edge_cases = edge_cases
            
            scenarios.append(scenario)
        
        regression_tests = [
            t for t in test_plan.get("prioritized_tests", [])
            if t.get("test_type") == "regression"
        ]
        
        for i, test in enumerate(regression_tests[:3]):
            scenario_id = f"SCEN_REGR_{test.get('module', 'unknown')}_{i+1:02d}"
            
            scenario = TestScenario(
                scenario_id=scenario_id,
                scenario_name=f"Regression: {test.get('test_name')}",
                description=f"Ensures existing functionality in {test.get('module')} remains intact",
                preconditions=[
                    "Previous version baseline established",
                    "Regression test data available"
                ],
                test_steps=[
                    f"Execute regression test for {test.get('module')}",
                    "Capture test results",
                    "Compare with baseline"
                ],
                expected_results=[
                    "All regression tests pass",
                    "No functionality regression detected"
                ],
                happy_path=True,
                edge_cases=[]
            )
            
            scenarios.append(scenario)
        
        if any(k in sprint_goal_lower for k in ["performance", "load"]):
            scenario_id = "SCEN_PERF_01"
            scenarios.append(TestScenario(
                scenario_id=scenario_id,
                scenario_name="Performance Benchmark Scenario",
                description="Validates system meets performance criteria under load",
                preconditions=[
                    "Load testing tools configured",
                    "Performance thresholds defined",
                    "Test environment matches production specs"
                ],
                test_steps=[
                    "Establish baseline performance metrics",
                    "Execute load test with expected user volume",
                    "Monitor response times and throughput",
                    "Collect performance data"
                ],
                expected_results=[
                    "Response time < 2 seconds for 95th percentile",
                    "System handles expected concurrent users",
                    "No resource exhaustion or crashes"
                ],
                happy_path=True,
                edge_cases=[]
            ))
        
        return scenarios

    def _create_test_cases_from_scenarios(
        self,
        scenarios: list[TestScenario]
    ) -> list[TestCase]:
        """Create detailed test cases from scenarios.
        
        Args:
            scenarios: List of test scenarios.
            
        Returns:
            List of detailed test cases.
        """
        test_cases = []
        
        for scenario in scenarios:
            case_id = f"TC_{scenario.scenario_id}_01"
            
            test_case = TestCase(
                case_id=case_id,
                case_name=f"Happy Path: {scenario.scenario_name}",
                scenario_id=scenario.scenario_id,
                module=scenario.scenario_id.split("_")[1] if "_" in scenario.scenario_id else "unknown",
                test_type="functional",
                priority="high",
                prerequisites=scenario.preconditions,
                test_data=self._generate_test_data_for_scenario(scenario),
                steps=[
                    {"step_number": str(i+1), "action": step, "expected": result}
                    for i, (step, result) in enumerate(zip(
                        scenario.test_steps,
                        scenario.expected_results
                    ))
                ],
                assertions=[
                    f"Verify: {result}" for result in scenario.expected_results
                ],
                tags=["happy_path", scenario.scenario_id]
            )
            test_cases.append(test_case)
            
            for edge in scenario.edge_cases:
                edge_case_id = f"TC_{scenario.scenario_id}_EDGE_{len(test_cases) + 1:02d}"
                
                edge_case = TestCase(
                    case_id=edge_case_id,
                    case_name=f"Edge: {edge.get('case_name', 'Unknown')}",
                    scenario_id=scenario.scenario_id,
                    module=test_case.module,
                    test_type="functional",
                    priority=edge.get("priority", "medium"),
                    prerequisites=scenario.preconditions,
                    test_data={},
                    steps=[
                        {
                            "step_number": "1",
                            "action": edge.get("trigger_condition", ""),
                            "expected": edge.get("expected_behavior", "")
                        }
                    ],
                    assertions=[
                        f"Assert: {edge.get('expected_behavior', '')}"
                    ],
                    tags=["edge_case", edge.get("case_type", "unknown"), scenario.scenario_id]
                )
                test_cases.append(edge_case)
        
        return test_cases

    def _generate_test_data_for_scenario(
        self,
        scenario: TestScenario
    ) -> dict[str, Any]:
        """Generate synthetic test data for a scenario.
        
        Args:
            scenario: The test scenario.
            
        Returns:
            Dictionary of test data.
        """
        import random
        import string
        
        def random_string(length: int = 10) -> str:
            return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        
        def random_email() -> str:
            return f"test_{random_string(8)}@example.com"
        
        def random_number(min_val: int = 1, max_val: int = 1000) -> int:
            return random.randint(min_val, max_val)
        
        data_templates = {
            "user": {
                "username": random_string(12),
                "email": random_email(),
                "age": random_number(18, 99),
                "status": "active"
            },
            "payment": {
                "card_number": "4111111111111111",
                "expiry": "12/25",
                "cvv": "123",
                "amount": random_number(10, 1000)
            },
            "order": {
                "order_id": f"ORD_{random_string(8).upper()}",
                "items": random_number(1, 5),
                "total": random_number(50, 500),
                "currency": "USD"
            }
        }
        
        module = scenario.scenario_id.split("_")[1] if "_" in scenario.scenario_id else "generic"
        
        for key in data_templates:
            if key in module.lower():
                return data_templates[key]
        
        return {
            "test_id": random_string(10),
            "timestamp": "2024-01-01T00:00:00Z",
            "data_value": random_number(1, 100)
        }

    def _design_test_environment(
        self,
        test_plan: dict[str, Any],
        sprint_goal: str
    ) -> TestEnvironment:
        """Design test environment requirements.
        
        Args:
            test_plan: Test plan from StrategyManager.
            sprint_goal: Sprint goal description.
            
        Returns:
            TestEnvironment configuration.
        """
        sprint_goal_lower = sprint_goal.lower()
        
        env_type = "staging"
        if "production" in sprint_goal_lower or "release" in sprint_goal_lower:
            env_type = "production"
        elif "uat" in sprint_goal_lower:
            env_type = "uat"
        
        required_services = ["database", "api", "cache"]
        
        if any(k in sprint_goal_lower for k in ["performance", "load"]):
            required_services.append("load_balancer")
            required_services.append("monitoring")
        
        if any(k in sprint_goal_lower for k in ["security", "auth"]):
            required_services.append("identity_provider")
            required_services.append("secret_manager")
        
        config = {
            "base_url": f"https://{env_type}.metanoia.example.com",
            "api_version": "v1",
            "timeout_seconds": 30,
            "retry_attempts": 3
        }
        
        network_config = {
            "vpc_id": f"vpc-{uuid.uuid4().hex[:8]}",
            "subnet_ids": [f"subnet-{i}" for i in range(3)],
            "security_groups": ["sg-web", "sg-api", "sg-db"],
            "load_balancer": "internal" if env_type == "staging" else "external"
        }
        
        secrets = []
        if "payment" in sprint_goal_lower or "billing" in sprint_goal_lower:
            secrets.append("payment_gateway_api_key")
            secrets.append("merchant_id")
        
        if "auth" in sprint_goal_lower or "user" in sprint_goal_lower:
            secrets.append("jwt_secret")
            secrets.append("encryption_key")
        
        secrets.extend(["database_url", "redis_url", "api_secret"])
        
        return TestEnvironment(
            environment_id=f"ENV_{uuid.uuid4().hex[:8]}",
            name=f"Test Environment {env_type.title()}",
            type=env_type,
            configuration=config,
            required_services=required_services,
            network_config=network_config,
            secrets_required=secrets
        )

    def _generate_synthetic_data_templates(
        self,
        scenarios: list[TestScenario]
    ) -> list[SyntheticDataTemplate]:
        """Generate synthetic data templates for test data creation.
        
        Args:
            scenarios: List of test scenarios.
            
        Returns:
            List of synthetic data templates.
        """
        templates = []
        
        entity_types = ["user", "order", "product", "payment", "session"]
        
        for entity_type in entity_types:
            template_id = f"TPL_{entity_type.upper()}_{uuid.uuid4().hex[:4]}"
            
            if entity_type == "user":
                fields = {
                    "id": "uuid",
                    "username": "string:12",
                    "email": "email",
                    "password": "string:16:mixed",
                    "created_at": "datetime",
                    "status": "enum:active,inactive,suspended"
                }
                generation_rules = {
                    "unique_fields": ["email", "username"],
                    "referential_integrity": []
                }
            elif entity_type == "order":
                fields = {
                    "order_id": "string:10:upper",
                    "user_id": "uuid",
                    "total_amount": "decimal:10.2",
                    "currency": "enum:USD,EUR,GBP",
                    "status": "enum:pending,processing,shipped,delivered",
                    "created_at": "datetime"
                }
                generation_rules = {
                    "unique_fields": ["order_id"],
                    "referential_integrity": ["user_id"]
                }
            elif entity_type == "product":
                fields = {
                    "product_id": "string:8:upper",
                    "name": "string:50",
                    "price": "decimal:8.2",
                    "category": "enum:electronics,clothing,food,books",
                    "inventory": "integer:0-1000"
                }
                generation_rules = {
                    "unique_fields": ["product_id"],
                    "referential_integrity": []
                }
            elif entity_type == "payment":
                fields = {
                    "payment_id": "uuid",
                    "order_id": "string:10",
                    "amount": "decimal:10.2",
                    "method": "enum:card,bank,wallet",
                    "status": "enum:pending,completed,failed,refunded",
                    "processed_at": "datetime|null"
                }
                generation_rules = {
                    "unique_fields": ["payment_id"],
                    "referential_integrity": ["order_id"]
                }
            else:
                fields = {
                    "session_id": "uuid",
                    "user_id": "uuid",
                    "started_at": "datetime",
                    "expires_at": "datetime"
                }
                generation_rules = {
                    "unique_fields": ["session_id"],
                    "referential_integrity": ["user_id"]
                }
            
            constraints = [
                f"{entity_type}_id must be unique",
                f"Referenced {entity_type}s must exist"
            ]
            
            templates.append(SyntheticDataTemplate(
                template_id=template_id,
                entity_type=entity_type,
                fields=fields,
                generation_rules=generation_rules,
                constraints=constraints
            ))
        
        return templates

    def _calculate_coverage_metrics(
        self,
        scenarios: list[TestScenario],
        test_cases: list[TestCase]
    ) -> dict[str, float]:
        """Calculate test coverage metrics.
        
        Args:
            scenarios: List of test scenarios.
            test_cases: List of test cases.
            
        Returns:
            Dictionary of coverage metrics.
        """
        happy_path_cases = sum(1 for tc in test_cases if "happy_path" in tc.tags)
        edge_cases = sum(1 for tc in test_cases if "edge_case" in tc.tags)
        
        modules_covered = len(set(
            tc.module for tc in test_cases if tc.module != "unknown"
        ))
        
        total_possible_modules = 10
        
        return {
            "happy_path_coverage": happy_path_cases / max(len(scenarios), 1),
            "edge_case_coverage": edge_cases / max(len(scenarios), 1),
            "module_coverage": modules_covered / total_possible_modules,
            "total_scenarios": len(scenarios),
            "total_test_cases": len(test_cases),
            "edge_case_ratio": edge_cases / max(len(test_cases), 1)
        }

    async def design_tests(
        self,
        test_plan: dict[str, Any],
        sprint_goal: str
    ) -> dict[str, Any]:
        """Design comprehensive tests based on test plan.
        
        Generates test scenarios (happy paths), infers edge cases using LLM,
        creates synthetic test data, designs test environment requirements,
        and outputs test cases to execution agents.
        
        Args:
            test_plan: Test plan from StrategyManager.
            sprint_goal: Sprint goal description.
            
        Returns:
            Dictionary containing:
                - scenarios: Generated test scenarios
                - test_cases: Detailed test cases
                - environment: Test environment configuration
                - synthetic_data: Data generation templates
                - design_rationale: Explanation of design decisions
                - coverage_metrics: Coverage statistics
        """
        logger.info(f"Designing tests for sprint goal: {sprint_goal[:100]}...")
        
        scenarios = await self._generate_scenarios(test_plan, sprint_goal)
        
        test_cases = self._create_test_cases_from_scenarios(scenarios)
        
        environment = self._design_test_environment(test_plan, sprint_goal)
        
        synthetic_data = self._generate_synthetic_data_templates(scenarios)
        
        coverage_metrics = self._calculate_coverage_metrics(scenarios, test_cases)
        
        design_rationale = (
            f"Test design based on {len(scenarios)} scenarios covering happy paths "
            f"and edge cases. Generated {len(test_cases)} test cases with "
            f"{coverage_metrics.get('edge_case_ratio', 0)*100:.0f}% edge case coverage. "
            f"Environment configured for {environment.type} testing with "
            f"{len(environment.required_services)} required services."
        )
        
        result = TestDesignResult(
            scenarios=list(scenarios),
            test_cases=list(test_cases),
            environment=environment,
            synthetic_data=list(synthetic_data),
            design_rationale=design_rationale,
            coverage_metrics=coverage_metrics
        )
        
        logger.info(
            f"Test design complete: {len(scenarios)} scenarios, "
            f"{len(test_cases)} test cases"
        )
        
        return dict(result.model_dump())
