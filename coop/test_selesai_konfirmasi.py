#!/usr/bin/env python
"""Test POST to selesai_konfirmasi to ensure it marks konfirmasi as completed"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coop.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from coops.models import KonfirmasiMagang

User = get_user_model()

client = Client()

supervisor = User.objects.filter(role='supervisor').first()
konfirmasi = KonfirmasiMagang.objects.filter(status='accepted').first()

print('Supervisor:', supervisor)
print('Konfirmasi:', konfirmasi)

if not supervisor or not konfirmasi:
    print('Missing supervisor or konfirmasi. Aborting test.')
    sys.exit(1)

# login via force_login
client.force_login(supervisor)

# Provide HTTP_HOST to prevent DisallowedHost during tests
resp = client.post(f'/jobs/supervisor/selesai/{konfirmasi.id}/', {}, HTTP_HOST='127.0.0.1')
print('POST response status:', resp.status_code)
konfirmasi.refresh_from_db()
print('New konfirmasi status:', konfirmasi.status)

if konfirmasi.status == 'completed':
    print('✅ sukses: konfirmasi ditandai completed')
else:
    print('❌ gagal: status tidak berubah')