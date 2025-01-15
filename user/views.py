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
class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.GOOGLE_OAUTH_CALLBACK_URL
    client_class = OAuth2Client



class GoogleLoginCallbackView(APIView):
    
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        # Step 1: Get the authorization code from the callback
        code = request.query_params.get('code')  # Use query_params to fetch from URL
        if code is None:
            return Response({"error": "Authorization code not provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Step 2: Exchange code for an access token
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "code": code,
            "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_OAUTH_CALLBACK_URL,
            "grant_type": "authorization_code",
        }

        token_response = requests.post(token_url, data=token_data)
        if token_response.status_code != 200:
            return Response({"error": "Failed to retrieve access token"}, status=status.HTTP_400_BAD_REQUEST)

        access_token = token_response.json().get("access_token")

        user_info_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        user_info_response = requests.get(user_info_url, headers={"Authorization": f"Bearer {access_token}"})
        if user_info_response.status_code != 200:
            return Response({"error": "Failed to retrieve user info"}, status=status.HTTP_400_BAD_REQUEST)

        user_info = user_info_response.json()
        email = user_info.get("email")
        
        if not email:
            return Response({"error": "Email not provided by Google"}, status=status.HTTP_400_BAD_REQUEST)

        # Step 4: Check if user exists, or create a new user
        user, created = User.objects.get_or_create(email=email)
        if created:
            print("created")
            user.set_unusable_password()  # Since it's a social login
            user.save()
        # Step 5: Generate JWT token
        refresh = RefreshToken.for_user(user)
        token_data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

        # Step 6: Return token and user info
        return Response(
            {
                "user": {"email": user.email},
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
    
    def get(self, request, *args, **kwargs):
        return render(
            request,
            "home.html",
            {
                "google_callback_uri": settings.GOOGLE_OAUTH_CALLBACK_URL,
                "google_client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            },
        )

class SetUserview(APIView):
    
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self,request):
        
        name = request.data.get('name')
        mobile_no = request.data.get('mobile_no')
        
        # add image
        
        user = UserService.get_user_by_id(request.user.id)
        
        
        if not user:
            return Response({'message':'requested by not allowed user'},status=status.HTTP_400_BAD_REQUEST)
        
        try:
            
            user.name = name
            user.mobile_no = mobile_no
            
            user.save()
            
            data = {
                'id':user.id,
                'email':user.email,
                'name':user.name,
                'mobile_no':user.mobile_no,
            }
            
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
            
            data = {
                    'id':user.id,
                    'email':user.email,
                    'name':user.name,
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
        
        searchStirng = request.query_params.get('search') 
        print(searchStirng) 
        
        try: 
            
            shops = Shop.objects.annotate(
                search=SearchVector("name","location__address")
                ).filter(search=searchStirng) 
            shop_list = getList(shops) 
            return Response({'shop_list':shop_list},status=status.HTTP_200_OK) 
        
        except Exception as e: 
            
            return Response({'message':'error occured','error':str(e)},status=status.HTTP_400_BAD_REQUEST)
        
    
    
    