"""Tests for Skill Hub CLI."""

import pytest
from unittest.mock import patch, Mock, AsyncMock
from click.testing import CliRunner

from metanoia.src.skill_hub.cli import skill, install, list as list_cmd, search


class TestInstallCommand:
    """Tests for install command."""

    def test_install_command(self):
        """Test install command."""
        runner = CliRunner()
        with patch("metanoia.src.skill_hub.cli.get_hub_registry") as mock_get_registry:
            mock_registry = Mock()
            mock_registry.install = AsyncMock(return_value=True)
            mock_get_registry.return_value = mock_registry
            
            result = runner.invoke(install, ["test-skill"])
            
            assert result.exit_code == 0


class TestListCommand:
    """Tests for list command."""

    def test_list_command_shows_installed_skills(self):
        """Test list shows installed skills."""
        runner = CliRunner()
        with patch("metanoia.src.skill_hub.cli.get_hub_registry") as mock_get_registry:
            mock_manifest = Mock()
            mock_manifest.name = "test-skill"
            mock_manifest.version = "1.0.0"
            mock_manifest.description = "A test skill"
            
            mock_registry = Mock()
            mock_registry.list_installed = Mock(return_value=[mock_manifest])
            mock_get_registry.return_value = mock_registry
            
            result = runner.invoke(list_cmd)
            
            assert result.exit_code == 0
            assert "test-skill" in result.output
            assert "1.0.0" in result.output


class TestSearchCommand:
    """Tests for search command."""

    def test_search_command_queries_registry(self):
        """Test search queries registry."""
        runner = CliRunner()
        with patch("metanoia.src.skill_hub.cli.get_hub_registry") as mock_get_registry:
            mock_manifest = Mock()
            mock_manifest.name = "pytest-skill"
            mock_manifest.version = "2.0.0"
            mock_manifest.description = "Pytest integration"
            mock_manifest.author = "Test Author"
            
            mock_registry = Mock()
            mock_registry.search = AsyncMock(return_value=[mock_manifest])
            mock_get_registry.return_value = mock_registry
            
            result = runner.invoke(search, ["pytest"])
            
            assert result.exit_code == 0
            assert "pytest-skill" in result.output