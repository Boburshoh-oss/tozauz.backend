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
    UserProfileUpdateSerializer,
)
from django.contrib.auth import authenticate, logout
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN
from apps.utils.pagination import MyPagination
from apps.bank.models import BankAccount
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

    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')

        if not phone_number or not password:
            return Response({
                'error': 'Both phone number and password are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, phone_number=phone_number, password=password)

        if user and user.is_active:
            token, created = Token.objects.get_or_create(user=user)
            user_data = {
                "token": token.key,
                "id": user.id,
                "phone_number": user.phone_number,
                "first_name": user.first_name,
                "role": user.role,
            }
            
            return Response(user_data, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Invalid credentials.'
            }, status=status.HTTP_401_UNAUTHORIZED)

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
        phone_number = request.data.get("phoneNumber")
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


class UserDeleteView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # password = request.data.get("password", None)
        user = request.user
        # if user.check_password(password):
        if True:
            user.first_name = ''
            user.last_name = ''
            user.is_active = False
            user.is_admin = False
            user.save()
            try:
                arg = BankAccount.objects.get(user=user)
                arg.capital = 0
                arg.save()
            except Exception as e:
                return Response({"message": "Bank accountingizda muammo bor"}, status=400)
            logout(request)
            return Response(
                {"message": "Ma'lumotlarningiz muvaffaqiyatli o'chirildi"}, status=202
            )
        return Response({"message": "Kiritgan parolingiz to'g'ri kelmadi"}, status=400)

class UserDeleteByIdView(views.APIView):
    # permission_classes = [permissions.IsAdminUser]

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            user.first_name = ''
            user.last_name = ''
            user.is_active = False
            user.is_admin = False
            user.save()

            try:
                bank_account = BankAccount.objects.get(user=user)
                bank_account.capital = 0
                bank_account.save()
            except BankAccount.DoesNotExist:
                pass  # If bank account doesn't exist, continue with deletion

            return Response(
                {"message": "Foydalanuvchi ma'lumotlari muvaffaqiyatli o'chirildi"}, 
                status=status.HTTP_202_ACCEPTED
            )
        except User.DoesNotExist:
            return Response(
                {"message": "Foydalanuvchi topilmadi"}, 
                status=status.HTTP_404_NOT_FOUND
            )

# version 2
class RegisterView(views.APIView):
    def perform_create(self, serializer):
        return serializer.save(role=RoleOptions.POPULATION)

    def post(self, request):
        phone_number = request.data.get('phone_number')
        if not phone_number:
            return Response({"message": "Phone number is required."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(phone_number=phone_number).first()
        if user and user.is_active:
            return Response({"message":"Foydalanuvchi allaqachon mavjud!"}, status=status.HTTP_403_FORBIDDEN)
        serializer = UserRegisterSerializer(instance=user, data=request.data) if user else UserRegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = self.perform_create(serializer)  # Use perform_create method to save the user
            otp = generate_random_password(6)
            res = send_sms(user.phone_number, f"Tozauz mobil ilovasi tozauz.uz ga kirish uchun tasdiqlash kodi: {otp}")
            if res.status_code != 200:
                return Response({"message": "Failed to send OTP to phone number.", "error": res.json()}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            redis_client.setex(f"otp_{user.phone_number}", 300, otp)
            return Response({"message": "User registered successfully. OTP sent to phone number.", "otp": otp}, status=status.HTTP_201_CREATED)

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
            send_sms(phone_number, f"Tozauz mobil ilovasi tozauz.uz ga kirish uchun tasdiqlash kodi: {otp}")
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

class UserProfileUpdateView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def put(self, request):
        user = self.get_object()
        serializer = UserProfileUpdateSerializer(user, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        user = self.get_object()
        serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    