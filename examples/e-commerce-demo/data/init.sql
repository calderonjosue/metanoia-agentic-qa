CREATE TABLE IF NOT EXISTS sprints (
    id SERIAL PRIMARY KEY,
    sprint_id VARCHAR(50) UNIQUE NOT NULL,
    goal TEXT,
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS test_results (
    id SERIAL PRIMARY KEY,
    sprint_id VARCHAR(50),
    agent VARCHAR(50),
    passed INT,
    failed INT,
    duration FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_sprints_sprint_id ON sprints(sprint_id);
CREATE INDEX idx_test_results_sprint_id ON test_results(sprint_id);
