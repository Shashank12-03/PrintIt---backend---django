# from django.db import models
from user.models import CustomUserModel
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from .storage import ShopImageStorage
import datetime
# Create your models here.


class Location(models.Model):
    address = models.CharField(max_length=400,default=None)
    geometry = models.PointField(geography=True,default=None)
    updated_at = models.DateTimeField(auto_now=True)

    

class Shop(CustomUserModel):
    name = models.CharField(max_length=200)
    owner_name = models.CharField(max_length=200,blank=True,null=True)
    owner_number = models.CharField(max_length=10,blank=True,null=True)
    rating = models.DecimalField(max_digits=5, decimal_places=1,default=3)
    payment_modes = ArrayField(
        models.CharField(), blank=True, default=list,null=True
    )
    facilities = models.JSONField(default=dict,null=True, blank=True)
    location = models.OneToOneField(Location,on_delete=models.CASCADE,null=True, related_name='shops')
    rated = models.IntegerField(default=0,null=True,blank=True)
    
class Images(models.Model):
    image = models.ImageField(upload_to='',storage=ShopImageStorage())
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="images")
    file_location = models.URLField(default='')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    format = models.CharField(max_length=10, null=True, blank=True)
    content_type = models.CharField(max_length=50, null=True, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)  