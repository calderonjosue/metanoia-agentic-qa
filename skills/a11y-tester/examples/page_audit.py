"""Example: Page accessibility audit using axe-core.

This example demonstrates how to run a full accessibility audit
on a web page and generate a detailed violation report.
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from metanoia.skills.a11y_tester.executor import A11yTesterExecutor


async def audit_page(
    url: str,
    standards: list[str] | None = None,
    output_file: str | None = None,
    format: str = "json"
) -> dict:
    """Run accessibility audit on a page.

    Args:
        url: URL to audit.
        standards: List of standards to check.
        output_file: Optional file to write report.
        format: Report format (json, html, sarif).

    Returns:
        Audit results dictionary.
    """
    if standards is None:
        standards = ["wcag21aa", "section508"]

    executor = A11yTesterExecutor()

    print(f"Starting accessibility audit for: {url}")
    print(f"Standards: {', '.join(standards)}")
    print("-" * 50)

    result = await executor.execute({
        "url": url,
        "standards": standards,
        "include_html": True,
        "output_format": format
    })

    print_audit_summary(result)

    if output_file:
        write_report(output_file, result, format)
        print(f"\nReport written to: {output_file}")

    return result


def print_audit_summary(result: dict) -> None:
    """Print audit summary to console.

    Args:
        result: Audit results dictionary.
    """
    if result["status"] == "error":
        print(f"ERROR: {result['error']}")
        return

    print(f"\nAudit Status: {result['status'].upper()}")
    print(f"URL: {result['url']}")
    print("\nViolation Summary:")
    print(f"  Critical: {result['critical_count']}")
    print(f"  Serious:  {result['serious_count']}")
    print(f"  Moderate: {result['moderate_count']}")
    print(f"  Minor:    {result['minor_count']}")
    print(f"  TOTAL:    {result['violation_count']}")

    if result["standards_passed"]:
        print(f"\nStandards Passed: {', '.join(result['standards_passed'])}")
    if result["standards_failed"]:
        print(f"Standards Failed: {', '.join(result['standards_failed'])}")

    if result["violation_count"] > 0:
        print("\nTop Violations:")
        for i, violation in enumerate(result["violations"][:5], 1):
            print(f"  {i}. [{violation['impact'].upper()}] {violation['id']}")
            print(f"     {violation.get('help', violation.get('description', ''))[:80]}...")


def write_report(output_file: str, result: dict, format: str) -> None:
    """Write audit report to file.

    Args:
        output_file: Path to output file.
        result: Audit results.
        format: Report format.
    """
    report = result.get("report")

    if report is None:
        report = json.dumps(result, indent=2)

    Path(output_file).write_text(report)


async def main():
    """Main entry point for example."""
    urls_to_test = [
        "https://example.com",
        "https://www.w3.org/WAI/demos/bad/",
    ]

    for url in urls_to_test:
        print(f"\n{'='*60}")
        print(f"Testing: {url}")
        print('='*60)

        try:
            await audit_page(
                url,
                standards=["wcag21aa"],
                output_file=f"a11y-report-{url.replace('://', '-').replace('/', '-')}.json"
            )
        except Exception as e:
            print(f"Failed to audit {url}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
