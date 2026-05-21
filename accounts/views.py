from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    SignUpSerializer, 
    VerifyCodeSerializer, 
    GetNewCodeSerializer, 
    UserProfileUpdateSerializer
)
from .models import CodeVerify

User = get_user_model()

class RegisterView(APIView):

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            code_obj = CodeVerify.objects.create(user=user)
            
            return Response({
                "message": "Ro'yxatdan o'tdingiz. Tasdiqlash kodi yuborildi.",
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
    """2. GET NEW CODE API — Kod eskirgan bo'lsa yangi kod yuborish"""
    def post(self, request):
        serializer = GetNewCodeSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            
           
            CodeVerify.objects.filter(user=user, is_used=False).update(is_used=True)
            
          
            new_code_obj = CodeVerify.objects.create(user=user)
            
            return Response({
                "message": "Yangi tasdiqlash kodi yuborildi.",
                "code": new_code_obj.code  
            }, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangeProfileInfoView(APIView):
   
    permission_classes = [IsAuthenticated] 

    def put(self, request):
       
        serializer = UserProfileUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Profil ma'lumotlari muvaffaqiyatli yangilandi.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)