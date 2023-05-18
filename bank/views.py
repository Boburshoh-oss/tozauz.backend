from rest_framework import generics, response, authentication, permissions
from django.db.models import Count
from rest_framework.views import APIView
from django.utils import timezone
from .serializers import (
    BankAccountSerializer,
    EarningSerializer,
    EarningListSerializer,
    MobileEarningListSerializer,
    PayOutSerializer,
    PayMeSerializer,
    PayMeListSerializer,
    PayMePayedSerializer,
)
from .models import BankAccount, Earning, PayOut, PayMe
from bank.models import BankAccount
from utils.pagination import MyPagination
from rest_framework.pagination import LimitOffsetPagination
from django.db.models import Sum
from django_filters import rest_framework as filters
from rest_framework import filters as rf_filters
from rest_framework.views import APIView


class BankAccountListAPIView(generics.ListAPIView):
    serializer_class = BankAccountSerializer
    queryset = BankAccount.objects.all()
    pagination_class = MyPagination


class AdminBankAccountAPIView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id, format=None):
        try:
            bank_account = BankAccount.objects.get(user=user_id)
        except:
            return response.Response({"error": "Bank accaount not found"})

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
            response.Response({"error": "user not found"})

        serializer = BankAccountSerializer(bank_account)
        return response.Response(serializer.data)


class EarningUserAPIView(APIView, LimitOffsetPagination):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, format=None):
        earning_list = Earning.objects.filter(bank_account__user=pk).order_by("-id")
        summa = earning_list.aggregate(Sum("amount"))
        paginator = MyPagination()
        result_page = paginator.paginate_queryset(earning_list, request)
        serializer = EarningSerializer(result_page, many=True)
        res = paginator.get_paginated_response(serializer.data)
        res.data.update(summa)
        return res


class EarningListAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    serializer_class = EarningListSerializer
    queryset = Earning.objects.all().order_by("-id")
    pagination_class = MyPagination
    filter_backends = [filters.DjangoFilterBackend, rf_filters.SearchFilter]
    filterset_fields = ["tarrif", "bank_account__user__role"]
    search_fields = [
        "bank_account__user__first_name",
        "bank_account__user__last_name",
        "bank_account__user__phone_number",
        "box__name",
        "packet__qr_code",
        "box__sim_module",
    ]

    def get_queryset(self):
        # get the start_date and end_date from the request parameters
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")

        queryset = Earning.objects.all().order_by("-id")
        # filter the queryset based on the date range
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date).order_by("-id")

        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date).order_by("-id")

        return queryset

    def get(self, request, *args, **kwargs):
        res = super().get(request, *args, **kwargs)
        summa = self.filter_queryset(self.get_queryset()).aggregate(Sum("amount"))
        res.data.update(summa)
        return res


class MobileEarningListAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MobileEarningListSerializer
    queryset = Earning.objects.all().order_by("-id")
    pagination_class = MyPagination

    def get_queryset(self):
        # get the start_date and end_date from the request parameters
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")

        queryset = Earning.objects.filter(
            bank_account__user=self.request.user
        ).order_by("-id")

        # filter the queryset based on the date range
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date).order_by("-id")

        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date).order_by("-id")

        return queryset

    def get(self, request, *args, **kwargs):
        res = super().get(request, *args, **kwargs)
        total = (
            Earning.objects.filter(bank_account__user=request.user)
            .values("tarrif")
            .annotate(count=Count("tarrif"))
        )
        res.data.update({"total_cat": total})
        return res


class PayOutUserMobileListAPIView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = MyPagination

    def get(self, request, format=None):
        payout_list = PayOut.objects.filter(user=request.user).order_by("-id")
        paginator = MyPagination()
        result_page = paginator.paginate_queryset(payout_list, request)
        serializer = PayOutSerializer(result_page, many=True)
        summa = payout_list.aggregate(Sum("amount"))
        res = paginator.get_paginated_response(serializer.data)
        res.data.update(summa)
        return res


class PayOutListAPIView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = MyPagination

    def get(self, request, pk, format=None):
        payout_list = PayOut.objects.filter(user=pk).order_by("-id")
        paginator = MyPagination()
        result_page = paginator.paginate_queryset(payout_list, request)
        serializer = PayOutSerializer(result_page, many=True)
        summa = payout_list.aggregate(Sum("amount"))
        res = paginator.get_paginated_response(serializer.data)
        res.data.update(summa)
        return res


class PayOutListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = PayOutSerializer
    queryset = PayOut.objects.all().order_by("-id")
    pagination_class = MyPagination

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
            return response.Response({"error": "User doesn't exists!"})
        if bank_account.capital >= money:
            bank_account.capital -= money
            bank_account.save()
            return super().post(request, *args, **kwargs)
        return response.Response(
            {"error": "The user's capital is insufficient. Please try paying less"}
        )


class PayMeCreateAPIView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PayMeSerializer
    queryset = PayMe.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        return super().perform_create(serializer)

    def create(self, request, *args, **kwargs):
        # serializer = PayMeSerializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        user = request.user
        payme = PayMe.objects.filter(user=user).last()
        if payme:
            time_difference = timezone.now() - payme.created_at
            day = time_difference.days
            if day >= 1:
                return super().create(request, *args, **kwargs)
            return response.Response(
                {"message": "Sizning so'rovingiz ko'rib chiqilmoqda..."}, status=200
            )
        return super().create(request, *args, **kwargs)


class PayMeListAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = PayMeListSerializer
    queryset = PayMe.objects.all().order_by("-id")
    pagination_class = MyPagination
    filter_backends = [filters.DjangoFilterBackend, rf_filters.SearchFilter]
    filterset_fields = ["user__role", "user"]
    search_fields = [
        "card",
        "card_name",
        "user__phone_number",
        "user__first_name",
        "user__last_name",
        "car_number",
    ]


class PayMePayedView(generics.UpdateAPIView):
    queryset = PayMe.objects.all()
    serializer_class = PayMePayedSerializer
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.payed == False:
            user_money = instance.user.bankaccount.capital
            payme_money = instance.amount
            if user_money > payme_money:
                PayOut.objects.create(
                    user=instance.user,
                    amount=payme_money,
                    admin=request.user,
                    card=instance.card,
                    card_name=instance.card_name,
                )
                instance.user.bankaccount.capital -= payme_money
                instance.user.bankaccount.save()
                instance.payed = True
                instance.save()

                return super().patch(request, *args, **kwargs)
            return response.Response(
                {"message": "Foydalanuvchi mablag'i yetarli emas!"}, status=200
            )
        return response.Response(
            {"message": "Foydalanuvchi pul o'tib bo'lgan"}, status=200
        )
