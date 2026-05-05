from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import UserProfile
from .serializers import UserProfileSerializer
from apps.jobs.models import Job
from apps.jobs.ranker import rescore_from_breakdown
from .autofill import extract_profile_data


class UserProfileView(APIView):
    def get(self, request):
        profile = UserProfile.get()
        return Response(UserProfileSerializer(profile).data)

    def put(self, request):
        profile = UserProfile.get()
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            profile.refresh_from_db()
            _apply_weights(profile)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AutofillView(APIView):
    def post(self, request):
        url = request.data.get("url", "").strip()
        if not url or "linkedin.com/in/" not in url:
            return Response({"error": "Provide a valid LinkedIn profile URL."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data = extract_profile_data(url)
            return Response(data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)


def _apply_weights(profile):
    weights = profile.get_weights()
    jobs = Job.objects.exclude(score_breakdown={})
    updated = []
    for job in jobs:
        new_score = rescore_from_breakdown(job.score_breakdown, weights)
        job.score = new_score
        updated.append(job)
    if updated:
        Job.objects.bulk_update(updated, ["score"])
