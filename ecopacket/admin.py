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


admin.site.register(EcoPacketQrCode)
