from django.db import models
from django.db.models import Count

# Create your models here.


class BankAccount(models.Model):
    user = models.OneToOneField("account.user", on_delete=models.CASCADE)
    capital = models.PositiveBigIntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.user.first_name} {self.capital}"


class Earning(models.Model):
    bank_account = models.ForeignKey("bank.BankAccount", on_delete=models.CASCADE)
    amount = models.PositiveBigIntegerField()
    tarrif = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    box = models.ForeignKey(
        "ecopacket.Box", on_delete=models.SET_NULL, null=True, blank=True
    )
    packet = models.ForeignKey(
        "packet.Packet", on_delete=models.SET_NULL, null=True, blank=True
    )
    is_penalty = models.BooleanField(default=False)
    penalty_amount = models.PositiveBigIntegerField(default=0)
    reason = models.TextField(blank=True, default="")

    def __str__(self) -> str:
        return f"{self.bank_account.user} {self.amount} {self.tarrif}"


class PayOut(models.Model):
    user = models.ForeignKey(
        "account.user", on_delete=models.CASCADE, related_name="payout_user"
    )
    amount = models.PositiveBigIntegerField()
    admin = models.ForeignKey(
        "account.user", on_delete=models.CASCADE, related_name="payout_admin"
    )
    card = models.CharField(max_length=16, null=True, blank=True)
    card_name = models.CharField(max_length=55, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user.first_name} {self.amount}"


class PayMe(models.Model):
    user = models.ForeignKey(
        "account.user",
        on_delete=models.CASCADE,
        related_name="payme_user",
        null=True,
        blank=True,
    )
    amount = models.PositiveBigIntegerField()
    card = models.CharField(max_length=16, null=True, blank=True)
    card_name = models.CharField(max_length=55, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    payed = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.user.first_name} {self.amount}"


class ApplicationStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    IN_WAY = "in_way", "In Way"
    DELIVERED = "delivered", "Delivered"


class PaymentType(models.TextChoices):
    BANK_ACCOUNT = "bank_account", "Bank Account"
    INVOICE = "invoice", "Invoice"
    CARD = "card", "Card"


class Application(models.Model):
    agent = models.ForeignKey(
        "account.user",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="application_agent",
    )
    box = models.ForeignKey(
        "ecopacket.box", on_delete=models.SET_NULL, null=True, blank=True
    )
    employee = models.ForeignKey(
        "account.user",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="application_employee",
    )
    amount = models.PositiveBigIntegerField()
    rejected_reason = models.TextField(blank=True, default="")
    rejected_by = models.ForeignKey(
        "account.user",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="application_rejected_by",
    )
    comment = models.TextField(blank=True, default="")
    payment_type = models.CharField(
        max_length=200, choices=PaymentType.choices, default=PaymentType.BANK_ACCOUNT
    )
    containers_count = models.PositiveBigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=200,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.PENDING,
    )

    def __str__(self) -> str:
        return f"{self.agent.first_name} {self.amount}"


class QrCheckLog(models.Model):
    """QR kod tekshirish so'rovlarini saqlash uchun model"""

    qr_code = models.CharField(max_length=255)
    request_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    qr_type = models.CharField(
        max_length=50, null=True, blank=True
    )  # ecopacket, flask, not_found
    exists = models.BooleanField(default=False)
    response_data = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ["-request_time"]
        verbose_name = "QR Check Log"
        verbose_name_plural = "QR Check Logs"

    def __str__(self) -> str:
        return f"{self.qr_code} - {self.request_time}"
