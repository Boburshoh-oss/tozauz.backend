from django.contrib import admin
from .models import Category, Packet

# Register your models here.

admin.site.register(Category)
# admin.site.register(Packet)


class PacketQrCodeAdmin(admin.ModelAdmin):
    # You can also specify read-only fields here
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
