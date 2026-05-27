from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import ActivityLog, CodeVerify
from .serializers import (
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    GetNewCodeSerializer,
    LoginSerializer,
    ResetPasswordSerializer,
    SignUpSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    VerifyCodeSerializer,
)

User = get_user_model()


# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────

def get_client_ip(request):
    """Foydalanuvchi IP manzilini olish"""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def send_email_verification(user_email, code, purpose="register"):
    """Gmail orqali tasdiqlash kodi yuborish"""
    if purpose == "register":
        purpose_text = "Ro'yxatdan o'tish"
        subject = "Online Shop — Akkauntingizni tasdiqlang"
    else:
        purpose_text = "Parolni tiklash"
        subject = "Online Shop — Parolni tiklash kodi"

    message = f"""\
Salom!

{purpose_text} uchun tasdiqlash kodingiz:

Kod: {code}

Kod 2 daqiqa davomida amal qiladi.
Kodni hech kimga bermang!

Agar siz bu so'rovni yubormagan bo'lsangiz, ushbu xatni e'tiborsiz qoldiring.

— Online Shop jamoasi
"""

    html_message = f"""\
<div style="font-family: Arial, sans-serif; max-width: 480px; margin: auto; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden;">
  <div style="background-color: #4f46e5; padding: 24px; text-align: center;">
    <h1 style="color: white; margin: 0; font-size: 22px;">🛒 Online Shop</h1>
  </div>
  <div style="padding: 32px;">
    <h2 style="color: #1f2937; margin-top: 0;">{purpose_text}</h2>
    <p style="color: #6b7280;">Tasdiqlash kodingiz:</p>
    <div style="background-color: #f3f4f6; border-radius: 8px; padding: 20px; text-align: center; margin: 24px 0;">
      <span style="font-size: 36px; font-weight: bold; letter-spacing: 8px; color: #4f46e5;">{code}</span>
    </div>
    <p style="color: #6b7280; font-size: 14px;">⏱ Kod <strong>2 daqiqa</strong> davomida amal qiladi.</p>
    <p style="color: #ef4444; font-size: 14px;">🔒 Kodni hech kimga bermang!</p>
    <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 24px 0;">
    <p style="color: #9ca3af; font-size: 12px;">
      Agar siz bu so'rovni yubormagan bo'lsangiz, ushbu xatni e'tiborsiz qoldiring.
    </p>
  </div>
</div>
"""

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Email yuborishda xatolik: {e}")
        return False


def log_activity(user, action, request=None):
    """Foydalanuvchi harakatini log qilish"""
    ip = get_client_ip(request) if request else None
    ActivityLog.objects.create(user=user, action=action, ip_address=ip)


def get_tokens_for_user(user):
    """Foydalanuvchi uchun JWT tokenlar yaratish"""
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


# ─────────────────────────────────────────────
# AUTH VIEWS
# ─────────────────────────────────────────────

class RegisterView(APIView):
    """
    POST /api/accounts/register/
    Yangi foydalanuvchi ro'yxatdan o'tkazish.
    """

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()

        # Tasdiqlash kodi yaratish va yuborish
        code_obj = CodeVerify.objects.create(user=user, purpose=CodeVerify.PurposeChoice.REGISTER)
        send_email_verification(user.email, code_obj.code, purpose="register")

        # Faollik log
        log_activity(user, ActivityLog.ActionChoice.REGISTER, request)

        return Response(
            {"message": "Ro'yxatdan o'tdingiz. Tasdiqlash kodi emailingizga yuborildi."},
            status=status.HTTP_201_CREATED,
        )


class VerifyCodeView(APIView):
    """
    POST /api/accounts/verify/
    Tasdiqlash kodini tekshirish va JWT token berish.
    """

    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]
        purpose = serializer.validated_data.get("purpose", "register")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Foydalanuvchi topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        verify_obj = CodeVerify.objects.filter(
            user=user, code=code, purpose=purpose, is_used=False
        ).first()

        if not verify_obj:
            return Response(
                {"error": "Kod noto'g'ri yoki allaqachon ishlatilgan!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if verify_obj.is_expired:
            return Response(
                {"error": "Kodning amal qilish vaqti tugagan!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        verify_obj.is_used = True
        verify_obj.save()

        user.is_verified = True
        user.is_active = True
        user.save(update_fields=["is_verified", "is_active"])

        tokens = get_tokens_for_user(user)
        return Response(
            {"message": "Akkount muvaffaqiyatli tasdiqlandi!", **tokens},
            status=status.HTTP_200_OK,
        )


class GetNewCodeView(APIView):
    """
    POST /api/accounts/get-new-code/
    Yangi tasdiqlash kodi yuborish.
    """

    def post(self, request):
        serializer = GetNewCodeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]
        purpose = request.data.get("purpose", "register")

        user = User.objects.get(email=email)

        # Eski kodlarni o'chirish
        CodeVerify.objects.filter(user=user, is_used=False).update(is_used=True)

        # Yangi kod yaratish va yuborish
        new_code_obj = CodeVerify.objects.create(user=user, purpose=purpose)
        send_email_verification(user.email, new_code_obj.code, purpose=purpose)

        return Response(
            {"message": "Yangi tasdiqlash kodi emailingizga yuborildi."},
            status=status.HTTP_200_OK,
        )


class LoginView(APIView):
    """
    POST /api/accounts/login/
    Email yoki telefon raqam bilan login.
    """

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data["user"]

        # Oxirgi kirgan vaqtni yangilash
        user.last_seen = timezone.now()
        user.save(update_fields=["last_seen"])

        # Faollik log
        log_activity(user, ActivityLog.ActionChoice.LOGIN, request)

        tokens = get_tokens_for_user(user)
        return Response(
            {"message": "Tizimga muvaffaqiyatli kirdingiz.", **tokens},
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """
    POST /api/accounts/logout/
    Tizimdan chiqish — refresh token blacklistga tushadi.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"error": "Refresh token taqdim etilmadi!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response(
                {"error": "Token yaroqsiz yoki allaqachon eskirgan!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        log_activity(request.user, ActivityLog.ActionChoice.LOGOUT, request)

        return Response(
            {"message": "Tizimdan muvaffaqiyatli chiqildi."},
            status=status.HTTP_205_RESET_CONTENT,
        )


# ─────────────────────────────────────────────
# PROFILE VIEWS
# ─────────────────────────────────────────────

class UserProfileView(APIView):
    """
    GET    /api/accounts/profile/  — Profilni ko'rish
    PUT    /api/accounts/profile/  — Profilni yangilash
    DELETE /api/accounts/profile/  — Akkauntni o'chirish (soft delete)
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        serializer = UserProfileUpdateSerializer(
            request.user, data=request.data, partial=True
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        log_activity(request.user, ActivityLog.ActionChoice.PROFILE_UPDATE, request)

        return Response(
            {
                "message": "Profil muvaffaqiyatli yangilandi.",
                "data": UserProfileSerializer(request.user).data,
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request):
        user = request.user
        user.is_active = False
        user.save(update_fields=["is_active"])
        return Response(
            {"message": "Akkaunt o'chirildi."},
            status=status.HTTP_200_OK,
        )


# ─────────────────────────────────────────────
# PASSWORD VIEWS
# ─────────────────────────────────────────────

class ChangePasswordView(APIView):
    """
    POST /api/accounts/password/change/
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password", "updated_at"])

        log_activity(user, ActivityLog.ActionChoice.PASSWORD_CHANGE, request)

        return Response(
            {"message": "Parol muvaffaqiyatli o'zgartirildi. Qaytadan login qiling."},
            status=status.HTTP_200_OK,
        )


class ForgotPasswordView(APIView):
    """
    POST /api/accounts/password/forgot/
    """

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]
        user = User.objects.get(email=email)

        CodeVerify.objects.filter(user=user, is_used=False).update(is_used=True)

        code_obj = CodeVerify.objects.create(user=user, purpose=CodeVerify.PurposeChoice.RESET)
        send_email_verification(user.email, code_obj.code, purpose="reset")

        return Response(
            {"message": "Parolni tiklash kodi emailingizga yuborildi."},
            status=status.HTTP_200_OK,
        )


class ResetPasswordView(APIView):
    """
    POST /api/accounts/password/reset/
    """

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Foydalanuvchi topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        verify_obj = CodeVerify.objects.filter(
            user=user, code=code, purpose=CodeVerify.PurposeChoice.RESET, is_used=False
        ).first()

        if not verify_obj:
            return Response(
                {"error": "Kod noto'g'ri yoki allaqachon ishlatilgan!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if verify_obj.is_expired:
            return Response(
                {"error": "Kodning amal qilish vaqti tugagan!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        verify_obj.is_used = True
        verify_obj.save()

        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])

        return Response(
            {"message": "Parol muvaffaqiyatli tiklandi. Yangi parol bilan kiring."},
            status=status.HTTP_200_OK,
        )