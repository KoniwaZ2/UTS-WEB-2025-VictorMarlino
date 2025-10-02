#!/usr/bin/env python
"""Test the new hasil_evaluasi view"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coop.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from coops.models import KonfirmasiMagang, EvaluasiSupervisor, EvaluasiTemplate

User = get_user_model()
client = Client()

# Get admin user
admin_user = User.objects.filter(role='admin').first()
if not admin_user:
    print("❌ No admin user found")
    exit(1)

# Get completed evaluation
completed_evaluation = EvaluasiSupervisor.objects.filter(status='completed').first()
if not completed_evaluation:
    print("❌ No completed evaluation found")
    exit(1)

konfirmasi = completed_evaluation.konfirmasi
template = completed_evaluation.template

print(f"Testing hasil_evaluasi view:")
print(f"👤 Admin: {admin_user.username}")
print(f"🎓 Student: {konfirmasi.mahasiswa.get_full_name() or konfirmasi.mahasiswa.username}")
print(f"📋 Template: {template.nama}")
print(f"✅ Evaluation Status: {completed_evaluation.status}")

# Login as admin
client.force_login(admin_user)

# Test the new view
url = f'/coops/evaluasi/hasil/{konfirmasi.id}/{template.id}/'
response = client.get(url, HTTP_HOST='127.0.0.1')

print(f"\n🔗 URL: {url}")
print(f"📊 Response Status: {response.status_code}")

if response.status_code == 200:
    content = response.content.decode('utf-8')
    print("✅ Page loaded successfully!")
    
    # Check if key elements are present
    checks = [
        ('Template name in title', template.nama in content),
        ('Student name displayed', konfirmasi.mahasiswa.username in content),
        ('Supervisor name displayed', konfirmasi.nama_supervisor in content),
        ('Evaluation status shown', 'Sudah Diisi' in content or 'completed' in content),
        ('Print button present', 'Cetak Evaluasi' in content),
        ('Back link present', 'Kembali ke Tracking' in content)
    ]
    
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"   {status} {check_name}")
        
    # Check if answers are displayed
    if completed_evaluation.jawaban:
        answers_found = any(answer in content for answer in completed_evaluation.jawaban.values() if answer)
        print(f"   {'✅' if answers_found else '❌'} Evaluation answers displayed")
    
else:
    print(f"❌ Failed to load page: {response.status_code}")
    if hasattr(response, 'content'):
        print(f"Response content: {response.content.decode('utf-8')[:500]}...")

print(f"\n🎉 Test completed!")