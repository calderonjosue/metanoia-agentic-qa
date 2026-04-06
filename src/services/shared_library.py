"""Shared test case library for multi-team collaboration."""

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class SharedTestCase(BaseModel):
    """Shared test case model."""
    id: str
    team_id: str
    name: str
    description: str
    module: str
    tags: List[str] = Field(default_factory=list)
    test_data: dict = Field(default_factory=dict)
    created_by: str
    created_at: datetime
    updated_at: datetime
    version: int = 1
    fork_count: int = 0


class TestCaseFork(BaseModel):
    """Test case fork model."""
    id: str
    original_id: str
    forked_by: str
    forked_team: str
    modifications: dict = Field(default_factory=dict)
    created_at: datetime


class SharedTestCaseCreate(BaseModel):
    """Request to create a shared test case."""
    name: str = Field(..., max_length=200, description="Test case name")
    description: str = Field(default="", description="Test case description")
    module: str = Field(..., max_length=100, description="Module name")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    test_data: dict = Field(default_factory=dict, description="Test data payload")


class SharedTestCaseUpdate(BaseModel):
    """Request to update a shared test case."""
    name: Optional[str] = None
    description: Optional[str] = None
    module: Optional[str] = None
    tags: Optional[List[str]] = None
    test_data: Optional[dict] = None


class ForkRequest(BaseModel):
    """Request to fork a test case."""
    modifications: dict = Field(default_factory=dict, description="Modifications to apply")


class SearchQuery(BaseModel):
    """Search query for library."""
    query: str = Field(..., description="Search query string")
    tags: Optional[List[str]] = Field(default=None, description="Filter by tags")
    module: Optional[str] = Field(default=None, description="Filter by module")
    limit: int = Field(default=50, description="Max results to return")


class SharedLibrary:
    """
    Manages shared test case library across teams.
    """

    def __init__(self, supabase_client=None):
        self.supabase = supabase_client
        self._storage: dict[str, SharedTestCase] = {}
        self._forks: dict[str, TestCaseFork] = {}

    async def create_test_case(
        self,
        team_id: str,
        test_case: SharedTestCaseCreate,
        user_id: str
    ) -> SharedTestCase:
        """
        Create a test case in shared library.

        Args:
            team_id: ID of the team creating the test case
            test_case: Test case data
            user_id: ID of the user creating the test case

        Returns:
            Created SharedTestCase instance
        """
        test_case_id = str(uuid.uuid4())
        now = datetime.now()

        new_test_case = SharedTestCase(
            id=test_case_id,
            team_id=team_id,
            name=test_case.name,
            description=test_case.description,
            module=test_case.module,
            tags=test_case.tags,
            test_data=test_case.test_data,
            created_by=user_id,
            created_at=now,
            updated_at=now,
            version=1,
            fork_count=0
        )

        self._storage[test_case_id] = new_test_case

        if self.supabase:
            await self._persist_test_case(new_test_case)

        return new_test_case

    async def fork_test_case(
        self,
        test_case_id: str,
        target_team: str,
        user_id: str,
        modifications: dict | None = None
    ) -> TestCaseFork:
        """
        Fork a test case to another team.

        Args:
            test_case_id: ID of the test case to fork
            target_team: ID of the target team
            user_id: ID of the user forking
            modifications: Optional modifications to apply

        Returns:
            Created TestCaseFork instance
        """
        original = self._storage.get(test_case_id)
        if not original:
            raise ValueError(f"Test case {test_case_id} not found")

        fork_id = str(uuid.uuid4())
        now = datetime.now()

        fork = TestCaseFork(
            id=fork_id,
            original_id=test_case_id,
            forked_by=user_id,
            forked_team=target_team,
            modifications=modifications or {},
            created_at=now
        )

        self._forks[fork_id] = fork

        original.fork_count += 1
        self._storage[test_case_id] = original

        new_test_case = SharedTestCase(
            id=f"forked_{fork_id}",
            team_id=target_team,
            name=original.name,
            description=original.description,
            module=original.module,
            tags=original.tags,
            test_data={**original.test_data, **(modifications or {})},
            created_by=user_id,
            created_at=now,
            updated_at=now,
            version=1,
            fork_count=0
        )
        self._storage[new_test_case.id] = new_test_case

        return fork

    async def search_library(
        self,
        team_id: str,
        query: str,
        tags: Optional[List[str]] = None,
        module: Optional[str] = None
    ) -> List[SharedTestCase]:
        """
        Search shared library.

        Args:
            team_id: ID of the team searching
            query: Search query string
            tags: Optional list of tags to filter by
            module: Optional module to filter by

        Returns:
            List of matching SharedTestCase instances
        """
        results = []
        query_lower = query.lower()

        for test_case in self._storage.values():
            if test_case.team_id != team_id:
                continue

            if query_lower not in test_case.name.lower() and query_lower not in test_case.description.lower():
                continue

            if tags and not any(tag in test_case.tags for tag in tags):
                continue

            if module and test_case.module != module:
                continue

            results.append(test_case)

        return results

    async def update_test_case(
        self,
        test_case_id: str,
        updates: dict,
        user_id: str
    ) -> SharedTestCase:
        """
        Update a shared test case (creates new version).

        Args:
            test_case_id: ID of the test case to update
            updates: Dictionary of fields to update
            user_id: ID of the user making the update

        Returns:
            Updated SharedTestCase instance
        """
        original = self._storage.get(test_case_id)
        if not original:
            raise ValueError(f"Test case {test_case_id} not found")

        now = datetime.now()

        updated = SharedTestCase(
            id=original.id,
            team_id=original.team_id,
            name=updates.get("name", original.name),
            description=updates.get("description", original.description),
            module=updates.get("module", original.module),
            tags=updates.get("tags", original.tags),
            test_data=updates.get("test_data", original.test_data),
            created_by=original.created_by,
            created_at=original.created_at,
            updated_at=now,
            version=original.version + 1,
            fork_count=original.fork_count
        )

        self._storage[test_case_id] = updated
        return updated

    async def get_test_case(self, test_case_id: str) -> Optional[SharedTestCase]:
        """Get a specific test case by ID."""
        return self._storage.get(test_case_id)

    async def delete_test_case(self, test_case_id: str) -> bool:
        """Delete a test case from the library."""
        if test_case_id in self._storage:
            del self._storage[test_case_id]
            return True
        return False

    async def get_team_library(self, team_id: str) -> List[SharedTestCase]:
        """Get all test cases for a team."""
        return [tc for tc in self._storage.values() if tc.team_id == team_id]

    async def _persist_test_case(self, test_case: SharedTestCase) -> None:
        """Persist test case to Supabase."""
        if not self.supabase:
            return

        data = test_case.model_dump()
        data["created_at"] = data["created_at"].isoformat()
        data["updated_at"] = data["updated_at"].isoformat()

        self.supabase.table("shared_test_cases").insert(data).execute()
