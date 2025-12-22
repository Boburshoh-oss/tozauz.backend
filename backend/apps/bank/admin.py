from django.contrib import admin
from .models import BankAccount, Earning, PayOut, PayMe, QrCheckLog


# Register your models here.
@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    search_fields = ["user__phone_number", "user__first_name", "user__last_name"]
    ordering = ["id"]


@admin.register(Earning)
class EarningAdmin(admin.ModelAdmin):
    list_display = ["amount", "penalty_amount"]
    list_filter = ["tarrif", "box", "is_penalty"]
    raw_id_fields = ["packet"]

@admin.register(QrCheckLog)
class QrCheckLogAdmin(admin.ModelAdmin):
    list_display = ["qr_code", "request_time", "ip_address", "qr_type", "exists"]
    list_filter = ["qr_type", "exists", "request_time"]
    search_fields = ["qr_code", "ip_address", "user_agent"]


admin.site.register(PayOut)
admin.site.register(PayMe)
