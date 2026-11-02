"""
Serializers turn community objects into JSON (and check incoming JSON).
Fields listed in `read_only_fields` are sent to the app but can't be changed by it.
"""
from rest_framework import serializers

from accounts.serializers import AuthorSerializer

from .models import Category, Comment, ModerationLog, Post


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description"]


class PostSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(source="user", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ["id", "title", "body", "category", "category_name", "author",
                  "status", "reject_reason", "comment_count", "created_at", "updated_at"]
        read_only_fields = ["status", "reject_reason", "created_at", "updated_at"]

    def get_comment_count(self, post):
        # The views add "comment_count" with .annotate(); a brand-new post has none yet.
        return getattr(post, "comment_count", 0)

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Title can't be empty.")
        return value.strip()

    def validate_body(self, value):
        if not value.strip():
            raise serializers.ValidationError("Text can't be empty.")
        return value.strip()


class CommentSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(source="user", read_only=True)
    post_title = serializers.CharField(source="post.title", read_only=True)  # handy in the admin panel

    class Meta:
        model = Comment
        fields = ["id", "post", "post_title", "body", "author",
                  "status", "reject_reason", "created_at", "updated_at"]
        read_only_fields = ["post", "status", "reject_reason", "created_at", "updated_at"]

    def validate_body(self, value):
        if not value.strip():
            raise serializers.ValidationError("Comment can't be empty.")
        return value.strip()


class ModerationLogSerializer(serializers.ModelSerializer):
    admin_username = serializers.CharField(source="admin.username", read_only=True, default="(deleted)")

    class Meta:
        model = ModerationLog
        fields = ["id", "admin_username", "target_type", "target_id", "action", "note", "created_at"]
