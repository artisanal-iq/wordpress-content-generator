# WordPress Content Generator

An autonomous, agent-based system that plans, writes, edits, illustrates and publishes long-form, SEO-optimised articles directly to WordPress.

> **Status:** Sprint 0 (scaffolding) – core structure, first agent stub, schema & orchestrator MVP in progress.

---

## 📚 Table of Contents
1. What it does  
2. Architecture overview  
3. Repository layout  
4. Quick start (local development **without Docker**)  
5. Environment variables  
6. Database schema & seed data  
7. Running agents manually  
8. Orchestrator usage  
9. Front-end scaffold  
10. Continuous integration  
11. Contributing  

---

## 1  What it does
The system automates the entire content pipeline:

* Generates keyword clusters, research citations, hooks, drafts, headlines, images …
* Stores intermediate data in Supabase (PostgreSQL + Storage).
* Uses Pocketflow to route LLM calls (OpenAI to start, others later).
* Publishes finished articles to WordPress via REST API.
* Designed for scale: each step is a **stateless micro-agent** supervised by a lightweight orchestrator.

---

## 2  Architecture overview

| Layer          | Tech / Tooling |
| -------------- | -------------- |
| LLM Router     | **Pocketflow** – multi-provider routing & eval |
| Agents         | Python scripts (OpenAI GPT-4/3.5) |
| Orchestrator   | `orchestrator.py` – polls Supabase task table & executes agents |
| Data Store     | **Supabase** (PostgreSQL, Storage) |
| Front-end      | **Next.js** (deployed on Vercel) – monitoring dashboard |
| CMS            | WordPress REST API |
| CI             | GitHub Actions – lint, tests, coverage |

Agents talk **only** through the database, never directly to each other.

---

## 3  Repository layout
```
.
├── agents/                  # All micro-agents
│   ├── shared/              # common schemas & utils
│   └── seo-agent/           # first working stub
├── docs/                    # PRD, roadmap, sprint docs
├── tests/                   # pytest suites
├── supabase_schema.sql      # full DDL export
├── run_agent.py             # CLI runner for any agent
├── orchestrator.py          # minimal task manager
├── seed_data.py             # populate DB with test data
├── .github/workflows/       # CI pipeline
└── README.md
```

---

## 4  Quick start – local development (no Docker)

### Prerequisites
* Python 3.10+  
* Node 18+ (for the Next.js dashboard – optional for backend only)

### 1. Clone & create virtual env
```bash
git clone https://github.com/your-org/wordpress-content-generator.git
cd wordpress-content-generator
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Copy environment template & fill credentials
```bash
cp .env.example .env
# edit .env with Supabase/OpenAI keys etc.
```

### 4. Bootstrap the database  
1. Create a new Supabase project  
2. Open SQL editor → paste `supabase_schema.sql` → run  
3. (Optional) seed with sample data  
   ```bash
   python seed_data.py  --reset
   ```

You’re ready to run agents.

---

## 5  Environment variables

Key vars (see `.env.example`):
```
SUPABASE_URL, SUPABASE_KEY
OPENAI_API_KEY
WP_API_URL, WP_USERNAME, WP_APP_PASSWORD
POCKETFLOW_API_URL, POCKETFLOW_API_KEY
```
Put secrets in `.env`; it’s ignored by Git.

---

## 6  Database schema & seed data
* `supabase_schema.sql` – full Postgres DDL (tables, indexes, triggers).  
* `seed_data.py` – inserts:
  * 3 strategic plans
  * 6 content pieces
  * starter keywords, research, hooks
  * initial agent_status rows (queued / done / processing examples)

Run with `--reset` to wipe existing rows.

---

## 7  Running agents manually

### CLI
```bash
python run_agent.py seo-agent agents/seo-agent/test_input.json
```
The runner:
* Dynamically imports `agents/<name>/index.py`
* Prints JSON output to stdout
* Optionally `--output-file result.json`

### Inside code
```python
from agents.seo_agent import run
result = run({"domain": "fitness-blog.com", "niche": "weight training"})
```

---

## 8  Orchestrator

Continuous mode (every 30 s):
```bash
python orchestrator.py --mode=continuous --interval 30
```

Single run for one content piece:
```bash
python orchestrator.py --mode=single --content-id <uuid>
```

Create new content from a strategic plan:
```bash
python orchestrator.py --strategic-plan-id <uuid>
```

The orchestrator:
* Polls `agent_status` table for `queued` tasks
* Checks dependencies (see dict in file)
* Executes agent, updates status / output / errors
* Queues subsequent tasks automatically
* Retries failed tasks up to `AGENT_MAX_RETRIES`

---

## 9  Front-end scaffold

Located in `frontend/` (to be added in Sprint 1):  
* Next.js + Tailwind  
* Supabase Auth (email magic-link if multi-user)  
* Live pipeline dashboard (content piece timeline, agent status, error logs)

---

## 10  Continuous integration

GitHub Actions workflow:
* Installs deps, runs **flake8** & **pytest + coverage**
* Publishes coverage to Codecov
* Secrets required for Supabase / OpenAI are injected via repo settings.

---

## 11  Contributing

1. Create feature branch: `feat/seo-agent-improvements`  
2. Follow conventions in **AGENTS.md** – namespaced outputs, shared schemas, idempotent logic.  
3. Add/adjust tests in `tests/`.  
4. Run `black . && isort . && flake8`.  
5. Open pull-request targeting `main`. CI must pass before merge.

---

Happy hacking & GLHF! 😊
