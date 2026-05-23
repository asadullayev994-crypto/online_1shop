from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

User = get_user_model()

class SignUpSerializer(serializers.ModelSerializer):
   
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
       
        fields = ['email', 'phone_number', 'password', 'password_confirm', 'role']
        extra_kwargs = {
            'email': {'required': True},
            'phone_number': {'required': False},
        }

    def validate_email(self, value):
       
        value = value.lower().strip()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Bu email manzil allaqachon ro'yxatdan o'tgan.")
        return value

    def validate(self, attrs):
       
        password = attrs.get('password')
        password_confirm = attrs.pop('password_confirm') 

       
        if password != password_confirm:
            raise serializers.ValidationError({"password_confirm": "Kiritilgan parollar bir-biriga mos kelmadi."})

        
        user_instance = User(email=attrs.get('email'), phone_number=attrs.get('phone_number'))
        try:
            validate_password(password, user=user_instance)
        except DjangoValidationError as error:
            raise serializers.ValidationError({"password": list(error.messages)})

        return attrs

    def create(self, validated_data):
       
        user = User.objects.create_user(
            email=validated_data['email'],
            phone_number=validated_data.get('phone_number'),
            password=validated_data['password'],
            role=validated_data.get('role', User.RoleChoice.CUSTOMER)
        )
        return user


class VerifyCodeSerializer(serializers.Serializer):
  
    email = serializers.EmailField(required=True)
    code = serializers.CharField(max_length=6, required=True)
    
    
class GetNewCodeSerializer(serializers.Serializer):
   
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        value = value.lower().strip()
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Bu email manzilga ega foydalanuvchi topilmadi.")
        return value


class UserProfileUpdateSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = User
       
        fields = ['first_name', 'last_name', 'phone_number', 'address', 'avatar']
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'phone_number': {'required': False},
            'address': {'required': False},
        }
        
        
        
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    new_password_confirm = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "Yangi parollar bir-biriga mos kelmadi."})
        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        value = value.lower().strip()
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Bu email manzilga ega foydalanuvchi topilmadi.")
        return value


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(max_length=6, required=True)
    new_password = serializers.CharField(required=True, write_only=True)
    new_password_confirm = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "Yangi parollar bir-biriga mos kelmadi."})
        return attrs