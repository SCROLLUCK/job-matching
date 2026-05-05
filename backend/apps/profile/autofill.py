import json

import anthropic
from django.conf import settings


def extract_profile_data(text: str) -> dict:
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=800,
        messages=[{
            "role": "user",
            "content": f"""Extract structured professional profile data from this LinkedIn profile page text (copied from the browser).

PAGE TEXT:
{text[:8000]}

Return ONLY valid JSON with no other text:
{{
  "competencies": "<2-4 sentence prose summary of background, skills, years of experience>",
  "tech_stack": ["<tech1>", "<tech2>"],
  "preferred_roles": ["<role1>", "<role2>"]
}}

Rules:
- tech_stack: concrete technologies, frameworks, languages, tools only (e.g. Python, React, Docker — not soft skills)
- preferred_roles: job titles this person has held or would target
- competencies: first-person style description of their background, in English
- If a field cannot be determined, use "" or []""",
        }],
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    return json.loads(raw)
