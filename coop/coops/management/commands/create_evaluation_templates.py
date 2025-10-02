from django.core.management.base import BaseCommand
from coops.models import EvaluasiTemplate
import json


class Command(BaseCommand):
    help = 'Membuat template evaluasi default untuk UTS dan UAS'

    def handle(self, *args, **options):
        # Template UTS - Laporan Kemajuan
        uts_questions = [
            "Bagaimana penilaian Anda terhadap kemampuan teknis mahasiswa?",
            "Seberapa baik kemampuan komunikasi mahasiswa dengan tim?", 
            "Bagaimana inisiatif dan kreativitas mahasiswa dalam menyelesaikan tugas?",
            "Seberapa baik kedisiplinan dan tanggung jawab mahasiswa?",
            "Bagaimana kemampuan mahasiswa dalam bekerja sama dengan tim?",
            "Berikan feedback konstruktif untuk pengembangan mahasiswa kedepan"
        ]

        uts_template, created = EvaluasiTemplate.objects.get_or_create(
            nama="Evaluasi UTS - Laporan Kemajuan",
            jenis="uts",
            defaults={
                'pertanyaan': json.dumps(uts_questions),  # Convert to JSON string
                'aktif': True
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Template UTS berhasil dibuat: {uts_template.nama}')
            )
        else:
            # Update existing template with proper JSON format
            uts_template.pertanyaan = json.dumps(uts_questions)
            uts_template.aktif = True
            uts_template.save()
            self.stdout.write(
                self.style.WARNING(f'Template UTS diperbarui: {uts_template.nama}')
            )

        # Template UAS - Laporan Akhir
        uas_questions = [
            "Berikan penilaian keseluruhan terhadap kinerja mahasiswa selama magang",
            "Bagaimana pencapaian target dan goals yang telah ditetapkan?",
            "Sebutkan kelebihan yang menonjol dari mahasiswa ini",
            "Apa saja area yang masih perlu diperbaiki atau dikembangkan?",
            "Bagaimana kemampuan adaptasi mahasiswa terhadap lingkungan kerja?",
            "Apakah mahasiswa menunjukkan profesionalisme dalam bekerja?",
            "Berikan rekomendasi untuk pengembangan karir mahasiswa",
            "Apakah Anda merekomendasikan mahasiswa ini untuk posisi yang lebih tinggi?",
            "Saran untuk perbaikan program magang di masa mendatang"
        ]

        uas_template, created = EvaluasiTemplate.objects.get_or_create(
            nama="Evaluasi UAS - Laporan Akhir",
            jenis="uas", 
            defaults={
                'pertanyaan': json.dumps(uas_questions),  # Convert to JSON string
                'aktif': True
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Template UAS berhasil dibuat: {uas_template.nama}')
            )
        else:
            # Update existing template with proper JSON format
            uas_template.pertanyaan = json.dumps(uas_questions)
            uas_template.aktif = True
            uas_template.save()
            self.stdout.write(
                self.style.WARNING(f'Template UAS diperbarui: {uas_template.nama}')
            )

        # Tampilkan summary
        total_templates = EvaluasiTemplate.objects.count()
        self.stdout.write(
            self.style.SUCCESS(f'\nTotal template evaluasi: {total_templates}')
        )
        
        for template in EvaluasiTemplate.objects.all():
            try:
                questions = json.loads(template.pertanyaan) if template.pertanyaan else []
                question_count = len(questions)
            except:
                question_count = 0
            self.stdout.write(f"• {template.nama} ({template.get_jenis_display()}) - {question_count} pertanyaan")