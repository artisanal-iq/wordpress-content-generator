Here’s a detailed **Product Requirements Document (PRD)** for your autonomous content generation system:

---

# 🧾 Product Requirements Document (PRD)

**Project Name:** Autonomous Content Generation System
**Owner:** Jay Jordan
**Date:** July 19, 2025
**Version:** 1.0

---

## 📌 1. Purpose

To build a fully autonomous, web-based content generation system that produces SEO-optimized, high-quality long-form content and publishes it directly to WordPress sites. The system will be orchestrated by a central controller that coordinates agent workflows using a strategic content plan. Output will include complete blog posts, images, metadata, and social microcontent.

---

## 🎯 2. Goals & Objectives

### Primary Goals:

* Automate the entire content creation pipeline: from keyword strategy to publishing.
* Maintain content quality through agentic review and editing flows.
* Generate SEO-optimized, evergreen content aligned to niche domains.
* Support scale: multiple domains, campaigns, and content types.

### Success Metrics:

* Time to publish from strategy → WordPress: < 10 minutes human involvement
* CTR lift of ≥20% from AI-generated hooks/headlines
* 95%+ content pass rate on flow + line edit evaluations
* Weekly publish cadence of 20+ posts across multiple sites

---

## 🧱 3. Architecture Overview

| Layer      | Stack/Tools                          |
| ---------- | ------------------------------------ |
| Frontend   | Vercel (Next.js), Tailwind CSS       |
| Backend    | Pocketbase Flow (orchestrator logic) |
| Data Store | Supabase (PostgreSQL, Storage, Auth) |
| CMS Output | WordPress REST API                   |
| Agents     | Custom Python/GPT agents via API     |

---

## 🔁 4. Workflow Overview

1. **Orchestrator Agent**

   * Reads strategic plan
   * Initializes tasks across the content pipeline
   * Tracks task status, retries failed agents
   * Ensures completion & triggers publishing

2. **SEO Agent**

   * Parses domain strategy
   * Outputs:

     * Focus keyword
     * Supporting keywords
     * Cluster reference
     * Internal link targets

3. **Research Agent**

   * Uses keywords to fetch high-quality source content
   * Extracts:

     * Key facts
     * Quotes
     * Statistics
     * Source links

4. **Hook Agent**

   * Builds a compelling main hook
   * Generates 7 micro-hooks for use in:

     * Section headings
     * Social media posts

5. **Writer Agent**

   * Drafts long-form article using:

     * SEO outline
     * Research data
     * Hook structure

6. **Flow Editor Agent**

   * Refines pacing, transitions, and structure
   * Ensures article maintains narrative flow and engagement

7. **Line Editor Agent**

   * Applies grammar, clarity, tone edits
   * Flags sensitive or incoherent sections

8. **Headline Agent**

   * Generates multiple titles
   * Evaluates clickability, SEO, engagement
   * Refactors subheadings for clarity + structure

9. **Image Agent**

   * Finds royalty-free images (Pexels/Unsplash APIs)
   * Resizes and stores
   * Applies alt text and captions

10. **Publisher Agent**

    * Bundles final content
    * Schedules or publishes via WP API
    * Stores status, links, and metadata

---

## 🗃️ 5. Data Models (Supabase)

### `strategic_plans`

| Field    | Type   |
| -------- | ------ |
| id       | UUID   |
| domain   | String |
| audience | String |
| tone     | String |
| niche    | String |
| goal     | String |

---

### `keywords`

| Field           | Type    |
| --------------- | ------- |
| id              | UUID    |
| focus\_keyword  | Text    |
| supporting\_kw  | Text\[] |
| cluster\_target | Text    |
| internal\_links | Text\[] |

---

### `content_pieces`

| Field         | Type      |
| ------------- | --------- |
| id            | UUID      |
| title         | Text      |
| slug          | Text      |
| status        | Enum      |
| draft\_text   | Text      |
| final\_text   | Text      |
| scheduled\_at | Timestamp |
| wp\_post\_id  | Integer   |

---

### `research`

| Field       | Type  |
| ----------- | ----- |
| id          | UUID  |
| content\_id | UUID  |
| excerpt     | Text  |
| url         | Text  |
| type        | Enum  |
| confidence  | Float |

---

### `images`

| Field       | Type |
| ----------- | ---- |
| id          | UUID |
| content\_id | UUID |
| url         | Text |
| alt\_text   | Text |
| source      | Text |

---

## 🔧 6. Agent Interfaces

Each agent will expose the following interface:

```json
{
  "agent": "string",
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

## 🧪 7. Evaluation Criteria

### Automated Checks

* Grammar + readability (e.g., Hemingway Score)
* SEO optimization (e.g., Surfer-style scoring)
* Hook clickability score (open/click prediction)
* Link validity + plagiarism check

### Human-in-the-loop (optional phase)

* Editorial review dashboard
* “Accept / Rewrite / Reject” workflow

---

## 🚀 8. Launch Roadmap

### Phase 1 (Weeks 1–4):

* Finalize Supabase schema
* Build orchestrator logic with Pocketbase Flow
* Build working chain: SEO → Research → Writer → Flow Editor

### Phase 2 (Weeks 5–8):

* Add Hook + Line Editor + Headline Agents
* Start Image Agent integration
* Draft → WordPress pipeline live
* Integrate WP authentication, scheduling

### Phase 3 (Weeks 9–12):

* Social content pipeline (micro hooks → content calendar)
* Add monitoring + feedback dashboard
* Begin testing multi-domain / multi-niche scheduling
* Automate posting calendar w/ queue management

---

## 🧩 9. Future Considerations

* Web scraping w/ citation memory
* Email list integration (auto-generate newsletters from blog output)
* A/B headline testing
* Agentic content refresh pipeline (auto-refresh old blog posts)
* Tiered monetization: sell content-as-a-service to other operators

---

Want me to generate user stories or dev tasks next?
