"""Pytest configuration for observability tests."""

import sys
from unittest.mock import Mock

import pytest


@pytest.fixture(autouse=True)
def mock_knowledge_client():
    """Mock knowledge.client before imports."""
    mock = Mock()
    mock.get_supabase_client = Mock(return_value=Mock())

    if 'src.knowledge.client' in sys.modules:
        old_module = sys.modules['src.knowledge.client']
        sys.modules['src.knowledge.client'] = mock
        yield
        sys.modules['src.knowledge.client'] = old_module
    else:
        sys.modules['src.knowledge.client'] = mock
        yield
        if 'src.knowledge.client' in sys.modules:
            del sys.modules['src.knowledge.client']
