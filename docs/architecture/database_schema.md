# Database Schema

This document provides a detailed overview of the WordPress Content Generator database schema, showing the structure of each table and the relationships between them.

## Database Schema Diagram

```mermaid
erDiagram
    STRATEGIC_PLANS {
        uuid id PK "Primary key"
        string domain "Website domain"
        string audience "Target audience"
        string tone "Content tone"
        string niche "Content niche"
        string goal "Content goal"
        timestamp created_at "Creation timestamp"
        timestamp updated_at "Last update timestamp"
    }
    
    CONTENT_PIECES {
        uuid id PK "Primary key"
        uuid strategic_plan_id FK "References strategic_plans.id"
        string title "Article title"
        string slug "URL-friendly title"
        string description "Brief description"
        string status "draft/researched/written/published"
        text draft_text "Full article content"
        int estimated_word_count "Target word count"
        timestamp created_at "Creation timestamp"
        timestamp updated_at "Last update timestamp"
    }
    
    KEYWORDS {
        uuid id PK "Primary key"
        uuid content_id FK "References content_pieces.id"
        string focus_keyword "Primary SEO keyword"
        json supporting_keywords "Array of secondary keywords"
        json search_volume "Keyword volume data"
        timestamp created_at "Creation timestamp"
    }
    
    RESEARCH {
        uuid id PK "Primary key"
        uuid content_id FK "References content_pieces.id"
        string excerpt "Research text snippet"
        string url "Source URL"
        string type "fact/quote/statistic"
        float confidence "Source reliability (0-1)"
        timestamp created_at "Creation timestamp"
    }
    
    AGENT_STATUS {
        uuid id PK "Primary key"
        uuid content_id FK "References content_pieces.id"
        string agent "Agent name (seo-agent/research-agent/etc)"
        string status "queued/processing/completed/failed"
        json input "Agent input data"
        json output "Agent output data"
        json error "Error details if failed"
        timestamp created_at "Creation timestamp"
        timestamp updated_at "Last update timestamp"
    }
    
    STRATEGIC_PLANS ||--o{ CONTENT_PIECES : "has many"
    CONTENT_PIECES ||--o{ KEYWORDS : "has one"
    CONTENT_PIECES ||--o{ RESEARCH : "has many"
    CONTENT_PIECES ||--o{ AGENT_STATUS : "has many"
```

## Table Descriptions

### strategic_plans

The strategic_plans table defines the high-level content strategy for a specific domain. Each strategic plan serves as the foundation for multiple content pieces.

- **id**: UUID primary key
- **domain**: Website domain for the content strategy
- **audience**: Target audience description
- **tone**: Content tone (e.g., informative, conversational, professional)
- **niche**: Content niche or industry focus
- **goal**: Content marketing goal (e.g., educate, generate leads, build authority)
- **created_at**: Timestamp when the plan was created
- **updated_at**: Timestamp when the plan was last updated

### content_pieces

The content_pieces table tracks individual articles through the content pipeline. Each piece is associated with a strategic plan and progresses through various status stages.

- **id**: UUID primary key
- **strategic_plan_id**: Foreign key referencing strategic_plans.id
- **title**: Article title
- **slug**: URL-friendly version of the title
- **description**: Brief article description or summary
- **status**: Current status in the pipeline (draft, researched, written, published)
- **draft_text**: Full article content (markdown format)
- **estimated_word_count**: Target word count for the article
- **created_at**: Timestamp when the content piece was created
- **updated_at**: Timestamp when the content piece was last updated

### keywords

The keywords table stores SEO keyword information for each content piece. Each content piece has one set of keywords.

- **id**: UUID primary key
- **content_id**: Foreign key referencing content_pieces.id
- **focus_keyword**: Primary SEO keyword for the article
- **supporting_keywords**: JSON array of secondary keywords
- **search_volume**: JSON object with search volume data for keywords
- **created_at**: Timestamp when the keywords were created

### research

The research table contains research data gathered for each content piece. Each content piece can have multiple research entries.

- **id**: UUID primary key
- **content_id**: Foreign key referencing content_pieces.id
- **excerpt**: Research text snippet (fact, quote, statistic)
- **url**: Source URL for the research
- **type**: Type of research (fact, quote, statistic)
- **confidence**: Source reliability score (0.0 to 1.0)
- **created_at**: Timestamp when the research was created

### agent_status

The agent_status table logs the execution status of each agent for each content piece. This provides a complete audit trail of the content pipeline.

- **id**: UUID primary key
- **content_id**: Foreign key referencing content_pieces.id
- **agent**: Name of the agent (seo-agent, research-agent, draft-writer-agent)
- **status**: Current status (queued, processing, completed, failed)
- **input**: JSON object containing the agent's input data
- **output**: JSON object containing the agent's output data
- **error**: JSON object with error details if the agent failed
- **created_at**: Timestamp when the agent status was created
- **updated_at**: Timestamp when the agent status was last updated

## Relationships

1. A **strategic plan** can have many **content pieces**
2. A **content piece** has one set of **keywords**
3. A **content piece** can have many **research** entries
4. A **content piece** can have many **agent status** entries (one per agent execution)
