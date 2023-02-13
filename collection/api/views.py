from rest_framework import status
from rest_framework.decorators import APIView
from .serializers import CollectionSerializer, MovieSerializer
from rest_framework.response import Response
from collection.models import Collection, Movie
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication

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
        # try:
        #     collection = list(Collection.objects.select_related("user").get(uuid=collection_uuid)).values()
        #     movies = Movie.objects.select_related("user").filter(collection=collection)
        # except Collection.DoesNotExist:
        #     return None
        # print(collection)
        # print(movies)
        # collection_serializer = None
        # movies_serializer = None
        # if collection:
        #     collection_serializer = CollectionSerializer(collection)
        # if movies:
        #     movies_serializer = MovieSerializer(Movie)
        try:
            collection = Collection.objects.get(uuid = collection_uuid, user = request.user.pk)
            movies = list(Movie.objects.filter(collection = collection_uuid, user = request.user.pk).values('description', 'title', 'genres'))
        except:
            return Response({"Error": "Record not found"}, status=status.HTTP_404_NOT_FOUND)

        response_payload = {
            "title" : collection.title,
            "description" : collection.description,
            "movies" : movies
        }
        return Response(response_payload, status=status.HTTP_200_OK)

    def put(self, request, collection_uuid):
        request.data['user'] = request.user.pk
        try:
            collection = Collection.objects.get(pk = collection_uuid, user = request.user)
        except Collection.DoesNotExist:
            return Response({"Error" : "Record not found"}, status=status.HTTP_404_NOT_FOUND) 
        serializer = CollectionSerializer(collection, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        for movie_data in request.data.get('movies', []):
            movie_data['collection'] = collection.uuid
            movie_data['user'] = request.user.pk
            movie_serializer = MovieSerializer(data=movie_data)
            movie_serializer.is_valid(raise_exception=True)
            movie_serializer.save()
        response_payload = {
            'info' : "Updated successfully"
        }
        return Response(response_payload, status= status.HTTP_200_OK)
        
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
        
        collection_serializer = CollectionSerializer(data = request.data)
        collection_serializer.is_valid(raise_exception=True)
        collection = collection_serializer.save()
        
        for movie_data in request.data.get('movies', []):
            movie_data['collection'] = collection.uuid
            movie_data['user'] = request.user.pk
            movie_serializer = MovieSerializer(data=movie_data)
        
            movie_serializer.is_valid(raise_exception=True)
            movie_serializer.save()

        response_payload = {
            'collection_uuid' : collection.uuid
        }
        
        return Response(response_payload, status=status.HTTP_201_CREATED)
        

    def get(self, request):
        # all_collections = list(Collection.objects.filter(user = request.user.pk).values('title','description','uuid'))
        # all_my_movies = list(Movie.objects.filter(user = request.user.pk).values())
        # #print(all_collections)
        
        # all_user_data = Movie.objects.select_related("user", "collection")
        # print(all_user_data.query)
        # print("all", all_user_data.values())
        # all_genres = all_user_data.values("collection_movie"."genres")
        # #using the selected_related query for query optimisation
        # #all_collections = list(Movie.objects.filter(user = request.user.pk).values('genres'))
        # #print(all_data_for_user.values('title','description','uuid', 'genres'))
        # # print(all_user_data.Collection.description)
        # user_collections = all_user_data.values('title', 'uuid', 'description')

        #user_genres = all_user_data.values('genres')
        #print("select related query", all_data.query)
        #print("All data", all_data)
        #print("all", all_genres)

        all_collections = list(Collection.objects.select_related("user").filter(user=request.user.pk).values('title','description','uuid'))
        all_my_movies = list(Movie.objects.select_related("user", "collection").filter(user=request.user.pk).values('genres'))

        all_genres = []
        for movie in all_my_movies:
            genre = (movie.get('genres')).split(',')
            all_genres.extend(genre)

        genres_cleaned_data = []

        for pair in all_my_movies:
            genres_cleaned_data.extend(pair['genres'].split(','))

        counter = {}
        for genre in genres_cleaned_data:
            counter[genre] = counter.get(genre, 0) + 1
        
        sorted_counter = sorted(counter.items(), key = lambda val : val[1], reverse=True)
        
        top_genre = []

        for _ in range(3):
            top_genre.append(sorted_counter[_][0])

        response_payload = {
            "is_success" : True,
            "data": {
                "collections": all_collections,
                "favourite_genres" : top_genre 
            },
            }
        return Response(response_payload, status=status.HTTP_200_OK)


       

