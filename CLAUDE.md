# job-matching

Job aggregator that scrapes LinkedIn, Nerdin, GeekhHunter, and Indeed and ranks results by compatibility with the user profile.

## Tech Stack

### Frontend
- React + Vite + TypeScript + Tailwind CSS + ECharts

### Backend
- Django REST Framework (Python 3.12)
- APScheduler for periodic scraping
- Playwright (GeekhHunter, Indeed — Cloudflare bypass via fresh context + `/rpc/jobdescs` RPC endpoint)
- requests + BeautifulSoup4 (Nerdin, LinkedIn)
- Claude API (Haiku) for job scoring

### Database
- PostgreSQL

### Infrastructure
- Docker (frontend, backend, database)

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
