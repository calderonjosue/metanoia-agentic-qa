"""Tests for quality gate."""

import pytest

from src.ci.quality_gate import QualityGate


class TestQualityGate:
    """Tests for QualityGate."""

    @pytest.fixture
    def quality_gate(self):
        """Create a QualityGate instance."""
        return QualityGate()

    def test_threshold_95_passes(self, quality_gate):
        """Test threshold_95_passes passes when score >= 95."""
        results = {
            "passed": 95,
            "failed": 5,
            "skipped": 0
        }
        passed = quality_gate.check_threshold(results, threshold=95)
        assert passed is True

    def test_threshold_94_fails(self, quality_gate):
        """Test threshold_94_fails fails when score < 95."""
        results = {
            "passed": 94,
            "failed": 6,
            "skipped": 0
        }
        passed = quality_gate.check_threshold(results, threshold=95)
        assert passed is False

    def test_calculate_score_from_results(self, quality_gate):
        """Test calculate_score_from_results computes correct percentage."""
        results = {
            "passed": 190,
            "failed": 10,
            "skipped": 0
        }
        score = quality_gate.calculate_score(results)
        assert score == 95.0

    def test_calculate_score_with_skipped(self, quality_gate):
        """Test calculate_score ignores skipped tests."""
        results = {
            "passed": 90,
            "failed": 5,
            "skipped": 5
        }
        score = quality_gate.calculate_score(results)
        assert score == 90.0
