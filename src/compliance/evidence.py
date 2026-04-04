"""Evidence collection for compliance reports.

Collects evidence from various sources for compliance reporting.
"""

from typing import Optional
from datetime import datetime


class EvidenceCollector:
    """Collects evidence from various sources for compliance reporting.

    Sources include:
    - Test execution results
    - Security scan reports
    - Agent activity logs
    - Code review records
    """

    def __init__(self, supabase_client):
        """Initialize the evidence collector.

        Args:
            supabase_client: Supabase client for data access
        """
        self.supabase = supabase_client

    async def collect_test_results(
        self,
        sprint_ids: list[str],
        start_date: datetime,
        end_date: datetime
    ) -> list[dict]:
        """Collect test execution evidence.

        Args:
            sprint_ids: List of sprint IDs to collect from
            start_date: Start of date range
            end_date: End of date range

        Returns:
            List of test result evidence items
        """
        evidence = []

        try:
            if sprint_ids:
                query = self.supabase.table("test_results").select("*").in_(
                    "sprint_id", sprint_ids
                )
            else:
                query = self.supabase.table("test_results").select("*")

            query = query.gte("created_at", start_date.isoformat()).lte(
                "created_at", end_date.isoformat()
            )

            result = query.execute()

            for record in result.data:
                evidence.append({
                    "type": "test_results",
                    "source": "test_execution",
                    "sprint_id": record.get("sprint_id"),
                    "timestamp": record.get("created_at"),
                    "content": {
                        "total_tests": record.get("total_tests", 0),
                        "passed": record.get("passed", 0),
                        "failed": record.get("failed", 0),
                        "skipped": record.get("skipped", 0),
                        "duration_seconds": record.get("duration_seconds", 0),
                    },
                    "evidence_types": ["test_execution_logs", "test_results"]
                })

        except Exception as e:
            evidence.append({
                "type": "test_results",
                "source": "test_execution",
                "error": str(e),
                "content": {},
                "evidence_types": ["test_results"]
            })

        return evidence

    async def collect_security_evidence(
        self,
        sprint_ids: list[str]
    ) -> list[dict]:
        """Collect security scan evidence.

        Args:
            sprint_ids: List of sprint IDs to collect from

        Returns:
            List of security evidence items
        """
        evidence = []

        security_sources = [
            ("security_scan_results", "security_scans"),
            ("zap_scan_reports", "zap_scans"),
            ("dependency_audits", "dependency_audit"),
            ("vulnerability_reports", "vulnerability_scans"),
        ]

        for table_name, source_type in security_sources:
            try:
                if sprint_ids:
                    query = self.supabase.table(table_name).select("*").in_(
                        "sprint_id", sprint_ids
                    )
                else:
                    query = self.supabase.table(table_name).select("*")

                result = query.execute()

                for record in result.data:
                    evidence.append({
                        "type": source_type,
                        "source": source_type,
                        "sprint_id": record.get("sprint_id"),
                        "timestamp": record.get("created_at"),
                        "content": {
                            "vulnerabilities_found": record.get("vulnerabilities_found", 0),
                            "critical": record.get("critical", 0),
                            "high": record.get("high", 0),
                            "medium": record.get("medium", 0),
                            "low": record.get("low", 0),
                        },
                        "evidence_types": ["security_scan_results", source_type]
                    })

            except Exception as e:
                evidence.append({
                    "type": source_type,
                    "source": source_type,
                    "error": str(e),
                    "content": {},
                    "evidence_types": ["security_scan_results"]
                })

        return evidence

    async def collect_agent_audit_trail(
        self,
        sprint_ids: list[str]
    ) -> list[dict]:
        """Collect agent activity logs.

        Args:
            sprint_ids: List of sprint IDs to collect from

        Returns:
            List of agent audit trail evidence items
        """
        evidence = []

        try:
            if sprint_ids:
                query = self.supabase.table("agent_logs").select("*").in_(
                    "sprint_id", sprint_ids
                )
            else:
                query = self.supabase.table("agent_logs").select("*")

            result = query.execute()

            agent_counts: dict[str, int] = {}
            for record in result.data:
                agent_type = record.get("agent_type", "unknown")
                agent_counts[agent_type] = agent_counts.get(agent_type, 0) + 1

            evidence.append({
                "type": "agent_audit_trail",
                "source": "agent_logs",
                "sprint_ids": sprint_ids,
                "timestamp": datetime.utcnow().isoformat(),
                "content": {
                    "total_operations": len(result.data),
                    "agents_active": len(agent_counts),
                    "agent_breakdown": agent_counts,
                },
                "evidence_types": ["agent_audit_trail"]
            })

        except Exception as e:
            evidence.append({
                "type": "agent_audit_trail",
                "source": "agent_logs",
                "error": str(e),
                "content": {},
                "evidence_types": ["agent_audit_trail"]
            })

        return evidence

    async def collect_code_review_evidence(
        self,
        sprint_ids: list[str]
    ) -> list[dict]:
        """Collect code review and quality metrics.

        Args:
            sprint_ids: List of sprint IDs to collect from

        Returns:
            List of code review evidence items
        """
        evidence = []

        code_review_sources = [
            ("code_review_logs", "code_reviews"),
            ("code_quality_metrics", "quality_metrics"),
        ]

        for table_name, source_type in code_review_sources:
            try:
                if sprint_ids:
                    query = self.supabase.table(table_name).select("*").in_(
                        "sprint_id", sprint_ids
                    )
                else:
                    query = self.supabase.table(table_name).select("*")

                result = query.execute()

                for record in result.data:
                    evidence.append({
                        "type": source_type,
                        "source": source_type,
                        "sprint_id": record.get("sprint_id"),
                        "timestamp": record.get("created_at"),
                        "content": {
                            "reviews_completed": record.get("reviews_completed", 0),
                            "issues_found": record.get("issues_found", 0),
                            "issues_resolved": record.get("issues_resolved", 0),
                            "coverage_percentage": record.get("coverage_percentage", 0),
                        },
                        "evidence_types": ["code_review_logs", "code_quality_metrics"]
                    })

            except Exception as e:
                evidence.append({
                    "type": source_type,
                    "source": source_type,
                    "error": str(e),
                    "content": {},
                    "evidence_types": ["code_review_logs"]
                })

        return evidence
