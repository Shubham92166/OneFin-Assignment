#rest framework
from rest_framework import serializers

#Django
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    """Serializes the USer object"""

    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """Creates a new User"""

        validated_data['password'] = make_password(validated_data.get('password'))
        return User.objects.create(**validated_data)