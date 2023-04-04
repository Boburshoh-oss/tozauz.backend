from rest_framework import serializers
from .models import Earning, BankAccount, PayOut


class EarningSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    class Meta:
        model = Earning
        fields = "__all__"


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = "__all__"



class PayOutSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    admin = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = PayOut
        fields = "__all__"
