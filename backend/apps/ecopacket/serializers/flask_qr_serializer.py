from rest_framework import serializers
from apps.ecopacket.models import FlaskQrCode


class FlaskQrCodeSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(read_only=True)

    class Meta:
        model = FlaskQrCode
        fields = ["id", "bar_code", "category", "created_at", "category_name","image"]
        read_only_fields = ["created_at"]
