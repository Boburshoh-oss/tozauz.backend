from django.core.management.base import BaseCommand
from apps.packet.models import Category


class Command(BaseCommand):
    help = "Test kategoriyalar yaratish va mavjudlarini yangilash"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Mavjud kategoriyalarni o'chirish",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            # Konfirmatsiya so'rash
            confirm = input(
                "Bu barcha mavjud kategoriyalarni o'chiradi! Davom etishni xohlaysizmi? (y/n): "
            )
            if confirm.lower() != "y":
                self.stdout.write(self.style.WARNING("Bekor qilindi."))
                return

            Category.objects.all().delete()
            self.stdout.write(
                self.style.WARNING("Barcha mavjud kategoriyalar o'chirildi")
            )

        # Test kategoriyalar ma'lumotlari
        categories_data = [
            {"name": "Plastik", "summa": 100, "ignore_agent": False},
            {"name": "Qog'oz", "summa": 80, "ignore_agent": False},
            {"name": "Shisha", "summa": 120, "ignore_agent": False},
            {"name": "Metal", "summa": 150, "ignore_agent": False},
            {"name": "Organik", "summa": 50, "ignore_agent": True},
            {"name": "Boshqa", "summa": 60, "ignore_agent": True},
            {"name": "Maishiy", "summa": 70, "ignore_agent": True},
        ]

        created_count = 0
        updated_count = 0

        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data["name"],
                defaults={
                    "summa": cat_data["summa"],
                    "ignore_agent": cat_data["ignore_agent"],
                },
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Yangi kategoriya yaratildi: {category.name} ({category.summa} sum, ignore_agent: {category.ignore_agent})"
                    )
                )
            else:
                # Mavjud bo'lsa yangilash
                category.summa = cat_data["summa"]
                category.ignore_agent = cat_data["ignore_agent"]
                category.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"↻ Kategoriya yangilandi: {category.name} ({category.summa} sum, ignore_agent: {category.ignore_agent})"
                    )
                )

        # Statistika chiqarish
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS(f"NATIJALAR:"))
        self.stdout.write(f"• Yaratilgan kategoriyalar: {created_count}")
        self.stdout.write(f"• Yangilangan kategoriyalar: {updated_count}")
        self.stdout.write(f"• Jami kategoriyalar: {Category.objects.count()}")
        self.stdout.write("=" * 50)

        # Barcha kategoriyalarni ko'rsatish
        self.stdout.write(self.style.SUCCESS("\nBARCHA KATEGORIYALAR:"))
        for category in Category.objects.all().order_by("name"):
            agent_status = (
                "❌ Ulush berilmaydi" if category.ignore_agent else "✅ Ulush beriladi"
            )
            self.stdout.write(
                f"• {category.name} - {category.summa} sum - {agent_status}"
            )
