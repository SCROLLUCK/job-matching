from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q, F
from .models import Job
from .serializers import JobSerializer


class JobStatsView(APIView):
    def get(self, request):
        jobs = list(Job.objects.values("experience_level", "tech_stack", "salary_min"))

        # By level
        level_data: dict = {}
        for job in jobs:
            level = job["experience_level"] or "unknown"
            entry = level_data.setdefault(level, {"count": 0, "salaries": []})
            entry["count"] += 1
            if job["salary_min"]:
                entry["salaries"].append(job["salary_min"])

        order = ["junior", "mid", "senior", "unknown"]
        by_level = sorted(
            [
                {
                    "level": level,
                    "count": d["count"],
                    "avg_salary": round(sum(d["salaries"]) / len(d["salaries"])) if d["salaries"] else None,
                }
                for level, d in level_data.items()
            ],
            key=lambda x: order.index(x["level"]) if x["level"] in order else 99,
        )

        # By stack (optionally filtered by level)
        level_param = request.query_params.get("level", "")
        level_filter = [l for l in level_param.split(",") if l]
        stack_jobs = [j for j in jobs if j["experience_level"] in level_filter] if level_filter else jobs
        stack_data: dict = {}
        for job in stack_jobs:
            for tech in job["tech_stack"]:
                entry = stack_data.setdefault(tech.lower(), {"count": 0, "salaries": []})
                entry["count"] += 1
                if job["salary_min"]:
                    entry["salaries"].append(job["salary_min"])

        by_stack = sorted(
            [
                {
                    "tech": tech,
                    "count": d["count"],
                    "avg_salary": round(sum(d["salaries"]) / len(d["salaries"])) if d["salaries"] else None,
                }
                for tech, d in stack_data.items()
            ],
            key=lambda x: x["count"],
            reverse=True,
        )

        return Response({"by_level": by_level, "by_stack": by_stack})


class JobListView(APIView):
    def get(self, request):
        qs = Job.objects.all()

        source = request.query_params.get("source")
        if source:
            qs = qs.filter(source=source)

        contract_type = request.query_params.get("contract_type")
        if contract_type:
            qs = qs.filter(contract_type=contract_type)

        work_mode = request.query_params.get("work_mode")
        if work_mode:
            qs = qs.filter(work_mode=work_mode)

        experience_level = request.query_params.get("experience_level")
        if experience_level:
            qs = qs.filter(experience_level=experience_level)

        min_score = request.query_params.get("min_score")
        if min_score:
            qs = qs.filter(score__gte=float(min_score))

        salary_min = request.query_params.get("salary_min")
        if salary_min:
            qs = qs.filter(salary_max__gte=int(salary_min))

        salary_max = request.query_params.get("salary_max")
        if salary_max:
            qs = qs.filter(salary_min__lte=int(salary_max))

        application_status = request.query_params.get("application_status")
        if application_status is not None:
            qs = qs.filter(application_status=application_status)

        search = request.query_params.get("search")
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search) | Q(company__icontains=search))

        sort = request.query_params.get("sort", "score")
        if sort == "score":
            qs = qs.order_by(F("score").desc(nulls_last=True), "-scraped_at")
        elif sort == "date":
            qs = qs.order_by(F("posted_at").desc(nulls_last=True), "-scraped_at")
        elif sort == "salary":
            qs = qs.order_by(F("salary_max").desc(nulls_last=True), "-scraped_at")
        else:
            qs = qs.order_by("-scraped_at")

        return Response(JobSerializer(qs, many=True).data)


class JobStatusView(APIView):
    VALID = {"", "applied", "rejected"}

    def post(self, request, pk):
        try:
            job = Job.objects.get(pk=pk)
        except Job.DoesNotExist:
            return Response(status=404)
        new_status = request.data.get("status", "")
        if new_status not in self.VALID:
            return Response({"error": "Invalid status"}, status=400)
        job.application_status = new_status
        job.save(update_fields=["application_status"])
        return Response({"application_status": job.application_status})
