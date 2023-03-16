from rest_framework import generics, response
from .serializers import (
    BankAccountSerializer,
    EarningSerializer,
    PayOutSerializer
)
from .models import BankAccount, Earning, PayOut
from bank.models import BankAccount

class BankAccountListAPIView(generics.ListAPIView):
    serializer_class = BankAccountSerializer
    queryset = BankAccount.objects.all()


class EarningListAPIView(generics.ListAPIView):
    serializer_class = EarningSerializer
    queryset = Earning.objects.all()


class PayOutListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PayOutSerializer
    queryset = PayOut.objects.all()

    def perform_create(self, serializer):
        serializer.save(admin=self.request.user)
        return super().perform_create(serializer)
    
    # @transaction.atomic
    def post(self, request, *args, **kwargs):
        employee = request.data["user"]
        money = int(request.data.get("amount"))
        print(employee, money)
        try:
            bank_account = BankAccount.objects.get(user__id=employee)
        except:
            return response.Response({"error":"User doesn't exists!"})
        if bank_account.capital >= money:
            bank_account.capital -= money
            bank_account.save()
            return super().post(request, *args, **kwargs)
        return response.Response({"error":"The user's capital is insufficient. Please try paying less"})