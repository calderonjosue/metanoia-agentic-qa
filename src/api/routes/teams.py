"""Team management and collaboration API routes."""

from datetime import datetime
from typing import List

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/v1/metanoia/teams", tags=["Teams"])


class TeamCreate(BaseModel):
    """Request to create a new team."""
    name: str = Field(..., max_length=100, description="Team name")
    description: str = Field(default="", description="Team description")


class Team(BaseModel):
    """Team model."""
    id: str
    name: str
    description: str
    members: List[str]
    created_at: datetime
    updated_at: datetime


class MemberAdd(BaseModel):
    """Request to add a member to a team."""
    user_id: str = Field(..., description="User ID to add")
    role: str = Field(default="member", description="Role: admin, member, viewer")
    permissions: List[str] = Field(default_factory=list, description="List of permissions")


class TeamMember(BaseModel):
    """Team member model."""
    id: str
    user_id: str
    team_id: str
    role: str
    permissions: List[str]
    joined_at: datetime


class Workspace(BaseModel):
    """Team workspace model."""
    id: str
    team_id: str
    name: str
    sprints: List[str]
    shared_test_library: List[str]


class TestCaseShare(BaseModel):
    """Request to share a test case with team."""
    test_case_id: str = Field(..., description="Test case ID to share")
    target_team_id: str = Field(..., description="Target team ID")
    fork: bool = Field(default=False, description="Fork instead of share directly")


@router.post("/", response_model=Team, status_code=status.HTTP_201_CREATED)
async def create_team(team_data: TeamCreate):
    """Create a new team."""
    team_id = f"team_{datetime.now().timestamp()}"
    now = datetime.now()

    return Team(
        id=team_id,
        name=team_data.name,
        description=team_data.description,
        members=[],
        created_at=now,
        updated_at=now
    )


@router.get("/{team_id}", response_model=Team)
async def get_team(team_id: str):
    """Get team details."""
    now = datetime.now()
    return Team(
        id=team_id,
        name="Sample Team",
        description="Sample team description",
        members=["user_1", "user_2"],
        created_at=now,
        updated_at=now
    )


@router.post("/{team_id}/members", response_model=TeamMember, status_code=status.HTTP_201_CREATED)
async def add_member(team_id: str, member_data: MemberAdd):
    """Add a member to team."""
    member_id = f"member_{datetime.now().timestamp()}"

    return TeamMember(
        id=member_id,
        user_id=member_data.user_id,
        team_id=team_id,
        role=member_data.role,
        permissions=member_data.permissions,
        joined_at=datetime.now()
    )


@router.delete("/{team_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(team_id: str, user_id: str):
    """Remove a member from team."""
    return None


@router.get("/{team_id}/workspace", response_model=Workspace)
async def get_workspace(team_id: str):
    """Get team workspace."""
    return Workspace(
        id=f"workspace_{team_id}",
        team_id=team_id,
        name="Default Workspace",
        sprints=[],
        shared_test_library=[]
    )


@router.post("/{team_id}/share", status_code=status.HTTP_201_CREATED)
async def share_test_case(team_id: str, share_data: TestCaseShare):
    """Share a test case with team."""
    return {
        "status": "shared",
        "test_case_id": share_data.test_case_id,
        "target_team_id": share_data.target_team_id,
        "fork": share_data.fork,
        "shared_at": datetime.now().isoformat()
    }


@router.get("/{team_id}/members", response_model=List[TeamMember])
async def list_members(team_id: str):
    """List all team members."""
    return []


@router.patch("/{team_id}", response_model=Team)
async def update_team(team_id: str, updates: dict):
    """Update team details."""
    return Team(
        id=team_id,
        name=updates.get("name", "Updated Team"),
        description=updates.get("description", ""),
        members=updates.get("members", []),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
