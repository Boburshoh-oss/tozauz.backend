from django.urls import path, include
from rest_framework import routers
from .views import (
    create_ecopacket_qr_code,
    IOTView, QrCodeScanerView,
    IOTLocationStateView, BoxModelViewSet,
    LifeCycleListAPIView,
    EcoPacketQrCodeListAPIView
)


router = routers.DefaultRouter()

router.register(r'box', BoxModelViewSet)

urlpatterns = [
    path('create-eco-qr-codes/', create_ecopacket_qr_code,
         name='create_ecopacket_qr_codes'),
    path('iot-qr-code-scan/', IOTView.as_view()),
    path('mobile-qr-code-scan/', QrCodeScanerView.as_view()),
    path('iot-location-state/', IOTLocationStateView.as_view()),
    path('', include(router.urls)),
    path('life-cycle-list/', LifeCycleListAPIView.as_view()),
    path('ecopacket-qr-code/', EcoPacketQrCodeListAPIView.as_view())
    # path('box/', BoxModelViewSet.as_view({'get': 'list',
    #                                       'post': 'create',
    #                                       'put': 'update',
    #                                       'patch': 'partial_update'}), name="box-crud")
]
