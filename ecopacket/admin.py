from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from .models import LifeCycle, Box, EcoPacketQrCode
# Register your models here.


@admin.register(LifeCycle)
class BoxFillCycleAdmin(OSMGeoAdmin):
    list_display = ('box', 'location', 'employee',
                    'state', 'started_at', 'filled_at')


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'qr_code', 'sim_module')


class EcoPacketQrCodeAdmin(admin.ModelAdmin):
    # You can also specify read-only fields here
    readonly_fields = ('qr_code', 'created_at', 'scannered_at')
    list_display = ('qr_code', 'created_at', 'user',
                    'life_cycle', 'category', 'scannered_at')

    def get_readonly_fields(self, request, obj=None):
        if obj:  # If the object exists, it's being edited
            # Add your read-only fields here
            return self.readonly_fields
        else:  # If the object is being created, all fields are writable
            return self.readonly_fields


admin.site.register(EcoPacketQrCode, EcoPacketQrCodeAdmin)
