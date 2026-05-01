import json

import anthropic
from django.conf import settings


def score_job(job_data: dict, profile) -> dict:
    """Score a job 0-10 against user profile using Claude Haiku. Returns empty dict if no API key or empty profile."""
    if not settings.ANTHROPIC_API_KEY:
        return {}
    if not profile.competencies and not profile.tech_stack:
        return {}

    salary_info = "Not specified"
    if job_data.get("salary_min") and job_data.get("salary_max"):
        salary_info = f"R${job_data['salary_min']:,} - R${job_data['salary_max']:,}"

    desired_salary_min = "Not specified"
    desired_salary_max = "Not specified"
    if profile.desired_salary_min:
        desired_salary_min = f"R${profile.desired_salary_min:,}/month"
    if profile.desired_salary_max:
        desired_salary_max = f"R${profile.desired_salary_max:,}/month"

    prompt = f"""Score this job opening from 0.0 to 10.0 based on compatibility with the candidate profile.

CANDIDATE PROFILE:
- Tech stack: {', '.join(profile.tech_stack) or 'Not specified'}
- Minimum acceptable salary: {desired_salary_min}
- Maximum desired salary: {desired_salary_max}
- Contract preference: {profile.preferred_contract_type}
- Work mode preference: {profile.preferred_work_mode}
- Preferred roles: {', '.join(profile.preferred_roles) or 'Not specified'}
- Competencies: {profile.competencies[:800] if profile.competencies else 'Not specified'}

JOB OPENING:
- Title: {job_data['title']}
- Company: {job_data.get('company', 'Unknown')}
- Tech stack: {', '.join(job_data.get('tech_stack', [])) or 'Not specified'}
- Salary: {salary_info}
- Contract: {job_data.get('contract_type', 'unknown')}
- Work mode: {job_data.get('work_mode', 'unknown')}
- Description: {job_data.get('description', '')[:2000]}

Scoring rules — apply strictly:
- stack_match: use BOTH the "Tech stack" field AND any technologies mentioned in the description. If neither lists any technology, score 0.0.
- salary_match: score 0.0 if no salary is specified. If salary is specified: compare against "Minimum acceptable salary" in the profile. Score 10.0 if job salary >= minimum acceptable salary. Score proportionally lower only if job salary is BELOW the minimum acceptable salary. Paying above the maximum desired salary is still 10.0 — never penalize for paying too much.
- work_mode_match: score 0.0 if work mode is "unknown".
- contract_match: score 0.0 if contract is "unknown".
- role_match: always score based on title and description — never 0.0 unless completely unrelated.
- The overall score is the average of all five criteria.

Return ONLY valid JSON, no other text:
{{
  "score": <float 0.0-10.0>,
  "breakdown": {{
    "stack_match": <float 0.0-10.0>,
    "salary_match": <float 0.0-10.0>,
    "role_match": <float 0.0-10.0>,
    "work_mode_match": <float 0.0-10.0>,
    "contract_match": <float 0.0-10.0>
  }},
}}"""

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.content[0].text.strip()
    # strip markdown code fences if present
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}
