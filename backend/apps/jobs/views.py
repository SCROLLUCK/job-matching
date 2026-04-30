from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from .models import Job
from .serializers import JobSerializer


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

        search = request.query_params.get("search")
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search) | Q(company__icontains=search))

        sort = request.query_params.get("sort", "score")
        sort_map = {
            "score": "-score",
            "date": "-posted_at",
            "salary": "-salary_max",
            "scraped": "-scraped_at",
        }
        qs = qs.order_by(sort_map.get(sort, "-score"), "-scraped_at")

        return Response(JobSerializer(qs, many=True).data)
