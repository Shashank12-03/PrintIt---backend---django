from rest_framework import serializers
from .models import Interaction
from user.services.user_services import UserService
from shops.services.shop_services import ShopService

class AddInteractionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Interaction
        fields = ['shop','user','timing','files']
        
    
    def create(self, validated_data):
        if validated_data:
            userId = validated_data.pop('userId')
            shopId = validated_data.pop('userId')
            files = validated_data.pop('files')
            
            if not userId or not shopId or not files:
                return serializers.ValidationError({'message':'Either of three are not in the body'})
            
            shop = ShopService.get_shop_by_id(shopId)
            user = UserService.get_user_by_id(userId)
            
            if not shop or not user:
                return serializers.ValidationError({'message':'either of shop or user is not in the db'})
            
            interaction = Interaction.objects.create(shop = shop, user = user, files = files)
            return interaction
        
        return serializers.ValidationError({'message':'interaction not created'})
        
