from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404

from .models import Home, HomeMembership
from .serializers import (
    HomeReportSerializer,
    HomeSerializer,
    HomeCreateSerializer,
    JoinHomeSerializer,
    HomeMembershipSerializer,
    HomeMemberReportSerializer,
)
from apps.ecopacket.models import EcoPacketQrCode


class HomeReportView(APIView):
    """
    GET /api/home/report/

    Foydalanuvchining uyidagi barcha a'zolar va ularning ecopaket sonlarini qaytaradi
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            # Get user's home membership
            membership = HomeMembership.objects.select_related("home").get(
                user=request.user
            )
            home = membership.home

        except HomeMembership.DoesNotExist:
            return Response(
                {"error": "Siz hech qanday uyga a'zo emassiz"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Get all members of the home with ecopacket counts
        # Using efficient query with annotations
        members_data = (
            HomeMembership.objects.filter(home=home)
            .select_related("user", "home")
            .annotate(
                ecopacket_count=Count(
                    "user__ecopacketqrcode",
                    filter=Q(user__ecopacketqrcode__user__isnull=False),
                )
            )
            .order_by("-ecopacket_count", "joined_at")
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
                "joined_at": member_data.joined_at,
                "is_admin": member_data.is_admin,
            }
            members_list.append(member_info)

        # Prepare response data
        response_data = {
            "home_id": home.id,
            "home_name": home.name,
            "member_count": len(members_list),
            "total_ecopackets": sum(
                member["ecopacket_count"] for member in members_list
            ),
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
        return HomeSerializer

    def get_queryset(self):
        # Return homes where user is a member
        return Home.objects.filter(
            memberships__user=self.request.user, is_active=True
        ).distinct()


class HomeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PUT/DELETE /api/home/homes/{id}/
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = HomeSerializer

    def get_queryset(self):
        # Only allow access to homes where user is a member
        return Home.objects.filter(memberships__user=self.request.user, is_active=True)


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
        membership = HomeMembership.objects.select_related("home").get(
            user=request.user
        )

        user_ecopacket_count = EcoPacketQrCode.objects.filter(user=request.user).count()

        return Response(
            {
                "has_home": True,
                "home_id": membership.home.id,
                "home_name": membership.home.name,
                "is_admin": membership.is_admin,
                "joined_at": membership.joined_at,
                "my_ecopacket_count": user_ecopacket_count,
                "invitation_code": (
                    membership.home.invitation_code if membership.is_admin else None
                ),
            }
        )

    except HomeMembership.DoesNotExist:
        user_ecopacket_count = EcoPacketQrCode.objects.filter(user=request.user).count()

        return Response({"has_home": False, "my_ecopacket_count": user_ecopacket_count})
