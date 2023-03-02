from rest_framework import serializers
from .models import User
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _


class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'phone_number', 'password')


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
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'phone_number',
                  'role', 'is_active']


class UserAdminRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'phone_number', 'email',
                  'username', 'password', 'last_login', 'date_joined', 'role', 'is_active')
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True},
            'last_login': {'read_only': True},
            'date_joined': {'read_only': True}
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


class UserAdminUpdateSerializer(UserAdminRegisterSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'phone_number', 'email',
                  'username', 'password', 'last_login', 'date_joined', 'role', 'is_active')
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True, 'required': False},
            'last_login': {'read_only': True},
            'date_joined': {'read_only': True}
        }
