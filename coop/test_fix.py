#!/usr/bin/env python
"""
Test script to verify the EvaluasiSupervisor model fix
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coop.settings')
django.setup()

from coops.models import EvaluasiSupervisor, EvaluasiTemplate, KonfirmasiMagang
from accounts.models import User

def test_evaluation_creation():
    """Test creating evaluation with empty jawaban"""
    print("Testing EvaluasiSupervisor creation...")
    
    # Get first user and template for testing
    try:
        user = User.objects.filter(role='mahasiswa').first()
        if not user:
            print("No mahasiswa user found")
            return
        
        konfirmasi = KonfirmasiMagang.objects.filter(mahasiswa=user).first()
        if not konfirmasi:
            print("No konfirmasi found for user")
            return
            
        template = EvaluasiTemplate.objects.first()
        if not template:
            print("No evaluation template found")
            return
        
        # Try to create evaluation with empty jawaban
        evaluation, created = EvaluasiSupervisor.objects.get_or_create(
            konfirmasi=konfirmasi,
            template=template,
            defaults={
                'status': 'pending',
                'jawaban': {}  # Empty dict should work now
            }
        )
        
        if created:
            print(f"✅ Successfully created evaluation: {evaluation}")
        else:
            print(f"✅ Evaluation already exists: {evaluation}")
            
        print(f"Jawaban field value: {evaluation.jawaban}")
        print(f"Jawaban field type: {type(evaluation.jawaban)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_evaluation_creation()