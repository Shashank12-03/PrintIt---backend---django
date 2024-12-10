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
from django.core.cache import cache
# Create your views here.
class RegisterShopView(APIView):
    
    permission_classes = [AllowAny]
    
    def post(self,request):
        
        serializer = RegisterShopSerializer(data = request.data)
        if serializer.is_valid():
            shop = serializer.save()
            return Response({'message':'Shop registered lets move to more details now!!!'},status=status.HTTP_201_CREATED)
        
        return Response({'message':'Oops something went wrong !!!'},status=status.HTTP_400_BAD_REQUEST)
    

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
            Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)
        
        except TokenError as e:
            Response({'message':'something went wrong','error':e},status=status.HTTP_400_BAD_REQUEST)
        
class GetEmailTokenView(TokenObtainPairView):
    serializer_class = EmailGetTokenSerializer



class CheckLoginView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self,request):
        
        print(request.user)
        return Response({'message':'welcome to print it!!! lets start printing'})
    
class GetShopDetailedView(APIView):
    
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self,request):
        
        print(request.user)
        
        name = request.data.get('name')
        payment_modes = request.data.get('payment_modes')
        services = request.data.get('services')
        
        shop = ShopService.get_shop_by_id(request.user.id)
        
        if shop is not None:
            try:
                shop.name = name
                shop.payment_modes = payment_modes
                shop.facilities = services
                shop.save()
                print(shop)
                return Response({'message':'shop name, payment modes and services saved!!!'},status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'message':'unable to make changes','error':str(e)},status=status.HTTP_400_BAD_REQUEST)
        else:
            
            return Response({'message':'shop doesnt exist !!!'},status=status.HTTP_200_OK)


class SetLocationView(APIView):
    
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self, request):
        address = request.data.get('address')
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        
            
        shop = ShopService.get_shop_by_id(request.user.id)
        
        if shop is not None:
            try:
                location, created = Location.objects.get_or_create(
                    address=address, 
                    location=Point(float(longitude), float(latitude)) 
                )
                shop.location = location
                shop.save()
                print(shop)
                return Response({'message':'shop location saved!!!'},status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'message':'unable to save location','error':str(e)},status=status.HTTP_400_BAD_REQUEST)
        else:
            
            return Response({'message':'shop doesnt exist !!!'},status=status.HTTP_404_NOT_FOUND)
        

class AddImagesView(APIView):
    
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self,request):
        
        images = request.FILES.getlist('images')
        
        
        if not isinstance(request.user,Shop):
            return Response({'message':'operation allowed only for shops!!!'},status=status.HTTP_401_UNAUTHORIZED)
        
        shop = ShopService.get_shop_by_id(request.user.id)
    
        if shop is not None:
            try:
                
                image_path = shop.images if shop.images else []
                
                for image in images:
                    file_name = default_storage.save(f'media/shops/{image.name}',image)
                    image_path.append(file_name)
                
                photos = Images.objects.get_or_create(images = image_path) 
                shop.images = photos
                shop.save()
        
                return Response({'message':'images added successfully!!!'},status=status.HTTP_200_OK)
        
            except Exception as e:
                return Response({'message':'unable to add images location','error':str(e)},status=status.HTTP_400_BAD_REQUEST)
            
        else:
            return Response({'message':'shop doesnt exist'},status=status.HTTP_404_NOT_FOUND)
        

class SignoutView(APIView):
    
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self,request,*args, **kwargs):
        print(request.user)
        
        refresh_token = request.headers.get('Authorization')
        print(refresh_token)
        if not refresh_token:
            return Response({'message':'need refresh token to signout'},status=status.HTTP_400_BAD_REQUEST)
        
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message':'sign out'},status=status.HTTP_200_OK)
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


# forgot password
# update account
# get shop i,e shopcard shop info get
# get shops 
# check sign in sign out
