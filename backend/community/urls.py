"""URLs under /api/"""
from django.urls import path

from . import views

urlpatterns = [
    path("categories/", views.category_list),                      # GET
    path("posts/", views.post_list),                               # GET list, POST create
    path("posts/<int:post_id>/", views.post_detail),               # GET, PUT, DELETE
    path("posts/<int:post_id>/comments/", views.post_comments),    # GET list, POST create
    path("comments/<int:comment_id>/", views.comment_detail),      # PUT, DELETE
]
