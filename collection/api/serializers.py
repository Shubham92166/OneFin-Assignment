#local imports
from collection.models import Collection, Movie

#rest framework
from rest_framework import serializers

class CollectionSerializer(serializers.ModelSerializer):
    """Serializes the Collection object"""

    class Meta:
        model = Collection
        fields = "__all__"
    
class MovieSerializer(serializers.ModelSerializer):
    """Serializes the Movie object"""

    class Meta:
        model = Movie
        fields = "__all__"
        


