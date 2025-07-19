-- Create a simple test table
CREATE TABLE test_table (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert a test record
INSERT INTO test_table (name) VALUES ('Test Record');
