from django.urls import path, include
from .views import (create_packet_qr_code,
                    EmployeeQrCodeScanerView,
                    CategoryModelViewSet,
                    PacketListAPIView
                    )
from rest_framework import routers
router = routers.DefaultRouter()

router.register(r'categories', CategoryModelViewSet)

urlpatterns = [
    path('create-packet-qr-codes/', create_packet_qr_code,
         name='create_packet_qr_codes'),
    path('employee-qr-code-scan/', EmployeeQrCodeScanerView.as_view()),
    path('', include(router.urls)),
    path('packet-list/', PacketListAPIView.as_view())
]
