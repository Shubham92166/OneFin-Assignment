"""OneFin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from django.urls import path, include
from .request_counter import RequestCountView, RequestCountResetView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from OneFin.api import views 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('collection/', include('collection.api.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.RegisterAV.as_view(), name = "register"),
    path('request-count/', RequestCountView.as_view(), name='request-count'),
    path('request-count/reset/', csrf_exempt(RequestCountResetView.as_view()), name='request-count-reset'),
    path('movies/', views.get_movies_list, name="movie-listing"),
]
