from rest_framework import serializers
from .models import Category, Packet


class CategorySerializer(serializers.ModelSerializer):
    count_user = serializers.IntegerField(read_only=True)
    class Meta:
        model = Category
        fields = "__all__"

class PacketSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = Packet
        fields = ("qr_code",)

class PacketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Packet
        fields = "__all__"
