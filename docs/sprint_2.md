# 🏃‍♂️ Sprint 2 — “Site Launch & Reliability”

**Duration:** 2 weeks  
**Team:** Platform 🐍 / Frontend ⚛️ / Dev Ops 🔧  
**Sprint Theme:** Turn the prototype into a “press-go” production system that can scaffold an entire WordPress site, run itself, and be safely used by multiple users.

---

## 1. Sprint Goals
1. **WordPress Site Scaffold** – one-click setup that creates EEAT pages, categories, pillar posts and supporting content.
2. **Orchestrator Improvements** – remove manual clicks by automatically queueing & executing the next agent in the pipeline.
3. **Authentication & RBAC** – enable multi-user access with admin / editor roles.
4. **Quality Gate** – introduce test coverage, linting and CI gates to prevent regressions.

Definition of Done:  
• All acceptance criteria below are met.  
• Automated tests green on main branch.  
• Demo video shows new site scaffold generating a live WP site.

---

## 2. User Stories & Acceptance Criteria

### 2.1  WordPress Site Scaffold  
| ID | User Story |
|----|------------|
| **S2-WP-1** | *As a growth marketer I want to click “Bootstrap Site” on a connected WordPress domain so that the system prepares an SEO-ready site structure without me writing anything.* |

**Acceptance Criteria**

1. “Bootstrap Site” button appears in **Settings → WordPress Sites** for every connected site.  
2. When clicked:  
   - Creates the pages: **About**, **Contact**, **Privacy Policy**, **Terms of Service**, **Author Bio**, **Sitemap.xml** draft.  
   - Adds default categories supplied in the strategic plan (min. 3).  
   - Generates 1 pillar post (≥ 2 000 words) per category and 3 supporting articles each, internally linked.  
   - All content pieces are stored in Supabase and progress through the agent pipeline automatically.  
3. Operation is idempotent — re-running does **not** duplicate pages or categories.  
4. Success toast + audit log entry.  
5. Failure shows user-friendly error and rolls back partial data.

---

### 2.2  Auto-Run Orchestrator  
| ID | User Story |
|----|------------|
| **S2-ORC-1** | *As a content operator I want the orchestrator to automatically launch the next agent once the previous one succeeds, so that I don’t need to babysit the pipeline.* |

**Acceptance Criteria**

1. Orchestrator polls `agent_status` every 30 s (configurable).  
2. When an agent row status = `completed`, orchestrator inserts a new `queued` task for the correct next agent (mapping table).  
3. Detects terminal state `failed` and retries up to `N` times, then escalates (status `needs_review`).  
4. Dashboard reflects live state without page refresh (Supabase realtime channel).  
5. Load test: process 50 articles in parallel without dead-locks.

---

### 2.3  Authentication & Role-Based Access Control  
| ID | User Story |
|----|------------|
| **S2-AUTH-1** | *As an admin I want to invite editors with restricted permissions so that they can manage content but not change system settings.* |

**Roles & Permissions**

| Action | Admin | Editor |
|--------|-------|--------|
| View content / plans | ✓ | ✓ |
| Trigger / rerun agent | ✓ | ✓ |
| Delete content | ✓ | ⚪︎ |
| Manage WordPress & API keys | ✓ | ✗ |
| Invite users | ✓ | ✗ |

**Acceptance Criteria**

1. Supabase Auth enabled with email magic-link.  
2. Role stored in `public.user_profiles.role` column.  
3. Next.js middleware redirects unauthenticated users to `/login`.  
4. UI elements respect role matrix (buttons hidden or disabled).  
5. Cypress e2e test proves that an editor cannot access `/settings`.

---

### 2.4  Testing & CI Improvements  
| ID | User Story |
|----|------------|
| **S2-CI-1** | *As an engineer I need a reliable CI pipeline that blocks merges on failing tests or lint errors so that main branch is always deployable.* |

**Acceptance Criteria**

1. ESLint + Prettier run on `npm run lint` (dashboard) — 0 errors.  
2. `pytest` unit tests reach ≥ 80 % coverage for backend agents.  
3. GitHub Actions workflow: install deps, run lint, run tests, upload coverage.  
4. Status checks required before PR can be merged.  
5. Badge for coverage shown in README.

---

## 3. Deliverables
* Updated Supabase schema (`user_profiles`, orchestration triggers).  
* New Python agent `site_scaffold_agent.py`.  
* Next.js UI components: `SiteBootstrapButton`, RBAC wrappers.  
* CI workflow file `.github/workflows/ci.yml`.  
* Sprint demo & retrospective notes.

---

## 4. Risks & Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| WordPress rate-limits during bulk scaffold | Medium | Exponential back-off, chunked publishing |
| Auth complexity delays other tasks | Medium | Use Supabase magic-link templates, scaffold with `@supabase/auth-helpers-nextjs` |
| Test flakiness in CI | Low | Isolate external HTTP with nock/vcr fixtures |

---

## 5. Milestones & Timeline

| Day | Milestone |
|-----|-----------|
| 1–2 | DB migration + Auth scaffold |
| 3–5 | Site Scaffold agent, unit tests |
| 6–7 | Orchestrator auto-run logic |
| 8–9 | Front-end buttons & RBAC UI |
| 10  | CI pipeline & coverage |
| 11  | Bug-fix, polish |
| 12  | Demo, retro, Sprint 3 planning |
