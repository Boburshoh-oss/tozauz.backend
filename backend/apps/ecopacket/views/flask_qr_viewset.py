from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import F
from apps.ecopacket.models import FlaskQrCode
from apps.ecopacket.serializers.flask_qr_serializer import FlaskQrCodeSerializer


class FlaskQrCodeViewSet(viewsets.ModelViewSet):
    queryset = FlaskQrCode.objects.all()
    serializer_class = FlaskQrCodeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["category"]
    search_fields = ["bar_code"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]  # Default ordering

    def get_queryset(self):
        return (
            FlaskQrCode.objects.select_related("category")
            .annotate(category_name=F("category__name"))
            .all()
        )
