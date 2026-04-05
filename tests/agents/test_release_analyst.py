"""Tests for ReleaseAnalyst agent."""

import pytest

from src.agents.release_analyst import (
    AgentResult,
    ReleaseAnalyst,
    ReleaseScore,
)


class TestAgentResult:
    """Tests for AgentResult model."""

    def test_agent_result_creation(self):
        """Test creating AgentResult."""
        result = AgentResult(
            agent_name="functional-lead",
            passed=45,
            failed=2,
            skipped=3,
            duration=120.5,
            status="completed",
            metadata={"findings": []}
        )

        assert result.agent_name == "functional-lead"
        assert result.passed == 45
        assert result.failed == 2


class TestReleaseScore:
    """Tests for ReleaseScore model."""

    def test_release_score_creation(self):
        """Test creating ReleaseScore."""
        score = ReleaseScore(
            overall=85.5,
            functional=90.0,
            performance=80.0,
            security=85.0,
            ui=87.0,
            weighted_factors={
                "functional_contribution": 31.5,
                "performance_contribution": 20.0
            }
        )

        assert score.overall == 85.5
        assert score.functional == 90.0


class TestReleaseAnalyst:
    """Tests for ReleaseAnalyst agent."""

    @pytest.fixture
    def release_analyst(self):
        """Create ReleaseAnalyst instance."""
        return ReleaseAnalyst()

    @pytest.fixture
    def sample_agent_results(self):
        """Create sample agent results."""
        return {
            "functional-lead": AgentResult(
                agent_name="functional-lead",
                passed=38,
                failed=2,
                skipped=2,
                duration=245.5,
                status="completed",
                metadata={}
            ),
            "performance-lead": AgentResult(
                agent_name="performance-lead",
                passed=20,
                failed=0,
                skipped=0,
                duration=180.0,
                status="completed",
                metadata={}
            ),
            "security-lead": AgentResult(
                agent_name="security-lead",
                passed=15,
                failed=0,
                skipped=0,
                duration=120.0,
                status="completed",
                metadata={}
            ),
            "ui-automation-lead": AgentResult(
                agent_name="ui-automation-lead",
                passed=25,
                failed=1,
                skipped=0,
                duration=95.0,
                status="completed",
                metadata={}
            )
        }

    def test_release_analyst_initialization(self, release_analyst):
        """Test ReleaseAnalyst initializes correctly."""
        assert release_analyst.name == "release-analyst"
        assert release_analyst.version == "1.0.0"
        assert release_analyst._agent_results == {}
        assert release_analyst._release_history == []

    def test_release_analyst_weights(self, release_analyst):
        """Test release analyst has correct weights."""
        assert ReleaseAnalyst.WEIGHTS["functional"] == 0.35
        assert ReleaseAnalyst.WEIGHTS["performance"] == 0.25
        assert ReleaseAnalyst.WEIGHTS["security"] == 0.25
        assert ReleaseAnalyst.WEIGHTS["ui"] == 0.15
        assert sum(ReleaseAnalyst.WEIGHTS.values()) == 1.0

    def test_calculate_weighted_score(self, release_analyst):
        """Test weighted score calculation."""
        score = release_analyst.calculate_weighted_score(
            functional_pct=100.0,
            performance_pct=100.0,
            security_pct=100.0,
            ui_pct=100.0
        )

        assert score.overall == 100.0
        assert score.functional == 100.0
        assert score.performance == 100.0
        assert score.security == 100.0
        assert score.ui == 100.0

    def test_calculate_weighted_score_partial(self, release_analyst):
        """Test weighted score with partial pass rate."""
        score = release_analyst.calculate_weighted_score(
            functional_pct=80.0,
            performance_pct=100.0,
            security_pct=100.0,
            ui_pct=100.0
        )

        expected = 80.0 * 0.35 + 100.0 * 0.25 + 100.0 * 0.25 + 100.0 * 0.15
        assert score.overall == expected

    def test_calculate_weighted_score_contributions(self, release_analyst):
        """Test weighted factor contributions."""
        score = release_analyst.calculate_weighted_score(
            functional_pct=100.0,
            performance_pct=100.0,
            security_pct=100.0,
            ui_pct=100.0
        )

        assert score.weighted_factors["functional_contribution"] == 35.0
        assert score.weighted_factors["performance_contribution"] == 25.0
        assert score.weighted_factors["security_contribution"] == 25.0
        assert score.weighted_factors["ui_contribution"] == 15.0

    @pytest.mark.asyncio
    async def test_execute_collects_results(self, release_analyst, sample_agent_results):
        """Test execute collects results from all agents."""
        context = {"agent_results": sample_agent_results}

        result = await release_analyst.execute([], context)

        assert result.passed == 98
        assert result.failed == 3
        assert result.skipped == 2
        assert result.duration > 0

    @pytest.mark.asyncio
    async def test_execute_with_dict_results(self, release_analyst):
        """Test execute handles dict-style results."""
        context = {
            "agent_results": {
                "functional-lead": {
                    "passed": 30,
                    "failed": 2,
                    "skipped": 1,
                    "duration": 100.0,
                    "status": "completed",
                    "metadata": {}
                }
            }
        }

        result = await release_analyst.execute([], context)

        assert result.passed == 30
        assert result.failed == 2

    def test_get_release_score(self, release_analyst, sample_agent_results):
        """Test get_release_score returns current score."""
        for name, result in sample_agent_results.items():
            release_analyst._agent_results[name] = result

        score = release_analyst.get_release_score()

        assert isinstance(score, ReleaseScore)
        assert 0 <= score.overall <= 100

    def test_calculate_release_score_all_pass(self, release_analyst):
        """Test score calculation when all tests pass."""
        release_analyst._agent_results = {
            "functional-lead": AgentResult(
                agent_name="functional-lead", passed=100, failed=0, skipped=0,
                duration=100.0, status="completed", metadata={}
            )
        }

        score = release_analyst._calculate_release_score()

        assert score.overall == 100.0

    def test_calculate_release_score_all_fail(self, release_analyst):
        """Test score calculation when all tests fail."""
        release_analyst._agent_results = {
            "functional-lead": AgentResult(
                agent_name="functional-lead", passed=0, failed=100, skipped=0,
                duration=100.0, status="completed", metadata={}
            )
        }

        score = release_analyst._calculate_release_score()

        assert score.overall == 0.0

    def test_calculate_release_score_missing_agent(self, release_analyst):
        """Test score calculation with missing agents returns 100."""
        release_analyst._agent_results = {}

        score = release_analyst._calculate_release_score()

        assert score.functional == 100.0

    def test_make_recommendation_go(self, release_analyst):
        """Test GO recommendation for high score."""
        score = ReleaseScore(
            overall=90.0,
            functional=95.0,
            performance=90.0,
            security=85.0,
            ui=90.0,
            weighted_factors={}
        )

        recommendation = release_analyst._make_recommendation(score, {})

        assert recommendation["decision"] in ["GO", "FAST-TRACK GO"]

    def test_make_recommendation_no_go_low_score(self, release_analyst):
        """Test NO-GO recommendation for low score."""
        score = ReleaseScore(
            overall=60.0,
            functional=70.0,
            performance=60.0,
            security=55.0,
            ui=60.0,
            weighted_factors={}
        )

        recommendation = release_analyst._make_recommendation(score, {})

        assert recommendation["decision"] == "NO-GO"
        assert len(recommendation["blockers"]) > 0

    def test_make_recommendation_no_go_security_failures(self, release_analyst):
        """Test NO-GO for security failures."""
        score = ReleaseScore(
            overall=85.0,
            functional=90.0,
            performance=85.0,
            security=80.0,
            ui=85.0,
            weighted_factors={}
        )
        results = {
            "security-lead": {"failed": 1, "metadata": {}}
        }

        recommendation = release_analyst._make_recommendation(score, results)

        assert recommendation["decision"] == "NO-GO"

    def test_make_recommendation_fast_track(self, release_analyst):
        """Test FAST-TRACK GO for exceptional score."""
        score = ReleaseScore(
            overall=95.0,
            functional=100.0,
            performance=95.0,
            security=90.0,
            ui=95.0,
            weighted_factors={}
        )

        recommendation = release_analyst._make_recommendation(score, {})

        assert recommendation["decision"] == "FAST-TRACK GO"

    def test_make_recommendation_conditional_go(self, release_analyst):
        """Test CONDITIONAL-GO for performance regressions."""
        score = ReleaseScore(
            overall=75.0,
            functional=80.0,
            performance=70.0,
            security=75.0,
            ui=80.0,
            weighted_factors={}
        )
        results = {
            "performance-lead": {
                "failed": 1,
                "metadata": {
                    "regressions": [{"severity": "high"}]
                }
            }
        }

        recommendation = release_analyst._make_recommendation(score, results)

        assert recommendation["decision"] == "CONDITIONAL-GO"

    def test_count_failures_by_agent(self, release_analyst):
        """Test counting failures by agent."""
        results = {
            "security-lead": {"failed": 3},
            "performance-lead": AgentResult(
                agent_name="performance-lead", passed=20, failed=2,
                skipped=0, duration=100.0, status="completed", metadata={}
            )
        }

        assert release_analyst._count_failures_by_agent("security-lead", results) == 3
        assert release_analyst._count_failures_by_agent("performance-lead", results) == 2
        assert release_analyst._count_failures_by_agent("unknown", results) == 0

    def test_count_critical_failures(self, release_analyst):
        """Test counting critical failures."""
        results = {
            "functional-lead": {
                "metadata": {
                    "findings": [
                        {"severity": "critical"},
                        {"severity": "high"}
                    ]
                }
            },
            "security-lead": {
                "metadata": {
                    "findings": [
                        {"severity": "critical"}
                    ]
                }
            }
        }

        count = release_analyst._count_critical_failures(results)

        assert count == 2

    def test_analyze_business_impact(self, release_analyst, sample_agent_results):
        """Test business impact analysis."""
        for name, result in sample_agent_results.items():
            release_analyst._agent_results[name] = result

        impact = release_analyst._analyze_business_impact()

        assert "functional-lead" in impact
        assert "performance-lead" in impact

    def test_estimate_business_impact(self, release_analyst):
        """Test business impact estimation."""
        result = AgentResult(
            agent_name="security-lead",
            passed=15,
            failed=6,
            skipped=0,
            duration=120.0,
            status="completed",
            metadata={}
        )

        impact = release_analyst._estimate_business_impact("security-lead", result)

        assert impact == "critical"

    def test_get_affected_business_areas(self, release_analyst):
        """Test getting affected business areas."""
        areas = release_analyst._get_affected_business_areas("security-lead")

        assert "Customer Data" in areas
        assert "Compliance" in areas

    def test_generate_executive_summary_go(self, release_analyst):
        """Test executive summary for GO."""
        score = ReleaseScore(
            overall=85.0, functional=90.0, performance=80.0,
            security=85.0, ui=85.0, weighted_factors={}
        )
        recommendation = {"decision": "GO", "reasoning": []}

        summary = release_analyst._generate_executive_summary(score, recommendation)

        assert "85.0%" in summary
        assert "GO" in summary

    def test_generate_executive_summary_no_go(self, release_analyst):
        """Test executive summary for NO-GO."""
        score = ReleaseScore(
            overall=60.0, functional=70.0, performance=60.0,
            security=55.0, ui=65.0, weighted_factors={}
        )
        recommendation = {"decision": "NO-GO", "reasoning": ["Score below threshold"]}

        summary = release_analyst._generate_executive_summary(score, recommendation)

        assert "60.0%" in summary
        assert "NO-GO" in summary

    def test_determine_certification_gold(self, release_analyst):
        """Test GOLD certification."""
        score = ReleaseScore(
            overall=96.0, functional=95.0, performance=95.0,
            security=98.0, ui=95.0, weighted_factors={}
        )
        recommendation = {"decision": "FAST-TRACK GO"}

        cert = release_analyst._determine_certification(score, recommendation)

        assert cert["level"] == "GOLD"

    def test_determine_certification_silver(self, release_analyst):
        """Test SILVER certification."""
        score = ReleaseScore(
            overall=85.0, functional=85.0, performance=85.0,
            security=85.0, ui=85.0, weighted_factors={}
        )
        recommendation = {"decision": "GO"}

        cert = release_analyst._determine_certification(score, recommendation)

        assert cert["level"] == "SILVER"

    def test_determine_certification_bronze(self, release_analyst):
        """Test BRONZE certification."""
        score = ReleaseScore(
            overall=75.0, functional=75.0, performance=75.0,
            security=75.0, ui=75.0, weighted_factors={}
        )
        recommendation = {"decision": "CONDITIONAL-GO"}

        cert = release_analyst._determine_certification(score, recommendation)

        assert cert["level"] == "BRONZE"

    def test_determine_certification_none(self, release_analyst):
        """Test no certification."""
        score = ReleaseScore(
            overall=50.0, functional=60.0, performance=50.0,
            security=45.0, ui=55.0, weighted_factors={}
        )
        recommendation = {"decision": "NO-GO"}

        cert = release_analyst._determine_certification(score, recommendation)

        assert cert["level"] == "NONE"

    def test_generate_next_steps_go(self, release_analyst):
        """Test next steps for GO."""
        recommendation = {"decision": "GO"}

        steps = release_analyst._generate_next_steps(recommendation)

        assert len(steps) > 0
        assert any("release" in s.lower() for s in steps)

    def test_generate_next_steps_no_go(self, release_analyst):
        """Test next steps for NO-GO."""
        recommendation = {"decision": "NO-GO"}

        steps = release_analyst._generate_next_steps(recommendation)

        assert len(steps) > 0

    def test_generate_release_report(self, release_analyst, sample_agent_results):
        """Test complete release report generation."""
        for name, result in sample_agent_results.items():
            release_analyst._agent_results[name] = result

        report = release_analyst.generate_release_report()

        assert "title" in report
        assert "timestamp" in report
        assert "executive_summary" in report
        assert "score_breakdown" in report
        assert "recommendation" in report
        assert "certification" in report
        assert "next_steps" in report

    def test_generate_report_path(self, release_analyst):
        """Test report path generation."""
        path = release_analyst._generate_report_path()

        assert "reports/" in path
        assert "release_certification_" in path
        assert path.endswith(".json")

    @pytest.mark.asyncio
    async def test_heal_performance(self, release_analyst):
        """Test healing for performance issues."""
        failure = {
            "agent": "performance-lead",
            "error": "High latency detected",
            "business_impact": "high"
        }

        result = await release_analyst.heal(failure)

        assert result["status"] == "analyzed"
        assert result["agent"] == "performance-lead"
        assert len(result["recommendations"]) > 0

    @pytest.mark.asyncio
    async def test_heal_security(self, release_analyst):
        """Test healing for security issues."""
        failure = {
            "agent": "security-lead",
            "error": "SQL injection vulnerability",
            "business_impact": "critical"
        }

        result = await release_analyst.heal(failure)

        assert result["block_release"] is True

    @pytest.mark.asyncio
    async def test_heal_ui(self, release_analyst):
        """Test healing for UI issues."""
        failure = {
            "agent": "ui-automation-lead",
            "error": "Broken selectors",
            "business_impact": "medium"
        }

        result = await release_analyst.heal(failure)

        assert "broken UI selectors" in result["recommendations"][0]
