#!/usr/bin/env python
"""
Comprehensive test to verify the IntegrityError fix
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
from django.contrib.auth.models import AnonymousUser
from accounts.models import User
from jobs.models import Supervisor
from jobs.views import supervisor_dashboard
from coops.models import EvaluasiSupervisor, KonfirmasiMagang, EvaluasiTemplate

def test_supervisor_dashboard_view():
    """Test the supervisor dashboard view that was causing IntegrityError"""
    print("Testing supervisor dashboard view...")
    
    # Create a supervisor user
    supervisor_user, created = User.objects.get_or_create(
        username='dashboard_test_supervisor',
        defaults={
            'email': 'dashboard@test.com',
            'role': 'supervisor',
            'first_name': 'Dashboard',
            'last_name': 'Test'
        }
    )
    
    print(f"Created supervisor user: {supervisor_user.username}")
    
    # Ensure supervisor profile exists
    supervisor_profile = supervisor_user.supervisor
    print(f"Supervisor profile: {supervisor_profile}")
    
    # Create a test student and konfirmasi
    student_user, created = User.objects.get_or_create(
        username='test_student',
        defaults={
            'email': 'student@test.com',
            'role': 'mahasiswa',
            'first_name': 'Test',
            'last_name': 'Student'
        }
    )
    
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
    
    print(f"Created konfirmasi: {konfirmasi}")
    
    # Ensure templates exist
    templates = EvaluasiTemplate.objects.filter(aktif=True)
    print(f"Found {templates.count()} active templates")
    
    # Create request and test the view
    factory = RequestFactory()
    request = factory.get('/jobs/supervisor/')
    request.user = supervisor_user
    
    try:
        # This should NOT raise IntegrityError anymore
        response = supervisor_dashboard(request)
        print(f"✅ Dashboard view executed successfully! Status: {response.status_code}")
        
        # Check if evaluations were created
        evaluations = EvaluasiSupervisor.objects.filter(konfirmasi=konfirmasi)
        print(f"Created {evaluations.count()} evaluations for the student")
        
        for eval in evaluations:
            print(f"  - {eval.template.nama}: jawaban={eval.jawaban}, status={eval.status}")
            
    except Exception as e:
        print(f"❌ Error in dashboard view: {e}")
        return False
    
    print("✅ All tests passed! IntegrityError is fixed.")
    return True

if __name__ == "__main__":
    test_supervisor_dashboard_view()