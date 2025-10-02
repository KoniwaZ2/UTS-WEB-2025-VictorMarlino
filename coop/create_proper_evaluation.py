#!/usr/bin/env python
"""Create a proper evaluation with real answers for testing"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coop.settings')
django.setup()

from coops.models import EvaluasiSupervisor, KonfirmasiMagang, EvaluasiTemplate
from django.utils import timezone

# Get a konfirmasi and template
konfirmasi = KonfirmasiMagang.objects.filter(status='accepted').first()
template = EvaluasiTemplate.objects.filter(aktif=True).first()

if konfirmasi and template:
    # Create or update evaluation with proper answers
    evaluation, created = EvaluasiSupervisor.objects.get_or_create(
        konfirmasi=konfirmasi,
        template=template,
        defaults={'status': 'pending'}
    )
    
    # Set proper answers matching the question indices
    proper_answers = {
        '0': 'Kemampuan teknis mahasiswa sangat baik, menguasai teknologi yang digunakan dengan cepat.',
        '1': 'Komunikasi dengan tim sangat lancar, aktif dalam diskusi dan memberikan ide-ide konstruktif.',
        '2': 'Mahasiswa menunjukkan inisiatif yang baik dan kreatif dalam menyelesaikan masalah yang kompleks.',
        '3': 'Kedisiplinan sangat baik, selalu tepat waktu dan bertanggung jawab penuh terhadap tugas.',
        '4': 'Kemampuan kerja tim excellent, mudah beradaptasi dan membantu rekan kerja lainnya.',
        '5': 'Untuk pengembangan ke depan, disarankan untuk lebih memperdalam knowledge di bidang cloud computing dan DevOps.'
    }
    
    evaluation.jawaban = proper_answers
    evaluation.status = 'completed'
    evaluation.submitted_at = timezone.now()
    evaluation.save()
    
    print(f"✅ Created proper evaluation for:")
    print(f"   🎓 Student: {konfirmasi.mahasiswa.get_full_name() or konfirmasi.mahasiswa.username}")
    print(f"   👨‍💼 Supervisor: {konfirmasi.nama_supervisor}")
    print(f"   📋 Template: {template.nama}")
    print(f"   💾 Answers: {len(proper_answers)} questions answered")
    
    print(f"\n🔗 View results at: /coops/evaluasi/hasil/{konfirmasi.id}/{template.id}/")
else:
    print("❌ Missing konfirmasi or template data")