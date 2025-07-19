-- Research Table
-- Stores research data, citations, and sources
CREATE TABLE IF NOT EXISTS public.research (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID REFERENCES public.content_pieces(id) ON DELETE CASCADE,
    excerpt TEXT NOT NULL,
    url TEXT NOT NULL,
    type TEXT NOT NULL,
    confidence FLOAT DEFAULT 1.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Add constraint for research types
    CONSTRAINT valid_research_type CHECK (type IN ('fact', 'quote', 'statistic', 'definition', 'example', 'study'))
);

-- Create index on research for content_id
CREATE INDEX IF NOT EXISTS idx_research_content_id ON research(content_id);
-- Create index on research for type
CREATE INDEX IF NOT EXISTS idx_research_type ON research(type);
