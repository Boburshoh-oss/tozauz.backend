# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin
# Register your models here.


class MyUserAdmin(UserAdmin):
    list_display = ('phone_number', 'first_name', 'last_name',
                    'role', 'car_number', 'is_active', 'is_admin')
    list_filter = ('is_admin', 'is_active', 'role')
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_admin',
         'is_active', 'role', 'categories', 'car_number')}),
        ('OTP Info', {'fields': ('otp', 'otp_created_at')}),
        ('Important Dates', {'fields': ('last_login',)})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'password1', 'password2', 'first_name', 'last_name', 'role', 'categories', 'car_number')}
         ),
    )
    search_fields = ('phone_number',)
    ordering = ('phone_number',)
    filter_horizontal = ('categories',)


# Register your models here.
admin.site.register(User, MyUserAdmin)


