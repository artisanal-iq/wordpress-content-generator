# API Reference

A complete reference to the **WordPress Content Generator** public-facing APIs and internal contracts that keep all agents, the orchestrator and utilities interoperating.

---

## 1. Agent Interfaces

All agents are **stateless CLIs** invoked by the orchestrator (`subprocess.run`) or manually via `run_agent.py`.  
Each agent must *only* communicate through:

* STDIN / CLI arguments (for single-shot execution)
* Supabase database tables (for persistent state)

### 1.1 Enhanced SEO Agent `enhanced_seo_agent.py`

| Aspect | Details |
| ------ | ------- |
| Invocation | `python enhanced_seo_agent.py --plan-id <uuid> [--no-ai]` |
| Reads | `strategic_plans` |
| Writes | `content_pieces`, `keywords`, `agent_status` |
| Status Transition | *none* → `draft` |

#### Input JSON (`stdin` alternative)

```json
{
  "plan_id": "5bc9…",
  "use_mock_data": false
}
```

#### Output JSON  *(written to `agent_status.output`)*

```json
{
  "content_ideas": [
    {
      "title": "The Ultimate Guide …",
      "focus_keyword": "weight training",
      "description": "An in-depth tutorial …",
      "estimated_word_count": 1800,
      "suggested_sections": [
        "Introduction",
        "Benefits",
        "Routine Examples",
        "Safety Tips",
        "Conclusion"
      ]
    }
  ],
  "keywords": {
    "focus_keyword": "weight training",
    "supporting_keywords": ["strength workouts", "gym routine"],
    "search_volume": {
      "weight training": 19000,
      "strength workouts": 4400
    }
  }
}
```

---

### 1.2 Research Agent `research_agent.py`

| Aspect | Details |
| ------ | ------- |
| Invocation | `python research_agent.py --content-id <uuid> [--no-ai]` |
| Reads | `content_pieces`, `keywords`, `strategic_plans` |
| Writes | `research`, `content_pieces.status = researched`, `agent_status` |
| Status Transition | `draft` → `researched` |

##### Output `research` row shape

```json
{
  "id": "uuid",
  "content_id": "uuid",
  "excerpt": "42 % of adults lift weights weekly.",
  "url": "https://cdc.gov/…",
  "type": "statistic",
  "confidence": 0.87
}
```

---

### 1.3 Draft Writer Agent `draft_writer_agent.py`

| Aspect | Details |
| ------ | ------- |
| Invocation | `python draft_writer_agent.py --content-id <uuid> [--no-ai]` |
| Reads | `content_pieces` (status = researched), `keywords`, `research`, `strategic_plans` |
| Writes | `content_pieces.draft_text`, `content_pieces.status = written`, `agent_status` |
| Status Transition | `researched` → `written` |

##### Draft Markdown Example

```
# Weight-Training 101

## Introduction
 …

## Benefits of Resistance Exercise
 …

## Sample 3-Day Routine
 …

## References
1. CDC. (2023). Resistance Training Guidelines. <https://cdc.gov/…>
```

---

## 2. Database Interaction Patterns

### 2.1 CRUD helpers

```python
from supabase import create_client
sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# SELECT
plan = sb.table("strategic_plans").select("*").eq("id", plan_id).execute().data[0]

# INSERT
sb.table("keywords").insert(payload).execute()

# UPDATE
sb.table("content_pieces").update({"status": "written"}).eq("id", cid).execute()
```

### 2.2 RPC / PostgREST Functions

Supabase function `select_content_pieces_by_plan(plan_id_param uuid)` returns all pieces for a plan.  
Agents fall back to a plain `SELECT … WHERE strategic_plan_id = …` if the RPC is missing.

### 2.3 Agent Status Logging

```python
sb.table("agent_status").insert({
    "content_id": cid,
    "agent": "research-agent",
    "status": "completed",
    "input": input_payload,      # JSON serialised
    "output": output_payload,    # JSON serialised
}).execute()
```

---

## 3. Orchestrator CLI

`python orchestrator.py [options]`

| Flag | Description |
| ---- | ----------- |
| `--create-plan` | Generate a new `strategic_plans` row – accepts extra meta flags (see below) |
| `--plan-id <uuid>` | Run pipeline for an existing plan |
| `--no-ai` | Force all agents to use deterministic mock data |
| `--loop` | Keep polling Supabase forever (daemon mode) |
| `--max-content <n>` | Limit number of content pieces to process in one run |

**Plan metadata flags (used only with `--create-plan`):**

```
--domain "mysite.com"
--audience "fitness enthusiasts"
--tone "motivational"
--niche "weight training"
--goal "inspire and educate"
```

### 3.1 Examples

Generate strategy + run full pipeline with mock data:

```bash
python orchestrator.py \
  --create-plan \
  --domain "fitnesssite.com" \
  --audience "fitness lovers" \
  --tone "friendly" \
  --niche "strength training" \
  --goal "grow newsletter" \
  --no-ai
```

Resume processing an existing plan (real LLM):

```bash
python orchestrator.py --plan-id 5bc9f… --max-content 5
```

---

## 4. Common Utility Functions (`agents/shared/utils.py`)

| Function | Purpose | Example |
| -------- | ------- | ------- |
| `slugify(title)` | Convert title to URL-friendly slug | `slugify("Hello World!") ➜ "hello-world"` |
| `load_json(path)` / `save_json(path, obj)` | Lightweight file IO wrappers | `keywords = load_json("keywords.json")` |
| `retry(max_attempts)(func)` | Decorator implementing exponential back-off |  |

_All utilities are pure functions with no external side-effects._

---

## 5. Error Handling Patterns

1. **Agent-Level Try/Catch**

```python
try:
    draft = write_draft_with_ai(client, …)
except Exception as exc:
    log_error("draft_writer", cid, exc)   # stores into agent_status
    raise
```

2. **Orchestrator Retry Wrapper**

```python
for attempt in range(AGENT_MAX_RETRIES):
    rc = subprocess.run(cmd)
    if rc.returncode == 0:
        break
    time.sleep(2 ** attempt)         # exponential back-off
else:
    mark_agent_failed(plan_id, agent, "max retries")
```

3. **Database Consistency**

* Agents update `content_pieces.status` **only after** a successful operation.  
* Any exception triggers a rollback to the previous status; partial writes are cleaned up in a compensating transaction.

4. **Graceful Degradation**

* Missing RPC function → fallback to raw SQL query.
* LLM offline → `--no-ai` provides deterministic stub data, ensuring pipeline continuity in CI.

---

## 6. Quick Reference Cheat-Sheet

```
Table            Primary Key      Core Columns              Owner
---------------------------------------------------------------------------
strategic_plans  id (uuid)        domain, audience,…        Orchestrator
content_pieces   id (uuid)        title, status,…           SEO / Agents
keywords         id (uuid)        focus_keyword,…           SEO Agent
research         id (uuid)        excerpt, url,…            Research Agent
agent_status     id (uuid)        agent, status, error      All Agents
```

All timestamps are generated in-DB (`DEFAULT now()`). UUIDs are created client-side using `uuid.uuid4()`.

---

For additional implementation details see:

* `docs/architecture/*.md` for diagrams
* `tests/` directory for executable examples
