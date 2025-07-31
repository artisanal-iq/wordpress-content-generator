# Sprint 2 Implementation Plan

This document outlines the steps required to deliver the user stories described in `docs/sprint_2.md`. It is focused on concrete development tasks for the next two weeks.

## 1. WordPress Site Scaffold (`S2-WP-1`)
- **Create new agent `site_scaffold_agent.py`**
  - Generates required EEAT pages (About, Contact, Privacy Policy, Terms of Service, Author Bio) using existing OpenAI helper functions.
  - Writes pages and default categories to Supabase and triggers WordPress publishing via REST API.
  - Inserts initial pillar posts and supporting articles as `content_pieces` rows and queues follow‑up agents via `agent_status`.
- **Dashboard button**
  - Add `SiteBootstrapButton` component in the Next.js dashboard to call an API route that launches the scaffold agent.
- **Idempotency & rollback**
  - Track created pages/categories in Supabase so re-running does not duplicate data.
  - Wrap site creation logic in a transaction; on error revert inserted rows and surface a friendly message.

## 2. Auto‑Run Orchestrator (`S2-ORC-1`)
- **Agent mapping table**
  - Introduce a table (or static map) defining the next agent for each status (`seo -> research -> writer -> flow-editor -> line-editor -> image -> publisher`).
- **Polling loop**
  - Extend `orchestrator.py` with a configurable polling interval (default 30 s) that checks `agent_status` and queues the next task when a row enters `completed` state.
  - Implement retry logic and move tasks to `needs_review` after `N` failures.
- **Realtime dashboard update**
  - Use Supabase realtime channels to push status changes to the dashboard so no manual refresh is needed.
- **Load test script**
  - Add a pytest integration test that spawns 50 dummy content pieces and ensures the orchestrator processes them without dead‑locks.

## 3. Authentication & RBAC (`S2-AUTH-1`)
- **Supabase setup**
  - Add `user_profiles` table with `role` column (`admin` / `editor`).
  - Configure Supabase Auth with email magic‑link sign‑in.
- **Next.js middleware**
  - Create a middleware check that redirects unauthenticated users to `/login` and exposes the user role on the client.
- **Role‑aware UI**
  - Hide destructive actions for editors. Provide an invitation form for admins to send magic‑link invites.
- **Cypress tests**
  - Add an end‑to‑end test verifying that an editor cannot access `/settings` while an admin can.

## 4. Testing & CI Improvements (`S2-CI-1`)
- **Linting**
  - Configure ESLint and Prettier for the dashboard; ensure `npm run lint` passes with zero errors.
  - Add `flake8`, `black` and `isort` checks for Python code (already used in `run_tests.sh`).
- **Coverage**
  - Expand unit tests to cover new agents and orchestrator logic aiming for ≥80 % coverage.
  - Publish coverage to Codecov via GitHub Actions and display a badge in `README.md`.
- **GitHub Actions workflow**
  - Create `.github/workflows/ci.yml` that installs dependencies, runs lint, executes tests, and uploads coverage reports.

## 5. Milestones
1. **Day 1‑2:** Apply DB migration for `user_profiles` and set up Supabase Auth.
2. **Day 3‑5:** Implement `site_scaffold_agent.py` and accompanying tests.
3. **Day 6‑7:** Add orchestrator polling loop and retry logic.
4. **Day 8‑9:** Build front‑end RBAC components and site bootstrap button.
5. **Day 10:** Finalise CI workflow and ensure coverage badge appears in the README.
6. **Day 11‑12:** Bug‑fix, load testing and sprint demo preparation.

This plan aligns with the acceptance criteria in `docs/sprint_2.md` and sets a clear path toward a production‑ready site generator.
