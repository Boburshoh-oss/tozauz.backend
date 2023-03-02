from django.contrib import admin
from .models import User
# Register your models here.


class MyUserAdmin(admin.ModelAdmin):
    readonly_fields = ['password']

    def get_readonly_fields(self, request, obj=None):
        if obj:  # If editing an existing object
            return self.readonly_fields + []
        else:  # If creating a new object
            return self.readonly_fields

admin.site.register(User, MyUserAdmin)
