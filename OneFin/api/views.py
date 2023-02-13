import os, requests, time
from django.http import JsonResponse
from rest_framework.response import Response
from dotenv import load_dotenv

load_dotenv()



def get_movies_list(request):
    API_USERNAME = os.getenv('API_USERNAME')
    API_PASSWORD = os.getenv('API_PASSWORD')
    
    response = requests.get('https://demo.credy.in/api/v1/maya/movies/', auth=(API_USERNAME, API_PASSWORD))
    
    MAX_RETRIES = 10

    for i in range(MAX_RETRIES):
        response = requests.get('https://demo.credy.in/api/v1/maya/movies/', auth=(API_USERNAME, API_PASSWORD))
        if response.status_code == 200:
            break
        else:
            time.sleep(1)
  
    data = response.json()
  
    response_payload = {
        "data" : data
    }
   

    return JsonResponse(response_payload)
    