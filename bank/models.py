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

    def __str__(self) -> str:
        return f"{self.user.first_name} {self.amount}"
