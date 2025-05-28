from django.core.management.base import BaseCommand
from apps.home.models import Region


class Command(BaseCommand):
    help = "O'zbekiston hududlari bilan Region modelini to'ldirish"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Mavjud hududlarni o'chirish",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            Region.objects.all().delete()
            self.stdout.write(self.style.WARNING("Barcha mavjud hududlar o'chirildi"))

        # O'zbekiston hududlari ro'yxati
        regions_data = [
            # Toshkent shahri va viloyati
            {"name": "Toshkent shahri", "code": "TAS-01", "monthly_waste_limit": 25},
            {"name": "Toshkent viloyati", "code": "TAS-02", "monthly_waste_limit": 20},
            # Boshqa viloyatlar
            {"name": "Andijon viloyati", "code": "AND-01", "monthly_waste_limit": 15},
            {"name": "Buxoro viloyati", "code": "BUX-01", "monthly_waste_limit": 15},
            {"name": "Farg'ona viloyati", "code": "FAR-01", "monthly_waste_limit": 18},
            {"name": "Jizzax viloyati", "code": "JIZ-01", "monthly_waste_limit": 12},
            {"name": "Xorazm viloyati", "code": "XOR-01", "monthly_waste_limit": 14},
            {"name": "Namangan viloyati", "code": "NAM-01", "monthly_waste_limit": 16},
            {"name": "Navoiy viloyati", "code": "NAV-01", "monthly_waste_limit": 13},
            {
                "name": "Qashqadaryo viloyati",
                "code": "QAS-01",
                "monthly_waste_limit": 17,
            },
            {
                "name": "Qoraqalpog'iston Respublikasi",
                "code": "QOR-01",
                "monthly_waste_limit": 14,
            },
            {"name": "Samarqand viloyati", "code": "SAM-01", "monthly_waste_limit": 19},
            {"name": "Sirdaryo viloyati", "code": "SIR-01", "monthly_waste_limit": 11},
            {
                "name": "Surxondaryo viloyati",
                "code": "SUR-01",
                "monthly_waste_limit": 13,
            },
        ]

        created_count = 0
        updated_count = 0

        for region_data in regions_data:
            region, created = Region.objects.get_or_create(
                code=region_data["code"],
                defaults={
                    "name": region_data["name"],
                    "monthly_waste_limit": region_data["monthly_waste_limit"],
                    "description": f"{region_data['name']} hududida oylik {region_data['monthly_waste_limit']} ta paket chiqindi limitsi belgilangan.",
                    "is_active": True,
                },
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Yangi hudud yaratildi: {region.name} ({region.code})"
                    )
                )
            else:
                # Mavjud bo'lsa yangilash
                region.name = region_data["name"]
                region.monthly_waste_limit = region_data["monthly_waste_limit"]
                region.description = f"{region_data['name']} hududida oylik {region_data['monthly_waste_limit']} ta paket chiqindi limitsi belgilangan."
                region.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"↻ Hudud yangilandi: {region.name} ({region.code})"
                    )
                )

        # Statistika chiqarish
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS(f"NATIJALAR:"))
        self.stdout.write(f"• Yaratilgan hududlar: {created_count}")
        self.stdout.write(f"• Yangilangan hududlar: {updated_count}")
        self.stdout.write(f"• Jami hududlar: {Region.objects.count()}")
        self.stdout.write("=" * 50)

        # Barcha hududlarni ko'rsatish
        self.stdout.write(self.style.SUCCESS("\nBARCHA HUDUDLAR:"))
        for region in Region.objects.all().order_by("name"):
            status = "✅ Faol" if region.is_active else "❌ Faol emas"
            self.stdout.write(
                f"• {region.name} ({region.code}) - Limit: {region.monthly_waste_limit} ta - {status}"
            )
