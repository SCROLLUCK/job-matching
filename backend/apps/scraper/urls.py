from django.urls import path
from .views import ScrapeView, RescoreView

urlpatterns = [
    path("run/", ScrapeView.as_view(), name="scrape-run"),
    path("rescore/", RescoreView.as_view(), name="rescore-jobs"),
]
