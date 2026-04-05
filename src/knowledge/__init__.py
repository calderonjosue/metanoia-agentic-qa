"""Metanoia-QA Knowledge Base with Supabase pgvector.

This module provides RAG (Retrieval-Augmented Generation) capabilities
for historical testing context and agent lessons learned.
"""

from src.knowledge.client import SupabaseClient
from src.knowledge.rag import (
    MetanoiaRAG,
    agent_lessons_learned,
    match_historical_testing,
)

__all__ = ["MetanoiaRAG", "match_historical_testing", "agent_lessons_learned", "SupabaseClient"]
