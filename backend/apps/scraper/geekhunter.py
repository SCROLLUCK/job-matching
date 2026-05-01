import re

BASE_URL = "https://www.geekhunter.com.br"
JOBS_URL = f"{BASE_URL}/vagas"


def _detect_work_mode(text):
    lower = text.lower()
    if "remoto" in lower or "remote" in lower:
        return "remote", True
    if "híbrido" in lower or "hybrid" in lower:
        return "hybrid", False
    if "presencial" in lower or "on-site" in lower:
        return "onsite", False
    return "unknown", None


def _detect_contract(text):
    lower = text.lower()
    if "pj" in lower or "pessoa jurídica" in lower:
        return "pj"
    if "clt" in lower:
        return "clt"
    return "unknown"


def _detect_level(text):
    lower = text.lower()
    if any(k in lower for k in ["sênior", "senior", "sr."]):
        return "senior"
    if any(k in lower for k in ["pleno", "mid", "pl."]):
        return "mid"
    if any(k in lower for k in ["júnior", "junior", "jr."]):
        return "junior"
    return "unknown"


def _parse_salary(text):
    cleaned = text.replace(".", "").replace(",", "").replace("R$", "").strip()
    nums = [int(n) for n in re.findall(r"\d+", cleaned) if int(n) > 100]
    if len(nums) >= 2:
        return nums[0], nums[1]
    if len(nums) == 1:
        return nums[0], nums[0]
    return None, None


def fetch_jobs(pages=3):
    from playwright.sync_api import sync_playwright

    jobs = []
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
        page = browser.new_page()
        page.set_extra_http_headers({
            "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
        })

        for page_num in range(1, pages + 1):
            url = f"{JOBS_URL}?page={page_num}" if page_num > 1 else JOBS_URL
            page.goto(url, wait_until="networkidle", timeout=30000)

            cards = page.query_selector_all("[data-testid='job-card'], article, .job-card, [class*='JobCard'], [class*='job-card']")
            if not cards:
                break

            for card in cards:
                try:
                    title = card.query_selector("h2, h3, [class*='title'], [class*='Title']")
                    title_text = title.inner_text().strip() if title else ""
                    if not title_text:
                        continue

                    company_el = card.query_selector("[class*='company'], [class*='Company']")
                    company = company_el.inner_text().strip() if company_el else ""

                    location_el = card.query_selector("[class*='location'], [class*='Location']")
                    location = location_el.inner_text().strip() if location_el else ""

                    salary_el = card.query_selector("[class*='salary'], [class*='Salary'], [class*='salario']")
                    salary_text = salary_el.inner_text() if salary_el else ""
                    salary_min, salary_max = _parse_salary(salary_text)

                    tags_els = card.query_selector_all("[class*='tag'], [class*='Tag'], [class*='skill'], [class*='Skill']")
                    tech_stack = [t.inner_text().strip() for t in tags_els if t.inner_text().strip()]

                    link_el = card.query_selector("a[href]")
                    href = link_el.get_attribute("href") if link_el else ""
                    url_job = href if href.startswith("http") else f"{BASE_URL}{href}"

                    external_id = href.rstrip("/").split("/")[-1] if href else ""
                    if not external_id or not title_text:
                        continue

                    all_text = f"{title_text} {location} {salary_text}"
                    work_mode, is_remote = _detect_work_mode(all_text)

                    description = ""
                    if url_job:
                        try:
                            detail = browser.new_page()
                            detail.goto(url_job, wait_until="domcontentloaded", timeout=20000)
                            desc_el = detail.query_selector("[class*='description'], [class*='Description'], [class*='descricao'], article, main")
                            description = desc_el.inner_text().strip()[:3000] if desc_el else ""
                            detail.close()
                        except Exception:
                            pass

                    jobs.append({
                        "external_id": external_id,
                        "title": title_text,
                        "company": company,
                        "location": location,
                        "work_mode": work_mode,
                        "is_remote": is_remote,
                        "salary_min": salary_min,
                        "salary_max": salary_max,
                        "tech_stack": tech_stack,
                        "url": url_job,
                        "source": "geekhunter",
                        "contract_type": _detect_contract(all_text),
                        "experience_level": _detect_level(title_text),
                        "description": description,
                    })
                except Exception:
                    continue

        browser.close()
    return jobs
