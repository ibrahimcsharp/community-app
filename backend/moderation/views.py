"""
Admin-only views: see what is waiting, and approve / reject / block.

Every view here uses @permission_classes([IsAdmin]), so normal users get 403.
Every action also writes a row to moderation_logs (see write_log below).
"""
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from accounts.models import User
from accounts.permissions import IsAdmin
from accounts.serializers import UserSerializer
from community.models import Comment, ModerationLog, Post
from community.serializers import CommentSerializer, ModerationLogSerializer, PostSerializer

# Which status each action leads to.
USER_ACTIONS = {
    "approve": "approved",
    "reject": "rejected",
    "block": "blocked",
    "unblock": "approved",
}
CONTENT_ACTIONS = {
    "approve": "approved",
    "reject": "rejected",
}


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def write_log(admin, target_type, target_id, action, note=""):
    """Save one line of history: who did what to which item."""
    ModerationLog.objects.create(admin=admin, target_type=target_type,
                                 target_id=target_id, action=action, note=note)


def unknown_action(action, allowed):
    return Response({"detail": f"Unknown action '{action}'. Use one of: {', '.join(allowed)}."},
                    status=status.HTTP_400_BAD_REQUEST)


def filter_by_status(queryset, request):
    """Apply ?status=pending (or approved, rejected, blocked) if it was given."""
    wanted = request.query_params.get("status")
    return queryset.filter(status=wanted) if wanted else queryset


def review_content(request, item, target_type, action):
    """Approve or reject a post or comment (they work the same way)."""
    if action not in CONTENT_ACTIONS:
        return unknown_action(action, CONTENT_ACTIONS)

    reason = request.data.get("reason", "").strip() if action == "reject" else ""
    item.status = CONTENT_ACTIONS[action]
    item.reject_reason = reason
    item.reviewed_by = request.user
    item.reviewed_at = timezone.now()
    item.save()
    write_log(request.user, target_type, item.id, action, reason)
    return None  # no error


# ---------------------------------------------------------------------
# Dashboard numbers
# ---------------------------------------------------------------------
@api_view(["GET"])
@permission_classes([IsAdmin])
def stats(request):
    """Counts shown on the admin page tabs."""
    return Response({
        "pending_users": User.objects.filter(status="pending").count(),
        "pending_posts": Post.objects.filter(status="pending").count(),
        "pending_comments": Comment.objects.filter(status="pending").count(),
        "total_users": User.objects.count(),
        "total_posts": Post.objects.count(),
        "total_comments": Comment.objects.count(),
    })


# ---------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------
@api_view(["GET"])
@permission_classes([IsAdmin])
def user_list(request):
    """All users, newest first. Optional ?status=pending"""
    users = filter_by_status(User.objects.order_by("-created_at"), request)
    return Response(UserSerializer(users, many=True).data)


@api_view(["POST"])
@permission_classes([IsAdmin])
def user_action(request, user_id, action):
    """POST /api/admin/users/<id>/<approve|reject|block|unblock>/"""
    if action not in USER_ACTIONS:
        return unknown_action(action, USER_ACTIONS)

    user = get_object_or_404(User, id=user_id)
    if user.id == request.user.id:
        return Response({"detail": "You can't change your own account status."},
                        status=status.HTTP_400_BAD_REQUEST)

    user.status = USER_ACTIONS[action]
    if action == "approve":
        user.approved_by = request.user
        user.approved_at = timezone.now()
    user.save()

    write_log(request.user, "user", user.id, action, request.data.get("reason", "").strip())
    return Response(UserSerializer(user).data)


# ---------------------------------------------------------------------
# Posts
# ---------------------------------------------------------------------
@api_view(["GET"])
@permission_classes([IsAdmin])
def post_list(request):
    """All posts, newest first. Optional ?status=pending"""
    posts = filter_by_status(Post.objects.select_related("user", "category"), request)
    return Response(PostSerializer(posts, many=True).data)


@api_view(["POST"])
@permission_classes([IsAdmin])
def post_action(request, post_id, action):
    """POST /api/admin/posts/<id>/<approve|reject>/   body: {"reason": "..."} (optional)"""
    post = get_object_or_404(Post.objects.select_related("user", "category"), id=post_id)
    error = review_content(request, post, "post", action)
    return error or Response(PostSerializer(post).data)


# ---------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------
@api_view(["GET"])
@permission_classes([IsAdmin])
def comment_list(request):
    """All comments, newest first. Optional ?status=pending"""
    comments = Comment.objects.select_related("user", "post").order_by("-created_at")
    comments = filter_by_status(comments, request)
    return Response(CommentSerializer(comments, many=True).data)


@api_view(["POST"])
@permission_classes([IsAdmin])
def comment_action(request, comment_id, action):
    """POST /api/admin/comments/<id>/<approve|reject>/   body: {"reason": "..."} (optional)"""
    comment = get_object_or_404(Comment.objects.select_related("user", "post"), id=comment_id)
    error = review_content(request, comment, "comment", action)
    return error or Response(CommentSerializer(comment).data)


# ---------------------------------------------------------------------
# History
# ---------------------------------------------------------------------
@api_view(["GET"])
@permission_classes([IsAdmin])
def log_list(request):
    """The latest 100 admin actions."""
    logs = ModerationLog.objects.select_related("admin")[:100]
    return Response(ModerationLogSerializer(logs, many=True).data)
