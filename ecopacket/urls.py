from django.urls import path
from .views import create_ecopacket_qr_code, IOTView, QrCodeScanerView, IOTLocationStateView

urlpatterns = [
    path('create-eco-qr-codes/', create_ecopacket_qr_code,
         name='create_ecopacket_qr_codes'),
    path('iot-qr-code-scan/', IOTView.as_view()),
    path('mobile-qr-code-scan/', QrCodeScanerView.as_view()),
    path('iot-location-state/', IOTLocationStateView.as_view())
]
