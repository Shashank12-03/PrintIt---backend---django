from django.shortcuts import render
from .models import Shop
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .serializer import RegisterShopSerializer,EmailGetTokenSerializer
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Shop,Location,Images
from django.contrib.gis.geos import Point 
from django.core.files.storage import default_storage
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import TokenError 
from rest_framework_simplejwt.tokens import RefreshToken
from .services.shop_services import ShopService 
from django.contrib.gis.db.models.functions import Distance
from django.core.cache import cache
from user.services.user_services import UserService
from django.contrib.postgres.search import SearchVector
from django.db import transaction
from django.db.models import F, ExpressionWrapper, FloatField

# Create your views here.
class RegisterShopView(APIView):
    
    permission_classes = [AllowAny]
    
    def post(self,request):
        
        email = request.data.get('email')
        shop = Shop.objects.filter(email=email).first()
        
        if shop:
            return Response({'message':'shop is already register!!!'},status=status.HTTP_400_BAD_REQUEST)
        
        try:
            
            serializer = RegisterShopSerializer(data = request.data)
            if serializer.is_valid():
                shop = serializer.save()
                return Response({'message':'Shop registered lets move to more details now!!!'},status=status.HTTP_201_CREATED)
            else:
                return Response({'message':'Oops something went wrong with serializer !!!'},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            
            return Response({'message':'Oops something went wrong !!!','error':str(e)},status=status.HTTP_400_BAD_REQUEST)


class SignInView(APIView):
    
    permission_classes = [AllowAny]
    
    def post(self,request,*args, **kwargs):
        
        serializer = EmailGetTokenSerializer(data=request.data, context = {'request':request})
        
        try:
            email = request.data.get('email')
            password = request.data.get('password')
            
            if not email or not password:
                return Response({'message':'email or password missing'},status=status.HTTP_400_BAD_REQUEST)
            
            
            shop = ShopService.get_shop_by_email(email)
            if shop is None:
                return Response({'message':'shop doesnt exist try registration'},status=status.HTTP_404_NOT_FOUND)
                
            print(shop)
            
            if serializer.is_valid():
                token = serializer._validated_data
                return Response(token,status=status.HTTP_200_OK)
            
            return Response({'message':'serializer is not valid'},status=status.HTTP_400_BAD_REQUEST)
        except serializers.ValidationError as e:
            print(e)
            Response({'error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except TokenError as e:
            Response({'message':'something went wrong','error':e},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GetEmailTokenView(TokenObtainPairView):
    serializer_class = EmailGetTokenSerializer



class CheckLoginView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self,request):
        
        print(request.user)
        return Response({'message':'welcome to print it!!! lets start printing'})
    
    
class VerifyShopView(APIView):
    
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    
    def get(self,request):
        
        shop = ShopService.get_shop_by_id(request.user.id)
        if not shop:
            return Response({'error':'only shop can print'},status=status.HTTP_401_UNAUTHORIZED)
        data = {
            'id':shop.id,
            'name':shop.name,
        }
        return Response({'message':'user', 'shop':data},status=status.HTTP_200_OK)

class AddShopDetailedView(APIView):
    
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self,request):
        
        print(request.user)
        
        name = request.data.get('name')
        owner_name = request.data.get('owner_name')
        owner_number = request.data.get('owner_number')
        payment_modes = request.data.get('payment_modes')
        services = request.data.get('services')
        address = request.data.get('address')
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        
        
        shop = ShopService.get_shop_by_id(request.user.id)
        
        if shop is None:
            return Response({'message':'shop doesnt exist !!!'},status=status.HTTP_200_OK)
        
        try:
            with transaction.atomic():
                shop.refresh_from_db()
                location, _ = Location.objects.get_or_create(
                    address=address, 
                    geometry=Point(float(longitude), float(latitude)) 
                )
                shop.name = name
                shop.payment_modes = payment_modes
                shop.facilities = services
                shop.owner_name = owner_name
                shop.owner_number = owner_number
                shop.location = location
                shop.save()

            return Response({'message':'shop details saved!!!'},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message':'unable to make changes','error':str(e)},status=status.HTTP_400_BAD_REQUEST)



class AddImagesView(APIView):
    
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self,request):
        
        images = request.data.get('images')    
        
        shop = ShopService.get_shop_by_id(request.user.id)
        if shop is None:
            return Response({'message':'shop doesnt exist !!!'},status=status.HTTP_200_OK)
    
        try:
            with transaction.atomic():
                shop.refresh_from_db()
                shop.images = images
                shop.save()
    
            return Response({'message':'images added successfully!!!'},status=status.HTTP_200_OK)
    
        except Exception as e:
            return Response({'message':'unable to add images location','error':str(e)},status=status.HTTP_400_BAD_REQUEST)
        

class SignoutView(APIView):
    
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self,request,*args, **kwargs):
        
        refresh_token = request.data.get('refresh_token')
        
        if not refresh_token:
            return Response({'message':'need refresh token to signout'},status=status.HTTP_400_BAD_REQUEST)
        
        try:
            
            token = RefreshToken(refresh_token)
            print(token)
            token.blacklist()
            return Response({'message':'signed out'},status=status.HTTP_200_OK)
        
        except TokenError as e:
            return Response({'message': 'Invalid or expired refresh token', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({'message':'unable to sign out','error':str(e)},status=status.HTTP_400_BAD_REQUEST)


class DeleteAccountView(APIView):
    
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def delete(self,request):
            
        try:
            
            shop = ShopService.get_shop_by_id(request.user.id)
            if shop is not None:
                shop.delete()
                cache_key = f"shop_{request.user.id}"
                cache.delete(cache_key)
                
                return Response({'message':'shop deleted !!!'},status=status.HTTP_200_OK)
            
            else:
                return Response({'message':'shop doesnt exist'},status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            return Response({'message':'error cant delete shop','error':str(e)},status=status.HTTP_400_BAD_REQUEST)

class GetShopView(APIView):
    
    
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self,request,id):
        
        user = UserService.get_user_by_id(request.user.id)
        if not user:
            return Response({'message':'requested by not allowed user'},status=status.HTTP_400_BAD_REQUEST)
        
        shop = ShopService.get_shop_by_id(id)
        if shop is None:
            print('shop not found')
            return Response({'message':'shop doesnt exist !!!'},status=status.HTTP_400_BAD_REQUEST)
        
        try:
            data = {
                'shop_id':id,
                'shop_name':shop.name,
                'shop_address': shop.location.address,
                'owner_name':shop.owner_name,
                'owner_number':shop.owner_number,
                'shop_images':["https://content.jdmagicbox.com/v2/comp/bangalore/l2/080pxx80.xx80.160519151520.l1l2/catalogue/galaxies-enterprises-bangalore-0rt9ockuaa-250.jpg","https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQogIEhbS0Zn-1OSXPPnEhkuNCpN_Jqi_hJBQ&s","https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQxILCoOct2LvnWikhR8L46MOiYPbSnVv2rVg&s"],
                'location':{
                    "latitude": shop.location.geometry.y,
                    "longitude": shop.location.geometry.x
                } if shop.location else None,
                'shop_rating':shop.rating,
                'shop_facilites':shop.facilities,
                'shop_paymentmodes':shop.payment_modes, 
            }
            
            return Response({'shop':data},status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'message':'error occured','error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetShopListView(APIView):
    
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request):
        user = UserService.get_user_by_id(request.user.id)
        if not user:
            return Response({'message': 'requested by not allowed user'}, status=status.HTTP_400_BAD_REQUEST)
         
        longitude = request.query_params.get('longitude')
        # longitude = request.data.get('longitude')
        latitude = request.query_params.get('latitude')
        # latitude = request.data.get('latitude')
        if not longitude or not latitude:
            return Response({'message': 'location required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:    
            user_location = Point(float(longitude), float(latitude), srid=4326)
            
            # shops = Shop.objects.select_related("location").annotate(
            #     distance=Distance('location__geometry', user_location)
            # ).order_by('distance')
            # print(shops)
            # shops = Shop.objects.select_related("location").annotate(
            #     distance=Distance('location__geometry', user_location)
            # ).order_by('distance').values_list('id','name','rating','location__address','images__images')
            shops = Shop.objects.select_related("location")\
            .annotate(distance_m=Distance('location__geometry', user_location))\
            .annotate(
                distance_km=ExpressionWrapper(
                    F('distance_m') / 1000.0,
                    output_field=FloatField()
                )
            ).order_by('distance_m')\
            .values('id', 'name', 'rating', 'location__address', 'images__images', 'distance_km')
            # print(shops)
            # shop_list = getList(shops)
            return Response({'shop_list': shops}, status=status.HTTP_200_OK)
        
        except Exception as e:
            print(str(e))
            return Response({'message': 'error occurred', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

def getList(shops):
    return [
        {
            'shop_id': shop.id, 
            'shop_name': shop.name,
            'shop_rating': shop.rating,
            'shopImages': "https://content.jdmagicbox.com/v2/comp/bangalore/l2/080pxx80.xx80.160519151520.l1l2/catalogue/galaxies-enterprises-bangalore-0rt9ockuaa-250.jpg",
            'shop_address': shop.location.address if shop.location.address else None,  # Access without additional DB queries
            'distance_km': shop.distance.km if shop.distance else None
        }
        for shop in shops
    ]



# forgot password 
# update account
# search shop
# shop qr 
# check sign in sign out
# shop opened tag need to alter tag

