"""Tests for RAG (Retrieval-Augmented Generation) knowledge module."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import os

from src.knowledge.rag import (
    MetanoiaRAG,
    AgentLessonsLearned,
    HistoricalTestingRecord,
    AgentLesson,
    GeminiEmbedder,
)


class TestHistoricalTestingRecord:
    """Tests for HistoricalTestingRecord dataclass."""

    def test_record_creation(self):
        """Test creating HistoricalTestingRecord."""
        record = HistoricalTestingRecord(
            id="rec-001",
            sprint_id="SP-40",
            test_type="functional",
            findings=["Login works", "Logout works"],
            risk_patterns=["auth timing"],
            resolution="Added delays",
            metadata={"env": "staging"}
        )
        
        assert record.sprint_id == "SP-40"
        assert len(record.findings) == 2
        assert record.resolution == "Added delays"


class TestAgentLesson:
    """Tests for AgentLesson dataclass."""

    def test_lesson_creation(self):
        """Test creating AgentLesson."""
        lesson = AgentLesson(
            id="lesson-001",
            agent_type="context-analyst",
            situation="High defect density detected",
            action_taken="Increased regression coverage",
            outcome="Defects caught early",
            applicability="Similar module patterns",
            confidence=0.8
        )
        
        assert lesson.agent_type == "context-analyst"
        assert lesson.confidence == 0.8


class TestGeminiEmbedder:
    """Tests for GeminiEmbedder class."""

    def test_embedder_requires_api_key(self):
        """Test embedder raises error without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="GEMINI_API_KEY"):
                GeminiEmbedder()

    def test_embedder_initialization(self):
        """Test embedder initializes with API key."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            embedder = GeminiEmbedder()
            
            assert embedder.model == "text-embedding-004"
            assert embedder.client is not None

    def test_embedder_custom_model(self):
        """Test embedder with custom model."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            embedder = GeminiEmbedder(model="custom-embedding")
            
            assert embedder.model == "custom-embedding"

    def test_embedder_embed_returns_list(self):
        """Test embed returns list of floats."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            mock_client = Mock()
            mock_result = Mock()
            mock_result.embeddings.values.return_value = [0.1, 0.2, 0.3]
            mock_client.models.embed_content.return_value = mock_result
            
            embedder = GeminiEmbedder()
            embedder.client = mock_client
            
            result = embedder.embed("test text")
            
            assert isinstance(result, list)
            assert len(result) == 3

    def test_embedder_embed_batch(self):
        """Test batch embedding."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            mock_client = Mock()
            mock_result = Mock()
            mock_result.embeddings.values.return_value = [0.1, 0.2, 0.3]
            mock_client.models.embed_content.return_value = mock_result
            
            embedder = GeminiEmbedder()
            embedder.client = mock_client
            
            results = embedder.embed_batch(["text1", "text2"])
            
            assert len(results) == 2
            assert all(isinstance(r, list) for r in results)


class TestMetanoiaRAG:
    """Tests for MetanoiaRAG class."""

    @pytest.fixture
    def mock_client(self):
        """Create mock Supabase client."""
        client = Mock()
        client.table = Mock(return_value=Mock())
        return client

    @pytest.fixture
    def mock_embedder(self):
        """Create mock embedder."""
        embedder = Mock()
        embedder.embed = Mock(return_value=[0.1] * 768)
        return embedder

    @pytest.fixture
    def rag(self, mock_client, mock_embedder):
        """Create MetanoiaRAG instance."""
        return MetanoiaRAG(client=mock_client, embedder=mock_embedder)

    def test_rag_initialization(self, rag, mock_client, mock_embedder):
        """Test RAG initializes correctly."""
        assert rag.client is mock_client
        assert rag.embedder is mock_embedder
        assert rag.TABLE_NAME == "metanoia_rag"

    def test_rag_default_clients(self):
        """Test RAG uses default clients when none provided."""
        with patch("src.knowledge.rag.get_supabase_client") as mock_get_client:
            mock_get_client.return_value = Mock()
            
            with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
                rag = MetanoiaRAG()
                
                assert rag.client is not None
                assert rag.embedder is not None

    def test_rag_get_table(self, rag, mock_client):
        """Test getting table reference."""
        table = rag._get_table()
        
        mock_client.table.assert_called_once_with("metanoia_rag")

    def test_rag_generate_embedding(self, rag, mock_embedder):
        """Test embedding generation."""
        embedding = rag._generate_embedding("test text")
        
        mock_embedder.embed.assert_called_once_with("test text")
        assert embedding == [0.1] * 768

    def test_rag_add_historical_record(self, rag, mock_client, mock_embedder):
        """Test adding historical record."""
        mock_table = Mock()
        mock_table.insert.return_value.execute = Mock(return_value=Mock(
            data=[{"id": "new-id", "sprint_id": "SP-50"}]
        ))
        mock_client.table.return_value = mock_table
        
        record = rag.add_historical_record(
            sprint_id="SP-50",
            test_type="functional",
            findings=["Test passed"],
            risk_patterns=["none"],
            resolution="N/A"
        )
        
        mock_table.insert.assert_called_once()
        assert record["sprint_id"] == "SP-50"

    def test_rag_cosine_similarity_identical(self, rag):
        """Test cosine similarity of identical vectors."""
        vec = [1.0, 0.0, 0.0]
        
        similarity = rag._cosine_similarity(vec, vec)
        
        assert similarity == 1.0

    def test_rag_cosine_similarity_orthogonal(self, rag):
        """Test cosine similarity of orthogonal vectors."""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [0.0, 1.0, 0.0]
        
        similarity = rag._cosine_similarity(vec1, vec2)
        
        assert similarity == 0.0

    def test_rag_cosine_similarity_different_length(self, rag):
        """Test cosine similarity with different length vectors."""
        vec1 = [1.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        
        similarity = rag._cosine_similarity(vec1, vec2)
        
        assert similarity == 0.0

    def test_rag_cosine_similarity_zero_magnitude(self, rag):
        """Test cosine similarity with zero magnitude vectors."""
        similarity = rag._cosine_similarity([0.0], [0.0])
        
        assert similarity == 0.0

    def test_rag_match_historical_testing(self, rag, mock_client, mock_embedder):
        """Test historical testing matching."""
        mock_table = Mock()
        mock_query = Mock()
        mock_query.select.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.execute = Mock(return_value=Mock(data=[
            {
                "id": "rec-001",
                "sprint_id": "SP-40",
                "test_type": "functional",
                "findings": ["Login works"],
                "risk_patterns": ["auth"],
                "resolution": "Fixed timing",
                "embedding": [0.1] * 768,
                "created_at": "2024-01-15"
            }
        ]))
        mock_table.select.return_value.limit.return_value = mock_query
        mock_client.table.return_value = mock_table
        
        results = rag.match_historical_testing(
            query="authentication login",
            threshold=0.7,
            count=5
        )
        
        assert len(results) > 0
        assert results[0]["sprint_id"] == "SP-40"
        assert "similarity" in results[0]

    def test_rag_match_historical_testing_with_filter(self, rag, mock_client, mock_embedder):
        """Test historical testing matching with test type filter."""
        mock_table = Mock()
        mock_query = Mock()
        mock_query.select.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.execute = Mock(return_value=Mock(data=[]))
        mock_table.select.return_value.limit.return_value = mock_query
        mock_table.select.return_value.eq.return_value.limit.return_value = mock_query
        mock_client.table.return_value = mock_table
        
        rag.match_historical_testing(
            query="test",
            threshold=0.5,
            count=3,
            test_type="security"
        )
        
        mock_query.eq.assert_called()

    def test_rag_get_similar_risks(self, rag, mock_client, mock_embedder):
        """Test getting similar risks."""
        mock_table = Mock()
        mock_query = Mock()
        mock_query.select.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.execute = Mock(return_value=Mock(data=[]))
        mock_table.select.return_value.limit.return_value = mock_query
        mock_client.table.return_value = mock_table
        
        rag.get_similar_risks("SQL injection", count=5)
        
        mock_embedder.embed.assert_called()

    def test_rag_create_rag_table_sql(self, rag):
        """Test SQL generation for RAG table."""
        sql = rag.create_rag_table_sql()
        
        assert "CREATE EXTENSION IF NOT EXISTS vector" in sql
        assert "metanoia_rag" in sql
        assert "embedding vector" in sql
        assert "idx_rag_sprint_id" in sql


class TestAgentLessonsLearned:
    """Tests for AgentLessonsLearned class."""

    @pytest.fixture
    def mock_client(self):
        """Create mock Supabase client."""
        return Mock()

    @pytest.fixture
    def lessons(self, mock_client):
        """Create AgentLessonsLearned instance."""
        return AgentLessonsLearned(client=mock_client)

    def test_lessons_initialization(self, lessons, mock_client):
        """Test lessons initializes correctly."""
        assert lessons.client is mock_client
        assert lessons.TABLE_NAME == "agent_lessons_learned"

    def test_lessons_get_table(self, lessons, mock_client):
        """Test getting table reference."""
        lessons._get_table()
        
        mock_client.table.assert_called_once_with("agent_lessons_learned")

    def test_lessons_create(self, lessons, mock_client):
        """Test creating a lesson."""
        mock_table = Mock()
        mock_table.insert.return_value.execute = Mock(return_value=Mock(
            data=[{"id": "lesson-new"}]
        ))
        mock_client.table.return_value = mock_table
        
        lesson = lessons.create(
            agent_type="context-analyst",
            situation="High risk sprint",
            action_taken="Added regression tests",
            outcome="Defects caught early",
            applicability="High risk sprints",
            confidence=0.85
        )
        
        mock_table.insert.assert_called_once()
        assert lesson["agent_type"] == "context-analyst"

    def test_lessons_get_by_agent(self, lessons, mock_client):
        """Test getting lessons by agent type."""
        mock_table = Mock()
        mock_query = Mock()
        mock_query.select.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.gte.return_value = mock_query
        mock_query.order.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.execute = Mock(return_value=Mock(data=[
            {"id": "l1", "agent_type": "context-analyst", "confidence": 0.8}
        ]))
        mock_table.select.return_value.eq.return_value.gte.return_value.order.return_value.limit.return_value = mock_query
        mock_client.table.return_value = mock_table
        
        results = lessons.get_by_agent("context-analyst", min_confidence=0.5, limit=10)
        
        assert len(results) == 1
        assert results[0]["agent_type"] == "context-analyst"

    def test_lessons_get_applicable(self, lessons, mock_client):
        """Test getting applicable lessons."""
        with patch.object(lessons, "get_by_agent", return_value=[]):
            results = lessons.get_applicable("authentication testing")
            
            assert isinstance(results, list)

    def test_lessons_update_confidence(self, lessons, mock_client):
        """Test updating lesson confidence."""
        mock_table = Mock()
        mock_table.update.return_value.eq.return_value.execute = Mock(return_value=Mock(
            data=[{"id": "lesson-1", "confidence": 0.9}]
        ))
        mock_client.table.return_value = mock_table
        
        result = lessons.update_confidence("lesson-1", 0.9)
        
        assert result["confidence"] == 0.9

    def test_lessons_delete(self, lessons, mock_client):
        """Test deleting a lesson."""
        mock_table = Mock()
        mock_table.delete.return_value.eq.return_value.execute = Mock()
        mock_client.table.return_value = mock_table
        
        success = lessons.delete("lesson-to-delete")
        
        assert success is True
        mock_table.delete.assert_called_once()

    def test_lessons_create_table_sql(self, lessons):
        """Test SQL generation for lessons table."""
        sql = lessons.create_table_sql()
        
        assert "agent_lessons_learned" in sql
        assert "agent_type" in sql
        assert "confidence" in sql
        assert "idx_lessons_agent_type" in sql
