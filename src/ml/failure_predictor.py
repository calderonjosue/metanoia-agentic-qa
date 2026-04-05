"""
ML-based failure prediction using historical data.

Uses simple statistical methods to predict which test cases
are likely to fail based on historical patterns.
"""

from pydantic import BaseModel


class FailurePrediction(BaseModel):
    test_case_id: str
    failure_probability: float
    risk_factors: list[str]
    recommended_action: str


class FailurePredictor:
    """
    Predicts test failures using:
    - Historical flaky test data
    - Module defect density
    - Code change patterns
    - Similar sprint history
    """

    def __init__(self, supabase_client):
        self.supabase = supabase_client

    async def predict(self, test_case: dict, context: dict) -> FailurePrediction:
        """Predict failure probability for a test case."""
        test_id = test_case.get("id", "unknown")

        historical_data = await self._get_historical_data(test_id)
        features = await self._extract_features(test_case, context, historical_data)
        probability = self._calculate_probability(features)

        risk_factors = await self.analyze_risk_factors(test_case, historical_data)
        recommended_action = self._determine_action(probability, risk_factors)

        return FailurePrediction(
            test_case_id=test_id,
            failure_probability=probability,
            risk_factors=risk_factors,
            recommended_action=recommended_action
        )

    async def _get_historical_data(self, test_id: str) -> dict:
        """Fetch historical failure data for a test case."""
        response = self.supabase.table("test_execution_history").select(
            "*"
        ).eq("test_case_id", test_id).order(
            "executed_at", desc=True
        ).limit(50).execute()

        return {"executions": response.data if response.data else []}

    async def _extract_features(
        self,
        test_case: dict,
        context: dict,
        historical_data: dict
    ) -> dict[str, float | int]:
        """Extract features for failure prediction."""
        executions = historical_data.get("executions", [])

        flaky_score = self._calculate_flaky_score(executions)
        module_id = test_case.get("module_id", "")
        defect_density = await self._get_defect_density(module_id if module_id else "")
        change_impact = self._estimate_change_impact(context)
        sprint_similarity = await self._calculate_sprint_similarity(context)

        return {
            "flaky_score": flaky_score,
            "defect_density": defect_density,
            "change_impact": change_impact,
            "sprint_similarity": sprint_similarity,
            "recent_failures": sum(1 for e in executions if not e.get("passed", True)),
            "total_runs": len(executions)
        }

    def _calculate_flaky_score(self, executions: list) -> float:
        """Calculate flakiness score based on execution history."""
        if not executions:
            return 0.5

        failures = sum(1 for e in executions if not e.get("passed", True))
        total = len(executions)

        if total < 3:
            return 0.5

        failure_rate = failures / total

        unique_results = len(set(str(e.get("result", "")) for e in executions))
        variability = unique_results / max(total, 1)

        return min(1.0, failure_rate * 0.7 + variability * 0.3)

    async def _get_defect_density(self, module_id: str) -> float:
        """Get defect density for a module."""
        if not module_id:
            return 0.0

        response = self.supabase.table("module_defects").select(
            "defect_count", "lines_of_code"
        ).eq("module_id", module_id).execute()

        if response.data:
            row = response.data[0]
            if row.get("lines_of_code", 0) > 0:
                return float(row["defect_count"]) / float(row["lines_of_code"])
        return 0.0

    def _estimate_change_impact(self, context: dict) -> float:
        """Estimate impact of code changes on test."""
        change_size = context.get("change_size", "small")
        files_changed = context.get("files_changed", [])
        core_files = context.get("core_module_files", [])

        size_map = {"small": 0.2, "medium": 0.5, "large": 0.8, "enterprise": 1.0}
        impact = size_map.get(change_size, 0.3)

        if core_files and files_changed:
            overlap = len(set(files_changed) & set(core_files))
            if overlap > 0:
                impact = min(1.0, impact + (overlap * 0.1))

        return impact

    async def _calculate_sprint_similarity(self, context: dict) -> float:
        """Calculate similarity to historically problematic sprints."""
        current_sprint = context.get("sprint", "")
        sprint_pattern = context.get("sprint_pattern", [])

        if not sprint_pattern:
            return 0.5

        similar_sprints = [s for s in sprint_pattern if s.get("name") == current_sprint]

        if similar_sprints:
            failure_rate = similar_sprints[0].get("failure_rate", 0)
            return float(failure_rate)

        return 0.5

    def _calculate_probability(self, features: dict[str, float | int]) -> float:
        """Calculate failure probability from features."""
        weights = {
            "flaky_score": 0.35,
            "defect_density": 0.25,
            "change_impact": 0.20,
            "sprint_similarity": 0.20
        }

        score = (
            float(features["flaky_score"]) * weights["flaky_score"] +
            float(features["defect_density"]) * weights["defect_density"] +
            float(features["change_impact"]) * weights["change_impact"] +
            float(features["sprint_similarity"]) * weights["sprint_similarity"]
        )

        if features["total_runs"] < 3:
            score = score * 0.7 + 0.3

        return min(1.0, max(0.0, score))

    async def analyze_risk_factors(
        self,
        test_case: dict,
        historical_data: dict
    ) -> list[str]:
        """Analyze and return risk factors."""
        risk_factors = []
        executions = historical_data.get("executions", [])

        flaky_score = self._calculate_flaky_score(executions)
        if flaky_score > 0.6:
            risk_factors.append("High flakiness detected in recent runs")

        recent_failures = sum(1 for e in executions[:10] if not e.get("passed", True))
        if recent_failures >= 3:
            risk_factors.append(f"Failed {recent_failures} of last 10 runs")

        if test_case.get("is_integration", False):
            risk_factors.append("Integration test with external dependencies")

        if test_case.get("has_timing_issues", False):
            risk_factors.append("Contains timing-dependent assertions")

        module_defect_count = test_case.get("module_defect_count", 0)
        if module_defect_count > 5:
            risk_factors.append(f"Module has {module_defect_count} known defects")

        return risk_factors

    def _determine_action(self, probability: float, risk_factors: list[str]) -> str:
        """Determine recommended action based on probability and risks."""
        if probability >= 0.8:
            return "Skip and investigate before running"
        elif probability >= 0.6:
            return "Run with priority but monitor closely"
        elif probability >= 0.4:
            return "Run in standard queue"
        else:
            if len(risk_factors) > 2:
                return "Run with priority - multiple minor risk factors"
            return "Run as normal priority"
