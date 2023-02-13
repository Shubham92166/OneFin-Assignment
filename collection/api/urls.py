from django.urls import path, include
from . import views

urlpatterns = [
    path('<uuid:collection_uuid>/', views.CollectionCrudAV.as_view(), name="collection-crud"),
    path('', views.CreateCollectionAV.as_view(), name="create-collection"),
]