"""
Top-level URL map. Every API address starts with /api/.

    /api/auth/...    register, login, profile      -> accounts/urls.py
    /api/...         categories, posts, comments   -> community/urls.py
    /api/admin/...   approve / reject / block      -> moderation/urls.py
"""
from django.urls import include, path

urlpatterns = [
    path("api/auth/", include("accounts.urls")),
    path("api/admin/", include("moderation.urls")),
    path("api/", include("community.urls")),
]
