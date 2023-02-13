from django.test import TestCase
from .models import Collection, Movie
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User 
from rest_framework.test import APITestCase, force_authenticate
from collection.api.serializers import CollectionSerializer
from collection.api.views import CreateCollectionAV
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
import uuid

User = get_user_model()

class CreateCollectionAVTestCase(APITestCase):
    def setUp(self):
        # create a user
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        # get the JWT token for the user
        response = self.client.post(reverse('token_obtain_pair'), data={
            'username': 'testuser',
            'password': 'testpassword'
        })
        self.token = response.data['access']

        self.collection_with_movies = {
                "title": "My Collect",
                "description": "A collection",
                "movies": [
                    {
                        "title": "Movie 5",
                        "description": "A movie",
                        "genres": "Action",
                        "uuid": "uuid_5"
                    },
                    {
                        "title": "Movie 10",
                        "description": "Another movie",
                        "genres": "Comedy, Drama",
                        "uuid": "uuid_6"
                    }
                ]
            }

        self.collection_without_movies = {
            "title": "My Collect",
            "description": "A collection"
        }

        self.invalid_collection_data = {
             'name': 'Test Collection',
             'description': 'Test Description',
             'movies': [
                 {
                     'title': 'Test Movie',
                     'description': 'Test Description'
                 }
           ]
        }
    
        self.url = reverse('create-collection')

    def test_create_collection_unauthentication_user_with_movies(self):
        """
        Asserts that user is not able to create collection having movies as anonymous user
        """

        response = self.client.post(self.url, self.collection_with_movies)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_collection_unauthentication_user_without_movies(self):
        """
        Asserts that user is not able to create collection which doesn't have movies without as anonymous user
        """

        response = self.client.post(self.url, self.collection_without_movies)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_collection_with_movies_authenticated_user(self):
        """
        Asserts that user is able to create collection with movies as an authenticated user
        """

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.url, self.collection_with_movies, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('collection_uuid', response.data)

        collection = Collection.objects.get(uuid=response.data['collection_uuid'])
        self.assertEqual(collection.title, self.collection_with_movies['title'])
        self.assertEqual(collection.user, self.user)

        movies = Movie.objects.filter(collection=collection)
        self.assertEqual(movies.count(), 2)
    
    def test_create_collection_without_movies_authenticated_user(self):
        """
        Asserts that user is able to create collection without movies as an authenticated user
        """

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.url, self.collection_without_movies, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('collection_uuid', response.data)

        collection = Collection.objects.get(uuid=response.data['collection_uuid'])
        self.assertEqual(collection.title, self.collection_without_movies['title'])
        self.assertEqual(collection.user, self.user)

        movies = Movie.objects.filter(collection=collection)
        self.assertEqual(movies.count(), 0)

    def test_create_collection_with_invalid_data_authenticated_user(self):
        """
        Asserts that user is not able to create collection with invalid data as an authenticated user
        """

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.url, self.invalid_collection_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CollectionCrudAVTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.collection = Collection.objects.create(
            title='Test Collection',
            description = "description",
            user=self.user
        )

        self.movie = Movie.objects.create(
            title='Test Movie',
            collection=self.collection,
            user=self.user
        )

        response = self.client.post(reverse('token_obtain_pair'), data={
            'username': 'testuser',
            'password': 'testpassword'
        })

        self.put_data_without_movies = {
            "title": "My Collection updated",
            "description": "A collection of movies updated",
            
        }

        self.put_data_with_movies = {
            "title": "My Collection updated",
            "description": "A collection of movies updated",
            "movies": [
                {
                    "title": "Movie upadted 1",
                    "description": "A movie",
                    "genres": "Action, Adventure",
                    "uuid": "uuid_1"
                },
                {
                    "title": "Movie updated 2",
                    "description": "Another movie",
                    "genres": "Comedy, Romance",
                    "uuid": "uuid_2"
                }
            ]
            }

        self.put_invalid_data = {
            "title": "My Collection updated",
            "movies": [
                {
                    "title": "Movie upadted 1",
                    "description": "A movie",
                    "genres": "Action, Adventure",
                    "uuid": "uuid_1"
                },
                {
                    "title": "Movie updated 2",
                    "description": "Another movie",
                    "genres": "Comedy, Romance",
                    "uuid": "uuid_2"
                }
            ]
            }

        self.token = response.data['access']
        self.invalid_collection = uuid.uuid1()

    def test_get_collection_unauthentication_user(self):
        """
        Asserts that user is not able to fetch the collection as an unauthenticated user
        """

        response = self.client.get(
            f'/collection/{self.collection.uuid}/'
        )  
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)     

    def test_get_collection_with_authentication_with_valid_uuid(self):
        """
        Asserts that user having a valid uuid is able to fetch the collection as an authenticated user
        """

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get(
            f'/collection/{self.collection.uuid}/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_collection_with_authentication_invalid_uuid(self):
        """
        Asserts that user having an invalid uuid is not able to fetch the collection as an authenticated user
        """

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get(
            f'/collection/{self.invalid_collection}/'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_collection_unauthenticated(self):
        """
        Asserts that user having a valid uuid is not able to update the collection as an unauthenticated user
        """

        response = self.client.put(
            f'/collection/{self.collection.uuid}/'
        )  
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_collection_authenticated_with_valid_uuid_without_movies(self):
        """
        Asserts that user having a valid uuid is able to update the collection without movies as an authenticated user
        """

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.put(
            f'/collection/{self.collection.uuid}/',
            self.put_data_without_movies,
             format='json'
        )  
        self.assertEqual(response.status_code, status.HTTP_200_OK) 

    def test_put_collection_authenticated_with_valid_uuid_with_movies(self):
        """
        Asserts that user having a valid uuid is able to update the collection having movies as an authenticated user
        """

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.put(
            f'/collection/{self.collection.uuid}/',
            self.put_data_with_movies,
             format='json'
        )  
        self.assertEqual(response.status_code, status.HTTP_200_OK)     


    def test_put_collection_authenticated_with_invalid_uuid(self):
        """
        Asserts that user having an invalid uuid is not able to update the collection as an authenticated user
        """

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.put(
            f'/collection/{self.invalid_collection}/'
        )  
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) 

    def test_put_collection_authenticated_with_invalid_data(self):
        """
        Asserts that user having an valid uuid and invalid data is not able to update the collection as an authenticated user
        """

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.put(
            f'/collection/{self.collection.uuid}/',
            self.put_invalid_data,
             format='json'
        )   
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) 


    def test_delete_collection_unauthenticated(self):
        """
        Asserts that user having a valid uuid is not able to delete the collection as an unauthenticated user
        """

        response = self.client.delete(
            f'/collection/{self.collection.uuid}/'
        )  
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_collection_authenticated_with_invalid_uuid(self):
        """
        Asserts that user having an invalid uuid is not able to delete the collection as an authenticated user
        """

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.delete(
            f'/collection/{self.invalid_collection}/'
        )  
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)  

    def test_delete_collection_authenticated_with_valid_uuid(self):
        """
        Asserts that user having a valid uuid is able to delete the collection as an authenticated user
        """

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.delete(
            f'/collection/{self.collection.uuid}/'
        )  
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class AllCollectionWithTopGenresTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.collection = Collection.objects.create(
            title='Test Collection',
            description = "description",
            user=self.user
        )

        self.collection2 = Collection.objects.create(
            title='Test Collection 2',
            description = "description 2",
            user=self.user
        )

        self.movie = Movie.objects.create(
            title='Test Movie',
            collection=self.collection2,
            description = "Test Movie",
            user=self.user,
            genres = "Drama,Action",
            uuid = uuid.uuid1(),
        )

        self.movie = Movie.objects.create(
            title='Test Movie 2',
            collection=self.collection,
            description = "Test Movie 2",
            user=self.user,
            genres = "Action",
            uuid = uuid.uuid1(),
        )

        self.movie = Movie.objects.create(
            title='Test Movie 3',
            collection=self.collection,
            description = "Test Movie 3",
            user=self.user,
            genres = "Action,Drama,Thriller",
            uuid = uuid.uuid1(),
        )

        self.movie = Movie.objects.create(
            title='Test Movie 4',
            collection=self.collection,
            description = "Test Movie 4",
            user=self.user,
            genres = "Action, Thriller",
            uuid = uuid.uuid1(),
        )

        response = self.client.post(reverse('token_obtain_pair'), data={
            'username': 'testuser',
            'password': 'testpassword'
        })

        self.token = response.data['access']

        self.invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjc2MjQxNTI3LCJpYXQiOjE2NzYyMzc5MjcsImp0aSI6ImY3ZjcyMmE5YjA3YzQ0ZTI4ZWEzZGE5YTE0ZDVjMGFjIiwidXNlcl9pZCI6NX0.mZwWE4Hh-5DiEm1dy3npxHQCnojtlQwMn16XdgReejY"

    def test_get_all_my_collections_unauthenticated(self):
        """
        Asserts that user without authentication is not able to access the collections
        """

        response = self.client.get(reverse('create-collection'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_all_my_collections_authenticated_for_valid_user(self):
        """
        Asserts that user having a valid token is able to access all its collections as an authenticated user
        """

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get(reverse('create-collection'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_all_my_collections_authenticated_for_invalid_user(self):
        """
        Asserts that user having invalid token is not able to access the collections as an authenticated user
        """

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.invalid_token)
        response = self.client.get(reverse('create-collection'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    







            


        


