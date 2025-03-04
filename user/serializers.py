from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from .models import User
import requests
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from dotenv import load_dotenv
import os


load_dotenv()
GOOGLE_OAUTH_CLIENT_ID=os.getenv('GOOGLE_OAUTH_CLIENT_ID')
GOOGLE_OAUTH_CLIENT_SECRET=os.getenv('GOOGLE_OAUTH_CLIENT_SECRET')
GOOGLE_OAUTH_CALLBACK_URL=os.getenv('GOOGLE_OAUTH_CALLBACK_URL')

class CustomRegisterSerializer(RegisterSerializer):
    username = None
    email = serializers.EmailField()
    
    def get_cleaned_data(self):
        data_dict = super().get_cleaned_data()
        data_dict['email'] = self.validated_data.get("email","")
        return data_dict
    
    
class GoogleSignInSerializer(serializers.Serializer):
    code = serializers.CharField()

    def validate(self, attrs):
        code = attrs.get("code")
        print(code)
        google_token_endpoint = "https://oauth2.googleapis.com/token"
        google_userinfo_endpoint = "https://www.googleapis.com/oauth2/v3/userinfo"
        
        # Exchange code for tokens
        data = {
            "code": code,
            "client_id": GOOGLE_OAUTH_CLIENT_ID,
            "client_secret":GOOGLE_OAUTH_CLIENT_SECRET,
            "redirect_uri":"https://auth.expo.io/@shashank1203/printit-user",  # Set this in Google Console
            "grant_type": "authorization_code",
        }
        token_response = requests.post(google_token_endpoint, data=data)
        if token_response.status_code != 200:
            raise serializers.ValidationError("Failed to exchange code for token.")

        token_data = token_response.json()
        id_token = token_data.get("id_token")
        access_token = token_data.get("access_token")

        # Fetch user info
        user_info_response = requests.get(
            google_userinfo_endpoint, headers={"Authorization": f"Bearer {access_token}"}
        )
        if user_info_response.status_code != 200:
            raise serializers.ValidationError("Failed to fetch user info.")

        user_info = user_info_response.json()
        email = user_info.get("email")
        if not email:
            raise serializers.ValidationError("Email not available in user info.")

        # Check if the user exists
        user, created = User.objects.get_or_create(email=email)
        if created:
            user.set_unusable_password()  # Since it's a social login
            user.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }