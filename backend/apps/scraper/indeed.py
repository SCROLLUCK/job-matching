import re
import json
from urllib.parse import quote
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from .linkedin import _extract_tech_stack, _detect_level

BASE_URL = "https://br.indeed.com"
SEARCH_URL = f"{BASE_URL}/jobs"
DETAIL_URL = f"{BASE_URL}/viewjob?jk={{job_id}}"
DESCS_URL = f"{BASE_URL}/rpc/jobdescs?jks={{jks}}"

BROWSER_ARGS = ["--no-sandbox", "--disable-dev-shm-usage", "--disable-blink-features=AutomationControlled"]
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
BATCH_SIZE = 20


def _parse_salary(text):
    text = re.sub(r"por\s+(mês|hora|ano|semana|dia)", "", text, flags=re.IGNORECASE)
    text = re.sub(r",\d{2}\b", "", text)
    cleaned = text.replace(".", "").replace("R$", "").replace("–", " ").replace("-", " ").strip()
    nums = [int(n) for n in re.findall(r"\d+", cleaned) if int(n) > 500]
    if len(nums) >= 2:
        return nums[0], nums[1]
    if len(nums) == 1:
        return nums[0], nums[0]
    return None, None


def _detect_work_mode(text):
    lower = text.lower()
    if "remoto" in lower or "remote" in lower or "home office" in lower:
        return "remote", True
    if "híbrido" in lower or "hibrido" in lower or "hybrid" in lower:
        return "hybrid", False
    if "presencial" in lower or "on-site" in lower or "onsite" in lower:
        return "onsite", False
    return "unknown", None


def _detect_contract(text, snippets=None):
    sources = [text.lower()]
    if snippets:
        sources += [s.lower() for s in snippets]
    combined = " ".join(sources)
    has_pj = "pessoa jurídica" in combined or " pj " in combined
    has_clt = "efetivo clt" in combined or " clt" in combined
    if has_pj and has_clt:
        return "both"
    if has_pj:
        return "pj"
    if has_clt:
        return "clt"
    return "unknown"


def _parse_card(card):
    jk_el = card.query_selector("[data-jk]")
    if not jk_el:
        return None
    jk = jk_el.get_attribute("data-jk")
    if not jk:
        return None

    title_el = card.query_selector("[id^='jobTitle-']")
    title = title_el.inner_text().strip() if title_el else ""
    if not title:
        return None

    company_el = card.query_selector("[data-testid='company-name']")
    company = company_el.inner_text().strip() if company_el else ""

    loc_el = card.query_selector("[data-testid='text-location']")
    location = loc_el.inner_text().strip() if loc_el else ""

    sal_el = card.query_selector("[class*='salary-snippet'] span")
    salary_text = sal_el.inner_text().strip() if sal_el else ""
    salary_min, salary_max = _parse_salary(salary_text)

    snippets = [el.inner_text().strip() for el in card.query_selector_all("[data-testid='attribute_snippet_testid'] span")]

    work_mode, is_remote = _detect_work_mode(f"{title} {location}")
    contract_type = _detect_contract("", snippets)
    is_remote = is_remote if is_remote is not None else False

    return {
        "external_id": jk,
        "title": title,
        "company": company,
        "location": location,
        "work_mode": work_mode,
        "is_remote": is_remote,
        "salary_min": salary_min,
        "salary_max": salary_max,
        "tech_stack": [],
        "url": DETAIL_URL.format(job_id=jk),
        "source": "indeed",
        "contract_type": contract_type,
        "experience_level": _detect_level(title),
        "description": "",
    }


def _fetch_descriptions(browser, jks):
    """Batch-fetch descriptions using a fresh browser context to avoid Cloudflare session taint."""
    results = {}
    ctx = browser.new_context(
        user_agent=USER_AGENT,
        viewport={"width": 1280, "height": 800},
        locale="pt-BR",
    )
    page = ctx.new_page()
    page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    for i in range(0, len(jks), BATCH_SIZE):
        batch = jks[i:i + BATCH_SIZE]
        jks_param = "%2C".join(batch)
        try:
            page.goto(DESCS_URL.format(jks=jks_param), wait_until="domcontentloaded", timeout=20000)
            page.wait_for_timeout(1000)
            body = page.inner_text("body").strip()
            if body.startswith("{"):
                results.update(json.loads(body))
        except Exception:
            pass

    ctx.close()
    return results


def fetch_jobs(keywords="desenvolvedor", location="Brasil", pages=3, filter_terms=None):
    stubs = []
    with sync_playwright() as p:
        browser = p.chromium.launch(args=BROWSER_ARGS)
        ctx = browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1280, "height": 800},
            locale="pt-BR",
        )
        page = ctx.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        for pg in range(pages):
            url = f"{SEARCH_URL}?q={quote(keywords)}&l={quote(location)}&start={pg * 10}"
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(2000)
            except Exception:
                break

            cards = page.query_selector_all("li:has([data-jk])")
            if not cards:
                break

            for card in cards:
                stub = _parse_card(card)
                if stub:
                    stubs.append(stub)

        # Batch-fetch descriptions in a fresh context (avoids Cloudflare session taint)
        jks = [s["external_id"] for s in stubs]
        descriptions = _fetch_descriptions(browser, jks) if stubs else {}

        browser.close()

    for stub in stubs:
        html = descriptions.get(stub["external_id"], "")
        if not html:
            continue
        text = BeautifulSoup(html, "lxml").get_text("\n", strip=True)[:3000]
        stub["description"] = text
        stub["tech_stack"] = _extract_tech_stack(text)

        if stub["contract_type"] == "unknown":
            contract = _detect_contract(text)
            if contract != "unknown":
                stub["contract_type"] = contract

        if stub["work_mode"] == "unknown":
            wm, is_remote = _detect_work_mode(text)
            if wm != "unknown":
                stub["work_mode"] = wm
                stub["is_remote"] = is_remote if is_remote is not None else False

        if stub["experience_level"] == "unknown":
            level = _detect_level(text)
            if level != "unknown":
                stub["experience_level"] = level

    return stubs
