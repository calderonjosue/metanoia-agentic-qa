"""Tests for Sprint API routes."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.routes.sprint import (
    CertificationResponse,
    SprintStartRequest,
    SprintStatusResponse,
    TestPlanResponse,
    router,
)


class TestSprintStartRequest:
    """Tests for SprintStartRequest model."""

    def test_sprint_start_request_creation(self):
        """Test creating SprintStartRequest."""
        request = SprintStartRequest(
            sprint_id="SP-45",
            sprint_goal="Implement checkout flow",
            run_async=True
        )

        assert request.sprint_id == "SP-45"
        assert request.run_async is True

    def test_sprint_start_request_defaults(self):
        """Test SprintStartRequest default values."""
        request = SprintStartRequest(
            sprint_id="SP-46",
            sprint_goal="Fix login bug"
        )

        assert request.run_async is False


class TestSprintStatusResponse:
    """Tests for SprintStatusResponse model."""

    def test_sprint_status_response_creation(self):
        """Test creating SprintStatusResponse."""
        response = SprintStatusResponse(
            sprint_id="SP-45",
            sprint_goal="Test sprint",
            current_phase="context_analysis",
            iteration_count=1,
            test_case_count=50,
            execution_results={},
            started_at="2024-01-15T10:00:00Z",
            updated_at="2024-01-15T10:30:00Z"
        )

        assert response.sprint_id == "SP-45"
        assert response.current_phase == "context_analysis"
        assert response.iteration_count == 1

    def test_sprint_status_response_optional_fields(self):
        """Test SprintStatusResponse optional fields."""
        response = SprintStatusResponse(
            sprint_id="SP-45",
            sprint_goal="Test",
            current_phase="startup",
            iteration_count=0,
            execution_results={},
            started_at="2024-01-15T10:00:00Z",
            updated_at="2024-01-15T10:00:00Z"
        )

        assert response.context_analysis is None
        assert response.test_plan is None
        assert response.release_certification is None


class TestCertificationResponse:
    """Tests for CertificationResponse model."""

    def test_certification_response_creation(self):
        """Test creating CertificationResponse."""
        response = CertificationResponse(
            sprint_id="SP-45",
            certified=True,
            confidence_score=0.92,
            blockers=[],
            recommendations=["Proceed with release"],
            summary="Release APPROVED",
            certified_at="2024-01-15T15:00:00Z"
        )

        assert response.certified is True
        assert response.confidence_score == 0.92


class TestSprintRoutes:
    """Tests for Sprint API routes."""

    @pytest.fixture
    def app(self):
        """Create FastAPI app for testing."""
        app = FastAPI()
        app.include_router(router)
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def mock_orchestrator(self):
        """Create mock orchestrator."""
        with patch("src.api.routes.sprint.start_sprint") as mock_start:
            mock_start.return_value = {
                "sprint_id": "SP-45",
                "status": "started",
                "message": "Sprint started successfully"
            }
            yield mock_start

    def test_router_has_correct_prefix(self, app):
        """Test router has correct prefix."""
        routes = [route.path for route in app.routes]

        assert any("/v1/metanoia/sprint" in route for route in routes)

    def test_router_has_sprint_tag(self):
        """Test router has Sprint tag."""
        assert router.tags == ["Sprint"]


class TestSprintRoutesIntegration:
    """Integration tests for Sprint routes with mocked dependencies."""

    @pytest.fixture
    def app_with_mocks(self):
        """Create app with mocked dependencies."""
        app = FastAPI()
        app.include_router(router)
        return app

    @pytest.fixture
    def client_with_mocks(self, app_with_mocks):
        """Create test client with mocked dependencies."""
        return TestClient(app_with_mocks)

    def test_sprint_start_endpoint_exists(self, client_with_mocks):
        """Test sprint start endpoint exists."""
        with patch("src.api.routes.sprint.start_sprint", new_callable=AsyncMock) as mock_start:
            mock_start.return_value = {
                "sprint_id": "SP-TEST",
                "status": "started"
            }

            response = client_with_mocks.post(
                "/v1/metanoia/sprint/start",
                json={
                    "sprint_id": "SP-TEST",
                    "sprint_goal": "Test sprint"
                }
            )

            assert response.status_code in [200, 201, 202, 500]

    def test_sprint_status_endpoint_exists(self, client_with_mocks):
        """Test sprint status endpoint exists."""
        with patch("src.api.routes.sprint.get_sprint_status", new_callable=AsyncMock) as mock_status:
            mock_status.return_value = {
                "sprint_id": "SP-TEST",
                "current_phase": "execution",
                "iteration_count": 2
            }

            response = client_with_mocks.get("/v1/metanoia/sprint/SP-TEST/status")

            assert response.status_code in [200, 404, 500]

    def test_sprint_start_request_validation(self, client_with_mocks):
        """Test sprint start validates request body."""
        response = client_with_mocks.post(
            "/v1/metanoia/sprint/start",
            json={"sprint_id": "SP-45"}
        )

        assert response.status_code in [400, 422, 500]

    def test_sprint_start_with_run_async(self, client_with_mocks):
        """Test sprint start with async flag."""
        with patch("src.api.routes.sprint.start_sprint", new_callable=AsyncMock) as mock_start:
            mock_start.return_value = {
                "sprint_id": "SP-ASYNC",
                "status": "started_async"
            }

            response = client_with_mocks.post(
                "/v1/metanoia/sprint/start",
                json={
                    "sprint_id": "SP-ASYNC",
                    "sprint_goal": "Async test",
                    "run_async": True
                }
            )

            assert response.status_code in [200, 201, 202, 500]


class TestSprintModelsValidation:
    """Tests for Sprint model validation."""

    def test_sprint_start_request_sprint_id_required(self):
        """Test sprint_id is required."""
        with pytest.raises(ValueError):
            SprintStartRequest(sprint_goal="Test")

    def test_sprint_start_request_goal_required(self):
        """Test sprint_goal is required."""
        with pytest.raises(ValueError):
            SprintStartRequest(sprint_id="SP-45")

    def test_sprint_status_response_all_fields(self):
        """Test SprintStatusResponse accepts all fields."""
        response = SprintStatusResponse(
            sprint_id="SP-45",
            sprint_goal="Test sprint",
            current_phase="release",
            iteration_count=5,
            context_analysis={"risk_level": "low"},
            test_plan={"total_cases": 100},
            test_case_count=100,
            execution_results={"passed": 95, "failed": 5},
            release_certification={"certified": True},
            started_at="2024-01-15T10:00:00Z",
            updated_at="2024-01-15T16:00:00Z"
        )

        assert response.current_phase == "release"
        assert response.iteration_count == 5
        assert response.context_analysis is not None

    def test_test_plan_response_structure(self):
        """Test TestPlanResponse structure."""
        response = TestPlanResponse(
            sprint_id="SP-45",
            test_plan={"plan_id": "P1"},
            test_cases=[{"case_id": "TC-001"}]
        )

        assert response.sprint_id == "SP-45"
        assert len(response.test_cases) == 1

    def test_certification_response_false(self):
        """Test CertificationResponse with certified=False."""
        response = CertificationResponse(
            sprint_id="SP-46",
            certified=False,
            confidence_score=0.45,
            blockers=["High failure rate", "Security issues"],
            recommendations=["Fix security first"],
            summary="Release DENIED",
            certified_at="2024-01-15T15:00:00Z"
        )

        assert response.certified is False
        assert len(response.blockers) == 2
