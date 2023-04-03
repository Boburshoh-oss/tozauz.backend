# from drf_extra_fields.geo_fields import PointField
from rest_framework import serializers
from .models import Box, LifeCycle, EcoPacketQrCode


class BoxSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    qr_code = serializers.CharField(read_only=True)

    class Meta:
        model = Box
        fields = '__all__'


class LifeCycleSerializer(serializers.ModelSerializer):
    box = BoxSerializer()

    class Meta:
        model = LifeCycle
        fields = '__all__'

class EcoPacketQrCodeSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = EcoPacketQrCode
        fields = ('qr_code',)

class EcoPacketQrCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EcoPacketQrCode
        fields = '__all__'
