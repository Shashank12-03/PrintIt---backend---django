from .views import (
    RegisterShopView,
    GetEmailTokenView,
    CheckLoginView,
    GetShopListView,
    GetShopView,
    AddImagesView,
    AddShopDetailedView,
    SignInView,
    SignoutView,
)
from django.urls import path

urlpatterns = [
    path("register", RegisterShopView.as_view()),
    path("token", GetEmailTokenView.as_view()),
    path("sign-in", SignInView.as_view()),
    path("sign-out", SignoutView.as_view()),
    path("check", CheckLoginView.as_view()),
    path("add-details", AddShopDetailedView.as_view()),
    path("get-shop/<int:id>", GetShopView.as_view()),
    path("get-shops", GetShopListView.as_view()),
]
