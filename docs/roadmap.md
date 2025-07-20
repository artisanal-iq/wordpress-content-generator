# 🛣️ Autonomous Content System Roadmap

**Timeline:** 12 weeks (agile sprints / milestone-based)
**Tools:** Pocketbase Flow · Supabase · Vercel (Next.js) · WordPress API · Python/LLM agents

---

## ✅ Phase 1: Infrastructure & Orchestrator Bootstrapping (Week 1–2)

### 🎯 Goals:

* Set up Supabase (schema + auth)
* Deploy basic frontend on Vercel
* Stand up Pocketbase Flow and test agent orchestration

### Tasks:

* [ ] Define Supabase tables (`strategic_plans`, `keywords`, `content_pieces`, etc.)
* [ ] Deploy Vercel frontend with login + basic dashboard
* [ ] Deploy Pocketbase with simple Orchestrator UI
* [ ] Build `Agent Interface` pattern and task queue logic
* [ ] Stub manual task input + trigger next-agent workflows

---

## ⚙️ Phase 2: Core Content Pipeline (Week 3–4)

### 🎯 Goals:

* Full pipeline from keyword → longform content
* Connect SEO → Research → Writer → Editor (flow)

### Tasks:

* [x] Build **SEO Agent** to generate keyword clusters from strategy
* [x] Build **Research Agent** to retrieve and store citations
* [x] Build **Writer Agent** to generate drafts using keywords + research
* [x] Build **Flow Editor Agent** to clean structure and transitions
* [x] Enable orchestration from strategy plan → stored draft
* [x] Store all intermediate outputs in Supabase

---

## 🪄 Phase 3: Quality & Packaging (Week 5–6)

### 🎯 Goals:

* Add polish layers: micro-hooks, line editing, and headlines
* Prepare draft for WordPress publishing

### Tasks:

* [ ] Build **Hook Agent** (main + 7 microhooks stored in DB)
* [x] Build **Line Editor Agent** (clarity, grammar, voice)
* [ ] Build **Headline Agent** (evaluate clickability, SEO)
* [ ] Enable draft assembly (merge output from agents)
* [ ] Add export-ready formatting: WordPress-compatible markdown or HTML

---

## 🖼️ Phase 4: Images & WordPress Integration (Week 7–8)

### 🎯 Goals:

* Finalize visual assets and publish to WordPress
* Ensure content is 100% complete, metadata attached

### Tasks:

* [x] Build **Image Agent** to generate and resize images (via DALL-E API)
* [ ] Store image assets in Supabase Storage
* [ ] Use **Publisher Agent** to push content via WordPress REST API
* [ ] Schedule post, update post ID + slug in Supabase
* [ ] Add retry + error handling for failed posts

---

## 📆 Phase 5: Automation, Scheduling & Monitoring (Week 9–10)

### 🎯 Goals:

* Add scheduled posting, visibility into pipeline health
* Orchestrator fully autonomous with fallback checks

### Tasks:

* [ ] Build Post Scheduler (based on calendar logic)
* [ ] Add monitoring dashboard (task status, retry queue, success rate)
* [ ] Enable dynamic daily/weekly post planning from strategy inputs
* [ ] Add basic webhooks or Slack/email alerts for task errors or bottlenecks

---

## 📢 Phase 6: Social Content Pipeline & Growth Hooks (Week 11–12)

### 🎯 Goals:

* Repurpose hooks for social media and newsletters
* Prepare system for scale (multi-niche, content-as-a-service)

### Tasks:

* [ ] Repurpose stored micro-hooks into tweet threads, LinkedIn posts, captions
* [ ] Export social post drafts to Notion, Google Sheets, or Buffer queue
* [ ] Add optional newsletter generator (weekly blog recap)
* [ ] Add multi-site support (map keywords + agents to domains)

---

## 🚀 Stretch Goals (Post-MVP)

* Auto-refresh old posts (update outdated facts)
* A/B test headlines or image thumbnails
* WordPress E-E-A-T page auto-builder (About, Contact, Author)
* Metrics ingestion (traffic, CTR, conversion) to feedback loop into strategy
