from ..models import Shop
from django.core.cache import cache

class ShopService():
    
    @staticmethod
    def get_shop_by_id(shop_id):
        
        cache_key = f"shop_{shop_id}"
        shop = cache.get(cache_key)
        
        if shop is None:
            try:
                shop = Shop.objects.filter(shop_id).first()
                cache.set(cache_key,shop,timeout=3600)
                
            except Shop.DoesNotExist as e:
                print(e)
                return None
        
        return shop
    
    @staticmethod
    def get_shop_by_email(email):
        
        cache_key = f"shop_{email}"
        shop = cache.get(cache_key)
        
        if shop is None:
            try:
                shop = Shop.objects.filter(email).first()
                cache.set(cache_key,shop,timeout=3600)
                
            except Shop.DoesNotExist as e:
                print(e)
                return None
        
        return shop
    