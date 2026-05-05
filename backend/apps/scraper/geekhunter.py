import re

BASE_URL = "https://www.geekhunter.com.br"
JOBS_URL = f"{BASE_URL}/vagas"


def _detect_work_mode(text):
    lower = text.lower()
    if "remoto" in lower or "remote" in lower or "home office" in lower:
        return "remote"
    if "híbrido" in lower or "hybrid" in lower:
        return "hybrid"
    if "presencial" in lower or "on-site" in lower:
        return "onsite"
    return "unknown"


def _detect_contract(text):
    lower = text.lower()
    has_pj = "pj" in lower or "pessoa jurídica" in lower
    has_clt = "clt" in lower
    if has_pj and has_clt:
        return "both"
    if has_pj:
        return "pj"
    if has_clt:
        return "clt"
    return "unknown"


def _detect_level(text):
    lower = text.lower()
    if any(k in lower for k in ["sênior", "senior", "sr."]):
        return "senior"
    if any(k in lower for k in ["pleno", "mid", "pl."]):
        return "mid"
    if any(k in lower for k in ["júnior", "junior", "jr.", "estagiário", "trainee"]):
        return "junior"
    return "unknown"


def _parse_salary(text):
    cleaned = re.sub(r",\d{2}", "", text)  # remove decimal part before stripping dots
    cleaned = cleaned.replace(".", "").replace("R$", "").strip()
    nums = [int(n) for n in re.findall(r"\d+", cleaned) if int(n) > 500]
    if len(nums) >= 2:
        return nums[0], nums[1]
    if len(nums) == 1:
        return nums[0], nums[0]
    return None, None


def _parse_detail_page(text):
    """Extract structured job data from the GeekhHunter detail page text.

    Page structure after "Voltar...":
      [0] company name
      [1] company HQ location (skip)
      [2] job title
      [3] work mode (Híbrido / Remoto / Presencial)
      [4] job location
      [5] "Faixa de Remuneração"
      [6] salary value or "Não informada"
      [7] "Nível de Experiência"
      [8] level
      [9+] description / requirements
    """
    lines = [l.strip().replace("\xa0", " ") for l in text.split("\n") if l.strip()]

    start = 0
    for i, line in enumerate(lines):
        if "Voltar" in line:
            start = i + 1
            break
    lines = lines[start:]
    if len(lines) < 5:
        return {}

    company = lines[0]
    # lines[1] is company HQ — skip
    title = lines[2].title() if len(lines) > 2 else ""
    work_mode = _detect_work_mode(lines[3]) if len(lines) > 3 else "unknown"
    location = lines[4] if len(lines) > 4 else ""

    salary_min = salary_max = None
    level = "unknown"
    description = ""

    for i, line in enumerate(lines[5:], start=5):
        if "Faixa de Remuneração" in line:
            for j in range(i + 1, min(i + 4, len(lines))):
                if lines[j] == "Não informada":
                    break
                if "r$" in lines[j].lower():
                    salary_min, salary_max = _parse_salary(lines[j])
                    break
        elif "Nível de Experiência" in line and i + 1 < len(lines):
            level = _detect_level(lines[i + 1])
        elif any(m in line for m in ["Tarefas e Responsabilidades", "Requisitos", "Sobre a ", "Descrição"]):
            description = " ".join(lines[i:])[:3000]
            break

    contract_type = _detect_contract(description + " " + title)

    return {
        "title": title,
        "company": company,
        "location": location,
        "work_mode": work_mode,
        "salary_min": salary_min,
        "salary_max": salary_max,
        "experience_level": level,
        "contract_type": contract_type,
        "description": description,
    }


def _fetch_detail(url):
    """Returns (salary_min, salary_max, work_mode) by re-fetching a single GeekhHunter job page."""
    from playwright.sync_api import sync_playwright
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)
            text = page.evaluate("document.body.innerText")
            browser.close()
        data = _parse_detail_page(text)
        return data.get("salary_min"), data.get("salary_max"), data.get("work_mode", "unknown")
    except Exception:
        return None, None, "unknown"


def fetch_jobs(pages=3, keywords=None, filter_terms=None):
    from playwright.sync_api import sync_playwright

    jobs = []
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
        page = browser.new_page()
        page.set_extra_http_headers({"Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"})

        # Collect job URLs from listing pages
        job_urls = []
        search_applied = False
        for page_num in range(1, pages + 1):
            if search_applied:
                # After search, GeekHunter resets to page 1 of filtered results;
                # click next-page or stop — check if current page has a "next" link
                next_link = page.query_selector("a[aria-label*='próxima'], a[aria-label*='next'], [data-testid='pagination-next']")
                if next_link:
                    try:
                        next_link.click()
                        page.wait_for_timeout(3000)
                    except Exception:
                        break
                else:
                    break
            else:
                url = f"{JOBS_URL}?page={page_num}" if page_num > 1 else JOBS_URL
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    page.wait_for_timeout(3000)
                except Exception:
                    break

                # Apply keyword search on the first page
                if keywords and page_num == 1:
                    try:
                        search_el = page.query_selector("input[placeholder*='cargo'], input[placeholder*='keyword'], input[type='search']")
                        if search_el:
                            search_el.fill(keywords)
                            page.keyboard.press("Enter")
                            page.wait_for_timeout(3000)
                            search_applied = True
                    except Exception:
                        pass

            links = page.query_selector_all("a[href]")
            found = 0
            for link in links:
                href = link.get_attribute("href") or ""
                if "/jobs/" in href and href.startswith("http"):
                    slug = href.rstrip("/").split("/")[-1]
                    if slug and href not in job_urls:
                        job_urls.append(href)
                        found += 1
            if not found:
                break

        # Visit each job detail page
        for url in job_urls:
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(2000)
                text = page.evaluate("document.body.innerText")
                data = _parse_detail_page(text)
                if not data.get("title"):
                    continue

                external_id = url.rstrip("/").split("/")[-1]
                jobs.append({
                    "external_id": external_id,
                    "title": data["title"],
                    "company": data["company"],
                    "location": data["location"],
                    "work_mode": data["work_mode"],
                    "is_remote": data["work_mode"] == "remote",
                    "salary_min": data["salary_min"],
                    "salary_max": data["salary_max"],
                    "tech_stack": [],
                    "url": url,
                    "source": "geekhunter",
                    "contract_type": data["contract_type"],
                    "experience_level": data["experience_level"],
                    "description": data["description"],
                })
            except Exception:
                continue

        browser.close()

    if filter_terms:
        jobs = [j for j in jobs if _matches(j["title"], j.get("description", ""), filter_terms)]
    return jobs


def _matches(title: str, description: str, terms: list[str]) -> bool:
    haystack = (title + " " + description).lower()
    return any(t.lower() in haystack for t in terms)
