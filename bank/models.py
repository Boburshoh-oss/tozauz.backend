from django.db import models

# Create your models here.
class BankAccount(models.Model):
    user = models.OneToOneField("account.user",on_delete=models.CASCADE)
    capital = models.PositiveBigIntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.user.first_name} {self.capital}"

class Earning(models.Model):
    bank_account = models.ForeignKey("bank.BankAccount",on_delete=models.CASCADE)
    amount = models.PositiveBigIntegerField()
    tarrif = models.ForeignKey("packet.Category",on_delete=models.SET_NULL,null=True)
    
    def __str__(self) -> str:
        return f"{self.bank_account.user} {self.amount} {self.tarrif}"

class PayOut(models.Model):
    user = models.ForeignKey("account.user", on_delete=models.CASCADE,related_name="payout_user")
    amount = models.PositiveBigIntegerField()
    admin = models.ForeignKey("account.user", on_delete=models.CASCADE,related_name="payout_admin")

    def __str__(self) -> str:
        return f"{self.user.first_name} {self.amount}"