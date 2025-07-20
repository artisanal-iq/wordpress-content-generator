-- WordPress Content Generator - Supabase Schema
-- This file defines the database schema for the autonomous content generation system.
-- It includes tables for strategic plans, content pieces, keywords, research, images, and agent tasks.

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

-- Research Table
-- Stores research data, citations, and sources
CREATE TABLE research (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID REFERENCES content_pieces(id) ON DELETE CASCADE,
    excerpt TEXT NOT NULL,
    url TEXT NOT NULL,
    type TEXT NOT NULL,
    confidence FLOAT DEFAULT 1.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Add constraint for research types
    CONSTRAINT valid_research_type CHECK (type IN ('fact', 'quote', 'statistic', 'definition', 'example', 'study'))
);

-- Create index on research for content_id
CREATE INDEX idx_research_content_id ON research(content_id);
-- Create index on research for type
CREATE INDEX idx_research_type ON research(type);

-- Hooks Table
-- Stores hooks and micro-hooks for content
CREATE TABLE hooks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID REFERENCES content_pieces(id) ON DELETE CASCADE,
    main_hook TEXT NOT NULL,
    micro_hooks TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on hooks for content_id
CREATE INDEX idx_hooks_content_id ON hooks(content_id);

-- Images Table
-- Stores image metadata for content
CREATE TABLE images (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID REFERENCES content_pieces(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    alt_text TEXT NOT NULL,
    caption TEXT,
    source TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on images for content_id
CREATE INDEX idx_images_content_id ON images(content_id);

-- Headlines Table
-- Stores headline options and selected titles
CREATE TABLE headlines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID REFERENCES content_pieces(id) ON DELETE CASCADE,
    title_options TEXT[] DEFAULT '{}',
    selected_title TEXT,
    subheaders TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on headlines for content_id
CREATE INDEX idx_headlines_content_id ON headlines(content_id);

-- Editing Feedback Table
-- Stores feedback from editing agents
CREATE TABLE editing_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID REFERENCES content_pieces(id) ON DELETE CASCADE,
    agent TEXT NOT NULL,
    grammar_score FLOAT,
    readability_score FLOAT,
    notes TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on editing_feedback for content_id
CREATE INDEX idx_editing_feedback_content_id ON editing_feedback(content_id);
-- Create index on editing_feedback for agent
CREATE INDEX idx_editing_feedback_agent ON editing_feedback(agent);

-- Publishing Metadata Table
-- Stores WordPress publishing metadata
CREATE TABLE publishing_metadata (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID REFERENCES content_pieces(id) ON DELETE CASCADE,
    wp_post_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    scheduled_at TIMESTAMP WITH TIME ZONE,
    published_at TIMESTAMP WITH TIME ZONE,
    permalink TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on publishing_metadata for content_id
CREATE INDEX idx_publishing_metadata_content_id ON publishing_metadata(content_id);
-- Create index on publishing_metadata for wp_post_id
CREATE INDEX idx_publishing_metadata_wp_post_id ON publishing_metadata(wp_post_id);

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

-- Categories Table
-- Stores content categories for strategic plans
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    strategic_plan_id UUID REFERENCES strategic_plans(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_plan_category UNIQUE (strategic_plan_id, name)
);

-- Create index on categories for strategic_plan_id
CREATE INDEX idx_categories_plan_id ON categories(strategic_plan_id);

-- User Profiles Table
-- Stores application users and roles
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL DEFAULT 'editor',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_user_role CHECK (role IN ('admin', 'editor'))
);

-- Content Sections Table
-- Stores structured sections of content pieces
CREATE TABLE content_sections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID REFERENCES content_pieces(id) ON DELETE CASCADE,
    heading TEXT NOT NULL,
    subheading TEXT,
    body TEXT NOT NULL,
    order_num INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on content_sections for content_id
CREATE INDEX idx_content_sections_content_id ON content_sections(content_id);
-- Create index on content_sections for order_num
CREATE INDEX idx_content_sections_order ON content_sections(order_num);

-- Add trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply the trigger to all tables with updated_at
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

CREATE TRIGGER update_publishing_metadata_timestamp
BEFORE UPDATE ON publishing_metadata
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_content_sections_timestamp
BEFORE UPDATE ON content_sections
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_categories_timestamp
BEFORE UPDATE ON categories
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_user_profiles_timestamp
BEFORE UPDATE ON user_profiles
FOR EACH ROW EXECUTE FUNCTION update_timestamp();
