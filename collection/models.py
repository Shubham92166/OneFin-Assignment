from django.db import models
import uuid
from django.contrib.auth.models import User

# Create your models here.
class Collection(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_collection")

class Movie(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name="collection")
    description = models.TextField(max_length=500)
    title = models.CharField(max_length=100)
    genres = models.CharField(max_length=200)
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


    
    

