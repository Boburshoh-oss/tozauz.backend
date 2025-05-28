from django.contrib import admin
from .models import Category, Packet

# Register your models here.


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "summa", "ignore_agent", "count_user")
    list_filter = ["ignore_agent"]
    search_fields = ["name"]
    list_editable = ["ignore_agent"]

    fieldsets = ((None, {"fields": ("name", "summa", "ignore_agent")}),)


admin.site.register(Category, CategoryAdmin)
# admin.site.register(Packet)


class PacketQrCodeAdmin(admin.ModelAdmin):
    # You can also specify read-only fields here
    search_fields = ["qr_code", "id"]
    list_filter = ["category"]
    readonly_fields = ("created_at", "qr_code", "scannered_at")
    list_display = (
        "category",
        "qr_code",
        "created_at",
        "scannered_at",
        "employee",
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # If the object exists, it's being edited
            # Add your read-only fields here
            return self.readonly_fields
        else:  # If the object is being created, all fields are writable
            return self.readonly_fields


admin.site.register(Packet, PacketQrCodeAdmin)
