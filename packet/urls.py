from django.urls import path
from .views import create_packet_qr_code, EmployeeQrCodeScanerView

urlpatterns = [
    path('create-packet-qr-codes/', create_packet_qr_code,
         name='create_packet_qr_codes'),
    path('employee-qr-code-scan/', EmployeeQrCodeScanerView.as_view())
]
