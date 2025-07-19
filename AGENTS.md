# 🧠 Agents.md

**Codex Agent Collaboration Guidelines**
**Project:** Autonomous Content Generation System
**Version:** 1.0
**Date:** July 19, 2025
**Owner:** Jay Jordan

---

## 📘 Purpose

This document provides standards, architectural principles, and development conventions for all Codex agents contributing to the autonomous content generation system. Each agent is responsible for developing specific components listed in the PRD. These components will be orchestrated via Pocketbase Flow and connected to Supabase and WordPress.

> 🧩 **Important:** You are not executing the agents. You are building them. Treat each agent as a microservice with clearly defined I/O contracts and modular logic.

---

## 🧱 Shared System Context

* **Backend Orchestration**: Pocketflow (task queues, triggers, coordination)
* **Database**: Supabase (PostgreSQL)
* **Frontend**: Vercel (Next.js dashboard, orchestrator UI)
* **Publishing**: WordPress REST API
* **LLM/Script Execution**: Python - Pocktflow LLM (OpenAI)

---

## 🔁 Workflow Contract

All agent tasks follow a universal schema for interoperability:

```json
{
  "agent": "string", // Name of the agent (e.g., seo-agent)
  "input": {
    "fields": {}
  },
  "output": {
    "fields": {}
  },
  "status": "queued | processing | done | error",
  "errors": []
}
```

---

## ⚙️ Agent Structure and Naming

Each agent should be a self-contained function or script with:

* A clear module name using `kebab-case`: `seo-agent`, `research-agent`, `hook-agent`
* Exported functions: `run(input)`, `validate(input)`, `transform(output)`
* Optional: a helper file for utils shared across agents

> 📁 Suggested structure:

```
/agents
  /seo-agent
    index.py
    validate.py
    utils.py
  /research-agent
  /writer-agent
  ...
```

---

## 🚦Agent Development Protocol

### 1. **Use Shared Types**

All agents must import shared types from a central `schemas.py` or `schemas.ts` file, depending on language. This includes:

* `ContentPiece`
* `KeywordCluster`
* `AgentTask`

### 2. **Idempotent + Stateless**

Agent logic must be:

* Stateless between runs
* Idempotent on same input
* Deterministic where possible (to aid retries & evaluation)

### 3. **Error Handling**

* Wrap all core logic in a try-catch or try-except block
* Always return a structured `error` list (even if empty)
* Use error tags for tracing (e.g., `HOOK_EMPTY`, `RESEARCH_FAIL`)

### 4. **Inter-agent Communication**

* Do not directly call another agent.
* Instead, write outputs to Supabase → let Orchestrator trigger next agent.
* Use `task_complete(content_id, agent_name)` to notify orchestrator.

### 5. **Testing**

Each agent must include:

* A test harness (`test_input.json`)
* Sample output snapshot
* Evaluation criteria in comments (e.g., `hook must be <200 chars`, `H1 must contain focus keyword`)

---

## 🤝 Collaboration Best Practices

### Use Namespaces:

* Always prefix your keys in `output` with the agent name to avoid collisions:

  * ✅ `seo.focus_keyword`
  * ✅ `hook.main`
  * ❌ `title` (ambiguous)

### Avoid Race Conditions:

* Don’t overwrite `content_piece.status`
* Only update your own agent-specific columns in Supabase
* Use `agent_status` table to track per-agent progress

### Leave Markers:

* Add comment headers in text blocks to mark your section:

  ```md
  <!-- START: hook-agent.main-hook -->
  {text here}
  <!-- END: hook-agent.main-hook -->
  ```

### Declare Dependencies Explicitly:

* If your agent depends on another agent’s output (e.g., `hook-agent` needs `research-agent` output), declare that in a `depends_on = ['research-agent']` field at the top of your module.

---

## 📦 Agent Output Expectations

| Agent             | Output Keys                                                         |
| ----------------- | ------------------------------------------------------------------- |
| `seo-agent`       | `focus_keyword`, `supporting_keywords`, `cluster`, `internal_links` |
| `research-agent`  | `sources[]`, `citations[]`, `data_points[]`                         |
| `hook-agent`      | `main_hook`, `micro_hooks[]`                                        |
| `writer-agent`    | `draft_html`, `outline[]`, `sections[]`                             |
| `flow-editor`     | `edited_html`, `notes[]`                                            |
| `line-editor`     | `grammar_score`, `readability_score`, `final_html`                  |
| `headline-agent`  | `title_options[]`, `selected_title`, `subheaders[]`                 |
| `image-agent`     | `image_url`, `alt_text`, `caption`                                  |
| `publisher-agent` | `wp_post_id`, `status`, `scheduled_at`                              |

---

## 🧪 Sample Agent Stub

```python
# seo-agent/index.py

def validate(input):
    assert 'domain' in input
    assert 'niche' in input

def run(input):
    try:
        focus_keyword = generate_focus_keyword(input['niche'])
        supporting_keywords = expand_keywords(focus_keyword)
        return {
            "output": {
                "seo": {
                    "focus_keyword": focus_keyword,
                    "supporting_keywords": supporting_keywords
                }
            },
            "status": "done",
            "errors": []
        }
    except Exception as e:
        return {
            "output": {},
            "status": "error",
            "errors": ["SEO_GENERATION_FAIL: " + str(e)]
        }
```

## 🧭 Final Notes

* Keep logs minimal but structured. Debug with intent.
* Push small, modular updates—don't block others by refactoring shared types without coordination.
* Write with the next agent in mind. Assume your output will be piped, not read.
