from django.urls import path
from . import views

app_name = "coops"

urlpatterns = [
    path("", views.mahasiswa_dashboard, name="mahasiswa_dashboard"),
    path("konfirmasi/", views.konfirmasi_magang, name="konfirmasi_magang"),
    path("status/", views.status_magang, name="status_magang"),
    path("<int:konfirmasi_id>/weekly-report/", views.submit_weekly_report, name="submit_weekly_report"),
]
