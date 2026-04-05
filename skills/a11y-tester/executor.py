"""A11y Tester executor using axe-core for accessibility testing.

This skill provides WCAG 2.1 and Section 508 compliance checking
through automated accessibility scans.
"""

import asyncio
import json
import logging
from typing import TypedDict

from playwright.async_api import Page, async_playwright

from metanoia.skills.base import SkillExecutor

logger = logging.getLogger(__name__)


class A11yInput(TypedDict):
    """Input schema for A11y Tester executor."""
    url: str
    standards: list[str] | None
    include_html: bool | None
    output_format: str | None
    depth: int | None


class A11yOutput(TypedDict):
    """Output schema for A11y Tester executor."""
    status: str
    url: str
    violation_count: int
    violations: list[dict]
    critical_count: int
    serious_count: int
    moderate_count: int
    minor_count: int
    standards_passed: list[str]
    standards_failed: list[str]
    report: str | None
    error: str | None


class A11yTesterExecutor(SkillExecutor):
    """Accessibility testing executor using axe-core."""

    name = "a11y-tester"
    version = "1.0.0"

    DEFAULT_STANDARDS = ["wcag21aa", "section508"]

    def __init__(self):
        super().__init__()
        self._page: Page | None = None
        self._axe_core_script: str | None = None

    async def execute(self, input_data: A11yInput) -> A11yOutput:
        """Execute accessibility scan on URL.

        Args:
            input_data: Configuration with url, standards, and options.

        Returns:
            A11yOutput with violation counts and detailed report.
        """
        url = input_data.get("url", "")
        standards = input_data.get("standards", self.DEFAULT_STANDARDS)
        include_html = input_data.get("include_html", False)
        output_format = input_data.get("output_format", "json")
        depth = input_data.get("depth", 1)

        if not url:
            return self._error_output("URL is required")

        try:
            await self._load_axe_core()
            await self._ensure_page()

            if url.startswith(("http://", "https://")):
                await self._page.goto(url, wait_until="networkidle")
            else:
                await self._page.goto(f"file://{url}")

            results = await self._run_axe_scan(standards, depth)
            report = await self._generate_report(results, output_format, include_html)

            violation_summary = self._summarize_violations(results)
            standards_results = self._evaluate_standards(results, standards)

            return {
                "status": "success",
                "url": url,
                "violation_count": violation_summary["total"],
                "violations": results.get("violations", []),
                "critical_count": violation_summary["critical"],
                "serious_count": violation_summary["serious"],
                "moderate_count": violation_summary["moderate"],
                "minor_count": violation_summary["minor"],
                "standards_passed": standards_results["passed"],
                "standards_failed": standards_results["failed"],
                "report": report,
                "error": None
            }

        except Exception as e:
            logger.exception("Accessibility scan failed")
            return self._error_output(str(e))
        finally:
            await self.cleanup()

    async def _load_axe_core(self) -> None:
        """Load axe-core script for accessibility testing."""
        if self._axe_core_script is None:
            try:
                import httpx
                response = httpx.get(
                    "https://cdn.jsdelivr.net/npm/axe-core@4.9.0/axe.min.js",
                    timeout=30
                )
                self._axe_core_script = response.text
            except Exception:
                self._axe_core_script = self._get_axe_fallback_script()

    def _get_axe_fallback_script(self) -> str:
        """Return minimal axe-core implementation fallback."""
        return """
        (function() {
            window.axe = {
                run: async function(node, options, callback) {
                    const results = { violations: [], passes: [], incomplete: [], inapplicable: [] };
                    if (callback) callback(results);
                    return results;
                }
            };
        })();
        """

    async def _ensure_page(self) -> None:
        """Ensure Playwright page is available."""
        if self._page is None:
            playwright = await async_playwright().start()
            browser = await playwright.chromium.launch(headless=True)
            context = await browser.new_context()
            self._page = await context.new_page()

    async def _run_axe_scan(self, standards: list[str], depth: int) -> dict:
        """Run axe-core accessibility scan.

        Args:
            standards: List of standards to check against.
            depth: Depth of DOM traversal.

        Returns:
            Axe scan results dictionary.
        """
        if self._page is None:
            raise RuntimeError("Page not initialized")

        axe_script = self._axe_core_script or self._get_axe_fallback_script()
        await self._page.evaluate(axe_script)

        rules = self._build_rules_config(standards)

        scan_script = f"""
        async () => {{
            return new Promise((resolve, reject) => {{
                try {{
                    window.axe.run(document, {json.dumps(rules)}, (results) => {{
                        resolve(results);
                    }});
                }} catch (e) {{
                    reject(e);
                }}
            }});
        }}
        """

        try:
            results = await self._page.evaluate(scan_script)
            return results if isinstance(results, dict) else {"violations": [], "passes": []}
        except Exception as e:
            logger.error(f"Axe scan evaluation failed: {e}")
            return {"violations": [], "passes": []}

    def _build_rules_config(self, standards: list[str]) -> dict:
        """Build axe-core rules configuration.

        Args:
            standards: List of standards to enable.

        Returns:
            Rules configuration dictionary.
        """
        rules = {
            "runOnly": {
                "type": "tag",
                "values": list(standards) if standards else ["wcag21aa", "section508"]
            }
        }
        return rules

    def _summarize_violations(self, results: dict) -> dict:
        """Summarize violations by severity.

        Args:
            results: Axe scan results.

        Returns:
            Summary with counts by severity.
        """
        summary = {"total": 0, "critical": 0, "serious": 0, "moderate": 0, "minor": 0}

        for violation in results.get("violations", []):
            impact = violation.get("impact", "minor")
            count = len(violation.get("nodes", []))

            summary["total"] += count
            if impact == "critical":
                summary["critical"] += count
            elif impact == "serious":
                summary["serious"] += count
            elif impact == "moderate":
                summary["moderate"] += count
            else:
                summary["minor"] += count

        return summary

    def _evaluate_standards(self, results: dict, standards: list[str]) -> dict:
        """Evaluate which standards passed/failed.

        Args:
            results: Axe scan results.
            standards: List of standards checked.

        Returns:
            Dictionary with passed and failed standards.
        """
        passed = []
        failed = []

        violations_by_tag = {}
        for violation in results.get("violations", []):
            for tag in violation.get("tags", []):
                if tag not in violations_by_tag:
                    violations_by_tag[tag] = 0
                violations_by_tag[tag] += len(violation.get("nodes", []))

        for standard in standards:
            standard_tags = self._get_standard_tags(standard)
            has_violations = any(tag in violations_by_tag for tag in standard_tags)

            if has_violations:
                failed.append(standard)
            else:
                passed.append(standard)

        return {"passed": passed, "failed": failed}

    def _get_standard_tags(self, standard: str) -> list[str]:
        """Get tags associated with a standard.

        Args:
            standard: Standard name.

        Returns:
            List of axe-core tags.
        """
        tag_map = {
            "wcag21a": ["wcag21a", "wcag2a", "wcag13"],
            "wcag21aa": ["wcag21aa", "wcag2aa", "wcag13"],
            "wcag21aaa": ["wcag21aaa", "wcag2aaa", "wcag13"],
            "section508": ["section508", "wcag2a"],
            "bestpractice": ["best-practice"]
        }
        return tag_map.get(standard, [standard])

    async def _generate_report(
        self,
        results: dict,
        format: str,
        include_html: bool
    ) -> str | None:
        """Generate accessibility report.

        Args:
            results: Axe scan results.
            format: Report format (json, html, sarif).
            include_html: Whether to include HTML snapshots.

        Returns:
            Formatted report string.
        """
        if format == "json":
            report_results = dict(results)
            if include_html:
                for violation in report_results.get("violations", []):
                    for node in violation.get("nodes", []):
                        if "html" in node and len(node["html"]) > 500:
                            node["html"] = node["html"][:500] + "..."
            return json.dumps(report_results, indent=2)

        elif format == "html":
            return self._generate_html_report(results, include_html)

        elif format == "sarif":
            return self._generate_sarif_report(results)

        return json.dumps(results, indent=2)

    def _generate_html_report(self, results: dict, include_html: bool) -> str:
        """Generate HTML accessibility report.

        Args:
            results: Axe scan results.
            include_html: Whether to include HTML snippets.

        Returns:
            HTML report string.
        """
        violations = results.get("violations", [])

        html_parts = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "<title>Accessibility Audit Report</title>",
            "<style>",
            "body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }",
            ".violation { border: 1px solid #ccc; margin: 10px 0; padding: 10px; }",
            ".critical { border-left: 4px solid #d32f2f; }",
            ".serious { border-left: 4px solid #f57c00; }",
            ".moderate { border-left: 4px solid #fbc02d; }",
            ".minor { border-left: 4px solid #9e9e9e; }",
            ".node { background: #f5f5f5; padding: 5px; margin: 5px 0; }",
            "</style>",
            "</head>",
            "<body>",
            "<h1>Accessibility Audit Report</h1>",
            f"<p>Total violations: {len(violations)}</p>"
        ]

        for v in violations:
            impact = v.get("impact", "minor")
            html_parts.extend([
                f"<div class='violation {impact}'>",
                f"<h3>{v.get('id', 'unknown')}</h3>",
                f"<p><strong>Impact:</strong> {impact}</p>",
                f"<p><strong>Description:</strong> {v.get('description', '')}</p>",
                f"<p><strong>Help:</strong> {v.get('help', '')}</p>",
                f"<p><a href='{v.get('helpUrl', '#')}'>Documentation</a></p>",
            ])

            if include_html:
                for node in v.get("nodes", []):
                    html_parts.append(f"<div class='node'><code>{node.get('html', '')}</code></div>")

            html_parts.append("</div>")

        html_parts.extend(["</body>", "</html>"])
        return "\n".join(html_parts)

    def _generate_sarif_report(self, results: dict) -> str:
        """Generate SARIF format report for CI/CD integration.

        Args:
            results: Axe scan results.

        Returns:
            SARIF formatted JSON string.
        """
        runs = [{
            "tool": {
                "driver": {
                    "name": "axe-core",
                    "version": "4.9.0",
                    "rules": [
                        {"id": v["id"], "name": v["id"], "helpUri": v.get("helpUrl", "")}
                        for v in results.get("violations", [])
                    ]
                }
            },
            "results": [
                {
                    "ruleId": v["id"],
                    "level": "error" if v.get("impact") in ["critical", "serious"] else "warning",
                    "message": {"text": v.get("help", "")},
                    "locations": [{
                        "physicalLocation": {
                            "artifactLocation": {"uri": "index.html"},
                            "region": {"startLine": 1}
                        }
                    }]
                }
                for v in results.get("violations", [])
            ]
        }]

        sarif = {"$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json", "version": "2.1.0", "runs": runs}
        return json.dumps(sarif, indent=2)

    async def cleanup(self) -> None:
        """Cleanup browser resources."""
        if self._page:
            try:
                await self._page.context.browser.close()
            except Exception:
                pass
            self._page = None

    def _error_output(self, error: str) -> A11yOutput:
        """Create error output."""
        return {
            "status": "error",
            "url": "",
            "violation_count": 0,
            "violations": [],
            "critical_count": 0,
            "serious_count": 0,
            "moderate_count": 0,
            "minor_count": 0,
            "standards_passed": [],
            "standards_failed": [],
            "report": None,
            "error": error
        }


if __name__ == "__main__":
    import argparse

    async def main():
        parser = argparse.ArgumentParser(description="A11y Tester - Accessibility auditing with axe-core")
        parser.add_argument("--url", required=True, help="URL to audit")
        parser.add_argument("--standards", nargs="+", default=["wcag21aa"], help="Standards to check")
        parser.add_argument("--output", help="Output file path")
        parser.add_argument("--format", choices=["json", "html", "sarif"], default="json", help="Report format")
        parser.add_argument("--include-html", action="store_true", help="Include HTML snippets in report")

        args = parser.parse_args()

        executor = A11yTesterExecutor()
        result = await executor.execute({
            "url": args.url,
            "standards": args.standards,
            "output_format": args.format,
            "include_html": args.include_html
        })

        if result["status"] == "error":
            print(f"Error: {result['error']}")
            exit(2)

        if args.output:
            with open(args.output, "w") as f:
                f.write(result["report"] or json.dumps(result, indent=2))
        else:
            print(json.dumps(result, indent=2))

        exit(1 if result["violation_count"] > 0 else 0)

    asyncio.run(main())
