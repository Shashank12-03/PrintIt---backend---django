from django.shortcuts import render
from user.services.user_services import UserService
from shops.services.shop_services import ShopService
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from .models import Interaction
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
        
        
# add the shop in user history
# add the user in shop history
# get list of shops user interacted
# get list of users interacted with shops

class AddInteractionView(APIView):
    
    permission_classes = [AllowAny]
    
    def post(self,request):
        
        try:
            
            serializer = AddInteractionSerializer(request.data)
            if serializer.is_valid():
                interaction = serializer.save()
                return Response({'message':'interaction added'},status=status.HTTP_200_OK)
            
            return Response({'message':'something went wrong'},status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            
            return Response({'error':'error occured','error':str(e)},status=status.HTTP_400_BAD_REQUEST) 