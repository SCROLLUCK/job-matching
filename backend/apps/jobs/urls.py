from django.urls import path
from .views import JobListView, JobStatusView

urlpatterns = [
    path("", JobListView.as_view(), name="job-list"),
    path("<int:pk>/status/", JobStatusView.as_view(), name="job-status"),
]
