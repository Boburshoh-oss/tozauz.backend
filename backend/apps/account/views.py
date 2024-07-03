from django_filters import rest_framework as filters
from rest_framework import filters as rf_filters, status
from rest_framework.authtoken.models import Token
from rest_framework import generics, permissions
from .models import User, RoleOptions
from .serializers import (
    UserRegisterSerializer,
    UserLoginSerializer,
    UserAdminRegisterSerializer,
    UserAdminUpdateSerializer,
    UserSerializer,
    UserUpdateSerializer,
)
from django.contrib.auth import authenticate
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN
from apps.utils.pagination import MyPagination
from rest_framework import views
from .utils import (
    # get_token_from_redis,
    # save_token_to_redis,
    generate_random_password,
    # eskiz_login,
    # eskiz_refresh_token,
    send_sms,
    redis_client
)


class GetAuthToken(ObtainAuthToken):
    serializer_class = UserLoginSerializer

    def post(self, request):
        phone_number = request.data.get("phone_number")
        password = request.data.get("password")
        user = authenticate(request, phone_number=phone_number, password=password)
        if user is None:
            return Response({"detail": "User not found"}, status=HTTP_404_NOT_FOUND)
        token, created = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "id": user.id,
                "phone_number": user.phone_number,
                "first_name": user.first_name,
                "role": user.role,
            }
        )


class UserRegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer

    def perform_create(self, serializer):
        serializer.save(role=RoleOptions.POPULATION)
        return super().perform_create(serializer)


# Admin
class AdminGetAuthToken(ObtainAuthToken):
    serializer_class = UserLoginSerializer

    def post(self, request):
        phone_number = request.data.get("phone_number")
        password = request.data.get("password")
        user = authenticate(request, phone_number=phone_number, password=password)
        if user is None:
            return Response({"detail": "User not found"}, status=HTTP_404_NOT_FOUND)
        if user.is_admin:
            token, created = Token.objects.get_or_create(user=user)
            return Response(
                {
                    "token": token.key,
                    "user": {
                        "id": user.id,
                        "phone_number": user.phone_number,
                        "firstName": user.first_name,
                    },
                },
                status=200,
            )
        return Response(
            {
                "detail": "User is not admin or access denied!",
            },
            status=HTTP_403_FORBIDDEN,
        )


# Admin
class UserAdminRegisterView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = UserAdminRegisterSerializer
    queryset = User.objects.all().order_by("-id")
    filter_backends = [filters.DjangoFilterBackend, rf_filters.SearchFilter]
    filterset_fields = ["is_admin", "role", "categories"]
    search_fields = ["first_name", "last_name", "phone_number", "car_number"]
    pagination_class = MyPagination

    def perform_create(self, serializer):
        serializer.save(role=RoleOptions.EMPLOYE)
        return super().perform_create(serializer)


# Admin
class UserAdminRetrieveView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all()
    serializer_class = UserAdminUpdateSerializer


class UserUpdateRetrieveView(generics.RetrieveUpdateDestroyAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer


class UserChangePasswordView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        old_password = request.data.get("old_password", None)
        new_password = request.data.get("new_password", None)
        user = request.user
        if user.check_password(old_password):
            user.set_password(new_password)
            user.save()
            return Response(
                {"message": "Parolingiz muvaffaqiyatli o'zgardi"}, status=200
            )
        return Response({"message": "Avvalgi parol to'g'ri kelmadi"}, status=400)


# version 2
class RegisterView(views.APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            otp = generate_random_password(6)
            res = send_sms(user.phone_number, "Bu Eskiz dan test")
            if res.status_code != 200:
                return Response(
                    {"message": "Failed to send OTP to phone number.", "error": res.json()}, status=500
                )
            redis_client.setex(f"otp_{user.phone_number}", 300, otp)
            return Response(
                {"message": "User registered successfully. OTP sent to phone number.", "otp": otp},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyRegistrationOTPView(views.APIView):
    def post(self, request):
        phone_number = request.data.get("phone_number")
        otp = request.data.get("otp")

        if not phone_number or not otp:
            return Response(
                {"error": "Phone number and OTP are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        saved_otp = redis_client.get(f"otp_{phone_number}")
        print(otp, saved_otp)
        if saved_otp and saved_otp == otp:
            user = User.objects.filter(phone_number=phone_number).first()
            if user:
                user.is_active = True
                user.save()
                redis_client.delete(f"otp_{phone_number}")
                return Response(
                    {"message": "OTP verified successfully."}, status=status.HTTP_200_OK
                )
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
        return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(views.APIView):
    def post(self, request):
        phone_number = request.data.get("phone_number")
        if not phone_number:
            return Response(
                {"error": "Phone number is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(phone_number=phone_number).first()
        if user:
            otp = generate_random_password(6)
            send_sms(phone_number, f"Your OTP code is {otp}")
            redis_client.setex(f"otp_{phone_number}", 300, otp)
            return Response(
                {"message": "OTP sent to phone number.", "otp": otp}, status=status.HTTP_200_OK
            )
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


class VerifyForgotPasswordOTPView(views.APIView):
    def post(self, request):
        phone_number = request.data.get("phone_number")
        otp = request.data.get("otp")
        new_password = request.data.get("new_password")

        if not phone_number or not otp or not new_password:
            return Response(
                {"error": "Phone number, OTP, and new password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        saved_otp = redis_client.get(f"otp_{phone_number}")
        if saved_otp and saved_otp == otp:
            user = User.objects.filter(phone_number=phone_number).first()
            if user:
                user.set_password(new_password)
                user.save()
                return Response(
                    {"message": "Password reset successfully."},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
        return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
