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

class AgentBoxSerializer(serializers.ModelSerializer):
    class CategoryForAgentBoxSerializer(serializers.ModelSerializer):
        class Meta:
            model = Category
            fields = "__all__"
    category = CategoryForAgentBoxSerializer()
    class Meta:
        model = Box
        fields = "__all__"

class BoxSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    qr_code = serializers.CharField(read_only=True)

    class Meta:
        model = Box
        fields = "__all__"


class LifeCycleSerializer(serializers.ModelSerializer):
    employee = UserEarningSerializer()

    class Meta:
        model = LifeCycle
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if 'location' in representation:
            representation['location'] = representation['location'].replace('(', '').replace(')', '')
        return representation

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
