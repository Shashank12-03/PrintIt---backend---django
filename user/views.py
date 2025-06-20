from tokenize import TokenError
from django.shortcuts import render
from google.oauth2 import id_token
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import GoogleSignInSerializer
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import User
import os
from rest_framework import status
from django.conf import settings
from rest_framework.permissions import AllowAny
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework_simplejwt.tokens import RefreshToken
import requests
from .services.user_services import UserService
from django.contrib.postgres.search import SearchVector
from shops.views import getList
from shops.models import Shop
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point 
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import EmailGetTokenSerializer
from rest_framework_simplejwt.views import TokenRefreshView
from django.db import transaction

class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = "https://auth.expo.io/@shashank1203/printit-user"
    client_class = OAuth2Client



class GoogleLoginCallbackView(APIView):
    
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # Step 1: Get the ID token from the request body
        access_token = request.data.get("token")
        print(access_token)
        
        if not access_token:
            return Response({"error": "Access token not provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Step 2: Verify the token with Google and get user info
        google_user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(google_user_info_url, headers=headers)

        if response.status_code != 200:
            return Response({"error": "Invalid access token"}, status=status.HTTP_400_BAD_REQUEST)

        user_info = response.json()
        email = user_info.get("email")
        print(email)
        if not email:
            return Response({"error": "Email not provided by Google"}, status=status.HTTP_400_BAD_REQUEST)

        user, created = User.objects.get_or_create(email=email)
        if created:
            user.set_unusable_password()  
            user.save()

        refresh = RefreshToken.for_user(user)
        token_data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

        return Response(
            {
                "user": {"id":user.id,"email": user.email, "name": user_info.get("name"), "picture": user_info.get("picture")},
                "token": token_data,
            },
            status=status.HTTP_200_OK,
        )

class CheckLogin(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(request):
        return Response({'message':'authentication successful!!! hello!!!!'},status.HTTP_200_OK)
    
    
class LoginView(APIView):
    
    permission_classes = [AllowAny]
    
    def get(self, request):
        try:
            data = {
                "google_callback_uri": settings.GOOGLE_OAUTH_CALLBACK_URL,
                "google_client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            }
            return Response({'message':'login page','credentials':data},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message':'error occured','error':str(e)},status=status.HTTP_400_BAD_REQUEST)

class RegisterUserView(APIView):
        
    permission_classes = [AllowAny]
    
    def post(self,request):
        
        email = request.data.get('email')
        password = request.data.get('password')
        print(email,password)
        if not email or not password:
            return Response({'message':'email and password required'},status=status.HTTP_400_BAD_REQUEST)
        
        try:
            
            user = User.objects.create_user(email=email,password=password)
            user.save()
            print(user)
            return Response({'message':'user created'},status=status.HTTP_200_OK)
        
        except Exception as e:
            print(str(e))
            return Response({'error':'error occured','error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GetEmailTokenView(TokenObtainPairView):
    serializer_class = EmailGetTokenSerializer
    

class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]
    
 
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
class SetUserview(APIView):
    
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self,request):
        
        user = UserService.get_user_by_id(request.user.id)
        
        if not user:
            return Response({'message':'requested by not allowed user'},status=status.HTTP_400_BAD_REQUEST)
        
        try:
            
            name = request.data.get('name', user.name)
            mobile_no = request.data.get('mobile_no',user.mobile_no)
            profile_photo = request.data.get('profile_photo',user.profile_photo)
            user.name = name
            user.mobile_no = mobile_no
            user.profile_photo = profile_photo
            user.save()
            
            
            return Response({'message':'user data saved'},status=status.HTTP_200_OK)
        
        except Exception as e:
            
            return Response({'error':'error occured','error':str(e)},status=status.HTTP_400_BAD_REQUEST) 


class GetuserView(APIView):
    
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self,request):
        
        user = UserService.get_user_by_id(request.user.id)
        if not user:
            return Response({'message':'requested by not allowed user'},status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                user = UserService.get_user_by_id(request.user.id) 
                user.refresh_from_db()
                data = {
                        'id':user.id,
                        'email':user.email,
                        'name':user.name,
                        'image':user.profile_photo,
                        'mobile_no':user.mobile_no,
                    }
            
            return Response({'user':data},status=status.HTTP_200_OK)
        
        except Exception as e:
            
            return Response({'error':'error occured','error':str(e)},status=status.HTTP_400_BAD_REQUEST) 
        
        
class VerifyUserView(APIView):
    
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    
    def get(self,request):
        
        user = UserService.get_user_by_id(request.user.id)
        if not user:
            return Response({'error':'only user can send document'},status=status.HTTP_401_UNAUTHORIZED)
        
        data = {
            'id':user.id,
            'name':user.name,
        }
        return Response({'message':'user', 'user':data},status=status.HTTP_200_OK)
    
    
class SearchShopView(APIView): 
    
    permission_classes = [IsAuthenticated] 
    authentication_classes = [JWTAuthentication] 
    
    def get(self,request): 
        
        user = UserService.get_user_by_id(request.user.id) 
        if not user: 
            return Response({'message':'Only users are allowed to search shop'},status=status.HTTP_401_UNAUTHORIZED) 
        
        longitude = request.data.get('longitude')
        latitude = request.data.get('latitude')
        
        if not longitude or not latitude:
            return Response({'message':'location required'},status=status.HTTP_400_BAD_REQUEST)
        
        searchStirng = request.query_params.get('search') 
        print(searchStirng) 
        
        try: 
            
            user_location = Point(float(longitude), float(latitude), srid=4326)
            shops = Shop.objects.annotate(
                search=SearchVector("name","location__address")
                ).annotate(distance = Distance('location__geometry', user_location)).filter(search=searchStirng).values('id', 'name', 'rating', 'location__address', 'images__images', 'distance_km') 
            
            shop_list = getList(shops) 
            return Response({'shop_list':shop_list},status=status.HTTP_200_OK) 
        
        except Exception as e: 
            
            return Response({'message':'error occured','error':str(e)},status=status.HTTP_400_BAD_REQUEST)
