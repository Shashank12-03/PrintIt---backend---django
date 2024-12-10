from django.contrib.auth.backends import BaseBackend
from .models import User


class UserAuthenticationBackend(BaseBackend):
    
    def authenticate(self, request, username = ..., password = ..., **kwargs):
        return super().authenticate(request, username, password, **kwargs)
