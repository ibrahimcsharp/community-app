"""
Community models, mapped to tables in database/community_db.sql.

`managed = False` means Django never creates or changes these tables.
To add a column: change the SQL file first, then add the field here.
"""
from django.conf import settings
from django.db import models

# Every post and comment has one of these statuses.
# Only 'approved' ones are shown to other people.
CONTENT_STATUS_CHOICES = [
    ("pending", "Pending"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
]


class Category(models.Model):
    """A topic, e.g. 'Questions'. Table: categories"""

    name = models.CharField(max_length=50, unique=True)
    slug = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Post(models.Model):
    """Something a user wrote on the community board. Table: posts"""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name="posts")  # the author
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="posts")
    title = models.CharField(max_length=200)
    body = models.TextField()
    status = models.CharField(max_length=10, choices=CONTENT_STATUS_CHOICES, default="pending")
    reject_reason = models.CharField(max_length=255, blank=True, default="")
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                    on_delete=models.SET_NULL, db_column="reviewed_by",
                                    related_name="+")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = "posts"
        ordering = ["-created_at"]  # newest first

    def __str__(self):
        return self.title


class Comment(models.Model):
    """A reply under a post. Table: comments"""

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name="comments")  # the author
    body = models.TextField()
    status = models.CharField(max_length=10, choices=CONTENT_STATUS_CHOICES, default="pending")
    reject_reason = models.CharField(max_length=255, blank=True, default="")
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                    on_delete=models.SET_NULL, db_column="reviewed_by",
                                    related_name="+")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = "comments"
        ordering = ["created_at"]  # oldest first, like a conversation

    def __str__(self):
        return self.body[:50]


class ModerationLog(models.Model):
    """One row per admin action (approve / reject / block / unblock). Table: moderation_logs"""

    TARGET_CHOICES = [("user", "User"), ("post", "Post"), ("comment", "Comment")]
    ACTION_CHOICES = [("approve", "Approve"), ("reject", "Reject"),
                      ("block", "Block"), ("unblock", "Unblock")]

    admin = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL,
                              related_name="+")
    target_type = models.CharField(max_length=10, choices=TARGET_CHOICES)
    target_id = models.PositiveIntegerField()  # id in users, posts or comments
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    note = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = "moderation_logs"
        ordering = ["-created_at", "-id"]  # newest first; id breaks ties within the same second

    def __str__(self):
        return f"{self.action} {self.target_type} #{self.target_id}"
