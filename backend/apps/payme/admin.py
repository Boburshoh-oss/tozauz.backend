from django.contrib import admin
from .models import PaymeCard, PaymeReceipt, PaymeTransaction


@admin.register(PaymeCard)
class PaymeCardAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "card_number",
        "card_expire",
        "is_verified",
        "is_recurrent",
        "is_active",
        "created_at",
    ]
    list_filter = ["is_verified", "is_recurrent", "is_active", "created_at"]
    search_fields = ["user__phone_number", "card_number"]
    readonly_fields = ["token", "created_at", "updated_at"]
    ordering = ["-created_at"]


@admin.register(PaymeReceipt)
class PaymeReceiptAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "receipt_id",
        "amount",
        "state",
        "order_id",
        "created_at",
    ]
    list_filter = ["state", "created_at"]
    search_fields = ["user__phone_number", "receipt_id", "order_id"]
    readonly_fields = [
        "receipt_id",
        "create_time",
        "pay_time",
        "cancel_time",
        "created_at",
        "updated_at",
    ]
    ordering = ["-created_at"]


@admin.register(PaymeTransaction)
class PaymeTransactionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "transaction_type",
        "is_success",
        "created_at",
    ]
    list_filter = ["transaction_type", "is_success", "created_at"]
    search_fields = ["user__phone_number", "error_message"]
    readonly_fields = ["request_data", "response_data", "created_at"]
    ordering = ["-created_at"]
