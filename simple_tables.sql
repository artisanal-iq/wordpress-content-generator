-- Create content_pieces table
CREATE TABLE IF NOT EXISTS public.content_pieces (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    strategic_plan_id UUID REFERENCES public.strategic_plans(id),
    title TEXT,
    slug TEXT,
    status TEXT NOT NULL DEFAULT 'draft',
    draft_text TEXT,
    final_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create keywords table
CREATE TABLE IF NOT EXISTS public.keywords (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID REFERENCES public.content_pieces(id) ON DELETE CASCADE,
    focus_keyword TEXT NOT NULL,
    supporting_keywords TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create agent_status table
CREATE TABLE IF NOT EXISTS public.agent_status (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent TEXT NOT NULL,
    content_id UUID REFERENCES public.content_pieces(id) ON DELETE CASCADE,
    input JSONB DEFAULT '{}',
    output JSONB DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'queued',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO public.content_pieces (strategic_plan_id, title, status)
SELECT
    id as strategic_plan_id,
    'Sample Article Title' as title,
    'draft' as status
FROM public.strategic_plans
LIMIT 1;
