from django.contrib import admin
from .models import BankAccount, Earning, PayOut
# Register your models here.
admin.site.register(BankAccount)
admin.site.register(Earning)
admin.site.register(PayOut)
