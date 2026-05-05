from django.urls import path
from .views import UserProfileView, AutofillView

urlpatterns = [
    path("", UserProfileView.as_view(), name="user-profile"),
    path("autofill/", AutofillView.as_view(), name="profile-autofill"),
]
