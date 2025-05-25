from rest_framework import serializers
from django.db.models import Count
from .models import Home, HomeMembership
from apps.account.models import User
from apps.ecopacket.models import EcoPacketQrCode


class HomeMemberReportSerializer(serializers.Serializer):
    """Uy a'zolari hisoboti serializer"""

    user_id = serializers.IntegerField()
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField(allow_null=True)
    phone_number = serializers.CharField()
    ecopacket_count = serializers.IntegerField()
    joined_at = serializers.DateTimeField()
    is_admin = serializers.BooleanField()


class HomeReportSerializer(serializers.Serializer):
    """Uy hisoboti serializer"""

    home_id = serializers.IntegerField()
    home_name = serializers.CharField()
    member_count = serializers.IntegerField()
    total_ecopackets = serializers.IntegerField()
    members = HomeMemberReportSerializer(many=True)


class HomeSerializer(serializers.ModelSerializer):
    """Asosiy Uy serializer"""

    member_count = serializers.ReadOnlyField()
    total_ecopackets = serializers.ReadOnlyField()

    class Meta:
        model = Home
        fields = [
            "id",
            "name",
            "address",
            "description",
            "invitation_code",
            "member_count",
            "total_ecopackets",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["invitation_code", "created_at", "updated_at"]


class HomeCreateSerializer(serializers.ModelSerializer):
    """Uy yaratish uchun serializer"""

    class Meta:
        model = Home
        fields = ["name", "address", "description"]

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
        ]

    def get_ecopacket_count(self, obj):
        return EcoPacketQrCode.objects.filter(user=obj.user).count()
