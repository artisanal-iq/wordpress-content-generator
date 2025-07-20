# WordPress Content Generator Dashboard

A modern Next.js dashboard (App Router + TypeScript + Tailwind CSS) for visualising and managing the autonomous content-generation pipeline.  
Use it to:

* Monitor pipeline progress (Draft → Researched → Written → Flow Edited → Line Edited → Image Generated → Published)
* Create new content pieces and strategic plans
* Inspect keywords, images and agent logs for each article
* Trigger the next agent in the chain or re-run a failed step
* Configure credentials for WordPress, OpenAI and Supabase – all in the browser

---

## 1 · Prerequisites

| Tool | Version (tested) |
|------|------------------|
| Node | ≥ 18 LTS |
| npm  | ≥ 9 |
| Supabase project | Tables matching the backend schema |
| WordPress site | Application password enabled |
| OpenAI account | API key |

> macOS/Linux users can use `nvm` to install Node 18 quickly.

---

## 2 · Getting Started

```bash
git clone https://github.com/your-org/wordpress-content-generator.git
cd wordpress-content-generator/dashboard
npm install
```

### 2.1 Environment variables

1. Copy the template and fill in your values:

```bash
cp .env.local.example .env.local
```

```
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=public-anon-key
```

2. (Optional) For CI / container deploys you may also add

```
NEXT_PUBLIC_WORDPRESS_URL=https://example.com
NEXT_PUBLIC_WORDPRESS_USER=admin
NEXT_PUBLIC_WORDPRESS_APP_PASSWORD=xxxx xxxx xxxx xxxx
NEXT_PUBLIC_OPENAI_API_KEY=sk-...
```

Those keys can be set later in **/settings** as well.

### 2.2 Run the dev server

```bash
npm run dev
# open http://localhost:3000
```

Hot-reload will pick up file changes instantly.

---

## 3 · Project Structure

```
dashboard/
├─ public/           # static assets (logo, icons, etc.)
├─ src/
│  ├─ app/           # Next.js 13 App Router pages
│  │  ├─ content/    # content list, detail & new routes
│  │  ├─ plans/      # strategic plan CRUD
│  │  ├─ settings/   # credentials & preferences
│  │  ├─ layout.tsx  # sidebar + theme provider
│  │  └─ page.tsx    # dashboard home
│  ├─ lib/
│  │  └─ supabase.ts # typed Supabase client factory
│  └─ styles/        # Tailwind base
├─ tailwind.config   # Tailwind & Radix colours
└─ tsconfig.json
```

---

## 4 · Using the Dashboard

### 4.1 Home / Dashboard

* KPI cards show the number of pieces in each pipeline stage.
* “Content Pipeline” bar visualises global progress.
* Recent 5 pieces with quick links.

### 4.2 Content

* Full table with search, status filter, sort & pagination.
* Row actions: view detail, open WordPress, delete.

### 4.3 Content Detail

* Rich preview of article HTML, keywords & featured image.
* Pipeline progress bar + chronological agent logs.
* “Run Next Agent” button to trigger the backend orchestrator.

### 4.4 Strategic Plans

* CRUD interface for website / audience strategies.
* Deleting a plan warns that related content will also be removed.

### 4.5 Settings

* Store API credentials in browser `localStorage`.
* Quick “Test Connection” buttons for WP / OpenAI / Supabase.
* Values can also come from build-time env vars.

---

## 5 · Build & Deployment

### Static build

```bash
npm run build
npm start          # production mode on port 3000
```

### Vercel

The dashboard works out-of-the-box on Vercel:

1. `vercel` → follow prompts  
2. Set the same env vars in the Vercel dashboard  
3. Each push to **main** auto-deploys

Tailwind’s JIT + App Router produce an optimised, edge-ready app.

---

## 6 · Troubleshooting

| Issue | Fix |
|-------|-----|
| 404 on images | Ensure the backend API `/api/images` proxy is reachable or store images in a public bucket. |
| “Failed to fetch” errors | Check Supabase URL/key and your CORS settings. |
| WordPress 401 | App password revoked or user lacks `author`/`editor` capabilities. |
| OpenAI “Incorrect API key provided” | Double-check you copied the entire `sk-...` token. |

---

## 7 · Contributing

PRs are welcome! Please run `npm run lint` and `npm run test` (coming soon) before opening a pull request.

---

Happy publishing 🚀
