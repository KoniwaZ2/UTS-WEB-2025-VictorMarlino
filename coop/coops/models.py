from django.db import models
from accounts.models import User

class KonfirmasiMagang(models.Model):
    mahasiswa = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': 'mahasiswa'})
    periode_awal = models.DateField(default=None, null=True, blank=True)
    periode_akhir = models.DateField(default=None, null=True, blank=True)
    posisi = models.CharField(max_length=200)
    nama_perusahaan = models.CharField(max_length=200)
    alamat_perusahaan = models.TextField()
    bidang_usaha = models.CharField(max_length=200)
    nama_supervisor = models.CharField(max_length=200)
    email_supervisor = models.EmailField()
    wa_supervisor = models.CharField(max_length=20, blank=True, null=True)
    surat_penerimaan = models.FileField(upload_to='surat_magang/')

    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ], default='pending')

    # optional deadline for when the student must have secured a placement
    deadline = models.DateField(null=True, blank=True)

    # whether this mahasiswa is required to submit weekly reports
    requires_weekly_report = models.BooleanField(default=False)

    # last time a reminder email was sent
    last_reminder_sent = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.mahasiswa.username} - {self.nama_perusahaan}"


class WeeklyReport(models.Model):
    konfirmasi = models.ForeignKey(KonfirmasiMagang, on_delete=models.CASCADE, related_name='weekly_reports')
    week_start = models.DateField()
    report_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report {self.konfirmasi.mahasiswa.username} ({self.week_start})"
