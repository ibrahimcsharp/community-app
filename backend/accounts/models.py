"""
The User model, mapped to the `users` table in database/community_db.sql.

`managed = False` means Django never creates or changes this table.
To add a column: add it in the SQL file (ALTER TABLE ...), then add the
matching field here, then show it in accounts/serializers.py.
"""
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Helpers to create users with a properly hashed password."""

    def create_user(self, username, email, password=None, **extra_fields):
        user = self.model(username=username, email=self.normalize_email(email), **extra_fields)
        user.set_password(password)  # stores a hash, never the plain password
        user.save()
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        # Used by `python manage.py createsuperuser`: makes an approved admin.
        extra_fields.setdefault("role", "admin")
        extra_fields.setdefault("status", "approved")
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser):
    # AbstractBaseUser already gives us: password, last_login,
    # set_password(), check_password().

    ROLE_CHOICES = [
        ("user", "User"),
        ("admin", "Admin"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pending"),    # just registered, waiting for an admin
        ("approved", "Approved"),  # can log in and post
        ("rejected", "Rejected"),  # admin said no
        ("blocked", "Blocked"),    # was approved, now banned
    ]

    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    full_name = models.CharField(max_length=100, blank=True, default="")
    bio = models.CharField(max_length=500, blank=True, default="")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="user")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    approved_by = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL,
        db_column="approved_by", related_name="+",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "username"  # the field used to log in
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["email"]  # asked for by `createsuperuser`

    class Meta:
        managed = False
        db_table = "users"

    def __str__(self):
        return self.username

    @property
    def is_active(self):
        # Only approved users may use the API. A pending or blocked user's
        # login token is refused automatically.
        return self.status == "approved"

    @property
    def is_admin(self):
        return self.role == "admin"
