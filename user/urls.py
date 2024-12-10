from django.urls import path
from .views import GoogleLoginView, CheckLogin,loginView

urlpatterns = [
    path('login/',GoogleLoginView.as_view()),
    path('',CheckLogin.as_view()),
    path('loginView/',loginView)
]
