"""Quality gate for evaluating test results against thresholds.

This module provides quality gate evaluation based on test coverage,
regression scores, and other quality metrics.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class QualityGateResult:
    """Result of quality gate evaluation.

    Attributes:
        passed: Whether the quality gate passed
        score: The computed quality score (0.0 to 1.0)
        threshold: The threshold that was used for evaluation
        reasons: List of reasons for pass/fail
        details: Additional details about the evaluation
    """

    passed: bool
    score: float
    threshold: float
    reasons: list[str] = None
    details: dict[str, Any] = None

    def __post_init__(self):
        if self.reasons is None:
            self.reasons = []
        if self.details is None:
            self.details = {}


class QualityGate:
    """Quality gate with configurable threshold.

    Evaluates test results and quality metrics against a threshold
    to determine if code is ready for merge.

    Attributes:
        threshold: Minimum score required to pass (default 0.95)
    """

    def __init__(self, threshold: float = 0.95):
        """Initialize quality gate.

        Args:
            threshold: Minimum score (0.0 to 1.0) required to pass.
                      Defaults to 0.95 (95%).
        """
        self.threshold = threshold

    def evaluate(self, test_results: dict[str, Any]) -> tuple[bool, float]:
        """Evaluate test results against the quality threshold.

        Args:
            test_results: Dictionary containing test results with keys:
                - regression_score: float (0.0 to 1.0) - main quality metric
                - coverage: float (0.0 to 1.0) - code coverage percentage
                - passed_tests: int - number of passing tests
                - failed_tests: int - number of failing tests
                - total_tests: int - total number of tests

        Returns:
            Tuple of (passed: bool, score: float)
        """
        regression_score = test_results.get("regression_score", 0.0)
        coverage = test_results.get("coverage", 0.0)
        passed_tests = test_results.get("passed_tests", 0)
        failed_tests = test_results.get("failed_tests", 0)
        total_tests = test_results.get("total_tests", 1)

        if total_tests == 0:
            return False, 0.0

        test_pass_rate = passed_tests / total_tests if total_tests > 0 else 0.0

        combined_score = (
            regression_score * 0.5 + coverage * 0.3 + test_pass_rate * 0.2
        )

        passed = combined_score >= self.threshold

        return passed, combined_score

    def evaluate_detailed(self, test_results: dict[str, Any]) -> QualityGateResult:
        """Evaluate test results with detailed reasons.

        Args:
            test_results: Dictionary containing test results

        Returns:
            QualityGateResult with pass/fail and detailed reasons
        """
        passed, score = self.evaluate(test_results)
        reasons = []

        regression_score = test_results.get("regression_score", 0.0)
        coverage = test_results.get("coverage", 0.0)
        passed_tests = test_results.get("passed_tests", 0)
        failed_tests = test_results.get("failed_tests", 0)
        total_tests = test_results.get("total_tests", 1)

        if regression_score < self.threshold:
            reasons.append(
                f"Regression score {regression_score:.2%} below threshold {self.threshold:.2%}"
            )
        else:
            reasons.append(
                f"Regression score {regression_score:.2%} meets threshold"
            )

        if coverage < 0.8:
            reasons.append(f"Coverage {coverage:.2%} below recommended 80%")
        else:
            reasons.append(f"Coverage {coverage:.2%} acceptable")

        if failed_tests > 0:
            reasons.append(f"{failed_tests} test(s) failing")
        else:
            reasons.append("All tests passing")

        details = {
            "regression_score": regression_score,
            "coverage": coverage,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "total_tests": total_tests,
            "test_pass_rate": passed_tests / total_tests if total_tests > 0 else 0.0,
        }

        return QualityGateResult(
            passed=passed,
            score=score,
            threshold=self.threshold,
            reasons=reasons,
            details=details,
        )
