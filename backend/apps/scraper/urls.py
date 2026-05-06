from django.urls import path
from .views import (
    ScrapeView, ScrapeEventsView, ScrapeStatusView,
    RescoreView, RescoreEventsView, RescoreStatusView,
)

urlpatterns = [
    path("run/", ScrapeView.as_view(), name="scrape-run"),
    path("events/", ScrapeEventsView.as_view(), name="scrape-events"),
    path("status/", ScrapeStatusView.as_view(), name="scrape-status"),
    path("rescore/", RescoreView.as_view(), name="rescore-jobs"),
    path("rescore/events/", RescoreEventsView.as_view(), name="rescore-events"),
    path("rescore/status/", RescoreStatusView.as_view(), name="rescore-status"),
]
