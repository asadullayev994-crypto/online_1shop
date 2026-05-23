import requests
from .models import CodeVerify
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    GetNewCodeSerializer,
    ResetPasswordSerializer,
    SignUpSerializer,
    UserProfileUpdateSerializer,
    VerifyCodeSerializer,
)


User = get_user_model()


def send_telegram_verification(user_email, code):
    BOT_TOKEN = "8713199732:AAEAJFVOFRppdpjxCFm7OztG4wncj1z6gts"
    CHAT_ID = "**********" 
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    message = (
        f"🔔 <b>ONLINE SHOP</b>\n\n"
        f"👤 <b>Foydalanuvchi:</b> {user_email}\n"
        f"🔑 <b>Tasdiqlash kodi:</b> <code>{code}</code>\n\n"
        f"<i>Kodni hech kimga bermang!</i>"
    )
    
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"Telegram botga xabar yuborishda xatolik yuz berdi: {e}")
        return False


class RegisterView(APIView):
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            code_obj = CodeVerify.objects.create(user=user)
            
            send_telegram_verification(user.email, code_obj.code)
            
            return Response({
                "message": "Ro'yxatdan o'tdingiz. Tasdiqlash kodi Telegram botingizga yuborildi.",
                "code": code_obj.code 
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyCodeView(APIView):
    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']
            
            try:
                user = User.objects.get(email=email)
                verify_obj = CodeVerify.objects.filter(user=user, code=code, is_used=False).first()
                
                if not verify_obj:
                    return Response({"error": "Kod noto'g'ri yoki allaqachon ishlatilgan!"}, status=status.HTTP_400_BAD_REQUEST)
                
                if verify_obj.is_expired:
                    return Response({"error": "Kodning amal qilish vaqti tugagan!"}, status=status.HTTP_400_BAD_REQUEST)
                
                verify_obj.is_used = True
                verify_obj.save()
                
                user.is_verified = True
                user.is_active = True
                user.save()
                
                refresh = RefreshToken.for_user(user)
                return Response({
                    "message": "Akkount muvaffaqiyatli tasdiqlandi!",
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                }, status=status.HTTP_200_OK)
                
            except User.DoesNotExist:
                return Response({"error": "Foydalanuvchi topilmadi"}, status=status.HTTP_404_NOT_FOUND)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetNewCodeView(APIView):
    def post(self, request):
        serializer = GetNewCodeSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            
            CodeVerify.objects.filter(user=user, is_used=False).update(is_used=True)
            
            new_code_obj = CodeVerify.objects.create(user=user)
            
            send_telegram_verification(user.email, new_code_obj.code)
            
            return Response({
                "message": "Yangi tasdiqlash kodi Telegram botingizga yuborildi.",
                "code": new_code_obj.code  
            }, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

   
    def get(self, request):
        serializer = UserProfileUpdateSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

   
    def put(self, request):
        serializer = UserProfileUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Profil ma'lumotlari muvaffaqiyatli yangilandi.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"error": "Refresh token taqdim etilmadi!"}, status=status.HTTP_400_BAD_REQUEST)
                
            token = RefreshToken(refresh_token)
            token.blacklist()  

            return Response({"message": "Tizimdan muvaffaqiyatli chiqildi (Logout)."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "Token yaroqsiz yoki allaqachon eskirgan!"}, status=status.HTTP_400_BAD_REQUEST)
        
        
        
        
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({"old_password": ["Eski parol noto'g'ri."]}, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"message": "Parol muvaffaqiyatli o'zgartirildi."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            
       
            CodeVerify.objects.filter(user=user, is_used=False).update(is_used=True)
            
           
            code_obj = CodeVerify.objects.create(user=user)
            
           
            send_telegram_verification(user.email, code_obj.code)
            
            return Response({
                "message": "Parolni tiklash kodi Telegram botingizga yuborildi.",
                "code": code_obj.code
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']
            
            try:
                user = User.objects.get(email=email)
                verify_obj = CodeVerify.objects.filter(user=user, code=code, is_used=False).first()
                
                if not verify_obj:
                    return Response({"error": "Kod noto'g'ri yoki allaqachon ishlatilgan!"}, status=status.HTTP_400_BAD_REQUEST)
                
                if verify_obj.is_expired:
                    return Response({"error": "Kodning amal qilish vaqti tugagan!"}, status=status.HTTP_400_BAD_REQUEST)
                
             
                verify_obj.is_used = True
                verify_obj.save()
                
                
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                
                return Response({"message": "Parol muvaffaqiyatli tiklandi. Yangi parol bilan tizimga kirishingiz mumkin."}, status=status.HTTP_200_OK)
                
            except User.DoesNotExist:
                return Response({"error": "Foydalanuvchi topilmadi"}, status=status.HTTP_404_NOT_FOUND)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)