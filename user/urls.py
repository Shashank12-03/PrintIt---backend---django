from django.urls import path
from .views import GoogleLoginCallbackView, CheckLogin,LoginView,GoogleLoginView,SetUserview,GetuserView
from shops.views import SignoutView
urlpatterns = [
    path("api/v1/auth/google/", GoogleLoginView.as_view(), name="google_login"),
    path('auth/callback', GoogleLoginCallbackView.as_view()),
    path('',CheckLogin.as_view()),
    path('login/',LoginView.as_view(),name='google_sign_in'),
    path("sign-out", SignoutView.as_view()),
    path('add-user-details', SetUserview.as_view()),
    path('get-user', GetuserView.as_view()),
]
