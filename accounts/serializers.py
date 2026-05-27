from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
from rest_framework import serializers

User = get_user_model()


# ─────────────────────────────────────────────
# AUTH SERIALIZERS
# ─────────────────────────────────────────────

class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    password_confirm = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = ["email", "phone_number", "password", "password_confirm", "role"]
        extra_kwargs = {
            "email": {"required": True},
            "phone_number": {"required": False},
        }

    def validate_email(self, value):
        value = value.lower().strip()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Bu email allaqachon ro'yxatdan o'tgan.")
        return value

    def validate(self, attrs):
        password = attrs.get("password")
        password_confirm = attrs.pop("password_confirm")

        if password != password_confirm:
            raise serializers.ValidationError({"password_confirm": "Parollar mos kelmadi."})

        user_instance = User(email=attrs.get("email"), phone_number=attrs.get("phone_number"))
        try:
            validate_password(password, user=user_instance)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        return attrs

    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data["email"],
            phone_number=validated_data.get("phone_number"),
            password=validated_data["password"],
            role=validated_data.get("role", User.RoleChoice.CUSTOMER),
        )


class LoginSerializer(serializers.Serializer):
    """Email, telefon yoki username bilan login"""
    login = serializers.CharField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, attrs):
        login = attrs.get("login", "").strip()
        password = attrs.get("password")

        # Email, phone orqali qidirish
        user_obj = User.objects.filter(
            Q(email=login) | Q(phone_number=login)
        ).first()

        if not user_obj:
            raise serializers.ValidationError("Login yoki parol noto'g'ri.")

        # Bloklangan foydalanuvchi
        if user_obj.is_banned:
            raise serializers.ValidationError("Sizning akkauntingiz bloklangan. Admin bilan bog'laning.")

        # Parolni tekshirish
        if not user_obj.check_password(password):
            raise serializers.ValidationError("Login yoki parol noto'g'ri.")

        # Tasdiqlanmaganligini tekshirish
        if not user_obj.is_verified:
            raise serializers.ValidationError("Akkauntingiz tasdiqlanmagan. Tasdiqlash kodini kiriting.")

        # Faolligini tekshirish
        if not user_obj.is_active:
            raise serializers.ValidationError("Akkauntingiz faol emas.")

        attrs["user"] = user_obj
        return attrs


class VerifyCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    purpose = serializers.ChoiceField(
        choices=["register", "reset"],
        default="register",
    )


class GetNewCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        value = value.lower().strip()
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Bu emailga ega foydalanuvchi topilmadi.")
        return value


# ─────────────────────────────────────────────
# PROFILE SERIALIZERS
# ─────────────────────────────────────────────

class UserProfileSerializer(serializers.ModelSerializer):
    """Faqat o'qish uchun — GET"""
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "email", "phone_number", "first_name", "last_name",
            "full_name", "address", "avatar", "role", "is_verified",
            "last_seen", "created_at",
        ]
        read_only_fields = fields


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Yangilash uchun — PUT/PATCH"""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone_number", "address", "avatar"]
        extra_kwargs = {
            "phone_number": {"required": False},
            "first_name": {"required": False},
            "last_name": {"required": False},
            "address": {"required": False},
            "avatar": {"required": False},
        }

    def validate_phone_number(self, value):
        user = self.instance
        if value and User.objects.filter(phone_number=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("Bu telefon raqam allaqachon ishlatilmoqda.")
        return value


# ─────────────────────────────────────────────
# PASSWORD SERIALIZERS
# ─────────────────────────────────────────────

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        request = self.context.get("request")
        user = request.user

        # Eski parolni tekshirish
        if not user.check_password(attrs["old_password"]):
            raise serializers.ValidationError({"old_password": "Eski parol noto'g'ri."})

        # Yangi parollar mosligini tekshirish
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Yangi parollar mos emas."})

        # Parol kuchliligini tekshirish
        try:
            validate_password(attrs["new_password"], user=user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})

        # Yangi parol eski parol bilan bir xil bo'lmasligi
        if attrs["old_password"] == attrs["new_password"]:
            raise serializers.ValidationError({"new_password": "Yangi parol eski parol bilan bir xil bo'lmasin."})

        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        value = value.lower().strip()
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Bu emailga ega foydalanuvchi topilmadi.")
        return value


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Parollar mos emas."})

        try:
            validate_password(attrs["new_password"])
        except DjangoValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})

        return attrs