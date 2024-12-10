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
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
load_dotenv()

class GoogleLoginView(APIView):
    
    @csrf_exempt
    def post(self,request):
        print("request came")
        token = request.data.get('token',None)
        print(token)
        if not token:
            return Response({'error':'Token is needed'},status=status.HTTP_400_BAD_REQUEST)
        
        try:
            client_id = os.getenv('GOOGLE_CLIENT_ID')
            idInfo = id_token.verify_oauth2_token(token,requests.Request(),client_id)
            if idInfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
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
            print('error ',ValueError)
            return Response({'error':ValueError},status=status.HTTP_400_BAD_REQUEST)


class CheckLogin(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated] 
    
    def get(request):
        return Response({'message':'authentication successful!!! hello!!!!'},status.HTTP_200_OK)
    
    
def loginView(request):
    return render(request,'home.html')

# update info patch
# delete user delete
# sign in 
# sign out
