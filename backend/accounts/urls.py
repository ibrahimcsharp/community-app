"""URLs under /api/auth/"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    path("register/", views.register),                 # POST  create account
    path("login/", views.login),                       # POST  get tokens
    path("refresh/", TokenRefreshView.as_view()),      # POST  {refresh} -> new {access} (built into simplejwt)
    path("me/", views.me),                             # GET / PUT  own profile
]
