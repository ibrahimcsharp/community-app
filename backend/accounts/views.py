"""
Account views: register, log in, view/edit your own profile.
Each function handles one URL (see accounts/urls.py).
"""
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import ProfileSerializer, RegisterSerializer, UserSerializer

# What a user sees when they try to log in but are not approved.
LOGIN_BLOCKED_MESSAGES = {
    "pending": "Your account is waiting for admin approval.",
    "rejected": "Your registration was rejected by an admin.",
    "blocked": "Your account has been blocked by an admin.",
}


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    """Create a new account. It stays 'pending' until an admin approves it."""
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)  # sends 400 + error messages if invalid
    user = serializer.save()
    return Response(
        {
            "message": "Account created. An admin must approve it before you can log in.",
            "user": UserSerializer(user).data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    """Check username + password and return JWT tokens plus the user's info."""
    username = request.data.get("username", "").strip()
    password = request.data.get("password", "")

    user = User.objects.filter(username=username).first()
    if user is None or not user.check_password(password):
        return Response({"detail": "Wrong username or password."},
                        status=status.HTTP_401_UNAUTHORIZED)

    if user.status != "approved":
        return Response({"detail": LOGIN_BLOCKED_MESSAGES[user.status]},
                        status=status.HTTP_403_FORBIDDEN)

    user.last_login = timezone.now()
    user.save(update_fields=["last_login"])

    refresh = RefreshToken.for_user(user)
    return Response({
        "access": str(refresh.access_token),  # send this with every request
        "refresh": str(refresh),              # use this to get a new access token
        "user": UserSerializer(user).data,
    })


@api_view(["GET", "PUT"])
def me(request):
    """GET: the logged-in user's info.  PUT: update email / full name / bio."""
    if request.method == "GET":
        return Response(UserSerializer(request.user).data)

    serializer = ProfileSerializer(request.user, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(UserSerializer(request.user).data)
