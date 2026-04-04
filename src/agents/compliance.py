"""Compliance Reports Agent for Metanoia-QA.

Generates compliance reports for:
- SOC 2 Type II
- ISO 27001
- HIPAA
- GDPR
"""

from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class ComplianceFramework(str, Enum):
    """Supported compliance frameworks."""
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    HIPAA = "hipaa"
    GDPR = "gdpr"


class ComplianceRequirement(BaseModel):
    """A single compliance requirement within a framework."""
    id: str
    framework: ComplianceFramework
    control_id: str
    description: str
    evidence_required: list[str]
    automated: bool


class ComplianceReport(BaseModel):
    """Complete compliance report for a framework."""
    framework: ComplianceFramework
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    coverage_percentage: float
    controls_passed: int
    controls_failed: int
    controls_not_applicable: int
    evidence: list[dict]
    gaps: list[dict]
    recommendation: str


class ComplianceAgent:
    """Generates compliance reports with automated evidence collection.

    Responsibilities:
    - Pre-built report templates for SOC2, ISO27001, HIPAA, GDPR
    - Automated evidence collection from test results and agent logs
    - Audit trail generation
    - Compliance score calculation
    """

    def __init__(self, supabase_client):
        """Initialize the compliance agent.

        Args:
            supabase_client: Supabase client for data access
        """
        self.supabase = supabase_client
        self._framework_templates = {}
        self._load_templates()

    def _load_templates(self) -> None:
        """Load compliance framework templates."""
        from src.compliance.templates import soc2_template, iso27001_template

        self._framework_templates = {
            ComplianceFramework.SOC2: soc2_template.SOC2_CONTROLS,
            ComplianceFramework.ISO27001: iso27001_template.ISO27001_CONTROLS,
        }

    async def generate_report(
        self,
        framework: ComplianceFramework,
        period_start: datetime,
        period_end: datetime,
        sprint_ids: Optional[list[str]] = None
    ) -> ComplianceReport:
        """Generate a compliance report for the given framework.

        Args:
            framework: The compliance framework to report on
            period_start: Start of the reporting period
            period_end: End of the reporting period
            sprint_ids: Optional list of specific sprints to include

        Returns:
            ComplianceReport with assessment results
        """
        evidence = await self.collect_evidence(framework, sprint_ids or [])

        controls = self._framework_templates.get(framework, {})
        assessment = await self.assess_controls(framework, evidence)

        controls_passed = assessment.get("passed", 0)
        controls_failed = assessment.get("failed", 0)
        controls_na = assessment.get("not_applicable", 0)

        total_controls = len(controls)
        if total_controls > 0:
            coverage = ((controls_passed + controls_na) / total_controls) * 100
        else:
            coverage = 0.0

        compliance_score = self.calculate_compliance_score(
            controls_passed, controls_failed, controls_na
        )

        gaps = assessment.get("gaps", [])
        recommendation = self._generate_recommendation(
            compliance_score, gaps
        )

        return ComplianceReport(
            framework=framework,
            generated_at=datetime.utcnow(),
            period_start=period_start,
            period_end=period_end,
            coverage_percentage=coverage,
            controls_passed=controls_passed,
            controls_failed=controls_failed,
            controls_not_applicable=controls_na,
            evidence=evidence,
            gaps=gaps,
            recommendation=recommendation,
        )

    async def collect_evidence(
        self,
        framework: ComplianceFramework,
        sprint_ids: list[str]
    ) -> list[dict]:
        """Collect evidence from test results and agent logs.

        Args:
            framework: The compliance framework
            sprint_ids: List of sprint IDs to collect evidence from

        Returns:
            List of evidence items with source, timestamp, and content
        """
        from src.compliance.evidence import EvidenceCollector

        collector = EvidenceCollector(self.supabase)

        evidence = []

        test_results = await collector.collect_test_results(
            sprint_ids,
            datetime.utcnow(),
            datetime.utcnow()
        )
        evidence.extend(test_results)

        security_evidence = await collector.collect_security_evidence(sprint_ids)
        evidence.extend(security_evidence)

        audit_trail = await collector.collect_agent_audit_trail(sprint_ids)
        evidence.extend(audit_trail)

        code_review = await collector.collect_code_review_evidence(sprint_ids)
        evidence.extend(code_review)

        return evidence

    async def assess_controls(
        self,
        framework: ComplianceFramework,
        evidence: list[dict]
    ) -> dict:
        """Assess compliance of individual controls.

        Args:
            framework: The compliance framework
            evidence: Collected evidence to assess against

        Returns:
            Dict with passed/failed counts and gap details
        """
        controls = self._framework_templates.get(framework, {})

        evidence_by_type = self._categorize_evidence(evidence)

        passed = 0
        failed = 0
        not_applicable = 0
        gaps = []

        for control_id, control_def in controls.items():
            required_evidence = control_def.get("evidence", [])
            control_passed = True

            for req_evidence in required_evidence:
                if req_evidence not in evidence_by_type:
                    control_passed = False
                    gaps.append({
                        "control_id": control_id,
                        "framework": framework.value,
                        "missing_evidence": req_evidence,
                        "severity": "high",
                        "description": f"Missing required evidence: {req_evidence}"
                    })

            if control_passed:
                passed += 1
            else:
                failed += 1

        return {
            "passed": passed,
            "failed": failed,
            "not_applicable": not_applicable,
            "gaps": gaps,
        }

    def calculate_compliance_score(
        self,
        controls_passed: int,
        controls_failed: int,
        controls_na: int
    ) -> float:
        """Calculate overall compliance score.

        Args:
            controls_passed: Number of controls that passed
            controls_failed: Number of controls that failed
            controls_na: Number of controls not applicable

        Returns:
            Compliance score as a percentage (0-100)
        """
        total_applicable = controls_passed + controls_failed
        if total_applicable == 0:
            return 100.0

        score = (controls_passed / total_applicable) * 100
        return round(score, 2)

    def _categorize_evidence(self, evidence: list[dict]) -> dict[str, list[dict]]:
        """Categorize evidence by type for control assessment."""
        categorized: dict[str, list[dict]] = {}
        for item in evidence:
            evidence_type = item.get("type", "unknown")
            if evidence_type not in categorized:
                categorized[evidence_type] = []
            categorized[evidence_type].append(item)
        return categorized

    def _generate_recommendation(self, score: float, gaps: list[dict]) -> str:
        """Generate compliance recommendation based on score and gaps."""
        if score >= 95:
            return "Compliance posture is excellent. Continue monitoring."
        elif score >= 80:
            return "Good compliance posture. Address identified gaps promptly."
        elif score >= 60:
            return "Moderate compliance risk. Prioritize remediation of high-severity gaps."
        else:
            critical_gaps = [g for g in gaps if g.get("severity") == "high"]
            return f"Significant compliance gaps identified. {len(critical_gaps)} critical items require immediate attention."
