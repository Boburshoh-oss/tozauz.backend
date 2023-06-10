from django.utils import timezone
from rest_framework import status
from django_filters import rest_framework as filters
from rest_framework import filters as rf_filters
from rest_framework.views import APIView
from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from utils.save_to_database import create_ecopacket_qr_codes
from .models import EcoPacketQrCode, Box, LifeCycle

from account.models import User
from .serializers import (
    BoxSerializer,
    LifeCycleSerializer,
    EcoPacketQrCodeSerializer,
    EcoPacketQrCodeSerializerCreate,
)
from bank.models import Earning

# from django.contrib.gis.geos import Point
from utils.pagination import MyPagination


@api_view(["POST"])
# @permission_classes([IsAuthenticated, IsAdminUser])
def create_ecopacket_qr_code(request):
    try:
        num_of_qrcodes = int(request.data["num_of_qrcodes"])
    except (KeyError, TypeError, ValueError):
        return Response({"error": "Invalid input"})
    category = request.data["category"]

    if num_of_qrcodes <= 0 or num_of_qrcodes > 10000:
        return Response({"error": "Number of QR codes must be between 1 and 10,000"})

    qr_codes = create_ecopacket_qr_codes(num_of_qrcodes, category)

    if qr_codes:
        serializer = EcoPacketQrCodeSerializerCreate(qr_codes, many=True)
        return Response(
            {
                "success": f"{num_of_qrcodes} QR codes created",
                "qr_codes": serializer.data,
            }
        )
    else:
        return Response({"error": "QR code creation failed"})


class IOTLocationStateView(APIView):
    def post(self, request):
        # Extract location data from request data
        lat = request.data.get("lat", None)
        lng = request.data.get("lng", None)
        sim_module = request.data.get("sim_module")
        state = request.data.get("state")

        try:
            box = Box.objects.get(sim_module=sim_module)
        except:
            return Response({"error": "No box found with this sim module"}, status=404)

        last_lifecycle = box.lifecycle.last()
        if last_lifecycle:
            # Create a Point object from location data
            last_lifecycle.location = f"{float(lng), float(lat)}"
            last_lifecycle.state = state
            last_lifecycle.save()
        else:
            LifeCycle.objects.create(
                box=box, location=f"{float(lng), float(lat)}", state=state
            )
        return Response(
            {"message": "Your data has been saved successfully!"}, status=201
        )

    def get(self, request):
        # Extract location data from request data
        lat = request.GET.get("lat", None)
        lng = request.GET.get("lng", None)
        sim_module = request.GET.get("sim_module")
        state = request.GET.get("state")

        try:
            box = Box.objects.get(sim_module=sim_module)
        except:
            return Response({"error": "No box found with this sim module"}, status=404)

        last_lifecycle = box.lifecycle.last()
        if last_lifecycle:
            # Create a Point object from location data
            last_lifecycle.location = f"{float(lng), float(lat)}"
            last_lifecycle.state = state
            last_lifecycle.save()
        else:
            LifeCycle.objects.create(
                box=box, location=f"{float(lng), float(lat)}", state=state
            )
        return Response(
            {"message": "Your data has been saved successfully!"}, status=201
        )


class IOTView(APIView):
    def post(self, request, format=None):
        qr_code = request.data["qr_code"]
        sim_module = request.data["sim_module"]

        if qr_code is None or sim_module is None:
            return Response(
                {
                    "error": "Please send me scannered qr code via"
                    "mobile phone send me, or sim module was missed!"
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            ecopacket_qr = EcoPacketQrCode.objects.get(qr_code=qr_code)
            box = Box.objects.get(sim_module=sim_module)
        except:
            return Response(
                {"error": "This qr code was not found or has been used before."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if ecopacket_qr.user is None:
            return Response(
                {
                    "error": "Please! Scan your mobile phone first or use another enpoint!"
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if ecopacket_qr.scannered_at is not None:
            return Response(
                {"error": "This Qr code has already been used"},
                status=status.HTTP_409_CONFLICT,
            )

        last_lifecycle = box.lifecycle.last()

        ecopacket_qr.scannered_at = timezone.now()
        ecopacket_qr.life_cycle = last_lifecycle
        ecopacket_qr.save()

        ecopakcet_money = ecopacket_qr.category.summa
        ecopakcet_catergory = ecopacket_qr.category
        user = ecopacket_qr.user
        bank_account = user.bankaccount
        bank_account.capital += ecopakcet_money
        bank_account.save()

        Earning.objects.create(
            bank_account=bank_account,
            amount=ecopakcet_money,
            tarrif=ecopakcet_catergory.name,
            box=box,
        )
        # Return a success response
        return Response(
            {"message": "Qr code was successfully scanned."},
            status=status.HTTP_202_ACCEPTED,
        )

    def get(self, request, format=None):
        qr_code = request.GET.get("qr_code", None)
        sim_module = request.GET.get("sim_module", None)

        if qr_code is None or sim_module is None:
            return Response(
                {
                    "error": "Please send me scannered qr code via"
                    "mobile phone send me, or sim module was missed!"
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            ecopacket_qr = EcoPacketQrCode.objects.get(qr_code=qr_code)
            box = Box.objects.get(sim_module=sim_module)
        except:
            return Response(
                {"error": "This qr code was not found or has been used before."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if ecopacket_qr.user is None:
            return Response(
                {
                    "error": "Please! Scan your mobile phone first or use another enpoint!"
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if ecopacket_qr.scannered_at is not None:
            return Response(
                {"error": "This Qr code has already been used"},
                status=status.HTTP_409_CONFLICT,
            )

        last_lifecycle = box.lifecycle.last()

        ecopacket_qr.scannered_at = timezone.now()
        ecopacket_qr.life_cycle = last_lifecycle
        ecopacket_qr.save()

        ecopakcet_money = ecopacket_qr.category.summa
        ecopakcet_catergory = ecopacket_qr.category
        user = ecopacket_qr.user
        bank_account = user.bankaccount
        bank_account.capital += ecopakcet_money
        bank_account.save()

        Earning.objects.create(
            bank_account=bank_account,
            amount=ecopakcet_money,
            tarrif=ecopakcet_catergory.name,
            box=box,
        )
        # Return a success response
        return Response(
            {"message": "Qr code was successfully scanned."},
            status=status.HTTP_202_ACCEPTED,
        )


class IOTManualView(APIView):
    def post(self, request, format=None):
        qr_code = request.data["qr_code"]
        sim_module = request.data["sim_module"]
        phone_number = request.data["phone_number"]
        try:
            user = User.objects.get(phone_number=phone_number)
        except:
            return Response(
                {"error": "Phone number doesn't exists!"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if qr_code is None or sim_module is None:
            return Response(
                {
                    "error": "Please send me scannered qr code via"
                    "mobile phone send me, or sim module was missed!"
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            ecopacket_qr = EcoPacketQrCode.objects.get(qr_code=qr_code)
            box = Box.objects.get(sim_module=sim_module)
        except:
            return Response(
                {"error": "This qr code was not found or has been used before."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if ecopacket_qr.user is not None:
            return Response(
                {"error": "Packet already scanned!"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if ecopacket_qr.scannered_at is not None:
            return Response(
                {"error": "This Qr code has already been used"},
                status=status.HTTP_409_CONFLICT,
            )

        last_lifecycle = box.lifecycle.last()

        ecopacket_qr.scannered_at = timezone.now()
        ecopacket_qr.life_cycle = last_lifecycle
        ecopacket_qr.user = user
        ecopacket_qr.save()

        ecopakcet_money = ecopacket_qr.category.summa
        ecopakcet_catergory = ecopacket_qr.category
        # user = ecopacket_qr.user
        bank_account = user.bankaccount
        bank_account.capital += ecopakcet_money
        bank_account.save()

        Earning.objects.create(
            bank_account=bank_account,
            amount=ecopakcet_money,
            tarrif=ecopakcet_catergory.name,
            box=box,
        )
        # Return a success response
        return Response(
            {"message": "Qr code was successfully scanned."},
            status=status.HTTP_202_ACCEPTED,
        )

    def get(self, request, format=None):
        qr_code = request.GET.get("qr_code", None)
        sim_module = request.GET.get("sim_module", None)
        phone_number = request.GET.get("phone_number", None)

        try:
            user = User.objects.get(phone_number=phone_number)
        except:
            return Response(
                {"error": "Phone number doesn't exists!"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if qr_code is None or sim_module is None:
            return Response(
                {
                    "error": "Please send me scannered qr code via"
                    "mobile phone send me, or sim module was missed!"
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            ecopacket_qr = EcoPacketQrCode.objects.get(qr_code=qr_code)
            box = Box.objects.get(sim_module=sim_module)
        except:
            return Response(
                {"error": "This qr code was not found or has been used before."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if ecopacket_qr.user is not None:
            return Response(
                {"error": "Packet already scanned!"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if ecopacket_qr.scannered_at is not None:
            return Response(
                {"error": "This Qr code has already been used"},
                status=status.HTTP_409_CONFLICT,
            )

        last_lifecycle = box.lifecycle.last()

        ecopacket_qr.scannered_at = timezone.now()
        ecopacket_qr.life_cycle = last_lifecycle
        ecopacket_qr.user = user
        ecopacket_qr.save()

        ecopakcet_money = ecopacket_qr.category.summa
        ecopakcet_catergory = ecopacket_qr.category
        # user = ecopacket_qr.user
        bank_account = user.bankaccount
        bank_account.capital += ecopakcet_money
        bank_account.save()

        Earning.objects.create(
            bank_account=bank_account,
            amount=ecopakcet_money,
            tarrif=ecopakcet_catergory.name,
            box=box,
        )
        # Return a success response
        return Response(
            {"message": "Qr code was successfully scanned."},
            status=status.HTTP_202_ACCEPTED,
        )


class IOTManualMultipleView(APIView):
    def post(self, request, format=None):
        qr_codies = request.data["qr_code"]
        sim_module = request.data["sim_module"]
        phone_number = request.data["phone_number"]

        try:
            box = Box.objects.get(sim_module=sim_module)
        except:
            return Response(
                {"error": "Box doesn't exists!"},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            user = User.objects.get(phone_number=phone_number)
        except:
            return Response(
                {"error": "Phone number doesn't exists!"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if qr_codies is None or sim_module is None:
            return Response(
                {
                    "error": "Please send me scannered qr code via"
                    "mobile phone send me, or sim module was missed!"
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        status_qr_code = {"success_qr_code": 0, "error_qr_code": 0}
        for qc in qr_codies:
            try:
                ecopacket_qr = EcoPacketQrCode.objects.get(qr_code=qc)
                if ecopacket_qr.scannered_at is not None:
                    status_qr_code["error_qr_code"] += 1

                else:
                    last_lifecycle = box.lifecycle.last()
                    ecopacket_qr.scannered_at = timezone.now()
                    ecopacket_qr.life_cycle = last_lifecycle
                    ecopacket_qr.user = user
                    ecopacket_qr.save()

                    ecopakcet_money = ecopacket_qr.category.summa
                    ecopakcet_catergory = ecopacket_qr.category
                    # user = ecopacket_qr.user
                    bank_account = user.bankaccount
                    bank_account.capital += ecopakcet_money
                    bank_account.save()

                    Earning.objects.create(
                        bank_account=bank_account,
                        amount=ecopakcet_money,
                        tarrif=ecopakcet_catergory.name,
                        box=box,
                    )
                    status_qr_code["success_qr_code"] += 1
            except:
                status_qr_code["error_qr_code"] += 1

        # Return a success response
        return Response(
            status_qr_code,
            status=status.HTTP_202_ACCEPTED,
        )

    def get(self, request, format=None):
        qr_codies = request.GET.get("qr_code", None)
        sim_module = request.GET.get("sim_module", None)
        phone_number = request.GET.get("phone_number", None)

        try:
            box = Box.objects.get(sim_module=sim_module)
        except:
            return Response(
                {"error": "Box doesn't exists!"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if "+" not in phone_number:
            phone_number = f"+{phone_number}"
        try:
            user = User.objects.get(phone_number=phone_number)
        except:
            return Response(
                {"error": "Phone number doesn't exists!"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if qr_codies is None or sim_module is None:
            return Response(
                {
                    "error": "Please send me scannered qr code via"
                    "mobile phone send me, or sim module was missed!"
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        status_qr_code = {"success_qr_code": 0, "error_qr_code": 0}
        for qc in qr_codies:
            try:
                ecopacket_qr = EcoPacketQrCode.objects.get(qr_code=qc)
                if ecopacket_qr.scannered_at is not None:
                    status_qr_code["error_qr_code"] += 1

                else:
                    last_lifecycle = box.lifecycle.last()
                    ecopacket_qr.scannered_at = timezone.now()
                    ecopacket_qr.life_cycle = last_lifecycle
                    ecopacket_qr.user = user
                    ecopacket_qr.save()

                    ecopakcet_money = ecopacket_qr.category.summa
                    ecopakcet_catergory = ecopacket_qr.category
                    # user = ecopacket_qr.user
                    bank_account = user.bankaccount
                    bank_account.capital += ecopakcet_money
                    bank_account.save()

                    Earning.objects.create(
                        bank_account=bank_account,
                        amount=ecopakcet_money,
                        tarrif=ecopakcet_catergory.name,
                        box=box,
                    )
                    status_qr_code["success_qr_code"] += 1
            except:
                status_qr_code["error_qr_code"] += 1

        # Return a success response
        return Response(
            status_qr_code,
            status=status.HTTP_202_ACCEPTED,
        )


class QrCodeScanerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        # Extract the data from the request
        qr_code = request.data["qr_code"]
        try:
            ecopacket_qr = EcoPacketQrCode.objects.get(qr_code=qr_code)
            if ecopacket_qr.scannered_at is None:
                ecopacket_qr.user = request.user
                ecopacket_qr.save()
        except:
            return Response(
                {"error": "This qr code was not found or has been used before."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Return a success response
        return Response(
            {"message": "Qr code was successfully scanned."},
            status=status.HTTP_202_ACCEPTED,
        )


class BoxOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        # Extract the data from the request
        lifecycle_id = request.data.get("lifecycle_id", None)
        cancel_lifecycle_id = request.data.get("cancel_lifecycle_id", None)

        if lifecycle_id is not None:
            try:
                lifecycle = LifeCycle.objects.get(pk=lifecycle_id)
            except:
                return Response(
                    {"error": "Bunday yashik mavjud emas ilitmos tekshirib ko'ring!"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if lifecycle.filled_at is not None or lifecycle.user is not None:
                return Response(
                    {
                        "error": "Bu yashik allaqachon bo'shatilgan yoki buyurtma qilingan!"
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            lifecycle.employee = request.user
            lifecycle.save()
            serializer = BoxSerializer(lifecycle.box)
            # Return a success response
            return Response(
                {"message": "Buyurtma sizga biriktirildi", "order": serializer.data},
                status=status.HTTP_202_ACCEPTED,
            )

        try:
            lifecycle = LifeCycle.objects.get(pk=cancel_lifecycle_id)
        except:
            return Response(
                {"error": "Bunday yashik mavjud emas ilitmos tekshirib ko'ring!"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if lifecycle.user != request.user:
            return Response(
                {"error": "Siz boshqaning buyurtmasini bekor qilolmaysiz!"},
                status=status.HTTP_403_FORBIDDEN,
            )
        lifecycle.employee = None
        lifecycle.save()
        serializer = BoxSerializer(lifecycle.box)
        # Return a success response
        return Response(
            {"message": "Buyurtma sizdan bekor qilindi", "order": serializer.data},
            status=status.HTTP_202_ACCEPTED,
        )

    def get(self, request):
        orders = LifeCycle.objects.filter(employee=None).filter(state__gte=80)
        ordered = LifeCycle.objects.exclude(employee=None).filter(filled_at=None)
        serializer = LifeCycleSerializer(orders, many=True)
        ordered_serializer = LifeCycleSerializer(ordered, many=True)
        return Response(
            data={"orders": serializer.data, "ordered": ordered_serializer.data},
            status=status.HTTP_200_OK,
        )


# CRUD DEVELOPER


class BoxModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser, IsAuthenticated]
    serializer_class = BoxSerializer
    queryset = Box.objects.all()


class LifeCycleListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LifeCycleSerializer
    queryset = LifeCycle.objects.all().order_by("-id")
    pagination_class = MyPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ["box"]


class EcoPacketQrCodeListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EcoPacketQrCodeSerializer
    queryset = EcoPacketQrCode.objects.exclude(scannered_at__isnull=True).order_by(
        "-id"
    )
    pagination_class = MyPagination
    filter_backends = [filters.DjangoFilterBackend, rf_filters.SearchFilter]
    filterset_fields = ["category"]
    search_fields = [
        "user__first_name",
        "user__last_name",
        "user__phone_number",
        "qr_code",
    ]
