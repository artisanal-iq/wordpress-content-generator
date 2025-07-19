-- Content Pieces Table
-- Core table for content articles/posts
CREATE TABLE content_pieces (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    strategic_plan_id UUID REFERENCES strategic_plans(id),
    title TEXT,
    slug TEXT,
    status TEXT NOT NULL DEFAULT 'draft',
    draft_text TEXT,
    final_text TEXT,
    wp_post_id INTEGER,
    featured_image_id UUID,
    scheduled_at TIMESTAMP WITH TIME ZONE,
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Add constraint for status values
    CONSTRAINT valid_status CHECK (status IN ('draft', 'editing', 'ready', 'scheduled', 'published', 'archived', 'error'))
);

-- Create index on content_pieces for strategic_plan_id
CREATE INDEX idx_content_pieces_strategic_plan ON content_pieces(strategic_plan_id);
-- Create index on content_pieces for status
CREATE INDEX idx_content_pieces_status ON content_pieces(status);

-- Keywords Table
-- Stores SEO keyword data for content pieces
CREATE TABLE keywords (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID REFERENCES content_pieces(id) ON DELETE CASCADE,
    focus_keyword TEXT NOT NULL,
    supporting_keywords TEXT[] DEFAULT '{}',
    cluster_target TEXT,
    internal_links TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on keywords for content_id
CREATE INDEX idx_keywords_content_id ON keywords(content_id);

-- Agent Status Table
-- Tracks agent task execution status
CREATE TABLE agent_status (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent TEXT NOT NULL,
    content_id UUID REFERENCES content_pieces(id) ON DELETE CASCADE,
    input JSONB DEFAULT '{}',
    output JSONB DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'queued',
    errors TEXT[] DEFAULT '{}',
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Add constraint for status values
    CONSTRAINT valid_agent_status CHECK (status IN ('queued', 'processing', 'done', 'error'))
);

-- Create index on agent_status for content_id
CREATE INDEX idx_agent_status_content_id ON agent_status(content_id);
-- Create index on agent_status for agent
CREATE INDEX idx_agent_status_agent ON agent_status(agent);
-- Create index on agent_status for status
CREATE INDEX idx_agent_status_status ON agent_status(status);
-- Create composite index on agent_status for agent and content_id
CREATE INDEX idx_agent_status_agent_content ON agent_status(agent, content_id);

-- Add trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply the trigger to tables with updated_at
CREATE TRIGGER update_strategic_plans_timestamp
BEFORE UPDATE ON strategic_plans
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_content_pieces_timestamp
BEFORE UPDATE ON content_pieces
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_keywords_timestamp
BEFORE UPDATE ON keywords
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_agent_status_timestamp
BEFORE UPDATE ON agent_status
FOR EACH ROW EXECUTE FUNCTION update_timestamp();
