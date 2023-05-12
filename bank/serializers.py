from rest_framework import serializers
from .models import Earning, BankAccount, PayOut, PayMe
from account.serializers import (
    UserAdminRetrieveSerializer,
    UserEarningSerializer,
    UserLoginSerializer,
)
from ecopacket.models import Box
from packet.models import Packet
from packet.models import Category


class EarningSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Earning
        fields = "__all__"


class EarningListSerializer(serializers.ModelSerializer):
    user = UserEarningSerializer(source="bank_account.user")
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Earning
        fields = "__all__"


class MobileCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id","name")


class MobileEarningListSerializer(serializers.ModelSerializer):
    tarrif = MobileCategorySerializer()
    
    
    class Meta:
        model = Earning
        fields = ("id", "tarrif", "amount", "created_at")


class BankAccountSerializer(serializers.ModelSerializer):
    user = UserAdminRetrieveSerializer(read_only=True)

    class Meta:
        model = BankAccount
        fields = "__all__"


class PayOutSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    admin = UserAdminRetrieveSerializer(read_only=True)

    class Meta:
        model = PayOut
        fields = "__all__"


class PayMeSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = PayMe
        fields = "__all__"


class PayMeListSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    user = UserAdminRetrieveSerializer(read_only=True)

    class Meta:
        model = PayMe
        fields = "__all__"
