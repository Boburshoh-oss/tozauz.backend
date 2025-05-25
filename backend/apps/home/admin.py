from django.contrib import admin
from .models import Home, HomeMembership


@admin.register(Home)
class HomeAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "owner",
        "member_count",
        # "total_ecopackets",
        "invitation_code",
        "is_active",
        "created_at",
    ]
    list_filter = ["is_active", "created_at"]
    search_fields = [
        "name",
        "invitation_code",
        "owner__first_name",
        "owner__phone_number",
    ]
    readonly_fields = [
        "invitation_code",
        "created_at",
        "updated_at",
        "member_count",
        # "total_ecopackets",
    ]

    fieldsets = (
        (None, {"fields": ("name", "description", "address", "owner", "is_active")}),
        ("Taklifnoma", {"fields": ("invitation_code",)}),
        (
            "Statistika",
            {"fields": ("member_count",), "classes": ("collapse",)},
        ),
        (
            "Vaqt ma'lumotlari",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(HomeMembership)
class HomeMembershipAdmin(admin.ModelAdmin):
    list_display = ["user", "home", "is_admin", "joined_at"]
    list_filter = ["is_admin", "joined_at", "home"]
    search_fields = ["user__first_name", "user__phone_number", "home__name"]
    readonly_fields = ["joined_at"]

    fieldsets = (
        (None, {"fields": ("home", "user", "is_admin")}),
        ("Vaqt ma'lumotlari", {"fields": ("joined_at",), "classes": ("collapse",)}),
    )
