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
from django.utils import timezone
from datetime import date, timedelta


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

    mahasiswa_qs = Mahasiswa.objects.select_related('email').all()
    # Bangun list of tuples: (mahasiswa, magang_or_none)
    mahasiswa_list = []
    for m in mahasiswa_qs:
        magang = KonfirmasiMagang.objects.filter(mahasiswa=m.email).first()
        mahasiswa_list.append((m, magang))

    # Calculate statistics
    all_konfirmasi = KonfirmasiMagang.objects.all()
    accepted_count = all_konfirmasi.filter(status='accepted').count()
    pending_count = all_konfirmasi.filter(status='pending').count()
    rejected_count = all_konfirmasi.filter(status='rejected').count()

    context = {
        'mahasiswa_list': mahasiswa_list,
        'accepted_count': accepted_count,
        'pending_count': pending_count,
        'rejected_count': rejected_count,
    }

    template = loader.get_template("coops/status_magang.html")
    return HttpResponse(template.render(context, request))


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
        magang_obj = KonfirmasiMagang.objects.filter(mahasiswa=request.user).first()

    return render(request, "coops/mahasiswa_dashboard.html", {"mahasiswa": mahasiswa_obj, "magang": magang_obj})


@login_required
def lowongan(request):
    # Render the jobs listing directly so the `lowongan` route under
    # the `coops` app serves the page without redirecting to the jobs app.
    # This keeps the URL `/coops/lowongan/` functional even if the jobs
    # app changes, and avoids an unnecessary HTTP redirect.
    return render(request, "jobs/list_lowongan.html")


@login_required
def tracking_evaluasi(request):
    """View untuk admin melihat tracking evaluasi supervisor"""
    if request.user.role != "admin":
        messages.error(request, "Akses ditolak. Anda bukan admin.")
        return redirect("/")

    from .models import EvaluasiTemplate, EvaluasiSupervisor
    
    tracking_data = []
    
    # Loop through each evaluation template
    for template in EvaluasiTemplate.objects.filter(aktif=True):
        # Get all internships with status accepted or completed
        # Note: "status='accepted' or 'completed'" would evaluate to 'accepted' in Python,
        # so use __in to match multiple values.
        accepted_konfirmasi = KonfirmasiMagang.objects.filter(status__in=['accepted', 'completed'])

        # Get evaluation data for this template
        evaluations = EvaluasiSupervisor.objects.filter(template=template)

        # Calculate statistics
        total_supervisors = accepted_konfirmasi.count()
        completed = evaluations.filter(status='completed').count()
        pending = total_supervisors - completed
        completion_rate = int((completed / total_supervisors) * 100) if total_supervisors > 0 else 0

        # Get detailed supervisor info
        supervisor_details = []
        for konfirmasi in accepted_konfirmasi:
            try:
                evaluation = evaluations.get(konfirmasi=konfirmasi)
                status = evaluation.status
                submitted_date = evaluation.submitted_at
            except EvaluasiSupervisor.DoesNotExist:
                status = 'not_created'
                submitted_date = None

            supervisor_details.append({
                'konfirmasi': konfirmasi,
                'status': status,
                'submitted_date': submitted_date
            })

        tracking_data.append({
            'template': template,
            'total_supervisors': total_supervisors,
            'completed': completed,
            'pending': pending,
            'completion_rate': completion_rate,
            'supervisor_details': supervisor_details
        })
    
    context = {
        'tracking_data': tracking_data
    }
    
    return render(request, 'coops/tracking_evaluasi.html', context)


@login_required
@mahasiswa_required
def laporan_kemajuan(request, bulan=None):
    """View untuk mahasiswa mengisi laporan kemajuan (UTS)"""
    # Cari konfirmasi magang mahasiswa
    try:
        konfirmasi = KonfirmasiMagang.objects.get(mahasiswa=request.user, status='accepted')
    except KonfirmasiMagang.DoesNotExist:
        messages.error(request, 'Anda belum memiliki konfirmasi magang yang diterima.')
        return redirect('coops:mahasiswa_dashboard')
    
    if request.method == 'POST':
        # Ambil data dari form
        from .models import LaporanKemajuan
        from datetime import datetime
        
        # Parse bulan dari form atau gunakan bulan sekarang
        bulan_input = request.POST.get('bulan')
        if bulan_input:
            try:
                # Convert dari format "2025-10" ke date object (hari pertama bulan)
                bulan_laporan = datetime.strptime(bulan_input + '-01', '%Y-%m-%d').date()
            except ValueError:
                bulan_laporan = timezone.now().date().replace(day=1)
        else:
            bulan_laporan = timezone.now().date().replace(day=1)
        
        # Determine action (draft or submit)
        action = request.POST.get('action', 'submit')
        status = 'draft' if action == 'draft' else 'submitted'
        
        # Cek apakah laporan sudah ada untuk mahasiswa dan bulan ini
        existing_laporan = LaporanKemajuan.objects.filter(
            konfirmasi=konfirmasi, 
            bulan=bulan_laporan
        ).first()
        
        try:
            if existing_laporan:
                # Update existing
                existing_laporan.profil_perusahaan = request.POST.get('profil_perusahaan')
                existing_laporan.jobdesk = request.POST.get('jobdesk')
                existing_laporan.suasana_lingkungan = request.POST.get('suasana_lingkungan')
                existing_laporan.manfaat_perkuliahan = request.POST.get('manfaat_perkuliahan')
                existing_laporan.kebutuhan_pembelajaran = request.POST.get('kebutuhan_pembelajaran')
                existing_laporan.status = status
                if status == 'submitted':
                    existing_laporan.submitted_at = timezone.now()
                existing_laporan.save()
                message = 'Laporan kemajuan berhasil diperbarui.'
                if status == 'submitted':
                    message = 'Laporan kemajuan berhasil dikirim.'
                messages.success(request, message)
            else:
                # Create new
                laporan = LaporanKemajuan.objects.create(
                    konfirmasi=konfirmasi,
                    bulan=bulan_laporan,
                    profil_perusahaan=request.POST.get('profil_perusahaan'),
                    jobdesk=request.POST.get('jobdesk'),
                    suasana_lingkungan=request.POST.get('suasana_lingkungan'),
                    manfaat_perkuliahan=request.POST.get('manfaat_perkuliahan'),
                    kebutuhan_pembelajaran=request.POST.get('kebutuhan_pembelajaran'),
                    status=status,
                    submitted_at=timezone.now() if status == 'submitted' else None
                )
                message = 'Laporan kemajuan berhasil disimpan.'
                if status == 'submitted':
                    message = 'Laporan kemajuan berhasil dikirim.'
                messages.success(request, message)
                
            return redirect('coops:mahasiswa_dashboard')
            
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
    
    # GET request - tampilkan form
    from .models import LaporanKemajuan
    from datetime import datetime
    
    # Set default bulan ke bulan sekarang (hari pertama)
    if not bulan:
        bulan_date = timezone.now().date().replace(day=1)
    else:
        try:
            # Parse bulan dari URL parameter jika ada
            bulan_date = datetime.strptime(bulan + '-01', '%Y-%m-%d').date()
        except ValueError:
            bulan_date = timezone.now().date().replace(day=1)
    
    existing_laporan = LaporanKemajuan.objects.filter(
        konfirmasi=konfirmasi,
        bulan=bulan_date
    ).first()
    
    # Generate available months (last 6 months)
    today = timezone.now().date()
    available_months = []
    for i in range(6):
        if i == 0:
            month = today.replace(day=1)
        else:
            # Go back i months
            year = today.year
            month_num = today.month - i
            if month_num <= 0:
                month_num += 12
                year -= 1
            month = date(year, month_num, 1)
        available_months.append(month)
    
    context = {
        'laporan': existing_laporan,
        'bulan': bulan_date,
        'bulan_str': bulan_date.strftime('%Y-%m'),  # For HTML input format
        'bulan_display': bulan_date.strftime('%B %Y'),  # For display
        'konfirmasi': konfirmasi,
        'is_submitted': existing_laporan.status == 'submitted' if existing_laporan else False,
        'available_months': available_months
    }
    
    return render(request, 'coops/laporan_kemajuan_form.html', context)


@login_required  
@mahasiswa_required
def laporan_akhir(request):
    """View untuk mahasiswa mengisi laporan akhir (UAS)"""
    # Cari konfirmasi magang mahasiswa
    try:
        konfirmasi = KonfirmasiMagang.objects.get(mahasiswa=request.user, status='accepted')
    except KonfirmasiMagang.DoesNotExist:
        messages.error(request, 'Anda belum memiliki konfirmasi magang yang diterima.')
        return redirect('coops:mahasiswa_dashboard')
        
    if request.method == 'POST':
        from .models import LaporanAkhir
        
        # Cek apakah laporan sudah ada untuk mahasiswa ini
        existing_laporan = LaporanAkhir.objects.filter(konfirmasi=konfirmasi).first()
        
        try:
            if existing_laporan:
                # Update existing
                existing_laporan.ringkasan_kegiatan = request.POST.get('ringkasan_kegiatan')
                existing_laporan.pencapaian_tujuan = request.POST.get('pencapaian_tujuan')
                existing_laporan.keterampilan_yang_diperoleh = request.POST.get('keterampilan_yang_diperoleh')
                existing_laporan.kesulitan_dan_solusi = request.POST.get('kesulitan_dan_solusi')
                existing_laporan.saran_untuk_program = request.POST.get('saran_untuk_program')
                existing_laporan.refleksi_personal = request.POST.get('refleksi_personal')
                existing_laporan.status = 'submitted'
                existing_laporan.submitted_at = timezone.now()
                existing_laporan.save()
                messages.success(request, 'Laporan akhir berhasil diperbarui.')
            else:
                # Create new
                laporan = LaporanAkhir.objects.create(
                    konfirmasi=konfirmasi,
                    ringkasan_kegiatan=request.POST.get('ringkasan_kegiatan'),
                    pencapaian_tujuan=request.POST.get('pencapaian_tujuan'),
                    keterampilan_yang_diperoleh=request.POST.get('keterampilan_yang_diperoleh'),
                    kesulitan_dan_solusi=request.POST.get('kesulitan_dan_solusi'),
                    saran_untuk_program=request.POST.get('saran_untuk_program'),
                    refleksi_personal=request.POST.get('refleksi_personal'),
                    status='submitted',
                    submitted_at=timezone.now()
                )
                messages.success(request, 'Laporan akhir berhasil disimpan.')
                
            return redirect('coops:mahasiswa_dashboard')
            
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
    
    # GET request - tampilkan form
    from .models import LaporanAkhir
    existing_laporan = LaporanAkhir.objects.filter(konfirmasi=konfirmasi).first()
    
    context = {
        'laporan': existing_laporan,
        'konfirmasi': konfirmasi
    }
    
    return render(request, 'coops/laporan_akhir_form.html', context)


@login_required
def evaluasi_supervisor(request, konfirmasi_id, template_id):
    """View untuk supervisor mengisi evaluasi mahasiswa"""
    from .models import EvaluasiTemplate, EvaluasiSupervisor
    import json
    
    try:
        konfirmasi = KonfirmasiMagang.objects.get(id=konfirmasi_id)
        template = EvaluasiTemplate.objects.get(id=template_id)
    except (KonfirmasiMagang.DoesNotExist, EvaluasiTemplate.DoesNotExist):
        messages.error(request, 'Data tidak ditemukan.')
        return redirect('/')
    
    # Get or create evaluation record
    evaluasi, created = EvaluasiSupervisor.objects.get_or_create(
        konfirmasi=konfirmasi,
        template=template,
        defaults={'status': 'pending'}
    )
    
    if request.method == 'POST':
        try:
            # Collect answers from form
            answers = {}
            for key, value in request.POST.items():
                if key.startswith('question_'):
                    question_id = key.replace('question_', '')
                    answers[question_id] = value
            
            # Save answers and update status
            evaluasi.jawaban = answers
            evaluasi.status = 'completed'
            evaluasi.submitted_at = timezone.now()
            evaluasi.save()
            
            messages.success(request, 'Evaluasi berhasil disimpan. Terima kasih atas partisipasi Anda.')
            return render(request, 'coops/evaluasi_success.html', {
                'konfirmasi': konfirmasi,
                'template': template
            })
            
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
    
    # Parse questions from template
    try:
        questions = json.loads(template.pertanyaan) if template.pertanyaan else []
    except json.JSONDecodeError:
        questions = []
    
    # If evaluation already completed, show read-only view
    if evaluasi.status == 'completed':
        context = {
            'konfirmasi': konfirmasi,
            'template': template,
            'evaluasi': evaluasi,
            'questions': questions,
            'read_only': True
        }
        return render(request, 'coops/evaluasi_readonly.html', context)
    
    context = {
        'konfirmasi': konfirmasi,
        'template': template,
        'evaluasi': evaluasi,
        'questions': questions
    }
    
    return render(request, 'coops/evaluasi_form.html', context)


@login_required
def hasil_evaluasi(request, konfirmasi_id, template_id):
    """View untuk admin melihat hasil evaluasi yang sudah diisi"""
    if request.user.role != "admin":
        messages.error(request, "Akses ditolak. Anda bukan admin.")
        return redirect("/")
    
    from .models import EvaluasiTemplate, EvaluasiSupervisor
    import json
    
    try:
        konfirmasi = KonfirmasiMagang.objects.get(id=konfirmasi_id)
        template = EvaluasiTemplate.objects.get(id=template_id)
        evaluasi = EvaluasiSupervisor.objects.get(konfirmasi=konfirmasi, template=template)
    except (KonfirmasiMagang.DoesNotExist, EvaluasiTemplate.DoesNotExist, EvaluasiSupervisor.DoesNotExist):
        messages.error(request, 'Data evaluasi tidak ditemukan.')
        return redirect('coops:tracking_evaluasi')
    
    # Parse questions from template
    try:
        questions = json.loads(template.pertanyaan) if template.pertanyaan else []
    except json.JSONDecodeError:
        questions = []
    
    # Combine questions with answers
    qa_pairs = []
    for i, question in enumerate(questions):
        # Try to get answer by index first, then by key
        answer = None
        if evaluasi.jawaban:
            # Try numbered key first (standard format)
            answer = evaluasi.jawaban.get(str(i))
            if not answer:
                # Try direct index key
                answer = evaluasi.jawaban.get(i)
            if not answer:
                # If no numbered answers, check if it's a test/demo format
                if len(evaluasi.jawaban) == 1 and 'test' in evaluasi.jawaban:
                    answer = f"[Demo data] {evaluasi.jawaban.get('test', '')}"
                else:
                    # Try to find any answer for this question
                    answer = evaluasi.jawaban.get(f'jawaban_{i}', evaluasi.jawaban.get(f'question_{i}', 'Tidak dijawab'))
        
        if not answer:
            answer = 'Tidak dijawab'
            
        qa_pairs.append({
            'question': question,
            'answer': answer
        })
    
    context = {
        'konfirmasi': konfirmasi,
        'template': template,
        'evaluasi': evaluasi,
        'qa_pairs': qa_pairs
    }
    
    return render(request, 'coops/hasil_evaluasi.html', context)


@login_required
def daftar_laporan_kemajuan(request):
    """View untuk admin melihat daftar semua laporan kemajuan mahasiswa"""
    if request.user.role != "admin":
        messages.error(request, "Akses ditolak. Anda bukan admin.")
        return redirect("/")
        
    from .models import LaporanKemajuan
    from accounts.models import Mahasiswa
    
    # Get all laporan kemajuan with related konfirmasi data
    laporan_list = LaporanKemajuan.objects.select_related('konfirmasi__mahasiswa').order_by('-created_at')
    
    # Get list of mahasiswa who have accepted internships but haven't submitted reports
    submitted_konfirmasi_ids = laporan_list.values_list('konfirmasi_id', flat=True)
    konfirmasi_belum_submit = KonfirmasiMagang.objects.filter(
        status='accepted'
    ).exclude(id__in=submitted_konfirmasi_ids).select_related('mahasiswa')
    
    context = {
        'laporan_list': laporan_list,
        'konfirmasi_belum_submit': konfirmasi_belum_submit,
        'total_mahasiswa_magang': KonfirmasiMagang.objects.filter(status='accepted').count(),
        'total_submitted': laporan_list.count(),
    }
    
    return render(request, 'coops/daftar_laporan_kemajuan.html', context)
