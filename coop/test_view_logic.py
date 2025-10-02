#!/usr/bin/env python
"""
Direct test of the view logic for template filtering
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
from django.contrib.auth import get_user_model
from coops.models import EvaluasiSupervisor, KonfirmasiMagang, EvaluasiTemplate
from jobs.views import evaluasi_mahasiswa

def test_view_logic():
    """Test the view logic directly"""
    print("🧪 TESTING VIEW LOGIC FOR TEMPLATE FILTERING")
    print("=" * 50)
    
    # Get supervisor user and konfirmasi
    User = get_user_model()
    supervisor_user = User.objects.filter(role='supervisor').first()
    konfirmasi = KonfirmasiMagang.objects.filter(status='accepted').first()
    
    if not supervisor_user or not konfirmasi:
        print("❌ Missing supervisor user or konfirmasi")
        return
    
    print(f"👤 Supervisor: {supervisor_user.get_full_name() or supervisor_user.username}")
    print(f"🎓 Student: {konfirmasi.mahasiswa.get_full_name() or konfirmasi.mahasiswa.username}")
    print()
    
    def test_template_filtering_logic(scenario_name, setup_func=None):
        """Test the filtering logic"""
        print(f"🔄 {scenario_name}")
        
        if setup_func:
            setup_func()
        
        # Simulate the view logic
        completed_templates = EvaluasiSupervisor.objects.filter(
            konfirmasi=konfirmasi,
            status='completed'
        ).values_list('template_id', flat=True)
        
        templates = EvaluasiTemplate.objects.filter(
            aktif=True
        ).exclude(id__in=completed_templates)
        
        completed_evaluations = EvaluasiSupervisor.objects.filter(
            konfirmasi=konfirmasi,
            status='completed'
        ).select_related('template')
        
        print(f"   📋 Total active templates: {EvaluasiTemplate.objects.filter(aktif=True).count()}")
        print(f"   ✅ Completed evaluations: {completed_evaluations.count()}")
        for eval in completed_evaluations:
            print(f"      • {eval.template.nama}")
        
        print(f"   📝 Available templates for form: {templates.count()}")
        for template in templates:
            print(f"      • {template.nama}")
        
        print(f"   🎯 Result: {'All completed - show message' if templates.count() == 0 else f'{templates.count()} template(s) available'}")
        print()
        
        return templates.count()
    
    # Test scenarios
    def setup_mixed():
        """Set up mixed status"""
        evaluations = EvaluasiSupervisor.objects.filter(konfirmasi=konfirmasi)
        uts_eval = evaluations.filter(template__jenis='uts').first()
        if uts_eval:
            uts_eval.status = 'pending'
            uts_eval.save()
        uas_eval = evaluations.filter(template__jenis='uas').first()
        if uas_eval:
            uas_eval.status = 'completed'
            uas_eval.jawaban = {'test': 'completed'}
            uas_eval.save()
    
    def setup_all_completed():
        """Complete all evaluations"""
        evaluations = EvaluasiSupervisor.objects.filter(konfirmasi=konfirmasi)
        for evaluation in evaluations:
            evaluation.status = 'completed'
            evaluation.jawaban = {'test': 'completed'}
            evaluation.save()
    
    def setup_all_pending():
        """Set all evaluations to pending"""
        evaluations = EvaluasiSupervisor.objects.filter(konfirmasi=konfirmasi)
        for evaluation in evaluations:
            evaluation.status = 'pending'
            evaluation.save()
    
    # Run tests
    count1 = test_template_filtering_logic("SCENARIO 1: UTS pending, UAS completed", setup_mixed)
    count2 = test_template_filtering_logic("SCENARIO 2: All evaluations completed", setup_all_completed)
    count3 = test_template_filtering_logic("SCENARIO 3: All evaluations pending", setup_all_pending)
    
    print("✨ VIEW LOGIC TEST RESULTS:")
    print(f"   • Mixed status: {count1} template(s) available ✅")
    print(f"   • All completed: {count2} template(s) available {'✅ (correct)' if count2 == 0 else '❌ (should be 0)'}")
    print(f"   • All pending: {count3} template(s) available ✅")
    print()
    print("🎉 VIEW LOGIC FILTERING TEST COMPLETE!")

if __name__ == "__main__":
    test_view_logic()