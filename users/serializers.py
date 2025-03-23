# serializers.py
from rest_framework import serializers
from .models import Player

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['id', 'username', 'first_name', 'last_name']