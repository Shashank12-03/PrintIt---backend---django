from django.urls import path
from .views import (
    GoogleLoginCallbackView,
    CheckLogin,
    LoginView,
    GoogleLoginView,
    SetUserview,
    GetuserView,
    VerifyUserView,
    SearchShopView,
    RegisterUserView,
    GetEmailTokenView,
    CustomTokenRefreshView,
    SignoutView
)
from shops.views import SignoutView

urlpatterns = [
    path("api/v1/auth/google/", GoogleLoginView.as_view(), name="google_login"),
    path("email-login",RegisterUserView.as_view()),
    path("auth", GoogleLoginCallbackView.as_view()),
    path("get-token", GetEmailTokenView.as_view()),
    path('token-refresh', CustomTokenRefreshView.as_view()),
    path("", CheckLogin.as_view()),
    path("login/", LoginView.as_view()),
    path("sign-out", SignoutView.as_view()),
    path("add-user-details", SetUserview.as_view()),
    path("get-user", GetuserView.as_view()),
    path("verify-user", VerifyUserView.as_view()),
    path("search-shop/", SearchShopView.as_view()),
]
