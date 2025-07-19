-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Strategic Plans Table
-- Stores high-level content strategy information
CREATE TABLE strategic_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    domain TEXT NOT NULL,
    audience TEXT NOT NULL,
    tone TEXT NOT NULL,
    niche TEXT NOT NULL,
    goal TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add a sample record
INSERT INTO strategic_plans (domain, audience, tone, niche, goal)
VALUES ('example.com', 'general audience', 'informative', 'technology', 'educate readers');
