from ..models import Shop
from django.core.cache import cache

class ShopService():
    
    @staticmethod
    def get_shop_by_id(shop_id):
        
        cache_key = f"shop_{shop_id}"
        shop = cache.get(cache_key)
        
        if shop is None:
            try:
                shop = Shop.objects.filter(id = shop_id).first()
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
                shop = Shop.objects.filter(email=email).first()
                cache.set(cache_key,shop,timeout=3600)
                
            except Shop.DoesNotExist as e:
                print(e)
                return None
        
        return shop
    
    @staticmethod
    def get_shops_by_ids(ids):
        cache_key = f"shops_{'_'.join(map(str, ids))}"
        shops = cache.get(cache_key)
        
        if shops is None:
            shops = []
            for shop_id in ids:
                shop_cache_key = f"shop_{shop_id}"
                shop = cache.get(shop_cache_key)
                
                if shop is None:
                    shop = Shop.objects.filter(id=shop_id).values('id', 'name', 'address', 'rating', 'images').first()
                    if shop:
                        cache.set(shop_cache_key, shop, timeout=3600)
            
            if shop:
                shops.append(shop)
            
            cache.set(cache_key, shops, timeout=None)  
        
        return shops