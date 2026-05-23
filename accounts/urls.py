from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView, 
    VerifyCodeView, 
    GetNewCodeView, 
    UserProfileView,  
    LogoutView,
    ChangePasswordView,   
    ForgotPasswordView,   
    ResetPasswordView     
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify/', VerifyCodeView.as_view(), name='verify'),
    path('get-new-code/', GetNewCodeView.as_view(), name='get_new_code'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('password/change/', ChangePasswordView.as_view(), name='password_change'),
    path('password/forgot/', ForgotPasswordView.as_view(), name='password_forgot'),
    path('password/reset/', ResetPasswordView.as_view(), name='password_reset'),
]