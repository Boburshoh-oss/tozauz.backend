from rest_framework import generics, response, authentication, permissions
from rest_framework.views import APIView
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


class AdminBankAccountAPIView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id, format=None):
        
        try:
            bank_account = BankAccount.objects.get(user=user_id)
        except:
            response.Response({"error": "Bank accaount not found"})

        serializer = BankAccountSerializer(bank_account)
        return response.Response(serializer.data)




class MeBankAccountAPIView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        try:
            bank_account = BankAccount.objects.get(user=user)
        except:
            response.Response({"error":"user not found"})
            
        serializer = BankAccountSerializer(bank_account)
        return response.Response(serializer.data)


class EarningListAPIView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request,pk, format=None):
        earning_list = Earning.objects.filter(bank_account__user=pk)
        serializer = EarningSerializer(earning_list,many=True)
        
        return response.Response(serializer.data)


class PayOutListAPIView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, format=None):
        payout_list = PayOut.objects.filter(user=pk)
        serializer = PayOutSerializer(payout_list, many=True)

        return response.Response(serializer.data)

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