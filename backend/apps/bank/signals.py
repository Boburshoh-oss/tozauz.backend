from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from apps.account.models import User
from .models import BankAccount, PayOut
from rest_framework import response

@receiver(post_save, sender=User)
def request_to_bank(sender, instance, created, **kwargs):   # type: ignore
    if created:
        BankAccount.objects.get_or_create(user=instance)

                
