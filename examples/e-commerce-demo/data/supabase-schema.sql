-- Enable vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Historical memory table
CREATE TABLE IF NOT EXISTS qa_historical_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sprint_id TEXT NOT NULL,
    module_name TEXT,
    description TEXT,
    defect_density FLOAT,
    critical_bugs_found INT,
    embedding VECTOR(768),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Agent lessons learned
CREATE TABLE IF NOT EXISTS agent_lessons_learned (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_role TEXT,
    tool_used TEXT,
    issue_encountered TEXT,
    resolution_applied TEXT,
    embedding VECTOR(768)
);

-- HNSW indexes
CREATE INDEX ON qa_historical_memory USING HNSW(embedding vector_cosine_ops);
CREATE INDEX ON agent_lessons_learned USING HNSW(embedding vector_cosine_ops);

-- Insert sample data
INSERT INTO qa_historical_memory (sprint_id, module_name, description, defect_density, critical_bugs_found)
VALUES 
    ('DEMO-01', 'checkout', 'Payment flow testing', 0.05, 0),
    ('DEMO-01', 'products', 'Product search functionality', 0.08, 1),
    ('DEMO-02', 'cart', 'Shopping cart operations', 0.03, 0);
