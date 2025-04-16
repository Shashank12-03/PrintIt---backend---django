from django.urls import path
from .views import RateShopView, AddInteractionView, AddFavouriteShopView, getFavouriteShopView, getUserHistoryView, getShopHistoryView 
urlpatterns = [
    path('rate-shop/<int:id>',RateShopView.as_view()),
    path('add-interaction',AddInteractionView.as_view()),
    path('add-favourite-shop',AddFavouriteShopView.as_view()),
    path('get-favourite-shops',getFavouriteShopView.as_view()),
    path('get-user-history',getUserHistoryView.as_view()),
    path('get-shop-history',getShopHistoryView.as_view()),
]
