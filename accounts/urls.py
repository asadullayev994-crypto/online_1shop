from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    ChangePasswordView,
    ForgotPasswordView,
    GetNewCodeView,
    LoginView,
    LogoutView,
    RegisterView,
    ResetPasswordView,
    UserProfileView,
    VerifyCodeView,
)

urlpatterns = [
    # Auth
    path("register/", RegisterView.as_view(), name="register"),
    path("verify/", VerifyCodeView.as_view(), name="verify"),
    path("get-new-code/", GetNewCodeView.as_view(), name="get_new_code"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Profile
    path("profile/", UserProfileView.as_view(), name="user_profile"),

    # Password
    path("password/change/", ChangePasswordView.as_view(), name="password_change"),
    path("password/forgot/", ForgotPasswordView.as_view(), name="password_forgot"),
    path("password/reset/", ResetPasswordView.as_view(), name="password_reset"),
]