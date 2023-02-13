from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
import uuid, os
User = get_user_model()

class RegisterAVTestCase(APITestCase):
    
    #test registration with valid data
    def test_register_valid(self):
        data = {
            "username" : "testingusername",
            "password" : "testingpassword"
        }

        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #test registration with invalid data
    def test_register_invalid(self):
        data = {
            "username" : "",
            "password" : ""
        }

        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RequestCounterMiddlewareTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
    
    def test_request_count_increment(self):
        response = self.client.get(reverse('request-count'))
        self.assertEqual(response.json()['requests'], 4)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_request_count_reset(self):
        """
        Asserts that request counter is reset to 0
        """

        response = self.client.post(reverse('request-count-reset'))
        self.assertEqual(response.json()['message'], 'request count reset successfully')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class MoviesListTestCase(APITestCase):
    def setUp(self):
        self.API_USERNAME = os.getenv('API_USERNAME')
        self.API_PASSWORD = os.getenv('API_PASSWORD')

        response = None
        self.MAX_RETRIES = 5

    def test_get_movies_list(self):
        """
        Asserts that third party API is invoked successfully
        """
        
        response = self.client.get('movie-listing')
        self.assertEqual(response.status_code, 200)