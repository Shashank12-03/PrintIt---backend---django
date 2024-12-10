from .views import (
    RegisterShopView,
    GetEmailTokenView,
    CheckLoginView,
    SetLocationView,
    AddImagesView,
    GetShopDetailedView,
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
    path("add-details", GetShopDetailedView.as_view()),
    path("add-location", SetLocationView.as_view()),
    path("add-photos", AddImagesView.as_view()),
]
