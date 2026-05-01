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
    # Remove Brazilian decimal part (e.g. ",00" or ",50") before stripping separators
    text = re.sub(r",\d{2}\b", "", text)
    cleaned = text.replace(".", "").replace("R$", "").replace("Até", "").replace("até", "").strip()
    nums = [int(n) for n in re.findall(r"\d+", cleaned) if int(n) > 500]
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
    if any(k in lower for k in ["sênior", "senior", "sr.", "nível: senior", "nível: sênior"]):
        return "senior"
    if any(k in lower for k in ["pleno", "mid", "pl.", "nível: pleno"]):
        return "mid"
    if any(k in lower for k in ["júnior", "junior", "jr.", "estagiário", "nível: júnior", "nível: junior"]):
        return "junior"
    return "unknown"


def _fetch_detail(url):
    """Returns dict with description, contract_type, experience_level, work_mode, salary_min, salary_max."""
    result = {"description": "", "contract_type": "unknown", "experience_level": "unknown",
              "work_mode": None, "salary_min": None, "salary_max": None}
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return result
        soup = BeautifulSoup(resp.text, "lxml")
        tab = soup.find("div", class_="tab-content")
        if not tab:
            return result
        full_text = tab.get_text("\n", strip=True)

        # Extract description (everything from first content marker)
        for marker in ["Sobre a Vaga", "Descrição da vaga", "Descrição"]:
            idx = full_text.find(marker)
            if idx != -1:
                result["description"] = full_text[idx:idx + 3000].strip()
                break

        result["contract_type"] = _detect_contract(full_text)
        result["experience_level"] = _detect_level(full_text)

        # Work mode from detail page overrides listing (more accurate)
        work_mode, _ = _parse_work_mode(full_text)
        if work_mode != "onsite" or "híbrido" in full_text.lower() or "remoto" in full_text.lower():
            result["work_mode"] = work_mode

        # Try salary from "Faixa salarial:" line (Benefícios tab) first
        sal_match = re.search(r"[Ff]aixa salarial[:\s]+([^\n]+)", full_text)
        if sal_match:
            sal_min, sal_max = _parse_salary(sal_match.group(1))
            if sal_min:
                result["salary_min"], result["salary_max"] = sal_min, sal_max

        # Fallback: first line of tab-content is always the salary display value
        if not result["salary_min"]:
            first_line = full_text.split("\n")[0].strip()
            sal_min, sal_max = _parse_salary(first_line)
            if sal_min:
                result["salary_min"], result["salary_max"] = sal_min, sal_max

    except Exception:
        pass
    return result


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
                detail = _fetch_detail(job["url"])
                job["description"] = detail["description"]
                if detail["contract_type"] != "unknown":
                    job["contract_type"] = detail["contract_type"]
                if detail["experience_level"] != "unknown":
                    job["experience_level"] = detail["experience_level"]
                if detail["work_mode"] is not None:
                    job["work_mode"] = detail["work_mode"]
                    job["is_remote"] = detail["work_mode"] == "remote"
                if detail["salary_min"] and not job["salary_min"]:
                    job["salary_min"] = detail["salary_min"]
                    job["salary_max"] = detail["salary_max"]
                jobs.append(job)
    return jobs
