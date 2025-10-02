#!/usr/bin/env python
"""
Simple test to verify evaluation completion logic
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
from coops.models import EvaluasiSupervisor, KonfirmasiMagang, EvaluasiTemplate

def test_evaluation_logic():
    """Test the evaluation completion logic"""
    print("Testing evaluation completion logic...")
    
    # Get existing data
    konfirmasi = KonfirmasiMagang.objects.filter(status='accepted').first()
    if not konfirmasi:
        print("No accepted konfirmasi found")
        return
    
    print(f"Testing with konfirmasi: {konfirmasi.mahasiswa.username}")
    
    # Count evaluations
    total_evaluations = EvaluasiSupervisor.objects.filter(konfirmasi=konfirmasi).count()
    completed_evaluations = EvaluasiSupervisor.objects.filter(
        konfirmasi=konfirmasi, 
        status='completed'
    ).count()
    
    all_evaluations_completed = (total_evaluations > 0 and 
                               completed_evaluations == total_evaluations)
    
    print(f"Total evaluations: {total_evaluations}")
    print(f"Completed evaluations: {completed_evaluations}")
    print(f"All completed: {all_evaluations_completed}")
    
    if all_evaluations_completed:
        print("✅ All evaluations completed - button should be HIDDEN")
    else:
        print("✅ Some evaluations pending - button should be VISIBLE")
    
    # Test with completion
    print("\n=== Completing all evaluations ===")
    evaluations = EvaluasiSupervisor.objects.filter(konfirmasi=konfirmasi)
    for evaluation in evaluations:
        if evaluation.status == 'pending':
            evaluation.status = 'completed'
            evaluation.jawaban = {'test': 'completed'}
            evaluation.save()
            print(f"Completed: {evaluation.template.nama}")
    
    # Re-check
    completed_evaluations = EvaluasiSupervisor.objects.filter(
        konfirmasi=konfirmasi, 
        status='completed'
    ).count()
    
    all_evaluations_completed = (total_evaluations > 0 and 
                               completed_evaluations == total_evaluations)
    
    print(f"Total evaluations: {total_evaluations}")
    print(f"Completed evaluations: {completed_evaluations}")
    print(f"All completed: {all_evaluations_completed}")
    
    if all_evaluations_completed:
        print("✅ Now all evaluations completed - button should be HIDDEN")
    else:
        print("❌ Expected all evaluations to be completed")

if __name__ == "__main__":
    test_evaluation_logic()