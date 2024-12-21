from ..models import User
from django.core.cache import cache


class UserService():
    
    @staticmethod
    def get_user_by_id(user_id):
        
        cache_key = f"user_{user_id}"
        user = cache.get(cache_key)
        if user is None:
            try:
                print("from db")
                user = User.objects.filter(id = user_id).first()
                cache.set(cache_key,user,timeout=3600)
                
            except User.DoesNotExist as e:
                print(e)
                return None
        return user
