from rest_framework import serializers
from .models import Earning, BankAccount, PayOut, PayMe, Application, PaymentType
from apps.ecopacket.models import Box
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


class BoxForAgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Box
        fields = ('id', 'name', 'address', 'location', 'containers_count')

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
        fields = (
            "id",
            "tarrif",
            "amount",
            "created_at",
            "is_penalty",
            "penalty_amount",
            "reason",
        )


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
        fields = ["id", "is_penalty", "penalty_amount", "reason"]
        read_only_fields = ["id"]


class ApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ["box", "comment", "containers_count", "payment_type"]

    def validate(self, data):
        box = data.get("box")
        containers_count = data.get("containers_count")
        payment_type = data.get("payment_type")
        user = self.context["request"].user

        if not box:
            raise serializers.ValidationError("Box is required")

        if containers_count > box.containers_count:
            raise serializers.ValidationError(
                f"Containers count cannot be greater than box capacity ({box.containers_count})"
            )

        # Avtomatik amount hisoblash
        amount = box.unloading_price * containers_count
        data["amount"] = amount

        # Bank account to'lov turi tanlangan bo'lsa tekshiruvlar
        if payment_type == PaymentType.BANK_ACCOUNT:
            agent_bank_account = user.bankaccount
            if not agent_bank_account:
                raise serializers.ValidationError("Agent bank account is required")

            if agent_bank_account.capital < amount:
                raise serializers.ValidationError(
                    f"Insufficient balance. Required: {amount}, Available: {agent_bank_account.capital}"
                )

        return data


class ApplicationListSerializer(serializers.ModelSerializer):
    class BoxForApplicationSerializer(serializers.ModelSerializer):
        class Meta:
            model = Box
            fields = ("id", "name")

    box = BoxForApplicationSerializer()

    class Meta:
        model = Application
        fields = "__all__"


class ApplicationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = [
            "status",
            "rejected_reason",
            "rejected_by",
            "comment",
            "containers_count",
        ]
        read_only_fields = ["id"]


class ApplicationRejectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ["rejected_reason", "rejected_by"]
        read_only_fields = ["id"]


class AgentPayMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayMe
        fields = ["amount", "card", "card_name"]
        read_only_fields = ["payed", "created_at"]


class AgentPayOutListSerializer(serializers.ModelSerializer):
    admin = UserAdminRetrieveSerializer(read_only=True)

    class Meta:
        model = PayOut
        fields = ["id", "amount", "card", "card_name", "created_at", "admin"]
