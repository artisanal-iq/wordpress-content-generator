-- WordPress Content Generator - Database Tables
-- Run this script in the Supabase SQL Editor

-- Content Pieces Table
CREATE TABLE IF NOT EXISTS public.content_pieces (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    strategic_plan_id UUID REFERENCES public.strategic_plans(id),
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
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on content_pieces for strategic_plan_id
CREATE INDEX IF NOT EXISTS idx_content_pieces_strategic_plan ON content_pieces(strategic_plan_id);
-- Create index on content_pieces for status
CREATE INDEX IF NOT EXISTS idx_content_pieces_status ON content_pieces(status);

-- Insert sample data into content_pieces
INSERT INTO public.content_pieces (strategic_plan_id, title, status)
SELECT 
    id as strategic_plan_id, 
    'Sample Content Piece for ' || domain as title,
    'draft' as status
FROM public.strategic_plans
LIMIT 1;

-- Keywords Table
CREATE TABLE IF NOT EXISTS public.keywords (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID REFERENCES public.content_pieces(id) ON DELETE CASCADE,
    focus_keyword TEXT NOT NULL,
    supporting_keywords TEXT[] DEFAULT '{}',
    cluster_target TEXT,
    internal_links TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on keywords for content_id
CREATE INDEX IF NOT EXISTS idx_keywords_content_id ON keywords(content_id);

-- Insert sample data into keywords
INSERT INTO public.keywords (content_id, focus_keyword, supporting_keywords)
SELECT 
    id as content_id,
    'sample keyword' as focus_keyword,
    ARRAY['supporting keyword 1', 'supporting keyword 2'] as supporting_keywords
FROM public.content_pieces
LIMIT 1;

-- Agent Status Table
CREATE TABLE IF NOT EXISTS public.agent_status (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent TEXT NOT NULL,
    content_id UUID REFERENCES public.content_pieces(id) ON DELETE CASCADE,
    input JSONB DEFAULT '{}',
    output JSONB DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'queued',
    errors TEXT[] DEFAULT '{}',
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes on agent_status
CREATE INDEX IF NOT EXISTS idx_agent_status_content_id ON agent_status(content_id);
CREATE INDEX IF NOT EXISTS idx_agent_status_agent ON agent_status(agent);
CREATE INDEX IF NOT EXISTS idx_agent_status_status ON agent_status(status);

-- Insert sample data into agent_status
INSERT INTO public.agent_status (agent, content_id, status)
SELECT 
    'seo-agent' as agent,
    id as content_id,
    'queued' as status
FROM public.content_pieces
LIMIT 1;

-- Add trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply the trigger to all tables with updated_at
CREATE TRIGGER update_content_pieces_timestamp
BEFORE UPDATE ON content_pieces
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_keywords_timestamp
BEFORE UPDATE ON keywords
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_agent_status_timestamp
BEFORE UPDATE ON agent_status
FOR EACH ROW EXECUTE FUNCTION update_timestamp();
