# job-matching

Job aggregator that scrapes LinkedIn, Nerdin, GeekHunter, and Indeed and ranks results by compatibility with the user profile.

## Tech Stack

### Frontend
- React + Vite + TypeScript + Tailwind CSS + ECharts

### Backend
- Django REST Framework (Python 3.12)
- APScheduler for periodic scraping
- Playwright (GeekHunter, Indeed — Cloudflare bypass via fresh context + `/rpc/jobdescs` RPC endpoint)
- requests + BeautifulSoup4 (Nerdin, LinkedIn)
- Claude API (`claude-haiku-4-5-20251001`) for job scoring and profile autofill

### Database
- PostgreSQL

### Infrastructure
- Docker (frontend, backend, database)

## Architecture

### Scraper Flow
1. `POST /api/scraper/run/` — starts a background thread (idempotent; no-op if already running), returns `{started_at}`
2. `GET /api/scraper/events/` — SSE stream that replays all past events then follows new ones; safe to reconnect at any time
3. `GET /api/scraper/status/` — returns `{running, events, started_at}` for reconnect on page refresh
4. Same pattern for `/api/scraper/rescore/`, `/rescore/events/`, `/rescore/status/`

On page mount the frontend calls both status endpoints and reconnects to any in-progress run, restoring the progress toast with correct elapsed time.

### Scoring
Claude Haiku returns a breakdown of 5 sub-scores (0–10): `stack_match`, `salary_match`, `role_match`, `work_mode_match`, `contract_match`.

Final score = `sum(weight × sub_score) / sum(weights)` — weighted average using `UserProfile.score_weights` (1=Low / 2=Med / 3=High per criterion).

When the user saves new weights, `_apply_weights()` instantly bulk-rescores all jobs from existing breakdowns — no Claude calls.

### Profile-Aware Scraping
`_scraper_kwargs(profile)` derives per-platform search params from the user profile:
- `search` keyword = first preferred role, or first tech, or `"desenvolvedor"`
- `filter_terms` = preferred_roles + first 5 techs (used as post-filter or server-side filter)
- Nerdin: maps tech names → `filtro_plataforma[]` IDs for server-side filtering (combining with `filtro_cargo[]` uses AND logic and returns zero results — only platform IDs are used)
- GeekHunter: fills the search input via Playwright and presses Enter (no URL-level filtering)
- LinkedIn / Indeed: `keywords=` URL param

### Profile Autofill
LinkedIn profile pages require authentication — URL scraping is blocked. Instead, the user pastes raw profile text into the UI → `POST /api/profile/autofill/` → Claude Haiku extracts `competencies`, `tech_stack`, `preferred_roles`.

### Description Extraction
All scrapers use full untruncated text for field detection (contract_type, work_mode, experience_level) and store up to 6000 chars as description. Previously 3000 chars caused these fields to be missed when the relevant text appeared late in long job postings.

## Behavioral Guidelines

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

### 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

### 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
```

### 5. English Only

**All development must be in English.**

- Variable names, function names, class names, field names: English.
- API routes, query params, JSON keys: English.
- UI labels, button text, error messages: English.
- Code comments (when necessary): English.
- Git commit messages: English.
