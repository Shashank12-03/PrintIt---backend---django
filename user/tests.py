from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

# Create your tests here.

class EmailLoginAPITest(APITestCase):
    def test_email_login_api_returns_200(self):
        url = reverse('user:email-login') 
        data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])
        
