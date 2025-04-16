from django.shortcuts import render
from user.services.user_services import UserService
from shops.services.shop_services import ShopService
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from .models import Interaction, UserInteraction, UserFavourite
from django.db import transaction
from .serializer import AddInteractionSerializer
# Create your views here.

class RateShopView(APIView):
    
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self,request,id):
        
        user = UserService.get_user_by_id(request.user.id)
        if not user:
            return Response({'message':'Only user is allowed to rate the shop'},status=status.HTTP_401_UNAUTHORIZED)
        
        user_rated = request.data.get('rating')
        if not user_rated:
            return Response({'message':'Need rating from user'},status=status.HTTP_401_UNAUTHORIZED)
            
        try:
            with transaction.atomic():
            
                shop = ShopService.get_shop_by_id(id)
                shop.refresh_from_db()
                rated = shop.rated
                shop_rating = shop.rating
                rating = shop_rating * rated
                rating += user_rated
                rated += 1
                rating = rating / rated
                shop.rating = rating
                shop.rated = rated
                shop.save()
                
                print("Shop after update:", shop)
                    
            return Response({'message':'shop rated','rating':rating})
        
        except Exception as e:
            
            return Response({'error':'error occured','error':str(e)},status=status.HTTP_400_BAD_REQUEST) 
        
        

class AddInteractionView(APIView):
    
    permission_classes = [AllowAny]
    
    def post(self,request):
        
        try:
            
            user_id = request.data.get('user_id')
            shop_id = request.data.get('shop_id')
            files = request.data.get('files')
            if not user_id or not shop_id:
                return Response({'message':'Need user_id and shop_id'},status=status.HTTP_401_UNAUTHORIZED)
            
            interaction = Interaction.objects.create(user_id=user_id,shop_id=shop_id)
            interaction.save()
            user_interaction =  UserInteraction.objects.create(interaction=interaction,files=files)
            user_interaction.save()
            
            return Response({'message':'Interaction added'},status=status.HTTP_200_OK)
            
        except Exception as e:
            
            return Response({'error':'error occured','error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
        
class AddFavouriteShopView(APIView):
    
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self,request):
        
        try:
            user_id = request.user.id
            shop_id = request.data.get('shop_id')
            if not shop_id:
                return Response({'message':'Need shop_id'},status=status.HTTP_401_UNAUTHORIZED)
            
            is_present = UserFavourite.objects.filter(user_id=user_id,shop_id=shop_id).exists()
            
            if is_present:
                return Response({'message':'Shop already in favourite'},status=status.HTTP_400_BAD_REQUEST)
            
            favourite = UserFavourite.objects.create(user_id=user_id,shop_id=shop_id)
            favourite.save()
            
            return Response({'message':'Favourite shop added'},status=status.HTTP_200_OK)
        
        except Exception as e:
            
            return Response({'error':'error occured','error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class getFavouriteShopView(APIView):
    
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self,request):
        
        try:
            user_id = request.user.id
            favourites = UserFavourite.objects.filter(user_id=user_id).values('shop__id','shop__name','shop__images__images','shop__rating','shop__location__address')
            print("Favourites:",favourites)
            
            return Response({'favourites':favourites},status=status.HTTP_200_OK)
        
        except Exception as e:
            
            return Response({'error':'error occured','error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class getUserHistoryView(APIView):
    
    def get(self, request):
        
        try:
            user_id = request.user.id
            userInteractions = UserInteraction.objects.filter(interaction__user_id=user_id).values_list('id','interaction__shop__name','interaction__shop__id','files')
            print("Interactions:",userInteractions)
            return Response({'interactions':userInteractions},status=status.HTTP_200_OK)
        
        except Exception as e:
            
            return Response({'error':'error occured','error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class getShopHistoryView(APIView):
    
    def get(self, request):
        
        try:
            shop_id = request.data.get('shop_id')
            interactions = Interaction.objects.filter(shop_id=shop_id)
            return Response({'interactions':interactions},status=status.HTTP_200_OK)
        
        except Exception as e:
            
            return Response({'error':'error occured','error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)