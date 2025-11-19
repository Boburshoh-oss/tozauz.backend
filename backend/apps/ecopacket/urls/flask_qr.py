from django.urls import path
from ..views.flask_qr_view import (
    FlaskQrManualMultipleView,
    FlaskQrManualSingleView,
    UniversalQrManualSingleView,
    UniversalQrCheckView,
)
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from apps.ecopacket.views.flask_qr_view import (
    FlaskQrManualMultipleView,
    FlaskQrManualSingleView,
    UniversalQrManualSingleView,
    UniversalQrCheckView,
)
from apps.ecopacket.views.flask_qr_viewset import (
    FlaskQrCodeViewSet,
    FlaskQrCodeViewSetV2,
)

router = DefaultRouter()
router.register("flask-qr-codes", FlaskQrCodeViewSet)
router.register("flask-qr-codes-v2", FlaskQrCodeViewSetV2, basename="flask-qr-codes-v2")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "manual/", FlaskQrManualMultipleView.as_view(), name="flask-qr-manual-multiple"
    ),
    path(
        "manual/single/",
        FlaskQrManualSingleView.as_view(),
        name="flask-qr-manual-single",
    ),
    path(
        "universal/", UniversalQrManualSingleView.as_view(), name="universal-qr-manual"
    ),
    path("check/", UniversalQrCheckView.as_view(), name="universal-qr-check"),
    path(
        "flask-qr/manual/", FlaskQrManualMultipleView.as_view(), name="flask-qr-manual"
    ),
]
