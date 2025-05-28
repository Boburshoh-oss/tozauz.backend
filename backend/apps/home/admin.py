from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Home, HomeMembership, Region, WasteMonthlyReport


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "code",
        "monthly_waste_limit",
        "total_homes",
        "total_active_members",
        "get_current_month_usage",
        "is_active",
        "created_at",
    ]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "code", "description"]
    readonly_fields = [
        "total_homes",
        "total_active_members",
        "created_at",
        "updated_at",
        "get_current_month_statistics",
    ]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "code",
                    "monthly_waste_limit",
                    "description",
                    "is_active",
                )
            },
        ),
        (
            "Statistika",
            {
                "fields": (
                    "total_homes",
                    "total_active_members",
                    "get_current_month_statistics",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Vaqt ma'lumotlari",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_current_month_usage(self, obj):
        """Joriy oylik foydalanish foizini ko'rsatish"""
        stats = obj.get_monthly_waste_statistics()
        usage_percent = stats["usage_percentage"]

        if usage_percent >= 100:
            color = "red"
            icon = "⚠️"
        elif usage_percent >= 80:
            color = "orange"
            icon = "🟡"
        elif usage_percent >= 60:
            color = "blue"
            icon = "🔵"
        else:
            color = "green"
            icon = "✅"

        return format_html(
            '<span style="color: {};">{} {}% ({}/{})</span>',
            color,
            icon,
            usage_percent,
            stats["total_scans"],
            stats["limit"],
        )

    get_current_month_usage.short_description = "Joriy oy foydalanish"

    def get_current_month_statistics(self, obj):
        """Joriy oy statistikasini batafsil ko'rsatish"""
        if obj.pk:
            stats = obj.get_monthly_waste_statistics()
            return format_html(
                """
                <strong>Joriy oy ({}/{}):</strong><br>
                • Jami skanerlangan: {} ta<br>
                • Limit: {} ta<br>
                • Qolgan: {} ta<br>
                • Foiz: {}%<br>
                • Holat: {}
                """,
                stats["month"],
                stats["year"],
                stats["total_scans"],
                stats["limit"],
                stats["remaining"],
                stats["usage_percentage"],
                "❌ Limit oshdi" if stats["is_exceeded"] else "✅ Normal",
            )
        return "-"

    get_current_month_statistics.short_description = "Joriy oy statistikasi"

    actions = ["generate_monthly_reports"]

    def generate_monthly_reports(self, request, queryset):
        """Tanlangan hududlar uchun oylik hisobotlar yaratish"""
        count = 0
        for region in queryset:
            WasteMonthlyReport.generate_monthly_report(region)
            count += 1
        self.message_user(
            request, f"{count} ta hudud uchun oylik hisobotlar yaratildi."
        )

    generate_monthly_reports.short_description = "Oylik hisobotlar yaratish"


@admin.register(Home)
class HomeAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "region",
        "owner",
        "member_count",
        "get_monthly_waste_count_display",
        "get_region_warning_status",
        "invitation_code",
        "is_active",
        "created_at",
    ]
    list_filter = ["is_active", "region", "created_at"]
    search_fields = [
        "name",
        "invitation_code",
        "owner__first_name",
        "owner__phone_number",
        "region__name",
        "region__code",
    ]
    readonly_fields = [
        "invitation_code",
        "created_at",
        "updated_at",
        "member_count",
        "get_monthly_waste_count_display",
        "get_region_warning_details",
    ]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "description",
                    "address",
                    "region",
                    "owner",
                    "is_active",
                )
            },
        ),
        ("Taklifnoma", {"fields": ("invitation_code",)}),
        (
            "Statistika",
            {
                "fields": (
                    "member_count",
                    "get_monthly_waste_count_display",
                    "get_region_warning_details",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Vaqt ma'lumotlari",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_monthly_waste_count_display(self, obj):
        """Uyning oylik chiqindi sonini ko'rsatish"""
        if obj.pk:
            count = obj.get_monthly_waste_count()
            return f"{count} ta paket"
        return "-"

    get_monthly_waste_count_display.short_description = "Oylik chiqindi"

    def get_region_warning_status(self, obj):
        """Hudud ogohlantirishini ko'rsatish"""
        if obj.pk and obj.region:
            warning_data = obj.check_region_limit_warning()
            if warning_data["is_critical"]:
                return format_html('<span style="color: red;">⚠️ KRITIK</span>')
            elif warning_data["has_warning"]:
                return format_html(
                    '<span style="color: orange;">🟡 OGOHLANTIRISH</span>'
                )
            else:
                return format_html('<span style="color: green;">✅ NORMAL</span>')
        return "-"

    get_region_warning_status.short_description = "Hudud holati"

    def get_region_warning_details(self, obj):
        """Hudud ogohlantirishini batafsil ko'rsatish"""
        if obj.pk and obj.region:
            warning_data = obj.check_region_limit_warning()

            status_color = (
                "red"
                if warning_data["is_critical"]
                else "orange" if warning_data["has_warning"] else "green"
            )

            return format_html(
                """
                <div style="border-left: 3px solid {}; padding-left: 10px;">
                    <strong>Hudud: {}</strong><br>
                    • Uy hissasi: {} ta ({}%)<br>
                    • Hudud jami: {}/{} ta<br>
                    • Qolgan: {} ta<br>
                    {}
                </div>
                """,
                status_color,
                obj.region.name,
                warning_data["home_contribution"],
                warning_data["home_percentage"],
                warning_data["region_stats"]["total_scans"],
                warning_data["region_stats"]["limit"],
                warning_data["region_stats"]["remaining"],
                (
                    f"<br><strong style='color: {status_color};'>{warning_data['warning_message']}</strong>"
                    if warning_data["warning_message"]
                    else ""
                ),
            )
        return "-"

    get_region_warning_details.short_description = "Hudud ogohlantirish tafsilotlari"


@admin.register(HomeMembership)
class HomeMembershipAdmin(admin.ModelAdmin):
    list_display = ["user", "home", "get_region", "is_admin", "joined_at"]
    list_filter = ["is_admin", "joined_at", "home__region", "home"]
    search_fields = [
        "user__first_name",
        "user__phone_number",
        "home__name",
        "home__region__name",
    ]
    readonly_fields = ["joined_at"]

    fieldsets = (
        (None, {"fields": ("home", "user", "is_admin")}),
        ("Vaqt ma'lumotlari", {"fields": ("joined_at",), "classes": ("collapse",)}),
    )

    def get_region(self, obj):
        """Uy hududini ko'rsatish"""
        return obj.home.region.name if obj.home and obj.home.region else "-"

    get_region.short_description = "Hudud"


@admin.register(WasteMonthlyReport)
class WasteMonthlyReportAdmin(admin.ModelAdmin):
    list_display = [
        "region",
        "year",
        "month",
        "total_scans",
        "get_limit_info",
        "total_homes",
        "total_members",
        "get_status",
        "created_at",
    ]
    list_filter = ["limit_exceeded", "year", "month", "region"]
    search_fields = ["region__name", "region__code"]
    readonly_fields = ["created_at"]

    fieldsets = (
        (None, {"fields": ("region", "year", "month")}),
        (
            "Statistika",
            {
                "fields": (
                    "total_scans",
                    "total_homes",
                    "total_members",
                    "limit_exceeded",
                )
            },
        ),
        ("Vaqt", {"fields": ("created_at",), "classes": ("collapse",)}),
    )

    def get_limit_info(self, obj):
        """Limit ma'lumotlarini ko'rsatish"""
        limit = obj.region.monthly_waste_limit
        percentage = round((obj.total_scans / limit) * 100, 2) if limit > 0 else 0
        return f"{obj.total_scans}/{limit} ({percentage}%)"

    get_limit_info.short_description = "Limit holati"

    def get_status(self, obj):
        """Hisobot holatini ko'rsatish"""
        if obj.limit_exceeded:
            return format_html('<span style="color: red;">⚠️ LIMIT OSHDI</span>')
        elif obj.total_scans / obj.region.monthly_waste_limit >= 0.8:
            return format_html('<span style="color: orange;">🟡 OGOHLANTIRISH</span>')
        else:
            return format_html('<span style="color: green;">✅ NORMAL</span>')

    get_status.short_description = "Holat"

    actions = ["regenerate_reports"]

    def regenerate_reports(self, request, queryset):
        """Tanlangan hisobotlarni qayta yaratish"""
        count = 0
        for report in queryset:
            WasteMonthlyReport.generate_monthly_report(
                report.region, report.year, report.month
            )
            count += 1
        self.message_user(request, f"{count} ta hisobot qayta yaratildi.")

    regenerate_reports.short_description = "Hisobotlarni qayta yaratish"
