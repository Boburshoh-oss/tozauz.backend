from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.home.models import Region, WasteMonthlyReport
from datetime import datetime


class Command(BaseCommand):
    help = "Barcha hududlar uchun oylik chiqindi hisobotlarini yaratish"

    def add_arguments(self, parser):
        parser.add_argument(
            "--year",
            type=int,
            help="Hisobot yili (masalan: 2024)",
        )
        parser.add_argument(
            "--month",
            type=int,
            help="Hisobot oyi (1-12)",
        )
        parser.add_argument(
            "--region",
            type=str,
            help="Hudud kodi (masalan: TAS-01)",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Mavjud hisobotlarni qayta yaratish",
        )

    def handle(self, *args, **options):
        # Parametrlarni olish
        year = options.get("year") or timezone.now().year
        month = options.get("month") or timezone.now().month
        region_code = options.get("region")
        force_regenerate = options.get("force", False)

        # Parametrlarni tekshirish
        if not (1 <= month <= 12):
            self.stdout.write(self.style.ERROR("Oy 1-12 orasida bo'lishi kerak"))
            return

        if year < 2020 or year > timezone.now().year + 1:
            self.stdout.write(self.style.ERROR("Yil noto'g'ri kiritilgan"))
            return

        # Hududlarni filtrlash
        if region_code:
            regions = Region.objects.filter(code=region_code, is_active=True)
            if not regions.exists():
                self.stdout.write(
                    self.style.ERROR(f"Hudud kodi topilmadi: {region_code}")
                )
                return
        else:
            regions = Region.objects.filter(is_active=True)

        self.stdout.write(
            self.style.SUCCESS(
                f"\n{'='*60}\n"
                f"OYLIK HISOBOTLAR YARATISH\n"
                f"Sana: {year}/{month:02d}\n"
                f"Hududlar soni: {regions.count()}\n"
                f"{'='*60}"
            )
        )

        created_count = 0
        updated_count = 0
        error_count = 0

        for region in regions:
            try:
                # Hisobotni yaratish yoki yangilash
                if force_regenerate:
                    # Mavjud hisobotni o'chirish
                    WasteMonthlyReport.objects.filter(
                        region=region, year=year, month=month
                    ).delete()

                report = WasteMonthlyReport.generate_monthly_report(region, year, month)

                # Hisobot yaratilganmi yoki yangilanganmi aniqlash
                if (
                    WasteMonthlyReport.objects.filter(
                        region=region, year=year, month=month
                    ).count()
                    == 1
                ):
                    existing_report = WasteMonthlyReport.objects.get(
                        region=region, year=year, month=month
                    )
                    if existing_report.pk == report.pk and not force_regenerate:
                        updated_count += 1
                        status_icon = "↻"
                        status_text = "yangilandi"
                    else:
                        created_count += 1
                        status_icon = "✓"
                        status_text = "yaratildi"
                else:
                    created_count += 1
                    status_icon = "✓"
                    status_text = "yaratildi"

                # Limit holatini aniqlash
                if report.limit_exceeded:
                    limit_status = "⚠️ LIMIT OSHDI"
                    limit_color = self.style.ERROR
                elif report.total_scans / region.monthly_waste_limit >= 0.8:
                    limit_status = "🟡 OGOHLANTIRISH"
                    limit_color = self.style.WARNING
                else:
                    limit_status = "✅ NORMAL"
                    limit_color = self.style.SUCCESS

                self.stdout.write(
                    f"{status_icon} {region.name} ({region.code}) - {status_text}\n"
                    f"   Skanlar: {report.total_scans}/{region.monthly_waste_limit} "
                    f"({report.total_scans/region.monthly_waste_limit*100:.1f}%) - "
                )
                self.stdout.write(limit_color(f"   {limit_status}"))

            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(
                        f"❌ {region.name} ({region.code}) - Xatolik: {str(e)}"
                    )
                )

        # Yakuniy natijalar
        self.stdout.write(
            f"\n{'='*60}\n"
            f"NATIJALAR:\n"
            f"• Yaratilgan hisobotlar: {created_count}\n"
            f"• Yangilangan hisobotlar: {updated_count}\n"
            f"• Xatoliklar: {error_count}\n"
            f"• Jami qayta ishlangan: {created_count + updated_count}\n"
            f"{'='*60}"
        )

        # Limit oshgan hududlar ro'yxati
        critical_reports = WasteMonthlyReport.objects.filter(
            year=year, month=month, limit_exceeded=True
        ).select_related("region")

        if critical_reports.exists():
            self.stdout.write(
                self.style.ERROR(
                    f"\n⚠️ LIMIT OSHGAN HUDUDLAR ({critical_reports.count()} ta):"
                )
            )
            for report in critical_reports:
                percentage = (
                    report.total_scans / report.region.monthly_waste_limit
                ) * 100
                self.stdout.write(
                    self.style.ERROR(
                        f"• {report.region.name}: {report.total_scans}/{report.region.monthly_waste_limit} "
                        f"({percentage:.1f}%)"
                    )
                )

        # Ogohlantirish zonasidagi hududlar
        warning_reports = WasteMonthlyReport.objects.filter(
            year=year, month=month, limit_exceeded=False
        ).select_related("region")

        warning_count = 0
        for report in warning_reports:
            if report.total_scans / report.region.monthly_waste_limit >= 0.8:
                warning_count += 1

        if warning_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"\n🟡 OGOHLANTIRISH ZONASIDA ({warning_count} ta hudud 80%+ ishlatish)"
                )
            )
