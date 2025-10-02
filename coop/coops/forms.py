from django import forms
from .models import KonfirmasiMagang
from .models import WeeklyReport

class KonfirmasiMagangForm(forms.ModelForm):
    class Meta:
        model = KonfirmasiMagang
        exclude = ["mahasiswa", "status"]
        widgets = {
            "periode": forms.TextInput(attrs={"class": "form-control", "placeholder": "Contoh: 2025/1"}),
            "posisi": forms.TextInput(attrs={"class": "form-control"}),
            "nama_perusahaan": forms.TextInput(attrs={"class": "form-control"}),
            "alamat_perusahaan": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "bidang_usaha": forms.TextInput(attrs={"class": "form-control"}),
            "nama_supervisor": forms.TextInput(attrs={"class": "form-control"}),
            "email_supervisor": forms.EmailInput(attrs={"class": "form-control"}),
            "wa_supervisor": forms.TextInput(attrs={"class": "form-control"}),
            # asumsikan field file bernama 'surat_penerimaan'
            "surat_penerimaan": forms.ClearableFileInput(attrs={"class": "form-control-file"}),
        }

class WeeklyReportForm(forms.ModelForm):
    class Meta:
        model = WeeklyReport
        fields = ['week_start', 'report_text']
        widgets = {
            'week_start': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'report_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
