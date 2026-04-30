import re
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://nerdin.com.br"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}


def _parse_salary(text):
    cleaned = text.replace(".", "").replace(",", "").replace("R$", "").strip()
    nums = [int(n) for n in re.findall(r"\d+", cleaned) if int(n) > 100]
    if len(nums) >= 2:
        return nums[0], nums[1]
    if len(nums) == 1:
        return nums[0], nums[0]
    return None, None


def _parse_work_mode(text):
    lower = text.lower()
    if "remoto" in lower or "remote" in lower:
        return "remote", True
    if "híbrido" in lower or "hibrido" in lower or "hybrid" in lower:
        return "hybrid", False
    return "onsite", False


def _parse_card(card):
    title_el = card.find("h3", class_="vaga-titulo")
    title = title_el.get_text(" ", strip=True) if title_el else ""

    company_el = card.find("div", class_="vaga-empresa")
    company = company_el.get_text(" ", strip=True) if company_el else ""

    location_el = card.find("div", class_="vaga-local")
    location_text = location_el.get_text(" ", strip=True) if location_el else ""

    salary_el = card.find("div", class_="vaga-salario--valor")
    salary_min, salary_max = _parse_salary(salary_el.get_text() if salary_el else "")

    tags = [a.get_text(strip=True).lstrip("#") for a in card.find_all("a", class_="hashtag")]

    link_el = card.find("a", class_="btn-ver-vaga")
    path = link_el["href"] if link_el and link_el.get("href") else ""
    url = f"{BASE_URL}/{path}" if path and not path.startswith("http") else path

    external_id = path.split("/")[-1].replace(".php", "") if path else ""
    if not external_id:
        return None

    work_mode, is_remote = _parse_work_mode(location_text)

    return {
        "external_id": external_id,
        "title": title,
        "company": company,
        "location": location_text,
        "work_mode": work_mode,
        "is_remote": is_remote,
        "salary_min": salary_min,
        "salary_max": salary_max,
        "tech_stack": tags,
        "url": url,
        "source": "nerdin",
        "contract_type": "unknown",
        "experience_level": "unknown",
    }


def fetch_jobs(pages=3):
    jobs = []
    for page in range(1, pages + 1):
        resp = requests.get(f"{BASE_URL}/vagas.php?pagina={page}", headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            break
        soup = BeautifulSoup(resp.text, "lxml")
        cards = soup.find_all("div", class_="vaga-card")
        if not cards:
            break
        for card in cards:
            job = _parse_card(card)
            if job:
                jobs.append(job)
    return jobs
