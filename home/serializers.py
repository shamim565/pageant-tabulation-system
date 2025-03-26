from rest_framework import serializers
from .models import Contestant, Score
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = ['contestant', 'value', 'judge_name']

class ContestantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contestant
        fields = ['id', 'name']