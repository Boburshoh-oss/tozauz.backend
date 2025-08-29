from django.urls import path
from ..views.flask_qr_view import FlaskQrManualMultipleView, FlaskQrManualSingleView, UniversalQrManualSingleView
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from apps.ecopacket.views.flask_qr_view import FlaskQrManualMultipleView, FlaskQrManualSingleView, UniversalQrManualSingleView
from apps.ecopacket.views.flask_qr_viewset import FlaskQrCodeViewSet

router = DefaultRouter()
router.register('flask-qr-codes', FlaskQrCodeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('manual/', FlaskQrManualMultipleView.as_view(), name='flask-qr-manual-multiple'),
    path('manual/single/', FlaskQrManualSingleView.as_view(), name='flask-qr-manual-single'),
    path('universal/', UniversalQrManualSingleView.as_view(), name='universal-qr-manual'),
]

urlpatterns = [
    path('', include(router.urls)),
    path('flask-qr/manual/', FlaskQrManualMultipleView.as_view(), name='flask-qr-manual')
]

