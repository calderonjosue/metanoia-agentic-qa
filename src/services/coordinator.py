"""Cross-team sprint coordination service."""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class CrossTeamSprint(BaseModel):
    """Cross-team sprint model."""
    id: str
    name: str
    participating_teams: List[str]
    goals: List[str]
    status: str = Field(default="planning", description="planning, executing, closed")
    created_at: datetime
    closed_at: Optional[datetime] = None


class TeamContribution(BaseModel):
    """Team contribution to a cross-team sprint."""
    team_id: str
    team_name: str
    assigned_modules: List[str]
    completed_tests: int = 0
    total_tests: int = 0
    blockers: List[str] = Field(default_factory=list)
    progress_percentage: float = 0.0


class ModuleAssignment(BaseModel):
    """Module assignment for a team in a sprint."""
    team_id: str
    team_name: str
    modules: List[str]


class BlockerReport(BaseModel):
    """Cross-team blocker report."""
    blocker_id: str
    description: str
    affected_teams: List[str]
    affected_modules: List[str]
    severity: str = Field(default="medium", description="low, medium, high, critical")
    reported_at: datetime
    resolved: bool = False
    resolution_notes: Optional[str] = None


class QA_Manager_Dashboard:
    """
    Unified dashboard for QA managers overseeing multiple teams.
    """
    
    def __init__(self, supabase_client=None):
        self.supabase = supabase_client
        self._sprints: dict[str, CrossTeamSprint] = {}
        self._assignments: dict[str, List[ModuleAssignment]] = {}
        self._contributions: dict[str, List[TeamContribution]] = {}
        self._blockers: dict[str, List[BlockerReport]] = {}
    
    async def create_cross_team_sprint(
        self,
        name: str,
        teams: List[str],
        goals: List[str]
    ) -> CrossTeamSprint:
        """
        Create a sprint spanning multiple teams.
        
        Args:
            name: Sprint name
            teams: List of team IDs participating
            goals: List of sprint goals
            
        Returns:
            Created CrossTeamSprint instance
        """
        sprint_id = str(uuid.uuid4())
        now = datetime.now()
        
        sprint = CrossTeamSprint(
            id=sprint_id,
            name=name,
            participating_teams=teams,
            goals=goals,
            status="planning",
            created_at=now
        )
        
        self._sprints[sprint_id] = sprint
        self._assignments[sprint_id] = []
        self._contributions[sprint_id] = []
        self._blockers[sprint_id] = []
        
        if self.supabase:
            await self._persist_sprint(sprint)
        
        return sprint
    
    async def assign_modules(
        self,
        sprint_id: str,
        team_assignments: List[dict]
    ) -> List[ModuleAssignment]:
        """
        Assign modules to teams for cross-team sprint.
        
        Args:
            sprint_id: Sprint ID
            team_assignments: List of dicts with team_id and modules
            
        Returns:
            List of created ModuleAssignment instances
        """
        if sprint_id not in self._sprints:
            raise ValueError(f"Sprint {sprint_id} not found")
        
        assignments: List[ModuleAssignment] = []
        for assignment in team_assignments:
            module_assignment = ModuleAssignment(
                team_id=assignment["team_id"],
                team_name=assignment.get("team_name", "Unknown Team"),
                modules=assignment.get("modules", [])
            )
            assignments.append(module_assignment)
        
        self._assignments[sprint_id] = assignments
        
        if self.supabase:
            for idx in range(len(assignments)):
                await self._persist_assignment(sprint_id, assignments[idx])
        
        return assignments
    
    async def get_dashboard_summary(self, sprint_id: str) -> dict:
        """
        Get summary for QA manager dashboard.
        
        Args:
            sprint_id: Sprint ID
            
        Returns:
            Dictionary containing dashboard summary
        """
        if sprint_id not in self._sprints:
            raise ValueError(f"Sprint {sprint_id} not found")
        
        sprint = self._sprints[sprint_id]
        assignments = self._assignments.get(sprint_id, [])
        contributions = self._contributions.get(sprint_id, [])
        blockers = self._blockers.get(sprint_id, [])
        
        total_teams = len(sprint.participating_teams)
        total_modules = sum(len(a.modules) for a in assignments)
        total_completed = sum(c.completed_tests for c in contributions)
        total_tests = sum(c.total_tests for c in contributions)
        open_blockers = [b for b in blockers if not b.resolved]
        critical_blockers = [b for b in open_blockers if b.severity == "critical"]
        
        overall_progress = 0.0
        if total_tests > 0:
            overall_progress = (total_completed / total_tests) * 100
        
        return {
            "sprint": sprint.model_dump(),
            "summary": {
                "total_teams": total_teams,
                "total_modules": total_modules,
                "total_tests": total_tests,
                "completed_tests": total_completed,
                "overall_progress_percentage": round(overall_progress, 2),
                "open_blockers_count": len(open_blockers),
                "critical_blockers_count": len(critical_blockers)
            },
            "team_contributions": [c.model_dump() for c in contributions],
            "assignments": [a.model_dump() for a in assignments],
            "blockers": [b.model_dump() for b in blockers],
            "goals_progress": self._calculate_goals_progress(sprint.goals, contributions)
        }
    
    async def identify_blockers(
        self,
        sprint_id: str
    ) -> List[BlockerReport]:
        """
        Identify and list cross-team blockers.
        
        Args:
            sprint_id: Sprint ID
            
        Returns:
            List of blocker reports
        """
        if sprint_id not in self._sprints:
            raise ValueError(f"Sprint {sprint_id} not found")
        
        all_blockers = self._blockers.get(sprint_id, [])
        return [b for b in all_blockers if not b.resolved]
    
    async def report_blocker(
        self,
        sprint_id: str,
        description: str,
        affected_teams: List[str],
        affected_modules: List[str],
        severity: str = "medium"
    ) -> BlockerReport:
        """
        Report a cross-team blocker.
        
        Args:
            sprint_id: Sprint ID
            description: Blocker description
            affected_teams: List of affected team IDs
            affected_modules: List of affected module names
            severity: Blocker severity (low, medium, high, critical)
            
        Returns:
            Created BlockerReport instance
        """
        if sprint_id not in self._sprints:
            raise ValueError(f"Sprint {sprint_id} not found")
        
        blocker = BlockerReport(
            blocker_id=str(uuid.uuid4()),
            description=description,
            affected_teams=affected_teams,
            affected_modules=affected_modules,
            severity=severity,
            reported_at=datetime.now(),
            resolved=False
        )
        
        self._blockers[sprint_id].append(blocker)
        
        if self.supabase:
            await self._persist_blocker(sprint_id, blocker)
        
        return blocker
    
    async def resolve_blocker(
        self,
        sprint_id: str,
        blocker_id: str,
        resolution_notes: str
    ) -> BlockerReport:
        """
        Mark a blocker as resolved.
        
        Args:
            sprint_id: Sprint ID
            blocker_id: Blocker ID
            resolution_notes: Resolution notes
            
        Returns:
            Updated BlockerReport instance
        """
        blockers = self._blockers.get(sprint_id, [])
        
        for blocker in blockers:
            if blocker.blocker_id == blocker_id:
                blocker.resolved = True
                blocker.resolution_notes = resolution_notes
                return blocker
        
        raise ValueError(f"Blocker {blocker_id} not found in sprint {sprint_id}")
    
    async def update_team_progress(
        self,
        sprint_id: str,
        team_id: str,
        completed_tests: int,
        total_tests: int,
        blockers: List[str] | None = None
    ) -> TeamContribution:
        """
        Update a team's progress in the sprint.
        
        Args:
            sprint_id: Sprint ID
            team_id: Team ID
            completed_tests: Number of completed tests
            total_tests: Total number of tests
            blockers: Optional list of current blockers
            
        Returns:
            Updated TeamContribution instance
        """
        sprint = self._sprints.get(sprint_id)
        if not sprint:
            raise ValueError(f"Sprint {sprint_id} not found")
        
        team_name = "Unknown Team"
        assignments = self._assignments.get(sprint_id, [])
        for assignment in assignments:
            if assignment.team_id == team_id:
                team_name = assignment.team_name
                break
        
        progress = 0.0
        if total_tests > 0:
            progress = (completed_tests / total_tests) * 100
        
        contribution = TeamContribution(
            team_id=team_id,
            team_name=team_name,
            assigned_modules=[],
            completed_tests=completed_tests,
            total_tests=total_tests,
            blockers=blockers or [],
            progress_percentage=round(progress, 2)
        )
        
        existing = None
        for i, c in enumerate(self._contributions[sprint_id]):
            if c.team_id == team_id:
                existing = i
                break
        
        if existing is not None:
            self._contributions[sprint_id][existing] = contribution
        else:
            self._contributions[sprint_id].append(contribution)
        
        return contribution
    
    async def close_sprint(self, sprint_id: str) -> CrossTeamSprint:
        """
        Close a cross-team sprint.
        
        Args:
            sprint_id: Sprint ID
            
        Returns:
            Updated CrossTeamSprint instance
        """
        sprint = self._sprints.get(sprint_id)
        if not sprint:
            raise ValueError(f"Sprint {sprint_id} not found")
        
        sprint.status = "closed"
        sprint.closed_at = datetime.now()
        
        return sprint
    
    def _calculate_goals_progress(
        self,
        goals: List[str],
        contributions: List[TeamContribution]
    ) -> List[dict]:
        """Calculate progress for each goal."""
        total_completed = sum(c.completed_tests for c in contributions)
        total_tests = sum(c.total_tests for c in contributions)
        
        progress = 0.0
        if total_tests > 0:
            progress = (total_completed / total_tests) * 100
        
        return [
            {
                "goal": goal,
                "progress_percentage": round(progress, 2),
                "status": "completed" if progress >= 100 else "in_progress" if progress > 0 else "not_started"
            }
            for goal in goals
        ]
    
    async def _persist_sprint(self, sprint: CrossTeamSprint) -> None:
        """Persist sprint to Supabase."""
        if not self.supabase:
            return
        
        data = sprint.model_dump()
        data["created_at"] = data["created_at"].isoformat()
        if data.get("closed_at"):
            data["closed_at"] = data["closed_at"].isoformat()
        
        self.supabase.table("cross_team_sprints").insert(data).execute()
    
    async def _persist_assignment(
        self,
        sprint_id: str,
        assignment: ModuleAssignment
    ) -> None:
        """Persist assignment to Supabase."""
        if not self.supabase:
            return
        
        data = {
            "sprint_id": sprint_id,
            "team_id": assignment.team_id,
            "assigned_modules": assignment.modules
        }
        
        self.supabase.table("sprint_team_assignments").insert(data).execute()
    
    async def _persist_blocker(
        self,
        sprint_id: str,
        blocker: BlockerReport
    ) -> None:
        """Persist blocker to Supabase."""
        if not self.supabase:
            return
        
        data = blocker.model_dump()
        data["reported_at"] = data["reported_at"].isoformat()
        
        self.supabase.table("cross_team_blockers").insert(data).execute()
