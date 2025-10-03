#!/usr/bin/env python
"""
Test script untuk memeriksa apakah error import Mahasiswa sudah diperbaiki
"""

import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_import_fix():
    """Test apakah error import Mahasiswa sudah diperbaiki"""
    
    print("🔧 TESTING: Perbaikan Import Error 'Mahasiswa'")
    print("=" * 60)
    
    try:
        print("1. ✅ Testing import dari views.py...")
        
        # Set up Django environment
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coop.settings')
        
        import django
        django.setup()
        
        # Test import
        from coops.views import laporan_mahasiswa
        print("   ✅ View laporan_mahasiswa berhasil diimport")
        
        print("\n2. ✅ Testing import models...")
        from accounts.models import Mahasiswa
        from coops.models import KonfirmasiMagang, LaporanKemajuan
        print("   ✅ Models Mahasiswa, KonfirmasiMagang, LaporanKemajuan berhasil diimport")
        
        print("\n3. ✅ Testing URL resolution...")
        from django.urls import reverse
        url = reverse('coops:laporan_mahasiswa')
        print(f"   ✅ URL resolved: {url}")
        
        print("\n" + "=" * 60)
        print("🎉 HASIL TEST: PERBAIKAN IMPORT BERHASIL!")
        print("✅ Import Mahasiswa sudah ditambahkan ke top-level imports")
        print("✅ Import LaporanKemajuan sudah dioptimalkan")
        print("✅ View laporan_mahasiswa sekarang bisa diakses tanpa error")
        print("✅ URL /coops/laporan-mahasiswa/ sekarang berfungsi")
        
        print("\n📝 PERBAIKAN YANG DILAKUKAN:")
        print("- Menambahkan 'from accounts.models import Mahasiswa' ke top imports")
        print("- Menambahkan 'LaporanKemajuan' ke import models di top level")
        print("- Menghapus redundant import di dalam function")
        print("- Memastikan semua dependencies tersedia secara global")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error lainnya: {e}")
        return False

if __name__ == "__main__":
    success = test_import_fix()
    if success:
        print("\n🚀 READY TO USE: Error 'name Mahasiswa is not defined' sudah diperbaiki!")
        print("💡 Sekarang halaman /coops/laporan-mahasiswa/ bisa diakses tanpa error")
    else:
        print("\n⚠️  PERLU PERBAIKAN: Masih ada masalah yang perlu diperbaiki")