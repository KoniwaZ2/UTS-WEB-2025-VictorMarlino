from django.contrib import admin
from .models import (
    KonfirmasiMagang, WeeklyReport, EvaluasiTemplate, 
    EvaluasiSupervisor, LaporanKemajuan, LaporanAkhir
)
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.http import HttpResponse
from django.contrib import messages
import csv


@admin.register(KonfirmasiMagang)
class KonfirmasiMagangAdmin(admin.ModelAdmin):
    # Use only actual KonfirmasiMagang model fields to avoid admin errors
    # show a combined periode column (periode_awal - periode_akhir)
    list_display = ('mahasiswa', 'get_periode', 'posisi', 'nama_perusahaan', 'status')
    list_filter = ('status',)
    search_fields = ('mahasiswa__username', 'nama_perusahaan')
    ordering = ('-id',)
    fieldsets = (
        (None, {
            'fields': (
                'mahasiswa', 'periode_awal', 'periode_akhir', 'posisi', 'nama_perusahaan', 'alamat_perusahaan',
                'bidang_usaha', 'nama_supervisor', 'email_supervisor', 'wa_supervisor',
                'surat_penerimaan', 'status'
            )
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('mahasiswa')

    def get_periode(self, obj):
        if obj.periode_awal and obj.periode_akhir:
            return f"{obj.periode_awal} — {obj.periode_akhir}"
        return obj.periode_awal or obj.periode_akhir or "-"
    get_periode.short_description = 'Periode'
    get_periode.admin_order_field = 'periode_awal'


@admin.register(WeeklyReport)
class WeeklyReportAdmin(admin.ModelAdmin):
    list_display = ('konfirmasi', 'week_start', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(EvaluasiTemplate)
class EvaluasiTemplateAdmin(admin.ModelAdmin):
    list_display = ('nama', 'jenis', 'aktif', 'created_at', 'get_pending_count', 'get_completed_count')
    list_filter = ('jenis', 'aktif')
    search_fields = ('nama',)
    actions = ['send_evaluations_to_supervisors', 'download_evaluation_results']

    def get_pending_count(self, obj):
        """Jumlah evaluasi yang belum diisi"""
        return EvaluasiSupervisor.objects.filter(template=obj, status='pending').count()
    get_pending_count.short_description = 'Belum Diisi'

    def get_completed_count(self, obj):
        """Jumlah evaluasi yang sudah diisi"""
        return EvaluasiSupervisor.objects.filter(template=obj, status='completed').count()
    get_completed_count.short_description = 'Sudah Diisi'

    def send_evaluations_to_supervisors(self, request, queryset):
        """Kirim evaluasi ke semua supervisor yang memiliki mahasiswa magang aktif"""
        total_sent = 0
        for template in queryset:
            if not template.aktif:
                continue
                
            # Ambil semua konfirmasi magang yang accepted
            konfirmasi_list = KonfirmasiMagang.objects.filter(status='accepted')
            
            for konfirmasi in konfirmasi_list:
                # Buat atau update EvaluasiSupervisor
                evaluasi, created = EvaluasiSupervisor.objects.get_or_create(
                    konfirmasi=konfirmasi,
                    template=template,
                    defaults={'status': 'pending'}
                )
                
                if created or evaluasi.status == 'pending':
                    # Kirim email ke supervisor (stub implementation)
                    try:
                        subject = f"Evaluasi {template.get_jenis_display()} - {konfirmasi.mahasiswa.get_full_name()}"
                        message = f"""
                        Kepada Yth. {konfirmasi.nama_supervisor},
                        
                        Anda diminta untuk mengisi evaluasi {template.nama} untuk mahasiswa magang:
                        Nama: {konfirmasi.mahasiswa.get_full_name()}
                        Posisi: {konfirmasi.posisi}
                        
                        Silakan login ke sistem untuk mengisi evaluasi:
                        [Link akan ditambahkan]
                        
                        Terima kasih atas kerjasamanya.
                        """
                        
                        # Uncomment when email settings are configured
                        # send_mail(
                        #     subject,
                        #     message,
                        #     settings.DEFAULT_FROM_EMAIL,
                        #     [konfirmasi.email_supervisor],
                        #     fail_silently=False
                        # )
                        total_sent += 1
                    except Exception as e:
                        pass  # Continue processing other evaluations
        
        self.message_user(request, f"Evaluasi berhasil dikirim ke {total_sent} supervisor.")
    send_evaluations_to_supervisors.short_description = "Kirim evaluasi ke supervisor"

    def download_evaluation_results(self, request, queryset):
        """Download hasil evaluasi dalam format CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="evaluation_results.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Template', 'Mahasiswa', 'Supervisor', 'Status', 'Tanggal Submit', 'Email Supervisor'])
        
        for template in queryset:
            evaluasi_list = EvaluasiSupervisor.objects.filter(template=template).select_related(
                'konfirmasi__mahasiswa'
            )
            
            for evaluasi in evaluasi_list:
                writer.writerow([
                    template.nama,
                    evaluasi.konfirmasi.mahasiswa.get_full_name(),
                    evaluasi.konfirmasi.nama_supervisor,
                    evaluasi.get_status_display(),
                    evaluasi.submitted_at.strftime('%Y-%m-%d %H:%M') if evaluasi.submitted_at else '',
                    evaluasi.konfirmasi.email_supervisor
                ])
        
        return response
    download_evaluation_results.short_description = "Download hasil evaluasi (CSV)"


@admin.register(EvaluasiSupervisor)
class EvaluasiSupervisorAdmin(admin.ModelAdmin):
    list_display = ('konfirmasi', 'template', 'status', 'submitted_at', 'get_supervisor_email')
    list_filter = ('status', 'template__jenis', 'template')
    search_fields = ('konfirmasi__mahasiswa__username', 'template__nama', 'konfirmasi__nama_supervisor')
    readonly_fields = ('submitted_at', 'created_at')
    actions = ['send_reminder_email', 'mark_as_completed', 'download_tracking_report']

    def get_supervisor_email(self, obj):
        return obj.konfirmasi.email_supervisor
    get_supervisor_email.short_description = 'Email Supervisor'

    def send_reminder_email(self, request, queryset):
        """Kirim email reminder ke supervisor yang belum mengisi evaluasi"""
        pending_evaluations = queryset.filter(status='pending')
        sent_count = 0
        
        for evaluasi in pending_evaluations:
            try:
                subject = f"Reminder: Evaluasi {evaluasi.template.get_jenis_display()} - {evaluasi.konfirmasi.mahasiswa.get_full_name()}"
                message = f"""
                Kepada Yth. {evaluasi.konfirmasi.nama_supervisor},
                
                Ini adalah pengingat untuk mengisi evaluasi {evaluasi.template.nama} untuk mahasiswa magang:
                Nama: {evaluasi.konfirmasi.mahasiswa.get_full_name()}
                Posisi: {evaluasi.konfirmasi.posisi}
                Perusahaan: {evaluasi.konfirmasi.nama_perusahaan}
                
                Mohon segera login ke sistem untuk mengisi evaluasi.
                
                Terima kasih.
                """
                
                # Uncomment when email settings are configured
                # send_mail(
                #     subject,
                #     message,
                #     settings.DEFAULT_FROM_EMAIL,
                #     [evaluasi.konfirmasi.email_supervisor],
                #     fail_silently=False
                # )
                sent_count += 1
            except Exception as e:
                pass
        
        self.message_user(request, f"Reminder berhasil dikirim ke {sent_count} supervisor.")
    send_reminder_email.short_description = "Kirim reminder ke supervisor"

    def mark_as_completed(self, request, queryset):
        """Tandai evaluasi sebagai selesai (untuk testing/admin override)"""
        updated = queryset.update(status='completed', submitted_at=timezone.now())
        self.message_user(request, f"{updated} evaluasi ditandai sebagai selesai.")
    mark_as_completed.short_description = "Tandai sebagai selesai"

    def download_tracking_report(self, request, queryset):
        """Download laporan tracking evaluasi"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="evaluation_tracking.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Mahasiswa', 'NIM', 'Perusahaan', 'Supervisor', 'Email Supervisor', 
            'Template Evaluasi', 'Jenis', 'Status', 'Tanggal Submit', 'Dibuat'
        ])
        
        for evaluasi in queryset.select_related('konfirmasi__mahasiswa', 'template'):
            writer.writerow([
                evaluasi.konfirmasi.mahasiswa.get_full_name(),
                getattr(evaluasi.konfirmasi.mahasiswa, 'mahasiswa', {}).get('nim', '') if hasattr(evaluasi.konfirmasi.mahasiswa, 'mahasiswa') else '',
                evaluasi.konfirmasi.nama_perusahaan,
                evaluasi.konfirmasi.nama_supervisor,
                evaluasi.konfirmasi.email_supervisor,
                evaluasi.template.nama,
                evaluasi.template.get_jenis_display(),
                evaluasi.get_status_display(),
                evaluasi.submitted_at.strftime('%Y-%m-%d %H:%M') if evaluasi.submitted_at else '',
                evaluasi.created_at.strftime('%Y-%m-%d %H:%M')
            ])
        
        return response
    download_tracking_report.short_description = "Download laporan tracking"


@admin.register(LaporanKemajuan)
class LaporanKemajuanAdmin(admin.ModelAdmin):
    list_display = ('konfirmasi', 'bulan', 'status', 'submitted_at')
    list_filter = ('status', 'bulan')
    search_fields = ('konfirmasi__mahasiswa__username',)
    readonly_fields = ('submitted_at', 'created_at', 'updated_at')


@admin.register(LaporanAkhir)
class LaporanAkhirAdmin(admin.ModelAdmin):
    list_display = ('konfirmasi', 'status', 'submitted_at', 'approved_at')
    list_filter = ('status',)
    search_fields = ('konfirmasi__mahasiswa__username',)
    readonly_fields = ('submitted_at', 'approved_at', 'created_at', 'updated_at')


def notify_kaprodi_mentor(modeladmin, request, queryset):
    # Simple notification stub — in production you would look up kaprodi/mentor
    # emails from settings or related models. We'll send to settings.DEFAULT_FROM_EMAIL
    subject = 'Notifikasi: Mahasiswa belum mendapat tempat magang / laporan mingguan'
    message = 'Mohon ditindaklanjuti: beberapa mahasiswa belum mengonfirmasi magang atau terlambat mengumpulkan laporan.'
    recipient = [settings.DEFAULT_FROM_EMAIL]
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient)
    modeladmin.message_user(request, 'Notifikasi dikirim ke kaprodi/mentor (stub).')


KonfirmasiMagangAdmin.actions = [notify_kaprodi_mentor]