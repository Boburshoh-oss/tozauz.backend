from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from apps.utils.save_to_database import create_packet_qr_codes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import authentication
from django.utils import timezone
from .models import Packet, Category
from apps.bank.models import Earning
from apps.ecopacket.models import Box, LifeCycle
from rest_framework import viewsets, generics
from .serializers import (
    CategorySerializer,
    PacketSerializer,
    PacketSerializerCreate,
    PacketGarbageSerializer,
)
from apps.account.serializers import UserEarningSerializer
from apps.utils.pagination import MyPagination
from django_filters import rest_framework as filters
from rest_framework import filters as rf_filters
from rest_framework.pagination import LimitOffsetPagination
from django.db import connection, reset_queries

reset_queries()


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdminUser])
def create_packet_qr_code(request):
    try:
        num_of_qrcodes = int(request.data["num_of_qrcodes"])
    except (KeyError, TypeError, ValueError):
        return Response({"error": "Invalid input"})
    category = request.data["category"]

    if num_of_qrcodes <= 0 or num_of_qrcodes > 10000:
        return Response({"error": "Number of QR codes must be between 1 and 10,000"})

    qrcodes = create_packet_qr_codes(num_of_qrcodes, category)

    if qrcodes:
        serializer = PacketSerializerCreate(qrcodes, many=True)
        return Response(
            {
                "success": f"{num_of_qrcodes} QR codes created",
                "qr_codes": serializer.data,
            }
        )
    else:
        return Response({"error": "QR code creation failed"})


class EmployeeQrCodeScanerView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        # Extract the data from the request
        qr_code = request.data["qr_code"]
        employer = request.user
        box_qr_code = Box.objects.filter(qr_code=qr_code)
        packet_qr_code = Packet.objects.filter(qr_code=qr_code)
        bank_account = employer.bankaccount
        # for ecopacket box
        if box_qr_code.first() is not None:
            box = box_qr_code.first()
            last_lifecycle = box.lifecycle.last()
            filled = last_lifecycle.state
            cat = box.category

            if filled > 80 and cat in employer.categories.all():
                last_lifecycle.employee = employer
                last_lifecycle.filled_at = timezone.now()
                last_lifecycle.save()
                LifeCycle.objects.create(box=box)
                money = box.category.summa * filled / 100

                bank_account.capital += money
                bank_account.save()

                Earning.objects.create(
                    bank_account=bank_account,
                    amount=money,
                    tarrif=cat.name,
                    box=box,
                )
                return Response(
                    {"message": "box successfully scaned"},
                    status=status.HTTP_202_ACCEPTED,
                )

            return Response(
                {"message": "The box is empty or your level is not suitable"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # for simple packets
        elif packet_qr_code.first() is not None:
            packet = packet_qr_code.first()
            user = packet.employee
            cat = packet.category
            if packet.scannered_at is None and cat in employer.categories.all():
                packet.employee = employer
                packet.scannered_at = timezone.now()
                packet.save()

                money = packet.category.summa
                bank_account.capital += money
                bank_account.save()

                Earning.objects.create(
                    bank_account=bank_account,
                    amount=money,
                    tarrif=cat.name,
                    packet=packet,
                )
                return Response(
                    {"message": "packet successfully scaned"},
                    status=status.HTTP_202_ACCEPTED,
                )
            elif cat not in employer.categories.all():
                return Response(
                    {
                        "message": "Sizning rolingiz packet uchun to'g'ri kelmaydi! Iltimos adminlarga murojat qiling!"
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
            serializer = UserEarningSerializer(user)
            return Response(
                {
                    "message": "paket allaqachon skanerlangan!",
                    "user": serializer.data,
                    "scannered_date": packet.scannered_at,
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        # Return a success response
        return Response(
            {"message": "Packet or Box doesn't exists"},
            status=status.HTTP_404_NOT_FOUND,
        )


class CategoryModelViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all().order_by("id")
    filter_backends = [filters.DjangoFilterBackend, rf_filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["filter_type", "ignore_agent"]
    


class PacketListAPIView(generics.ListAPIView):
    pagination_class = MyPagination
    serializer_class = PacketSerializer
    queryset = (
        Packet.objects.all()
        .exclude(scannered_at__isnull=True)
        .only("scannered_at")
        .order_by("-scannered_at")
    )
    filter_backends = [filters.DjangoFilterBackend, rf_filters.SearchFilter]
    filterset_fields = ["category"]
    search_fields = [
        "employee__first_name",
        'qr_code',
        "employee__phone_number",
        "employee__car_number",
    ]


class ListOrBulkDeletePacket(APIView, LimitOffsetPagination):
    def get(self, request, *args, **kwargs):
        date = request.query_params.get("date", None)
        queryset = (
            Packet.objects.filter(scannered_at__isnull=True)
            .filter(created_at__lte=date)
            .only("category", "created_at")
        )
        paginator = MyPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = PacketGarbageSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def delete(self, request, *args, **kwargs):
        date = request.query_params.get("date", None)
        queryset = Packet.objects.filter(scannered_at__isnull=True).filter(
            created_at__lte=date
        )
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
