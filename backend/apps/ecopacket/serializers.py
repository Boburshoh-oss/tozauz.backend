# from drf_extra_fields.geo_fields import PointField
from rest_framework import serializers
from .models import Box, LifeCycle, EcoPacketQrCode
from apps.account.serializers import UserEarningSerializer
from apps.packet.serializers import CategorySerializer
from apps.packet.models import Category


class BoxEcoPacketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Box
        fields = ("id", "name")


class BoxSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    qr_code = serializers.CharField(read_only=True)

    class Meta:
        model = Box
        fields = (
            "id",
            "name",
            "state",
            "cycle_created_at",
            "sim_module",
            "qr_code",
            "created_at",
            "category",
        )


class LifeCycleSerializer(serializers.ModelSerializer):
    employee = UserEarningSerializer()

    class Meta:
        model = LifeCycle
        fields = "__all__"


class EcoPacketQrCodeSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = EcoPacketQrCode
        fields = ("qr_code",)


class EcoPacketQrCodeSerializer(serializers.ModelSerializer):
    user = UserEarningSerializer()
    box = BoxEcoPacketSerializer()

    class Meta:
        model = EcoPacketQrCode
        fields = "__all__"
