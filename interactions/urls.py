from django.urls import path
from .views import RateShopView,AddInteractionView
urlpatterns = [
    path('rate-shop/<int:id>',RateShopView.as_view()),
    path('add-interaction',AddInteractionView.as_view()),
]
