from .models import Shop
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

class RegisterShopSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Shop
        fields = ['email','password']
        
    def create(self, validated_data):
        if validated_data:
            email = validated_data.pop('email')
            password = validated_data.pop('password')
            shop = Shop.objects.create_user(email=email,password=password,**validated_data)
            return shop
        
class EmailGetTokenSerializer(TokenObtainPairSerializer):
    
    def validate(self, attrs):
        
        email = attrs.get('email')
        password = attrs.get('password')
        
        self.shop = authenticate(request=self.context.get('request'),username=email,password=password, backend ='shops.backends.ShopAuthenticationBackend' )
        if not self.shop :
            return serializers.ValidationError((f'No active user found with {email}'),code='authentication')
        
        data ={}
        refresh = self.get_token(self.shop)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        
        return data
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        return token