from rest_framework import generics, status, permissions, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Home, HomeMembership, Region, WasteMonthlyReport
from .serializers import (
    HomeReportSerializer,
    HomeSerializer,
    HomeCreateSerializer,
    JoinHomeSerializer,
    HomeMembershipSerializer,
    HomeMemberReportSerializer,
    HomeListSerializer,
    RegionSerializer,
    RegionDetailSerializer,
    WasteMonthlyReportSerializer,
    HomeWarningSerializer,
)
from apps.ecopacket.models import EcoPacketQrCode


class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Region CRUD operations
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return RegionDetailSerializer
        return RegionSerializer

    def get_queryset(self):
        return Region.objects.filter(is_active=True).order_by("name")

    @action(detail=True, methods=["get"])
    def monthly_stats(self, request, pk=None):
        """Hudud uchun oylik statistika"""
        region = self.get_object()
        year = request.query_params.get("year")
        month = request.query_params.get("month")

        if year:
            year = int(year)
        if month:
            month = int(month)

        stats = region.get_monthly_waste_statistics(year, month)
        return Response(stats)

    @action(detail=True, methods=["post"])
    def generate_report(self, request, pk=None):
        """Hudud uchun oylik hisobot yaratish"""
        region = self.get_object()
        year = request.data.get("year")
        month = request.data.get("month")

        if year:
            year = int(year)
        if month:
            month = int(month)

        report = WasteMonthlyReport.generate_monthly_report(region, year, month)
        serializer = WasteMonthlyReportSerializer(report)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class HomeReportView(APIView):
    """
    GET /api/home/report/

    Foydalanuvchining uyidagi barcha a'zolar va ularning ecopaket sonlarini qaytaradi
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            # Get user's home membership
            membership = HomeMembership.objects.select_related(
                "home", "home__region"
            ).get(user=request.user)
            home = membership.home

        except HomeMembership.DoesNotExist:
            return Response(
                {"error": "Siz hech qanday uyga a'zo emassiz"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Get current month for statistics
        now = timezone.now()

        # Get all members of the home with ecopacket counts
        members_data = (
            HomeMembership.objects.filter(home=home)
            .select_related("user", "home")
            .annotate(
                ecopacket_count=Count(
                    "user__ecopacketqrcode",
                    filter=Q(user__ecopacketqrcode__scannered_at__isnull=False),
                ),
                monthly_ecopacket_count=Count(
                    "user__ecopacketqrcode",
                    filter=Q(
                        user__ecopacketqrcode__scannered_at__year=now.year,
                        user__ecopacketqrcode__scannered_at__month=now.month,
                        user__ecopacketqrcode__scannered_at__isnull=False,
                    ),
                ),
            )
            .order_by("-monthly_ecopacket_count", "-ecopacket_count", "joined_at")
        )

        # Prepare members list
        members_list = []
        for member_data in members_data:
            member_info = {
                "user_id": member_data.user.id,
                "username": member_data.user.phone_number,  # Using phone as username
                "first_name": member_data.user.first_name,
                "last_name": member_data.user.last_name,
                "phone_number": member_data.user.phone_number,
                "ecopacket_count": member_data.ecopacket_count,
                "monthly_ecopacket_count": member_data.monthly_ecopacket_count,
                "joined_at": member_data.joined_at,
                "is_admin": member_data.is_admin,
            }
            members_list.append(member_info)

        # Get region warning data
        region_warning = home.check_region_limit_warning()

        # Prepare response data
        response_data = {
            "home_id": home.id,
            "home_name": home.name,
            "region_name": home.region.name if home.region else None,
            "member_count": len(members_list),
            "total_ecopackets": sum(
                member["ecopacket_count"] for member in members_list
            ),
            "monthly_ecopackets": sum(
                member["monthly_ecopacket_count"] for member in members_list
            ),
            "region_warning": region_warning,
            "members": members_list,
        }

        serializer = HomeReportSerializer(response_data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class HomeListCreateView(generics.ListCreateAPIView):
    """
    GET /api/home/homes/ - Foydalanuvchi a'zo bo'lgan uylar ro'yxati
    POST /api/home/homes/ - Yangi uy yaratish
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return HomeCreateSerializer
        return HomeListSerializer

    def get_queryset(self):
        # Return homes where user is a member
        return (
            Home.objects.filter(memberships__user=self.request.user, is_active=True)
            .select_related("region")
            .distinct()
        )


class HomeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PUT/DELETE /api/home/homes/{id}/
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = HomeSerializer

    def get_queryset(self):
        # Skip filtering for Swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Home.objects.none()
            
        # Only allow access to homes where user is a member
        return Home.objects.filter(
            memberships__user=self.request.user, is_active=True
        ).select_related("region")


class HomeWarningView(APIView):
    """
    GET /api/home/warning/

    Foydalanuvchi uyining hudud limit ogohlantirishini olish
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            membership = HomeMembership.objects.select_related(
                "home", "home__region"
            ).get(user=request.user)
            home = membership.home
        except HomeMembership.DoesNotExist:
            return Response(
                {"error": "Siz hech qanday uyga a'zo emassiz"},
                status=status.HTTP_404_NOT_FOUND,
            )

        warning_data = home.check_region_limit_warning()

        response_data = {
            "home_id": home.id,
            "home_name": home.name,
            "region_name": home.region.name,
            **warning_data,
        }

        serializer = HomeWarningSerializer(response_data)
        return Response(serializer.data)


class RegionHomesWarningView(APIView):
    """
    GET /api/home/region-warnings/

    Barcha hududlar va ularning limit holatlari
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        regions = Region.objects.filter(is_active=True)
        warnings = []

        for region in regions:
            stats = region.get_monthly_waste_statistics()
            usage_ratio = (
                stats["total_scans"] / stats["limit"] if stats["limit"] > 0 else 0
            )

            warning_level = "normal"
            if usage_ratio >= 1.0:
                warning_level = "critical"
            elif usage_ratio >= 0.8:
                warning_level = "warning"

            warnings.append(
                {
                    "region_id": region.id,
                    "region_name": region.name,
                    "region_code": region.code,
                    "warning_level": warning_level,
                    "stats": stats,
                }
            )

        return Response(warnings)


class JoinHomeView(APIView):
    """
    POST /api/home/join/

    Taklifnoma kodi bilan uyga qo'shilish
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = JoinHomeSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            membership = serializer.save()
            return Response(
                {
                    "message": f"Siz '{membership.home.name}' uyiga muvaffaqiyatli qo'shildingiz",
                    "home_id": membership.home.id,
                    "home_name": membership.home.name,
                    "region_name": membership.home.region.name,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LeaveHomeView(APIView):
    """
    POST /api/home/leave/

    Uydan chiqish
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            membership = HomeMembership.objects.get(user=request.user)
            home_name = membership.home.name

            # Check if user is the only admin
            if membership.is_admin:
                admin_count = HomeMembership.objects.filter(
                    home=membership.home, is_admin=True
                ).count()

                if admin_count == 1:
                    return Response(
                        {
                            "error": "Siz bu uyning yagona adminisiz. Avval boshqa adminni tayinlang"
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            membership.delete()

            return Response(
                {"message": f"Siz '{home_name}' uyidan muvaffaqiyatli chiqdingiz"},
                status=status.HTTP_200_OK,
            )

        except HomeMembership.DoesNotExist:
            return Response(
                {"error": "Siz hech qanday uyga a'zo emassiz"},
                status=status.HTTP_404_NOT_FOUND,
            )


class HomeMembersView(generics.ListAPIView):
    """
    GET /api/home/members/

    Foydalanuvchi uyidagi barcha a'zolarni ko'rsatish
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = HomeMembershipSerializer

    def get_queryset(self):
        try:
            membership = HomeMembership.objects.get(user=self.request.user)
            return (
                HomeMembership.objects.filter(home=membership.home)
                .select_related("user")
                .order_by("-joined_at")
            )
        except HomeMembership.DoesNotExist:
            return HomeMembership.objects.none()


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def my_home_status(request):
    """
    GET /api/home/status/

    Foydalanuvchining uy holati haqida ma'lumot
    """
    try:
        membership = HomeMembership.objects.select_related("home", "home__region").get(
            user=request.user
        )

        # Current month ecopacket count
        now = timezone.now()
        user_monthly_ecopacket_count = EcoPacketQrCode.objects.filter(
            user=request.user,
            scannered_at__year=now.year,
            scannered_at__month=now.month,
            scannered_at__isnull=False,
        ).count()

        # Total ecopacket count
        user_total_ecopacket_count = EcoPacketQrCode.objects.filter(
            user=request.user, scannered_at__isnull=False
        ).count()

        # Region warning
        region_warning = membership.home.check_region_limit_warning()

        return Response(
            {
                "has_home": True,
                "home_id": membership.home.id,
                "home_name": membership.home.name,
                "region_id": membership.home.region.id,
                "region_name": membership.home.region.name,
                "region_code": membership.home.region.code,
                "is_admin": membership.is_admin,
                "joined_at": membership.joined_at,
                "my_monthly_ecopacket_count": user_monthly_ecopacket_count,
                "my_total_ecopacket_count": user_total_ecopacket_count,
                "region_warning": region_warning,
                "invitation_code": (
                    membership.home.invitation_code if membership.is_admin else None
                ),
            }
        )

    except HomeMembership.DoesNotExist:
        # Current month ecopacket count
        now = timezone.now()
        user_monthly_ecopacket_count = EcoPacketQrCode.objects.filter(
            user=request.user,
            scannered_at__year=now.year,
            scannered_at__month=now.month,
            scannered_at__isnull=False,
        ).count()

        # Total ecopacket count
        user_total_ecopacket_count = EcoPacketQrCode.objects.filter(
            user=request.user, scannered_at__isnull=False
        ).count()

        return Response(
            {
                "has_home": False,
                "my_monthly_ecopacket_count": user_monthly_ecopacket_count,
                "my_total_ecopacket_count": user_total_ecopacket_count,
            }
        )
