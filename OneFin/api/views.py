#Django
from django.http import JsonResponse

#rest framework
from rest_framework.response import Response
from rest_framework.decorators import APIView
from collection.api.views import get_tokens_for_user
from rest_framework import status

#local Django
from .serializers import UserSerializer


#standard libraries
from dotenv import load_dotenv
import os
import requests 

load_dotenv()

def get_movies_list(request):
    """Helper method to call third party API. It also implements the retry mechanism"""

    API_USERNAME = os.getenv('API_USERNAME')
    API_PASSWORD = os.getenv('API_PASSWORD')
    
    url = 'https://demo.credy.in/api/v1/maya/movies/'

    response = None
    max_retries = 5
    for i in range(max_retries):
        try:
            response = requests.get(url, auth=(API_USERNAME, API_PASSWORD), verify=False)
            response.raise_for_status()
            break
        except requests.exceptions.RequestException as e:
            if i == max_retries - 1:
                raise e
            continue

    data = response.json()

    return JsonResponse(data)
    

class RegisterAV(APIView):
    '''Registers a new user'''

    def post(self, request):
        """Creates a user and returs the access token as response"""

        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = get_tokens_for_user(user)
        response_payload = {
            'access_token' : token['access']
        }
        
        return Response(response_payload, status=status.HTTP_201_CREATED)