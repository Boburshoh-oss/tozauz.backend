from django.db import models
from django.core.validators import MinLengthValidator
from django.utils import timezone
from datetime import datetime
from django.db.models import Count


class Region(models.Model):
    """Hududlar modeli"""

    name = models.CharField(
        max_length=100, unique=True, help_text="Hudud nomi", verbose_name="Hudud nomi"
    )
    code = models.CharField(
        max_length=10,
        unique=True,
        help_text="Hudud kodi (masalan: TAS-01)",
        verbose_name="Hudud kodi",
    )
    monthly_waste_limit = models.PositiveIntegerField(
        default=15,
        help_text="Oylik chiqindi limitsi (paketlar soni)",
        verbose_name="Oylik chiqindi limitsi",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Hudud haqida qo'shimcha ma'lumot",
        verbose_name="Tavsif",
    )
    is_active = models.BooleanField(
        default=True, help_text="Hudud faol holati", verbose_name="Faol"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Hudud"
        verbose_name_plural = "Hududlar"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"

    @property
    def total_homes(self):
        """Hududdagi uylar soni"""
        return self.homes.filter(is_active=True).count()

    @property
    def total_active_members(self):
        """Hududdagi barcha faol a'zolar soni"""
        return sum(home.member_count for home in self.homes.filter(is_active=True))

    def get_monthly_waste_statistics(self, year=None, month=None):
        """Oylik chiqindi statistikasini olish"""
        if not year:
            year = timezone.now().year
        if not month:
            month = timezone.now().month

        from apps.ecopacket.models import EcoPacketQrCode

        # Hududdagi barcha uylarning a'zolari
        home_members = []
        for home in self.homes.filter(is_active=True):
            for membership in home.memberships.filter(user__is_active=True):
                home_members.append(membership.user.id)

        # Oylik skanerlangan paketlar soni
        monthly_scans = EcoPacketQrCode.objects.filter(
            user__id__in=home_members,
            scannered_at__year=year,
            scannered_at__month=month,
            scannered_at__isnull=False,
        ).count()

        return {
            "year": year,
            "month": month,
            "total_scans": monthly_scans,
            "limit": self.monthly_waste_limit,
            "remaining": max(0, self.monthly_waste_limit - monthly_scans),
            "is_exceeded": monthly_scans > self.monthly_waste_limit,
            "usage_percentage": (
                round((monthly_scans / self.monthly_waste_limit) * 100, 2)
                if self.monthly_waste_limit > 0
                else 0
            ),
        }


class Home(models.Model):
    name = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(2)],
        help_text="Uy nomi kamida 2 ta belgidan iborat bo'lishi kerak",
    )
    address = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Home owner (optional)
    owner = models.ForeignKey(
        "account.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_homes",
    )

    # Region relation
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        null=True,
        related_name="homes",
        help_text="Uy tegishli bo'lgan hudud",
        verbose_name="Hudud",
        
    )

    # Invitation code for joining the home
    invitation_code = models.CharField(
        max_length=10, unique=True, help_text="Uyga qo'shilish uchun taklifnoma kodi"
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Uy"
        verbose_name_plural = "Uylar"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.region.name}"

    def save(self, *args, **kwargs):
        if not self.invitation_code:
            # Generate unique invitation code
            import random
            import string

            while True:
                code = "".join(
                    random.choices(string.ascii_uppercase + string.digits, k=8)
                )
                if not Home.objects.filter(invitation_code=code).exists():
                    self.invitation_code = code
                    break
        super().save(*args, **kwargs)

    @property
    def member_count(self):
        """Uy a'zolari soni"""
        return self.memberships.filter(user__is_active=True).count()

    @property
    def members(self):
        """Uy a'zolari (QuerySet)"""
        return self.memberships.filter(user__is_active=True)

    def get_monthly_waste_count(self, year=None, month=None):
        """Uy a'zolarining oylik chiqindi soni"""
        if not year:
            year = timezone.now().year
        if not month:
            month = timezone.now().month

        from apps.ecopacket.models import EcoPacketQrCode

        # Uy a'zolarining user id lari
        member_ids = [membership.user.id for membership in self.members]

        # Oylik skanerlangan paketlar soni
        monthly_count = EcoPacketQrCode.objects.filter(
            user__id__in=member_ids,
            scannered_at__year=year,
            scannered_at__month=month,
            scannered_at__isnull=False,
        ).count()

        return monthly_count

    def check_region_limit_warning(self, year=None, month=None):
        """Hudud limitiga yetish ogohlantirishini tekshirish"""
        if not year:
            year = timezone.now().year
        if not month:
            month = timezone.now().month

        region_stats = self.region.get_monthly_waste_statistics(year, month)
        home_contribution = self.get_monthly_waste_count(year, month)

        warning_threshold = 0.8  # 80% chegaragacha yetganda ogohlantirish
        critical_threshold = 1.0  # 100% limitga yetganda

        usage_ratio = (
            region_stats["total_scans"] / region_stats["limit"]
            if region_stats["limit"] > 0
            else 0
        )

        warning_data = {
            "has_warning": usage_ratio >= warning_threshold,
            "is_critical": usage_ratio >= critical_threshold,
            "region_stats": region_stats,
            "home_contribution": home_contribution,
            "home_percentage": (
                round((home_contribution / region_stats["total_scans"]) * 100, 2)
                if region_stats["total_scans"] > 0
                else 0
            ),
            "warning_message": self._get_warning_message(usage_ratio, region_stats),
        }

        return warning_data

    def _get_warning_message(self, usage_ratio, region_stats):
        """Ogohlantirish xabarini yaratish"""
        if usage_ratio >= 1.0:
            return f"⚠️ DIQQAT: {self.region.name} hududida oylik chiqindi limitsi ({region_stats['limit']} ta) oshib ketdi! Joriy holat: {region_stats['total_scans']} ta paket skanerlandi."
        elif usage_ratio >= 0.9:
            return f"🔴 OGOHLANTRISH: {self.region.name} hududida oylik limit 90% ga yetdi! Qolgan: {region_stats['remaining']} ta paket."
        elif usage_ratio >= 0.8:
            return f"🟡 ESLATMA: {self.region.name} hududida oylik limit 80% ga yetdi! Qolgan: {region_stats['remaining']} ta paket."
        else:
            return ""

    # @property
    # def total_ecopackets(self):
    #     """Uy a'zolari tomonidan skanerlanish umumiy ecopaketlar soni"""
    #     from apps.ecopacket.models import EcoPacketQrCode

    #     return EcoPacketQrCode.objects.filter(
    #         user__home=self, user__is_active=True
    #     ).count()


class HomeMembership(models.Model):
    """Uy a'zoligi ma'lumotlari"""

    home = models.ForeignKey(Home, on_delete=models.CASCADE, related_name="memberships")
    user = models.OneToOneField(
        "account.User", on_delete=models.CASCADE, related_name="home_membership"
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False, help_text="Uy admin huquqlari")

    class Meta:
        verbose_name = "Uy a'zoligi"
        verbose_name_plural = "Uy a'zoliklari"
        unique_together = ["home", "user"]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.home.name}"


class WasteMonthlyReport(models.Model):
    """Oylik chiqindi hisoboti"""

    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name="monthly_reports",
        verbose_name="Hudud",
    )
    year = models.PositiveIntegerField(verbose_name="Yil")
    month = models.PositiveIntegerField(verbose_name="Oy")
    total_scans = models.PositiveIntegerField(
        default=0, verbose_name="Jami skanerlangan paketlar"
    )
    total_homes = models.PositiveIntegerField(default=0, verbose_name="Jami uylar soni")
    total_members = models.PositiveIntegerField(
        default=0, verbose_name="Jami a'zolar soni"
    )
    limit_exceeded = models.BooleanField(
        default=False, verbose_name="Limit oshirilganmi"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Oylik hisobot"
        verbose_name_plural = "Oylik hisobotlar"
        unique_together = ["region", "year", "month"]
        ordering = ["-year", "-month"]

    def __str__(self):
        return f"{self.region.name} - {self.year}/{self.month:02d}"

    @classmethod
    def generate_monthly_report(cls, region, year=None, month=None):
        """Oylik hisobotni avtomatik yaratish"""
        if not year:
            year = timezone.now().year
        if not month:
            month = timezone.now().month

        stats = region.get_monthly_waste_statistics(year, month)

        report, created = cls.objects.get_or_create(
            region=region,
            year=year,
            month=month,
            defaults={
                "total_scans": stats["total_scans"],
                "total_homes": region.total_homes,
                "total_members": region.total_active_members,
                "limit_exceeded": stats["is_exceeded"],
            },
        )

        if not created:
            # Mavjud hisobotni yangilash
            report.total_scans = stats["total_scans"]
            report.total_homes = region.total_homes
            report.total_members = region.total_active_members
            report.limit_exceeded = stats["is_exceeded"]
            report.save()

        return report
