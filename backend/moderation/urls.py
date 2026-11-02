"""URLs under /api/admin/  (admins only)"""
from django.urls import path

from . import views

urlpatterns = [
    path("stats/", views.stats),                                                # GET counts
    path("users/", views.user_list),                                            # GET ?status=
    path("users/<int:user_id>/<str:action>/", views.user_action),               # POST approve|reject|block|unblock
    path("posts/", views.post_list),                                            # GET ?status=
    path("posts/<int:post_id>/<str:action>/", views.post_action),               # POST approve|reject
    path("comments/", views.comment_list),                                      # GET ?status=
    path("comments/<int:comment_id>/<str:action>/", views.comment_action),      # POST approve|reject
    path("logs/", views.log_list),                                              # GET history
]
