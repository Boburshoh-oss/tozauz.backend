from django.urls import path
from ..views.flask_qr_view import FlaskQrManualMultipleView

urlpatterns = [
    path(
        "flask-qr/manual/",
        FlaskQrManualMultipleView.as_view(),
        name="flask-qr-manual",
    ),
]
