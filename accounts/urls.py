from django.urls import path
from .views import RegisterView, VerifyCodeView ,GetNewCodeView, ChangeProfileInfoView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify/', VerifyCodeView.as_view(), name='verify'),
    path('get-new-code/', GetNewCodeView.as_view(), name='get_new_code'),
    path('profile/update/', ChangeProfileInfoView.as_view(), name='profile_update'),
    
    
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]