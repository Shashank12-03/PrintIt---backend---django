# from django.db import models
from user.models import CustomUserModel
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
# Create your models here.


class Location(models.Model):
    address = models.CharField(max_length=400,default=None)
    geometry = models.PointField(geography=True,default=None)
    updated_at = models.DateTimeField(auto_now=True)

class Images(models.Model):
    images = ArrayField(models.CharField(max_length=200), blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    

class Shop(CustomUserModel):
    name = models.CharField(max_length=200)
    rating =models.DecimalField(max_digits=5, decimal_places=1,default=3)
    payment_modes = ArrayField(
        models.CharField(), blank=True, default=list,null=True
    )
    facilities = models.JSONField(default=dict,null=True, blank=True)
    images = models.ForeignKey(Images,on_delete=models.CASCADE, related_name='photos',null=True)
    location = models.OneToOneField(Location,on_delete=models.CASCADE,null=True, related_name='shops')
    rated = models.IntegerField(default=0,null=True,blank=True)