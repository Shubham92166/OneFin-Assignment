#Django
from django.contrib import admin

#local Django
from .models import Collection, Movie

"""Registers the model on admin panel"""
admin.site.register(Collection)
admin.site.register(Movie)