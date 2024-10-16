from django.shortcuts import render
from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from dotenv import load_dotenv
from .models import User
import os


load_dotenv()

class GoogleLoginView(APIView):
    
    def post(request):
        token = request.data.get('token',None)
        
        if not token:
            return Response({'error':'Token is needed'},status=400)
        
        try:
            client_id = os.getenv('GOOGLE_CLIENT_ID')
            idInfo = id_token.verify_oauth2_token(token,requests.Request(),client_id)
            print(idInfo)
            email = idInfo['email']
            gid = idInfo['sub']
            user = User.objects.get_or_create(username=email)
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        except ValueError:
            return Response({'error':ValueError},status=400)


class CheckLogin(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated] 
    
    def get(request):
        return Response({'message':'authentication successful!!! hello!!!!'})