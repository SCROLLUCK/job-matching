import json
import threading
import time as _time

from django.http import StreamingHttpResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.jobs.models import Job
from apps.jobs.ranker import score_job
from apps.profile.models import UserProfile

from . import geekhunter, indeed, linkedin, nerdin

_lock = threading.Lock()
_scrape_state = {"running": False, "events": [], "started_at": None}
_rescore_state = {"running": False, "events": [], "started_at": None}


def _scraper_kwargs(profile):
    roles = profile.preferred_roles or []
    techs = profile.tech_stack or []
    search = roles[0] if roles else (techs[0] if techs else "desenvolvedor")
    filter_terms = roles + techs[:5] if (roles or techs) else []
    return {
        "nerdin":      {"pages": 3, "preferred_roles": roles, "tech_stack": techs, "filter_terms": filter_terms or None},
        "linkedin":    {"pages": 3, "keywords": search},
        "geekhunter":  {"pages": 2, "keywords": search, "filter_terms": filter_terms or None},
        "indeed":      {"pages": 3, "keywords": search},
    }


SCRAPERS = {
    "nerdin": nerdin.fetch_jobs,
    "linkedin": linkedin.fetch_jobs,
    "geekhunter": geekhunter.fetch_jobs,
    "indeed": indeed.fetch_jobs,
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


def _push(state, event):
    with _lock:
        state["events"].append(event)


def _run_scrape_bg(sources, profile):
    kwargs_map = _scraper_kwargs(profile)
    results = {}
    for source in sources:
        fn = SCRAPERS.get(source)
        if not fn:
            continue
        _push(_scrape_state, {"type": "source_start", "source": source})
        try:
            jobs = fn(**kwargs_map.get(source, {}))
            count = _save_jobs(jobs)
            results[source] = count
            _push(_scrape_state, {"type": "source_done", "source": source, "count": count})
        except Exception as e:
            results[f"{source}_error"] = str(e)
            _push(_scrape_state, {"type": "source_error", "source": source, "error": str(e)})
    results["scraped_at"] = timezone.now().isoformat()
    _push(_scrape_state, {"type": "complete", **results})
    with _lock:
        _scrape_state["running"] = False


def _run_rescore_bg(profile):
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
            _push(_rescore_state, {"processed": i, "total": total, "updated": updated})
    _push(_rescore_state, {"type": "complete", "updated": updated})
    with _lock:
        _rescore_state["running"] = False


def _event_stream(state):
    """Replays all past events then follows new ones until the run completes."""
    cursor = 0
    while True:
        with _lock:
            events = list(state["events"])
            running = state["running"]
        for event in events[cursor:]:
            yield _sse(event)
        cursor = len(events)
        if not running:
            break
        _time.sleep(0.3)


class ScrapeView(APIView):
    def post(self, request):
        sources = request.data.get("sources", list(SCRAPERS.keys()))
        with _lock:
            already = _scrape_state["running"]
            if not already:
                _scrape_state["running"] = True
                _scrape_state["events"] = []
                _scrape_state["started_at"] = timezone.now().isoformat()
        if not already:
            profile = UserProfile.get()
            threading.Thread(target=_run_scrape_bg, args=(sources, profile), daemon=True).start()
        return Response({"started_at": _scrape_state["started_at"]})


class ScrapeEventsView(APIView):
    def get(self, request):
        return StreamingHttpResponse(_event_stream(_scrape_state), content_type="text/event-stream")


class ScrapeStatusView(APIView):
    def get(self, request):
        with _lock:
            return Response({
                "running": _scrape_state["running"],
                "events": list(_scrape_state["events"]),
                "started_at": _scrape_state["started_at"],
            })


class RescoreView(APIView):
    def post(self, request):
        profile = UserProfile.get()
        if not profile.competencies and not profile.tech_stack:
            return Response({"error": "Profile is empty."}, status=status.HTTP_400_BAD_REQUEST)
        with _lock:
            already = _rescore_state["running"]
            if not already:
                _rescore_state["running"] = True
                _rescore_state["events"] = []
                _rescore_state["started_at"] = timezone.now().isoformat()
        if not already:
            threading.Thread(target=_run_rescore_bg, args=(profile,), daemon=True).start()
        return Response({"started_at": _rescore_state["started_at"]})


class RescoreEventsView(APIView):
    def get(self, request):
        return StreamingHttpResponse(_event_stream(_rescore_state), content_type="text/event-stream")


class RescoreStatusView(APIView):
    def get(self, request):
        with _lock:
            return Response({
                "running": _rescore_state["running"],
                "events": list(_rescore_state["events"]),
                "started_at": _rescore_state["started_at"],
            })
