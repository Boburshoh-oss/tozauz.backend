from django.db import models
from django.conf import settings


class PaymeCard(models.Model):
    """
    User's saved Payme card tokens
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payme_cards",
    )
    token = models.CharField(max_length=500, unique=True)
    card_number = models.CharField(
        max_length=20, help_text="Masked card number (e.g., 860006******6311)"
    )
    card_expire = models.CharField(max_length=10, help_text="Card expiry date (MM/YY)")
    is_verified = models.BooleanField(default=False)
    is_recurrent = models.BooleanField(
        default=False, help_text="Can be used for recurring payments"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Payme Card"
        verbose_name_plural = "Payme Cards"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.phone_number} - {self.card_number}"


class PaymeReceipt(models.Model):
    """
    Payment receipts/transactions
    """

    class ReceiptState(models.IntegerChoices):
        INPUT = 0, "Yaratilgan"
        WAITING = 1, "Kutilmoqda"
        PENDING = 2, "Pending"
        PAID = 4, "To'langan"
        CANCELLED = 50, "Bekor qilingan"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payme_receipts",
    )
    card = models.ForeignKey(
        PaymeCard,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="receipts",
    )
    receipt_id = models.CharField(
        max_length=100, unique=True, help_text="Payme receipt _id"
    )
    amount = models.PositiveBigIntegerField(help_text="Amount in tiyin")
    state = models.IntegerField(
        choices=ReceiptState.choices,
        default=ReceiptState.INPUT,
    )
    description = models.TextField(blank=True, default="")
    order_id = models.CharField(max_length=100, blank=True, null=True)

    create_time = models.BigIntegerField(null=True, blank=True)
    pay_time = models.BigIntegerField(null=True, blank=True)
    cancel_time = models.BigIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Payme Receipt"
        verbose_name_plural = "Payme Receipts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Receipt {self.receipt_id} - {self.amount} tiyin"

    @property
    def amount_in_sum(self):
        """Convert tiyin to sum"""
        return self.amount / 100


class PaymeTransaction(models.Model):
    """
    Track all Payme API transactions for logging/debugging
    """

    class TransactionType(models.TextChoices):
        CARD_CREATE = "card_create", "Card Create"
        CARD_VERIFY = "card_verify", "Card Verify"
        CARD_CHECK = "card_check", "Card Check"
        CARD_REMOVE = "card_remove", "Card Remove"
        RECEIPT_CREATE = "receipt_create", "Receipt Create"
        RECEIPT_PAY = "receipt_pay", "Receipt Pay"
        RECEIPT_CANCEL = "receipt_cancel", "Receipt Cancel"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payme_transactions",
    )
    transaction_type = models.CharField(
        max_length=50,
        choices=TransactionType.choices,
    )
    request_data = models.JSONField(default=dict)
    response_data = models.JSONField(default=dict)
    is_success = models.BooleanField(default=False)
    error_message = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Payme Transaction Log"
        verbose_name_plural = "Payme Transaction Logs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.transaction_type} - {self.created_at}"
