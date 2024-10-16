from django.urls import path
from .views import GoogleLoginView, CheckLogin

urlpatterns = [
    path('login',GoogleLoginView.as_view()),
    path('check',CheckLogin.as_view()),
]
