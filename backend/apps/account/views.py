from django_filters import rest_framework as filters
from rest_framework import filters as rf_filters, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework import generics, permissions
from .models import User, RoleOptions, AppVersion
from .serializers import (
    UserRegisterSerializer,
    UserLoginSerializer,
    UserAdminRegisterSerializer,
    UserAdminUpdateSerializer,
    UserSerializer,
    UserUpdateSerializer,
    UserProfileUpdateSerializer,
    AppVersionSerializer,
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
    redis_client,
    check_otp_limit,
    increment_otp_counter,
)
from apps.ecopacket.models import Box


class GetAuthToken(ObtainAuthToken):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        phone_number = request.data.get("phone_number")
        password = request.data.get("password")

        if not phone_number or not password:
            return Response(
                {"error": "Both phone number and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

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
            return Response(
                {"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED
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
    queryset = User.objects.filter(is_active=True).order_by("-id")
    filter_backends = [filters.DjangoFilterBackend, rf_filters.SearchFilter]
    filterset_fields = ["is_admin", "role", "categories"]
    search_fields = ["first_name", "last_name", "phone_number", "car_number"]
    pagination_class = MyPagination

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # Agent foydalanuvchilarni olish
        agent_users = self.get_queryset().filter(role="AGENT")

        if agent_users.exists():
            # Barcha box konteynerlarni bir marta olish
            agent_boxes = {}
            boxes = Box.objects.filter(seller__in=agent_users)

            # Agent ID bo'yicha box ma'lumotlarini saqlash
            for box in boxes:
                if box.seller_id not in agent_boxes:
                    agent_boxes[box.seller_id] = []
                agent_boxes[box.seller_id].append(box)

            context["agent_boxes"] = agent_boxes
        return context

    # def perform_create(self, serializer):
    #     serializer.save(role=RoleOptions.EMPLOYE)
    #     return super().perform_create(serializer)


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
            user.first_name = ""
            user.last_name = ""
            user.is_active = False
            user.is_admin = False
            user.save()
            try:
                arg = BankAccount.objects.get(user=user)
                arg.capital = 0
                arg.save()
            except Exception as e:
                return Response(
                    {"message": "Bank accountingizda muammo bor"}, status=400
                )
            logout(request)
            return Response(
                {"message": "Ma'lumotlarningiz muvaffaqiyatli o'chirildi"}, status=202
            )
        return Response({"message": "Kiritgan parolingiz to'g'ri kelmadi"}, status=400)


class UserDeleteByIdView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        # Foydalanuvchi faqat o'zining hisobini o'chirishi mumkinligini tekshirish
        if str(request.user.id) != str(user_id):
            return Response(
                {"message": "Siz faqat o'zingizning hisobingizni o'chira olasiz"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            user = User.objects.get(id=user_id)
            user.first_name = ""
            user.last_name = ""
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
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                {"message": "Foydalanuvchi topilmadi"}, status=status.HTTP_200_OK
            )


# version 2
class RegisterView(views.APIView):
    def perform_create(self, serializer):
        return serializer.save(role=RoleOptions.POPULATION)

    def post(self, request):
        phone_number = request.data.get("phone_number")
        auto_input_code = request.data.get("auto_input_code")
        if not phone_number:
            return Response(
                {"message": "Phone number is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # IP manzilni olish
        ip_address = self.get_client_ip(request)

        # OTP cheklovini tekshirish
        if not check_otp_limit(phone_number, ip_address):
            return Response(
                {
                    "message": "Siz bugun OTP kodlarini jo'natish limitiga yetdingiz. Iltimos, ertaga qayta urinib ko'ring."
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        user = User.objects.filter(phone_number=phone_number).first()
        if user and user.is_active:
            return Response(
                {"message": "Foydalanuvchi allaqachon mavjud!"},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = (
            UserRegisterSerializer(instance=user, data=request.data)
            if user
            else UserRegisterSerializer(data=request.data)
        )

        if serializer.is_valid():
            user = self.perform_create(
                serializer
            )  # Use perform_create method to save the user
            # Generate OTP and save it to the user model
            otp = user.generate_otp()

            # SMS xabarini tayyorlash
            sms_message = f"Tozauz mobil ilovasi tozauz.uz ga kirish uchun tasdiqlash code is: {otp}"
            if auto_input_code:
                sms_message += f" {auto_input_code}"

            res = send_sms(user.phone_number, sms_message)
            if res.status_code != 200:
                return Response(
                    {
                        "message": "Failed to send OTP to phone number.",
                        "error": res.json(),
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # OTP jo'natilganini hisoblagichga qo'shish
            increment_otp_counter(phone_number, ip_address)

            return Response(
                {
                    "message": "User registered successfully. OTP sent to phone number.",
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_client_ip(self, request):
        """Mijoz IP manzilini aniqlash"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class VerifyRegistrationOTPView(views.APIView):
    def post(self, request):
        phone_number = request.data.get("phone_number")
        otp = request.data.get("otp")

        if not phone_number or not otp:
            return Response(
                {"error": "Phone number and OTP are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(phone_number=phone_number).first()
        if not user:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if user.verify_otp(otp):
            user.is_active = True
            user.clear_otp()  # Clear OTP after successful verification
            return Response(
                {"message": "OTP verified successfully."}, status=status.HTTP_200_OK
            )

        return Response(
            {"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST
        )


class ForgotPasswordView(views.APIView):
    def post(self, request):
        phone_number = request.data.get("phone_number")
        auto_input_code = request.data.get(
            "auto_input_code"
        )  # Qo'shimcha input kodini olish
        if not phone_number:
            return Response(
                {"error": "Phone number is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # IP manzilni olish
        ip_address = self.get_client_ip(request)

        # OTP cheklovini tekshirish
        if not check_otp_limit(phone_number, ip_address):
            return Response(
                {
                    "message": "Siz bugun OTP kodlarini jo'natish limitiga yetdingiz. Iltimos, ertaga qayta urinib ko'ring."
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        user = User.objects.filter(phone_number=phone_number).first()
        if user:
            otp = user.generate_otp()

            # SMS xabarini tayyorlash
            sms_message = f"Tozauz mobil ilovasi tozauz.uz ga kirish uchun tasdiqlash code is: {otp}"
            if auto_input_code:
                sms_message += f" {auto_input_code}"

            res = send_sms(phone_number, sms_message)

            # OTP jo'natilganini hisoblagichga qo'shish
            if res.status_code == 200:
                increment_otp_counter(phone_number, ip_address)

            return Response(
                {
                    "message": "OTP sent to phone number.",
                },
                status=status.HTTP_200_OK,
            )
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    def get_client_ip(self, request):
        """Mijoz IP manzilini aniqlash"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


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

        user = User.objects.filter(phone_number=phone_number).first()
        if not user:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if user.verify_otp(otp):
            user.set_password(new_password)
            user.clear_otp()  # Clear OTP after successful verification
            return Response(
                {"message": "Password reset successfully."},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST
        )


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


class AppVersionViewSet(viewsets.ModelViewSet):
    queryset = AppVersion.objects.all()
    serializer_class = AppVersionSerializer


class CheckPhoneNumberView(views.APIView):
    """
    Telefon raqam orqali foydalanuvchining ro'yxatdan o'tgan yoki o'tmaganligini tekshiruvchi API.
    """
    
    def post(self, request, format=None):
        """
        Telefon raqamni tekshirish.

        Args:
            request data:
            {
                "phone_number": "string"        # Majburiy. Telefon raqami
            }

        Returns:
            {
                "phone_number": "string",       # Tekshirilgan telefon raqami
                "is_registered": boolean,       # Ro'yxatdan o'tgan yoki yo'q
                "user_info": {                  # Agar ro'yxatdan o'tgan bo'lsa
                    "id": int,
                    "first_name": "string",
                    "last_name": "string",
                    "role": "string"
                }
            }

        Raises:
            400 Bad Request:
                - phone_number kiritilmagan
        """
        phone_number = request.data.get("phone_number")
        
        if not phone_number:
            return Response(
                {"error": "phone_number is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            user = User.objects.get(phone_number=phone_number)
            # Foydalanuvchi topildi
            return Response({
                "phone_number": phone_number,
                "is_registered": True,
                "user_info": {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role
                }
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            # Foydalanuvchi topilmadi
            return Response({
                "phone_number": phone_number,
                "is_registered": False,
                "user_info": None
            }, status=status.HTTP_200_OK)
