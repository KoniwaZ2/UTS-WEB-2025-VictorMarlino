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
        ('completed', 'Completed'),
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


class EvaluasiTemplate(models.Model):
    """Template evaluasi yang dibuat oleh admin untuk UTS/UAS"""
    nama = models.CharField(max_length=200)
    jenis = models.CharField(max_length=20, choices=[
        ('uts', 'UTS - Laporan Kemajuan'),
        ('uas', 'UAS - Laporan Akhir'),
    ])
    pertanyaan = models.JSONField(help_text="Array of questions for the evaluation")
    aktif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nama} ({self.get_jenis_display()})"


class EvaluasiSupervisor(models.Model):
    """Evaluasi yang diisi oleh supervisor"""
    konfirmasi = models.ForeignKey(KonfirmasiMagang, on_delete=models.CASCADE)
    template = models.ForeignKey(EvaluasiTemplate, on_delete=models.CASCADE)
    jawaban = models.JSONField(help_text="Answers corresponding to template questions", default=dict, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Belum Diisi'),
        ('completed', 'Sudah Diisi'),
    ], default='pending')
    submitted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['konfirmasi', 'template']

    def __str__(self):
        return f"Evaluasi {self.template.nama} - {self.konfirmasi.mahasiswa.username}"


class LaporanKemajuan(models.Model):
    """Laporan kemajuan bulanan yang diisi mahasiswa"""
    konfirmasi = models.ForeignKey(KonfirmasiMagang, on_delete=models.CASCADE, related_name='laporan_kemajuan')
    bulan = models.DateField()
    
    # Informasi yang diminta dalam requirement
    profil_perusahaan = models.TextField(help_text="Profil perusahaan")
    jobdesk = models.TextField(help_text="Jobdesk yang dikerjakan")
    suasana_lingkungan = models.TextField(help_text="Suasana lingkungan pekerjaan")
    manfaat_perkuliahan = models.TextField(help_text="Apa yang didapatkan dari perkuliahan yang berguna untuk pekerjaan")
    kebutuhan_pembelajaran = models.TextField(help_text="Apa yang berguna pada perusahaan tapi belum didapatkan dalam pembelajaran")
    
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('reviewed', 'Reviewed'),
    ], default='draft')
    
    submitted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['konfirmasi', 'bulan']

    def __str__(self):
        return f"Laporan {self.bulan.strftime('%B %Y')} - {self.konfirmasi.mahasiswa.username}"


class LaporanAkhir(models.Model):
    """Laporan akhir yang dikumpulkan mahasiswa di akhir magang"""
    konfirmasi = models.OneToOneField(KonfirmasiMagang, on_delete=models.CASCADE, related_name='laporan_akhir')
    
    # Konten laporan akhir
    ringkasan_kegiatan = models.TextField(help_text="Ringkasan kegiatan selama magang")
    pencapaian = models.TextField(help_text="Pencapaian dan hasil yang diperoleh")
    kendala_solusi = models.TextField(help_text="Kendala yang dihadapi dan solusinya")
    saran_perusahaan = models.TextField(help_text="Saran untuk perusahaan")
    saran_kampus = models.TextField(help_text="Saran untuk kampus")
    
    # File laporan
    file_laporan = models.FileField(upload_to='laporan_akhir/', null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
    ], default='draft')
    
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Laporan Akhir - {self.konfirmasi.mahasiswa.username}"
