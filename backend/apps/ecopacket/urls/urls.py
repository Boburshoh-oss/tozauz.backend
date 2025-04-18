from django.urls import path, include
from rest_framework import routers
from apps.ecopacket.views import (
    create_ecopacket_qr_code,
    IOTView,
    QrCodeScanerView,
    IOTLocationStateView,
    BoxModelViewSet,
    LifeCycleListAPIView,
    EcoPacketQrCodeListAPIView,
    BoxOrderAPIView,
    IOTManualView,
    IOTManualMultipleView,
    BoxLocationAPIView,
    BoxListView
)


router = routers.DefaultRouter()

router.register(r"box", BoxModelViewSet)

urlpatterns = [
    path("agent/boxes/", BoxListView.as_view()),
    path(
        "create-eco-qr-codes/",
        create_ecopacket_qr_code,
        name="create_ecopacket_qr_codes",
    ),
    path("iot-qr-code-scan/", IOTView.as_view()),
    path("iot-qr-code-manual-scan/", IOTManualView.as_view()),
    path("iot-qr-code-multiple-scan/", IOTManualMultipleView.as_view()),
    path("mobile-qr-code-scan/", QrCodeScanerView.as_view()),
    path("iot-location-state/", IOTLocationStateView.as_view()),
    path("", include(router.urls)),
    path("life-cycle-list/", LifeCycleListAPIView.as_view()),
    path("ecopacket-qr-code/", EcoPacketQrCodeListAPIView.as_view()),
    path("fill-box-order/", BoxOrderAPIView.as_view()),
    path("box-location/",BoxLocationAPIView.as_view())
    # path('box/', BoxModelViewSet.as_view({'get': 'list',
    #                                       'post': 'create',
    #                                       'put': 'update',
    #                                       'patch': 'partial_update'}), name="box-crud")
]
