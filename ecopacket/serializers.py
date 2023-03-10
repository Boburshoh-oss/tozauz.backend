# from drf_extra_fields.geo_fields import PointField
from rest_framework import serializers
from .models import Box

class BoxSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Box
        fields = '__all__'
