from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from utils.save_to_database import create_ecopacket_qr_codes
from .models import EcoPacketQrCode, Box, LifeCycle
# from account.models import User
from .serializers import (
    BoxSerializer,
    LifeCycleSerializer,
    EcoPacketQrCodeSerializer
)
from bank.models import Earning
from django.contrib.gis.geos import Point
from utils.pagination import MyPagination


@api_view(['POST'])
# @permission_classes([IsAuthenticated, IsAdminUser])
def create_ecopacket_qr_code(request):
    try:
        num_of_qrcodes = int(request.data['num_of_qrcodes'])
    except (KeyError, TypeError, ValueError):
        return Response({'error': 'Invalid input'})
    category = request.data['category']

    if num_of_qrcodes <= 0 or num_of_qrcodes > 10000:
        return Response({'error': 'Number of QR codes must be between 1 and 10,000'})

    success = create_ecopacket_qr_codes(num_of_qrcodes, category)

    if success:
        return Response({'success': f'{num_of_qrcodes} QR codes created'})
    else:
        return Response({'error': 'QR code creation failed'})


class IOTLocationStateView(APIView):

    def post(self, request):
        # Extract location data from request data
        lat = request.data.get('lat')
        lng = request.data.get('lng')
        sim_module = request.data.get('sim_module')
        state = request.data.get('state')
        
        try:
            box = Box.objects.get(sim_module=sim_module)
        except:
            return Response({'error': "No box found with this sim module"}, status=404)
        
        last_lifecycle = box.lifecycle.last()
        # Create a Point object from location data
        point = Point(float(lng), float(lat))
        # Create a new model instance with the PointField set to the Point object
        last_lifecycle.location=point
        last_lifecycle.state = state
        last_lifecycle.save()
        return Response({'message': "Your data has been saved successfully!"}, status=201)

class IOTView(APIView):

    def post(self, request, format=None):
        qr_code = request.data["qr_code"]
        try:
            ecopacket_qr = EcoPacketQrCode.objects.get(qr_code=qr_code)
        except:
            return Response({'error': 'This qr code was not found or has been used before.'}, status=status.HTTP_404_NOT_FOUND)
        
        if ecopacket_qr.user is None:
            return Response({'error': 'Please! Scan your mobile phone first!'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if ecopacket_qr.scannered_at is not None:
            return Response({'error': 'This Qr code has already been used'}, status=status.HTTP_409_CONFLICT)
        
        ecopacket_qr.scannered_at = timezone.now()
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
            tarrif=ecopakcet_catergory
        )
        # Return a success response
        return Response({'message': 'Qr code was successfully scanned.'}, status=status.HTTP_202_ACCEPTED)


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
            return Response({'error': 'This qr code was not found or has been used before.'}, status=status.HTTP_404_NOT_FOUND)


        # Return a success response
        return Response({'message': 'Qr code was successfully scanned.'}, status=status.HTTP_202_ACCEPTED)



#CRUD DEVELOPER
class BoxModelViewSet(viewsets.ModelViewSet):
    serializer_class = BoxSerializer
    queryset = Box.objects.all()


class LifeCycleListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LifeCycleSerializer
    queryset = LifeCycle.objects.all().order_by('-id')
    pagination_class = MyPagination


class EcoPacketQrCodeListAPIView(generics.ListAPIView):
    # permission_classes = [IsAuthenticated]
    serializer_class = EcoPacketQrCodeSerializer
    queryset = EcoPacketQrCode.objects.all().order_by('-id')
    pagination_class = MyPagination
