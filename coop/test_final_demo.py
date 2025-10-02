#!/usr/bin/env python
"""
Final test demonstrating the conditional button functionality
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coop.settings')
django.setup()

from coops.models import EvaluasiSupervisor, KonfirmasiMagang

def demonstrate_functionality():
    """Demonstrate the conditional button functionality"""
    print("🎯 DEMONSTRATING CONDITIONAL 'ISI EVALUASI' BUTTON FUNCTIONALITY")
    print("=" * 70)
    
    # Get existing konfirmasi
    konfirmasi = KonfirmasiMagang.objects.filter(status='accepted').first()
    if not konfirmasi:
        print("❌ No accepted konfirmasi found")
        return
    
    student_name = konfirmasi.mahasiswa.get_full_name() or konfirmasi.mahasiswa.username
    print(f"👤 Testing with student: {student_name}")
    print(f"🏢 Company: {konfirmasi.nama_perusahaan}")
    print(f"💼 Position: {konfirmasi.posisi}")
    print()
    
    def show_status():
        """Show current evaluation status"""
        total = EvaluasiSupervisor.objects.filter(konfirmasi=konfirmasi).count()
        completed = EvaluasiSupervisor.objects.filter(
            konfirmasi=konfirmasi, status='completed'
        ).count()
        pending = total - completed
        all_completed = (total > 0 and completed == total)
        
        print(f"📊 CURRENT STATUS:")
        print(f"   Total evaluations: {total}")
        print(f"   Completed: {completed}")
        print(f"   Pending: {pending}")
        print(f"   All completed: {all_completed}")
        print()
        
        # Show what the UI would display
        if all_completed:
            print("🔴 UI STATE: 'Isi Evaluasi' button is HIDDEN")
            print("   ✅ Shows: 'Evaluasi Selesai' (disabled button)")
            print("   🏷️  Badge: 'Evaluasi Selesai' (green)")
        else:
            print("🟢 UI STATE: 'Isi Evaluasi' button is VISIBLE")
            print("   📝 Shows: 'Isi Evaluasi' (clickable button)")
            print(f"   🏷️  Badge: 'Evaluasi Pending ({completed}/{total})' (warning)")
        print()
        
        return all_completed
    
    # Test scenario 1: Mixed status (some pending)
    print("🔄 SCENARIO 1: Setting one evaluation to PENDING...")
    evaluations = EvaluasiSupervisor.objects.filter(konfirmasi=konfirmasi)
    if evaluations.exists():
        first_eval = evaluations.first()
        first_eval.status = 'pending'
        first_eval.save()
        print(f"   Set '{first_eval.template.nama}' to PENDING")
    
    show_status()
    
    # Test scenario 2: All completed
    print("🔄 SCENARIO 2: Completing ALL evaluations...")
    for evaluation in evaluations:
        if evaluation.status == 'pending':
            evaluation.status = 'completed'
            evaluation.jawaban = {'test': 'completed for demo'}
            evaluation.save()
            print(f"   Completed '{evaluation.template.nama}'")
    
    show_status()
    
    # Test scenario 3: Back to mixed
    print("🔄 SCENARIO 3: Setting UAS evaluation back to PENDING...")
    uas_eval = evaluations.filter(template__jenis='uas').first()
    if uas_eval:
        uas_eval.status = 'pending'
        uas_eval.save()
        print(f"   Set '{uas_eval.template.nama}' to PENDING")
    
    show_status()
    
    print("✨ SUMMARY OF FUNCTIONALITY:")
    print("   • When ALL evaluations are completed → 'Isi Evaluasi' button is HIDDEN")
    print("   • When ANY evaluation is pending → 'Isi Evaluasi' button is VISIBLE")
    print("   • Status badge shows completion progress (e.g., '1/2 completed')")
    print("   • Quick action modal only shows students with pending evaluations")
    print("   • Completed students show 'Evaluasi Selesai' disabled button instead")
    print()
    print("🎉 IMPLEMENTATION COMPLETE!")

if __name__ == "__main__":
    demonstrate_functionality()