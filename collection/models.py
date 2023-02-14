#Django
from django.db import models
from django.contrib.auth.models import User

#third party lbraries
import uuid

class Collection(models.Model):
    """Model class for creating Collection table"""

    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="collection_user")

class Movie(models.Model):
    """Model class for creating Movie table"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name="collection")
    description = models.TextField(max_length=500)
    title = models.CharField(max_length=100)
    genres = models.CharField(max_length=200)
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)