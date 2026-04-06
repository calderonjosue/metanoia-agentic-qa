"""Context & Regression Analyzer for Metanoia-QA.

This agent connects to Supabase pgvector to analyze historical sprint data,
identify similar modules/features, detect flaky tests, and calculate
defect density to provide risk assessments for new sprints.
"""

import logging
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from langchain_postgres import PGVector

logger = logging.getLogger(__name__)


class SprintScope(BaseModel):
    """Input model for sprint scope analysis."""
    description: str = Field(..., description="Description of sprint scope")
    modules: list[str] = Field(default_factory=list, description="Affected modules")
    features: list[str] = Field(default_factory=list, description="New features")
    test_types: list[str] = Field(
        default=["functional"],
        description="Types of testing needed"
    )


class HistoricalSimilarity(BaseModel):
    """Model for historical sprint similarity results."""
    sprint_id: str
    sprint_name: str
    similarity_score: float = Field(..., ge=0.0, le=1.0)
    shared_modules: list[str]
    shared_features: list[str]
    defect_density: float
    test_effectiveness: float


class FlakyTest(BaseModel):
    """Model for flaky test information."""
    test_id: str
    test_name: str
    module: str
    failure_rate: float = Field(..., ge=0.0, le=1.0)
    last_failure: str | None
    root_cause: str | None


class ModuleRisk(BaseModel):
    """Model for module-level risk assessment."""
    module_name: str
    defect_density: float
    change_frequency: float
    test_coverage: float
    risk_level: str = Field(..., pattern="^(low|medium|high|critical)$")
    recommendations: list[str] = Field(default_factory=list)


class ContextAnalysisResult(BaseModel):
    """Output model for context analysis results."""
    risk_level: str = Field(..., pattern="^(low|medium|high|critical)$")
    risk_score: float = Field(..., ge=0.0, le=1.0)
    similar_sprints: list[HistoricalSimilarity] = Field(default_factory=list)
    flaky_tests: list[FlakyTest] = Field(default_factory=list)
    module_risks: list[ModuleRisk] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    effort_multiplier: float = Field(default=1.0, ge=0.1, le=5.0)


class ContextAnalyst:
    """Agent for analyzing historical context and regression risks.

    Connects to Supabase pgvector to search historical sprints for similar
    modules/features, identifies flaky tests from history, and calculates
    defect density per module to return risk assessments.

    Attributes:
        supabase_client: Supabase client for pgvector operations.
        gemini_client: Gemini client for LLM-based analysis.
    """

    def __init__(self, supabase_client: Any, gemini_client: Any):
        """Initialize the Context Analyst.

        Args:
            supabase_client: Supabase client instance for database operations.
            gemini_client: Gemini client for LLM-based analysis.
        """
        self.supabase_client = supabase_client
        self.gemini_client = gemini_client
        self._vector_store: "PGVector | None" = None

    async def _initialize_vector_store(self) -> None:
        """Initialize the pgvector store for similarity search."""
        try:
            from langchain_openai import OpenAIEmbeddings
            from langchain_postgres import PGVector

            embeddings = OpenAIEmbeddings(
                model="models/embedding-001",
                api_key=self.gemini_client.api_key
            )

            self._vector_store = PGVector(
                connection=str(self.supabase_client.connection_string),
                embeddings=embeddings,
                collection_name="sprint_contexts"
            )
        except ImportError as e:
            logger.warning(f"LangChain dependencies not available: {e}")
            self._vector_store = None

    async def _search_historical_sprints(
        self,
        query: str,
        lookback: int = 3
    ) -> list[dict[str, Any]]:
        """Search for similar historical sprints using vector similarity.

        Args:
            query: Search query text.
            lookback: Number of past sprints to consider.

        Returns:
            List of similar sprint records.
        """
        if self._vector_store is None:
            await self._initialize_vector_store()

        if self._vector_store is None:
            logger.warning("Vector store not available, using direct DB query")
            return await self._direct_db_search(query, lookback)

        try:
            results = await self._vector_store.similarity_search(
                query=query,
                k=lookback
            )
            return [doc.metadata for doc in results]
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return await self._direct_db_search(query, lookback)

    async def _direct_db_search(
        self,
        query: str,
        lookback: int
    ) -> list[dict[str, Any]]:
        """Fallback direct database search for similar sprints.

        Args:
            query: Search query text.
            lookback: Number of past sprints to consider.

        Returns:
            List of similar sprint records from direct DB query.
        """
        try:
            response = self.supabase_client.table("sprints").select(
                "*"
            ).order(
                "created_at", desc=True
            ).limit(lookback * 2).execute()

            sprints = response.data or []
            scored_sprints = []

            for sprint in sprints:
                query_lower = query.lower()
                sprint_text = (
                    f"{sprint.get('name', '')} {sprint.get('description', '')} "
                    f"{' '.join(sprint.get('modules', []))}"
                ).lower()

                similarity = self._calculate_text_similarity(query_lower, sprint_text)

                if similarity > 0.3:
                    scored_sprints.append({
                        "sprint_id": sprint.get("id"),
                        "sprint_name": sprint.get("name"),
                        "similarity_score": similarity,
                        "shared_modules": list(
                            set(query_lower.split()) &
                            set(sprint_text.split())
                        ),
                        "shared_features": [],
                        "defect_density": sprint.get("defect_density", 0.0),
                        "test_effectiveness": sprint.get("test_effectiveness", 0.0)
                    })

            scored_sprints.sort(key=lambda x: x["similarity_score"], reverse=True)
            return scored_sprints[:lookback]

        except Exception as e:
            logger.error(f"Direct DB search failed: {e}")
            return []

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity score.

        Args:
            text1: First text string.
            text2: Second text string.

        Returns:
            Similarity score between 0 and 1.
        """
        words1 = set(text1.split())
        words2 = set(text2.split())

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union)

    async def _get_flaky_tests(
        self,
        modules: list[str],
        lookback: int = 3
    ) -> list[FlakyTest]:
        """Retrieve flaky tests from historical data.

        Args:
            modules: List of modules to check.
            lookback: Number of past sprints to analyze.

        Returns:
            List of flaky tests with failure rates.
        """
        if not modules:
            return []

        try:
            response = self.supabase_client.table("test_results").select(
                "test_id, test_name, module, status, created_at"
            ).in_(
                "module", modules
            ).order(
                "created_at", desc=True
            ).limit(1000).execute()

            test_runs = response.data or []
            test_stats: dict[str, dict[str, Any]] = {}

            for run in test_runs:
                test_id = run.get("test_id")
                if test_id not in test_stats:
                    test_stats[test_id] = {
                        "test_id": test_id,
                        "test_name": run.get("test_name", test_id),
                        "module": run.get("module", ""),
                        "failures": 0,
                        "total": 0,
                        "last_failure": None
                    }

                test_stats[test_id]["total"] += 1
                if run.get("status") == "failed":
                    test_stats[test_id]["failures"] += 1
                    test_stats[test_id]["last_failure"] = run.get("created_at")

            flaky_tests = []
            for test_id, stats in test_stats.items():
                failure_rate = stats["failures"] / stats["total"] if stats["total"] > 0 else 0
                if failure_rate > 0.1:
                    flaky_tests.append(FlakyTest(
                        test_id=test_id,
                        test_name=stats["test_name"],
                        module=stats["module"],
                        failure_rate=failure_rate,
                        last_failure=stats["last_failure"],
                        root_cause=None
                    ))

            flaky_tests.sort(key=lambda x: x.failure_rate, reverse=True)
            return flaky_tests[:10]

        except Exception as e:
            logger.error(f"Failed to get flaky tests: {e}")
            return []

    async def _calculate_defect_density(
        self,
        modules: list[str]
    ) -> list[ModuleRisk]:
        """Calculate defect density per module.

        Args:
            modules: List of modules to analyze.

        Returns:
            List of module risk assessments.
        """
        if not modules:
            return []

        module_risks = []

        for module in modules:
            try:
                response = self.supabase_client.table("defects").select(
                    "id, severity, detected_at"
                ).eq(
                    "module", module
                ).order(
                    "detected_at", desc=True
                ).limit(100).execute()

                defects = response.data or []

                response2 = self.supabase_client.table("test_results").select(
                    "id"
                ).eq(
                    "module", module
                ).execute()

                total_tests = len(response2.data or [])
                defect_count = len(defects)

                defect_density = defect_count / max(total_tests, 1)

                severity_counts: dict[str, int] = {}
                for defect in defects:
                    sev = defect.get("severity", "low")
                    severity_counts[sev] = severity_counts.get(sev, 0) + 1

                critical_count = severity_counts.get("critical", 0)
                high_count = severity_counts.get("high", 0)

                if critical_count > 0 or defect_density > 0.5:
                    risk_level = "critical"
                elif high_count > 2 or defect_density > 0.3:
                    risk_level = "high"
                elif defect_density > 0.1:
                    risk_level = "medium"
                else:
                    risk_level = "low"

                recommendations = []
                if risk_level in ("high", "critical"):
                    recommendations.append("Increase regression test coverage")
                    recommendations.append("Schedule additional security testing")
                if defect_density > 0.3:
                    recommendations.append("Consider refactoring module")

                module_risks.append(ModuleRisk(
                    module_name=module,
                    defect_density=defect_density,
                    change_frequency=0.0,
                    test_coverage=min(defect_density * 10, 1.0),
                    risk_level=risk_level,
                    recommendations=recommendations
                ))

            except Exception as e:
                logger.error(f"Failed to calculate defect density for {module}: {e}")
                module_risks.append(ModuleRisk(
                    module_name=module,
                    defect_density=0.0,
                    change_frequency=0.0,
                    test_coverage=0.0,
                    risk_level="low",
                    recommendations=[]
                ))

        return module_risks

    async def analyze(
        self,
        sprint_scope: str | SprintScope,
        lookback: int = 3
    ) -> dict[str, Any]:
        """Analyze sprint scope against historical data for risk assessment.

        Connects to Supabase pgvector to search historical sprints for
        similar modules/features, identifies flaky tests, and calculates
        defect density per module to provide comprehensive risk assessment.

        Args:
            sprint_scope: Description of sprint scope (string or SprintScope).
            lookback: Number of past sprints to analyze for context.

        Returns:
            Dictionary containing:
                - risk_level: Overall risk level (low/medium/high/critical)
                - risk_score: Numeric risk score (0-1)
                - similar_sprints: Historical sprints with similarity data
                - flaky_tests: Flaky tests identified from history
                - module_risks: Per-module risk assessments
                - recommendations: Actionable recommendations
                - effort_multiplier: Adjustment factor for test effort
        """
        if isinstance(sprint_scope, str):
            scope = SprintScope(description=sprint_scope)
        else:
            scope = sprint_scope

        logger.info(f"Analyzing sprint scope: {scope.description[:100]}...")

        similar_sprints = await self._search_historical_sprints(
            query=scope.description,
            lookback=lookback
        )

        modules = scope.modules or self._extract_modules_from_description(scope.description)
        flaky_tests = await self._get_flaky_tests(modules, lookback)
        module_risks = await self._calculate_defect_density(modules)

        historical_similarity_results = [
            HistoricalSimilarity(**sprint) for sprint in similar_sprints
        ]

        avg_similarity = sum(
            s.similarity_score for s in historical_similarity_results
        ) / max(len(historical_similarity_results), 1)

        high_risk_modules = sum(
            1 for r in module_risks if r.risk_level in ("high", "critical")
        )
        flaky_test_count = len(flaky_tests)

        risk_score = (
            avg_similarity * 0.3 +
            (high_risk_modules / max(len(module_risks), 1)) * 0.4 +
            min(flaky_test_count * 0.05, 0.3)
        )

        if risk_score > 0.7:
            risk_level = "critical"
        elif risk_score > 0.5:
            risk_level = "high"
        elif risk_score > 0.3:
            risk_level = "medium"
        else:
            risk_level = "low"

        recommendations = []
        if flaky_test_count > 0:
            recommendations.append(
                f"Review {flaky_test_count} flaky tests before sprint start"
            )
        if high_risk_modules > 0:
            recommendations.append(
                f"Focus on {high_risk_modules} high-risk module(s) with elevated defect density"
            )
        if avg_similarity > 0.6:
            recommendations.append(
                "Similar sprints found - consider reusing test cases"
            )
        recommendations.append(
            "Plan for at least 20% additional regression testing time"
        )

        effort_multiplier = 1.0 + (risk_score * 0.5)

        result = ContextAnalysisResult(
            risk_level=risk_level,
            risk_score=risk_score,
            similar_sprints=historical_similarity_results,
            flaky_tests=flaky_tests,
            module_risks=module_risks,
            recommendations=recommendations,
            effort_multiplier=effort_multiplier
        )

        return dict(result.model_dump())

    def _extract_modules_from_description(self, description: str) -> list[str]:
        """Extract module names from sprint description using common patterns.

        Args:
            description: Sprint description text.

        Returns:
            List of potential module names.
        """
        common_modules = [
            "auth", "payment", "user", "admin", "api", "ui", "database",
            "notification", "reporting", "analytics", "billing", "checkout"
        ]

        description_lower = description.lower()
        found_modules = [
            m for m in common_modules
            if m in description_lower
        ]

        return found_modules
