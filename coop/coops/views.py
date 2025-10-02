from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.decorators import mahasiswa_required
from django.contrib import messages
from .models import KonfirmasiMagang
from django.http import HttpResponse
from django.template import loader
from .forms import WeeklyReportForm
from django.core.mail import send_mail
from django.conf import settings

# Mahasiswa isi konfirmasi magang
@login_required
def konfirmasi_magang(request):
    if request.user.role != "mahasiswa":
        return redirect("/")  # hanya mahasiswa

    if request.method == "POST":
        # ambil field dari form HTML
        periode_awal = request.POST.get('periode_awal', '').strip()
        periode_akhir = request.POST.get('periode_akhir', '').strip()
        posisi = request.POST.get('posisi', '').strip()
        nama_perusahaan = request.POST.get('nama_perusahaan', '').strip()
        alamat_perusahaan = request.POST.get('alamat_perusahaan', '').strip()
        bidang_usaha = request.POST.get('bidang_usaha', '').strip()
        nama_supervisor = request.POST.get('nama_supervisor', '').strip()
        email_supervisor = request.POST.get('email_supervisor', '').strip()
        wa_supervisor = request.POST.get('wa_supervisor', '').strip()

        # file
        surat = request.FILES.get('surat_penerimaan')  # name input file

        # validasi sederhana
        errors = []
        if not periode_awal or not periode_akhir:
            errors.append("Periode harus diisi.")
        if not posisi:
            errors.append("Posisi harus diisi.")
        if not nama_perusahaan:
            errors.append("Nama perusahaan harus diisi.")
        # ... tambah validasi lain sesuai kebutuhan

        # contoh validasi file (opsional)
        if surat:
            # batasi tipe dan ukuran (contoh)
            if surat.size > 5 * 1024 * 1024:  # 5 MB
                errors.append("File terlalu besar (maks 5MB).")
            if not surat.content_type in ("application/pdf", "image/jpeg", "image/png"):
                errors.append("Format file harus PDF/JPEG/PNG.")

        if errors:
            for e in errors:
                messages.error(request, e)
            # kembalikan ke form, Anda mungkin ingin menyimpan field agar tetap tampil
            return render(request, "coops/konfirmasi_magang.html", {"form_values": request.POST})

        # simpan ke model
        # Jika sudah ada KonfirmasiMagang untuk user ini, update record
        km = KonfirmasiMagang.objects.filter(mahasiswa=request.user).first()
        if km:
            # update existing
            km.periode_awal = periode_awal
            km.periode_akhir = periode_akhir
            km.posisi = posisi
            km.nama_perusahaan = nama_perusahaan
            km.alamat_perusahaan = alamat_perusahaan
            km.bidang_usaha = bidang_usaha
            km.nama_supervisor = nama_supervisor
            km.email_supervisor = email_supervisor
            km.wa_supervisor = wa_supervisor
            if surat:
                km.surat_penerimaan = surat
            # keep current status (or reset to pending) — choose pending for re-submission
            km.status = 'pending'
            km.save()
            messages.success(request, "Konfirmasi magang berhasil diperbarui.")
        else:
            # create new
            km = KonfirmasiMagang()
            km.mahasiswa = request.user  # pastikan request.user adalah Mahasiswa terkait
            km.periode_awal = periode_awal
            km.periode_akhir = periode_akhir
            km.posisi = posisi
            km.nama_perusahaan = nama_perusahaan
            km.alamat_perusahaan = alamat_perusahaan
            km.bidang_usaha = bidang_usaha
            km.nama_supervisor = nama_supervisor
            km.email_supervisor = email_supervisor
            km.wa_supervisor = wa_supervisor
            if surat:
                km.surat_penerimaan = surat  # field FileField di model
            km.status = 'pending'  # contoh default status
            km.save()
            messages.success(request, "Konfirmasi magang berhasil dikirim.")

        # set Mahasiswa.magang flag if Mahasiswa record exists
        try:
            m = request.user.mahasiswa
            m.magang = True
            m.save()
        except Exception:
            pass

        # redirect to mahasiswa dashboard
        return redirect('coops:mahasiswa_dashboard')
    # method GET
    return render(request, "coops/konfirmasi_magang.html")

# Admin lihat status magang semua mahasiswa
@login_required
def status_magang(request):
    if request.user.role != "admin":
        return redirect("/")  # hanya admin

    # Tampilkan semua mahasiswa beserta konfirmasi magang jika ada
    from accounts.models import Mahasiswa

    mahasiswa_qs = Mahasiswa.objects.select_related('nama').all()
    # Bangun list of tuples: (mahasiswa, magang_or_none)
    mahasiswa_list = []
    for m in mahasiswa_qs:
        magang = KonfirmasiMagang.objects.filter(mahasiswa=m.nama).first()
        mahasiswa_list.append((m, magang))

    template = loader.get_template("coops/status_magang.html")
    return HttpResponse(template.render({"mahasiswa_list": mahasiswa_list}))


@login_required
def submit_weekly_report(request, konfirmasi_id):
    try:
        konfirmasi = KonfirmasiMagang.objects.get(id=konfirmasi_id)
    except KonfirmasiMagang.DoesNotExist:
        return redirect('coops:mahasiswa_dashboard')

    if request.method == 'POST':
        form = WeeklyReportForm(request.POST)
        if form.is_valid():
            wr = form.save(commit=False)
            wr.konfirmasi = konfirmasi
            wr.save()
            messages.success(request, 'Laporan mingguan berhasil disimpan.')
            return redirect('coops:mahasiswa_dashboard')
    else:
        form = WeeklyReportForm()

    return render(request, 'coops/submit_weekly_report.html', {'form': form, 'konfirmasi': konfirmasi})

@mahasiswa_required
def mahasiswa_dashboard(request):
    # Safely obtain related Mahasiswa and KonfirmasiMagang objects and pass
    # them into the template to avoid template attribute-lookup errors.
    mahasiswa_obj = None
    magang_obj = None

    try:
        mahasiswa_obj = request.user.mahasiswa
    except Exception:
        mahasiswa_obj = None

    if mahasiswa_obj:
        # KonfirmasiMagang.mahasiswa is a OneToOneField to User, so query by
        # request.user (not Mahasiswa). Use .filter().first() to avoid
        # DoesNotExist exceptions.
        magang_obj = KonfirmasiMagang.objects.filter(w=request.user).first()

    return render(request, "coops/mahasiswa_dashboard.html", {"mahasiswa": mahasiswa_obj, "magang": magang_obj})
