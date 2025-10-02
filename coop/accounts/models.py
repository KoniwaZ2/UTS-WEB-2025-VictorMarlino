from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('mahasiswa', 'Mahasiswa'),
        ('supervisor', 'Supervisor'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)


class Mahasiswa(models.Model):
    nama = models.OneToOneField(User, on_delete=models.CASCADE)
    nim = models.CharField(max_length=20)
    prodi = models.CharField(max_length=100)
    angkatan = models.IntegerField()
    jenis_kelamin = models.CharField(max_length=10, choices=[('L', 'Laki-laki'), ('P', 'Perempuan')])
    email = models.EmailField()
    no_hp = models.CharField(max_length=15)
    konsultasi = models.CharField(max_length=100, blank=True, null=True)
    sptjm = models.CharField(max_length=100, blank=True, null=True)
    magang = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nama} {self.nim} {self.prodi} {self.angkatan} {self.jenis_kelamin} {self.email} {self.no_hp} {self.konsultasi} {self.sptjm}"
