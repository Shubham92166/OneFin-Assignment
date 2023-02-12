from django.urls import path, include
from . import views
urlpatterns = [
    path('<uuid:collection_uuid>/', views.CollectionAV.as_view(), name="update-collection"),
    path('', views.CreateCollectionAV.as_view(), name="collection"),
    path('register/', views.RegisterAV.as_view(), name="register"),
    
]