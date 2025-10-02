#!/usr/bin/env python
"""
Test to verify that completed evaluation templates are filtered out
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coop.settings')
django.setup()

from coops.models import EvaluasiSupervisor, KonfirmasiMagang, EvaluasiTemplate

def test_template_filtering():
    """Test that completed templates are filtered out"""
    print("🧪 TESTING TEMPLATE FILTERING FOR COMPLETED EVALUATIONS")
    print("=" * 60)
    
    # Get existing konfirmasi
    konfirmasi = KonfirmasiMagang.objects.filter(status='accepted').first()
    if not konfirmasi:
        print("❌ No accepted konfirmasi found")
        return
    
    student_name = konfirmasi.mahasiswa.get_full_name() or konfirmasi.mahasiswa.username
    print(f"👤 Testing with student: {student_name}")
    print()
    
    # Show all available templates
    all_templates = EvaluasiTemplate.objects.filter(aktif=True)
    print(f"📋 Total available templates: {all_templates.count()}")
    for template in all_templates:
        print(f"   • {template.nama} ({template.get_jenis_display()})")
    print()
    
    def show_filtering_status():
        """Show current filtering status"""
        # Get completed template IDs for this student
        completed_templates = EvaluasiSupervisor.objects.filter(
            konfirmasi=konfirmasi,
            status='completed'
        ).values_list('template_id', flat=True)
        
        # Get available (not completed) templates
        available_templates = EvaluasiTemplate.objects.filter(
            aktif=True
        ).exclude(id__in=completed_templates)
        
        print(f"✅ Completed evaluations: {len(completed_templates)}")
        for template_id in completed_templates:
            template = EvaluasiTemplate.objects.get(id=template_id)
            print(f"   • {template.nama} ({template.get_jenis_display()}) - COMPLETED")
        print()
        
        print(f"📝 Available templates (for form): {available_templates.count()}")
        for template in available_templates:
            print(f"   • {template.nama} ({template.get_jenis_display()}) - AVAILABLE")
        print()
        
        if available_templates.count() == 0:
            print("🎉 ALL EVALUATIONS COMPLETED - No templates should be shown in form!")
        else:
            print(f"⏳ {available_templates.count()} template(s) still available for evaluation")
        print()
        
        return available_templates.count()
    
    # Test scenario 1: Some evaluations pending
    print("🔄 SCENARIO 1: Setting UTS evaluation to PENDING...")
    evaluations = EvaluasiSupervisor.objects.filter(konfirmasi=konfirmasi)
    uts_eval = evaluations.filter(template__jenis='uts').first()
    if uts_eval:
        uts_eval.status = 'pending'
        uts_eval.save()
        print(f"   Set '{uts_eval.template.nama}' to PENDING")
    
    available_count = show_filtering_status()
    
    # Test scenario 2: Complete all evaluations
    print("🔄 SCENARIO 2: Completing ALL evaluations...")
    for evaluation in evaluations:
        if evaluation.status == 'pending':
            evaluation.status = 'completed'
            evaluation.jawaban = {'test': 'completed for filtering test'}
            evaluation.save()
            print(f"   Completed '{evaluation.template.nama}'")
    
    available_count = show_filtering_status()
    
    # Test scenario 3: Set one back to pending
    print("🔄 SCENARIO 3: Setting UAS evaluation back to PENDING...")
    uas_eval = evaluations.filter(template__jenis='uas').first()
    if uas_eval:
        uas_eval.status = 'pending'
        uas_eval.save()
        print(f"   Set '{uas_eval.template.nama}' to PENDING")
    
    available_count = show_filtering_status()
    
    print("✨ FILTERING LOGIC SUMMARY:")
    print("   • When evaluation is COMPLETED → Template is HIDDEN from form")
    print("   • When evaluation is PENDING → Template is SHOWN in form")
    print("   • When ALL evaluations are completed → Form shows 'All evaluations completed' message")
    print("   • When SOME evaluations are pending → Form shows available templates only")
    print()
    print("🎉 TEMPLATE FILTERING TEST COMPLETE!")

if __name__ == "__main__":
    test_template_filtering()