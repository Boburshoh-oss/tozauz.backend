from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import logging

from apps.ecopacket.models import EcoPacketQrCode
from .models import Region, WasteMonthlyReport, Home

logger = logging.getLogger(__name__)


@receiver(post_save, sender=EcoPacketQrCode)
def check_region_limits_on_scan(sender, instance, created, **kwargs):
    """
    EcoPacket skanerlanganda hudud limitlarini tekshirish va
    kerak bo'lsa ogohlantirish yuborish
    """
    print("EcoPacketQrCode signali yuklandi")
    if not created or not instance.scannered_at or not instance.user:
        return

    try:
        # Foydalanuvchining uyini topish
        membership = instance.user.home_membership
        if not membership or not membership.home.region:
            return

        region = membership.home.region
        home = membership.home

        # Joriy oy statistikasini olish
        current_stats = region.get_monthly_waste_statistics()

        # Ogohlantirish chegaralarini aniqlash
        warning_threshold = 0.8  # 80%
        critical_threshold = 1.0  # 100%

        usage_ratio = (
            current_stats["total_scans"] / current_stats["limit"]
            if current_stats["limit"] > 0
            else 0
        )

        # Ogohlantirish yoki kritik holat
        if usage_ratio >= critical_threshold:
            # Kritik holat - limit oshdi
            logger.warning(
                f"KRITIK: {region.name} hududida oylik limit oshdi! "
                f"Joriy: {current_stats['total_scans']}/{current_stats['limit']}"
            )

            # Oylik hisobotni yangilash
            WasteMonthlyReport.generate_monthly_report(region)

        elif usage_ratio >= warning_threshold:
            # Ogohlantirish - 80% ga yetdi
            logger.info(
                f"OGOHLANTIRISH: {region.name} hududida oylik limit {usage_ratio*100:.1f}% ga yetdi! "
                f"Joriy: {current_stats['total_scans']}/{current_stats['limit']}"
            )

    except Exception as e:
        logger.error(f"Hudud limitini tekshirishda xatolik: {str(e)}")


def send_region_warning_notification(region, stats, warning_type="warning"):
    """
    Hudud ogohlantirish xabarini yuborish
    """
    try:
        if warning_type == "critical":
            subject = f"⚠️ KRITIK: {region.name} hududida limit oshdi!"
            message = f"""
DIQQAT! {region.name} hududida oylik chiqindi limitsi oshib ketdi!

📊 STATISTIKA:
• Hudud: {region.name} ({region.code})
• Limit: {stats['limit']} ta paket/oy
• Joriy holat: {stats['total_scans']} ta paket skanerlandi
• Ortiqcha: {stats['total_scans'] - stats['limit']} ta paket
• Foiz: {stats['usage_percentage']}%

Bu holatda darhol chora ko'rish talab etiladi!

Tizim tomonidan avtomatik yuborildi.
            """
        else:  # warning
            subject = f"🟡 OGOHLANTIRISH: {region.name} hududida limit 80% ga yetdi"
            message = f"""
Diqqat! {region.name} hududida oylik chiqindi limitsi 80% ga yetdi.

📊 STATISTIKA:
• Hudud: {region.name} ({region.code})
• Limit: {stats['limit']} ta paket/oy
• Joriy holat: {stats['total_scans']} ta paket skanerlandi
• Qolgan: {stats['remaining']} ta paket
• Foiz: {stats['usage_percentage']}%

Iltimos, chiqindi boshqaruviga e'tibor bering.

Tizim tomonidan avtomatik yuborildi.
            """

        # Email yuborish (agar konfiguratsiya qilingan bo'lsa)
        if hasattr(settings, "REGION_ADMIN_EMAIL") and settings.REGION_ADMIN_EMAIL:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.REGION_ADMIN_EMAIL],
                fail_silently=True,
            )

        logger.info(f"Ogohlantirish yuborildi: {subject}")

    except Exception as e:
        logger.error(f"Ogohlantirish yuborishda xatolik: {str(e)}")


@receiver(post_save, sender=Home)
def update_region_stats_on_home_change(sender, instance, created, **kwargs):
    """
    Uy o'zgarganda hudud statistikasini yangilash
    """
    if created and instance.region:
        logger.info(f"Yangi uy yaratildi: {instance.name} - {instance.region.name}")


def generate_daily_reports():
    """
    Kunlik avtomatik hisobotlar yaratish (cron job uchun)
    """
    try:
        now = timezone.now()
        regions = Region.objects.filter(is_active=True)

        for region in regions:
            WasteMonthlyReport.generate_monthly_report(region, now.year, now.month)

        logger.info(f"Kunlik hisobotlar yaratildi: {regions.count()} ta hudud")

    except Exception as e:
        logger.error(f"Kunlik hisobotlar yaratishda xatolik: {str(e)}")


def check_all_regions_daily():
    """
    Barcha hududlarni kunlik tekshirish
    """
    try:
        regions = Region.objects.filter(is_active=True)
        warning_count = 0
        critical_count = 0

        for region in regions:
            stats = region.get_monthly_waste_statistics()
            usage_ratio = (
                stats["total_scans"] / stats["limit"] if stats["limit"] > 0 else 0
            )

            if usage_ratio >= 1.0:
                critical_count += 1
                send_region_warning_notification(region, stats, "critical")
            elif usage_ratio >= 0.8:
                warning_count += 1
                send_region_warning_notification(region, stats, "warning")

        logger.info(
            f"Kunlik tekshirish tugadi: {critical_count} kritik, {warning_count} ogohlantirish"
        )

    except Exception as e:
        logger.error(f"Kunlik tekshirishda xatolik: {str(e)}")
