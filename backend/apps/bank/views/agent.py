from rest_framework import generics, permissions
from django.db.models import Sum
from django_filters import rest_framework as filters
from django.db import transaction
from apps.utils.pagination import MyPagination
from django.utils import timezone
from rest_framework import serializers
from ..models import Earning, Application, PaymentType, ApplicationStatus, PayMe, PayOut
from ..serializers import (
    EarningListSerializer,
    ApplicationCreateSerializer,
    ApplicationListSerializer,
    ApplicationUpdateSerializer,
    AgentPayMeSerializer,
    AgentPayOutListSerializer,
)
from ..filters import EarningFilter


# agent earnings list
class AgentEarningListAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EarningListSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = EarningFilter
    pagination_class = MyPagination

    def get_queryset(self):
        # Swagger uchun fake view tekshirish
        if getattr(self, 'swagger_fake_view', False):
            return Earning.objects.none()
        
        queryset = Earning.objects.all().order_by("-created_at")
        return queryset

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        # Calculate total amount for filtered results
        filtered_queryset = self.filter_queryset(self.get_queryset())
        total_amount = filtered_queryset.aggregate(
            total=Sum("amount"), total_penalty=Sum("penalty_amount")
        )

        response.data["total_amount"] = total_amount["total"] or 0
        response.data["total_penalty"] = total_amount["total_penalty"] or 0

        return response


class ApplicationCreateView(generics.CreateAPIView):
    serializer_class = ApplicationCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def perform_create(self, serializer):
        payment_type = serializer.validated_data.get("payment_type")
        amount = serializer.validated_data.get("amount")

        application = serializer.save(agent=self.request.user)

        if payment_type == PaymentType.BANK_ACCOUNT:
            # Balansdan yechib olish
            agent_bank_account = self.request.user.bankaccount
            agent_bank_account.capital -= amount
            agent_bank_account.save()

            # Arizani approved holatiga o'tkazish
            application.status = ApplicationStatus.APPROVED
            application.save()


class AgentApplicationListAPIView(generics.ListAPIView):
    serializer_class = ApplicationListSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = MyPagination
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ["status", "employee", "box", "payment_type"]

    def get_queryset(self):
         # Swagger uchun fake view tekshirish
        if getattr(self, 'swagger_fake_view', False):
            return Application.objects.none()
            
        queryset = Application.objects.filter(agent=self.request.user).order_by(
            "-created_at"
        )
        return queryset

class AgentAdminApplicationListAPIView(generics.ListAPIView):
    serializer_class = ApplicationListSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    pagination_class = MyPagination
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ["status", "employee", "box"]

    def get_queryset(self):
        queryset = Application.objects.all().order_by(
            "-created_at"
        )
        return queryset
    
class AgentApplicationUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = ApplicationUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Application.objects.all()
    lookup_field = 'pk'
    
    
