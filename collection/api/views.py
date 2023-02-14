#rest framework
from rest_framework import status
from rest_framework.decorators import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import BasePermission

#local Django
from .serializers import CollectionSerializer, MovieSerializer
from collection.models import Collection, Movie

#local imports
from collection.views import get_top_genres_from_all_movies

class IsAuthenticated(BasePermission):
    """Return if user is authenticated"""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

def get_tokens_for_user(user):
    """Returns the access and regresh token for the given in user"""

    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class CollectionCrudAV(APIView):
    """Handles the CRUD operation for Collections"""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, collection_uuid):
        """Handles the read operation for Collections"""

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
        """Handles the update operaton for Collection with the given collection uuid"""

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
        """Handles the delete operation for the given collection uuid"""

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
    """Handles the read and write operations for collections"""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Creates a new collecton for the current user"""

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
        """Fetches all the collections for the current user"""

        #used select_related query to optimize the query
        all_collections = list(Collection.objects.select_related("user").filter(user=request.user.pk).values('title','description','uuid'))
        all_my_movies = list(Movie.objects.select_related("user", "collection").filter(user=request.user.pk).values('genres'))

        top_genres = get_top_genres_from_all_movies(all_my_movies)

        response_payload = {
            "is_success" : True,
            "data": {
                "collections": all_collections,
                "favourite_genres" : top_genres
            },
            }
        return Response(response_payload, status=status.HTTP_200_OK)


       

