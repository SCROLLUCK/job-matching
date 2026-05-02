from django.urls import path
from .views import JobListView, JobStatusView, JobStatsView

urlpatterns = [
    path("", JobListView.as_view(), name="job-list"),
    path("stats/", JobStatsView.as_view(), name="job-stats"),
    path("<int:pk>/status/", JobStatusView.as_view(), name="job-status"),
]
