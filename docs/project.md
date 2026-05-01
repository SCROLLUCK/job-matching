# Job Matching — Project Decisions

## Stack
- **Frontend**: React + Vite + TypeScript + Tailwind CSS — port `7778`
- **Backend**: Django REST Framework — port `8889`
- **DB**: PostgreSQL — port `5432`
- **Infra**: Docker Compose with `restart: always` on all services
- **AI**: Anthropic Claude Haiku via SDK

## Scraping architecture

### Sources
| Source      | Method                        | `source` value |
|-------------|-------------------------------|----------------|
| LinkedIn    | requests + BeautifulSoup      | `linkedin`     |
| Nerdin      | requests + BeautifulSoup      | `nerdin`       |
| GeekhHunter | Playwright (Next.js SPA)      | `geekhunter`   |

### Scrape flow
1. Each scraper fetches the job listing pages
2. For each job, the scraper visits the detail page to extract description and detect `contract_type`
3. Only new jobs (by `external_id + source`) are saved
4. Each new job is scored by Claude before being saved

### LinkedIn external_id
- Stored as the full URL slug (e.g. `developer-at-company-4408774896`)
- The numeric job ID is the last segment after the final `-`
- `_fetch_detail` extracts the numeric ID before calling the LinkedIn API endpoint

### LinkedIn detail page
- Uses the public API: `https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{id}`
- Description selector: `show-more-less-html__markup`

### Nerdin detail page
- Description starts after the "Sobre a Vaga" / "Descrição da vaga" markers
- The `tab-content` div contains noise at the top (masked contacts, premium upsells) — stripped by finding those markers

### Contract type detection
- Detected from description text in both LinkedIn and Nerdin scrapers
- Logic: look for "pj", "pessoa jurídica", "clt" in lowercase text
- If both found → `"both"`, otherwise `"pj"` or `"clt"` or `"unknown"`

### Management command
- `fill_descriptions`: backfills `description` and `contract_type` for jobs that have none
- Calls `_fetch_detail` for each source

## Scoring

### Claude Haiku prompt
- Scores five criteria: `stack_match`, `salary_match`, `role_match`, `work_mode_match`, `contract_match`
- Rule: if a criterion is missing in the job listing, score is **0.0** (not 5.0)
- Overall score is the average of the five criteria
- Returns JSON with `score`, `breakdown`, and `summary`

### Rescore
- `POST /api/scraper/rescore/` re-scores all jobs using the current profile
- Useful after updating the profile
- Available in the Profile tab via "Re-score Jobs" button

## Application status
- `application_status` field on `Job`: `""` (not applied) | `"applied"` | `"rejected"`
- Replaces the original boolean `applied` field (migrated in `0003`)
- Card shows green border when applied, red border when rejected
- "Applied" tab shows all jobs with `application_status = "applied"`, fetched separately

## Job ordering
- Default sort: `score DESC NULLS LAST, scraped_at DESC`
- Uses `F("score").desc(nulls_last=True)` to push unscored jobs to the bottom

## Profile
- Singleton model (`pk=1`, created on first access via `get_or_create`)
- Fields: `competencies` (free text), `tech_stack` (list), `preferred_roles` (list), `desired_salary_min/max`, `preferred_contract_type`, `preferred_work_mode`

## Frontend
- Two-column grid of `JobCard` components (`xl:grid-cols-2`)
- Filter drawer on the left side of the Jobs tab
- Tabs: Jobs / Applied / Profile
- Job card shows: title, company, source badge, status button, salary/contract/work mode/level grid, tech stack tags, description (3 lines, clipped), score bars

## Ports
| Service  | Host port | Container port |
|----------|-----------|----------------|
| Frontend | 7778      | 5173           |
| Backend  | 8889      | 8889           |
| DB       | —         | 5432 (internal)|
