import re
import requests
from bs4 import BeautifulSoup

SEARCH_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    "Referer": "https://www.linkedin.com/",
}


def _detect_work_mode(text):
    lower = text.lower()
    if "remoto" in lower or "remote" in lower:
        return "remote", True
    if "híbrido" in lower or "hibrido" in lower or "hybrid" in lower:
        return "hybrid", False
    if "presencial" in lower or "on-site" in lower or "onsite" in lower:
        return "onsite", False
    return "unknown", None


def _detect_level(title):
    lower = title.lower()
    if any(k in lower for k in ["sênior", "senior", "sr.", " sr "]):
        return "senior"
    if any(k in lower for k in ["pleno", "mid", "pl.", " pl "]):
        return "mid"
    if any(k in lower for k in ["júnior", "junior", "jr.", " jr "]):
        return "junior"
    return "unknown"


def _parse_item(item):
    title_el = item.find("h3")
    title = title_el.get_text(strip=True) if title_el else ""
    if not title:
        return None

    company_el = item.find("h4")
    company = company_el.get_text(strip=True) if company_el else ""

    location_el = item.find(class_=re.compile(r"location|subtitle"))
    location = location_el.get_text(strip=True) if location_el else ""

    link_el = item.find("a", href=True)
    url = link_el["href"].split("?")[0] if link_el else ""
    if not url:
        return None

    external_id = url.rstrip("/").split("/")[-1]
    work_mode, is_remote = _detect_work_mode(f"{title} {location}")

    return {
        "external_id": external_id,
        "title": title,
        "company": company,
        "location": location,
        "work_mode": work_mode,
        "is_remote": is_remote,
        "salary_min": None,
        "salary_max": None,
        "tech_stack": [],
        "url": url,
        "source": "linkedin",
        "contract_type": "unknown",
        "experience_level": _detect_level(title),
    }


def fetch_jobs(keywords="desenvolvedor", location="Brazil", pages=3):
    jobs = []
    for page in range(pages):
        params = {
            "keywords": keywords,
            "location": location,
            "start": page * 25,
            "f_TPR": "r86400",
        }
        resp = requests.get(SEARCH_URL, headers=HEADERS, params=params, timeout=15)
        if resp.status_code != 200:
            break
        soup = BeautifulSoup(resp.text, "lxml")
        items = soup.find_all("li")
        for item in items:
            job = _parse_item(item)
            if job:
                jobs.append(job)
        if not items:
            break
    return jobs
