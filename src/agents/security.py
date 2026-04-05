"""Security Test Engineer agent for Metanoia-QA.

Executes OWASP ZAP scans and API fuzzing for vulnerability detection.
"""

import asyncio
import logging
from typing import Optional, Any

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class SecurityFinding(BaseModel):
    """A security vulnerability finding."""
    vuln_type: str
    severity: str
    url: str
    param: Optional[str] = None
    evidence: Optional[str] = None
    cwe_id: Optional[str] = None
    wasc_id: Optional[str] = None


class TestResult(BaseModel):
    """Result of security test execution."""
    passed: int
    failed: int
    skipped: int
    duration: float
    report_url: Optional[str] = None
    findings: list[SecurityFinding] = []
    owasp_top_10: dict = {}


class SecurityEngineer:
    """Security Test Engineer that runs ZAP scans and API fuzzing.
    
    Responsibilities:
    - Run OWASP ZAP scans using zap-executor skill
    - Perform API fuzzing
    - Check for OWASP Top 10 vulnerabilities
    - Generate security report
    - Integrate with skill_runtime (zap-executor)
    
    Note: zap-executor skill not yet implemented. Using subprocess approach.
    """

    name = "security-engineer"
    version = "1.0.0"

    OWASP_TOP_10_2021 = {
        "A01": "Broken Access Control",
        "A02": "Cryptographic Failures",
        "A03": "Injection",
        "A04": "Insecure Design",
        "A05": "Security Misconfiguration",
        "A06": "Vulnerable Components",
        "A07": "Authentication Failures",
        "A08": "Software Integrity Failures",
        "A09": "Logging Failures",
        "A10": "SSRF"
    }

    def __init__(self):
        from skill_runtime.loader import SkillLoader
        self._skill_loader = SkillLoader()
        self._zap_executor = None
        self._scan_results: list[SecurityFinding] = []

    async def execute(self, test_cases: list[dict], context: dict) -> TestResult:
        """Execute security tests and return results.
        
        Args:
            test_cases: List of target configurations (urls, endpoints).
            context: Execution context with target_url, scan_type, etc.
            
        Returns:
            TestResult with findings and OWASP Top 10 mapping.
        """
        target_url = context.get("target_url", context.get("base_url", "http://localhost:3000"))
        scan_type = context.get("scan_type", "quick")

        findings: list[SecurityFinding] = []
        duration = 0.0

        zap_executor = self._get_zap_executor()

        try:
            if zap_executor:
                result = await self._execute_zap_scan(zap_executor, target_url, scan_type)
                findings = result.get("findings", [])
                duration = result.get("duration", 0.0)
            else:
                findings = await self._execute_basic_scan(target_url, test_cases)

            owasp_mapping = self._map_to_owasp_top_10(findings)
            
            critical_findings = [f for f in findings if f.severity in ("critical", "high")]
            
            return TestResult(
                passed=1 if len(critical_findings) == 0 else 0,
                failed=len(critical_findings),
                skipped=len(findings) - len(critical_findings),
                duration=duration,
                findings=findings,
                owasp_top_10=owasp_mapping
            )

        except Exception:
            logger.exception("Security test execution failed")
            return TestResult(
                passed=0,
                failed=1,
                skipped=0,
                duration=duration,
                findings=[],
                owasp_top_10={}
            )

    async def heal(self, failure: dict) -> dict:
        """Attempt to remediate or investigate a security finding.
        
        Args:
            failure: Security finding to investigate.
            
        Returns:
            Investigation result with recommendations.
        """
        vuln_type = failure.get("vuln_type", "")
        failure.get("url", "")
        
        recommendations = []
        
        if "sql" in vuln_type.lower() or "injection" in vuln_type.lower():
            recommendations.append({
                "type": "input_validation",
                "suggestion": "Implement parameterized queries",
                "priority": "high"
            })
            
        if "xss" in vuln_type.lower():
            recommendations.append({
                "type": "output_encoding",
                "suggestion": "Implement proper output encoding",
                "priority": "high"
            })
            
        if "auth" in vuln_type.lower() or "access" in vuln_type.lower():
            recommendations.append({
                "type": "access_control",
                "suggestion": "Review and fix access control checks",
                "priority": "high"
            })

        return {
            "status": "analyzed",
            "finding": failure,
            "recommendations": recommendations
        }

    def generate_security_report(self) -> dict:
        """Generate comprehensive security report.
        
        Returns:
            Security report with findings and remediation steps.
        """
        return {
            "title": "Security Scan Report",
            "summary": self._generate_executive_summary(),
            "findings": [f.model_dump() for f in self._scan_results],
            "owasp_top_10": self._map_to_owasp_top_10(self._scan_results),
            "remediation": self._generate_remediation_plan()
        }

    def get_findings(self) -> list[SecurityFinding]:
        """Get all security findings from scans."""
        return self._scan_results.copy()

    def _get_zap_executor(self):
        """Get or create ZAP executor from skill_runtime."""
        if self._zap_executor is None:
            try:
                from skill_runtime.loader import SkillLoader
                self._skill_loader = SkillLoader()
                executor_class = self._skill_loader.load_skill("zap-executor")
                if executor_class:
                    self._zap_executor = executor_class()
            except Exception as e:
                logger.warning(f"Failed to load zap-executor skill: {e}")
                self._zap_executor = None
        return self._zap_executor

    async def _execute_zap_scan(
        self,
        executor: Any,
        target_url: str,
        scan_type: str
    ) -> dict:
        """Execute ZAP scan using skill executor."""
        input_data = {
            "target": target_url,
            "scan_type": scan_type,
            "zap_options": {
                "spider": True,
                "active_scan": True,
                "passive_scan": True
            }
        }
        
        from skill_runtime.executor import create_executor
        engine = create_executor(timeout_seconds=1800.0)
        result = await engine.execute(executor, input_data)
        
        if result["status"] == "success":
            return dict(result.get("data", {})) if result.get("data") else {"findings": [], "duration": 0.0}
        return {"findings": [], "duration": 0.0}

    async def _execute_basic_scan(
        self,
        target_url: str,
        test_cases: list[dict]
    ) -> list[SecurityFinding]:
        """Execute basic security checks without ZAP."""
        findings: list[SecurityFinding] = []
        
        await asyncio.sleep(0.1)
        
        fuzz_results = await self._fuzz_endpoints(target_url, test_cases)
        findings.extend(fuzz_results)
        
        self._scan_results.extend(findings)
        
        return findings

    async def _fuzz_endpoints(
        self,
        base_url: str,
        endpoints: list[dict]
    ) -> list[SecurityFinding]:
        """Perform basic API fuzzing.
        
        Args:
            base_url: Base URL for fuzzing.
            endpoints: List of endpoint configs.
            
        Returns:
            List of security findings from fuzzing.
        """
        findings: list[SecurityFinding] = []
        
        fuzz_patterns = [
            ("'", "sql_injection", "SQL Injection"),
            ("<script>alert('xss')</script>", "xss", "Cross-Site Scripting"),
            ("../../../../etc/passwd", "path_traversal", "Path Traversal"),
            ("${7*7}", "ssti", "Server-Side Template Injection"),
        ]
        
        for endpoint in endpoints:
            url = base_url + endpoint.get("path", "")
            
            for payload, vuln_type, description in fuzz_patterns:
                try:
                    result = await self._test_payload(url, payload, endpoint)
                    if result.get("vulnerable"):
                        findings.append(SecurityFinding(
                            vuln_type=vuln_type,
                            severity=result.get("severity", "medium"),
                            url=url,
                            param=endpoint.get("param", ""),
                            evidence=f"Payload: {payload}",
                            cwe_id=self._get_cwe_id(vuln_type)
                        ))
                except Exception as e:
                    logger.debug(f"Fuzz test failed for {url}: {e}")

        return findings

    async def _test_payload(
        self,
        url: str,
        payload: str,
        endpoint: dict
    ) -> dict:
        """Test a single payload against an endpoint.
        
        Returns:
            Dict with vulnerable=True/False and severity.
        """
        import httpx
        
        method = endpoint.get("method", "GET").upper()
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                if method == "GET":
                    response = await client.get(url, params={"q": payload})
                else:
                    response = await client.request(
                        method,
                        url,
                        json={endpoint.get("param", "data"): payload}
                    )
                
                response_text = response.text.lower()
                
                if "<script>" in payload.lower() and "<script>" in response_text:
                    return {"vulnerable": True, "severity": "high"}
                    
                if "sql" in payload and any(x in response_text for x in ["syntax", "error", "mysql", "postgres", "sqlite"]):
                    return {"vulnerable": True, "severity": "critical"}
                    
                if "root:" in response_text or "etc/passwd" in response_text:
                    return {"vulnerable": True, "severity": "high"}
                    
                if "${" in payload and "49" in response_text:
                    return {"vulnerable": True, "severity": "high"}
                    
        except Exception:
            pass
        
        return {"vulnerable": False}

    def _map_to_owasp_top_10(self, findings: list[SecurityFinding]) -> dict:
        """Map findings to OWASP Top 10 categories.
        
        Returns:
            Dict with OWASP categories and finding counts.
        """
        mapping: dict[str, dict[str, Any]] = {
            code: {"name": name, "count": 0, "findings": []} 
            for code, name in self.OWASP_TOP_10_2021.items()
        }
        
        category_keywords: dict[str, list[str]] = {
            "A01": ["access", "authorization", "idor", "broken"],
            "A02": ["crypto", "encryption", "password", "hash"],
            "A03": ["injection", "sql", "xss", "ssti", "command"],
            "A04": ["design", "weak", "missing"],
            "A05": ["config", "misconfiguration", "default", "error"],
            "A06": ["component", "dependency", "library", "version"],
            "A07": ["auth", "credential", "session", "password"],
            "A08": ["integrity", "signature", "trusted"],
            "A09": ["logging", "monitoring", "detection"],
            "A10": ["ssrf", "url", "redirect"]
        }
        
        for finding in findings:
            vuln_lower = finding.vuln_type.lower()
            for code, keywords in category_keywords.items():
                if any(kw in vuln_lower for kw in keywords):
                    mapping[code]["count"] += 1
                    mapping[code]["findings"].append(finding.model_dump())
                    break

        return mapping

    def _get_cwe_id(self, vuln_type: str) -> Optional[str]:
        """Map vulnerability type to CWE ID."""
        cwe_map = {
            "sql_injection": "CWE-89",
            "xss": "CWE-79",
            "path_traversal": "CWE-22",
            "ssti": "CWE-1336",
            "ssrf": "CWE-918"
        }
        return cwe_map.get(vuln_type.lower())

    def _generate_executive_summary(self) -> str:
        """Generate executive summary of security scan."""
        total = len(self._scan_results)
        critical = len([f for f in self._scan_results if f.severity == "critical"])
        high = len([f for f in self._scan_results if f.severity == "high"])
        
        return f"""Security scan completed.
        
Total findings: {total}
Critical: {critical}
High: {high}

{'Recommendation: Fix critical and high severity issues before release.' if critical > 0 else 'No critical issues found.'}
"""

    def _generate_remediation_plan(self) -> list[dict]:
        """Generate prioritized remediation plan."""
        plan = []
        
        by_severity: dict[str, list[SecurityFinding]] = {}
        for finding in self._scan_results:
            severity = finding.severity
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append(finding)
        
        severity_order = ["critical", "high", "medium", "low"]
        
        for severity in severity_order:
            for finding in by_severity.get(severity, []):
                remediation = self._get_remediation(finding.vuln_type)
                if remediation:
                    plan.append({
                        "priority": severity,
                        "vulnerability": finding.vuln_type,
                        "url": finding.url,
                        "remediation": remediation
                    })
        
        return plan

    def _get_remediation(self, vuln_type: str) -> Optional[str]:
        """Get remediation steps for vulnerability type."""
        remediations = {
            "sql_injection": "Use parameterized queries or ORM. Never concatenate user input into SQL.",
            "xss": "Implement output encoding. Use Content-Security-Policy headers.",
            "path_traversal": "Validate and sanitize file paths. Use allowlists for permitted paths.",
            "ssti": "Avoid rendering user input in templates. Use sandboxed template engines.",
            "ssrf": "Implement URL validation. Use allowlists for permitted destinations."
        }
        return remediations.get(vuln_type.lower())
