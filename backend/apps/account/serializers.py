from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.ecopacket.models import Box
from .models import User, RoleOptions, AppVersion



class UserEarningSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "phone_number", "role"]


class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "phone_number", "password")


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "phone_number", "first_name", "last_name")

        extra_kwargs = {
            "id": {"read_only": True},
        }


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "phone_number",
            "password",
            "last_login",
            "role",
            "is_active",
        )
        extra_kwargs = {
            "id": {"read_only": True},
            "password": {"write_only": True},
            "last_login": {"read_only": True},
            "role": {"read_only": True},
            "is_active": {"read_only": True},
        }

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class UserAdminRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "phone_number",
            "role",
            "is_active",
            "categories",
            "car_number",
            "is_admin",
            "inn",
            "bank_receipt",
        ]


class BoxForAgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Box
        fields = ("id", "name", "address", "location", "containers_count")


class UserAdminRegisterSerializer(serializers.ModelSerializer):
    boxes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "phone_number",
            "password",
            "last_login",
            "role",
            "categories",
            "car_number",
            "is_admin",
        )
        extra_kwargs = {
            "id": {"read_only": True},
            "password": {"write_only": True},
            "last_login": {"read_only": True},
        }

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def get_boxes(self, obj):
        # Faqat AGENT rolida bo'lgan foydalanuvchilar uchun box konteynerlarni qaytaramiz
        if obj.role == "AGENT":
            # Context dan oldindan yuklangan box ma'lumotlarini olish
            agent_boxes = self.context.get("agent_boxes", {})
            if obj.id in agent_boxes:
                return BoxForAgentSerializer(agent_boxes[obj.id], many=True).data

            # Agar context da ma'lumot bo'lmasa, bazadan olish (bu kamdan-kam holatlarda bo'ladi)
            boxes = Box.objects.filter(seller=obj)
            return BoxForAgentSerializer(boxes, many=True).data
        return []


class UserAdminUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "phone_number",
            "password",
            "role",
            "categories",
            "car_number",
            "is_admin",
        )
        extra_kwargs = {
            "id": {"read_only": True},
            "password": {"write_only": True, "required": False},
        }

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["phone_number", "first_name", "last_name", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User(
            phone_number=validated_data["phone_number"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            is_active=False,  # User will be activated after OTP verification
        )
        user.set_password(validated_data["password"])
        user.save()
        return user

    def update(self, instance, validated_data):
        # Update only the fields that are present in validated_data
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)

        # Set and hash the new password if present
        password = validated_data.get("password")
        if password:
            instance.set_password(password)

        instance.save()
        return instance


class OTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    otp = serializers.CharField()
    new_password = serializers.CharField(write_only=True)


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "car_number")
        extra_kwargs = {"car_number": {"required": False}}

    def validate(self, data):
        user = self.instance
        if (
            user.role not in [RoleOptions.EMPLOYE, RoleOptions.ADMIN]
            and "car_number" in data
        ):
            raise serializers.ValidationError(
                "Siz moshina raqamini o'zgartira olmaysiz!"
            )
        return data


class AppVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppVersion
        fields = "__all__"
