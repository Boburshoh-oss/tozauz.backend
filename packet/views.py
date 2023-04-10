from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from utils.save_to_database import create_packet_qr_codes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import authentication
from django.utils import timezone
from .models import Packet, Category
from bank.models import Earning
from ecopacket.models import Box, LifeCycle
from rest_framework import viewsets, generics
from .serializers import CategorySerializer, PacketSerializer, PacketSerializerCreate
from utils.pagination import MyPagination
from django_filters import rest_framework as filters
from rest_framework import filters as rf_filters



@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def create_packet_qr_code(request):
    try:
        num_of_qrcodes = int(request.data['num_of_qrcodes'])
    except (KeyError, TypeError, ValueError):
        return Response({'error': 'Invalid input'})
    category = request.data['category']

    if num_of_qrcodes <= 0 or num_of_qrcodes > 10000:
        return Response({'error': 'Number of QR codes must be between 1 and 10,000'})

    qrcodes = create_packet_qr_codes(num_of_qrcodes, category)
    
    if qrcodes:
        serializer = PacketSerializerCreate(qrcodes,many=True)
        return Response({'success': f'{num_of_qrcodes} QR codes created', 'qr_codes': serializer.data})
    else:
        return Response({'error': 'QR code creation failed'})


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
                LifeCycle.objects.create(
                    box=box
                )
                money = box.category.summa * filled/100

                bank_account.capital += money
                bank_account.save()

                Earning.objects.create(
                    bank_account=bank_account,
                    amount=money,
                    tarrif=cat,
                    box=box,
                    
                )
            else:
                return Response({'message': "The box is empty or your level is not suitable"},
                                status=status.HTTP_403_FORBIDDEN)
        # for simple packets
        elif packet_qr_code.first() is not None:
            packet = packet_qr_code.first()
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
                    tarrif=cat,
                    packet = packet
                )

        # Return a success response
        return Response({'message': "Okay"}, status=status.HTTP_202_ACCEPTED)


class CategoryModelViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all().order_by('id')


class PacketListAPIView(generics.ListAPIView):
    pagination_class = MyPagination
    serializer_class = PacketSerializer
    queryset = Packet.objects.all().order_by('-id')
    filter_backends = [filters.DjangoFilterBackend, rf_filters.SearchFilter]
    filterset_fields = ['scannered_at', 'employee', 'life_cycle','category']
    search_fields = ['employee']