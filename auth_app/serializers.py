from django.contrib.auth.models import User
from rest_framework import serializers

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']  # Add email field
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Ensure that the password is properly hashed
        user = User.objects.create_user(**validated_data)
        return user


