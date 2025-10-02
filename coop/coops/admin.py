from django.contrib import admin
from .models import KonfirmasiMagang
from .models import WeeklyReport
from django.core.mail import send_mail
from django.conf import settings


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


def notify_kaprodi_mentor(modeladmin, request, queryset):
    # Simple notification stub — in production you would look up kaprodi/mentor
    # emails from settings or related models. We'll send to settings.DEFAULT_FROM_EMAIL
    subject = 'Notifikasi: Mahasiswa belum mendapat tempat magang / laporan mingguan'
    message = 'Mohon ditindaklanjuti: beberapa mahasiswa belum mengonfirmasi magang atau terlambat mengumpulkan laporan.'
    recipient = [settings.DEFAULT_FROM_EMAIL]
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient)
    modeladmin.message_user(request, 'Notifikasi dikirim ke kaprodi/mentor (stub).')


KonfirmasiMagangAdmin.actions = [notify_kaprodi_mentor]