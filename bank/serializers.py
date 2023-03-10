from rest_framework import serializers
from .models import Earning


class EarningSerializer(serializers.ModelSerializer):
    class Meta:
        model = Earning
        fields = "__all__"
