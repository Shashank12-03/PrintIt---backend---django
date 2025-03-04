from django.db import models
from shops.models import Shop
from user.models import User
from django.contrib.postgres.fields import ArrayField


class Interaction(models.Model):
    
    shop = models.ForeignKey(Shop,on_delete=models.CASCADE,related_name='shop_interaction')
    user = models.ForeignKey(User,on_delete=models.CASCADE, null=True, related_name='user_interaction')
    timing = models.DateTimeField(auto_now_add=True)
    
    
class UserInteraction(models.Model):
    interaction = models.ForeignKey(Interaction, on_delete=models.CASCADE, related_name='interactions')
    files = ArrayField(models.CharField(max_length=200, blank=True, default=list, null=True))
    
class UserFavourite(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, null=True, related_name='favorite_hotels')
    shop = models.ForeignKey(Shop,on_delete=models.CASCADE, related_name='favorited_by')
    