import logging
from decimal import Decimal
from rest_framework import status, generics, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import PaymeCard, PaymeReceipt, PaymeTransaction
from .serializers import (
    CardCreateSerializer,
    CardVerifyCodeSerializer,
    CardVerifySerializer,
    CardRemoveSerializer,
    PaymeCardSerializer,
    PaymeCardDetailSerializer,
    ReceiptCreateSerializer,
    ReceiptPaySerializer,
    PaymeReceiptSerializer,
    PaymeReceiptDetailSerializer,
    BoxBalanceTopUpSerializer,
    BoxBalanceSerializer,
    AgentBoxSerializer,
)
from .services import payme_service, PaymeException
from .pagination import PaymePagination
from apps.ecopacket.models import Box
from apps.account.models import RoleOptions

logger = logging.getLogger(__name__)

# Response schemas for Swagger
card_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
        "message": openapi.Schema(type=openapi.TYPE_STRING),
        "card": openapi.Schema(type=openapi.TYPE_OBJECT),
    },
)

error_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
        "error": openapi.Schema(type=openapi.TYPE_STRING),
        "code": openapi.Schema(type=openapi.TYPE_INTEGER),
    },
)


class CardCreateView(APIView):
    """
    Yangi karta token yaratish.
    Karta raqami va amal qilish muddatini kiritib, Payme orqali token oling.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="payme_card_create",
        operation_summary="Yangi karta qo'shish",
        operation_description="Foydalanuvchi kartasini Payme tizimiga qo'shadi va token oladi. SMS tasdiqlash kerak bo'ladi.",
        tags=["Payme - Kartalar"],
        request_body=CardCreateSerializer,
        responses={
            201: openapi.Response("Karta yaratildi", card_response_schema),
            400: openapi.Response("Xatolik", error_response_schema),
        },
    )
    def post(self, request):
        serializer = CardCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        card_number = serializer.validated_data["card_number"]
        card_expire = serializer.validated_data["card_expire"]
        save = serializer.validated_data["save"]

        try:
            # Call Payme API
            result = payme_service.cards_create(
                card_number=card_number,
                card_expire=card_expire,
                save=save,
                customer=request.user.phone_number,
            )

            # Save card to database
            card = PaymeCard.objects.create(
                user=request.user,
                token=result["token"],
                card_number=result["number"],
                card_expire=result["expire"],
                is_verified=result.get("verify", False),
                is_recurrent=result.get("recurrent", False),
            )

            # Log transaction
            PaymeTransaction.objects.create(
                user=request.user,
                transaction_type=PaymeTransaction.TransactionType.CARD_CREATE,
                request_data={"card_number": f"****{card_number[-4:]}"},
                response_data={"card_id": card.id, "number": result["number"]},
                is_success=True,
            )

            return Response(
                {
                    "success": True,
                    "message": "Karta muvaffaqiyatli qo'shildi. SMS tasdiqlash kerak.",
                    "card": PaymeCardSerializer(card).data,
                },
                status=status.HTTP_201_CREATED,
            )

        except PaymeException as e:
            # Log failed transaction
            PaymeTransaction.objects.create(
                user=request.user,
                transaction_type=PaymeTransaction.TransactionType.CARD_CREATE,
                request_data={"card_number": f"****{card_number[-4:]}"},
                response_data={},
                is_success=False,
                error_message=str(e.message),
            )

            return Response(
                {"success": False, "error": e.message, "code": e.code},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CardGetVerifyCodeView(APIView):
    """
    Karta uchun SMS tasdiqlash kodini so'rash.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="payme_card_get_verify_code",
        operation_summary="SMS kod olish",
        operation_description="Kartani tasdiqlash uchun SMS kod yuboradi. Kod karta egasining telefon raqamiga yuboriladi.",
        tags=["Payme - Kartalar"],
        request_body=CardVerifyCodeSerializer,
        responses={
            200: openapi.Response(
                "SMS yuborildi",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                        "phone": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Masked phone number"
                        ),
                        "wait": openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="Kutish vaqti (millisekund)",
                        ),
                    },
                ),
            ),
            400: openapi.Response("Xatolik", error_response_schema),
        },
    )
    def post(self, request):
        serializer = CardVerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        card_id = serializer.validated_data["card_id"]
        card = get_object_or_404(
            PaymeCard, id=card_id, user=request.user, is_active=True
        )

        try:
            result = payme_service.cards_get_verify_code(card.token)

            return Response(
                {
                    "success": True,
                    "message": f"SMS kod {result.get('phone', '')} raqamiga yuborildi",
                    "phone": result.get("phone"),
                    "wait": result.get("wait"),
                }
            )

        except PaymeException as e:
            return Response(
                {"success": False, "error": e.message, "code": e.code},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CardVerifyView(APIView):
    """
    Kartani SMS kod orqali tasdiqlash.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="payme_card_verify",
        operation_summary="Kartani tasdiqlash",
        operation_description="SMS orqali olingan 6 xonali kod bilan kartani tasdiqlaydi.",
        tags=["Payme - Kartalar"],
        request_body=CardVerifySerializer,
        responses={
            200: openapi.Response("Karta tasdiqlandi", card_response_schema),
            400: openapi.Response("Xatolik", error_response_schema),
        },
    )
    def post(self, request):
        serializer = CardVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        card_id = serializer.validated_data["card_id"]
        code = serializer.validated_data["code"]
        card = get_object_or_404(
            PaymeCard, id=card_id, user=request.user, is_active=True
        )

        try:
            result = payme_service.cards_verify(card.token, code)

            # Update card with new token and verified status
            card.token = result.get("token", card.token)
            card.is_verified = result.get("verify", True)
            card.is_recurrent = result.get("recurrent", card.is_recurrent)
            card.save()

            # Log transaction
            PaymeTransaction.objects.create(
                user=request.user,
                transaction_type=PaymeTransaction.TransactionType.CARD_VERIFY,
                request_data={"card_id": card.id},
                response_data={"verified": True},
                is_success=True,
            )

            return Response(
                {
                    "success": True,
                    "message": "Karta muvaffaqiyatli tasdiqlandi",
                    "card": PaymeCardSerializer(card).data,
                }
            )

        except PaymeException as e:
            PaymeTransaction.objects.create(
                user=request.user,
                transaction_type=PaymeTransaction.TransactionType.CARD_VERIFY,
                request_data={"card_id": card.id},
                response_data={},
                is_success=False,
                error_message=str(e.message),
            )

            return Response(
                {"success": False, "error": e.message, "code": e.code},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CardCheckView(APIView):
    """
    Karta holatini tekshirish.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="payme_card_check",
        operation_summary="Karta holatini tekshirish",
        operation_description="Kartaning hozirgi holatini (tasdiqlangan/tasdiqlanmagan) tekshiradi.",
        tags=["Payme - Kartalar"],
        request_body=CardVerifyCodeSerializer,
        responses={
            200: openapi.Response("Karta holati", card_response_schema),
            400: openapi.Response("Xatolik", error_response_schema),
        },
    )
    def post(self, request):
        serializer = CardVerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        card_id = serializer.validated_data["card_id"]
        card = get_object_or_404(
            PaymeCard, id=card_id, user=request.user, is_active=True
        )

        try:
            result = payme_service.cards_check(card.token)

            # Update card info
            card.is_verified = result.get("verify", card.is_verified)
            card.is_recurrent = result.get("recurrent", card.is_recurrent)
            card.save()

            return Response(
                {
                    "success": True,
                    "card": PaymeCardSerializer(card).data,
                }
            )

        except PaymeException as e:
            return Response(
                {"success": False, "error": e.message, "code": e.code},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CardRemoveView(APIView):
    """
    Kartani o'chirish.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="payme_card_remove",
        operation_summary="Kartani o'chirish",
        operation_description="Foydalanuvchi kartasini Payme tizimidan va ma'lumotlar bazasidan o'chiradi.",
        tags=["Payme - Kartalar"],
        request_body=CardRemoveSerializer,
        responses={
            200: openapi.Response(
                "Karta o'chirildi",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            400: openapi.Response("Xatolik", error_response_schema),
        },
    )
    def post(self, request):
        serializer = CardRemoveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        card_id = serializer.validated_data["card_id"]
        card = get_object_or_404(
            PaymeCard, id=card_id, user=request.user, is_active=True
        )

        try:
            result = payme_service.cards_remove(card.token)

            if result:
                # Mark card as inactive
                card.is_active = False
                card.save()

                # Log transaction
                PaymeTransaction.objects.create(
                    user=request.user,
                    transaction_type=PaymeTransaction.TransactionType.CARD_REMOVE,
                    request_data={"card_id": card.id},
                    response_data={"removed": True},
                    is_success=True,
                )

                return Response(
                    {
                        "success": True,
                        "message": "Karta muvaffaqiyatli o'chirildi",
                    }
                )

            return Response(
                {"success": False, "error": "Kartani o'chirib bo'lmadi"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except PaymeException as e:
            PaymeTransaction.objects.create(
                user=request.user,
                transaction_type=PaymeTransaction.TransactionType.CARD_REMOVE,
                request_data={"card_id": card.id},
                response_data={},
                is_success=False,
                error_message=str(e.message),
            )

            return Response(
                {"success": False, "error": e.message, "code": e.code},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CardListView(generics.ListAPIView):
    """
    Foydalanuvchi kartalarini ro'yxatini olish.
    Pagination, filtering va ordering qo'llab-quvvatlanadi.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = PaymeCardSerializer
    pagination_class = PaymePagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["is_verified", "is_recurrent"]
    search_fields = ["card_number"]
    ordering_fields = ["created_at", "card_number", "is_verified"]
    ordering = ["-created_at"]

    @swagger_auto_schema(
        operation_id="payme_card_list",
        operation_summary="Kartalar ro'yxati",
        operation_description="""
        Foydalanuvchining barcha faol kartalarini qaytaradi.
        
        **Pagination parametrlari:**
        - `page` - Sahifa raqami (default: 1)
        - `page_size` - Har sahifadagi elementlar soni (default: 10, max: 100)
        
        **Filter parametrlari:**
        - `is_verified` - Tasdiqlangan kartalar (true/false)
        - `is_recurrent` - Takroriy to'lov uchun kartalar (true/false)
        
        **Search:**
        - `search` - Karta raqami bo'yicha qidirish
        
        **Ordering:**
        - `ordering` - Saralash (created_at, -created_at, card_number, is_verified)
        """,
        tags=["Payme - Kartalar"],
        manual_parameters=[
            openapi.Parameter(
                "page",
                openapi.IN_QUERY,
                description="Sahifa raqami",
                type=openapi.TYPE_INTEGER,
                default=1,
            ),
            openapi.Parameter(
                "page_size",
                openapi.IN_QUERY,
                description="Har sahifadagi elementlar soni",
                type=openapi.TYPE_INTEGER,
                default=10,
            ),
            openapi.Parameter(
                "is_verified",
                openapi.IN_QUERY,
                description="Tasdiqlangan kartalar",
                type=openapi.TYPE_BOOLEAN,
            ),
            openapi.Parameter(
                "is_recurrent",
                openapi.IN_QUERY,
                description="Takroriy to'lov uchun kartalar",
                type=openapi.TYPE_BOOLEAN,
            ),
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="Karta raqami bo'yicha qidirish",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "ordering",
                openapi.IN_QUERY,
                description="Saralash (created_at, -created_at)",
                type=openapi.TYPE_STRING,
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return PaymeCard.objects.none()
        return PaymeCard.objects.filter(user=self.request.user, is_active=True)


class CardDetailView(generics.RetrieveAPIView):
    """
    Karta tafsilotlarini olish.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = PaymeCardDetailSerializer

    @swagger_auto_schema(
        operation_id="payme_card_detail",
        operation_summary="Karta tafsilotlari",
        operation_description="Bitta kartaning to'liq ma'lumotlarini qaytaradi.",
        tags=["Payme - Kartalar"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return PaymeCard.objects.none()
        return PaymeCard.objects.filter(user=self.request.user, is_active=True)


# ==================== RECEIPT VIEWS ====================


class ReceiptCreateView(APIView):
    """
    To'lov kvitansiyasi yaratish.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="payme_receipt_create",
        operation_summary="To'lov yaratish",
        operation_description="Yangi to'lov kvitansiyasi yaratadi. Summa tiyinda kiritiladi (1 so'm = 100 tiyin).",
        tags=["Payme - To'lovlar"],
        request_body=ReceiptCreateSerializer,
        responses={
            201: openapi.Response(
                "To'lov yaratildi",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                        "receipt": openapi.Schema(type=openapi.TYPE_OBJECT),
                    },
                ),
            ),
            400: openapi.Response("Xatolik", error_response_schema),
        },
    )
    def post(self, request):
        serializer = ReceiptCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        amount = serializer.validated_data["amount"]
        order_id = serializer.validated_data["order_id"]
        description = serializer.validated_data.get("description", "")

        try:
            result = payme_service.receipts_create(
                amount=amount,
                order_id=order_id,
                description=description,
            )

            # Save receipt to database
            receipt = PaymeReceipt.objects.create(
                user=request.user,
                receipt_id=result["_id"],
                amount=amount,
                state=result.get("state", 0),
                description=description,
                order_id=order_id,
                create_time=result.get("create_time"),
            )

            PaymeTransaction.objects.create(
                user=request.user,
                transaction_type=PaymeTransaction.TransactionType.RECEIPT_CREATE,
                request_data={"amount": amount, "order_id": order_id},
                response_data={"receipt_id": receipt.receipt_id},
                is_success=True,
            )

            return Response(
                {
                    "success": True,
                    "message": "To'lov kvitansiyasi yaratildi",
                    "receipt": PaymeReceiptSerializer(receipt).data,
                },
                status=status.HTTP_201_CREATED,
            )

        except PaymeException as e:
            PaymeTransaction.objects.create(
                user=request.user,
                transaction_type=PaymeTransaction.TransactionType.RECEIPT_CREATE,
                request_data={"amount": amount, "order_id": order_id},
                response_data={},
                is_success=False,
                error_message=str(e.message),
            )

            return Response(
                {"success": False, "error": e.message, "code": e.code},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ReceiptPayView(APIView):
    """
    Karta orqali to'lovni amalga oshirish.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="payme_receipt_pay",
        operation_summary="To'lovni amalga oshirish",
        operation_description="Yaratilgan to'lov kvitansiyasini tasdiqlangan karta orqali to'lash.",
        tags=["Payme - To'lovlar"],
        request_body=ReceiptPaySerializer,
        responses={
            200: openapi.Response(
                "To'lov amalga oshirildi",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                        "receipt": openapi.Schema(type=openapi.TYPE_OBJECT),
                    },
                ),
            ),
            400: openapi.Response("Xatolik", error_response_schema),
        },
    )
    def post(self, request):
        serializer = ReceiptPaySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        receipt_id = serializer.validated_data["receipt_id"]
        card_id = serializer.validated_data["card_id"]

        receipt = get_object_or_404(PaymeReceipt, id=receipt_id, user=request.user)
        card = get_object_or_404(
            PaymeCard,
            id=card_id,
            user=request.user,
            is_active=True,
            is_verified=True,
        )

        try:
            result = payme_service.receipts_pay(
                receipt_id=receipt.receipt_id,
                token=card.token,
                payer_phone=request.user.phone_number,
            )

            # Update receipt
            receipt.state = result.get("state", receipt.state)
            receipt.pay_time = result.get("pay_time")
            receipt.card = card
            receipt.save()

            PaymeTransaction.objects.create(
                user=request.user,
                transaction_type=PaymeTransaction.TransactionType.RECEIPT_PAY,
                request_data={"receipt_id": receipt.id, "card_id": card.id},
                response_data={"state": receipt.state},
                is_success=True,
            )

            return Response(
                {
                    "success": True,
                    "message": "To'lov muvaffaqiyatli amalga oshirildi",
                    "receipt": PaymeReceiptSerializer(receipt).data,
                }
            )

        except PaymeException as e:
            PaymeTransaction.objects.create(
                user=request.user,
                transaction_type=PaymeTransaction.TransactionType.RECEIPT_PAY,
                request_data={"receipt_id": receipt.id, "card_id": card.id},
                response_data={},
                is_success=False,
                error_message=str(e.message),
            )

            return Response(
                {"success": False, "error": e.message, "code": e.code},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ReceiptListView(generics.ListAPIView):
    """
    Foydalanuvchi to'lovlari ro'yxatini olish.
    Pagination, filtering va ordering qo'llab-quvvatlanadi.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = PaymeReceiptSerializer
    pagination_class = PaymePagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["state", "order_id"]
    search_fields = ["order_id", "description"]
    ordering_fields = ["created_at", "amount", "state", "pay_time"]
    ordering = ["-created_at"]

    @swagger_auto_schema(
        operation_id="payme_receipt_list",
        operation_summary="To'lovlar ro'yxati",
        operation_description="""
        Foydalanuvchining barcha to'lov kvitansiyalarini qaytaradi.
        
        **Pagination parametrlari:**
        - `page` - Sahifa raqami (default: 1)
        - `page_size` - Har sahifadagi elementlar soni (default: 10, max: 100)
        
        **Filter parametrlari:**
        - `state` - To'lov holati (0=input, 1=waiting, 2=pending, 4=paid, 50=cancelled)
        - `order_id` - Buyurtma ID bo'yicha filter
        
        **Search:**
        - `search` - Buyurtma ID yoki tavsif bo'yicha qidirish
        
        **Ordering:**
        - `ordering` - Saralash (created_at, -created_at, amount, -amount, state, pay_time)
        """,
        tags=["Payme - To'lovlar"],
        manual_parameters=[
            openapi.Parameter(
                "page",
                openapi.IN_QUERY,
                description="Sahifa raqami",
                type=openapi.TYPE_INTEGER,
                default=1,
            ),
            openapi.Parameter(
                "page_size",
                openapi.IN_QUERY,
                description="Har sahifadagi elementlar soni",
                type=openapi.TYPE_INTEGER,
                default=10,
            ),
            openapi.Parameter(
                "state",
                openapi.IN_QUERY,
                description="To'lov holati (0=input, 1=waiting, 2=pending, 4=paid, 50=cancelled)",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "order_id",
                openapi.IN_QUERY,
                description="Buyurtma ID bo'yicha filter",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="Buyurtma ID yoki tavsif bo'yicha qidirish",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "ordering",
                openapi.IN_QUERY,
                description="Saralash (created_at, -created_at, amount, state)",
                type=openapi.TYPE_STRING,
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return PaymeReceipt.objects.none()
        return PaymeReceipt.objects.filter(user=self.request.user)


class ReceiptDetailView(generics.RetrieveAPIView):
    """
    To'lov tafsilotlarini olish.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = PaymeReceiptDetailSerializer

    @swagger_auto_schema(
        operation_id="payme_receipt_detail",
        operation_summary="To'lov tafsilotlari",
        operation_description="Bitta to'lov kvitansiyasining to'liq ma'lumotlarini qaytaradi.",
        tags=["Payme - To'lovlar"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return PaymeReceipt.objects.none()
        return PaymeReceipt.objects.filter(user=self.request.user)


class ReceiptCheckView(APIView):
    """
    To'lov holatini tekshirish.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="payme_receipt_check",
        operation_summary="To'lov holatini tekshirish",
        operation_description="To'lov kvitansiyasining hozirgi holatini tekshiradi (yaratilgan, to'langan, bekor qilingan).",
        tags=["Payme - To'lovlar"],
        responses={
            200: openapi.Response(
                "To'lov holati",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "state": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "state_display": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            400: openapi.Response("Xatolik", error_response_schema),
        },
    )
    def get(self, request, pk):
        receipt = get_object_or_404(PaymeReceipt, id=pk, user=request.user)

        try:
            state = payme_service.receipts_check(receipt.receipt_id)
            receipt.state = state
            receipt.save()

            return Response(
                {
                    "success": True,
                    "state": state,
                    "state_display": receipt.get_state_display(),
                }
            )

        except PaymeException as e:
            return Response(
                {"success": False, "error": e.message, "code": e.code},
                status=status.HTTP_400_BAD_REQUEST,
            )


# ==================== AGENT BOX BALANCE TOP-UP VIEWS ====================


class IsAgent(IsAuthenticated):
    """Permission class for Agent users only"""

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.role == RoleOptions.AGENT


class AgentBoxListView(generics.ListAPIView):
    """
    Agent uchun unga tegishli Box'lar ro'yxatini olish.
    Pagination, filtering va ordering qo'llab-quvvatlanadi.
    """

    permission_classes = [IsAgent]
    serializer_class = AgentBoxSerializer
    pagination_class = PaymePagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["fandomat", "is_active"]
    search_fields = ["name", "sim_module", "address"]
    ordering_fields = ["created_at", "name", "balance"]
    ordering = ["-created_at"]

    @swagger_auto_schema(
        operation_id="agent_box_list",
        operation_summary="Agent Box'lari ro'yxati",
        operation_description="""
        Agentga tegishli barcha fandomat Box'larini va ularning balanslarini qaytaradi.
        
        **Pagination parametrlari:**
        - `page` - Sahifa raqami (default: 1)
        - `page_size` - Har sahifadagi elementlar soni (default: 10, max: 100)
        
        **Filter parametrlari:**
        - `fandomat` - Fandomat turi (true/false)
        - `is_active` - Faol Box'lar (true/false)
        
        **Search:**
        - `search` - Nomi, sim_module yoki manzil bo'yicha qidirish
        
        **Ordering:**
        - `ordering` - Saralash (created_at, -created_at, name, balance)
        """,
        tags=["Payme - Agent Box Balance"],
        manual_parameters=[
            openapi.Parameter(
                "page",
                openapi.IN_QUERY,
                description="Sahifa raqami",
                type=openapi.TYPE_INTEGER,
                default=1,
            ),
            openapi.Parameter(
                "page_size",
                openapi.IN_QUERY,
                description="Har sahifadagi elementlar soni",
                type=openapi.TYPE_INTEGER,
                default=10,
            ),
            openapi.Parameter(
                "fandomat",
                openapi.IN_QUERY,
                description="Fandomat turi",
                type=openapi.TYPE_BOOLEAN,
            ),
            openapi.Parameter(
                "is_active",
                openapi.IN_QUERY,
                description="Faol Box'lar",
                type=openapi.TYPE_BOOLEAN,
            ),
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="Nomi, sim_module yoki manzil bo'yicha qidirish",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "ordering",
                openapi.IN_QUERY,
                description="Saralash (created_at, -created_at, name, balance)",
                type=openapi.TYPE_STRING,
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Box.objects.none()
        return Box.objects.filter(
            seller=self.request.user,  is_active=True
        )


class AgentBoxBalanceTopUpView(APIView):
    """
    Agent uchun Box fandomat balansini to'ldirish.
    """

    permission_classes = [IsAgent]

    @swagger_auto_schema(
        operation_id="agent_box_balance_topup",
        operation_summary="Box balansini to'ldirish",
        operation_description="""
        Agent o'ziga tegishli fandomat Box balansini karta orqali to'ldiradi.
        
        Jarayon:
        1. To'lov kvitansiyasi yaratiladi
        2. Karta orqali to'lov amalga oshiriladi
        3. Muvaffaqiyatli to'lovdan so'ng Box balansi oshiriladi
        
        Summa tiyinda kiritiladi (1 so'm = 100 tiyin).
        """,
        tags=["Payme - Agent Box Balance"],
        request_body=BoxBalanceTopUpSerializer,
        responses={
            200: openapi.Response(
                "Balans to'ldirildi",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                        "box": openapi.Schema(type=openapi.TYPE_OBJECT),
                        "receipt": openapi.Schema(type=openapi.TYPE_OBJECT),
                    },
                ),
            ),
            400: openapi.Response("Xatolik", error_response_schema),
            403: openapi.Response("Ruxsat yo'q"),
        },
    )
    def post(self, request):
        serializer = BoxBalanceTopUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        box_id = serializer.validated_data["box_id"]
        amount = serializer.validated_data["amount"]
        card_id = serializer.validated_data["card_id"]
        description = serializer.validated_data.get("description", "")

        # Get Box - must belong to this agent and be a fandomat
        box = get_object_or_404(
            Box,
            id=box_id,
            seller=request.user,
            fandomat=True,
            is_active=True,
        )

        # Get verified card
        card = get_object_or_404(
            PaymeCard,
            id=card_id,
            user=request.user,
            is_active=True,
            is_verified=True,
        )

        # Generate unique order ID
        import uuid

        order_id = f"box_topup_{box.id}_{uuid.uuid4().hex[:8]}"

        if not description:
            description = f"Fandomat {box.name} balansini to'ldirish"

        try:
            with transaction.atomic():
                # Step 1: Create receipt
                receipt_result = payme_service.receipts_create(
                    amount=amount,
                    order_id=order_id,
                    description=description,
                )

                # Save receipt to database
                receipt = PaymeReceipt.objects.create(
                    user=request.user,
                    receipt_id=receipt_result["_id"],
                    amount=amount,
                    state=receipt_result.get("state", 0),
                    description=description,
                    order_id=order_id,
                    create_time=receipt_result.get("create_time"),
                )

                # Step 2: Pay receipt
                pay_result = payme_service.receipts_pay(
                    receipt_id=receipt.receipt_id,
                    token=card.token,
                    payer_phone=request.user.phone_number,
                )

                # Update receipt
                receipt.state = pay_result.get("state", receipt.state)
                receipt.pay_time = pay_result.get("pay_time")
                receipt.card = card
                receipt.save()

                # Step 3: If payment successful (state=4), update Box balance
                if receipt.state == PaymeReceipt.ReceiptState.PAID:
                    # Convert tiyin to sum (amount is in tiyin, balance is in sum)
                    amount_sum = Decimal(amount) / 100
                    box.balance += amount_sum
                    box.save()

                    # Log successful transaction
                    PaymeTransaction.objects.create(
                        user=request.user,
                        transaction_type=PaymeTransaction.TransactionType.RECEIPT_PAY,
                        request_data={
                            "box_id": box.id,
                            "amount": amount,
                            "card_id": card.id,
                            "action": "box_balance_topup",
                        },
                        response_data={
                            "receipt_id": receipt.receipt_id,
                            "state": receipt.state,
                            "new_balance": float(box.balance),
                        },
                        is_success=True,
                    )

                    return Response(
                        {
                            "success": True,
                            "message": f"Balans muvaffaqiyatli to'ldirildi. Yangi balans: {box.balance} so'm",
                            "box": {
                                "id": box.id,
                                "name": box.name,
                                "sim_module": box.sim_module,
                                "new_balance": float(box.balance),
                            },
                            "receipt": PaymeReceiptSerializer(receipt).data,
                        }
                    )
                else:
                    # Payment not completed
                    return Response(
                        {
                            "success": False,
                            "error": "To'lov amalga oshmadi",
                            "state": receipt.state,
                            "state_display": receipt.get_state_display(),
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

        except PaymeException as e:
            # Log failed transaction
            PaymeTransaction.objects.create(
                user=request.user,
                transaction_type=PaymeTransaction.TransactionType.RECEIPT_PAY,
                request_data={
                    "box_id": box_id,
                    "amount": amount,
                    "card_id": card_id,
                    "action": "box_balance_topup",
                },
                response_data={},
                is_success=False,
                error_message=str(e.message),
            )

            return Response(
                {"success": False, "error": e.message, "code": e.code},
                status=status.HTTP_400_BAD_REQUEST,
            )


class AgentBoxBalanceView(APIView):
    """
    Agent uchun bitta Box balansini ko'rish.
    """

    permission_classes = [IsAgent]

    @swagger_auto_schema(
        operation_id="agent_box_balance_detail",
        operation_summary="Box balansi",
        operation_description="Agentga tegishli bitta fandomat Box balansini qaytaradi.",
        tags=["Payme - Agent Box Balance"],
        responses={
            200: openapi.Response(
                "Box balansi",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "box": openapi.Schema(type=openapi.TYPE_OBJECT),
                    },
                ),
            ),
            404: openapi.Response("Box topilmadi"),
        },
    )
    def get(self, request, pk):
        box = get_object_or_404(
            Box,
            id=pk,
            seller=request.user,
            fandomat=True,
            is_active=True,
        )

        return Response(
            {
                "success": True,
                "box": {
                    "id": box.id,
                    "name": box.name,
                    "sim_module": box.sim_module,
                    "address": box.address,
                    "balance": float(box.balance),
                    "is_fandomat": box.fandomat,
                },
            }
        )
