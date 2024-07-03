from django.contrib import admin
from .models import BankAccount, Earning, PayOut, PayMe
# Register your models here.
admin.site.register(BankAccount)
admin.site.register(Earning)
admin.site.register(PayOut)
admin.site.register(PayMe)
