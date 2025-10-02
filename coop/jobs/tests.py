from django.urls import path
from . import views

app_name = "jobs"

urlpatterns = [
    path("supervisor_dashboard/", views.supervisor_dashboard, name="supervisor_dashboard"),
]