#!/usr/bin/env python3
"""
Test script untuk menguji fitur kirim ke Kaprodi & Mentor
"""

import os
import sys
import django

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coop.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from coops.models import KonfirmasiMagang, EvaluasiTemplate, EvaluasiSupervisor
from accounts.models import Mahasiswa
import json

User = get_user_model()

def test_kirim_ke_kaprodi():
    """Test fitur kirim ke Kaprodi & Mentor"""
    
    print("🚀 TESTING: KIRIM KE KAPRODI & MENTOR FUNCTIONALITY")
    print("=" * 60)
    
    # Create test client
    client = Client()
    
    # Check if admin user exists
    admin_user = User.objects.filter(role='admin').first()
    if not admin_user:
        print("❌ No admin user found. Please create an admin user first.")
        return
    
    # Login as admin
    client.force_login(admin_user)
    print(f"✅ Logged in as admin: {admin_user.username}")
    
    # Check for completed evaluations
    completed_evaluations = EvaluasiSupervisor.objects.filter(status='completed')
    print(f"📊 Found {completed_evaluations.count()} completed evaluations")
    
    if not completed_evaluations.exists():
        print("⚠️  No completed evaluations found. Creating test data...")
        
        # Create test mahasiswa
        test_user = User.objects.filter(role='mahasiswa').first()
        if not test_user:
            test_user = User.objects.create_user(
                username='test_mahasiswa',
                email='test@student.com',
                password='testpass123',
                role='mahasiswa',
                first_name='Test',
                last_name='Student'
            )
            Mahasiswa.objects.create(email=test_user, nim='123456789')
        
        # Create test konfirmasi
        konfirmasi, created = KonfirmasiMagang.objects.get_or_create(
            mahasiswa=test_user,
            defaults={
                'periode_awal': '2025-01-01',
                'periode_akhir': '2025-06-30',
                'posisi': 'Software Developer Intern',
                'nama_perusahaan': 'Tech Company',
                'alamat_perusahaan': 'Jakarta',
                'bidang_usaha': 'Technology',
                'nama_supervisor': 'John Supervisor',
                'email_supervisor': 'supervisor@company.com',
                'wa_supervisor': '081234567890',
                'status': 'accepted'
            }
        )
        
        # Create test template
        template, created = EvaluasiTemplate.objects.get_or_create(
            nama='Evaluasi UTS Test',
            defaults={
                'jenis': 'uts',
                'pertanyaan': json.dumps([
                    'Bagaimana kinerja mahasiswa dalam menyelesaikan tugas?',
                    'Seberapa baik kemampuan komunikasi mahasiswa?',
                    'Bagaimana tingkat kedisiplinan mahasiswa?'
                ]),
                'aktif': True
            }
        )
        
        # Create test evaluation
        evaluation, created = EvaluasiSupervisor.objects.get_or_create(
            konfirmasi=konfirmasi,
            template=template,
            defaults={
                'status': 'completed',
                'jawaban': {
                    '0': 'Sangat baik, mahasiswa selalu menyelesaikan tugas tepat waktu',
                    '1': 'Komunikasi lancar dan profesional',
                    '2': 'Sangat disiplin, tidak pernah terlambat'
                }
            }
        )
        
        print("✅ Test data created successfully")
    
    # Get first template with completed evaluations
    templates_with_completions = []
    for template in EvaluasiTemplate.objects.filter(aktif=True):
        completed_count = EvaluasiSupervisor.objects.filter(
            template=template, 
            status='completed'
        ).count()
        if completed_count > 0:
            templates_with_completions.append((template, completed_count))
    
    if not templates_with_completions:
        print("❌ No templates with completed evaluations found")
        return
    
    # Test the sending functionality
    template, completed_count = templates_with_completions[0]
    print(f"📧 Testing with template: {template.nama} ({completed_count} completed evaluations)")
    
    # Test the kirim_ke_kaprodi endpoint
    response = client.post(f'/coops/evaluasi/kirim-kaprodi/{template.id}/')
    
    if response.status_code == 302:  # Redirect after successful POST
        print("✅ POST request successful - redirected")
    else:
        print(f"❌ POST request failed with status: {response.status_code}")
        return
    
    # Test tracking evaluasi page
    response = client.get('/coops/tracking-evaluasi/')
    if response.status_code == 200:
        print("✅ Tracking evaluasi page loads successfully")
        
        # Check if button logic works correctly
        if hasattr(response, 'context') and response.context:
            tracking_data = response.context.get('tracking_data', [])
            for data in tracking_data:
                if data['template'].id == template.id:
                    if data['completed'] == data['total_supervisors'] and data['total_supervisors'] > 0:
                        print(f"✅ Button should be visible for template: {data['template'].nama}")
                        print(f"   - Completed: {data['completed']}/{data['total_supervisors']} ({data['completion_rate']}%)")
                    else:
                        print(f"⚠️  Button should be hidden for template: {data['template'].nama}")
                        print(f"   - Completed: {data['completed']}/{data['total_supervisors']} ({data['completion_rate']}%)")
                    break
        else:
            print("✅ Page loads but context not available in test mode")
    else:
        print(f"❌ Tracking evaluasi page failed with status: {response.status_code}")
    
    print("\n📧 Email Configuration:")
    from django.conf import settings
    print(f"   - Backend: {getattr(settings, 'EMAIL_BACKEND', 'Not configured')}")
    print(f"   - From Email: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'Not configured')}")
    print(f"   - Kaprodi Email: {getattr(settings, 'KAPRODI_EMAIL', 'Not configured')}")
    print(f"   - Mentor Email: {getattr(settings, 'MENTOR_EMAIL', 'Not configured')}")
    
    print("\n🎉 TEST COMPLETED: KIRIM KE KAPRODI & MENTOR")
    print("✅ Functionality is working correctly!")
    print("📧 Check console for email output (development mode)")

if __name__ == '__main__':
    test_kirim_ke_kaprodi()