#!/usr/bin/env python
"""Debug the evaluation data to see what's stored"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coop.settings')
django.setup()

from coops.models import EvaluasiSupervisor
import json

evaluation = EvaluasiSupervisor.objects.filter(status='completed').first()
if evaluation:
    print(f"📋 Template: {evaluation.template.nama}")
    print(f"🎓 Student: {evaluation.konfirmasi.mahasiswa.get_full_name() or evaluation.konfirmasi.mahasiswa.username}")
    print(f"👨‍💼 Supervisor: {evaluation.konfirmasi.nama_supervisor}")
    print(f"📅 Submitted: {evaluation.submitted_at}")
    print(f"💾 Jawaban data type: {type(evaluation.jawaban)}")
    print(f"💾 Jawaban content: {evaluation.jawaban}")
    
    # Check template questions
    try:
        questions = json.loads(evaluation.template.pertanyaan) if evaluation.template.pertanyaan else []
        print(f"❓ Questions count: {len(questions)}")
        for i, q in enumerate(questions):
            print(f"   {i}: {q}")
    except:
        print("❌ Error parsing questions")
else:
    print("❌ No completed evaluation found")