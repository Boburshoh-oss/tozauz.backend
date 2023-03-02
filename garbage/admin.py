from django.contrib.gis.admin import OSMGeoAdmin
from django.contrib import admin
from .models import Category, Box, BoxFillCycle
# Register your models here.
admin.site.register(Category)


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'qr_code', 'sim_module')


@admin.register(BoxFillCycle)
class BoxFillCycleAdmin(OSMGeoAdmin):
    list_display = ('box', 'start_date', 'fill_date', 'state', 'location')
