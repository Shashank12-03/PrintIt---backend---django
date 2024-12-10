from django.contrib.auth.backends import BaseBackend
from .models import Shop



class ShopAuthenticationBackend(BaseBackend):
    
    def authenticate(self, request, username = None, password = None, **kwargs):
        try:
            shop = Shop.objects.get(email=username)
            if shop.check_password(password):
                return shop
        except Shop.DoesNotExist:
            return None
        
    def get_user(self,shop_id):
        try:
            return Shop.objects.get(pk = shop_id)
        except Shop.DoesNotExist:
            return None
