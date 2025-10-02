#!/usr/bin/env python
"""
Test template logic for conditional button display
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

def test_template_logic():
    """Simulate template logic for conditional button"""
    print("Testing template conditional logic...")
    
    # Get existing konfirmasi
    konfirmasi = KonfirmasiMagang.objects.filter(status='accepted').first()
    if not konfirmasi:
        print("No accepted konfirmasi found")
        return
    
    print(f"Testing konfirmasi: {konfirmasi.mahasiswa.username}")
    
    # Simulate the view logic
    total_evaluations = EvaluasiSupervisor.objects.filter(konfirmasi=konfirmasi).count()
    completed_evaluations = EvaluasiSupervisor.objects.filter(
        konfirmasi=konfirmasi, 
        status='completed'
    ).count()
    
    all_evaluations_completed = (total_evaluations > 0 and 
                               completed_evaluations == total_evaluations)
    
    item = {
        'konfirmasi': konfirmasi,
        'total_evaluations': total_evaluations,
        'completed_evaluations': completed_evaluations,
        'all_evaluations_completed': all_evaluations_completed
    }
    
    print(f"Template context item:")
    print(f"  - konfirmasi: {item['konfirmasi'].mahasiswa.username}")
    print(f"  - total_evaluations: {item['total_evaluations']}")
    print(f"  - completed_evaluations: {item['completed_evaluations']}")
    print(f"  - all_evaluations_completed: {item['all_evaluations_completed']}")
    
    # Simulate template conditional logic
    print("\nTemplate logic simulation:")
    if not item['all_evaluations_completed']:
        print("✅ SHOW: 'Isi Evaluasi' button (evaluations pending)")
        print(f"   Badge: 'Evaluasi Pending ({item['completed_evaluations']}/{item['total_evaluations']})'")
    else:
        print("✅ HIDE: 'Isi Evaluasi' button (all evaluations completed)")
        print("   Show: 'Evaluasi Selesai' disabled button instead")
        print("   Badge: 'Evaluasi Selesai'")
    
    # Test both scenarios
    print("\n=== Testing completed scenario ===")
    # Set all to completed for testing
    all_evaluations_completed_test = True
    completed_evaluations_test = total_evaluations
    
    item_completed = {
        'konfirmasi': konfirmasi,
        'total_evaluations': total_evaluations,
        'completed_evaluations': completed_evaluations_test,
        'all_evaluations_completed': all_evaluations_completed_test
    }
    
    print(f"Template context item (completed scenario):")
    print(f"  - total_evaluations: {item_completed['total_evaluations']}")
    print(f"  - completed_evaluations: {item_completed['completed_evaluations']}")
    print(f"  - all_evaluations_completed: {item_completed['all_evaluations_completed']}")
    
    if not item_completed['all_evaluations_completed']:
        print("❌ Should SHOW button but all are completed")
    else:
        print("✅ HIDE: 'Isi Evaluasi' button (all evaluations completed)")
        print("   Show: 'Evaluasi Selesai' disabled button instead")

if __name__ == "__main__":
    test_template_logic()