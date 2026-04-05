"""RAG (Retrieval-Augmented Generation) for Metanoia-QA Knowledge Base.

This module provides RAG capabilities for historical testing context,
embedding generation using Gemini, and CRUD operations for agent lessons learned.
"""

import os
from typing import Optional, Any
from datetime import datetime
from dataclasses import dataclass, field

from supabase import Client
from google.genai import Client as GeminiClient
from google.genai.types import EmbedContentConfig

from src.knowledge.client import get_supabase_client


@dataclass
class HistoricalTestingRecord:
    """Represents a historical testing record for RAG retrieval.

    Attributes:
        id: Unique identifier
        sprint_id: Associated sprint identifier
        test_type: Type of testing performed
        findings: Key findings from the testing
        risk_patterns: Identified risk patterns
        resolution: How issues were resolved
        metadata: Additional metadata
        created_at: When the record was created
    """
    id: Optional[str] = None
    sprint_id: str = ""
    test_type: str = ""
    findings: list[str] = field(default_factory=list)
    risk_patterns: list[str] = field(default_factory=list)
    resolution: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None


@dataclass
class AgentLesson:
    """Represents a lesson learned from agent execution.

    Attributes:
        id: Unique identifier
        agent_type: Type of agent that generated the lesson
        situation: Context/situation description
        action_taken: What action was taken
        outcome: Result of the action
        applicability: When this lesson applies
        confidence: Confidence score (0-1)
        created_at: When the lesson was recorded
    """
    id: Optional[str] = None
    agent_type: str = ""
    situation: str = ""
    action_taken: str = ""
    outcome: str = ""
    applicability: str = ""
    confidence: float = 0.5
    created_at: Optional[datetime] = None


class GeminiEmbedder:
    """Embedding generator using Google Gemini.

    This class provides text embedding capabilities using the Gemini API
    for vector similarity searches in the knowledge base.

    Attributes:
        client: Gemini client instance
        model: Model name for embeddings
    """

    def __init__(self, model: str = "text-embedding-004"):
        """Initialize Gemini embedder.

        Args:
            model: Gemini embedding model name
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")

        self.client = GeminiClient(api_key=api_key)
        self.model = model

    def embed(self, text: str) -> list[float]:
        """Generate embedding for text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector as list of floats
        """
        result = self.client.models.embed_content(
            model=self.model,
            content=text,
            config=EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
        )

        return list(result.embeddings.values())[0].values

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        results = []
        for text in texts:
            results.append(self.embed(text))
        return results


class MetanoiaRAG:
    """RAG system for Metanoia-QA historical context retrieval.

    This class provides retrieval-augmented generation capabilities
    for querying historical testing data and agent lessons.

    Attributes:
        client: Supabase client
        embedder: Gemini embedding generator
        table_name: Name of the RAG table
    """

    TABLE_NAME = "metanoia_rag"

    def __init__(
        self,
        client: Optional[Client] = None,
        embedder: Optional[GeminiEmbedder] = None,
    ):
        """Initialize MetanoiaRAG.

        Args:
            client: Supabase client (defaults to global client)
            embedder: Gemini embedder (creates default if None)
        """
        self.client = client or get_supabase_client()
        self.embedder = embedder or GeminiEmbedder()

    def _get_table(self):
        """Get the RAG table reference."""
        return self.client.table(self.TABLE_NAME)

    def _generate_embedding(self, text: str) -> list[float]:
        """Generate embedding for text content.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        return self.embedder.embed(text)

    def add_historical_record(
        self,
        sprint_id: str,
        test_type: str,
        findings: list[str],
        risk_patterns: Optional[list[str]] = None,
        resolution: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Add a historical testing record.

        Args:
            sprint_id: Sprint identifier
            test_type: Type of testing
            findings: Key findings
            risk_patterns: Identified risk patterns
            resolution: How issues were resolved
            metadata: Additional metadata

        Returns:
            Created record with ID
        """
        content = f"""
        Sprint: {sprint_id}
        Test Type: {test_type}
        Findings: {' '.join(findings)}
        Risk Patterns: {' '.join(risk_patterns or [])}
        Resolution: {resolution or 'N/A'}
        """.strip()

        embedding = self._generate_embedding(content)

        record = {
            "sprint_id": sprint_id,
            "test_type": test_type,
            "content": content,
            "findings": findings,
            "risk_patterns": risk_patterns or [],
            "resolution": resolution or "",
            "metadata": metadata or {},
            "embedding": embedding,
            "created_at": datetime.utcnow().isoformat(),
        }

        response = self._get_table().insert(record).execute()
        return response.data[0] if response.data else record

    def match_historical_testing(
        self,
        query: str,
        threshold: float = 0.7,
        count: int = 5,
        test_type: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Query historical testing records by similarity.

        Args:
            query: Search query text
            threshold: Minimum similarity score (0-1)
            count: Maximum number of results
            test_type: Optional filter by test type

        Returns:
            List of matching records with similarity scores
        """
        query_embedding = self._generate_embedding(query)

        match_query = (
            self._get_table()
            .select("*")
            .limit(count)
        )

        if test_type:
            match_query = match_query.eq("test_type", test_type)

        response = match_query.execute()

        results = []
        for record in response.data:
            stored_embedding = record.get("embedding", [])
            if not stored_embedding:
                continue

            similarity = self._cosine_similarity(query_embedding, stored_embedding)
            if similarity >= threshold:
                results.append({
                    "id": record["id"],
                    "sprint_id": record["sprint_id"],
                    "test_type": record["test_type"],
                    "findings": record.get("findings", []),
                    "risk_patterns": record.get("risk_patterns", []),
                    "resolution": record.get("resolution", ""),
                    "similarity": similarity,
                    "created_at": record.get("created_at"),
                })

        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between two vectors.

        Args:
            a: First vector
            b: Second vector

        Returns:
            Cosine similarity score (0-1)
        """
        if len(a) != len(b):
            return 0.0

        dot_product = sum(x * y for x, y in zip(a, b))
        magnitude_a = sum(x * x for x in a) ** 0.5
        magnitude_b = sum(x * x for x in b) ** 0.5

        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0

        return dot_product / (magnitude_a * magnitude_b)

    def get_similar_risks(self, risk_pattern: str, count: int = 5) -> list[dict[str, Any]]:
        """Find records with similar risk patterns.

        Args:
            risk_pattern: Risk pattern to search for
            count: Maximum results

        Returns:
            List of records with matching risks
        """
        return self.match_historical_testing(
            query=f"Risk pattern: {risk_pattern}",
            threshold=0.6,
            count=count,
        )

    def create_rag_table_sql(self) -> str:
        """Generate SQL for creating the RAG table.

        Returns:
            SQL CREATE TABLE statement
        """
        return f"""
        CREATE EXTENSION IF NOT EXISTS vector;

        CREATE TABLE IF NOT EXISTS {self.TABLE_NAME} (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            sprint_id VARCHAR(255) NOT NULL,
            test_type VARCHAR(100) NOT NULL,
            content TEXT NOT NULL,
            findings JSONB DEFAULT '[]',
            risk_patterns JSONB DEFAULT '[]',
            resolution TEXT,
            metadata JSONB DEFAULT '{{}}',
            embedding vector(768),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        CREATE INDEX IF NOT EXISTS idx_rag_sprint_id ON {self.TABLE_NAME}(sprint_id);
        CREATE INDEX IF NOT EXISTS idx_rag_test_type ON {self.TABLE_NAME}(test_type);
        CREATE INDEX IF NOT EXISTS idx_rag_embedding ON {self.TABLE_NAME} USING ivfflat (embedding vector_cosine_ops);
        """


class AgentLessonsLearned:
    """CRUD operations for agent lessons learned.

    This class manages the lessons_learned table where agents
    record insights and learnings from execution.
    """

    TABLE_NAME = "agent_lessons_learned"

    def __init__(self, client: Optional[Client] = None):
        """Initialize AgentLessonsLearned.

        Args:
            client: Supabase client (defaults to global client)
        """
        self.client = client or get_supabase_client()

    def _get_table(self):
        """Get the lessons table reference."""
        return self.client.table(self.TABLE_NAME)

    def create(
        self,
        agent_type: str,
        situation: str,
        action_taken: str,
        outcome: str,
        applicability: str,
        confidence: float = 0.5,
    ) -> dict[str, Any]:
        """Create a new agent lesson.

        Args:
            agent_type: Type of agent
            situation: Context/situation description
            action_taken: What action was taken
            outcome: Result of the action
            applicability: When this lesson applies
            confidence: Confidence score (0-1)

        Returns:
            Created lesson with ID
        """
        lesson = {
            "agent_type": agent_type,
            "situation": situation,
            "action_taken": action_taken,
            "outcome": outcome,
            "applicability": applicability,
            "confidence": confidence,
            "created_at": datetime.utcnow().isoformat(),
        }

        response = self._get_table().insert(lesson).execute()
        return response.data[0] if response.data else lesson

    def get_by_agent(
        self,
        agent_type: str,
        min_confidence: float = 0.3,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Get lessons for a specific agent.

        Args:
            agent_type: Type of agent
            min_confidence: Minimum confidence threshold
            limit: Maximum results

        Returns:
            List of lessons
        """
        response = (
            self._get_table()
            .select("*")
            .eq("agent_type", agent_type)
            .gte("confidence", min_confidence)
            .order("confidence", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data or []

    def get_applicable(
        self,
        situation: str,
        agent_type: Optional[str] = None,
        threshold: float = 0.5,
    ) -> list[dict[str, Any]]:
        """Find lessons applicable to a situation.

        Args:
            situation: Situation description to match
            agent_type: Optional filter by agent type
            threshold: Minimum similarity threshold

        Returns:
            List of applicable lessons
        """
        rag = MetanoiaRAG(client=self.client)
        query = f"Agent lesson: {situation}"

        if agent_type:
            query += f" (Agent: {agent_type})"

        results = rag.match_historical_testing(
            query=query,
            threshold=threshold,
            count=10,
        )

        return results

    def update_confidence(self, lesson_id: str, new_confidence: float) -> dict[str, Any]:
        """Update the confidence score of a lesson.

        Args:
            lesson_id: Lesson ID
            new_confidence: New confidence score (0-1)

        Returns:
            Updated lesson
        """
        response = (
            self._get_table()
            .update({"confidence": new_confidence})
            .eq("id", lesson_id)
            .execute()
        )
        return response.data[0] if response.data else {}

    def delete(self, lesson_id: str) -> bool:
        """Delete a lesson.

        Args:
            lesson_id: Lesson ID

        Returns:
            True if deleted successfully
        """
        self._get_table().delete().eq("id", lesson_id).execute()
        return True

    def create_table_sql(self) -> str:
        """Generate SQL for creating the lessons table.

        Returns:
            SQL CREATE TABLE statement
        """
        return f"""
        CREATE TABLE IF NOT EXISTS {self.TABLE_NAME} (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            agent_type VARCHAR(100) NOT NULL,
            situation TEXT NOT NULL,
            action_taken TEXT NOT NULL,
            outcome TEXT NOT NULL,
            applicability TEXT,
            confidence FLOAT DEFAULT 0.5,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        CREATE INDEX IF NOT EXISTS idx_lessons_agent_type ON {self.TABLE_NAME}(agent_type);
        CREATE INDEX IF NOT EXISTS idx_lessons_confidence ON {self.TABLE_NAME}(confidence DESC);
        """


match_historical_testing = MetanoiaRAG().match_historical_testing
agent_lessons_learned = AgentLessonsLearned()
