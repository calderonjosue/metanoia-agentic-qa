"""QA Release Analyst agent for Metanoia-QA.

Collects results from all execution agents and generates release recommendations.
"""

import logging
from typing import Optional

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class AgentResult(BaseModel):
    """Result from a single execution agent."""
    agent_name: str
    passed: int
    failed: int
    skipped: int
    duration: float
    status: str
    metadata: dict = {}


class ReleaseScore(BaseModel):
    """Calculated release score breakdown."""
    overall: float
    functional: float
    performance: float
    security: float
    ui: float
    weighted_factors: dict


class TestResult(BaseModel):
    """Result of release analysis."""
    passed: int
    failed: int
    skipped: int
    duration: float
    report_url: Optional[str] = None


class ReleaseAnalyst:
    """QA Release Analyst that collects results and generates release recommendations.
    
    Responsibilities:
    - Collect results from all execution agents
    - Calculate weighted release score
    - Cross technical errors with business impact
    - Generate release certification report
    - Make go/no-go recommendation
    """

    name = "release-analyst"
    version = "1.0.0"

    WEIGHTS = {
        "functional": 0.35,
        "performance": 0.25,
        "security": 0.25,
        "ui": 0.15
    }

    BUSINESS_IMPACT_MAP = {
        "critical": 10,
        "high": 7,
        "medium": 4,
        "low": 1
    }

    def __init__(self):
        self._agent_results: dict[str, AgentResult] = {}
        self._release_history: list[dict] = []

    async def execute(self, test_cases: list[dict], context: dict) -> TestResult:
        """Collect agent results and generate release analysis.
        
        Args:
            test_cases: Not used directly - results collected from agents.
            context: Must contain 'agent_results' with results from all agents.
            
        Returns:
            TestResult with release score and recommendation.
        """
        agent_results = context.get("agent_results", {})

        total_passed = 0
        total_failed = 0
        total_skipped = 0
        total_duration = 0.0

        for agent_name, result in agent_results.items():
            if isinstance(result, dict):
                agent_result = AgentResult(
                    agent_name=agent_name,
                    passed=result.get("passed", 0),
                    failed=result.get("failed", 0),
                    skipped=result.get("skipped", 0),
                    duration=result.get("duration", 0.0),
                    status=result.get("status", "unknown"),
                    metadata=result.get("metadata", {})
                )
            else:
                agent_result = result

            self._agent_results[agent_name] = agent_result
            total_passed += agent_result.passed
            total_failed += agent_result.failed
            total_skipped += agent_result.skipped
            total_duration += agent_result.duration

        score = self._calculate_release_score()
        recommendation = self._make_recommendation(score, agent_results)

        logger.info(
            f"Release analysis complete: score={score.overall:.2f}, "
            f"recommendation={recommendation['decision']}"
        )

        return TestResult(
            passed=total_passed,
            failed=total_failed,
            skipped=total_skipped,
            duration=total_duration,
            report_url=self._generate_report_path()
        )

    async def heal(self, failure: dict) -> dict:
        """Investigate a failure and provide remediation guidance.
        
        Args:
            failure: Failure information with agent, error, business_impact.
            
        Returns:
            Analysis with remediation steps.
        """
        agent = failure.get("agent", "")
        error = failure.get("error", "")
        business_impact = failure.get("business_impact", "medium")

        severity_score = self.BUSINESS_IMPACT_MAP.get(business_impact, 4)

        recommendations = []

        if agent == "performance-engineer":
            recommendations.extend([
                "Review slow endpoints for optimization opportunities",
                "Consider scaling infrastructure",
                "Check for N+1 query patterns"
            ])
        elif agent == "security-engineer":
            recommendations.extend([
                "Do not release until critical vulnerabilities are fixed",
                "Apply security patches immediately",
                "Consider penetration testing"
            ])
        elif agent == "ui-automation-engineer":
            recommendations.extend([
                "Fix broken UI selectors before release",
                "Review and update locator strategy",
                "Ensure cross-browser compatibility"
            ])
        else:
            recommendations.append("Investigate and resolve the failure")

        return {
            "status": "analyzed",
            "agent": agent,
            "error": error,
            "business_impact_score": severity_score,
            "recommendations": recommendations,
            "block_release": severity_score >= 7
        }

    def calculate_weighted_score(
        self,
        functional_pct: float,
        performance_pct: float,
        security_pct: float,
        ui_pct: float
    ) -> ReleaseScore:
        """Calculate weighted release score.
        
        Args:
            functional_pct: Functional test pass percentage.
            performance_pct: Performance test pass percentage.
            security_pct: Security test pass percentage.
            ui_pct: UI test pass percentage.
            
        Returns:
            ReleaseScore with breakdown.
        """
        weights = self.WEIGHTS

        overall = (
            functional_pct * weights["functional"] +
            performance_pct * weights["performance"] +
            security_pct * weights["security"] +
            ui_pct * weights["ui"]
        )

        return ReleaseScore(
            overall=overall,
            functional=functional_pct,
            performance=performance_pct,
            security=security_pct,
            ui=ui_pct,
            weighted_factors={
                "functional_contribution": functional_pct * weights["functional"],
                "performance_contribution": performance_pct * weights["performance"],
                "security_contribution": security_pct * weights["security"],
                "ui_contribution": ui_pct * weights["ui"]
            }
        )

    def generate_release_report(self) -> dict:
        """Generate comprehensive release certification report.
        
        Returns:
            Release certification report with all details.
        """
        score = self._calculate_release_score()
        recommendation = self._make_recommendation(score, self._agent_results)

        report = {
            "title": "Release Certification Report",
            "timestamp": self._get_timestamp(),
            "executive_summary": self._generate_executive_summary(score, recommendation),
            "score_breakdown": score.model_dump(),
            "agent_results": {name: r.model_dump() for name, r in self._agent_results.items()},
            "business_impact_analysis": self._analyze_business_impact(),
            "recommendation": recommendation,
            "certification": self._determine_certification(score, recommendation),
            "next_steps": self._generate_next_steps(recommendation)
        }

        self._release_history.append(report)

        return report

    def get_release_score(self) -> ReleaseScore:
        """Get current release score."""
        return self._calculate_release_score()

    def _calculate_release_score(self) -> ReleaseScore:
        """Calculate weighted release score from agent results."""
        functional_result = self._agent_results.get("functional-lead") or \
                           self._agent_results.get("strategy-manager")
        performance_result = self._agent_results.get("performance-engineer")
        security_result = self._agent_results.get("security-engineer")
        ui_result = self._agent_results.get("ui-automation-engineer")

        def calc_pct(result: Optional[AgentResult]) -> float:
            if result is None:
                return 100.0
            total = result.passed + result.failed + result.skipped
            if total == 0:
                return 100.0
            return (result.passed / total) * 100

        functional_pct = calc_pct(functional_result)
        performance_pct = calc_pct(performance_result)
        security_pct = calc_pct(security_result)
        ui_pct = calc_pct(ui_result)

        return self.calculate_weighted_score(
            functional_pct,
            performance_pct,
            security_pct,
            ui_pct
        )

    def _make_recommendation(
        self,
        score: ReleaseScore,
        agent_results: dict
    ) -> dict:
        """Make go/no-go release recommendation.
        
        Returns:
            Recommendation with decision and reasoning.
        """
        decision = "GO"
        reasoning = []
        blockers = []

        if score.overall < 70:
            decision = "NO-GO"
            reasoning.append(f"Overall score {score.overall:.1f}% is below threshold (70%)")
            blockers.append("Score below minimum threshold")

        security_failures = self._count_failures_by_agent("security-engineer", agent_results)
        if security_failures > 0:
            decision = "NO-GO"
            reasoning.append(f"Security tests have {security_failures} failures")
            blockers.append("Critical security vulnerabilities")

        performance_result = agent_results.get("performance-engineer")
        if performance_result and isinstance(performance_result, dict):
            if performance_result.get("failed", 0) > 0:
                regressions = performance_result.get("metadata", {}).get("regressions", [])
                if any(r.get("severity") == "high" for r in regressions):
                    decision = "CONDITIONAL-GO"
                    reasoning.append("High severity performance regressions detected")

        critical_failures = self._count_critical_failures(agent_results)
        if critical_failures > 0:
            decision = "NO-GO"
            reasoning.append(f"{critical_failures} critical failures detected")
            blockers.append("Critical test failures")

        if decision == "GO" and score.overall >= 90:
            decision = "FAST-TRACK GO"
            reasoning.append("Exceptional score - eligible for fast-track release")

        return {
            "decision": decision,
            "reasoning": reasoning,
            "blockers": blockers,
            "score": score.overall
        }

    def _count_failures_by_agent(self, agent: str, results: dict) -> int:
        """Count failures for a specific agent."""
        result = results.get(agent, {})
        if isinstance(result, dict):
            return result.get("failed", 0) or 0
        if hasattr(result, "failed"):
            return int(result.failed)
        return 0

    def _count_critical_failures(self, results: dict) -> int:
        """Count critical severity failures across all agents."""
        critical_count = 0

        for agent_name, result in results.items():
            if isinstance(result, dict):
                findings = result.get("metadata", {}).get("findings", [])
                critical_count += len([f for f in findings if f.get("severity") == "critical"])

        return critical_count

    def _analyze_business_impact(self) -> dict:
        """Analyze business impact of failures."""
        impact_analysis = {}

        for agent_name, result in self._agent_results.items():
            if result.failed > 0:
                impact_analysis[agent_name] = {
                    "failure_count": result.failed,
                    "estimated_impact": self._estimate_business_impact(agent_name, result),
                    "affected_areas": self._get_affected_business_areas(agent_name)
                }

        return impact_analysis

    def _estimate_business_impact(self, agent: str, result: AgentResult) -> str:
        """Estimate business impact of agent failures."""
        impact_scores = {
            "security-engineer": "critical",
            "performance-engineer": "high",
            "ui-automation-engineer": "medium",
            "functional-lead": "high"
        }

        severity = impact_scores.get(agent, "medium")

        if result.failed > 5:
            severity = "critical"
        elif result.failed > 2:
            if severity == "medium":
                severity = "high"

        return severity

    def _get_affected_business_areas(self, agent: str) -> list[str]:
        """Get business areas affected by agent failures."""
        area_map = {
            "security-engineer": ["Customer Data", "Compliance", "Reputation"],
            "performance-engineer": ["User Experience", "Conversion", "SEO"],
            "ui-automation-engineer": ["User Experience", "Accessibility"],
            "functional-lead": ["Core Functionality", "Revenue"]
        }
        return area_map.get(agent, ["General"])

    def _generate_executive_summary(self, score: ReleaseScore, recommendation: dict) -> str:
        """Generate executive summary for report."""
        decision = recommendation["decision"]
        score_val = score.overall

        summary_parts = [
            f"Release analysis completed with overall score of {score_val:.1f}%.",
            f"Recommendation: {decision}.",
        ]

        if decision == "NO-GO":
            summary_parts.append("Release is not recommended due to critical issues.")
        elif decision == "CONDITIONAL-GO":
            summary_parts.append("Release may proceed with caution and monitoring.")
        elif decision == "FAST-TRACK GO":
            summary_parts.append("Release is recommended with priority processing.")
        else:
            summary_parts.append("Release is recommended with standard processing.")

        return " ".join(summary_parts)

    def _determine_certification(
        self,
        score: ReleaseScore,
        recommendation: dict
    ) -> dict:
        """Determine certification level."""
        decision = recommendation["decision"]

        if decision == "FAST-TRACK GO" and score.overall >= 95:
            return {
                "level": "GOLD",
                "badge": "Certified - Gold",
                "validity_days": 30
            }
        elif decision in ("GO", "FAST-TRACK GO") and score.overall >= 80:
            return {
                "level": "SILVER",
                "badge": "Certified - Silver",
                "validity_days": 14
            }
        elif decision == "CONDITIONAL-GO":
            return {
                "level": "BRONZE",
                "badge": "Certified - Bronze",
                "validity_days": 7
            }
        else:
            return {
                "level": "NONE",
                "badge": "Not Certified",
                "validity_days": 0
            }

    def _generate_next_steps(self, recommendation: dict) -> list[str]:
        """Generate recommended next steps."""
        decision = recommendation["decision"]

        if decision == "NO-GO":
            return [
                "Address all critical blockers before re-testing",
                "Run full test suite after fixes",
                "Escalate to senior management if blockers cannot be resolved"
            ]
        elif decision == "CONDITIONAL-GO":
            return [
                "Implement monitoring for performance regressions",
                "Schedule follow-up security review within 48 hours",
                "Document known issues for release notes"
            ]
        else:
            return [
                "Proceed with release preparation",
                "Update release documentation",
                "Notify stakeholders of release timeline"
            ]

    def _generate_report_path(self) -> str:
        """Generate report file path."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"reports/release_certification_{timestamp}.json"

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
