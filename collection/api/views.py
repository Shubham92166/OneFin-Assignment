from rest_framework import status
from rest_framework.decorators import APIView
from .serializers import CollectionSerializer, MovieSerializer, UserSerializer
from rest_framework.response import Response
from collection.models import Collection
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

class CollectionAV(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, collection_uuid):
        try:
            collection = Collection.objects.get(pk = collection_uuid)
        except Collection.DoesNotExist:
            print("Exception")
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = CollectionSerializer(collection)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, collection_uuid):
        request.data['user'] = request.user.pk
        collection = Collection.objects.get(pk = collection_uuid, user = request.user)
        #print(list(collection).values())
        serializer = CollectionSerializer(collection, data=request.data)

        if serializer.is_valid():
            serializer.save()
            print("collection saved")
            for movie_data in request.data.get('movies', []):
                movie_data['collection'] = collection.uuid
                movie_data['user'] = request.user.pk
                movie_serializer = MovieSerializer(data=movie_data)
                if movie_serializer.is_valid():
                    movie_serializer.save()
                    print("updated")
            return Response(status= status.HTTP_204_NO_CONTENT)

        print("exception")
        return Response(status= status.HTTP_200_OK)
        
    def delete(self, request, collection_uuid):
        collection = Collection.objects.get(pk = collection_uuid, user = request.user)
        print(collection)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CreateCollectionAV(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.data['user'] = request.user.pk
        
        serializer = CollectionSerializer(data = request.data)
        if serializer.is_valid():
            collection = serializer.save()
           
            for movie_data in request.data.get('movies', []):
                movie_data['collection'] = collection.uuid
                movie_data['user'] = request.user.pk
                movie_serializer = MovieSerializer(data=movie_data)
            
                if movie_serializer.is_valid():
                    movie_serializer.save()
                    print("movie done")

            response_payload = {
                'collection_uuid' : collection.uuid
            }
            
            return Response(response_payload, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def get(self, request):
        all_collections = list(Collection.objects.filter(user = request.user.pk).values())
        result_set = []
        for collection in all_collections:
            del collection['user_id']
            result_set.append(collection)
        print(result_set)
        response = {
            "is_successful" : True,
            "data": {
                "collections": result_set
        } 
        }
        return Response(response, status=status.HTTP_200_OK)

class RegisterAV(APIView):
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

