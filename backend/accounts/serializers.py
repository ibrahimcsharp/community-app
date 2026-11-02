"""
Serializers turn User objects into JSON (and check incoming JSON).
To show a new user field in the app, add its name to a `fields` list here.
"""
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Full user info: for the logged-in user and for the admin panel."""

    class Meta:
        model = User
        fields = ["id", "username", "email", "full_name", "bio",
                  "role", "status", "approved_at", "last_login", "created_at"]
        read_only_fields = fields


class AuthorSerializer(serializers.ModelSerializer):
    """Small version shown next to posts and comments."""

    class Meta:
        model = User
        fields = ["id", "username", "full_name"]
        read_only_fields = fields


class RegisterSerializer(serializers.ModelSerializer):
    """Checks the registration form and creates a 'pending' user."""

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "full_name"]

    def validate_password(self, value):
        validate_password(value)  # length, too common, all numbers (see settings.py)
        return value

    def create(self, validated_data):
        # New users always start as 'pending' until an admin approves them.
        return User.objects.create_user(**validated_data, status="pending", role="user")


class ProfileSerializer(serializers.ModelSerializer):
    """The fields a user may change on their own profile page."""

    class Meta:
        model = User
        fields = ["email", "full_name", "bio"]
