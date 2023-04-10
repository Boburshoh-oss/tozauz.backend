from rest_framework import serializers
from .models import Earning, BankAccount, PayOut
from account.serializers import UserAdminRetrieveSerializer

    
class EarningSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    class Meta:
        model = Earning
        fields = "__all__"


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
