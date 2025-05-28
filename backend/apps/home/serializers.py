from rest_framework import serializers
from django.db.models import Count
from django.utils import timezone
from .models import Home, HomeMembership, Region, WasteMonthlyReport
from apps.account.models import User
from apps.ecopacket.models import EcoPacketQrCode


class RegionSerializer(serializers.ModelSerializer):
    """Hudud serializer"""

    total_homes = serializers.ReadOnlyField()
    total_active_members = serializers.ReadOnlyField()
    current_month_stats = serializers.SerializerMethodField()

    class Meta:
        model = Region
        fields = [
            "id",
            "name",
            "code",
            "monthly_waste_limit",
            "description",
            "is_active",
            "total_homes",
            "total_active_members",
            "current_month_stats",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_current_month_stats(self, obj):
        """Joriy oy statistikasini olish"""
        return obj.get_monthly_waste_statistics()


class RegionDetailSerializer(RegionSerializer):
    """Hudud batafsil serializer"""

    homes = serializers.SerializerMethodField()
    monthly_reports = serializers.SerializerMethodField()

    class Meta(RegionSerializer.Meta):
        fields = RegionSerializer.Meta.fields + ["homes", "monthly_reports"]

    def get_homes(self, obj):
        """Hududdagi uylar ro'yxati"""
        homes = obj.homes.filter(is_active=True)[:10]  # Oxirgi 10 ta uy
        return HomeListSerializer(homes, many=True).data

    def get_monthly_reports(self, obj):
        """Oxirgi 6 oylik hisobotlar"""
        reports = obj.monthly_reports.all()[:6]
        return WasteMonthlyReportSerializer(reports, many=True).data


class WasteMonthlyReportSerializer(serializers.ModelSerializer):
    """Oylik chiqindi hisoboti serializer"""

    region_name = serializers.CharField(source="region.name", read_only=True)
    region_limit = serializers.IntegerField(
        source="region.monthly_waste_limit", read_only=True
    )
    usage_percentage = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = WasteMonthlyReport
        fields = [
            "id",
            "region",
            "region_name",
            "region_limit",
            "year",
            "month",
            "total_scans",
            "total_homes",
            "total_members",
            "limit_exceeded",
            "usage_percentage",
            "status",
            "created_at",
        ]

    def get_usage_percentage(self, obj):
        """Foydalanish foizini hisoblash"""
        if obj.region.monthly_waste_limit > 0:
            return round((obj.total_scans / obj.region.monthly_waste_limit) * 100, 2)
        return 0

    def get_status(self, obj):
        """Holat statusini olish"""
        if obj.limit_exceeded:
            return "critical"
        elif obj.total_scans / obj.region.monthly_waste_limit >= 0.8:
            return "warning"
        else:
            return "normal"


class HomeMemberReportSerializer(serializers.Serializer):
    """Uy a'zolari hisoboti serializer"""

    user_id = serializers.IntegerField()
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField(allow_null=True)
    phone_number = serializers.CharField()
    ecopacket_count = serializers.IntegerField()
    monthly_ecopacket_count = serializers.IntegerField()
    joined_at = serializers.DateTimeField()
    is_admin = serializers.BooleanField()


class HomeReportSerializer(serializers.Serializer):
    """Uy hisoboti serializer"""

    home_id = serializers.IntegerField()
    home_name = serializers.CharField()
    region_name = serializers.CharField()
    member_count = serializers.IntegerField()
    total_ecopackets = serializers.IntegerField()
    monthly_ecopackets = serializers.IntegerField()
    region_warning = serializers.DictField()
    members = HomeMemberReportSerializer(many=True)


class HomeListSerializer(serializers.ModelSerializer):
    """Uylar ro'yxati uchun serializer"""

    region_name = serializers.CharField(source="region.name", read_only=True)
    member_count = serializers.ReadOnlyField()
    monthly_waste_count = serializers.SerializerMethodField()
    region_warning_status = serializers.SerializerMethodField()

    class Meta:
        model = Home
        fields = [
            "id",
            "name",
            "region_name",
            "address",
            "member_count",
            "monthly_waste_count",
            "region_warning_status",
            "invitation_code",
            "created_at",
        ]

    def get_monthly_waste_count(self, obj):
        """Oylik chiqindi sonini olish"""
        return obj.get_monthly_waste_count()

    def get_region_warning_status(self, obj):
        """Hudud ogohlantirish holatini olish"""
        warning_data = obj.check_region_limit_warning()
        return {
            "has_warning": warning_data["has_warning"],
            "is_critical": warning_data["is_critical"],
            "message": warning_data["warning_message"],
        }


class HomeSerializer(serializers.ModelSerializer):
    """Asosiy Uy serializer"""

    region_name = serializers.CharField(source="region.name", read_only=True)
    member_count = serializers.ReadOnlyField()
    monthly_waste_count = serializers.SerializerMethodField()
    region_warning = serializers.SerializerMethodField()

    class Meta:
        model = Home
        fields = [
            "id",
            "name",
            "region",
            "region_name",
            "address",
            "description",
            "invitation_code",
            "member_count",
            "monthly_waste_count",
            "region_warning",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["invitation_code", "created_at", "updated_at"]

    def get_monthly_waste_count(self, obj):
        """Oylik chiqindi sonini olish"""
        return obj.get_monthly_waste_count()

    def get_region_warning(self, obj):
        """Hudud ogohlantirishini olish"""
        return obj.check_region_limit_warning()


class HomeCreateSerializer(serializers.ModelSerializer):
    """Uy yaratish uchun serializer"""

    class Meta:
        model = Home
        fields = ["name", "region", "address", "description"]

    def validate_region(self, value):
        """Hudud faol ekanligini tekshirish"""
        if not value.is_active:
            raise serializers.ValidationError("Tanlangan hudud faol emas")
        return value

    def create(self, validated_data):
        user = self.context["request"].user
        home = Home.objects.create(**validated_data, owner=user)

        # Create membership for the creator as admin
        HomeMembership.objects.create(home=home, user=user, is_admin=True)

        return home


class JoinHomeSerializer(serializers.Serializer):
    """Uyga qo'shilish uchun serializer"""

    invitation_code = serializers.CharField(max_length=10)

    def validate_invitation_code(self, value):
        try:
            home = Home.objects.get(invitation_code=value, is_active=True)
        except Home.DoesNotExist:
            raise serializers.ValidationError("Noto'g'ri taklifnoma kodi")

        user = self.context["request"].user
        if HomeMembership.objects.filter(user=user).exists():
            raise serializers.ValidationError("Siz allaqachon biror uyga a'zosiz")

        return value

    def save(self):
        user = self.context["request"].user
        home = Home.objects.get(invitation_code=self.validated_data["invitation_code"])

        membership, created = HomeMembership.objects.get_or_create(
            user=user, defaults={"home": home}
        )

        return membership


class HomeMembershipSerializer(serializers.ModelSerializer):
    """Uy a'zoligi serializer"""

    user_full_name = serializers.CharField(source="user.get_full_name", read_only=True)
    user_phone = serializers.CharField(source="user.phone_number", read_only=True)
    ecopacket_count = serializers.SerializerMethodField()
    monthly_ecopacket_count = serializers.SerializerMethodField()

    class Meta:
        model = HomeMembership
        fields = [
            "id",
            "user_id",
            "user_full_name",
            "user_phone",
            "joined_at",
            "is_admin",
            "ecopacket_count",
            "monthly_ecopacket_count",
        ]

    def get_ecopacket_count(self, obj):
        """Jami ecopaket soni"""
        return EcoPacketQrCode.objects.filter(
            user=obj.user, scannered_at__isnull=False
        ).count()

    def get_monthly_ecopacket_count(self, obj):
        """Oylik ecopaket soni"""
        now = timezone.now()
        return EcoPacketQrCode.objects.filter(
            user=obj.user,
            scannered_at__year=now.year,
            scannered_at__month=now.month,
            scannered_at__isnull=False,
        ).count()


class HomeWarningSerializer(serializers.Serializer):
    """Uy ogohlantirish serializer"""

    home_id = serializers.IntegerField()
    home_name = serializers.CharField()
    region_name = serializers.CharField()
    has_warning = serializers.BooleanField()
    is_critical = serializers.BooleanField()
    region_stats = serializers.DictField()
    home_contribution = serializers.IntegerField()
    home_percentage = serializers.FloatField()
    warning_message = serializers.CharField()
