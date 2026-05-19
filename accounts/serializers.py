from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

User = get_user_model()

class SignUpSerializer(serializers.ModelSerializer):
    # Parol maydonlari xavfsizlik uchun faqat yozish (write_only) rejimida bo'ladi
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        # Ro'yxatdan o'tishda foydalanuvchidan so'raladigan maydonlar
        fields = ['email', 'phone_number', 'password', 'password_confirm', 'role']
        extra_kwargs = {
            'email': {'required': True},
            'phone_number': {'required': False},
        }

    def validate_email(self, value):
        """Email band yoki yo'qligini tekshirish"""
        value = value.lower().strip()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Bu email manzil allaqachon ro'yxatdan o'tgan.")
        return value

    def validate(self, attrs):
        """Parollar bir-biriga mosligi va murakkabligini tekshirish"""
        password = attrs.get('password')
        password_confirm = attrs.pop('password_confirm')  # Bazaga saqlanmasligi uchun o'chirib tashlaymiz

        # 1. Parollar mosligini tekshirish
        if password != password_confirm:
            raise serializers.ValidationError({"password_confirm": "Kiritilgan parollar bir-biriga mos kelmadi."})

        # 2. Djangoning xavfsiz parol qoidalariga tekshirish
        user_instance = User(email=attrs.get('email'), phone_number=attrs.get('phone_number'))
        try:
            validate_password(password, user=user_instance)
        except DjangoValidationError as error:
            raise serializers.ValidationError({"password": list(error.messages)})

        return attrs

    def create(self, validated_data):
        """Foydalanuvchini bazada yaratish"""
        user = User.objects.create_user(
            email=validated_data['email'],
            phone_number=validated_data.get('phone_number'),
            password=validated_data['password'],
            role=validated_data.get('role', User.RoleChoice.CUSTOMER)
        )
        return user


class VerifyCodeSerializer(serializers.Serializer):
    """Kod tasdiqlash uchun serializer"""
    email = serializers.EmailField(required=True)
    code = serializers.CharField(max_length=6, required=True)