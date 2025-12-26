from rest_framework import serializers
from .models import PaymeCard, PaymeReceipt


class CardCreateSerializer(serializers.Serializer):
    """Serializer for creating a new card"""

    card_number = serializers.CharField(
        min_length=16,
        max_length=16,
        help_text="Card number (16 digits)",
    )
    card_expire = serializers.CharField(
        min_length=4,
        max_length=4,
        help_text="Expiry date MMYY (e.g., 0399)",
    )
    save = serializers.BooleanField(
        default=True,
        help_text="Save card for recurring payments",
    )

    def validate_card_number(self, value):
        """Validate card number is numeric"""
        if not value.isdigit():
            raise serializers.ValidationError("Card number must contain only digits")
        return value

    def validate_card_expire(self, value):
        """Validate expiry format"""
        if not value.isdigit():
            raise serializers.ValidationError("Expiry must be in MMYY format")
        month = int(value[:2])
        if month < 1 or month > 12:
            raise serializers.ValidationError("Invalid month in expiry date")
        return value


class CardVerifyCodeSerializer(serializers.Serializer):
    """Serializer for requesting verification code"""

    card_id = serializers.IntegerField(help_text="PaymeCard ID from database")


class CardVerifySerializer(serializers.Serializer):
    """Serializer for verifying card with SMS code"""

    card_id = serializers.IntegerField(help_text="PaymeCard ID from database")
    code = serializers.CharField(
        min_length=6,
        max_length=6,
        help_text="6-digit SMS verification code",
    )

    def validate_code(self, value):
        """Validate code is numeric"""
        if not value.isdigit():
            raise serializers.ValidationError("Code must contain only digits")
        return value


class CardRemoveSerializer(serializers.Serializer):
    """Serializer for removing a card"""

    card_id = serializers.IntegerField(help_text="PaymeCard ID from database")


class PaymeCardSerializer(serializers.ModelSerializer):
    """Serializer for PaymeCard model"""

    class Meta:
        model = PaymeCard
        fields = [
            "id",
            "card_number",
            "card_expire",
            "is_verified",
            "is_recurrent",
            "is_active",
            "created_at",
        ]
        read_only_fields = fields


class PaymeCardDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for PaymeCard"""

    class Meta:
        model = PaymeCard
        fields = [
            "id",
            "card_number",
            "card_expire",
            "is_verified",
            "is_recurrent",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


# ==================== RECEIPT SERIALIZERS ====================


class ReceiptCreateSerializer(serializers.Serializer):
    """Serializer for creating a payment receipt"""

    amount = serializers.IntegerField(
        min_value=100,
        help_text="Amount in tiyin (1 sum = 100 tiyin)",
    )
    order_id = serializers.CharField(
        max_length=100,
        help_text="Unique order identifier",
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        help_text="Payment description",
    )


class ReceiptPaySerializer(serializers.Serializer):
    """Serializer for paying a receipt"""

    receipt_id = serializers.IntegerField(help_text="PaymeReceipt ID from database")
    card_id = serializers.IntegerField(help_text="PaymeCard ID to use for payment")


class PaymeReceiptSerializer(serializers.ModelSerializer):
    """Serializer for PaymeReceipt model"""

    amount_sum = serializers.SerializerMethodField()
    state_display = serializers.CharField(source="get_state_display", read_only=True)

    class Meta:
        model = PaymeReceipt
        fields = [
            "id",
            "receipt_id",
            "amount",
            "amount_sum",
            "state",
            "state_display",
            "description",
            "order_id",
            "created_at",
        ]
        read_only_fields = fields

    def get_amount_sum(self, obj):
        """Convert tiyin to sum"""
        return obj.amount / 100


class PaymeReceiptDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for PaymeReceipt"""

    amount_sum = serializers.SerializerMethodField()
    state_display = serializers.CharField(source="get_state_display", read_only=True)
    card = PaymeCardSerializer(read_only=True)

    class Meta:
        model = PaymeReceipt
        fields = [
            "id",
            "receipt_id",
            "amount",
            "amount_sum",
            "state",
            "state_display",
            "description",
            "order_id",
            "card",
            "create_time",
            "pay_time",
            "cancel_time",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_amount_sum(self, obj):
        return obj.amount / 100


# ==================== BOX BALANCE TOP-UP SERIALIZERS ====================


class BoxBalanceTopUpSerializer(serializers.Serializer):
    """Serializer for topping up Box fandomat balance"""

    box_id = serializers.IntegerField(help_text="Box ID to top up balance")
    amount = serializers.IntegerField(
        min_value=100,
        help_text="Amount in tiyin (1 sum = 100 tiyin)",
    )
    card_id = serializers.IntegerField(help_text="PaymeCard ID to use for payment")
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        help_text="Payment description",
    )


class BoxBalanceSerializer(serializers.Serializer):
    """Serializer for Box balance info"""

    box_id = serializers.IntegerField()
    box_name = serializers.CharField()
    sim_module = serializers.CharField()
    balance = serializers.DecimalField(max_digits=20, decimal_places=2)
    balance_sum = serializers.SerializerMethodField()

    def get_balance_sum(self, obj):
        return float(obj.get("balance", 0))


class AgentBoxSerializer(serializers.Serializer):
    """Serializer for Agent's Box list with pagination support"""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    sim_module = serializers.CharField(read_only=True)
    address = serializers.CharField(read_only=True)
    balance = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    fandomat = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
