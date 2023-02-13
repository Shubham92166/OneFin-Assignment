from rest_framework import status
from rest_framework.decorators import APIView
from .serializers import CollectionSerializer, MovieSerializer, UserSerializer
from rest_framework.response import Response
from collection.models import Collection, Movie
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import get_user_model

from rest_framework.permissions import BasePermission

class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class CollectionCrudAV(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, collection_uuid):
        try:
            collection = Collection.objects.get(pk = collection_uuid)
        except Collection.DoesNotExist:
            print("Exception")
            return Response({"Error" : "Record not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CollectionSerializer(collection)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, collection_uuid):
        request.data['user'] = request.user.pk
        try:
            collection = Collection.objects.get(pk = collection_uuid, user = request.user)
        except Collection.DoesNotExist:
            return Response({"Error" : "Record not found"}, status=status.HTTP_404_NOT_FOUND) 
        serializer = CollectionSerializer(collection, data=request.data)

        if serializer.is_valid():
            serializer.save()
            for movie_data in request.data.get('movies', []):
                movie_data['collection'] = collection.uuid
                movie_data['user'] = request.user.pk
                movie_serializer = MovieSerializer(data=movie_data)
                if movie_serializer.is_valid():
                    movie_serializer.save()
            response = {
                'data' : "Updated successfully"
            }
            return Response(response, status= status.HTTP_200_OK)

        return Response(status= status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request, collection_uuid):
        try:
            collection = Collection.objects.get(pk = collection_uuid, user = request.user)
        except Collection.DoesNotExist:
            return Response({"Error" : "Record not found"}, status=status.HTTP_404_NOT_FOUND)
            
        collection.delete()
        response = {
            'data' : "deleted successfully"
        }
        return Response(response, status=status.HTTP_204_NO_CONTENT)

class CreateCollectionAV(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.data['user'] = request.user.pk
        
        serializer = CollectionSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        collection = serializer.save()
        
        for movie_data in request.data.get('movies', []):
            movie_data['collection'] = collection.uuid
            movie_data['user'] = request.user.pk
            movie_serializer = MovieSerializer(data=movie_data)
        
            movie_serializer.is_valid(raise_exception=True)
            movie_serializer.save()
            print("movie done")

        response_payload = {
            'collection_uuid' : collection.uuid
        }
        
        return Response(response_payload, status=status.HTTP_201_CREATED)
        

    def get(self, request):
        all_collections = list(Collection.objects.filter(user = request.user.pk).values())
        all_my_movies = list(Movie.objects.filter(user = request.user.pk).values())
        result_set = []
        print(all_my_movies)
        all_genres = []
        for movie in all_my_movies:
            genre = (movie.get('genres')).split(',')
            all_genres.extend(genre)
        
        print(all_genres)
        counter = {}
        for genre in all_genres:
            counter[genre] = counter.get(genre, 0) + 1
        
        sorted_counter = sorted(counter.items(), key = lambda val : val[1], reverse=True)
        print(sorted_counter)
        top_genre = []
        for _ in range(3):
            top_genre.append(sorted_counter[_][0])
        
        print(top_genre)

        for collection in all_collections:
            del collection['user_id']
            result_set.append(collection)
        #print(result_set)
        response = {
            "is_successful" : True,
            "data": {
                "collections": result_set
            },
            "favourite_genres" : top_genre 
        }
        return Response(response, status=status.HTTP_200_OK)

class RegisterAV(APIView):
    '''Register a new user'''

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = get_tokens_for_user(user)
            response_data = {
                'access_token' : token['access']
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

