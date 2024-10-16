# from django.db import models
from user.models import CustomUserModel
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
# Create your models here.

class Service(models.Model):
    facility = models.CharField(max_length=100,blank=True,default=None)
    price = models.DecimalField(max_digits=4,decimal_places=2)
    
class Location(models.Model):
    address = models.CharField(max_length=400,default=None,required=True)
    location = models.PointField(geography=True,default=None)
    updated_at = models.DateTimeField(auto_now=True)

class Images(models.Model):
    photo = models.ImageField(upload_to='media/shops')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    

class Shop(CustomUserModel):
    email = models.EmailField(max_length=100,required=True,unique=True)
    name = models.CharField(max_length=200)
    gstIn = models.CharField(max_length=50,unique=True)
    rating = models.DecimalField(max_digits=1,default=3)
    payment_modes = ArrayField(
        models.CharField(), blank=True, default=list
    )
    images = models.ForeignKey(Images,on_delete=models.CASCADE, related_name='photos')
    services = models.ForeignKey(Service,on_delete=models.CASCADE)
    location = models.ForeignKey(Location,on_delete=models.CASCADE)