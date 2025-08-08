from rest_framework import serializers
from apps.ecopacket.models import FlaskQrCode

class FlaskQrCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlaskQrCode
        fields = ['id', 'bar_code', 'category', 'created_at']
        read_only_fields = ['created_at']
