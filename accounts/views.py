from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .serializers import SignUpSerializer, VerifyCodeSerializer
from .models import CodeVerify
from rest_framework_simplejwt.tokens import RefreshToken



User = get_user_model()

class RegisterView(APIView):
       def post(self, request):
           
           serializer = SignUpSerializer(data=request.data)
           if serializer.is_view_valid if hasattr(serializer, 'is_view_valid') else serializer.is_valid():
            user = serializer.save()
            
         
            code_obj = CodeVerify.objects.create(user=user)
            
            return Response({
                "message": "Ro'yxatdan o'tdingiz. Tasdiqlash kodi yuborildi.",
                "code": code_obj.code 
            }, status=status.HTTP_210_CREATED if hasattr(status, 'HTTP_210_CREATED') else status.HTTP_201_CREATED)
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
                    return Response({"error": "Kod noto'g'ri!"}, status=status.HTTP_400_BAD_REQUEST)
                
                if verify_obj.is_expired:
                    return Response({"error": "Kodning vaqti tugagan!"}, status=status.HTTP_400_BAD_REQUEST)
                
             
                verify_obj.is_used = True
                verify_obj.save()
                
                user.is_verified = True
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