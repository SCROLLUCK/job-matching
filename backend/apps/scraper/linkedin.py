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


DETAIL_URL = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"

KNOWN_TECHS = [
    "python", "django", "fastapi", "flask", "node", "node.js", "express", "nestjs",
    "react", "react native", "next.js", "nextjs", "vue", "angular", "svelte",
    "typescript", "javascript", "html", "html5", "css", "css3", "bootstrap", "tailwind",
    "java", "spring", "kotlin", "scala", "go", "golang", "rust", "c#", ".net", "asp.net",
    "c++", "c", "php", "laravel", "ruby", "rails",
    "sql", "mysql", "postgresql", "postgres", "sqlite", "sql server", "oracle", "mongodb",
    "redis", "elasticsearch", "dynamodb", "firebase",
    "docker", "kubernetes", "aws", "azure", "gcp", "terraform", "ansible",
    "git", "github", "gitlab", "ci/cd", "jenkins",
    "graphql", "rest", "grpc", "kafka", "rabbitmq",
    "linux", "bash", "shell", "nginx",
    "power bi", "power platform", "power apps", "vba", "excel",
    "figma", "photoshop",
]


def _extract_tech_stack(text):
    lower = text.lower()
    found = []
    for tech in KNOWN_TECHS:
        pattern = r'\b' + re.escape(tech) + r'\b'
        if re.search(pattern, lower):
            found.append(tech)
    return found


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


def _extract_salary(description):
    for line in description.split("\n"):
        lower = line.lower()
        if "r$" in lower or "salário" in lower or "remuneração" in lower:
            s_min, s_max = _parse_salary(line)
            if s_min and s_min > 1000:
                return s_min, s_max
    return None, None


def _fetch_detail(job_id):
    """Returns (description, contract_type, salary_min, salary_max, work_mode) from the LinkedIn job posting API."""
    try:
        numeric_id = job_id.split("-")[-1] if not job_id.isdigit() else job_id
        resp = requests.get(DETAIL_URL.format(job_id=numeric_id), headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return "", "unknown", None, None, "unknown"
        soup = BeautifulSoup(resp.text, "lxml")
        desc = soup.find(class_="show-more-less-html__markup")
        text = desc.get_text("\n", strip=True)[:3000] if desc else ""
        salary_min, salary_max = _extract_salary(text)
        work_mode, _ = _detect_work_mode(text)
        return text, _detect_contract(text), salary_min, salary_max, work_mode
    except Exception:
        return "", "unknown", None, None, "unknown"


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
                description, contract_type, salary_min, salary_max, work_mode = _fetch_detail(job["external_id"])
                job["description"] = description
                if contract_type != "unknown":
                    job["contract_type"] = contract_type
                if salary_min:
                    job["salary_min"] = salary_min
                    job["salary_max"] = salary_max
                if job["work_mode"] == "unknown" and work_mode != "unknown":
                    job["work_mode"] = work_mode
                if description:
                    job["tech_stack"] = _extract_tech_stack(description)
                jobs.append(job)
        if not items:
            break
    return jobs
