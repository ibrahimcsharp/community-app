"""
Community views: categories, posts and comments for logged-in users.

The rules, in plain words:
  * Everyone sees approved posts/comments. You also see your own, whatever their status.
  * Admins can open any post and see all its comments (the board itself shows the same as for users).
  * New posts/comments start as 'pending' (admins' are approved straight away).
  * You can edit/delete your own. Editing sends it back to 'pending' for re-approval.
  * Admins can edit/delete anything.
  * You can only comment on approved posts.
"""
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Category, Comment, Post
from .serializers import CategorySerializer, CommentSerializer, PostSerializer


# ---------------------------------------------------------------------
# Small helpers used by the views below
# ---------------------------------------------------------------------
def approved_or_mine(user):
    """Filter: rows that are approved, or written by this user. Used for the board."""
    return Q(status="approved") | Q(user=user)


def visible_to(user):
    """Filter for opening one post and its comments. Admins see everything,
    so they can check pending items in context."""
    if user.is_admin:
        return Q()  # no filter
    return approved_or_mine(user)


def posts_with_comment_count():
    """All posts, newest first, each with the number of approved comments attached."""
    return (
        Post.objects.select_related("user", "category")
        .annotate(comment_count=Count("comments", filter=Q(comments__status="approved")))
        # Must be explicit: Django ignores Meta.ordering on queries with Count().
        .order_by("-created_at", "-id")
    )


def can_change(user, item):
    """Only the author or an admin may edit or delete a post/comment."""
    return item.user_id == user.id or user.is_admin


def starting_status(user, item):
    """Admins' writing is approved at once; everyone else waits for review."""
    if user.is_admin:
        item.status = "approved"
        item.reviewed_by = user
        item.reviewed_at = timezone.now()
    else:
        item.status = "pending"
        item.reject_reason = ""


def not_allowed():
    return Response({"detail": "You can only change your own writing."},
                    status=status.HTTP_403_FORBIDDEN)


# ---------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------
@api_view(["GET"])
def category_list(request):
    """List all categories (for the dropdown and the filter)."""
    categories = Category.objects.all()
    return Response(CategorySerializer(categories, many=True).data)


# ---------------------------------------------------------------------
# Posts
# ---------------------------------------------------------------------
@api_view(["GET", "POST"])
def post_list(request):
    """
    GET:  the community board. Optional filters:
            ?category=<id>   only that category
            ?mine=1          only my own posts (all statuses)
    POST: write a new post  {title, body, category}
    """
    if request.method == "GET":
        posts = posts_with_comment_count().filter(approved_or_mine(request.user))

        category_id = request.query_params.get("category")
        if category_id:
            posts = posts.filter(category_id=category_id)

        if request.query_params.get("mine") == "1":
            posts = posts.filter(user=request.user)

        return Response(PostSerializer(posts, many=True).data)

    serializer = PostSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    post = Post(user=request.user, **serializer.validated_data)
    starting_status(request.user, post)
    post.save()
    return Response(PostSerializer(post).data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "DELETE"])
def post_detail(request, post_id):
    """GET one post, PUT to edit it, DELETE to remove it."""
    post = get_object_or_404(posts_with_comment_count().filter(visible_to(request.user)), id=post_id)

    if request.method == "GET":
        return Response(PostSerializer(post).data)

    if not can_change(request.user, post):
        return not_allowed()

    if request.method == "DELETE":
        post.delete()  # its comments are deleted too
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = PostSerializer(post, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    post = serializer.save()
    if not request.user.is_admin:
        starting_status(request.user, post)  # an edit needs approval again
        post.save()
    return Response(PostSerializer(post).data)


# ---------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------
@api_view(["GET", "POST"])
def post_comments(request, post_id):
    """GET the comments under a post, POST a new one  {body}"""
    post = get_object_or_404(Post.objects.filter(visible_to(request.user)), id=post_id)

    if request.method == "GET":
        comments = post.comments.select_related("user", "post").filter(visible_to(request.user))
        return Response(CommentSerializer(comments, many=True).data)

    if post.status != "approved":
        return Response({"detail": "You can only comment on approved posts."},
                        status=status.HTTP_400_BAD_REQUEST)

    serializer = CommentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    comment = Comment(post=post, user=request.user, **serializer.validated_data)
    starting_status(request.user, comment)
    comment.save()
    return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)


@api_view(["PUT", "DELETE"])
def comment_detail(request, comment_id):
    """PUT to edit your comment  {body}, DELETE to remove it."""
    comment = get_object_or_404(Comment.objects.select_related("user", "post"), id=comment_id)

    if not can_change(request.user, comment):
        return not_allowed()

    if request.method == "DELETE":
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = CommentSerializer(comment, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    comment = serializer.save()
    if not request.user.is_admin:
        starting_status(request.user, comment)  # an edit needs approval again
        comment.save()
    return Response(CommentSerializer(comment).data)
