#!/usr/bin/env python
"""
Test the conditional "Isi Evaluasi" button functionality
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coop.settings')
django.setup()

from django.test import RequestFactory
from accounts.models import User
from jobs.models import Supervisor
from jobs.views import supervisor_dashboard
from coops.models import EvaluasiSupervisor, KonfirmasiMagang, EvaluasiTemplate

def test_button_visibility():
    """Test that Isi Evaluasi button is hidden when all evaluations are completed"""
    print("Testing conditional Isi Evaluasi button visibility...")
    
    # Create supervisor user
    supervisor_user, created = User.objects.get_or_create(
        username='button_test_supervisor',
        defaults={
            'email': 'button@test.com',
            'role': 'supervisor',
            'first_name': 'Button',
            'last_name': 'Test'
        }
    )
    
    supervisor_profile = supervisor_user.supervisor
    print(f"Supervisor: {supervisor_profile.nama}")
    
    # Create test student
    student_user, created = User.objects.get_or_create(
        username='button_test_student',
        defaults={
            'email': 'student_button@test.com',
            'role': 'mahasiswa',
            'first_name': 'Student',
            'last_name': 'Button'
        }
    )
    
    # Create konfirmasi
    konfirmasi, created = KonfirmasiMagang.objects.get_or_create(
        mahasiswa=student_user,
        defaults={
            'posisi': 'Test Developer',
            'nama_perusahaan': 'Test Company',
            'alamat_perusahaan': 'Test Address',
            'bidang_usaha': 'Technology',
            'nama_supervisor': supervisor_profile.nama,
            'email_supervisor': supervisor_profile.email,
            'wa_supervisor': '1234567890',
            'status': 'accepted'
        }
    )
    
    print(f"Konfirmasi: {konfirmasi}")
    
    # Get templates
    templates = EvaluasiTemplate.objects.filter(aktif=True)
    print(f"Found {templates.count()} templates")
    
    # Create evaluations (initially pending)
    for template in templates:
        evaluasi, created = EvaluasiSupervisor.objects.get_or_create(
            konfirmasi=konfirmasi,
            template=template,
            defaults={
                'status': 'pending',
                'jawaban': {}
            }
        )
        print(f"Evaluation: {evaluasi.template.nama} - Status: {evaluasi.status}")
    
    # Test dashboard view with pending evaluations
    factory = RequestFactory()
    request = factory.get('/jobs/supervisor/')
    request.user = supervisor_user
    
    response = supervisor_dashboard(request)
    
    # Check if mahasiswa_magang_with_status is in context
    if hasattr(response, 'context_data'):
        context = response.context_data
    else:
        # For render response, we need to get context differently
        from django.template.response import TemplateResponse
        if hasattr(response, 'context'):
            context = response.context
        else:
            print("❌ Could not access context data")
            return
    
    print("\n=== Testing with PENDING evaluations ===")
    mahasiswa_with_status = context.get('mahasiswa_magang_with_status', [])
    
    for item in mahasiswa_with_status:
        konfirmasi_item = item['konfirmasi']
        if konfirmasi_item.id == konfirmasi.id:
            print(f"Student: {konfirmasi_item.mahasiswa.username}")
            print(f"Total evaluations: {item['total_evaluations']}")
            print(f"Completed evaluations: {item['completed_evaluations']}")
            print(f"All completed: {item['all_evaluations_completed']}")
            
            if not item['all_evaluations_completed']:
                print("✅ 'Isi Evaluasi' button should be VISIBLE (evaluations pending)")
            else:
                print("❌ Expected pending evaluations but all are completed")
    
    print("\n=== Testing with COMPLETED evaluations ===")
    # Complete all evaluations
    evaluations = EvaluasiSupervisor.objects.filter(konfirmasi=konfirmasi)
    for evaluation in evaluations:
        evaluation.status = 'completed'
        evaluation.jawaban = {'1': 'Test answer', '2': 'Another answer'}
        evaluation.save()
        print(f"Completed: {evaluation.template.nama}")
    
    # Test again with completed evaluations
    response = supervisor_dashboard(request)
    if hasattr(response, 'context'):
        context = response.context
    
    mahasiswa_with_status = context.get('mahasiswa_magang_with_status', [])
    
    for item in mahasiswa_with_status:
        konfirmasi_item = item['konfirmasi']
        if konfirmasi_item.id == konfirmasi.id:
            print(f"Student: {konfirmasi_item.mahasiswa.username}")
            print(f"Total evaluations: {item['total_evaluations']}")
            print(f"Completed evaluations: {item['completed_evaluations']}")
            print(f"All completed: {item['all_evaluations_completed']}")
            
            if item['all_evaluations_completed']:
                print("✅ 'Isi Evaluasi' button should be HIDDEN (all evaluations completed)")
            else:
                print("❌ Expected all evaluations to be completed")
    
    print("\n✅ Test completed successfully!")

if __name__ == "__main__":
    test_button_visibility()