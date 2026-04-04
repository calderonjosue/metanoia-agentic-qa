-- Teams table
CREATE TABLE IF NOT EXISTS teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Team members
CREATE TABLE IF NOT EXISTS team_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID REFERENCES teams(id) ON DELETE CASCADE,
    user_id VARCHAR(100) NOT NULL,
    role VARCHAR(20) DEFAULT 'member',
    permissions JSONB DEFAULT '[]',
    joined_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(team_id, user_id)
);

-- Shared test library
CREATE TABLE IF NOT EXISTS shared_test_cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID REFERENCES teams(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    module VARCHAR(100),
    tags JSONB DEFAULT '[]',
    test_data JSONB,
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    version INT DEFAULT 1
);

-- Test case forks
CREATE TABLE IF NOT EXISTS test_case_forks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_id UUID REFERENCES shared_test_cases(id),
    forked_by VARCHAR(100) NOT NULL,
    forked_team_id UUID REFERENCES teams(id),
    modifications JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Cross-team sprints
CREATE TABLE IF NOT EXISTS cross_team_sprints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    status VARCHAR(20) DEFAULT 'planning',
    created_at TIMESTAMP DEFAULT NOW(),
    closed_at TIMESTAMP
);

-- Sprint team assignments
CREATE TABLE IF NOT EXISTS sprint_team_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sprint_id UUID REFERENCES cross_team_sprints(id),
    team_id UUID REFERENCES teams(id),
    assigned_modules JSONB DEFAULT '[]',
    status VARCHAR(20) DEFAULT 'pending',
    UNIQUE(sprint_id, team_id)
);

-- Cross-team blockers
CREATE TABLE IF NOT EXISTS cross_team_blockers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sprint_id UUID REFERENCES cross_team_sprints(id),
    description TEXT NOT NULL,
    affected_teams JSONB DEFAULT '[]',
    affected_modules JSONB DEFAULT '[]',
    severity VARCHAR(20) DEFAULT 'medium',
    reported_at TIMESTAMP DEFAULT NOW(),
    resolved BOOLEAN DEFAULT FALSE,
    resolution_notes TEXT
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_team_members_team ON team_members(team_id);
CREATE INDEX IF NOT EXISTS idx_team_members_user ON team_members(user_id);
CREATE INDEX IF NOT EXISTS idx_shared_tests_team ON shared_test_cases(team_id);
CREATE INDEX IF NOT EXISTS idx_shared_tests_tags ON shared_test_cases USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_shared_tests_module ON shared_test_cases(module);
CREATE INDEX IF NOT EXISTS idx_test_case_forks_original ON test_case_forks(original_id);
CREATE INDEX IF NOT EXISTS idx_test_case_forks_team ON test_case_forks(forked_team_id);
CREATE INDEX IF NOT EXISTS idx_sprint_assignments_sprint ON sprint_team_assignments(sprint_id);
CREATE INDEX IF NOT EXISTS idx_sprint_assignments_team ON sprint_team_assignments(team_id);
CREATE INDEX IF NOT EXISTS idx_blockers_sprint ON cross_team_blockers(sprint_id);
CREATE INDEX IF NOT EXISTS idx_blockers_resolved ON cross_team_blockers(resolved);

-- Trigger to update updated_at on teams
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_teams_updated_at
    BEFORE UPDATE ON teams
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
