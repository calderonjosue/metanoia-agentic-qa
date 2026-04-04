-- Self-learning patterns table
CREATE TABLE IF NOT EXISTS agent_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_role VARCHAR(50) NOT NULL,
    pattern_type VARCHAR(50) NOT NULL,
    trigger_context TEXT NOT NULL,
    response TEXT NOT NULL,
    success_rate FLOAT DEFAULT 0.5,
    times_applied INT DEFAULT 0,
    times_succeeded INT DEFAULT 0,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_patterns_agent ON agent_patterns(agent_role);
CREATE INDEX IF NOT EXISTS idx_patterns_type ON agent_patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_patterns_success ON agent_patterns(success_rate DESC);

-- Function to update success rate
CREATE OR REPLACE FUNCTION update_pattern_success()
RETURNS TRIGGER AS $$
BEGIN
    NEW.success_rate = CASE 
        WHEN NEW.times_applied > 0 
        THEN NEW.times_succeeded::FLOAT / NEW.times_applied 
        ELSE 0.5 
    END;
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_pattern_success ON agent_patterns;
CREATE TRIGGER trigger_update_pattern_success
BEFORE UPDATE ON agent_patterns
FOR EACH ROW
EXECUTE FUNCTION update_pattern_success();

-- Increment times_applied function
CREATE OR REPLACE FUNCTION increment_times_applied(pid UUID)
RETURNS INT AS $$
DECLARE
    new_count INT;
BEGIN
    UPDATE agent_patterns 
    SET times_applied = times_applied + 1
    WHERE id = pid
    RETURNING times_applied INTO new_count;
    
    RETURN new_count;
END;
$$ LANGUAGE plpgsql;
