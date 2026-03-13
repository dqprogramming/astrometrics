from django.urls import path

from . import views

app_name = "manager"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
]
