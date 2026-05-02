# Job Matching

Job aggregator that scrapes LinkedIn, Nerdin, GeekhHunter, and Indeed, then ranks results by compatibility with your profile using Claude AI.

## Features

- Scrapes job listings from LinkedIn, Nerdin, GeekhHunter, and Indeed
- Scores each job (0–10) across five criteria: stack, salary, role, work mode, and contract
- Editable candidate profile (tech stack, salary range, contract preference, work mode, competencies)
- Re-score all jobs after updating your profile
- Mark jobs as Applied / Not selected
- Applied jobs tab with status tracking
- Filter by source, contract type, work mode, experience level, salary range, and score
- Stats tab: dual-bar chart of tech stack occurrences and average salary, filterable by level, stack, and sort order
- Periodic auto-scrape via APScheduler

## Stack

| Layer    | Technology                                      |
|----------|-------------------------------------------------|
| Frontend | React + Vite + TypeScript + Tailwind CSS + ECharts |
| Backend  | Django REST Framework (Python 3.12)             |
| Database | PostgreSQL                                      |
| Infra    | Docker Compose (`restart: always` on all services) |
| Scraping | requests + BeautifulSoup4 (LinkedIn, Nerdin) / Playwright (GeekhHunter, Indeed) / curl-cffi (Indeed RPC) |
| AI       | Anthropic Claude Haiku via SDK                  |

## Getting Started

### Prerequisites

- Docker + Docker Compose
- An [Anthropic API key](https://console.anthropic.com/)

### Setup

```bash
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY (and optionally DJANGO_SECRET_KEY)
docker compose up --build
```

The app will be available at:

| Service  | URL                       |
|----------|---------------------------|
| Frontend | http://localhost:7778      |
| API      | http://localhost:8889      |

### First run

1. Open the app and go to the **Profile** tab
2. Fill in your tech stack, competencies, salary range, and preferences
3. Click **Save Profile**
4. Go back to **Jobs** and click **Scrape Now**
5. Jobs will be fetched and scored automatically

After updating your profile, click **Re-score Jobs** to re-rank all existing jobs.

## API

### `GET /api/jobs/`

Returns scored job listings.

| Query param          | Type   | Description                                      |
|----------------------|--------|--------------------------------------------------|
| `source`             | string | `linkedin` \| `nerdin` \| `geekhunter` \| `indeed` |
| `contract_type`      | string | `pj` \| `clt` \| `both`                         |
| `work_mode`          | string | `remote` \| `hybrid` \| `onsite`                |
| `experience_level`   | string | `junior` \| `mid` \| `senior`                   |
| `min_score`          | float  | Minimum score (e.g. `7`)                         |
| `salary_min`         | int    | Filter jobs whose max salary ≥ this value        |
| `salary_max`         | int    | Filter jobs whose min salary ≤ this value        |
| `application_status` | string | `applied` \| `rejected`                         |
| `search`             | string | Full-text search on title, company, description  |
| `sort`               | string | `score` \| `date` \| `salary` \| `scraped`      |

### `POST /api/jobs/<id>/status/`

Update application status for a job.

```json
{ "status": "applied" }
```

### `POST /api/scraper/run/`

Triggers a manual scrape. Optionally restrict to specific sources:

```json
{ "sources": ["linkedin", "nerdin"] }
```

### `POST /api/scraper/rescore/`

Re-scores all jobs using the current profile.

### `GET /api/jobs/stats/`

Returns aggregated stats for the Stats tab.

| Query param | Type   | Description                                             |
|-------------|--------|---------------------------------------------------------|
| `level`     | string | Comma-separated levels to filter stack stats (e.g. `junior,mid`) |

### `GET /api/profile/`

Returns the current candidate profile.

### `PUT /api/profile/`

Updates the candidate profile.

## Environment Variables

See `.env.example` for all required variables.

| Variable             | Description                          |
|----------------------|--------------------------------------|
| `POSTGRES_*`         | PostgreSQL connection settings       |
| `DJANGO_SECRET_KEY`  | Django secret key                    |
| `DJANGO_DEBUG`       | Enable debug mode (`True`/`False`)   |
| `ANTHROPIC_API_KEY`  | Anthropic API key for job scoring    |
| `VITE_API_URL`       | Backend URL used by the frontend     |

## Management Commands

```bash
# Backfill descriptions and contract_type for existing jobs
docker compose exec backend python manage.py fill_descriptions
```
