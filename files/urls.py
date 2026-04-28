from django.urls import path

from . import views

app_name = "files"

urlpatterns = [
    path("<slug:slug>.<str:ext>", views.serve_file, name="serve"),
]
