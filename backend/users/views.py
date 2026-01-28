from django.contrib.auth.models import User
from users.models import UserProfile
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout

# --------------------------
# Registration
# --------------------------
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    class_name = request.data.get('class_name', '')  # Optional for admin
    batch = request.data.get('batch', '')  # Optional for admin
    role = request.data.get('role', 'student')

    if not username or not password:
        return Response({"error": "Username and password are required"}, status=400)

    # Validate that students must provide class and batch
    if role == 'student' and (not class_name or not batch):
        return Response({"error": "Students must provide class_name and batch"}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already taken"}, status=400)

    # 1️⃣ Create auth user
    user = User.objects.create_user(username=username, password=password)

    # 2️⃣ Create UserProfile
    UserProfile.objects.create(
        user=user,
        role=role,
        class_name=class_name,
        batch=batch
    )

    return Response({
        "message": "User registered",
        "user_id": user.id,
        "role": role
    })


# --------------------------
# Login
# --------------------------
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if user:
        login(request, user)

        # Ensure UserProfile exists
        try:
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            return Response({"error": "UserProfile not found"}, status=404)

        return Response({
            "message": "Login successful",
            "user_id": user.id,
            "role": profile.role  # Return the role from profile
        })

    return Response({"error": "Invalid credentials"}, status=400)


# --------------------------
# Logout
# --------------------------
@api_view(['POST'])
def logout_view(request):
    logout(request)
    return Response({"message": "Logged out"})