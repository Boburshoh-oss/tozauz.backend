from rest_framework import serializers
from .models import User
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _


class UserEarningSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','first_name','phone_number','role']


class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'phone_number', 'password')

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'phone_number','first_name','last_name')

        extra_kwargs = {
            'id': {'read_only': True},
        }
        
class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'phone_number',
                  'password', 'last_login', 'role', 'is_active')
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True},
            'last_login': {'read_only': True},
            'role': {'read_only': True},
            'is_active': {'read_only': True},
        }

    def create(self, validated_data):
        if "password" in validated_data:
            validated_data["password"] = make_password(
                validated_data["password"])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "password" in validated_data:
            validated_data["password"] = make_password(
                validated_data["password"])
        return super().update(instance, validated_data)


class UserAdminRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'phone_number',
                  'role', 'is_active', 'categories', 'car_number', 'is_admin']


class UserAdminRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'phone_number',
                  'password', 'last_login',  'role', 'categories', 'car_number', 'is_admin')
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True},
            'last_login': {'read_only': True},
        }

    def create(self, validated_data):
        if "password" in validated_data:
            validated_data["password"] = make_password(
                validated_data["password"])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "password" in validated_data:
            validated_data["password"] = make_password(
                validated_data["password"])
        return super().update(instance, validated_data)

class UserAdminUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name',
                  'phone_number',
                  'password', 'role',
                  'categories', 'car_number', 'is_admin')
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True, 'required': False},
        }

 
    def create(self, validated_data):
        if "password" in validated_data:
            validated_data["password"] = make_password(
                validated_data["password"])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "password" in validated_data:
            validated_data["password"] = make_password(
                validated_data["password"])
        return super().update(instance, validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone_number', 'first_name', 'last_name', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            phone_number=validated_data['phone_number'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            is_active=False  # User will be activated after OTP verification
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class OTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    otp = serializers.CharField()
    new_password = serializers.CharField(write_only=True)