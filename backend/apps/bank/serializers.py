from rest_framework import serializers
from .models import Earning, BankAccount, PayOut, PayMe, Application
from apps.account.serializers import (
    UserAdminRetrieveSerializer,
    UserEarningSerializer,
    UserLoginSerializer,
)
from apps.packet.serializers import PacketSerializerCreate


class EarningSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Earning
        fields = "__all__"


class EarningListSerializer(serializers.ModelSerializer):
    user = UserEarningSerializer(source="bank_account.user")
    created_at = serializers.DateTimeField(read_only=True)
    packet = PacketSerializerCreate()

    class Meta:
        model = Earning
        fields = "__all__"


# class MobileCategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Category
#         fields = ("id","name")


class MobileEarningListSerializer(serializers.ModelSerializer):
    # tarrif = MobileCategorySerializer()

    class Meta:
        model = Earning
        fields = ("id", "tarrif", "amount", "created_at", "is_penalty", "penalty_amount", "reason")



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


class PayMePayedSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayMe
        fields = ("payed",)


class EarningPenaltySerializer(serializers.ModelSerializer):
    class Meta:
        model = Earning
        fields = ['id', 'is_penalty', 'penalty_amount', 'reason']
        read_only_fields = ['id']
        
class ApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['box', 'amount', 'comment', 'containers_count']
        
class ApplicationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = "__all__"
class ApplicationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['status', 'rejected_reason', 'rejected_by', 'comment', 'containers_count']
        read_only_fields = ['id']
        
class ApplicationRejectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['rejected_reason', 'rejected_by']
        read_only_fields = ['id']
