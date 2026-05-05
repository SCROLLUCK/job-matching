import json

import anthropic
from django.conf import settings
from playwright.sync_api import sync_playwright


def _scrape_linkedin_profile(url: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            locale="pt-BR",
        )
        page = context.new_page()
        page.goto(url, timeout=30000, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)
        text = page.inner_text("body")
        browser.close()
    return text[:8000]


def extract_profile_data(url: str) -> dict:
    page_text = _scrape_linkedin_profile(url)

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=800,
        messages=[{
            "role": "user",
            "content": f"""Extract structured professional profile data from this LinkedIn profile page.

PAGE TEXT:
{page_text}

Return ONLY valid JSON with no other text:
{{
  "competencies": "<2-4 sentence prose summary of background, skills, years of experience>",
  "tech_stack": ["<tech1>", "<tech2>"],
  "preferred_roles": ["<role1>", "<role2>"]
}}

Rules:
- tech_stack: concrete technologies, frameworks, languages, tools only
- preferred_roles: job titles the person has held or would target
- competencies: first-person style description of their background
- If a field cannot be determined, use "" or []""",
        }],
    )

    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    return json.loads(text)
