CREATE TABLE IF NOT EXISTS solutions (
    id SERIAL PRIMARY KEY,
    expression TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    answer TEXT NOT NULL,
    steps JSONB NOT NULL,
    explanation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_solutions_category ON solutions(category);
CREATE INDEX idx_solutions_created_at ON solutions(created_at DESC);