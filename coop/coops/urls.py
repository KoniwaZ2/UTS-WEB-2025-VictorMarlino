from django.urls import path
from . import views

app_name = "coops"

urlpatterns = [
    path("", views.mahasiswa_dashboard, name="mahasiswa_dashboard"),
    path("konfirmasi/", views.konfirmasi_magang, name="konfirmasi_magang"),
    path("status/", views.status_magang, name="status_magang"),
    path("<int:konfirmasi_id>/weekly-report/", views.submit_weekly_report, name="submit_weekly_report"),
    path("lowongan/", views.lowongan, name="lowongan"),
    
    # Laporan Kemajuan (UTS)
    path("laporan-kemajuan/", views.laporan_kemajuan, name="laporan_kemajuan"),
    path("laporan-kemajuan/<str:bulan>/", views.laporan_kemajuan, name="laporan_kemajuan_bulan"),
    path("daftar-laporan-kemajuan/", views.daftar_laporan_kemajuan, name="daftar_laporan_kemajuan"),
    
    # Laporan Akhir (UAS)
    path("laporan-akhir/", views.laporan_akhir, name="laporan_akhir"),
    
    # Evaluasi Supervisor
    path("evaluasi/<int:konfirmasi_id>/<int:template_id>/", views.evaluasi_supervisor, name="evaluasi_supervisor"),
    path("evaluasi/hasil/<int:konfirmasi_id>/<int:template_id>/", views.hasil_evaluasi, name="hasil_evaluasi"),
    
    # Admin tracking
    path("tracking-evaluasi/", views.tracking_evaluasi, name="tracking_evaluasi"),
]
