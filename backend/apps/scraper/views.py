from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from apps.jobs.models import Job
from apps.jobs.ranker import score_job
from apps.profile.models import UserProfile
from . import nerdin, linkedin, geekhunter


def _save_jobs(job_list):
    profile = UserProfile.get()
    created_count = 0

    for data in job_list:
        if not data.get("url") or not data.get("title"):
            continue

        exists = Job.objects.filter(external_id=data["external_id"], source=data["source"]).exists()
        if exists:
            continue

        score_result = score_job(data, profile)
        score = score_result.get("score")
        breakdown = score_result.get("breakdown", {})
        if score_result.get("summary"):
            breakdown["summary"] = score_result["summary"]

        Job.objects.create(
            external_id=data["external_id"],
            title=data["title"],
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
            score=score,
            score_breakdown=breakdown,
        )
        created_count += 1

    return created_count


class ScrapeView(APIView):
    def post(self, request):
        sources = request.data.get("sources", ["linkedin", "nerdin", "geekhunter"])
        results = {}

        if "nerdin" in sources:
            try:
                jobs = nerdin.fetch_jobs(pages=3)
                results["nerdin"] = _save_jobs(jobs)
            except Exception as e:
                results["nerdin_error"] = str(e)

        if "linkedin" in sources:
            try:
                jobs = linkedin.fetch_jobs(pages=3)
                results["linkedin"] = _save_jobs(jobs)
            except Exception as e:
                results["linkedin_error"] = str(e)

        if "geekhunter" in sources:
            try:
                jobs = geekhunter.fetch_jobs(pages=2)
                results["geekhunter"] = _save_jobs(jobs)
            except Exception as e:
                results["geekhunter_error"] = str(e)

        results["scraped_at"] = timezone.now().isoformat()
        return Response(results)


class RescoreView(APIView):
    """Re-score all jobs using the current profile. Useful after updating the profile."""
    def post(self, request):
        profile = UserProfile.get()
        if not profile.competencies and not profile.tech_stack:
            return Response({"error": "Profile is empty. Add competencies or tech stack first."}, status=status.HTTP_400_BAD_REQUEST)

        jobs = Job.objects.all()
        updated = 0
        for job in jobs:
            data = {
                "title": job.title,
                "company": job.company,
                "description": job.description,
                "tech_stack": job.tech_stack,
                "salary_min": job.salary_min,
                "salary_max": job.salary_max,
                "contract_type": job.contract_type,
                "work_mode": job.work_mode,
            }
            result = score_job(data, profile)
            if result:
                breakdown = result.get("breakdown", {})
                if result.get("summary"):
                    breakdown["summary"] = result["summary"]
                job.score = result.get("score")
                job.score_breakdown = breakdown
                job.save(update_fields=["score", "score_breakdown"])
                updated += 1

        return Response({"updated": updated})
