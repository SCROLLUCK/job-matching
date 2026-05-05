import json

from django.http import StreamingHttpResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.jobs.models import Job
from apps.jobs.ranker import score_job
from apps.profile.models import UserProfile

from . import geekhunter, indeed, linkedin, nerdin

SCRAPERS = {
    "nerdin": (nerdin.fetch_jobs, {"pages": 3}),
    "linkedin": (linkedin.fetch_jobs, {"pages": 3}),
    "geekhunter": (geekhunter.fetch_jobs, {"pages": 2}),
    "indeed": (indeed.fetch_jobs, {"pages": 3}),
}


def _sse(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


def _clean_title(title: str) -> str:
    import re
    return re.sub(r"\s+\b(NEW|NOVO|NOVA)\b\s*$", "", title, flags=re.IGNORECASE).strip()


def _save_jobs(job_list):
    profile = UserProfile.get()
    created = 0
    for data in job_list:
        if not data.get("url") or not data.get("title"):
            continue
        if Job.objects.filter(external_id=data["external_id"], source=data["source"]).exists():
            continue
        result = score_job(data, profile)
        Job.objects.create(
            external_id=data["external_id"],
            title=_clean_title(data["title"]),
            company=data.get("company", ""),
            description=data.get("description", ""),
            url=data["url"],
            location=data.get("location", ""),
            work_mode=data.get("work_mode", "unknown"),
            contract_type=data.get("contract_type", "unknown"),
            salary_min=data.get("salary_min"),
            salary_max=data.get("salary_max"),
            tech_stack=data.get("tech_stack", []),
            experience_level=data.get("experience_level", "unknown"),
            source=data["source"],
            score=result.get("score"),
            score_breakdown=result.get("breakdown", {}),
        )
        created += 1
    return created


def _stream_scrape(sources):
    results = {}
    for source in sources:
        fn, kwargs = SCRAPERS.get(source, (None, {}))
        if not fn:
            continue
        yield _sse({"type": "source_start", "source": source})
        try:
            jobs = fn(**kwargs)
            count = _save_jobs(jobs)
            results[source] = count
            yield _sse({"type": "source_done", "source": source, "count": count})
        except Exception as e:
            results[f"{source}_error"] = str(e)
            yield _sse({"type": "source_error", "source": source, "error": str(e)})
    results["scraped_at"] = timezone.now().isoformat()
    yield _sse({"type": "complete", **results})


def _stream_rescore(profile):
    jobs = list(Job.objects.all())
    total = len(jobs)
    updated = 0
    for i, job in enumerate(jobs, 1):
        result = score_job({
            "title": job.title, "company": job.company, "description": job.description,
            "tech_stack": job.tech_stack, "salary_min": job.salary_min, "salary_max": job.salary_max,
            "contract_type": job.contract_type, "work_mode": job.work_mode,
        }, profile)
        if result:
            job.score = result.get("score")
            job.score_breakdown = result.get("breakdown", {})
            job.save(update_fields=["score", "score_breakdown"])
            updated += 1
        if i % 5 == 0 or i == total:
            yield _sse({"processed": i, "total": total, "updated": updated})
    yield _sse({"type": "complete", "updated": updated})


class ScrapeView(APIView):
    def post(self, request):
        sources = request.data.get("sources", list(SCRAPERS.keys()))
        return StreamingHttpResponse(_stream_scrape(sources), content_type="text/event-stream")


class RescoreView(APIView):
    def post(self, request):
        profile = UserProfile.get()
        if not profile.competencies and not profile.tech_stack:
            return Response({"error": "Profile is empty."}, status=status.HTTP_400_BAD_REQUEST)
        return StreamingHttpResponse(_stream_rescore(profile), content_type="text/event-stream")
