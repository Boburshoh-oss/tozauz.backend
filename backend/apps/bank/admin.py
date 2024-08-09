from django.contrib import admin
from .models import BankAccount, Earning, PayOut, PayMe
# Register your models here.
@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    search_fields = ["user__phone_number","user__first_name","user__last_name"]
    ordering = ["id"]
@admin.register(Earning)
class EarningAdmin(admin.ModelAdmin):
    list_display = ["amount", "penalty_amount"]
    list_filter = ["tarrif","box","is_penalty"]
    raw_id_fields = ["packet"]
admin.site.register(PayOut)
admin.site.register(PayMe)
