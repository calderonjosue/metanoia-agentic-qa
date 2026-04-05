"""PostgreSQL Checkpointing for LangGraph.

This module provides persistent checkpointing capabilities using PostgreSQL
via Supabase, enabling state recovery across process restarts and distributed
execution scenarios.
"""

import json
import uuid
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Iterator, Optional

from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    Checkpoint,
    CheckpointMetadata,
)
from langgraph.checkpoint.serde.base import SerializerProtocol
from supabase import Client

from src.knowledge.client import get_supabase_client


class PostgresCheckpointSaver(BaseCheckpointSaver):
    """PostgreSQL-based checkpoint saver for LangGraph.

    This checkpointer stores checkpoints in Supabase with the following schema:

    Table: metanoia_checkpoints
    - id: UUID (primary key)
    - thread_id: VARCHAR (conversation/sprint identifier)
    - checkpoint_id: VARCHAR (timestamp-based unique ID)
    - checkpoint: JSONB (serialized state)
    - metadata: JSONB (checkpoint metadata)
    - created_at: TIMESTAMP

    Attributes:
        client: Supabase client instance
        serde: Serializer for checkpoint data
        thread_id: Optional default thread ID for all checkpoints
    """

    table_name: str = "metanoia_checkpoints"

    def __init__(
        self,
        client: Optional[Client] = None,
        serde: Optional[SerializerProtocol] = None,
        thread_id: Optional[str] = None,
    ):
        """Initialize PostgreSQL checkpoint saver.

        Args:
            client: Supabase client instance. If None, creates default client.
            serde: Custom serializer for checkpoint data.
            thread_id: Default thread ID for all checkpoints if not specified.
        """
        super().__init__(serde=serde)
        self.client = client or get_supabase_client()
        self.thread_id = thread_id

    def _get_table(self):
        """Get the checkpoints table reference."""
        return self.client.table(self.table_name)

    def _serialize_checkpoint(self, checkpoint: Checkpoint) -> dict[str, Any]:
        """Serialize checkpoint to storable format.

        Args:
            checkpoint: The checkpoint to serialize

        Returns:
            Dictionary suitable for PostgreSQL storage
        """
        return {
            "id": str(uuid.uuid4()),
            "checkpoint": json.loads(self.serde.dumps(checkpoint)),
            "checkpoint_id": checkpoint.get("id", str(uuid.uuid4())),
            "version": checkpoint.get("version", 1),
        }

    def _deserialize_checkpoint(self, data: dict[str, Any]) -> Checkpoint:
        """Deserialize checkpoint from storage format.

        Args:
            data: Raw data from PostgreSQL

        Returns:
            Deserialized Checkpoint object
        """
        checkpoint_data = data.get("checkpoint", {})
        if isinstance(checkpoint_data, str):
            checkpoint_data = json.loads(checkpoint_data)
        return self.serde.loads(json.dumps(checkpoint_data))

    def _serialize_metadata(self, metadata: CheckpointMetadata) -> dict[str, Any]:
        """Serialize checkpoint metadata.

        Args:
            metadata: CheckpointMetadata to serialize

        Returns:
            Serializable dictionary
        """
        if metadata is None:
            return {}
        return {
            "source": metadata.source,
            "step": metadata.step,
            "writes": metadata.writes,
            "thread_id": metadata.thread_id,
        }

    def put(
        self,
        config: dict[str, Any],
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
    ) -> dict[str, Any]:
        """Store a checkpoint.

        Args:
            config: Configuration with thread_id and checkpoint_id
            checkpoint: The checkpoint to store
            metadata: Checkpoint metadata

        Returns:
            Updated config with checkpoint_id
        """
        thread_id = config.get("configurable", {}).get("thread_id", self.thread_id or str(uuid.uuid4()))
        checkpoint_id = config.get("configurable", {}).get("checkpoint_id", str(uuid.uuid4()))

        record = {
            "thread_id": thread_id,
            "checkpoint_id": checkpoint_id,
            "checkpoint": self._serialize_checkpoint(checkpoint)["checkpoint"],
            "metadata": self._serialize_metadata(metadata),
            "created_at": datetime.utcnow().isoformat(),
        }

        self._get_table().insert(record).execute()

        return {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_id": checkpoint_id,
            }
        }

    def get(self, config: dict[str, Any]) -> Optional[tuple[Checkpoint, CheckpointMetadata]]:
        """Retrieve a checkpoint by config.

        Args:
            config: Configuration with thread_id and checkpoint_id

        Returns:
            Tuple of (checkpoint, metadata) or None if not found
        """
        thread_id = config.get("configurable", {}).get("thread_id", self.thread_id)
        checkpoint_id = config.get("configurable", {}).get("checkpoint_id")

        if not thread_id:
            return None

        query = self._get_table().select("*").eq("thread_id", thread_id)

        if checkpoint_id:
            query = query.eq("checkpoint_id", checkpoint_id)
        else:
            query = query.order("created_at", desc=True).limit(1)

        response = query.execute()

        if not response.data:
            return None

        data = response.data[0]
        checkpoint = self._deserialize_checkpoint(data)
        metadata = data.get("metadata", {})

        return checkpoint, metadata

    def list(
        self,
        config: dict[str, Any],
        filter: Optional[dict[str, Any]] = None,
        limit: Optional[int] = None,
        before: Optional[dict[str, Any]] = None,
        after: Optional[dict[str, Any]] = None,
    ) -> Iterator[dict[str, Any]]:
        """List checkpoints matching the given criteria.

        Args:
            config: Configuration with thread_id
            filter: Optional metadata filters
            limit: Maximum number of checkpoints to return
            before: Return checkpoints before this checkpoint_id
            after: Return checkpoints after this checkpoint_id

        Yields:
            Config dictionaries for matching checkpoints
        """
        thread_id = config.get("configurable", {}).get("thread_id", self.thread_id)

        if not thread_id:
            return

        query = self._get_table().select("checkpoint_id", "metadata", "created_at").eq("thread_id", thread_id)

        if limit:
            query = query.limit(limit)

        if before:
            before_id = before.get("configurable", {}).get("checkpoint_id")
            if before_id:
                query = query.lt("checkpoint_id", before_id)

        if after:
            after_id = after.get("configurable", {}).get("checkpoint_id")
            if after_id:
                query = query.gt("checkpoint_id", after_id)

        query = query.order("checkpoint_id", desc=True)

        response = query.execute()

        for item in response.data:
            yield {
                "configurable": {
                    "thread_id": thread_id,
                    "checkpoint_id": item["checkpoint_id"],
                }
            }

    def delete(self, config: dict[str, Any]) -> None:
        """Delete a checkpoint.

        Args:
            config: Configuration with thread_id and checkpoint_id
        """
        thread_id = config.get("configurable", {}).get("thread_id", self.thread_id)
        checkpoint_id = config.get("configurable", {}).get("checkpoint_id")

        if not thread_id or not checkpoint_id:
            return

        self._get_table().delete().eq("thread_id", thread_id).eq("checkpoint_id", checkpoint_id).execute()

    @classmethod
    def create_table_sql(cls) -> str:
        """Generate SQL for creating the checkpoints table.

        Returns:
            SQL CREATE TABLE statement
        """
        return """
        CREATE TABLE IF NOT EXISTS metanoia_checkpoints (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            thread_id VARCHAR(255) NOT NULL,
            checkpoint_id VARCHAR(255) NOT NULL,
            checkpoint JSONB NOT NULL,
            metadata JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(thread_id, checkpoint_id)
        );

        CREATE INDEX IF NOT EXISTS idx_checkpoints_thread_id ON metanoia_checkpoints(thread_id);
        CREATE INDEX IF NOT EXISTS idx_checkpoints_checkpoint_id ON metanoia_checkpoints(checkpoint_id);
        CREATE INDEX IF NOT EXISTS idx_checkpoints_created_at ON metanoia_checkpoints(created_at DESC);
        """

    @contextmanager
    def session(
        self,
        config: dict[str, Any],
        metadata: Optional[CheckpointMetadata] = None,
    ) -> Iterator[dict[str, Any]]:
        """Context manager for atomic checkpoint operations.

        Args:
            config: Configuration with thread_id
            metadata: Optional metadata for the session

        Yields:
            Updated config after the session
        """
        thread_id = config.get("configurable", {}).get("thread_id", self.thread_id)
        checkpoint_id = str(uuid.uuid4())

        yield {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_id": checkpoint_id,
            }
        }


def get_checkpointer(thread_id: Optional[str] = None) -> PostgresCheckpointSaver:
    """Factory function to create a configured PostgresCheckpointSaver.

    Args:
        thread_id: Optional default thread ID

    Returns:
        Configured PostgresCheckpointSaver instance
    """
    return PostgresCheckpointSaver(thread_id=thread_id)
