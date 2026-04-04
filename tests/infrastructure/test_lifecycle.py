"""Tests for lab lifecycle manager."""

import pytest
from unittest.mock import Mock, AsyncMock
from src.infrastructure.lab_lifecycle_manager import LabLifecycleManager


class TestLabLifecycleManager:
    """Tests for LabLifecycleManager."""

    @pytest.fixture
    def mock_iac_provider(self):
        """Create a mock IaC provider."""
        provider = Mock()
        provider.provision = AsyncMock(return_value={"lab_id": "lab-123"})
        provider.destroy = AsyncMock(return_value={"status": "destroyed"})
        provider.get_status = Mock(return_value={"state": "running"})
        return provider

    @pytest.fixture
    def lifecycle_manager(self, mock_iac_provider):
        """Create a LabLifecycleManager with mocked provider."""
        return LabLifecycleManager(iac_provider=mock_iac_provider)

    @pytest.mark.asyncio
    async def test_provision_creates_lab(self, lifecycle_manager, mock_iac_provider):
        """Test provision_creates_lab creates a lab successfully."""
        result = await lifecycle_manager.provision(
            lab_type="sandbox",
            config={"size": "small"}
        )

        mock_iac_provider.provision.assert_called_once_with(
            lab_type="sandbox",
            config={"size": "small"}
        )
        assert result["lab_id"] == "lab-123"

    @pytest.mark.asyncio
    async def test_teardown_destroys_lab(self, lifecycle_manager, mock_iac_provider):
        """Test teardown_destroys_lab destroys a lab successfully."""
        result = await lifecycle_manager.teardown(lab_id="lab-123")

        mock_iac_provider.destroy.assert_called_once_with(lab_id="lab-123")
        assert result["status"] == "destroyed"

    def test_status_returns_state(self, lifecycle_manager, mock_iac_provider):
        """Test status_returns_state returns the current state."""
        result = lifecycle_manager.status(lab_id="lab-123")

        mock_iac_provider.get_status.assert_called_once_with(lab_id="lab-123")
        assert result["state"] == "running"
