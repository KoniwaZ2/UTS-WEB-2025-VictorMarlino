#!/usr/bin/env python
"""
Test supervisor dashboard functionality
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coop.settings')
django.setup()

from accounts.models import User
from jobs.models import Supervisor
from coops.models import EvaluasiSupervisor, EvaluasiTemplate, KonfirmasiMagang

def test_supervisor_access():
    """Test supervisor access and evaluation creation"""
    print("Testing supervisor dashboard functionality...")
    
    # Get or create a supervisor user
    supervisor_user, created = User.objects.get_or_create(
        username='test_supervisor',
        defaults={
            'email': 'supervisor@test.com',
            'role': 'supervisor',
            'first_name': 'Test',
            'last_name': 'Supervisor'
        }
    )
    
    print(f"Supervisor user: {supervisor_user.username} (created: {created})")
    
    # Test supervisor property access
    try:
        supervisor_profile = supervisor_user.supervisor
        print(f"✅ Supervisor profile accessed: {supervisor_profile}")
    except Exception as e:
        print(f"❌ Error accessing supervisor profile: {e}")
        return
    
    # Test auto-creation of evaluations
    templates = EvaluasiTemplate.objects.filter(aktif=True)
    konfirmasi_list = KonfirmasiMagang.objects.filter(status='accepted', email_supervisor=supervisor_profile.email)
    
    print(f"Found {templates.count()} templates and {konfirmasi_list.count()} accepted students")
    
    evaluation_count_before = EvaluasiSupervisor.objects.count()
    
    # Simulate the dashboard view logic
    for konfirmasi in konfirmasi_list:
        for template in templates:
            evaluasi, created = EvaluasiSupervisor.objects.get_or_create(
                konfirmasi=konfirmasi,
                template=template,
                defaults={
                    'status': 'pending',
                    'jawaban': {}
                }
            )
            if created:
                print(f"✅ Created evaluation: {evaluasi}")
    
    evaluation_count_after = EvaluasiSupervisor.objects.count()
    print(f"Evaluations before: {evaluation_count_before}, after: {evaluation_count_after}")
    
    print("✅ Supervisor dashboard test completed successfully!")

if __name__ == "__main__":
    test_supervisor_access()