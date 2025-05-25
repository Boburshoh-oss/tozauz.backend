from django.db import models
from django.core.validators import MinLengthValidator


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
        return self.name

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
        return self.members.filter(is_active=True).count()

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
