#Django
from django.urls import reverse
from django.contrib.auth import get_user_model

#rest framework
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIClient

#standard libraries
import os

User = get_user_model()

class RegisterAVTestCase(APITestCase):
    """Tests the User registration functionality"""
    
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
    """Tests the custom middleware used to increment or reset the request counter"""

    def setUp(self):
        self.client = APIClient()
    
    def test_request_count_increment(self):
        """
        Asserts the request count is incremented succesully through the middleware
        """

        response = self.client.get(reverse('request-count'))
        self.assertEqual(response.json()['requests'], 4)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_request_count_reset(self):
        """
        Asserts that request counter is reset to 0 through the middleware
        """

        response = self.client.post(reverse('request-count-reset'))
        self.assertEqual(response.json()['message'], 'request count reset successfully')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class MoviesListTestCase(APITestCase):
    """Tests the third API"""

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