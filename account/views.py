from rest_framework import generics, views
from rest_framework.authtoken.models import Token
from rest_framework import generics, permissions
from .models import User, RoleOptions
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserAdminRegisterSerializer, UserAdminRetrieveSerializer
from django.contrib.auth import authenticate
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN


class GetAuthToken(ObtainAuthToken):
    serializer_class = UserLoginSerializer

    def post(self, request):
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')
        user = authenticate(
            request, phone_number=phone_number, password=password)
        if user is None:
            return Response({
                'detail': 'User not found'
            }, status=HTTP_404_NOT_FOUND)
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'id': user.id,
            'phone_number': user.phone_number,
            'first_name': user.first_name,
        })


class AdminGetAuthToken(ObtainAuthToken):
    serializer_class = UserLoginSerializer

    def post(self, request):
        phone_number = request.data.get('phoneNumber')
        password = request.data.get('password')
        user = authenticate(
            request, phone_number=phone_number, password=password)
        if user is None:
            return Response({
                'detail': 'User not found'
            }, status=HTTP_404_NOT_FOUND)
        if user.is_admin:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': {
                    'id': user.id,
                    'phoneNumber': user.phone_number,
                    'firstName': user.first_name,
                }
            }, status=200)
        return Response({
            'detail': "User is not admin or access denied!",
        }, status=HTTP_403_FORBIDDEN)


class UserListRegisterView(generics.ListCreateAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer

    def perform_create(self, serializer):
        serializer.save(role=RoleOptions.POPULATION)
        return super().perform_create(serializer)

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            return []
        if user.is_admin:
            return User.objects.all()
        return [user]


class UserAdminRegisterView(generics.ListCreateAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()
    serializer_class = UserAdminRegisterSerializer

    def perform_create(self, serializer):
        serializer.save(role=RoleOptions.EMPLOYE)
        return super().perform_create(serializer)

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            return []
        if user.is_admin:
            return User.objects.all()
        return [user]


class UserAdmninRetrieveView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all()
    serializer_class = UserAdminRetrieveSerializer


# class UserLoginView(views.APIView):
#     def post(self, request):
#         serializer = UserLoginSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         return Response(serializer.data)
